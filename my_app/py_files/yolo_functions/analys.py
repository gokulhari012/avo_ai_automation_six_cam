import cv2
from ultralytics import YOLO

# Load the YOLOv8 model
model_path = "train3/weights/best.pt"
# model_path = "runs/detect/train3/weights/last.pt"
model = YOLO(model_path)

# Get class names and colors
class_names = model.names
colors = {"cb":(0,255,0),"defect":(0,0,255)}

def check_frame(frame):
    cb_identified = False 
    defect_identified = False 
    # Perform detection
    results = model(frame)
    detections = results[0]

    # Draw bounding boxes
    for box in detections.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        conf = box.conf[0].item()
        class_id = int(box.cls[0].item())
        class_name = class_names[class_id]
        #if True:
        if class_name == 'defect' or class_name == 'cb':  # Modify condition as needed
            color = colors[class_name]
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            label = f"{class_name}: {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        if not cb_identified and class_name == "cb":
            cb_identified = True
        if not defect_identified and class_name == "defect":
            defect_identified = True

    
    return frame, cb_identified, defect_identified

