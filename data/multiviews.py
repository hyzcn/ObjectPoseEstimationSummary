from tqdm import tqdm
import argparse
import os
from os.path import join, isdir
import sys

sys.path.append('..')
from blender_render.render_grid import dodecahedron_vertex_coord, semi_sphere_coord, RenderMachine


parser = argparse.ArgumentParser()
parser.add_argument('--dataset_dir', type=str, help='dataset directory')
parser.add_argument('--dataset_format', type=str, choices=['BOP', 'Pascal3D', 'ShapeNet'], help='dataset format')
parser.add_argument('--up', type=str, default=None, help='up axis')
parser.add_argument('--forward', type=str, default=None, help='forward axis')
parser.add_argument('--input', type=str, help='subdirectory containing obj files in the dataset directory')
parser.add_argument('--target_size', type=int, default=128, help='crop the rendering image and resize to the target size')
parser.add_argument('--rendering', type=str, choices=['nocs', 'nontextured'], default='nocs',
                    help='rendering format which could be local field or non-textured images')
parser.add_argument('--views', type=str, choices=['dodecahedron', 'semisphere'], default='dodecahedron',
                    help='views under which the object will be rendered')
args = parser.parse_args()

input_dir = join(args.dataset_dir, args.input)
output_dir = join(args.dataset_dir, 'multiviews', args.views)

if args.views == 'dodecahedron':
    views = dodecahedron_vertex_coord
elif args.views == 'semisphere':
    views = semi_sphere_coord
else:
    sys.exit(0)

if args.dataset_format == 'BOP':
    model_files = sorted(os.listdir(input_dir))
    for model_file in tqdm(model_files):
        model_path = join(input_dir, model_file)
        render_dir = join(output_dir, model_file.split(".")[0])
        render_machine = RenderMachine(model_path, render_dir, rendering=args.rendering, target_size=args.target_size, up=args.up, forward=args.forward)
        render_machine.render_grid_pose(views)

elif args.dataset_format in ['Pascal3D', 'ShapeNet']:
    categories = sorted(os.listdir(input_dir))
    for cat in tqdm(categories):
        cat_in = join(input_dir, cat)
        cat_out = join(output_dir, cat)
        model_files = sorted(os.listdir(cat_in))
        if len(model_files) > 200:
            model_files = model_files[:200]
        for model_file in tqdm(model_files):
            if args.dataset_format == 'Pascal3D':
                model_path = join(cat_in, model_file)
                model_name = model_file.split(".")[0]
            else:
                model_path = join(cat_in, model_file, 'models', 'model_normalized.obj')
                model_name = model_file
            render_dir = join(cat_out, model_name)
            if isdir(render_dir) and isdir(join(render_dir, args.rendering)):
                continue
            render_machine = RenderMachine(model_path, render_dir, rendering=args.rendering, target_size=args.target_size, up=args.up, forward=args.forward)
            render_machine.render_grid_pose(views)
else:
    sys.exit(0)

os.system('rm blender_render.log')
