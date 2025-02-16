import cv2
import serial
import time
import time
import threading
import json
import tkinter as tk
from PIL import Image, ImageTk
from multiprocessing import Process
import multiprocessing
import yolo_functions.analys as yolo_analys
from multiprocessing import Manager, Lock
is_ouput_required = False
# is_ouput_required = True



camera_index_list = [0,1,2,3,4,5]

settings_file_path = "./json/settings.json"


with open("configuration.json", "r") as file:
    json_data = json.load(file)

running = multiprocessing.Value('b', True)  # Shared variable for process control

camera_index_list = json_data["camera_index_list"]
time_delay = json_data["time_delay"] #time delay to take pictures
arduino_com_port = json_data["arduino_com_port"] #time delay to take pictures
is_ouput_required = json_data["is_ouput_required"] #arduino connection status.

# camera_0 = [0,0,0,0,0,0]
# camera_1 = [0,0,0,0,0,0]
# camera_2 = [0,0,0,0,0,0]
# camera_3 = [0,0,0,0,0,0]
# camera_4 = [0,0,0,0,0,0]
# camera_5 = [0,0,0,0,0,0]
# camera_map = {0:camera_0,1:camera_1,2:camera_2,3:camera_3,4:camera_4,5:camera_5}
# update_lock = threading.Lock()

# Initialize Manager and Lock for shared state
manager = Manager()
camera_map = manager.dict({i: manager.list([0, 0, 0, 0, 0, 0]) for i in range(6)})
update_lock = Lock()  # Lock for synchronizing updates

last_camera = 5

if is_ouput_required:
    # Set up serial communication with Arduino
    ser = serial.Serial(arduino_com_port, 9600)  # Replace 'COM7' with your actual port
    time.sleep(0.5)  # Reduced delay for Arduino initialization

    # Set servo to home position initially
    ser.write(b'H')
    print("Servo set to home position.")

servo_status = False
brush_id = 0

# Button dimensions
button_width, button_height = 50, 30

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

import json

def save_variable(variable_name, value):
    try:
        # Load existing data or initialize an empty dictionary
        try:
            with open(settings_file_path, 'r') as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        # Update the variable in the dictionary
        data[variable_name] = value

        # Save the updated data back to the file
        with open(settings_file_path, 'w') as file:
            json.dump(data, file, indent=4)
        # print(f"Variable '{variable_name}' saved successfully.")
    except Exception as e:
        print(f"Error saving variable '{variable_name}': {e}")

def load_variable(variable_name, default_value=0):
    try:
        data = {}
        with open(settings_file_path, 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return default_value
    except Exception as e:
        print(f"Error loading variable '{variable_name}': {e}")
        return default_value
    finally:
        return data.get(variable_name, default_value)

def append_and_rotate(camera_index, new_value):
    global camera_map
    print("Camera update List before")
    for i in range(len(camera_map)):
        print("camera "+str(i),end=": ")
        for j in camera_map[i]:
            print(str(j),end=" ")
        print("")
    with update_lock:
        camera_map[camera_index].append(new_value)  # Append new value
        camera_map[camera_index].pop(0)  # Remove the first element to maintain size
    print("Camera update List after")
    for i in range(len(camera_map)):
        print("camera "+str(i),end=": ")
        for j in camera_map[i]:
            print(str(j),end=" ")
        print("")

# Function to relay final decision to Arduino and update servo
def relay_servo_command(status):
    global servo_status
    if status != servo_status:  # Only send command if the status changes
        if status:
            if is_ouput_required:
                ser.write(b'A')  # Send "accepted" command
            print("Sent command: Accepted")
        else:
            if is_ouput_required:
                ser.write(b'R')  # Send "rejected" command to stay at home
            print("Sent command: Rejected")
        servo_status = status  # Update the servo status

# Function to check the diagonal values
def check_diagonal():
    # Iterate through each camera index and check the diagonal values
    print("Camera Detected List")
    for i in range(len(camera_map)):
        print("camera "+str(i),end=": ")
        for j in camera_map[i]:
            print(str(j),end=" ")
        print("")
        
    for i in range(len(camera_map)):
        if camera_map[i][i] == 1:  # Check diagonal value
            return False  # Return False if any diagonal value is 0
    return True  # Return True if no diagonal value is 0

def rejection_machanism():
    global brush_id
    try:
        brush_status = check_diagonal()
        relay_servo_command(brush_status)
        brush_id = brush_id + 1
        if brush_status:
            print("Brush "+str(brush_id)+" is Accepted")
        else:
            print("Brush "+str(brush_id)+" is Rejected ")
    except Exception as e:
            print(f"Error in rejection_machanism: {e}")

def is_last_camera(camera_index):
    if camera_index == last_camera:
        return True
    else:
        return False
    
def main_program(camera_id, camera_index, running):
    cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print(f"Error: Could not open camera id {camera_id} index{camera_index}")
        return
    
     # Read the folder name from selected_brush.txt
    with open("json/selected_brush.txt", "r") as file:
        folder_name = "datasets/"+file.read().strip()+"/"+str(camera_index)

    cb_on_cam = False
    any_defect_identified = False
    # Main loop
    while running.value:
        # Capture frame from webcam
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image from webcam.")
            break
        # t = time.process_time()
        frame, cb_identified, defect_identified = yolo_analys.check_frame(frame)
        # print(time.process_time()-t)
        window_name = f"Camera id: {camera_id} index: {camera_index}"+" - Q-quit"
        cv2.imshow(window_name, frame)
        # Check for key inputs
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # Quit the stream
            print(f"Closing All Cameras.")
            running.value = False
            break

        if not cb_on_cam and cb_identified: 
            cb_on_cam = True

        if not any_defect_identified and cb_on_cam and cb_identified and defect_identified:
            any_defect_identified = True

        if cb_on_cam and not cb_identified:
            cb_on_cam = False
            # Handle buffering and updating states
            if any_defect_identified:
                append_and_rotate(camera_index, 1)
            else:
                append_and_rotate(camera_index, 0)
            any_defect_identified = False
            if is_last_camera(camera_index):
                rejection_machanism()

    if is_ouput_required:
        ser.close()

def daily_operation_window(running):
    
    # Create a new window for Select Brush
    window_close = tk.Tk()
    window_close.title("Daily Operation")
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
    close_button = tk.Button(window_close, image=close_photo, command=lambda: on_close(window_close, running), borderwidth=0)
    close_button.image = close_photo
    close_button.place(x=250, y=360)

    window_close.protocol("WM_DELETE_WINDOW", lambda: on_close(window_close, running))
    window_close.mainloop()

def on_close(window_close, running):
    # Close the window
    window_close.destroy()
    running.value = False

if __name__ == "__main__":
    # multiprocessing.set_start_method("spawn")  # Ensure proper initialization

    thread_list = []
    processes = []
    
    # multiprocessing.set_start_method("spawn")
    t = threading.Thread(target=daily_operation_window, args=(running,))
    thread_list.append(t)
    t.start()
    # Start threads for each camera
    for camera_index, camera_id in enumerate(camera_index_list):
        try:
            process = Process(target=main_program, args=(camera_id, camera_index, running))
            process.start()
            processes.append(process)

        except Exception as e:
            print(f"Error initializing camera id: {camera_id} index: {camera_index} {e}")

    for process in processes:
        process.join()

    # Wait for threads to complete
    for t in thread_list:
        t.join()

    print("All camera daily operations are closed")
