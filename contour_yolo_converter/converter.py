import os
import shutil
import yaml
import argparse
from pathlib import Path

def convert_annotation(input_path, output_path):
    """Convert polygon annotation to YOLO bounding box format."""
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        for line in infile:
            parts = line.strip().split()
            if len(parts) < 3 or len(parts) % 2 == 0:
                continue  # skip malformed lines
            class_id = parts[0]
            coords = list(map(float, parts[1:]))
            x_coords = coords[::2]
            y_coords = coords[1::2]
            x_min = min(x_coords)
            x_max = max(x_coords)
            y_min = min(y_coords)
            y_max = max(y_coords)
            x_center = (x_min + x_max) / 2
            y_center = (y_min + y_max) / 2
            width = x_max - x_min
            height = y_max - y_min
            outfile.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

def parse_obj_data(obj_data_path):
    """Read obj.data and clean paths by removing 'data/' prefix where needed."""
    data = {}
    with open(obj_data_path, 'r') as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                key = key.strip()
                value = value.strip()
                if key in ["train", "names", "backup"] and value.startswith("data/"):
                    value = value[len("data/"):]
                data[key] = value
    return data

def read_class_names(names_path):
    """Load class names from obj.names file (one name per line)."""
    with open(names_path, 'r') as f:
        lines = f.readlines()
    return [line.strip() for line in lines if line.strip()]

def generate_data_yaml(output_dir, class_names):
    """Generate data.yaml file for YOLO training with class names and image paths."""
    data_yaml = {
        'path': str(output_dir),
        'train': 'images/train',
        'val': 'images/val',
        'names': {i: name for i, name in enumerate(class_names)}
    }
    with open(os.path.join(output_dir, 'data.yaml'), 'w') as f:
        yaml.dump(data_yaml, f, default_flow_style=False, allow_unicode=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert annotation format to YOLO-compatible structure.')
    parser.add_argument('input_dir', type=str, help='Path to directory containing the "data" folder with obj.data, obj.names, etc.')
    parser.add_argument('--output_dir', type=str, default=None, help='Path to output directory (defaults to <input_dir>_converted)')
    args = parser.parse_args()

    input_root = Path(args.input_dir)
    output_root = Path(args.output_dir) if args.output_dir else Path(str(input_root) + '_converted')
    data_dir = input_root / "data"

    obj_data = parse_obj_data(data_dir / 'obj.data')
    class_names = read_class_names(data_dir / obj_data['names'])

    for split in ['train', 'val']:
        (output_root / 'images' / split).mkdir(parents=True, exist_ok=True)
        (output_root / 'labels' / split).mkdir(parents=True, exist_ok=True)

    with open(data_dir / obj_data['train'], 'r') as f:
        image_paths = [line.strip() for line in f if line.strip()]

    image_paths = [line[len("data/"):] if line.startswith("data/") else line for line in image_paths]
    split_index = int(0.8 * len(image_paths))
    train_images = image_paths[:split_index]
    val_images = image_paths[split_index:]

    for split, images in [('train', train_images), ('val', val_images)]:
        for img_path in images:
            img_name = os.path.basename(img_path)
            label_name = os.path.splitext(img_name)[0] + '.txt'

            shutil.copy(data_dir / img_path, output_root / 'images' / split / img_name)

            input_annotation_path = data_dir / 'obj_train_data' / label_name
            output_annotation_path = output_root / 'labels' / split / label_name
            if input_annotation_path.exists():
                convert_annotation(input_annotation_path, output_annotation_path)

    generate_data_yaml(output_root, class_names)
