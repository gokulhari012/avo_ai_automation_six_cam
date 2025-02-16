from ultralytics import YOLO, SAM
import cv2
import numpy as np

# Load YOLO and SAM models
yolo_model = YOLO("runs/detect/train/weights/best.pt") 
sam_model = SAM("D:/yolodataset v2/sam/sam2_t.pt")    

def setup_camera():
    """Initialize camera and check if it is opened properly."""
    cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    #cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        exit()
    return cap

def setup_trackbars():
    """Create trackbars for dynamic edge detection parameter tuning."""
    cv2.namedWindow('Edges')
    cv2.createTrackbar('Threshold 1', 'Edges', 50, 255, lambda x: None)
    cv2.createTrackbar('Threshold 2', 'Edges', 100, 200, lambda x: None)

def compute_pca_orientation(contour):
    """Compute PCA to determine the orientation angle of the detected object."""
    data_pts = np.array(contour, dtype=np.float32).reshape(-1, 2)
    mean, eigenvectors = cv2.PCACompute(data_pts, mean=None)
    angle = np.arctan2(eigenvectors[0, 1], eigenvectors[0, 0]) * (180 / np.pi)
    return angle

def get_oriented_crop(image, contour):
    """Extract and crop the oriented bounding box from the image and ensure it's vertically aligned."""
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)
    box = np.intp(box)

    width = int(rect[1][0])
    height = int(rect[1][1])

    # Ensure the biggest dimension is always the height (oriented vertically)
    

    src_pts = box.astype("float32")
    dst_pts = np.array([[0, height-1],
                        [0, 0],
                        [width-1, 0],
                        [width-1, height-1]], dtype="float32")

    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    cropped = cv2.warpPerspective(image, M, (width, height))
    if width > height:
        cropped= cv2.rotate(cropped, cv2.ROTATE_90_CLOCKWISE)

    return cropped, box, width, height

def detect_objects(image):
    """Run YOLO object detection on the input image."""
    yolo_results = yolo_model(image)
    if yolo_results and len(yolo_results[0].boxes) > 0:
        return yolo_results[0].boxes.xyxy.cpu().numpy()
    return None

def segment_objects(image, boxes):
    """Run SAM segmentation on detected objects using bounding boxes."""
    sam_results = sam_model(image, bboxes=boxes, verbose=False, save=True, device=0)
    if hasattr(sam_results[0], "masks") and sam_results[0].masks is not None:
        return sam_results[0].masks.data.cpu().numpy()
    return None

def process_mask(mask, frame_shape):
    """Smooth and preprocess the segmentation mask for better edge detection."""
    mask = (mask * 255).astype(np.uint8)
    mask_resized = cv2.resize(mask, (frame_shape[1], frame_shape[0]))
    smooth_img = cv2.bilateralFilter(mask_resized, 5, 50, 50)
    blurred = cv2.GaussianBlur(smooth_img, (11, 11), 1.5)
    return blurred

def detect_and_measure_edges(mask, frame):
    """Detect object edges, compute distances, and determine orientation."""
    thresh1 = cv2.getTrackbarPos('Threshold 1', 'Edges')
    thresh2 = cv2.getTrackbarPos('Threshold 2', 'Edges')
    thresh2 = max(thresh2, 10)  # Ensure a minimum threshold value

    _, thresh = cv2.threshold(mask, thresh1, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    line_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
    dimensions = []

    for contour in contours:
        if cv2.contourArea(contour) > 100:  # Ignore small noise
            cropped, box, width, height = get_oriented_crop(frame, contour)
            dimensions.append(f"Width: {width}px, Height: {height}px")

            for i in range(len(box)):
                pt1 = tuple(box[i])
                pt2 = tuple(box[(i+1) % len(box)])
                cv2.line(frame, pt1, pt2, line_colors[i % len(line_colors)], 3)

            for i, point in enumerate(box):
                cv2.circle(frame, tuple(point), 5, (0, 0, 0), -1)

            epsilon = (1/thresh2) * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            points = [tuple(point[0]) for point in approx]

            for i in range(len(points)):
                p1, p2 = points[i], points[(i + 1) % len(points)]
                distance = cv2.norm(np.array(p1) - np.array(p2))
                cv2.line(frame, p1, p2, (0, 255, 0), 2)
                cv2.putText(frame, f"{distance:.2f}px", ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

            angle = compute_pca_orientation(contour)
            center = np.mean(box, axis=0).astype(int)
            length = 100
            angle_rad = np.deg2rad(angle)
            x2 = int(center[0] + length * np.cos(angle_rad))
            y2 = int(center[1] + length * np.sin(angle_rad))
            cv2.line(frame, tuple(center), (x2, y2), (0, 0, 255), 2)
            cv2.putText(frame, f"Angle: {angle:.2f}°", (center[0] + 10, center[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

            y_offset = 20
            for i, dim in enumerate(dimensions):
                cv2.putText(frame, dim, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                y_offset += 20
            if width>height:
                width,height=height,width
            #cv2.resizeWindow("Oriented Cropped Object", width, height) 
            cv2.imshow("Oriented Cropped Object", cropped)

def main():
    """Main function to process the camera feed and perform object analysis."""
    cap = setup_camera()
    setup_trackbars()
    #cv2.namedWindow("Oriented Cropped Object", cv2.WINDOW_NORMAL) 
  
    # Using resizeWindow() 
     
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to grab frame.")
            break

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = detect_objects(image_rgb)

        if boxes is not None:
            masks = segment_objects(image_rgb, boxes)
            if masks is not None:
                for mask in masks:
                    processed_mask = process_mask(mask, frame.shape)
                    detect_and_measure_edges(processed_mask, frame)
                    cv2.imshow("Mask", processed_mask)

        cv2.imshow("Live Camera Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
