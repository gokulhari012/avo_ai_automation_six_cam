import cv2
import threading
import os
import time
import json 

record_folder = "photos"

capture_photo_accept = False
capture_photo_reject = False

run = True

with open("configuration.json", "r") as file:
    json_data = json.load(file)

camera_index_list = json_data["camera_index_list"]

def make_camera_directory(path):
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)

def  save_snapshot(camera_id, frame, status):
    camera_id = str(camera_id)
    staus_name = ""
    if status == 'a':
        path = record_folder + "/" + camera_id+"/"+"accept"
        staus_name = "accept"
    else:
        path = record_folder + "/" + camera_id+"/"+"reject"
        staus_name = "reject"
    make_camera_directory(path)
    if os.path.isdir(path):
        filename = os.path.join(path, f'{camera_id}_{staus_name}_snapshot_{int(time.time())}.jpg')
        cv2.imwrite(filename, frame)
        print(f"Snapshot saved: {filename}")
    else:
        print("No dataset folder exists. Please create a dataset first.")


def save_snapshot_all(status):
    for camera_id in camera_index_list:
        camera_id = str(camera_id)
        if status == 'a':
            path = record_folder + "/" + camera_id+"/"+"accept"
        else:
            path = record_folder + "/" + camera_id+"/"+"reject"
        make_camera_directory(path)
        if os.path.isdir(path):
            filename = os.path.join(path, f'snapshot_{int(time.time())}.jpg')
            camera = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
            if not camera.isOpened():
                print(f"Camera {camera_id} could not be opened.")
                continue
            ret, frame = camera.read()
            cv2.imwrite(filename, frame)
            print(f"Snapshot saved: {filename}")
        else:
            print("No dataset folder exists. Please create a dataset first.")

def camera_stream(camera_id):
    """Function to display the camera stream."""
    global capture_photo_accept, capture_photo_reject, run
    camera = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    if not camera.isOpened():
        print(f"Camera {camera_id} could not be opened.")
        return
    camera_index =  camera_index_list.index(camera_id)
    window_name = f"Camera id: {camera_id} index: {camera_index}"+" - A-Accept, R-Reject , Q-quit"
    cv2.namedWindow(window_name)

    while run:
        ret, frame = camera.read()
        if not ret:
            print(f"Failed to grab frame for Camera index {camera_index}.")
            break

        # Display the frame
        cv2.imshow(window_name, frame)

        # Check for quit key
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print(f"Closing Camera index {camera_index}.")
            run = False
            break
        elif capture_photo_accept or key == ord('a'):
            capture_photo_accept = True
            save_snapshot(camera_index, frame, 'a')
            save_snapshot_all('a')
            time.sleep(1)
            capture_photo_accept = False
        elif capture_photo_reject or key == ord('r'):
            capture_photo_reject = True
            save_snapshot(camera_index, frame, 'r')
            # save_snapshot_all('r')
            time.sleep(1)
            capture_photo_reject = False

    # Cleanup
    camera.release()
    cv2.destroyWindow(window_name)

if __name__ == "__main__":

    # Start a thread for each camera
    threads = []
    for camera_id in camera_index_list:
        t = threading.Thread(target=camera_stream, args=(camera_id,))
        t.start()
        threads.append(t)

    # Wait for all threads to finish
    for t in threads:
        t.join()

    print("All camera streams closed.")
