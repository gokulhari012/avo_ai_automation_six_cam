import cv2
import numpy as np

# Load the image
frame = cv2.imread("snapshots/snapshot_1728449057.jpg")
framea = frame[:, 0:500]

# Convert the image to HSV
hsv_image = cv2.cvtColor(framea, cv2.COLOR_BGR2HSV)

# Initial HSV threshold values for each window
hsv_values = [
    {'hue_min': 0, 'hue_max': 180, 'sat_min': 0, 'sat_max': 255, 'val_min': 0, 'val_max': 255},
    {'hue_min': 0, 'hue_max': 180, 'sat_min': 0, 'sat_max': 255, 'val_min': 0, 'val_max': 255},
    {'hue_min': 0, 'hue_max': 180, 'sat_min': 0, 'sat_max': 255, 'val_min': 0, 'val_max': 255},
    {'hue_min': 0, 'hue_max': 180, 'sat_min': 0, 'sat_max': 255, 'val_min': 0, 'val_max': 255}
]

# Create windows for four simultaneous displays
window_names = ['Live Feed', 'Head', 'Tail', 'Brush']
for i in range(4):
    cv2.namedWindow(window_names[i])

# Function to do nothing (placeholder for trackbar callbacks)
def nothing(x):
    pass

# Create trackbars for each window
for i in range(4):
    cv2.createTrackbar('Hue Min', window_names[i], hsv_values[i]['hue_min'], 179, nothing)
    cv2.createTrackbar('Hue Max', window_names[i], hsv_values[i]['hue_max'], 179, nothing)
    cv2.createTrackbar('Sat Min', window_names[i], hsv_values[i]['sat_min'], 255, nothing)
    cv2.createTrackbar('Sat Max', window_names[i], hsv_values[i]['sat_max'], 255, nothing)
    cv2.createTrackbar('Val Min', window_names[i], hsv_values[i]['val_min'], 255, nothing)
    cv2.createTrackbar('Val Max', window_names[i], hsv_values[i]['val_max'], 255, nothing)

# Function to apply HSV threshold and return the masked image and frame with bounding boxes for each window
def apply_threshold(hsv, frame_copy):
    lower_hsv = np.array([hsv['hue_min'], hsv['sat_min'], hsv['val_min']])
    upper_hsv = np.array([hsv['hue_max'], hsv['sat_max'], hsv['val_max']])

    # Apply threshold to isolate colors in the range
    mask = cv2.inRange(hsv_image, lower_hsv, upper_hsv)

    # Apply the mask to the image
    result = cv2.bitwise_and(framea, framea, mask=mask)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw contours and bounding boxes with the area on the frame copy
    for cnt in contours:
        area = cv2.contourArea(cnt)
        x, y, w, h = cv2.boundingRect(cnt)
        if area > 5000:  # Filter based on the area threshold
            cv2.rectangle(frame_copy, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(frame_copy, f"Area: {int(area)}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

    return frame_copy

# Main loop
while True:
    # Create a copy of the original framea for each window
    frames = [framea.copy() for _ in range(4)]
    
    # Loop through each window
    for i in range(4):
        # Get current positions of all trackbars
        hsv_values[i]['hue_min'] = cv2.getTrackbarPos('Hue Min', window_names[i])
        hsv_values[i]['hue_max'] = cv2.getTrackbarPos('Hue Max', window_names[i])
        hsv_values[i]['sat_min'] = cv2.getTrackbarPos('Sat Min', window_names[i])
        hsv_values[i]['sat_max'] = cv2.getTrackbarPos('Sat Max', window_names[i])
        hsv_values[i]['val_min'] = cv2.getTrackbarPos('Val Min', window_names[i])
        hsv_values[i]['val_max'] = cv2.getTrackbarPos('Val Max', window_names[i])

        # Apply the thresholding and get the frame with bounding boxes and area text
        threshold_image = apply_threshold(hsv_values[i], frames[i])

        # Show the result in the respective window
        cv2.imshow(window_names[i], threshold_image)

    # Exit the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources and close all windows
cv2.destroyAllWindows()