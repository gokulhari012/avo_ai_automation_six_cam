import cv2
import numpy as np

# Load image
# image_path = "C:/Users/Karthick-PC/Documents/brushID_12[1]/brushID_12/0/datasets_0_accept_1739623712138.jpg"
image_path = r"C:\AI-Software\avo_automation_yolo\my_app\datasets\brushID_12\0/datasets_0_accept_1739623712138.jpg"

image = cv2.imread(image_path)
image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Default HSV values for mask
lower1 = np.array([0, 0, 0])  # Adjust if needed
upper1 = np.array([179, 66, 153])
lower2 = np.array([0, 0, 0])
upper2 = np.array([83, 255, 255])

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

for cnt in contours:
    if cv2.contourArea(cnt) > 500:  # Ignore small objects
        # Get minimum area rectangle
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)
        box = np.intp(box)

        # Calculate width & height
        width = np.linalg.norm(box[0] - box[1])
        height = np.linalg.norm(box[1] - box[2])

        # Draw bounding box
        cv2.drawContours(image, [box], 0, (0, 255, 0), 2)

        # Display width & height
        cv2.putText(image, f"W: {width:.1f}px", (box[0][0], box[0][1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(image, f"H: {height:.1f}px", (box[1][0], box[1][1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Approximate contour with a polygon
        epsilon = 0.01 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        # Draw polygon
        cv2.polylines(image, [approx], True, (0, 0, 255), 2)

        # Measure point-to-point distances
        for j in range(len(approx)):
            pt1 = tuple(approx[j][0])
            pt2 = tuple(approx[(j + 1) % len(approx)][0])  # Next point (loop back)
            distance = np.linalg.norm(np.array(pt1) - np.array(pt2))
            midpoint = ((pt1[0] + pt2[0]) // 2, (pt1[1] + pt2[1]) // 2)

            # Display distance
            cv2.putText(image, f"{distance:.1f}px", midpoint, 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
        print("Mask Area: "+str(cv2.contourArea(cnt)))
# Show results
cv2.imshow("Original", image)
cv2.imshow("Mask", combined_mask)
cv2.imshow("Smoothed Mask", smoothed_mask)

cv2.waitKey(0)
cv2.destroyAllWindows()
