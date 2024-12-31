import pygame
import cv2
import os
import time
import shutil

# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 600  # Increased width for better layout with three buttons
button_height = 100  # Space allocated for buttons
video_height = height - button_height
window = pygame.display.set_mode((width, height))
pygame.display.set_caption('Live Feed with Create Dataset/Snap/Merge')

# Initialize camera
camera_index = 0  # Default camera index; change if necessary
camera = cv2.VideoCapture(camera_index)
if not camera.isOpened():
    print(f"Error: Could not open camera with index {camera_index}.")
    exit()

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
GREEN = (34, 139, 34)
BLUE = (30, 144, 255)
GRAY = (50, 50, 50)

# Set fonts
font = pygame.font.SysFont(None, 40)

# Dataset states
record_folder = None

# Function to get the next dataset folder name
def get_next_dataset_folder():
    dataset_count = 1
    while os.path.exists(f"dataset_{dataset_count}"):
        dataset_count += 1
    return f"dataset_{dataset_count}"

# Create buttons
button_width = 150
button_height_actual = 60
padding = 20

# Positions for three buttons: Create Dataset, Snap, Merge
create_dataset_button = pygame.Rect(padding, video_height + (button_height - button_height_actual) // 2, button_width, button_height_actual)
snap_button = pygame.Rect((width - button_width) // 2, video_height + (button_height - button_height_actual) // 2, button_width, button_height_actual)
merge_button = pygame.Rect(width - button_width - padding, video_height + (button_height - button_height_actual) // 2, button_width, button_height_actual)

# Save a snapshot
def save_snapshot(frame):
    global record_folder
    if record_folder:
        filename = os.path.join(record_folder, f'snapshot_{int(time.time())}.jpg')
        cv2.imwrite(filename, frame)
        print(f'Snapshot saved: {filename}')
    else:
        print("No dataset folder exists. Please create a dataset first.")

# Create a new dataset folder
def create_dataset():
    global record_folder
    record_folder = get_next_dataset_folder()
    os.makedirs(record_folder, exist_ok=True)
    print(f"Created dataset folder: {record_folder}")

# Merge all datasets and snapshots into common_dataset
def merge_datasets():
    common_folder = 'common_dataset'
    os.makedirs(common_folder, exist_ok=True)
    # Merge datasets
    dataset_folders = [folder for folder in os.listdir('.') if os.path.isdir(folder) and folder.startswith('dataset_')]
    for folder in dataset_folders:
        for file in os.listdir(folder):
            src = os.path.join(folder, file)
            dst = os.path.join(common_folder, f'{folder}_{file}')
            shutil.copy2(src, dst)
    print(f"All datasets and snapshots have been merged into '{common_folder}'.")

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    ret, frame = camera.read()
    if not ret:
        print("Failed to grab frame.")
        break

    # Resize frame to fit the video area
    frame = cv2.resize(frame, (width, video_height))

    # Convert frame to RGB and then to Pygame surface
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_rgb = pygame.surfarray.make_surface(frame_rgb)
    frame_rgb = pygame.transform.rotate(frame_rgb, -90)  # Adjust rotation if needed

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if create_dataset_button.collidepoint(event.pos):
                create_dataset()
            if snap_button.collidepoint(event.pos):
                # Convert Pygame surface back to OpenCV format
                snapshot = pygame.surfarray.array3d(frame_rgb)
                snapshot = cv2.transpose(snapshot)
                snapshot = cv2.cvtColor(snapshot, cv2.COLOR_RGB2BGR)
                save_snapshot(snapshot)
            if merge_button.collidepoint(event.pos):
                merge_datasets()

    # Blit the video frame first
    window.blit(frame_rgb, (0, 0))

    # Draw a separator line between video and buttons
    pygame.draw.line(window, GRAY, (0, video_height), (width, video_height), 2)

    # Draw buttons on top of the video frame
    pygame.draw.rect(window, GREEN, create_dataset_button)
    pygame.draw.rect(window, BLUE, snap_button)
    pygame.draw.rect(window, (128, 0, 128), merge_button)  # Purple color for Merge button

    # Draw button text
    create_text = font.render('Create Dataset', True, WHITE)
    snap_text = font.render('Snap', True, WHITE)
    merge_text = font.render('Merge', True, WHITE)

    # Center the text on the buttons
    create_text_rect = create_text.get_rect(center=create_dataset_button.center)
    snap_text_rect = snap_text.get_rect(center=snap_button.center)
    merge_text_rect = merge_text.get_rect(center=merge_button.center)

    window.blit(create_text, create_text_rect)
    window.blit(snap_text, snap_text_rect)
    window.blit(merge_text, merge_text_rect)

    # Update display
    pygame.display.update()

    # Cap the frame rate
    clock.tick(30)

# Release camera and quit Pygame
camera.release()
pygame.quit()