# Reusable 3D book

A style-independent rectangular hardcover book, generated with Blender 4.3.
The front uses your image; the back and left spine share a color sampled from
its border. Top, bottom and right fore-edge are white paper. Thin boards and
small bevels catch the light. No ground plane; renders have real alpha.

## Generate a model and preview

From the repository root (Blender required; no Python packages):

```bash
blender -b --python shared/models/book/book.py -- \
  --cover /absolute/path/cover.png --output /tmp/my-book
```

Outputs `book.blend` (editable model, packed cover texture, camera, lighting and
rotation) and `preview.png`. Without `--cover`, a plain blue-green book is made.
Use a tightly cropped front-cover image; the full image maps upright to the
front. Set `--width` and `--height` to its aspect ratio to avoid stretching.
Use `--depth` for thickness. Dimensions default to 1.5 × 2.2 × 0.28.

`--color '#194457'` overrides back/spine color. Automatic sampling selects the
most common quantized color in the outer 12% of the image; borders, photographs,
and multicolor covers may need this override. No back-cover artwork is invented.

## Render the loop

```bash
blender -b --python shared/models/book/book.py -- \
  --cover /absolute/path/cover.png --output /tmp/my-book \
  --seconds 6 --fps 30 --resolution 720 --samples 64 --render
```

The root `BOOK` turns exactly 360° around its vertical axis at constant speed.
The closing keyframe is at N+1, while only frames 1…N are exported: the wrap
advances by one normal angular step, without a repeated endpoint or pause.
RGBA PNG frames are the lossless transparency master for video compositing.

Optional alpha WebM (requires FFmpeg with libvpx-vp9):

```bash
ffmpeg -framerate 30 -i /tmp/my-book/frames/frame_%04d.png \
  -c:v libvpx-vp9 -pix_fmt yuva420p -auto-alt-ref 0 \
  /tmp/my-book/book-loop.webm
```

Match `-framerate` to `--fps`. Some players ignore WebM alpha; use the PNG
sequence when importing into a video pipeline. Ordinary MP4 does not preserve
this transparency. Loop playback is controlled by the video editor/player.

In Blender, replace the image in the `Replaceable front cover` material or
regenerate with `--cover` (recommended: also recalculates back/spine color).
Reuse the `BOOK` root and its children in other scenes. Camera and lights remain
separate. For video-generation agents, provide the image path and desired
sizes, run the command, and composite the resulting RGBA sequence.

Keep binary models, textures and full frame sequences outside Git (for example
in Drive); record their links when used in a production. The generator is the
versioned source of truth. This module is generic and reusable across styles.
