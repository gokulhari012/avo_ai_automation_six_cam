import tkinter as tk
from PIL import Image, ImageTk
import subprocess
import os
import glob

# python_project_env = r"label_env\Scripts\python.exe" #For custom environment
# python_project_env = r"C:\AI-Software\avo_automation_yolo\my_app\label_env\Scripts\python.exe" #For custom environment
python_project_env = r"C:\AI-Software\avo_automation\my_app\label_env\Scripts\python.exe" #For custom environment
# python_project_env = "python"
disable_options = True

def main_window():
    # Create the main root windows
    root = tk.Tk()
    root.title("AVO CARBON")
    # root.geometry("700x820")
    root.geometry("700x820")

    # Set background image
    bg_image = Image.open("assets/flat_bg.png")
    bg_image = bg_image.resize((700, 820), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.image = bg_photo  # Keep a reference to avoid garbage collection
    bg_label.place(relwidth=1, relheight=1)

    # Add start button
    start_image = Image.open("assets/start.jpg")
    start_image = start_image.resize((200, 75), Image.LANCZOS)
    start_photo = ImageTk.PhotoImage(start_image)
    start_button = tk.Button(root, image=start_photo, command=lambda: goto_main_menu(root), borderwidth=0)
    start_button.image = start_photo
    start_button.place(x=250, y=400)

    root.mainloop()

# Function to apply opacity to an image
def apply_opacity(image, opacity):
    # Convert image to RGBA (if it's not already)
    image = image.convert("RGBA")
    
    # Create a new image with reduced opacity
    alpha = image.split()[3]  # Get the alpha channel (transparency)
    alpha = alpha.point(lambda p: p * opacity)  # Modify opacity
    image.putalpha(alpha)  # Set the new alpha channel

    return image

def goto_main_menu(root):
    # Destroy the welcome window
    root.destroy()

    # Create the main menu window
    main_menu = tk.Tk()
    main_menu.title("AVO CARBON - Main Menu")
    main_menu.geometry("700x820")

    # Set background image
    bg_image = Image.open("assets/flat_bg.png")
    bg_image = bg_image.resize((700, 820), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(main_menu, image=bg_photo)
    bg_label.image = bg_photo  # Keep a reference to avoid garbage collection
    bg_label.place(relwidth=1, relheight=1)

    # Add buttons for each menu item with 50 px spacing between them
    # new_dataset_image = Image.open("assets/New.jpg")
    # if disable_options:
    #     # Apply opacity (for example, 50% opacity)
    #     new_dataset_image = apply_opacity(new_dataset_image, 0.5)
    # new_dataset_image = new_dataset_image.resize((200, 75), Image.LANCZOS)
    # new_dataset_photo = ImageTk.PhotoImage(new_dataset_image)
    # new_dataset_button = tk.Button(main_menu, image=new_dataset_photo, command=lambda: open_new_dataset(main_menu), borderwidth=0)
    # if disable_options:
    #     # Disable the button
    #     new_dataset_button.config(state="disabled")
    # new_dataset_button.image = new_dataset_photo
    # new_dataset_button.place(x=250, y=260)

    create_brush_image = Image.open("assets/create_brush.jpg")
    create_brush_image = create_brush_image.resize((200, 75), Image.LANCZOS)
    create_brush_photo = ImageTk.PhotoImage(create_brush_image)
    create_brush_button = tk.Button(main_menu, image=create_brush_photo, command=open_create_brush, borderwidth=0)
    create_brush_button.image = create_brush_photo
    create_brush_button.place(x=250, y=260)

    select_brush_image = Image.open("assets/select_brush.jpg")
    select_brush_image = select_brush_image.resize((200, 75), Image.LANCZOS)
    select_brush_photo = ImageTk.PhotoImage(select_brush_image)
    select_brush_button = tk.Button(main_menu, image=select_brush_photo, command=open_select_brush, borderwidth=0)
    select_brush_button.image = select_brush_photo
    select_brush_button.place(x=250, y=360)

    # train_image = Image.open("assets/train.jpg")
    # if disable_options:
    #     train_image = apply_opacity(train_image, 0.5)
    # train_image = train_image.resize((200, 75), Image.LANCZOS)
    # train_photo = ImageTk.PhotoImage(train_image)
    # train_button = tk.Button(main_menu, image=train_photo, command=open_train, borderwidth=0)
    # if disable_options:
    #     # Disable the button
    #     train_button.config(state="disabled")
    # train_button.image = train_photo
    # train_button.place(x=250, y=460)

    train_image = Image.open("assets/Train_Size.jpg")
    train_image = train_image.resize((200, 75), Image.LANCZOS)
    train_photo = ImageTk.PhotoImage(train_image)
    train_button = tk.Button(main_menu, image=train_photo, command=open_train_size, borderwidth=0)
    train_button.image = train_photo
    train_button.place(x=250, y=460)

    daily_operations_image = Image.open("assets/Daily_Operations.jpg")
    daily_operations_image = daily_operations_image.resize((200, 75), Image.LANCZOS)
    daily_operations_photo = ImageTk.PhotoImage(daily_operations_image)
    daily_operations_button = tk.Button(main_menu, image=daily_operations_photo, command=open_daily_operations, borderwidth=0)
    daily_operations_button.image = daily_operations_photo
    daily_operations_button.place(x=250, y=560)

    more_operations_image = Image.open("assets/more_menu.jpg")
    more_operations_image = more_operations_image.resize((200, 75), Image.LANCZOS)
    more_operations_photo = ImageTk.PhotoImage(more_operations_image)
    more_operations_button = tk.Button(main_menu, image=more_operations_photo, command=open_more_menu, borderwidth=0)
    more_operations_button.image = more_operations_photo
    more_operations_button.place(x=250, y=660)

    main_menu.protocol("WM_DELETE_WINDOW", lambda: on_close(main_menu))
    main_menu.mainloop()

def open_create_brush():
    # Run the new_dataset.py script
    subprocess.Popen([python_project_env, "py_files/create_brush.py"])

def open_new_dataset(main_menu):
    # Run the new_dataset.py script
    subprocess.Popen([python_project_env, "py_files/new_dataset.py"])
    pass

def open_select_brush():
    # Open a new window for Select Brush
    subprocess.Popen([python_project_env, "py_files/select_brush.py"])

def open_train():
    # Open a new window for Train
    subprocess.Popen([python_project_env, "py_files/training.py"])
    
def open_train_size():
    subprocess.Popen([python_project_env, "py_files/tranning_color_match.py"])

def open_daily_operations():
    # Open a new window for Daily Operations
    
    process = subprocess.Popen([python_project_env, "py_files/daily_operations.py"])
    print("Daily operation triggerd")
    # process.wait()

def open_more_menu():
    subprocess.Popen([python_project_env, "py_files/more_options.py"])

def new_window(title):
    # Create a new window with the given title
    window = tk.Toplevel()
    window.title(title)
    window.geometry("700x820")

    # Set background image
    bg_image = Image.open("assets/flat_bg.png")
    bg_image = bg_image.resize((700, 820), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(window, image=bg_photo)
    bg_label.image = bg_photo  # Keep a reference to avoid garbage collection
    bg_label.place(relwidth=1, relheight=1)

    window.protocol("WM_DELETE_WINDOW", lambda: on_close(window))
    window.mainloop()

def on_close(window):
    # Close the window
    window.destroy()
    # Delete all generated button images
    for file_path in glob.glob("assets/dataset_*_button.jpg"):
        os.remove(file_path)

if __name__ == "__main__":
    main_window()
