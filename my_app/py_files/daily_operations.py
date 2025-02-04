import cv2
import time
import threading
import json
import tkinter as tk
from PIL import Image, ImageTk
import yolo_functions.analys as yolo_analys
from pymodbus.client import ModbusTcpClient as ModbusClient
import plc_communication as plc


camera_index_list = [0,1,2,3,4,5]

settings_file_path = "./json/settings.json"


with open("configuration.json", "r") as file:
    json_data = json.load(file)

running = True

camera_index_list = json_data["camera_index_list"]
rejection_time_delay = json_data["rejection_time_delay"] #time delay to take pictures
plc_ip_address = json_data["plc_ip_address"] #time delay to take pictures
is_ouput_required = json_data["is_ouput_required"] #arduino connection status.
brush_left_time_delay = json_data["brush_left_time_delay"]

camera_0 = [0,0,0,0,0,0]
camera_1 = [0,0,0,0,0,0]
camera_2 = [0,0,0,0,0,0]
camera_3 = [0,0,0,0,0,0]
camera_4 = [0,0,0,0,0,0]
camera_5 = [0,0,0,0,0,0]
camera_map = {0:camera_0,1:camera_1,2:camera_2,3:camera_3,4:camera_4,5:camera_5}

#0 for not detect - 1 - defect - 2 is good breash
last_updated_brush_id = {i:0 for i in range(6)}

brush_map = {}

camera_map_lock = threading.Lock()
brush_map_lock = threading.Lock()

last_camera = 5
first_camera = 0

if is_ouput_required:
    plc.setup(plc_ip_address)
    # Set servo to home position initially
    print("Servo set to home position.")

servo_status = True
brush_id = 0

brush_id_name = ""
# Read the folder name from selected_brush.txt
with open("json/selected_brush.txt", "r") as file:
    brush_id_name = file.read().strip()

window_close = ""
# Button dimensions
button_width, button_height = 50, 30

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

import json

def reset_brush():
    global brush_id, servo_status, brush_map, last_updated_brush_id
    servo_status = True
    brush_id = 0
    last_updated_brush_id = {i:0 for i in range(6)}
    brush_map = {}
    plc.setup(plc_ip_address)

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
    global camera_map, brush_map, last_updated_brush_id, running
    with camera_map_lock:
        camera_map[camera_index].append(new_value)  # Append new value
        camera_map[camera_index].pop(0)  # Remove the first element to maintain size
    with brush_map_lock:
         brush_id = last_updated_brush_id[camera_index] + 1
         if brush_id in brush_map:
            # print(camera_index)
            # print(brush_map)
            # print(last_updated_brush_id[camera_index])
            last_updated_brush_id[camera_index] = brush_id
            if 0 not in brush_map[last_updated_brush_id[camera_index]][:camera_index]:
                brush_map[last_updated_brush_id[camera_index]][camera_index] = new_value
            else: 
                print("From Camera index:"+str(camera_index)+" Some camera has skipped for brush ID: "+str(last_updated_brush_id[camera_index])+" Brush list: "+str(brush_map[last_updated_brush_id[camera_index]]))
                # running = False
                brush_map[last_updated_brush_id[camera_index]] = [1,1,1,1,1,1]
                last_updated_brush_id[camera_index-1] = last_updated_brush_id[camera_index-1] + 1 # camera_index 0 will not come to else part because [:0] is [] no 0 will come.

# Function to relay final decision to Arduino and update servo
def relay_servo_command(status):
    global servo_status
    print("Inside Servo control")
    time.sleep(rejection_time_delay/1000)
    if status != servo_status:  # Only send command if the status changes
        if status:
            if is_ouput_required:
                plc.write(0)  # Send "accepted" command
            print("Sent command: Accepted")
        else:
            if is_ouput_required:
                plc.write(1)  # Send "rejected" command to stay at home
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

def check_brush(brush_id):
    if 1 in brush_map[brush_id]:
        return False # not accepted
    else:
        return True # accepted
    
def rejection_machanism(brush_id):
    global brush_map
    try:
        brush_status = check_brush(brush_id)
        t = threading.Thread(target=relay_servo_command, args=(brush_status,))
        t.start()
        if brush_status:
            print("Brush "+str(brush_id)+" is Accepted")
        else:
            print("Brush "+str(brush_id)+" is Rejected ")
        print("brush status: "+str(brush_map[brush_id]))
        with brush_map_lock:
            brush_map.pop(brush_id)

    except Exception as e:
            print(f"Error in rejection_machanism: {e}")

def is_last_camera(camera_index):
    if camera_index == last_camera:
        return True
    else:
        return False
    
def is_first_camera(camera_index):
    if camera_index == first_camera:
        return True
    else:
        return False

def create_brush():
    global brush_map, brush_id
    with brush_map_lock:
        brush_id = brush_id + 1
        brush_map[brush_id] = [0,0,0,0,0,0]


def main_program(camera_id, camera_index):
    global running
    cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print(f"Error: Could not open camera id {camera_id} index{camera_index}")
        return
    
    previous_time = time.time() * 1000    
    cb_on_cam = False
    any_defect_identified = False
    make_delay = False
    # Main loop
    while running:
        # Capture frame from webcam
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image from webcam.")
            break
        # t = time.process_time()
        frame, cb_identified, defect_identified = yolo_analys.check_frame(frame, last_updated_brush_id[camera_index]+1,brush_id_name)
        # print(time.process_time()-t)
        window_name = f"Camera id: {camera_id} index: {camera_index}"+" - Q-quit"
        cv2.imshow(window_name, frame)
        # Check for key inputs
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # Quit the stream
            print(f"Closing All Cameras.")
            running = False
            # window_close.destroy()
            break

        if make_delay:
            current_time = time.time() * 1000
            if(previous_time + brush_left_time_delay < current_time):
                previous_time = current_time
                make_delay = False
        else:
            if not cb_on_cam and cb_identified: 
                cb_on_cam = True
                if is_first_camera(camera_index):
                    create_brush()

            if not any_defect_identified and cb_on_cam and cb_identified and defect_identified:
                any_defect_identified = True

            if cb_on_cam and not cb_identified:
                cb_on_cam = False
                # Handle buffering and updating states
                if any_defect_identified:
                    append_and_rotate(camera_index, 1) # defected
                else:
                    append_and_rotate(camera_index, 2) # good
                any_defect_identified = False
                if is_last_camera(camera_index):
                    rejection_machanism(last_updated_brush_id[last_camera])
                make_delay = True
                previous_time = time.time() * 1000
        
        if key == ord('r'):
            reset_brush()
            print("Reseted brush")
            
    if is_ouput_required:
        plc.close()

def daily_operation_window():
    global window_close
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

if __name__ == "__main__":
    # multiprocessing.set_start_method("spawn")  # Ensure proper initialization

    thread_list = []
  
    # multiprocessing.set_start_method("spawn")
    t = threading.Thread(target=daily_operation_window)
    thread_list.append(t)
    t.start()
    # Start threads for each camera
    for camera_index, camera_id in enumerate(camera_index_list):
        try:
            t = threading.Thread(target=main_program, args=(camera_id, camera_index,))
            t.start()
            thread_list.append(t)

        except Exception as e:
            print(f"Error initializing camera id: {camera_id} index: {camera_index} {e}")

    # Wait for threads to complete
    for t in thread_list:
        t.join()

    print("All camera daily operations are closed")
