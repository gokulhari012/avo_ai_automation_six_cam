import cv2
import numpy as np

def nothing(x):
    pass

# Load image
image_path = r"C:\AI-Software\avo_automation_yolo\my_app\datasets\brushID_12\0/datasets_0_accept_1739623712138.jpg"
image = cv2.imread(image_path)



image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Create a window
cv2.namedWindow("Trackbars")

# Create trackbars for first color range (Lower and Upper HSV)
cv2.createTrackbar("Low H1", "Trackbars", 0, 179, nothing)
cv2.createTrackbar("Low S1", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("Low V1", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("High H1", "Trackbars", 179, 179, nothing)
cv2.createTrackbar("High S1", "Trackbars", 66, 255, nothing)
cv2.createTrackbar("High V1", "Trackbars", 153, 255, nothing)

# Create trackbars for second color range
cv2.createTrackbar("Low H2", "Trackbars", 0, 179, nothing)
cv2.createTrackbar("Low S2", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("Low V2", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("High H2", "Trackbars", 83, 179, nothing)
cv2.createTrackbar("High S2", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("High V2", "Trackbars", 255, 255, nothing)

while True:
    # Get trackbar positions
    l_h1 = cv2.getTrackbarPos("Low H1", "Trackbars")
    l_s1 = cv2.getTrackbarPos("Low S1", "Trackbars")
    l_v1 = cv2.getTrackbarPos("Low V1", "Trackbars")
    h_h1 = cv2.getTrackbarPos("High H1", "Trackbars")
    h_s1 = cv2.getTrackbarPos("High S1", "Trackbars")
    h_v1 = cv2.getTrackbarPos("High V1", "Trackbars")

    l_h2 = cv2.getTrackbarPos("Low H2", "Trackbars")
    l_s2 = cv2.getTrackbarPos("Low S2", "Trackbars")
    l_v2 = cv2.getTrackbarPos("Low V2", "Trackbars")
    h_h2 = cv2.getTrackbarPos("High H2", "Trackbars")
    h_s2 = cv2.getTrackbarPos("High S2", "Trackbars")
    h_v2 = cv2.getTrackbarPos("High V2", "Trackbars")

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

    # Apply mask
    result = cv2.bitwise_and(image, image, mask=combined_mask)

    # Show results
    cv2.imshow("Original", image)
    cv2.imshow("Mask", combined_mask)
    cv2.imshow("Trackbars", result)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
