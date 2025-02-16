import tkinter as tk
from PIL import Image, ImageTk
import subprocess
import os
import glob

# python_project_env = r"label_env\Scripts\python.exe" #For custom environment
# python_project_env = r"C:\AI-Software\avo_automation_yolo\my_app\label_env\Scripts\python.exe" #For custom environment
python_project_env = r"C:\AI-Software\avo_automation\my_app\label_env\Scripts\python.exe" #For custom environment
# python_project_env = "python"
disable_options = False

# Function to apply opacity to an image
def apply_opacity(image, opacity):
    # Convert image to RGBA (if it's not already)
    image = image.convert("RGBA")
    
    # Create a new image with reduced opacity
    alpha = image.split()[3]  # Get the alpha channel (transparency)
    alpha = alpha.point(lambda p: p * opacity)  # Modify opacity
    image.putalpha(alpha)  # Set the new alpha channel

    return image

def goto_more_menu():

    # Create the main menu window
    main_menu = tk.Tk()
    main_menu.title("AVO CARBON - More Menu")
    main_menu.geometry("700x820")

    # Set background image
    bg_image = Image.open("assets/flat_bg.png")
    bg_image = bg_image.resize((700, 820), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(main_menu, image=bg_photo)
    bg_label.image = bg_photo  # Keep a reference to avoid garbage collection
    bg_label.place(relwidth=1, relheight=1)

    # Add buttons for each menu item with 50 px spacing between them
    new_dataset_image = Image.open("assets/New.jpg")
    if disable_options:
        # Apply opacity (for example, 50% opacity)
        new_dataset_image = apply_opacity(new_dataset_image, 0.5)
    new_dataset_image = new_dataset_image.resize((200, 75), Image.LANCZOS)
    new_dataset_photo = ImageTk.PhotoImage(new_dataset_image)
    new_dataset_button = tk.Button(main_menu, image=new_dataset_photo, command=lambda: open_new_dataset(main_menu), borderwidth=0)
    if disable_options:
        # Disable the button
        new_dataset_button.config(state="disabled")
    new_dataset_button.image = new_dataset_photo
    new_dataset_button.place(x=250, y=260)


    select_brush_image = Image.open("assets/select_brush.jpg")
    select_brush_image = select_brush_image.resize((200, 75), Image.LANCZOS)
    select_brush_photo = ImageTk.PhotoImage(select_brush_image)
    select_brush_button = tk.Button(main_menu, image=select_brush_photo, command=open_select_brush, borderwidth=0)
    select_brush_button.image = select_brush_photo
    select_brush_button.place(x=250, y=360)

    train_image = Image.open("assets/train.jpg")
    train_image = train_image.resize((200, 75), Image.LANCZOS)
    train_photo = ImageTk.PhotoImage(train_image)
    train_button = tk.Button(main_menu, image=train_photo, command=open_train, borderwidth=0)
    train_button.image = train_photo
    train_button.place(x=250, y=460)

    main_menu.protocol("WM_DELETE_WINDOW", lambda: on_close(main_menu))
    main_menu.mainloop()

def open_new_dataset(main_menu):
    # Run the new_dataset.py script
    subprocess.Popen([python_project_env, "py_files/new_dataset.py"])
    pass

def open_select_brush():
    # Open a new window for Select Brush
    subprocess.Popen([python_project_env, "py_files/select_brush-old.py"])

def open_train():
    # Open a new window for Train
    subprocess.Popen([python_project_env, "py_files/training.py"])


def on_close(window):
    # Close the window
    window.destroy()
    # Delete all generated button images
    for file_path in glob.glob("assets/dataset_*_button.jpg"):
        os.remove(file_path)

if __name__ == "__main__":
    goto_more_menu()
