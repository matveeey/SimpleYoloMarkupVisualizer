import os
import glob
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

from image_processor import ImageProcessor
from markup_parser import MarkupParser

class MarkupViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Markup Verification")
        
        # Set window dimensions
        self.root.geometry("1200x800")
        
        # Initialize variables
        self.current_index = 0
        self.image_files = []
        self.txt_files = []
        self.base_path = ""
        self.current_image_path = ""
        self.current_txt_path = ""
        
        # Helper classes
        self.image_processor = ImageProcessor()
        self.markup_parser = MarkupParser()
        
        # Zoom and pan settings
        self.zoom_factor = 1.0
        self.zoom_step = 0.1
        self.panning = False
        self.start_x = 0
        self.start_y = 0
        self.current_image = None
        
        # Create button frame
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Add buttons
        self.btn_open = tk.Button(self.button_frame, text="Select Folder", command=self.open_folder)
        self.btn_open.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.btn_prev = tk.Button(self.button_frame, text="Previous", command=self.prev_image)
        self.btn_prev.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.btn_next = tk.Button(self.button_frame, text="Next", command=self.next_image)
        self.btn_next.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.btn_jump = tk.Button(self.button_frame, text="Jump to Frame", command=self.jump_to_image)
        self.btn_jump.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Zoom buttons
        self.btn_zoom_in = tk.Button(self.button_frame, text="Zoom In (+)", command=self.zoom_in)
        self.btn_zoom_in.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.btn_zoom_out = tk.Button(self.button_frame, text="Zoom Out (-)", command=self.zoom_out)
        self.btn_zoom_out.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.btn_reset_zoom = tk.Button(self.button_frame, text="Reset Zoom", command=self.reset_zoom)
        self.btn_reset_zoom.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Current file info
        self.file_info = tk.StringVar()
        self.file_info.set("Image: 0/0")
        self.lbl_file_info = tk.Label(self.button_frame, textvariable=self.file_info)
        self.lbl_file_info.pack(side=tk.LEFT, padx=20, pady=5)
        
        # Zoom info
        self.zoom_info = tk.StringVar()
        self.zoom_info.set("Zoom: 100%")
        self.lbl_zoom_info = tk.Label(self.button_frame, textvariable=self.zoom_info)
        self.lbl_zoom_info.pack(side=tk.RIGHT, padx=20, pady=5)
        
        # Help info frame
        self.help_frame = tk.Frame(self.root)
        self.help_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.help_text = tk.Label(
            self.help_frame, 
            text="Controls: ← (prev), → (next), + (zoom in), - (zoom out), 0 (reset zoom), Mouse wheel (zoom), Left click + drag (pan)",
            anchor=tk.W,
            justify=tk.LEFT,
            bg="#efefef",
            pady=3
        )
        self.help_text.pack(fill=tk.X)
        
        # Canvas for image display
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        self.h_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.v_scrollbar = tk.Scrollbar(self.canvas_frame)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas
        self.canvas = tk.Canvas(
            self.canvas_frame, 
            bg="gray",
            xscrollcommand=self.h_scrollbar.set, 
            yscrollcommand=self.v_scrollbar.set
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        self.h_scrollbar.config(command=self.canvas.xview)
        self.v_scrollbar.config(command=self.canvas.yview)
        
        # Overlay frame for file info
        self.overlay_frame = tk.Frame(self.canvas, bg='#333333', bd=0)
        self.overlay_frame.place(relx=0, rely=0, anchor='nw')
        
        # Overlay text for file names
        self.overlay_text = tk.StringVar()
        self.overlay_text.set("No active files")
        self.overlay_label = tk.Label(
            self.overlay_frame, 
            textvariable=self.overlay_text, 
            bg='#333333', 
            fg='white', 
            justify=tk.LEFT,
            padx=10, 
            pady=5,
            anchor='w'
        )
        self.overlay_label.pack(fill=tk.X)

        # Bind keyboard and mouse events
        self.root.bind("<Left>", lambda event: self.prev_image())
        self.root.bind("<Right>", lambda event: self.next_image())
        self.root.bind("<plus>", lambda event: self.zoom_in())
        self.root.bind("<minus>", lambda event: self.zoom_out())
        self.root.bind("<0>", lambda event: self.reset_zoom())
        
        # Bind mouse events for panning
        self.canvas.bind("<ButtonPress-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.pan_image)
        self.canvas.bind("<ButtonRelease-1>", self.stop_pan)
        
        # Bind mouse wheel for zooming
        self.canvas.bind("<MouseWheel>", self.mouse_wheel)  # Windows
        self.canvas.bind("<Button-4>", self.mouse_wheel)  # Linux scroll up
        self.canvas.bind("<Button-5>", self.mouse_wheel)  # Linux scroll down
        
    def open_folder(self):
        """Opens folder selection dialog and loads file lists"""
        self.base_path = filedialog.askdirectory(title="Select folder with images and markup")
        if not self.base_path:
            return
            
        # Get file lists
        self.image_files = sorted(glob.glob(os.path.join(self.base_path, "*.jpeg")))
        if not self.image_files:
            self.image_files = sorted(glob.glob(os.path.join(self.base_path, "*.jpg")))
        if not self.image_files:
            self.image_files = sorted(glob.glob(os.path.join(self.base_path, "*.png")))
            
        self.txt_files = sorted(glob.glob(os.path.join(self.base_path, "*.txt")))
        
        if not self.image_files or not self.txt_files:
            messagebox.showerror("Error", "No images or markup files found in the selected folder")
            return
            
        self.current_index = 0
        self.reset_zoom()
        self.show_current_image()
        
    def get_frame_number(self, file_path):
        """Extracts frame number from filename"""
        base_name = Path(file_path).stem
        try:
            return int(base_name)
        except ValueError:
            return None
        
    def find_next_available_frame(self, current_frame_num, direction=1):
        """Finds next available frame number (forward or backward)"""
        if not self.image_files:
            return None
            
        # Get all frame numbers
        frame_numbers = []
        for file in self.image_files:
            frame_num = self.get_frame_number(file)
            if frame_num is not None:
                frame_numbers.append((frame_num, file))
                
        if not frame_numbers:
            return None
            
        # Sort by frame number
        frame_numbers.sort(key=lambda x: x[0])
        
        if direction > 0:  # Moving forward
            for num, file in frame_numbers:
                if num > current_frame_num:
                    return self.image_files.index(file), num
            # If no frames ahead, return to first
            first_num = frame_numbers[0][0] if frame_numbers else None
            return 0, first_num
        else:  # Moving backward
            for num, file in reversed(frame_numbers):
                if num < current_frame_num:
                    return self.image_files.index(file), num
            # If no frames behind, go to last
            last_num = frame_numbers[-1][0] if frame_numbers else None
            return len(self.image_files) - 1, last_num
        
    def show_current_image(self):
        """Displays current image with markup"""
        if not self.image_files or self.current_index >= len(self.image_files):
            return
            
        # Load image
        img_path = self.image_files[self.current_index]
        self.current_image_path = img_path
        img = self.image_processor.load_image(img_path)
        if img is None:
            messagebox.showerror("Error", f"Failed to load image: {img_path}")
            return
            
        # Get base name for finding corresponding txt file
        base_name = Path(img_path).stem
        txt_path = None
        txt_exists = True
        
        # Find matching txt file
        for txt_file in self.txt_files:
            if Path(txt_file).stem == base_name:
                txt_path = txt_file
                break
                
        if txt_path is None:
            # If no exact match, try by frame number
            try:
                frame_number = int(base_name)
                txt_path = os.path.join(self.base_path, f"{frame_number}.txt")
                if not os.path.exists(txt_path):
                    txt_exists = False
                    messagebox.showwarning("Warning", f"No markup file found for {img_path}")
                    # Display image without markup
                    self.display_image_with_markup(img, [])
            except ValueError:
                txt_exists = False
                messagebox.showwarning("Warning", f"No markup file found for {img_path}")
                # Display image without markup
                self.display_image_with_markup(img, [])
                
        self.current_txt_path = txt_path if txt_exists else "Markup file not found"
                
        # Load and parse markup
        markup_data = []
        if txt_exists and txt_path:
            try:
                markup_data = self.markup_parser.parse_markup_file(txt_path)
            except Exception as e:
                messagebox.showerror("Error", f"Error reading markup file: {e}")
            
        # Display image with markup
        self.display_image_with_markup(img, markup_data)
        
        # Get current frame number
        frame_number = self.get_frame_number(img_path) or base_name
        
        # Get total number of frames (not just files)
        frame_numbers = []
        for file in self.image_files:
            num = self.get_frame_number(file)
            if num is not None:
                frame_numbers.append(num)
        
        # Update image counter - FIX: Show actual frame number instead of index
        if isinstance(frame_number, int):
            self.file_info.set(f"Frame: {frame_number}/{len(self.image_files)} (Image {self.current_index + 1}/{len(self.image_files)})")
        else:
            self.file_info.set(f"Image: {self.current_index + 1}/{len(self.image_files)} (Name: {frame_number})")
        
        # Update file info in overlay
        img_name = os.path.basename(img_path)
        txt_info = os.path.basename(txt_path) if txt_exists else "Markup file not found"
        self.overlay_text.set(f"Image: {img_name}\nMarkup: {txt_info}")
        
    def display_image_with_markup(self, img, markup_data):
        """Displays image with overlaid markup"""
        # Save original image with markup
        self.current_image = self.image_processor.apply_markup(img.copy(), markup_data)
        
        # Update display with current zoom
        self.update_display()
        
    def update_display(self):
        """Updates display with current zoom factor"""
        if self.current_image is None:
            return
            
        # Get image and canvas dimensions
        img_height, img_width = self.current_image.shape[:2]
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # If canvas not drawn yet, use window dimensions
        if canvas_width < 10:
            canvas_width = self.root.winfo_width() - 20
        if canvas_height < 10:
            canvas_height = self.root.winfo_height() - 60
            
        # Calculate new dimensions with zoom
        new_width = int(img_width * self.zoom_factor)
        new_height = int(img_height * self.zoom_factor)
        
        # Update scroll region
        self.canvas.config(scrollregion=(0, 0, new_width, new_height))
        
        # Convert and display image
        tk_img = self.image_processor.prepare_image_for_tkinter(
            self.current_image, 
            new_width, 
            new_height
        )
        self.tk_img = tk_img  # Keep reference to prevent garbage collection
        
        # Display in canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
        
        # Re-add overlay
        self.overlay_frame = tk.Frame(self.canvas, bg='#333333')
        self.overlay_frame.place(relx=0, rely=0, anchor='nw')
        
        self.overlay_label = tk.Label(
            self.overlay_frame, 
            textvariable=self.overlay_text, 
            bg='#333333', 
            fg='white', 
            justify=tk.LEFT,
            padx=10, 
            pady=5,
            anchor='w'
        )
        self.overlay_label.pack(fill=tk.X)
        
        # Update zoom info
        zoom_percentage = int(self.zoom_factor * 100)
        self.zoom_info.set(f"Zoom: {zoom_percentage}%")
        
    def next_image(self):
        """Switch to next image"""
        if not self.image_files:
            return
        
        current_frame_num = self.get_frame_number(self.image_files[self.current_index])
        if current_frame_num is not None:
            # Find next available frame
            next_index, next_frame = self.find_next_available_frame(current_frame_num, 1)
            if next_index == self.current_index:
                # If same index, we've reached the end and looped back
                messagebox.showinfo("Info", "End of list reached. Moving to first frame.")
            elif next_frame and next_frame > current_frame_num + 1:
                # If next frame number isn't sequential
                messagebox.showinfo("Info", 
                                    f"Frame {current_frame_num + 1} not found. Moving to frame {next_frame}.")
            
            self.current_index = next_index
        else:
            # If frame number not determined, just go to next file
            self.current_index = (self.current_index + 1) % len(self.image_files)
            if self.current_index == 0:
                messagebox.showinfo("Info", "End of list reached. Moving to first frame.")
            
        self.show_current_image()
        
    def prev_image(self):
        """Switch to previous image"""
        if not self.image_files:
            return
            
        current_frame_num = self.get_frame_number(self.image_files[self.current_index])
        if current_frame_num is not None:
            # Find previous available frame
            prev_index, prev_frame = self.find_next_available_frame(current_frame_num, -1)
            if prev_index == self.current_index:
                # If same index, we've reached the beginning and looped back
                messagebox.showinfo("Info", "Start of list reached. Moving to last frame.")
            elif prev_frame and prev_frame < current_frame_num - 1:
                # If previous frame number isn't sequential
                messagebox.showinfo("Info", 
                                    f"Frame {current_frame_num - 1} not found. Moving to frame {prev_frame}.")
            
            self.current_index = prev_index
        else:
            # If frame number not determined, just go to previous file
            was_at_start = self.current_index == 0
            self.current_index = (self.current_index - 1) % len(self.image_files)
            if was_at_start:
                messagebox.showinfo("Info", "Start of list reached. Moving to last frame.")
            
        self.show_current_image()
        
    def jump_to_image(self):
        """Jump to image by frame number"""
        if not self.image_files:
            return
            
        frame_number = simpledialog.askinteger("Jump", "Enter frame number:")
        if frame_number is None:
            return
            
        # Find file with specified frame number
        for i, file in enumerate(self.image_files):
            if self.get_frame_number(file) == frame_number:
                self.current_index = i
                self.show_current_image()
                return
                
        # If exact number not found, find nearest higher
        next_frame = None
        next_index = None
        
        for i, file in enumerate(sorted(self.image_files, key=lambda x: self.get_frame_number(x) or float('inf'))):
            file_frame_num = self.get_frame_number(file)
            if file_frame_num is not None and file_frame_num > frame_number:
                next_frame = file_frame_num
                next_index = self.image_files.index(file)
                break
                
        if next_index is not None:
            self.current_index = next_index
            messagebox.showinfo("Info", f"Frame {frame_number} not found. Moving to frame {next_frame}.")
            self.show_current_image()
        else:
            # If no frames higher than requested, go to first
            for i, file in enumerate(sorted(self.image_files, key=lambda x: self.get_frame_number(x) or float('inf'))):
                file_frame_num = self.get_frame_number(file)
                if file_frame_num is not None:
                    self.current_index = self.image_files.index(file)
                    messagebox.showinfo("Info", 
                                       f"Frame {frame_number} and later frames not found. Moving to frame {file_frame_num}.")
                    self.show_current_image()
                    return
                    
            messagebox.showinfo("Info", "No files with numeric names found.")
        
    def zoom_in(self):
        """Increase zoom level"""
        self.zoom_factor += self.zoom_step
        self.update_display()
        
    def zoom_out(self):
        """Decrease zoom level"""
        if self.zoom_factor > self.zoom_step:
            self.zoom_factor -= self.zoom_step
            self.update_display()
        
    def reset_zoom(self):
        """Reset zoom to 100%"""
        self.zoom_factor = 1.0
        if self.current_image is not None:
            self.update_display()
        
    def start_pan(self, event):
        """Start panning operation"""
        self.panning = True
        self.start_x = event.x
        self.start_y = event.y
        
    def pan_image(self, event):
        """Pan the image"""
        if not self.panning:
            return
            
        # Calculate offset
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        
        # Move view area
        self.canvas.xview_scroll(dx, "units")
        self.canvas.yview_scroll(dy, "units")
        
        # Update start coordinates
        self.start_x = event.x
        self.start_y = event.y
        
    def stop_pan(self, event):
        """End panning operation"""
        self.panning = False
        
    def mouse_wheel(self, event):
        """Handle mouse wheel scrolling"""
        # Determine scroll direction
        if event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):
            # Scroll up - zoom in
            self.zoom_in()
        elif event.num == 5 or (hasattr(event, 'delta') and event.delta < 0):
            # Scroll down - zoom out
            self.zoom_out()