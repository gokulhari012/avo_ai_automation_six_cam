import tkinter as tk
from PIL import Image, ImageTk, ImageFont, ImageDraw
import subprocess
import os
import cv2
import numpy as np
import glob
import pickle

def main_window():
    # Create the main root window
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
    start_button.place(x=250, y=560)

    root.mainloop()

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
    new_dataset_image = Image.open("assets/New.jpg")
    new_dataset_image = new_dataset_image.resize((200, 75), Image.LANCZOS)
    new_dataset_photo = ImageTk.PhotoImage(new_dataset_image)
    new_dataset_button = tk.Button(main_menu, image=new_dataset_photo, command=lambda: open_new_dataset(main_menu), borderwidth=0)
    new_dataset_button.image = new_dataset_photo
    new_dataset_button.place(x=250, y=260)

    select_brush_image = Image.open("assets/select_brush.jpg")
    select_brush_image = select_brush_image.resize((200, 75), Image.LANCZOS)
    select_brush_photo = ImageTk.PhotoImage(select_brush_image)
    select_brush_button = tk.Button(main_menu, image=select_brush_photo, command=open_select_brush, borderwidth=0)
    select_brush_button.image = select_brush_photo
    select_brush_button.place(x=250, y=410)

    train_image = Image.open("assets/train.jpg")
    train_image = train_image.resize((200, 75), Image.LANCZOS)
    train_photo = ImageTk.PhotoImage(train_image)
    train_button = tk.Button(main_menu, image=train_photo, command=open_train, borderwidth=0)
    train_button.image = train_photo
    train_button.place(x=250, y=560)

    daily_operations_image = Image.open("assets/Daily_Operations.jpg")
    daily_operations_image = daily_operations_image.resize((200, 75), Image.LANCZOS)
    daily_operations_photo = ImageTk.PhotoImage(daily_operations_image)
    daily_operations_button = tk.Button(main_menu, image=daily_operations_photo, command=open_daily_operations, borderwidth=0)
    daily_operations_button.image = daily_operations_photo
    daily_operations_button.place(x=250, y=680)

    main_menu.protocol("WM_DELETE_WINDOW", lambda: on_close(main_menu))
    main_menu.mainloop()

def open_new_dataset(main_menu):
    # Run the new_dataset.py script
    subprocess.Popen(["python", "new_dataset.py"])

def open_select_brush():
    # Open a new window for Select Brush
    subprocess.Popen(["python", "select_brush.py"])

def open_train():
    # Open a new window for Train
    subprocess.Popen(["python", "training.py"])
    

def open_daily_operations():
    # Open a new window for Daily Operations
    
    process = subprocess.Popen(["python", "daily_operations.py"])
    print("Daily operation triggerd")
    # process.wait()

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
