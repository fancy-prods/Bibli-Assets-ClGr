"""Alinha o roteiro (texto exato narrado) com o áudio e gera words.json para a legenda.

    python tools/align.py videos/toyadent/narracao.mp3 videos/toyadent/narracao.txt videos/toyadent/words.json

Saída: [{"w": "Todo", "s": 0.12, "e": 0.38}, ...] — palavras com a GRAFIA DO ROTEIRO, tempos do áudio.
Método 1 (preferido): faster-whisper com timestamps por palavra + casamento com o roteiro (difflib).
Método 2 (fallback, sem rede/modelo): pausas do ffmpeg + duração proporcional ao tamanho das palavras.
O relatório no fim diz quantas palavras casaram; abaixo de 85% vale avisar o Arthur
(provável frase regravada diferente do texto).
"""
import sys, json, re, subprocess, difflib, unicodedata


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", w)


def load_audio(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    import numpy as np
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def whisper_words(path):
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(load_audio(path), language="pt", word_timestamps=True)
    return [(w.word.strip(), w.start, w.end) for s in segs for w in s.words if w.word.strip()]


def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True).stdout)


def fallback(path, words):
    """Distribui as palavras entre os trechos de fala (fora das pausas) proporcionalmente ao tamanho."""
    log = subprocess.run(["ffmpeg", "-i", path, "-af", "silencedetect=noise=-35dB:d=0.2", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    total = duration(path)
    speech, cur = [], 0.0
    for a, b in zip(st, en + [total]):
        if a > cur: speech.append((cur, a))
        cur = b
    if cur < total: speech.append((cur, total))
    tot_speech = sum(b - a for a, b in speech) or total
    weights = [len(w) + 2 for w in words]; k = tot_speech / sum(weights)
    out, seg, pos = [], 0, speech[0][0] if speech else 0
    for w, wt in zip(words, weights):
        d = wt * k
        while seg < len(speech) - 1 and pos + d * 0.5 > speech[seg][1]:
            seg += 1; pos = speech[seg][0]
        out.append({"w": w, "s": round(pos, 3), "e": round(pos + d, 3)}); pos += d
    return out


def align(audio, text):
    words = text.split()
    try:
        hyp = whisper_words(audio)
    except Exception as e:
        print("whisper indisponível, usando fallback por pausas:", e)
        return fallback(audio, words), None
    a, b = [norm(w) for w in words], [norm(w) for w, _, _ in hyp]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    times = [None] * len(words)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            _, s, e = hyp[blk.b + k]; times[blk.a + k] = (s, e)
    matched = sum(t is not None for t in times)
    # interpola as palavras sem par entre vizinhos casados
    total = hyp[-1][2] if hyp else duration(audio)
    i = 0
    while i < len(words):
        if times[i] is not None: i += 1; continue
        j = i
        while j < len(words) and times[j] is None: j += 1
        t0 = times[i - 1][1] if i > 0 else 0.0
        t1 = times[j][0] if j < len(words) else total
        step = max(0.05, (t1 - t0) / (j - i))
        for k in range(i, j): times[k] = (t0 + (k - i) * step, t0 + (k - i + 1) * step)
        i = j
    out = [{"w": w, "s": round(s, 3), "e": round(e, 3)} for w, (s, e) in zip(words, times)]
    return out, matched / max(1, len(words))


if __name__ == "__main__":
    audio, txt, dst = sys.argv[1:4]
    text = re.sub(r"\{\{.*?\}\}|\[.*?\]", " ", open(txt, encoding="utf-8").read())  # remove notas e tags ElevenLabs
    out, ratio = align(audio, text)
    json.dump(out, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"{len(out)} palavras -> {dst}")
    if ratio is not None:
        print(f"casamento com o roteiro: {ratio:.0%}" + ("  << ABAIXO DE 85%: conferir se o áudio bate com o texto"
                                                        if ratio < 0.85 else ""))
