# YOLO Markup Visualizer

A visual tool for inspecting and validating YOLO format image annotations.

## Overview

YOLO Markup Visualizer is a desktop application that allows you to:
- Browse through image and annotation files
- Visualize YOLO format annotations overlaid on images
- Zoom, pan, and navigate through multiple images
- Jump to specific frames by number

## Features

- **Image Navigation**: Navigate through images using arrow keys or buttons
- **Markup Visualization**: View YOLO format annotations overlaid on images
- **Zooming**: Zoom in/out with mouse wheel or keyboard shortcuts
- **Panning**: Move around zoomed images by dragging
- **Flexible Navigation**: Jump to specific frames or navigate sequentially

## Requirements

- Python 3.6+
- OpenCV (cv2)
- NumPy
- PIL (Pillow)
- Tkinter (usually included with Python)

## Installation

1. Clone the repository or download the files
2. Install required dependencies:
   ```
   pip install opencv-python numpy pillow
   ```

## Usage

1. Run the application:
   ```
   python yolo_markup_visualizer.py
   ```

2. Click "Select Folder" to choose a directory containing:
   - Image files (.jpg, .jpeg, or .png)
   - YOLO format annotation files (.txt)

3. Use the controls to navigate through images:
   - Previous/Next buttons
   - Left/Right arrow keys
   - Jump to Frame button

4. Use the zoom controls:
   - Zoom In/Out buttons
   - Plus (+) / Minus (-) keys
   - Mouse wheel
   - Reset zoom with the "0" key

## File Format

The application expects:
- Images in .jpg, .jpeg, or .png format
- YOLO format annotation files (.txt) with the same base name as their corresponding images

YOLO format: Each line in the annotation file represents one object:
```
class_id x1 y1 x2 y2 ... xn yn
```
Where:
- class_id: Integer class identifier
- x, y: Normalized coordinates (0-1) of the polygon vertices

## Keyboard Shortcuts

- **←**: Previous image
- **→**: Next image
- **+**: Zoom in
- **-**: Zoom out
- **0**: Reset zoom

## Mouse Controls

- **Wheel**: Zoom in/out
- **Left button + drag**: Pan around image
