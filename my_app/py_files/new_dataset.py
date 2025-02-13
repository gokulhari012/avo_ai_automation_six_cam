import cv2
import os
import time
import shutil
import threading
import json
import yolo_functions.analys as yolo_analys

# Constants
width, video_height = 800, 600  # Window size
button_height = 100  # Space allocated for buttons
record_folder = None  # Global variable for the dataset folder

camera_index_list = [0,1,2,3,4,5]  # List of camera indices

with open("configuration.json", "r") as file:
    json_data = json.load(file)

camera_index_list = json_data["camera_index_list"]
brush_left_time_delay = json_data["brush_left_time_delay"]

thread_list = []
start_capturing = False
run = True

# Function to get the next dataset folder name
def get_next_dataset_folder():
    dataset_count = 1
    while os.path.exists(f"datasets/brushID_{dataset_count}"):
        dataset_count += 1
    return f"datasets/brushID_{dataset_count}"

# Create a new dataset folder
def create_dataset(camera_id):
    global record_folder
    camera_id = str(camera_id)
    if record_folder is None:
        record_folder = get_next_dataset_folder()
        os.makedirs(record_folder, exist_ok=True)
        print(f"Created dataset folder: {record_folder}")
    try:
        if not os.path.isdir(record_folder + "/" + camera_id):
            os.makedirs(record_folder + "/" + camera_id, exist_ok=True)
            print(f"Created camera ID folder: {record_folder}/{camera_id}")
    except Exception as e:
        print("Error creating dataset folder: " + str(e))

# Save a snapshot
def save_snapshot(camera_id, frame):
    create_dataset(camera_id)
    global record_folder
    camera_id = str(camera_id)
    if record_folder and os.path.isdir(record_folder + "/" + camera_id):
        filename = os.path.join(record_folder + "/" + camera_id, f'{record_folder.split("/")[0]}_{camera_id}_accept_{int(time.time()*1000)}.jpg')
        cv2.imwrite(filename, frame)
        print(f"Snapshot saved: {filename}")
    else:
        print("No dataset folder exists. Please create a dataset first.")
    
    return filename

def save_snapshot_labled(filename,camera_id, frame):
    create_dataset(camera_id)
    global record_folder
    camera_id = str(camera_id)
    if record_folder and os.path.isdir(record_folder + "/" + camera_id):
        # filename = os.path.join(record_folder + "/" + camera_id, f'{record_folder.split("/")[0]}_{camera_id}_accept_labeled_{int(time.time())}.jpg')
        # filename = os.path.join(record_folder + "/" + camera_id, f'snapshot_labeled_{int(time.time())}.jpg')
        cv2.imwrite(filename, frame)
        print(f"Snapshot labeled saved: {filename}")
    else:
        print("No dataset folder exists. Please create a dataset first.")

# Merge datasets
def merge_datasets():
    common_folder = 'datasets/common_dataset'
    os.makedirs(common_folder, exist_ok=True)
    dataset_folders = [folder for folder in os.listdir('./datasets') if os.path.isdir(folder) and folder.startswith('brushID_')]
    for folder in dataset_folders:
        for file in os.listdir(f"./datasets/{folder}"):
            src = os.path.join(f"./datasets/{folder}", file)
            dst = os.path.join(common_folder, f'{folder}_{file}')
            shutil.copy2(src, dst)
    print(f"All datasets merged into '{common_folder}'.")

def save_anotation(file_path, captured_position, captured_frame):
    # Save annotations
    # annotation_path = path.replace(".jpg", ".txt")
    with open(file_path, "w") as f:
        x1, y1, x2, y2 = captured_position
        label = int(record_folder.split("_")[-1])
        # Save annotation in YOLO format: class x_center y_center width height (normalized)
        x_center = (x1 + x2) / (2 * captured_frame.shape[1])
        y_center = (y1 + y2) / (2 * captured_frame.shape[0])
        width = (x2 - x1) / captured_frame.shape[1]
        height = (y2 - y1) / captured_frame.shape[0]
        f.write(f"{int(label)} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
        print(f"labeled file saved: {file_path}")

# Main function for each camera
def main_program(camera_id, camera):
    global start_capturing, run

    previous_time = time.time() * 1000
    current_time = previous_time
    make_delay = False

    print(f"Starting camera {camera_id}")
    window_name = f"Camera id: {camera_id} index: {camera_index_list.index(camera_id)}"+" - S-Start, Q-quit"

    while run:
        ret, frame = camera.read()
        if not ret:
            print(f"Failed to grab frame for Camera {camera_id}.")
            break

        # Display the video feed
        brush_id = "cb"
        if start_capturing:
            if make_delay:
                current_time = time.time() * 1000
                if(previous_time + brush_left_time_delay < current_time):
                    previous_time = current_time
                    make_delay = False
            else:
                frame, status, captured_frame, captured_position = yolo_analys.capture_cb(frame, brush_id)
                if status:
                    filename = ""
                    if captured_frame is not None and captured_frame.size > 0:
                        filename = save_snapshot(camera_id,captured_frame)
                        save_snapshot_labled(filename.replace(".jpg","_labeled.jpg"),camera_id,frame)
                        make_delay = True
                        if captured_position!=None:
                            save_anotation(filename.replace(".jpg",".txt"),captured_position,captured_frame)

        cv2.imshow(window_name, frame)
        
        # Check for key inputs
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # Quit the stream
            print(f"Closing Camera {camera_id}.")
            run = False
            start_capturing = False
            break
        elif key == ord('c'):  # Create dataset
            # create_dataset(camera_id)
            pass
        elif key == ord('s'):  # Save snapshot
            # print("Capturing Started")
            start_capturing = True
            # save_snapshot(camera_id, frame)
        elif key == ord('m'):  # Merge datasets
            # merge_datasets()
            pass

        # if start_capturing:
        #     current_time = time.time() * 1000
        #     if(previous_time + time_delay < current_time):
        #         previous_time = current_time
        #         save_snapshot(camera_id, frame)

    # Cleanup
    camera.release()
    cv2.destroyWindow(window_name)

# Start threads for each camera
start_capturing = True
for camera_id in camera_index_list:
    try:
        camera = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        if not camera.isOpened():
            print(f"Error: Could not open camera {camera_id}.")
            continue
        t = threading.Thread(target=main_program, args=(camera_id, camera,))
        thread_list.append(t)
        t.start()
    except Exception as e:
        print(f"Error initializing camera {camera_id}: {e}")

# Wait for threads to complete
for t in thread_list:
    t.join()

print("All camera streams closed.")
