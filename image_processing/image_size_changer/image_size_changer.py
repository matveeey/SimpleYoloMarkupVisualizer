import os
import argparse
from PIL import Image
import glob

def resize_images(input_dir, output_dir=None, size=(512, 512), overwrite=False):
    if output_dir is None and not overwrite:
        output_dir = os.path.join(input_dir, 'resized')
        os.makedirs(output_dir, exist_ok=True)
    elif output_dir:
        os.makedirs(output_dir, exist_ok=True)

    extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.webp']
    image_files = []
    for ext in extensions:
        image_files.extend(glob.glob(os.path.join(input_dir, ext)))
        image_files.extend(glob.glob(os.path.join(input_dir, ext.upper())))

    for img_path in image_files:
        try:
            img = Image.open(img_path)
            img_ratio = img.width / img.height
            target_ratio = size[0] / size[1]

            if img_ratio > target_ratio:
                new_height = int(size[0] / img_ratio)
                resized = img.resize((size[0], new_height), Image.LANCZOS)
                result = Image.new("RGB", size, (255, 255, 255))
                result.paste(resized, (0, (size[1] - new_height) // 2))
            elif img_ratio < target_ratio:
                new_width = int(size[1] * img_ratio)
                resized = img.resize((new_width, size[1]), Image.LANCZOS)
                result = Image.new("RGB", size, (255, 255, 255))
                result.paste(resized, ((size[0] - new_width) // 2, 0))
            else:
                result = img.resize(size, Image.LANCZOS)

            save_path = img_path if output_dir is None else os.path.join(output_dir, os.path.basename(img_path))
            result.save(save_path, format=img.format or 'JPEG')

        except Exception as e:
            print(f"Skipped: {os.path.basename(img_path)} ({e})")

    print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Resize images to a target size.')
    parser.add_argument('--input_dir', required=True, help='Path to input directory')
    parser.add_argument('--output_dir', help='Optional output directory')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite original files')
    parser.add_argument('--size', type=str, default='512x512', help='Target size, format: WIDTHxHEIGHT (e.g. 512x512)')

    args = parser.parse_args()
    try:
        width, height = map(int, args.size.lower().split('x'))
    except:
        raise ValueError("Size must be in format WIDTHxHEIGHT, e.g. 512x512")

    resize_images(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        size=(width, height),
        overwrite=args.overwrite
    )