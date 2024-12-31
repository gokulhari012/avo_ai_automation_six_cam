import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Load the image
image_path = "assets/Button.jpg"  # Replace with your image path
image = cv2.imread(image_path)

# Check if image was loaded
if image is None:
    print("Failed to load the image. Please check the path.")
else:
    # Convert OpenCV image (BGR) to PIL format (RGB)
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Load custom font
    font_path = "assets/Loubag-Bold.ttf"  # Path to the custom font
    font_size = 70
    font = ImageFont.truetype(font_path, font_size)

    # Prepare to draw on the image
    draw = ImageDraw.Draw(image_pil)
    text = "Train Model"
    text_position = (70, 60)  # Position to start the text
    text_color = (255, 255, 255)  # Red color

    # Draw the text
    draw.text(text_position, text, font=font, fill=text_color)

    # Convert back to OpenCV format
    image_with_text = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

    # Display the image
    cv2.imwrite("assets/train.jpg", image_with_text)
    cv2.waitKey(0)
    cv2.destroyAllWindows()