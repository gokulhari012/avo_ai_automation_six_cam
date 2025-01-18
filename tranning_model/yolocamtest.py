import cv2
from ultralytics import YOLO

# Load the YOLOv8 model
model_path = "runs/detect/train3/weights/best.pt"
# model_path = "runs/detect/train3/weights/last.pt"
model = YOLO(model_path)

# Open the webcam (0 for default camera, change if using external camera)
cap = cv2.VideoCapture(4, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Define colors for bounding boxes
def generate_colors(num_classes):
    import random
    random.seed(42)
    return [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(num_classes)]

# Get class names and colors
class_names = model.names
colors = generate_colors(len(class_names))

# Check if the camera is opened
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    # Read frame from the webcam
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

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
            color = colors[class_id]
            if class_name == "defect":
                color = (0,0,255)
            else:
                color = (0,255,0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            label = f"{class_name}: {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Display the frame
    cv2.imshow('Defect Detection', frame)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
