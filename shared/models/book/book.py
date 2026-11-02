"""Blender CLI: blender -b --python book.py -- --output /tmp/book [--cover cover.png]."""
import argparse
import math
from pathlib import Path
import sys
import bpy
from mathutils import Vector


def material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Roughness'].default_value = 0.48
    return mat


def box(name, dimensions, location, mat, parent, bevel=0.008):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.parent = parent
    obj.data.materials.append(mat)
    mod = obj.modifiers.new('Small realistic edge bevel', 'BEVEL')
    mod.width = bevel
    mod.segments = 3
    obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj


def cover_color(image):
    # Quantized dominant opaque color of the perimeter avoids central title artwork.
    w, h = image.size
    pixels = image.pixels[:]
    buckets = {}
    for y in range(0, h, max(1, h // 80)):
        for x in range(0, w, max(1, w // 80)):
            if 0.12 * w < x < 0.88 * w and 0.12 * h < y < 0.88 * h:
                continue
            i = 4 * (y * w + x)
            if pixels[i + 3] < 0.5:
                continue
            rgb = pixels[i:i + 3]
            key = tuple(int(c * 15) for c in rgb)
            total, count = buckets.get(key, ([0, 0, 0], 0))
            buckets[key] = ([a + b for a, b in zip(total, rgb)], count + 1)
    if not buckets:
        raise ValueError('Cover has no opaque border pixels; supply --color.')
    total, count = max(buckets.values(), key=lambda pair: pair[1])
    # 8-bit image pixels are sRGB; Base Color expects linear (same conversion as --color).
    return srgb_to_linear(c / count for c in total)


def srgb_to_linear(srgb):
    return tuple(c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in srgb)


def build(args):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    image = bpy.data.images.load(str(args.cover.resolve())) if args.cover else None
    if args.color:
        value = args.color.lstrip('#')
        if len(value) != 6:
            raise ValueError('--color must be #RRGGBB')
        srgb = [int(value[i:i+2], 16) / 255 for i in (0, 2, 4)]
        color = srgb_to_linear(srgb)
    else:
        color = cover_color(image) if image else (0.025, 0.11, 0.16)
    cover = material('Cover / back / spine color', color)
    pages = material('White paper edges', (0.93, 0.93, 0.90))
    front = material('Replaceable front cover', color)
    if image:
        tex = front.node_tree.nodes.new('ShaderNodeTexImage')
        tex.image = image
        front.node_tree.links.new(tex.outputs['Color'], front.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
        image.pack()
    bpy.ops.object.empty_add()
    book = bpy.context.object
    book.name = 'BOOK — rotate or instance this root'
    w, h, d = args.width, args.height, args.depth
    skin = min(w, h, d) * .06
    # Front faces -Y; spine is -X. Inset page block exposes top, bottom and fore-edge.
    box('Page block', (w - skin, d - 2 * skin, h - 2 * skin), (skin / 2, 0, 0), pages, book)
    box('Back cover', (w, skin, h), (0, (d - skin) / 2, 0), cover, book)
    box('Front cover board', (w, skin, h), (0, -(d - skin) / 2, 0), cover, book)
    box('Spine', (skin, d, h), (-(w - skin) / 2, 0, 0), cover, book)
    mesh = bpy.data.meshes.new('Cover artwork UV mesh')
    mesh.from_pydata([(-w/2, -d/2-.0005, -h/2), (w/2, -d/2-.0005, -h/2),
                       (w/2, -d/2-.0005, h/2), (-w/2, -d/2-.0005, h/2)], [], [(0, 1, 2, 3)])
    mesh.uv_layers.new(name='Full cover image')
    for loop, uv in zip(mesh.uv_layers.active.data, [(0, 0), (1, 0), (1, 1), (0, 1)]):
        loop.uv = uv
    obj = bpy.data.objects.new('Front artwork — replace image in material', mesh)
    bpy.context.collection.objects.link(obj)
    obj.parent = book
    obj.data.materials.append(front)
    scene = bpy.context.scene
    count = round(args.seconds * args.fps)
    if count < 2:
        raise ValueError('Loop requires at least two frames')
    for frame, angle in [(1, 0), (count + 1, 2 * math.pi)]:
        book.rotation_euler.z = angle
        book.keyframe_insert(data_path='rotation_euler', frame=frame)
    for curve in book.animation_data.action.fcurves:
        for point in curve.keyframe_points:
            point.interpolation = 'LINEAR'
    scene.frame_start, scene.frame_end = 1, count
    scene.render.fps = args.fps
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = args.samples
    scene.cycles.use_denoising = False
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.resolution_x = scene.render.resolution_y = args.resolution
    scene.render.resolution_percentage = 100
    bpy.ops.object.camera_add(location=(0, -6, 2.4))
    camera = bpy.context.object
    camera.rotation_euler = (Vector((0, 0, 0)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = math.sqrt(w*w + h*h + d*d) * 1.25
    scene.camera = camera
    for name, pos, energy, size in [('Key', (-3, -4, 5), 450, 4), ('Fill', (4, -1, 2), 220, 3), ('Rim', (0, 3, 4), 350, 3)]:
        bpy.ops.object.light_add(type='AREA', location=pos)
        light = bpy.context.object
        light.name = name
        light.data.energy, light.data.size = energy, size
        light.rotation_euler = (-light.location).to_track_quat('-Z', 'Y').to_euler()
    scene.world.color = (.22, .22, .22)
    scene.view_settings.view_transform = 'Standard'   # AgX (default) washes out cover colors
    args.output.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(args.output.resolve() / 'frames' / 'frame_')
    (args.output / 'frames').mkdir(exist_ok=True)
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output.resolve() / 'book.blend'))
    if args.render:
        bpy.ops.render.render(animation=True)
    else:
        scene.render.filepath = str(args.output.resolve() / 'preview.png')
        scene.frame_set(max(1, count // 12))
        bpy.ops.render.render(write_still=True)
    print(f'BOOK_READY: {count} frames, endpoint excluded, output={args.output}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cover', type=Path)
    parser.add_argument('--color', help='Back/spine override, #RRGGBB; otherwise sampled from cover border')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--width', type=float, default=1.5)
    parser.add_argument('--height', type=float, default=2.2)
    parser.add_argument('--depth', type=float, default=.28)
    parser.add_argument('--seconds', type=float, default=6)
    parser.add_argument('--fps', type=int, default=30)
    parser.add_argument('--resolution', type=int, default=720)
    parser.add_argument('--samples', type=int, default=32)
    parser.add_argument('--render', action='store_true', help='Render full RGBA PNG sequence instead of preview')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if any(not math.isfinite(v) or v <= 0 for v in [args.width, args.height, args.depth, args.seconds, args.fps, args.resolution, args.samples]):
        parser.error('Dimensions, duration, FPS, resolution and samples must be positive and finite')
    build(args)


if __name__ == '__main__':
    main()
