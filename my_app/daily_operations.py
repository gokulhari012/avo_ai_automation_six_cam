import cv2
import numpy as np
import pygame
import serial
import time
import time
import threading
import json
import tkinter as tk
from PIL import Image, ImageTk, ImageFont, ImageDraw
import os
import glob
from multiprocessing import Process
import multiprocessing

is_ouput_required = False
# is_ouput_required = True



camera_index_list = [0,1,2,3,4,5]

settings_file_path = "./settings.json"


with open("configuration.json", "r") as file:
    json_data = json.load(file)

running = multiprocessing.Value('b', True)  # Shared variable for process control

camera_index_list = json_data["camera_index_list"]
time_delay = json_data["time_delay"] #time delay to take pictures
arduino_com_port = json_data["arduino_com_port"] #time delay to take pictures
is_ouput_required = json_data["is_ouput_required"] #arduino connection status.

camera_0 = [0,0,0,0,0,0]
camera_1 = [0,0,0,0,0,0]
camera_2 = [0,0,0,0,0,0]
camera_3 = [0,0,0,0,0,0]
camera_4 = [0,0,0,0,0,0]
camera_5 = [0,0,0,0,0,0]

camera_map = {0:camera_0,1:camera_1,2:camera_2,3:camera_3,4:camera_4,5:camera_5}

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
    camera_map[camera_index].append(new_value)  # Append new value
    camera_map[camera_index].pop(0)  # Remove the first element to maintain size

# Function to draw buttons
def draw_buttons(window):
    font = pygame.font.SysFont(None, 24)
    window.blit(font.render('Threshold Min        Threshold Max', True, BLACK), (10, 10))
    pygame.draw.rect(window, RED, (10, 30, button_width, button_height))  # Decrease min threshold
    pygame.draw.rect(window, GREEN, (70, 30, button_width, button_height))  # Increase min threshold
    pygame.draw.rect(window, RED, (150, 30, button_width, button_height))  # Decrease max threshold
    pygame.draw.rect(window, GREEN, (210, 30, button_width, button_height))  # Increase max threshold

    # Button labels
    window.blit(font.render('-', True, BLACK), (30, 35))
    window.blit(font.render('+', True, BLACK), (90, 35))
    window.blit(font.render('-', True, BLACK), (170, 35))
    window.blit(font.render('+', True, BLACK), (230, 35))

# Function to relay final decision to Arduino and update servo
def relay_servo_command(status):
    global servo_status
    if status != servo_status:  # Only send command if the status changes
        if status == "Accepted":
            if is_ouput_required:
                ser.write(b'A')  # Send "accepted" command
            print("Sent command: Accepted")
        elif status == "Rejected":
            if is_ouput_required:
                ser.write(b'R')  # Send "rejected" command to stay at home
            print("Sent command: Rejected")
        servo_status = status  # Update the servo status

# Function to check the diagonal values
def check_diagonal():
    # Iterate through each camera index and check the diagonal values
    for i in range(len(camera_map)):
        if camera_map[i][i] == 0:  # Check diagonal value
            return False  # Return False if any diagonal value is 0
    return True  # Return True if no diagonal value is 0

def rejection_machanism(running):
    global brush_id
    while running.value:
        try:
            brush_status = check_diagonal()
            relay_servo_command(brush_status)
            brush_id = brush_id + 1
            if brush_status:
                print("Brush "+str(brush_id)+" is Accepted")
            else:
                print("Brush "+str(brush_id)+" is Rejected ")
            time.sleep(time_delay/1000)
        except Exception as e:
            print(f"Error in rejection_machanism: {e}")

# Function to apply threshold and convert image to Pygame surface
def apply_threshold(gray, threshold_min, threshold_max, min_area, max_area):
    global last_state, buffer_state, last_detection_time, state_confirmed
    _, threshold = cv2.threshold(gray, threshold_min, threshold_max, cv2.THRESH_BINARY)
    threshold_rgb = cv2.cvtColor(threshold, cv2.COLOR_GRAY2RGB)

    # Find contours
    contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    brush_detected = False  # Flag to track if a brush is detected

    cnt_temp = None
    # Draw contours and determine brush state
    for cnt in contours:
        area = cv2.contourArea(cnt)
        cnt_temp = cv2.boundingRect(cnt)
        if area > min_area and area < max_area:  # Filter by area threshold
            brush_detected = True
            status = "Accepted"
            color = (0, 255, 0)
            break
    else:
        brush_detected = False
        status = "Rejected"
        color = (0, 0, 255)
    if cnt_temp!=None:
        x, y, w, h = cnt_temp
        cv2.drawContours(threshold_rgb, [cnt], -1, (0, 255, 0), 2)
        cv2.putText(threshold_rgb, f"Area: {int(area)}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        cv2.rectangle(threshold_rgb, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.putText(threshold_rgb, status, (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
    surface = pygame.surfarray.make_surface(threshold_rgb.transpose((1, 0, 2)))
    return surface, brush_detected


def main_program(camera_id, camera_index, running):

    cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print(f"Error: Could not open camera {camera_id}.")
        return
    
    previous_time = time.time() * 1000
    current_time = previous_time

     # Read the folder name from brush.txt
    with open("brush.txt", "r") as file:
        folder_name = "datasets/"+file.read().strip()+"/"+str(camera_id)

    # Read captured areas from the corresponding text file
    areas_file = f"{folder_name}/{camera_id}.txt"
    with open(areas_file, "r") as file:
        areas = [float(value) for line in file.readlines() for value in line.strip()[1:-1].split(',') if value.strip()]
        #print(areas)
        max_area = max(areas)
        min_area = min(areas)

    # Initialize Pygame
    pygame.init()

    # Set up display
    window_width, window_height = 640, 580  # Assuming a standard webcam resolution
    window = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Threshold Adjuster ID: "+str(camera_id)+" Index: "+str(camera_index))
 

    # Initial threshold values based on captured areas
    threshold_min = load_variable(str(camera_index)+"_threshold_min",0)
    threshold_max = load_variable(str(camera_index)+"_threshold_max",255)

    # Main loop
    while running.value:
        # Capture frame from webcam
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image from webcam.")
            break

        # Convert the image to grayscale
        framea = frame[:, 300:700]
        frame2 = cv2.bitwise_not(framea)
        gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running.value = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos

                # Decrease min threshold button
                if 10 <= mouse_x <= 10 + button_width and 30 <= mouse_y <= 30 + button_height:
                    threshold_min = max(0, threshold_min - 5)
                    save_variable(str(camera_index)+"_threshold_min",threshold_min)
                    print(f"Updated threshold_min: {threshold_min}")

                # Increase min threshold button
                elif 70 <= mouse_x <= 70 + button_width and 30 <= mouse_y <= 30 + button_height:
                    threshold_min = min(255, threshold_min + 5)
                    save_variable(str(camera_index)+"_threshold_min",threshold_min)
                    print(f"Updated threshold_min: {threshold_min}")

                # Decrease max threshold button
                elif 150 <= mouse_x <= 150 + button_width and 30 <= mouse_y <= 30 + button_height:
                    threshold_max = max(0, threshold_max - 5)
                    save_variable(str(camera_index)+"_threshold_max",threshold_max)
                    print(f"Updated threshold_max: {threshold_max}")

                # Increase max threshold button
                elif 210 <= mouse_x <= 210 + button_width and 30 <= mouse_y <= 30 + button_height:
                    threshold_max = min(255, threshold_max + 5)
                    save_variable(str(camera_index)+"_threshold_max",threshold_max)
                    print(f"Updated threshold_max: {threshold_max}")
                
        # Update the display
        window.fill(WHITE)
        draw_buttons(window)
        threshold_surface, brush_detected = apply_threshold(gray, threshold_min, threshold_max, min_area, max_area)
        window.blit(threshold_surface, (10, 80))
        pygame.display.flip()
        # Handle buffering and updating states
        current_time = time.time() * 1000
        if(previous_time + time_delay < current_time):
            previous_time = current_time
            if brush_detected:
                append_and_rotate(camera_index, 1)
            else:
                append_and_rotate(camera_index, 0)

        # time.sleep(time_delay)

    # Release resources and quit
    cap.release()
    pygame.quit()
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
    pygame.quit()

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
            print(f"Error initializing camera {camera_id}: {e}")

    t = threading.Thread(target=rejection_machanism, args=(running,))
    thread_list.append(t)
    t.start()

    for process in processes:
        process.join()

    # Wait for threads to complete
    for t in thread_list:
        t.join()

    print("All camera daily operations are closed")
