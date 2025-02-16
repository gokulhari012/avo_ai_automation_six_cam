import cv2
import numpy as np
import pygame
import os
import time
import json
import copy

brush_dimensions_path = "./json/brush_dimensions.json"
settings_file_path = "./json/settings.json"

camera_index_list = [0,1,2,3,4,5]  # List of camera indices
with open("configuration.json", "r") as file:
    json_data = json.load(file)

brush_id_name = ""
# Read the folder name from selected_brush.txt
with open("json/selected_brush.txt", "r") as file:
    brush_id_name = file.read().strip()

camera_index_list = json_data["camera_index_list"]
contours_area_threshold = json_data["contours_area_threshold"]

first_camera_id = camera_index_list[0]  # List of camera indices

window_name = "Traning Dimensions Brush ID : "+ brush_id_name +" S-SaveArea, Q-Quit"


l_h1, l_s1, l_v1, h_h1, h_s1, h_v1 = (0, 12, 0, 179, 61, 165)
l_h2, l_s2, l_v2, h_h2, h_s2, h_v2 = (0, 0, 0, 85, 255, 201)

running = True

def save_variable():
    try:
        # Load existing data or initialize an empty dictionary
        # try:
        #     with open(settings_file_path, 'r') as file:
        #         data = json.load(file)
        # except (FileNotFoundError, json.JSONDecodeError):
        #     data = {}

        # Update the variable in the dictionary
        data = {}
        data["l_h1"], data["l_s1"], data["l_v1"], data["h_h1"], data["h_s1"], data["h_v1"] = l_h1, l_s1, l_v1, h_h1, h_s1, h_v1
        data["l_h2"], data["l_s2"], data["l_v2"], data["h_h2"], data["h_s2"], data["h_v2"] = l_h2, l_s2, l_v2, h_h2, h_s2, h_v2

        # Save the updated data back to the file
        with open(settings_file_path, 'w') as file:
            json.dump(data, file, indent=4)
        # print(f"Variable '{variable_name}' saved successfully.")
    except Exception as e:
        print(f"Error saving variables: {e}")
        
def load_variable():
    try:
        data = {}
        with open(settings_file_path, 'r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        print(f"Error loading setting json : {e}")
    

def load_values():
    global l_h1, l_s1, l_v1, h_h1, h_s1, h_v1, l_h2, l_s2, l_v2, h_h2, h_s2, h_v2
    data = load_variable()
    if data:
        l_h1, l_s1, l_v1, h_h1, h_s1, h_v1 = (data["l_h1"], data["l_s1"], data["l_v1"], data["h_h1"], data["h_s1"], data["h_v1"])
        l_h2, l_s2, l_v2, h_h2, h_s2, h_v2 = (data["l_h2"], data["l_s2"], data["l_v2"], data["h_h2"], data["h_s2"], data["h_v2"])

def nothing(x):
    pass

# Function to draw buttons
def draw_window():
   
    # Create a window
    cv2.namedWindow(window_name)

    # Create trackbars for first color range (Lower and Upper HSV)
    cv2.createTrackbar("Low H1", window_name, l_h1, 179, nothing)
    cv2.createTrackbar("Low S1", window_name, l_s1, 255, nothing)
    cv2.createTrackbar("Low V1", window_name, l_v1, 255, nothing)
    cv2.createTrackbar("High H1", window_name, h_h1, 179, nothing)
    cv2.createTrackbar("High S1", window_name, h_s1, 255, nothing)
    cv2.createTrackbar("High V1", window_name, h_v1, 255, nothing)

    # Create trackbars for second color range
    cv2.createTrackbar("Low H2", window_name, l_h2, 179, nothing)
    cv2.createTrackbar("Low S2", window_name, l_s2, 255, nothing)
    cv2.createTrackbar("Low V2", window_name, l_v2, 255, nothing)
    cv2.createTrackbar("High H2", window_name, h_h2, 179, nothing)
    cv2.createTrackbar("High S2", window_name, h_s2, 255, nothing)
    cv2.createTrackbar("High V2", window_name, h_v2, 255, nothing)

# Save areas to a single text file
def save_areas(areas):
    try:
        # Load existing data or initialize an empty dictionary
        try:
            with open(brush_dimensions_path, 'r') as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        # Update the variable in the dictionary
        
        data[brush_id_name+"_area"] = areas

        # Save the updated data back to the file
        with open(brush_dimensions_path, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Brush Area: '{areas}' saved successfully.")
    except Exception as e:
        print(f"Error saving Brush Area: '{areas}': {e}")
        

def main_loop(cap):
    global l_h1, l_s1, l_v1, h_h1, h_s1, h_v1, l_h2, l_s2, l_v2, h_h2, h_s2, h_v2, running

    while running:
        # Capture frame from webcam
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image from webcam.")
            break
        image_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Get trackbar positions
        l_h1 = cv2.getTrackbarPos("Low H1", window_name)
        l_s1 = cv2.getTrackbarPos("Low S1", window_name)
        l_v1 = cv2.getTrackbarPos("Low V1", window_name)
        h_h1 = cv2.getTrackbarPos("High H1", window_name)
        h_s1 = cv2.getTrackbarPos("High S1", window_name)
        h_v1 = cv2.getTrackbarPos("High V1", window_name)

        l_h2 = cv2.getTrackbarPos("Low H2", window_name)
        l_s2 = cv2.getTrackbarPos("Low S2", window_name)
        l_v2 = cv2.getTrackbarPos("Low V2", window_name)
        h_h2 = cv2.getTrackbarPos("High H2", window_name)
        h_s2 = cv2.getTrackbarPos("High S2", window_name)
        h_v2 = cv2.getTrackbarPos("High V2", window_name)

        # Define color ranges
        lower1 = np.array([l_h1, l_s1, l_v1])
        upper1 = np.array([h_h1, h_s1, h_v1])
        lower2 = np.array([l_h2, l_s2, l_v2])
        upper2 = np.array([h_h2, h_s2, h_v2])

        # Create masks
        mask1 = cv2.inRange(image_hsv, lower1, upper1)
        mask2 = cv2.inRange(image_hsv, lower2, upper2)

        # Combine masks
        combined_mask = cv2.bitwise_or(mask1, mask2)

        result = cv2.bitwise_and(frame, frame, mask=combined_mask)

        # === SMOOTHING THE MASK ===
        kernel = np.ones((5, 5), np.uint8)  # Kernel for morphological operations

        # 1. Apply Gaussian Blur (smooths edges)
        blurred_mask = cv2.GaussianBlur(combined_mask, (5, 5), 0)

        # 2. Apply Morphological Closing (fills small holes)
        closed_mask = cv2.morphologyEx(blurred_mask, cv2.MORPH_CLOSE, kernel, iterations=2)

        # 3. Apply Morphological Opening (removes small noise)
        smoothed_mask = cv2.morphologyEx(closed_mask, cv2.MORPH_OPEN, kernel, iterations=2)

        # Find contours on the smoothed mask
        contours, _ = cv2.findContours(smoothed_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        frame_copy = copy.deepcopy(frame)
        contours_area = 0
        for cnt in contours:
            if cv2.contourArea(cnt) > contours_area_threshold:  # Ignore small objects
                contours_area = cv2.contourArea(cnt)
                # Get minimum area rectangle
                rect = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(rect)
                box = np.intp(box)

                # Calculate width & height
                width = np.linalg.norm(box[0] - box[1])
                height = np.linalg.norm(box[1] - box[2])

                # Draw bounding box
                cv2.drawContours(frame_copy, [box], 0, (0, 255, 0), 2)

                # Display width & height
                cv2.putText(frame_copy, f"W: {width:.1f}px", (box[0][0], box[0][1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                cv2.putText(frame_copy, f"H: {height:.1f}px", (box[1][0], box[1][1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                cv2.putText(frame_copy, f"Brush ID: "+brush_id_name, (20, 40),
                            cv2.FONT_HERSHEY_TRIPLEX, 0.8, (0, 255, 255), 1)
                cv2.putText(frame_copy, f"Area: {contours_area:.1f}px", (20, 80),
                            cv2.FONT_HERSHEY_TRIPLEX, 0.8, (0, 100, 255), 1)

                # Approximate contour with a polygon
                epsilon = 0.01 * cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True)

                # Draw polygon
                cv2.polylines(frame_copy, [approx], True, (0, 0, 255), 2)

                # Measure point-to-point distances
                for j in range(len(approx)):
                    pt1 = tuple(approx[j][0])
                    pt2 = tuple(approx[(j + 1) % len(approx)][0])  # Next point (loop back)
                    distance = np.linalg.norm(np.array(pt1) - np.array(pt2))
                    midpoint = ((pt1[0] + pt2[0]) // 2, (pt1[1] + pt2[1]) // 2)

                    # Display distance
                    cv2.putText(frame_copy, f"{distance:.1f}px", midpoint, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
                    
            # print("Mask Area: "+str(contours_area))

        # Show results
        cv2.imshow("Original", frame)
        cv2.imshow("Dimensions Marked", frame_copy)
        cv2.imshow("Mask", combined_mask)
        cv2.imshow("Smoothed Mask", smoothed_mask)
        cv2.imshow(window_name, result)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # Quit the stream
            print(f"Closing All Camera")
            running = False
            break
        if key == ord('s'):  # Quit the stream
            if not contours_area == 0:
                save_variable()
                save_areas(contours_area)
                print(f"Saved Area")
            print(f"Closing All Camera")
            running = False
            break

def init_program():
    cap = cv2.VideoCapture(first_camera_id, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print(f"Error: Could not open camera id {first_camera_id} index{camera_index_list.index(first_camera_id)}")
    load_values()
    draw_window()
    main_loop(cap)

init_program()

cv2.destroyAllWindows()
print ("Tranning Dimensions successfully Completed")

