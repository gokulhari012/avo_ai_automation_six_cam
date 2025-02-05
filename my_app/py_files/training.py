import tkinter as tk
from PIL import Image, ImageTk
import yolo_functions.analys as yolo_analys
import time
import threading
import os
import shutil
import yaml
import subprocess

# Define the source directory containing subfolders
source_directory = "datasets"

# Define the common destination folder
destination_directory = "colleged_dataset"

# Path to your YAML file
yaml_file = "yolo_functions/data.yml"
yolo_model = "yolo_functions/yolo11n.pt"
epochs = 60

def daily_operation_window():
    global window_close
    # Create a new window for Select Brush
    window_close = tk.Tk()
    window_close.title("Training model")
    window_close.geometry("700x820")
    
    # Set background image
    bg_image = Image.open("assets/Technology Wallpaper.jpg")
    bg_image = bg_image.resize((700, 820), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(window_close, image=bg_photo)
    bg_label.image = bg_photo  # Keep a reference to avoid garbage collection
    bg_label.place(relwidth=1, relheight=1)

    close_image = Image.open("assets/close.jpg")
    close_image = close_image.resize((200, 75), Image.LANCZOS)
    close_photo = ImageTk.PhotoImage(close_image)
    close_button = tk.Button(window_close, image=close_photo, command=lambda: on_close(window_close), borderwidth=0)
    close_button.image = close_photo
    close_button.place(x=250, y=360)

    window_close.protocol("WM_DELETE_WINDOW", lambda: on_close(window_close))
    window_close.mainloop()

def on_close(window_close):
    global running
    # Close the window
    window_close.destroy()
    running = False

def move_to_common():
     # Create the destination directory if it doesn't exist
    os.makedirs(destination_directory, exist_ok=True)

    # Loop through all subdirectories and move files
    for root, dirs, files in os.walk(source_directory):
        if "brushID_" in root:
            for file in files:
                source_path = os.path.join(root, file)
                destination_path = os.path.join(destination_directory, file)
                
                # Ensure file name uniqueness
                if os.path.exists(destination_path):
                    base, ext = os.path.splitext(file)
                    count = 1
                    while os.path.exists(destination_path):
                        destination_path = os.path.join(destination_directory, f"{base}_{count}{ext}")
                        count += 1
                
                shutil.move(source_path, destination_path)

            print("All files have been moved successfully!")

def update_data_yml():
    # Example usage - updating data.yml
    current_directory = os.getcwd()
    current_directory = current_directory+"/"+yaml_file
    dataset_folders = [folder for folder in os.listdir('./datasets') if os.path.isdir(os.path.join('./datasets', folder)) and folder.startswith('brushID_')]
    dataset_folders.insert(0,"defect")
    new_data = {
        "train": current_directory,
        "val": current_directory,
        "nc": len(dataset_folders),
        "names": dataset_folders
    }
    try:
        # Load existing data
        with open(yaml_file, "r") as file:
            data = yaml.safe_load(file) or {}

        # Update with new data
        data.update(new_data)

        # Write back to the YAML file
        with open(yaml_file, "w") as file:
            yaml.dump(data, file, default_flow_style=False, sort_keys=False)

        print("YAML file updated successfully!")
    except Exception as e:
        print(f"Error updating YAML file: {e}")

def training_model():
    move_to_common()
    update_data_yml()

    command = f'yolo detect train data="{yaml_file}" model={yolo_model} epochs={epochs} imgsz=640'
    # Open a new Command Prompt and run the command
    subprocess.Popen(["start", "cmd", "/k", command], shell=True)

daily_operation_window()
