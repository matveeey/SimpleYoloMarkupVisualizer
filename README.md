# This repo contains tools for working with YOLO and contour markup

## 1. contour_visualizer
This tool is used to demonstrate current markup
Structure of .txts:
```
<class_id> <x_N> <y_N>
```
Where *N* - is a number of a picture, and *x* and *y* are normalized coordinates

## 2. yolo_converter
This tool helps to convert contour-based markup to YOLO format:
```
<class_id> <x_center> <y_center> <width> <height>
```