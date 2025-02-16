import cv2
from ultralytics import YOLO
import logging
import numpy as np
from logger import log_info, log_error
import json 

brush_dimensions_path = "./json/brush_dimensions.json"
settings_file_path = "./json/settings.json"

with open(brush_dimensions_path, "r") as file:
    brush_dimensions_json = json.load(file)

with open("configuration.json", "r") as file:
    json_data = json.load(file)
contours_area_threshold = json_data["contours_area_threshold"]
contours_area_tolarance = json_data["contours_area_tolarance"]

brush_id_name = ""
# Read the folder name from selected_brush.txt
with open("json/selected_brush.txt", "r") as file:
    brush_id_name = file.read().strip()

logging.getLogger("ultralytics").setLevel(logging.ERROR) 
confidence = 0.50
defect_confidence = 0.4
square_value = 100
square_value_detect = 100

# Load the YOLOv8 model
common_knowledge_path = "common_knowledge/weights/best.pt"
# model_path = "runs/detect/train3/weights/last.pt"
common_knowledge_model = YOLO(common_knowledge_path)
# Get class names and colors
common_knowledge_class_names = common_knowledge_model.names


brush_knowledge_path = "brush_knowledge/weights/best.pt"
brush_knowledge_model = YOLO(brush_knowledge_path)
brush_knowledge_class_names = brush_knowledge_model.names

colors = {"cb":(0,255,0),"defect":(0,0,255)}

# Reference object for calibration (example)
real_world_size = 10  # in mm (for example, the reference object's real-world size)
pixel_size = 100  # in pixels (size of the reference object in the image)
conversion_factor = real_world_size / pixel_size

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

load_values()

def check_frame(frame, brush_count_id, brush_id):
    cb_identified = False 
    defect_identified = False 
    cb_dimensions = (0,0)

    height, width, _ = frame.shape
    center_x, center_y = width // 2, height // 2
    
    # Perform detection
    results = brush_knowledge_model(frame)
    detections = results[0]
    label_confidence_map = {}
    label_value_map = {}
    # Draw bounding boxes
    #log_info("Analys start")
    for box in detections.boxes:
        # print(box)
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        conf = box.conf[0].item()
        class_id = int(box.cls[0].item())
        class_name = brush_knowledge_class_names[class_id]
        #if True:
        # Modify condition as needed
        obj_center_x, obj_center_y = x1+((x2-x1)//2), y1+((y2-y1)//2)
        # Check if object is near center
        if abs(center_x-square_value_detect) <= obj_center_x <= abs(center_x+square_value_detect) and abs(center_y-square_value_detect) <= obj_center_y <= abs(center_y+square_value_detect):
            if class_name == "brushID_0" or class_name == 'defect': # brushID_0 is defect
                if conf > defect_confidence:
                    color = colors["defect"]
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    label = f"defect: {conf:.2f}"
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)             
                    if not defect_identified:
                        defect_identified = True
                    log_info("Decfect identified 1")
            else :
                if conf > confidence:
                    label_confidence_map[class_name] = conf
                    label_value_map[class_name] = (x1, y1, x2, y2)
                    log_info("cp identified 1")

            

    if label_confidence_map and label_value_map:
        maxmium_confidence_brush = max(label_confidence_map, key=label_confidence_map.get)
        log_info(maxmium_confidence_brush)
        color = colors["cb"]
        conf = label_confidence_map[maxmium_confidence_brush]
        x1, y1, x2, y2 =  label_value_map[maxmium_confidence_brush]
        width = x2 - x1
        height = y2 - y1
        # Convert dimensions from pixels to real-world units
        real_width = width * conversion_factor
        real_height = height * conversion_factor
        cb_dimensions = (real_width, real_height)
        log_info("Cb Dimention wXh: "+ str(cb_dimensions))
        obj_center_x, obj_center_y = x1+((x2-x1)//2), y1+((y2-y1)//2)
        cv2.circle(frame, (obj_center_x, obj_center_y), 5, (0, 0, 255), -1)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        label = f"BrushID: {maxmium_confidence_brush} - CountID: {brush_count_id} - Conf: {conf:.2f}"
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        log_info("cp identified 2: "+str(cb_identified)+" Class Name: "+str(maxmium_confidence_brush))
        if not cb_identified and (maxmium_confidence_brush == brush_id or maxmium_confidence_brush == "cb"):
            cb_identified = True
            log_info("cp identified 3")

    # log_info("Analys End")
    
    if cb_identified and defect_identified:
        log_info("##############################Both identified####################################")
    #print(cb_identified, defect_identified)
    return frame, cb_identified, defect_identified, cb_dimensions

def capture_cb(frame, brush_id):
    status = False
    # Perform detection
    results = common_knowledge_model(frame)
    detections = results[0]
    
    height, width, _ = frame.shape
    center_x, center_y = width // 2, height // 2
    captured_frame = None
    captured_position = None
    captured_frame = np.copy(frame)
    
    # Draw bounding boxes
    for box in detections.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        conf = box.conf[0].item()
        class_id = int(box.cls[0].item())
        class_name = common_knowledge_class_names[class_id]

        #if True:
        if conf > confidence and class_name == 'cb':  # Modify condition as needed
            # Object center
            obj_center_x, obj_center_y = x1+((x2-x1)//2), y1+((y2-y1)//2)
            # Check if object is near center
            if abs(center_x-square_value) < obj_center_x and (center_x+square_value) > obj_center_x and abs(center_y-square_value) < obj_center_y and abs(center_y+square_value) > obj_center_y:
                print(f"Object '{class_name}' centered! Capturing image.")
                captured_position = x1, y1, x2, y2
                # cv2.imshow("Captured Image", frame)
                # cv2.waitKey(0)  # Show captured image for 500ms
                status = True

            color = colors[class_name]
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            if class_name == 'cb': 
                label = f"Brush ID: {brush_id}: {conf:.2f}"
            else:
                label = f"{class_name}: {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    return frame, status, captured_frame, captured_position

def check_dimensions(frame, brush_id_name):
    cb_dimensions_good = True
    brush_id_name = brush_id_name+"_area"
    if brush_id_name in brush_dimensions_json:
        brush_dimensions = brush_dimensions_json[brush_id_name]
        # Capture frame from webcam
        image_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Get trackbar positions

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
                cv2.drawContours(frame, [box], 0, (0, 255, 0), 2)

                # Display width & height
                cv2.putText(frame, f"W: {width:.1f}px", (box[0][0], box[0][1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                cv2.putText(frame, f"H: {height:.1f}px", (box[1][0], box[1][1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                # Approximate contour with a polygon
                epsilon = 0.01 * cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True)

                # Draw polygon
                cv2.polylines(frame, [approx], True, (0, 0, 255), 2)

                # Measure point-to-point distances
                for j in range(len(approx)):
                    pt1 = tuple(approx[j][0])
                    pt2 = tuple(approx[(j + 1) % len(approx)][0])  # Next point (loop back)
                    distance = np.linalg.norm(np.array(pt1) - np.array(pt2))
                    midpoint = ((pt1[0] + pt2[0]) // 2, (pt1[1] + pt2[1]) // 2)

                    # Display distance
                    cv2.putText(frame, f"{distance:.1f}px", midpoint, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
                    
            # print("Mask Area: "+str(contours_area))
        if contours_area > contours_area_threshold:
            cb_dimensions_good = False
            if brush_dimensions - contours_area_tolarance <= contours_area <= brush_dimensions + contours_area_tolarance:
                cb_dimensions_good = True
        print("Expected Dimension: "+str(brush_dimensions))
        print("Contour Dimension: "+str(contours_area))
        log_info("Expected Dimension: "+str(brush_dimensions))
        log_info("Contour Dimension: "+str(contours_area))
        log_info("Tolarance: "+str(contours_area_tolarance)+" Diff: "+str(contours_area-brush_dimensions))

    return frame, cb_dimensions_good


