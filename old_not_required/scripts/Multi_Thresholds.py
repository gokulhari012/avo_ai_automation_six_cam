import cv2
import numpy as np
import pygame

# Load the image
frame = cv2.imread("snapshots/snapshot_1728449057.jpg")
framea = frame[:,0:500]

# Convert the image to HSV
hsv_image = cv2.cvtColor(framea, cv2.COLOR_BGR2HSV)

# Initialize Pygame
pygame.init()

# Set up display
window_width, window_height = framea.shape[1], framea.shape[0]
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("HSV Threshold Adjuster")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Button dimensions
button_width, button_height = 50, 30

# Initial HSV threshold values
hue_min = 0
hue_max = 180
sat_min = 0
sat_max = 255
val_min = 0
val_max = 255

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

    # Button labels
    font = pygame.font.SysFont(None, 24)
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
    for cnt in contours:
        # Draw the contour on the result
        cv2.drawContours(result, [cnt], -1, (0, 255, 0), 2)
        # Calculate and put the area text
        area = cv2.contourArea(cnt)
        x, y, w, h = cv2.boundingRect(cnt)
        if area > 5000:
            cv2.putText(result, f"Area: {int(area)}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        # Draw bounding box
            cv2.rectangle(result, (x, y), (x + w, y + h), (255, 0, 0), 2)

    surface = pygame.surfarray.make_surface(result.transpose((1, 0, 2)))
    return surface

# Main loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            # Decrease min hue button
            if 10 <= mouse_x <= 10 + button_width and 10 <= mouse_y <= 10 + button_height:
                hue_min = max(0, hue_min - 5)
                print(f"Updated hue_min: {hue_min}")

            # Increase min hue button
            elif 70 <= mouse_x <= 70 + button_width and 10 <= mouse_y <= 10 + button_height:
                hue_min = min(180, hue_min + 5)
                print(f"Updated hue_min: {hue_min}")

            # Decrease max hue button
            elif 150 <= mouse_x <= 150 + button_width and 10 <= mouse_y <= 10 + button_height:
                hue_max = max(0, hue_max - 5)
                print(f"Updated hue_max: {hue_max}")

            # Increase max hue button
            elif 210 <= mouse_x <= 210 + button_width and 10 <= mouse_y <= 10 + button_height:
                hue_max = min(180, hue_max + 5)
                print(f"Updated hue_max: {hue_max}")

            # Decrease min saturation button
            elif 10 <= mouse_x <= 10 + button_width and 50 <= mouse_y <= 50 + button_height:
                sat_min = max(0, sat_min - 5)
                print(f"Updated sat_min: {sat_min}")

            # Increase min saturation button
            elif 70 <= mouse_x <= 70 + button_width and 50 <= mouse_y <= 50 + button_height:
                sat_min = min(255, sat_min + 5)
                print(f"Updated sat_min: {sat_min}")

            # Decrease max saturation button
            elif 150 <= mouse_x <= 150 + button_width and 50 <= mouse_y <= 50 + button_height:
                sat_max = max(0, sat_max - 5)
                print(f"Updated sat_max: {sat_max}")

            # Increase max saturation button
            elif 210 <= mouse_x <= 210 + button_width and 50 <= mouse_y <= 50 + button_height:
                sat_max = min(255, sat_max + 5)
                print(f"Updated sat_max: {sat_max}")

            # Decrease min value button
            elif 10 <= mouse_x <= 10 + button_width and 90 <= mouse_y <= 90 + button_height:
                val_min = max(0, val_min - 5)
                print(f"Updated val_min: {val_min}")

            # Increase min value button
            elif 70 <= mouse_x <= 70 + button_width and 90 <= mouse_y <= 90 + button_height:
                val_min = min(255, val_min + 5)
                print(f"Updated val_min: {val_min}")

            # Decrease max value button
            elif 150 <= mouse_x <= 150 + button_width and 90 <= mouse_y <= 90 + button_height:
                val_max = max(0, val_max - 5)
                print(f"Updated val_max: {val_max}")

            # Increase max value button
            elif 210 <= mouse_x <= 210 + button_width and 90 <= mouse_y <= 90 + button_height:
                val_max = min(255, val_max + 5)
                print(f"Updated val_max: {val_max}")

    # Update the display
    window.fill(WHITE)
    draw_buttons()
    threshold_surface = apply_threshold()
    window.blit(threshold_surface, (0, 130))  # Adjusted height for buttons
    pygame.display.flip()

# Quit Pygame
pygame.quit()