import cv2
import numpy as np
import pygame

# Load the image
frame = cv2.imread("snapshots/snapshot_1728449057.jpg")
framea = frame[:,0:500]
frame2 = cv2.bitwise_not(framea)

gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

# Initialize Pygame
pygame.init()

# Set up display
window_width, window_height = gray.shape[1], gray.shape[0]
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Threshold Adjuster")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Button dimensions
button_width, button_height = 50, 30

# Initial threshold values
threshold_min = 95
threshold_max = 255

# Function to draw buttons
def draw_buttons():
    pygame.draw.rect(window, RED, (10, 10, button_width, button_height))  # Decrease min threshold
    pygame.draw.rect(window, GREEN, (70, 10, button_width, button_height))  # Increase min threshold
    pygame.draw.rect(window, RED, (150, 10, button_width, button_height))  # Decrease max threshold
    pygame.draw.rect(window, GREEN, (210, 10, button_width, button_height))  # Increase max threshold

    # Button labels
    font = pygame.font.SysFont(None, 24)
    window.blit(font.render('-', True, BLACK), (30, 15))
    window.blit(font.render('+', True, BLACK), (90, 15))
    window.blit(font.render('-', True, BLACK), (170, 15))
    window.blit(font.render('+', True, BLACK), (230, 15))

# Function to apply threshold and convert image to Pygame surface
def apply_threshold():
    _, threshold = cv2.threshold(gray, threshold_min, threshold_max, cv2.THRESH_BINARY)
    threshold_rgb = cv2.cvtColor(threshold, cv2.COLOR_GRAY2RGB)

    # Find contours
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw contours and area
    for cnt in contours:
        # Draw the contour on the original frame
        cv2.drawContours(threshold_rgb, [cnt], -1, (0, 255, 0), 2)
        # Calculate and put the area text
        area = cv2.contourArea(cnt)
        x, y, w, h = cv2.boundingRect(cnt)
        if area > 5000:
            cv2.putText(threshold_rgb, f"Area: {int(area)}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        # Draw bounding box
            cv2.rectangle(threshold_rgb, (x, y), (x + w, y + h), (255, 0, 0), 2)

    surface = pygame.surfarray.make_surface(threshold_rgb.transpose((1, 0, 2)))
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

            # Decrease min threshold button
            if 10 <= mouse_x <= 10 + button_width and 10 <= mouse_y <= 10 + button_height:
                threshold_min = max(0, threshold_min - 5)
                print(f"Updated threshold_min: {threshold_min}")

            # Increase min threshold button
            elif 70 <= mouse_x <= 70 + button_width and 10 <= mouse_y <= 10 + button_height:
                threshold_min = min(255, threshold_min + 5)
                print(f"Updated threshold_min: {threshold_min}")

            # Decrease max threshold button
            elif 150 <= mouse_x <= 150 + button_width and 10 <= mouse_y <= 10 + button_height:
                threshold_max = max(0, threshold_max - 5)
                print(f"Updated threshold_max: {threshold_max}")

            # Increase max threshold button
            elif 210 <= mouse_x <= 210 + button_width and 10 <= mouse_y <= 10 + button_height:
                threshold_max = min(255, threshold_max + 5)
                print(f"Updated threshold_max: {threshold_max}")

    # Update the display
    window.fill(WHITE)
    draw_buttons()
    threshold_surface = apply_threshold()
    window.blit(threshold_surface, (0, 50))
    pygame.display.flip()

# Quit Pygame
pygame.quit()
