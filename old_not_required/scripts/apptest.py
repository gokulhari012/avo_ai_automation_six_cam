import tkinter as tk

# Define the rectangular region coordinates
RECT_X1, RECT_Y1 = 50, 50  # Top-left corner of the rectangle
RECT_X2, RECT_Y2 = 150, 150  # Bottom-right corner of the rectangle

# Function to handle mouse clicks
def on_click(event):
    # Check if the click is inside the rectangular region
    if RECT_X1 <= event.x <= RECT_X2 and RECT_Y1 <= event.y <= RECT_Y2:
        open_new_window()

# Function to open a new window
def open_new_window():
    new_window = tk.Toplevel(root)
    new_window.title("New Window")
    new_window.geometry("200x100")
    label = tk.Label(new_window, text="You clicked inside the rectangle!")
    label.pack(pady=20)

# Create the main application window
root = tk.Tk()
root.title("Mouse Click Detector")
root.geometry("300x300")

# Bind the mouse click event to the main window
root.bind("<Button-1>", on_click)

# Run the Tkinter main loop
root.mainloop()
