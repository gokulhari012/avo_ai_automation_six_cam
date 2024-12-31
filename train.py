import cv2
import numpy as np
import pygame
import os

folder_path = ""

with open("brush.txt", "r") as file:
    folder_path = file.read().strip()

# Folder containing images
# folder_path = "dataset_7"
image_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(('.png', '.jpg', '.jpeg'))]
image_index = 0  # Start with the first image

# Initialize Pygame
pygame.init()

# Load the current image and initialize variables
def load_image():
    global hsv_image, frame, framea
    frame = cv2.imread(image_files[image_index])
    framea = frame[:, 0:500]
    hsv_image = cv2.cvtColor(framea, cv2.COLOR_BGR2HSV)

load_image()  # Load the initial image

# Set up display
window_width, window_height = framea.shape[1], framea.shape[0] + 180
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("HSV Threshold Adjuster")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Button dimensions
button_width, button_height = 50, 30

# Initial HSV threshold values
hue_min, hue_max = 0, 180
sat_min, sat_max = 0, 255
val_min, val_max = 0, 255

# File to store the areas
output_file = os.path.join(folder_path, f"{os.path.basename(folder_path)}.txt")

# Function to draw buttons
def draw_buttons():
    pygame.draw.rect(window, RED, (10, 10, button_width, button_height))  # Decrease min hue
    pygame.draw.rect(window, GREEN, (70, 10, button_width, button_height))  # Increase min hue
    pygame.draw.rect(window, RED, (150, 10, button_width, button_height))  # Decrease max hue
    pygame.draw.rect(window, GREEN, (210, 10, button_width, button_height))  # Increase max hue

    pygame.draw.rect(window, RED, (10, 50, button_width, button_height))  # Decrease min saturation
    pygame.draw.rect(window, GREEN, (70, 50, button_width, button_height))  # Increase min saturation
    pygame.draw.rect(window, RED, (150, 50, button_width, button_height))  # Decrease max saturation
    pygame.draw.rect(window, GREEN, (210, 50, button_width, button_height))  # Increase max saturation

    pygame.draw.rect(window, RED, (10, 90, button_width, button_height))  # Decrease min value
    pygame.draw.rect(window, GREEN, (70, 90, button_width, button_height))  # Increase min value
    pygame.draw.rect(window, RED, (150, 90, button_width, button_height))  # Decrease max value
    pygame.draw.rect(window, GREEN, (210, 90, button_width, button_height))  # Increase max value

    # Capture area button
    pygame.draw.rect(window, BLUE, (300, 50, 150, 40))  # Capture area button
    # Next image button
    pygame.draw.rect(window, BLUE, (300, 100, 150, 40))  # Next image button

    font = pygame.font.SysFont(None, 24)
    window.blit(font.render('Capture Area', True, WHITE), (320, 60))
    window.blit(font.render('Next Image', True, WHITE), (320, 110))

    # Button labels for HSV controls
    window.blit(font.render('-', True, BLACK), (30, 15))
    window.blit(font.render('+', True, BLACK), (90, 15))
    window.blit(font.render('-', True, BLACK), (170, 15))
    window.blit(font.render('+', True, BLACK), (230, 15))

    window.blit(font.render('-', True, BLACK), (30, 55))
    window.blit(font.render('+', True, BLACK), (90, 55))
    window.blit(font.render('-', True, BLACK), (170, 55))
    window.blit(font.render('+', True, BLACK), (230, 55))

    window.blit(font.render('-', True, BLACK), (30, 95))
    window.blit(font.render('+', True, BLACK), (90, 95))
    window.blit(font.render('-', True, BLACK), (170, 95))
    window.blit(font.render('+', True, BLACK), (230, 95))

# Function to apply HSV threshold and convert the image to a Pygame surface
def apply_threshold():
    lower_hsv = np.array([hue_min, sat_min, val_min])
    upper_hsv = np.array([hue_max, sat_max, val_max])

    # Apply threshold to isolate colors in the range
    mask = cv2.inRange(hsv_image, lower_hsv, upper_hsv)

    # Apply the mask to the image
    result = cv2.bitwise_and(framea, framea, mask=mask)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw contours and area
    areas = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        x, y, w, h = cv2.boundingRect(cnt)
        if area > 5000:
            areas.append(area)
            cv2.putText(result, f"Area: {int(area)}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            cv2.rectangle(result, (x, y), (x + w, y + h), (255, 0, 0), 2)

    surface = pygame.surfarray.make_surface(result.transpose((1, 0, 2)))
    return surface, areas

# Save areas to a single text file
def save_areas(areas):
    with open(output_file, "a") as file:
        file.write(f"{areas}\n")
    print(f"Captured areas: {areas}")

# Function to go to the next image
def next_image():
    global image_index
    image_index = (image_index + 1) % len(image_files)  # Cycle through images
    load_image()  # Load the next image
    draw_buttons()  # Draw the buttons after loading the next image

# Main loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            # Adjust thresholds based on button clicked
            if 10 <= mouse_x <= 10 + button_width and 10 <= mouse_y <= 10 + button_height:
                hue_min = max(0, hue_min - 5)
            elif 70 <= mouse_x <= 70 + button_width and 10 <= mouse_y <= 10 + button_height:
                hue_min = min(180, hue_min + 5)
            elif 150 <= mouse_x <= 150 + button_width and 10 <= mouse_y <= 10 + button_height:
                hue_max = max(0, hue_max - 5)
            elif 210 <= mouse_x <= 210 + button_width and 10 <= mouse_y <= 10 + button_height:
                hue_max = min(180, hue_max + 5)
            elif 10 <= mouse_x <= 10 + button_width and 50 <= mouse_y <= 50 + button_height:
                sat_min = max(0, sat_min - 5)
            elif 70 <= mouse_x <= 70 + button_width and 50 <= mouse_y <= 50 + button_height:
                sat_min = min(255, sat_min + 5)
            elif 150 <= mouse_x <= 150 + button_width and 50 <= mouse_y <= 50 + button_height:
                sat_max = max(0, sat_max - 5)
            elif 210 <= mouse_x <= 210 + button_width and 50 <= mouse_y <= 50 + button_height:
                sat_max = min(255, sat_max + 5)
            elif 10 <= mouse_x <= 10 + button_width and 90 <= mouse_y <= 90 + button_height:
                val_min = max(0, val_min - 5)
            elif 70 <= mouse_x <= 70 + button_width and 90 <= mouse_y <= 90 + button_height:
                val_min = min(255, val_min + 5)
            elif 150 <= mouse_x <= 150 + button_width and 90 <= mouse_y <= 90 + button_height:
                val_max = max(0, val_max - 5)
            elif 210 <= mouse_x <= 210 + button_width and 90 <= mouse_y <= 90 + button_height:
                val_max = min(255, val_max + 5)

            # Capture area button
            elif 300 <= mouse_x <= 300 + 150 and 50 <= mouse_y <= 50 + 40:
                _, areas = apply_threshold()
                save_areas(areas)

            # Next image button
            elif 300 <= mouse_x <= 300 + 150 and 100 <= mouse_y <= 100 + 40:
                next_image()

    # Update the display
    window.fill(WHITE)
    draw_buttons()
    threshold_surface, _ = apply_threshold()
    window.blit(threshold_surface, (0, 130))  # Adjusted height for buttons
    pygame.display.flip()

# Quit Pygame
pygame.quit()
