import cv2
import numpy as np
import pygame
import serial
import time

# Set up serial communication with Arduino
ser = serial.Serial('COM7', 9600)  # Replace 'COM7' with your actual port
time.sleep(0.5)  # Reduced delay for Arduino initialization

# Set servo to home position initially
ser.write(b'H')
print("Servo set to home position.")

# Open webcam feed (default webcam index 1)
cap = cv2.VideoCapture(1)

# Initialize Pygame
pygame.init()

# Set up display
window_width, window_height = 640, 480  # Assuming a standard webcam resolution
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
threshold_min = 160
threshold_max = 255

# Variables to manage servo timing and state tracking
servo_status = "home"  # Track current status: "home", "accepted", or "rejected"
last_state = "home"  # Last confirmed state sent to Arduino
buffer_state = "home"  # Temporary state buffer for consecutive detection
last_detection_time = time.time()  # Time of last brush detection
state_confirmed = False  # Confirm stability of the state

# Minimum time between brushes for reset (2-3 seconds)
reset_time = 2.5

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

# Function to relay final decision to Arduino and update servo
def relay_servo_command(status):
    global servo_status
    if status != servo_status:  # Only send command if the status changes
        if status == "Accepted":
            ser.write(b'A')  # Send "accepted" command
            print("Sent command: Accepted")
        elif status == "Rejected":
            ser.write(b'R')  # Send "rejected" command to stay at home
            print("Sent command: Rejected")
        servo_status = status  # Update the servo status

# Function to apply threshold and convert image to Pygame surface
def apply_threshold(gray):
    global last_state, buffer_state, last_detection_time, state_confirmed
    _, threshold = cv2.threshold(gray, threshold_min, threshold_max, cv2.THRESH_BINARY)
    threshold_rgb = cv2.cvtColor(threshold, cv2.COLOR_GRAY2RGB)

    # Find contours
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    brush_detected = False  # Flag to track if a brush is detected
    current_state = "home"  # Default to home position

    # Draw contours and determine brush state
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 14000:  # Filter by area threshold
            brush_detected = True
            x, y, w, h = cv2.boundingRect(cnt)
            status = "Accepted" if area > 7500 else "Rejected"
            current_state = status  # Set the detected state
            color = (0, 255, 0) if status == "Accepted" else (0, 0, 255)
            cv2.drawContours(threshold_rgb, [cnt], -1, (0, 255, 0), 2)
            cv2.putText(threshold_rgb, f"Area: {int(area)}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            cv2.rectangle(threshold_rgb, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(threshold_rgb, status, (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            break

    # Handle buffering and updating states
    if brush_detected:
        # Only update buffer_state if it changes from current_state
        if current_state != buffer_state:
            buffer_state = current_state
            state_confirmed = False  # Reset confirmation until detected again

        # Confirm state if current and buffer states match, then relay
        elif current_state == buffer_state and not state_confirmed:
            last_state = buffer_state
            last_detection_time = time.time()  # Update detection time
            relay_servo_command(last_state)  # Relay stable state
            state_confirmed = True  # Mark state as confirmed
    else:
        # If no brush is detected and reset time has passed, reset to "home"
        if time.time() - last_detection_time > reset_time:
            last_state = "home"
            buffer_state = "home"
            state_confirmed = False
            relay_servo_command("home")
            print("No brush detected. Servo staying at home position.")

    surface = pygame.surfarray.make_surface(threshold_rgb.transpose((1, 0, 2)))
    return surface

# Main loop
running = True
while running:
    # Capture frame from webcam
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image from webcam.")
        break

    # Convert the image to grayscale
    framea = frame[:, 300:700]
    frame2 = cv2.bitwise_not(framea)
    gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

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
    threshold_surface = apply_threshold(gray)
    window.blit(threshold_surface, (0, 50))
    pygame.display.flip()

# Release resources and quit
cap.release()
pygame.quit()
ser.close()