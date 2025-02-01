import cv2
import os
import uuid
from ultralytics import YOLO

def detect_and_save(image_path, model_path='D:/YoloSegment/runs/detect/train/weights/best.pt', output_dir='D:/YoloSegment/dataset'):
    # Load YOLO model
    model = YOLO(model_path)
    
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Unable to load image.")
        return
    
    # Run YOLO detection
    results = model(image)
    
    # Create output folder
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate unique filename
    filename = f"{uuid.uuid4().hex}.jpg"
    image_save_path = os.path.join(output_dir, filename)
    cv2.imwrite(image_save_path, image)
    
    # Save annotations
    annotation_path = image_save_path.replace(".jpg", ".txt")
    with open(annotation_path, "w") as f:
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()  # Get bounding boxes
            labels = result.boxes.cls.cpu().numpy()  # Get labels
            
            for box, label in zip(boxes, labels):
                x1, y1, x2, y2 = map(int, box)
                label_name = model.names[int(label)]
                
                # Save annotation in YOLO format: class x_center y_center width height (normalized)
                x_center = (x1 + x2) / (2 * image.shape[1])
                y_center = (y1 + y2) / (2 * image.shape[0])
                width = (x2 - x1) / image.shape[1]
                height = (y2 - y1) / image.shape[0]
                f.write(f"{int(label)} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
    
    print(f"Saved image: {image_save_path}")
    print(f"Saved annotation: {annotation_path}")

if __name__ == "__main__":
    image_path = "D:/yolodataset v2/brush final/cb_train (20).jpg"  # Change this to your image path
    detect_and_save(image_path)
