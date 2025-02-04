import cv2
from ultralytics import YOLO
import logging
import numpy as np

logging.getLogger("ultralytics").setLevel(logging.ERROR) 
confidence = 0.40

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

def check_frame(frame, brush_count_id, brush_id):
    cb_identified = False 
    defect_identified = False 
    
    # Perform detection
    results = brush_knowledge_model(frame)
    detections = results[0]

    # Draw bounding boxes
    for box in detections.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        conf = box.conf[0].item()
        class_id = int(box.cls[0].item())
        class_name = brush_knowledge_class_names[class_id]
        #if True:
        if conf > confidence and (class_name == 'defect' or class_name == 'cb'):  # Modify condition as needed
            color = colors[class_name]
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            if class_name == brush_id: 
                label = f"Brush ID: {brush_count_id}: {conf:.2f}"
            else:
                label = f"{class_name}: {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        if not cb_identified and class_name == "cb":
            cb_identified = True
        if not defect_identified and class_name == "defect":
            defect_identified = True

    
    return frame, cb_identified, defect_identified

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
            obj_center_x, obj_center_y = x2 // 2, y2 // 2
            # Check if object is near center
            square_value = 50
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

