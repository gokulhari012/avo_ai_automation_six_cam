import tkinter as tk
from PIL import Image, ImageTk
import yolo_functions.analys as yolo_analys
import time
import threading
import os
import shutil
import yaml
import subprocess
import json

# Define the source directory containing subfolders
source_directory = "datasets"

# Define the common destination folder
destination_directory = "colleged_dataset"

current_directory = os.getcwd()
working_directory = current_directory

# Path to your YAML file
yaml_file = os.path.join(working_directory,"py_files" ,"yolo_functions", "data.yml")
# yaml_file = working_directory +"\\" +"yolo_functions/data.yml"
yolo_model = os.path.join(working_directory, "py_files" ,"yolo_functions", "yolo11n.pt")
# yolo_model = working_directory +"\\" +"yolo_functions/yolo11n.pt"

yolo_dataset = os.path.join(working_directory, destination_directory)

print(yaml_file)
print(yolo_model)
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

    start_image = Image.open("assets/start.jpg")
    start_image = start_image.resize((200, 75), Image.LANCZOS)
    start_photo = ImageTk.PhotoImage(start_image)
    start_button = tk.Button(window_close, image=start_photo, command=lambda: training_model(), borderwidth=0)
    start_button.image = start_photo
    start_button.place(x=250, y=260)

    close_image = Image.open("assets/close.jpg")
    close_image = close_image.resize((200, 75), Image.LANCZOS)
    close_photo = ImageTk.PhotoImage(close_image)
    close_button = tk.Button(window_close, image=close_photo, command=lambda: on_close(window_close), borderwidth=0)
    close_button.image = close_photo
    close_button.place(x=250, y=460)

    window_close.protocol("WM_DELETE_WINDOW", lambda: on_close(window_close))
    window_close.mainloop()

def on_close(window_close):
    global running
    # Close the window
    window_close.destroy()
    running = False

def copy_to_common():
    
    # Remove the existing directory and all its contents if it exists
    # if os.path.exists(destination_directory):
    #     shutil.rmtree(destination_directory)

    # Create the destination directory if it doesn't exist
    os.makedirs(destination_directory, exist_ok=True)

    # Loop through all subdirectories and move files
    for root, dirs, files in os.walk(source_directory):
        if "brushID_" in root:
            for file in files:
                source_path = os.path.join(root, file)
                destination_path = os.path.join(destination_directory, file)
                
                # Ensure file name uniqueness
                # if os.path.exists(destination_path):
                #     base, ext = os.path.splitext(file)
                #     count = 1
                #     while os.path.exists(destination_path):
                #         destination_path = os.path.join(destination_directory, f"{base}_{count}{ext}")
                #         count += 1
                # Check if the file already exists in the destination
                if not os.path.exists(destination_path):
                    shutil.copy2(source_path, destination_path)  # Preserve metadata
                    # print(f"Copied: {filename}")
                # else:
                    # print(f"Skipped: {filename} (Already exists)")
                
                # shutil.move(source_path, destination_path)
                # shutil.copy2(source_path, destination_path) # Preserves metadata like timestamps
                # shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
            print("All files have been Copied successfully!")

def update_data_yml():
    # Example usage - updating data.yml
    # current_directory = os.getcwd()
    dataset_folders = [folder for folder in os.listdir('./datasets') if os.path.isdir(os.path.join('./datasets', folder)) and folder.startswith('brushID_')]
    # dataset_folders.insert(0,"defect")

    # Extract numeric part and find max index
    indices  = [int(item.split("_")[1]) for item in dataset_folders if "_" in item and item.split("_")[1].isdigit()]
    print("Brush List: "+str(indices))
    max_index = max(indices)

    # Create a list with empty strings of the required size
    filled_list = ["Folder_Deleted"] * (max_index + 1)

    # Insert values in the correct positions
    for item in dataset_folders:
        idx = int(item.split("_")[1])
        filled_list[idx] = item

    dataset_folders = filled_list

    new_data = {
        "train": yolo_dataset,
        "val": yolo_dataset,
        "nc": len(dataset_folders)
    }
    try:
        # Load existing data
        with open(yaml_file, "r") as file:
            data = yaml.safe_load(file) or {}

        # Update with new data
        data.update(new_data)
        data["names"] = dataset_folders

        # Write back to the YAML file
        with open(yaml_file, "w") as file:
            yaml.dump(data, file, default_flow_style=False, sort_keys=False)

        print("YAML file updated successfully!")
    except Exception as e:
        print(f"Error updating YAML file: {e}")

def training_model():
    copy_to_common()
    update_data_yml()
    # yaml_file = r"C:\Users\gokul\Documents\projects\Avo Six Camera Ai\repo\avo_ai_automation_six_cam\my_app\yolo_functions\data.yml"
    # yolo_model = r"C:\Users\gokul\Documents\projects\Avo Six Camera Ai\repo\avo_ai_automation_six_cam\my_app\yolo_functions\yolo11n.pt"
    epochs = 60

    # Correcting the command formatting with proper quotes
    # command = f'yolo detect train data="{yaml_file}" model="{yolo_model}" epochs={epochs} imgsz=640 project="{working_directory}" name="brush_knowledge"'
    # command = f'yolo detect train data="{yaml_file}" model="{yolo_model}" epochs={epochs} imgsz=640'
    command = f'yolo detect train data="{yaml_file}" model="{yolo_model}" epochs={epochs} imgsz=640 name="brush_knowledge'
    # Open a new Command Prompt and run the command
    subprocess.Popen(f'start cmd /k "{command}"', shell=True)
    
    # Open a new Command Prompt and run the command
    # subprocess.Popen(["start", "cmd", "/k", command], shell=True)

daily_operation_window()
