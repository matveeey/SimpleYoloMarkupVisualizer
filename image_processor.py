import cv2
import numpy as np
from PIL import Image, ImageTk

class ImageProcessor:
    def __init__(self):
        # Colors for different classes
        self.colors = {
            0: (255, 0, 0),    # Red
            1: (0, 255, 0),    # Green
            2: (0, 0, 255),    # Blue
            3: (255, 255, 0),  # Yellow
            4: (255, 0, 255),  # Purple
            5: (0, 255, 255),  # Cyan
            6: (128, 0, 0),    # Dark red
            7: (0, 128, 0),    # Dark green
            8: (0, 0, 128),    # Dark blue
            9: (128, 128, 0)   # Olive
        }
    
    def load_image(self, path):
        """Loads image from specified path"""
        return cv2.imread(path)
    
    def apply_markup(self, img, markup_data):
        """Applies markup overlay to the image"""
        if img is None:
            return None
            
        img_height, img_width = img.shape[:2]
        
        # Apply markup to image
        for class_id, points in markup_data:
            color = self.colors.get(class_id, (255, 255, 255))  # White color as default
            
            # Convert normalized coordinates to pixel coordinates
            pixel_points = []
            for x, y in points:
                px = int(x * img_width)
                py = int(y * img_height)
                pixel_points.append((px, py))
                
            # Draw points and lines
            for i, (px, py) in enumerate(pixel_points):
                cv2.circle(img, (px, py), 3, color, -1)
                
                # Connect points with lines
                if i > 0:
                    prev_px, prev_py = pixel_points[i-1]
                    cv2.line(img, (prev_px, prev_py), (px, py), color, 2)
                    
            # Connect first and last points if more than 2 points
            if len(pixel_points) > 2:
                first_px, first_py = pixel_points[0]
                last_px, last_py = pixel_points[-1]
                cv2.line(img, (last_px, last_py), (first_px, first_py), color, 2)
                
            # Add class label near first point
            if pixel_points:
                px, py = pixel_points[0]
                cv2.putText(img, str(class_id), (px + 5, py + 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                
        return img
    
    def prepare_image_for_tkinter(self, cv_img, width=None, height=None):
        """Converts OpenCV image to Tkinter format"""
        if cv_img is None:
            return None
            
        # Convert from BGR to RGB (Pillow uses RGB)
        img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        
        # Scale image if dimensions provided
        if width is not None and height is not None:
            if width > 0 and height > 0:  # Protect against invalid dimensions
                pil_img = pil_img.resize((width, height), Image.LANCZOS)
                
        # Convert to Tkinter format
        return ImageTk.PhotoImage(pil_img)