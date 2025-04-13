import tkinter as tk
from markup_viewer import MarkupViewer

def main():
    root = tk.Tk()
    app = MarkupViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()