import pygame
import cv2
import os
import time
import shutil
import threading


# Set up display
width, height = 800, 600  # Increased width for better layout with three buttons
button_height = 100  # Space allocated for buttons
video_height = height - button_height


# Initialize camera
# camera_index = 0  # Default camera index; change if necessary
camera_index_list = [0,1,2,3,4,5]
thread_list=[]


# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
GREEN = (34, 139, 34)
BLUE = (30, 144, 255)
GRAY = (50, 50, 50)



# Dataset states
record_folder = None

# Function to get the next dataset folder name
def get_next_dataset_folder():
    dataset_count = 1
    while os.path.exists(f"datasets/dataset_{dataset_count}"):
        dataset_count += 1
    return f"datasets/dataset_{dataset_count}"

# Create buttons
button_width = 150
button_height_actual = 60
padding = 20

# Positions for three buttons: Create Dataset, Snap, Merge
create_dataset_button = pygame.Rect(padding, video_height + (button_height - button_height_actual) // 2, button_width, button_height_actual)
snap_button = pygame.Rect((width - button_width) // 2, video_height + (button_height - button_height_actual) // 2, button_width, button_height_actual)
merge_button = pygame.Rect(width - button_width - padding, video_height + (button_height - button_height_actual) // 2, button_width, button_height_actual)

# Save a snapshot
def save_snapshot(camera_id,frame):
    global record_folder
    camera_id = str(camera_id)
    if record_folder and os.path.isdir(record_folder+"/"+camera_id):
        filename = os.path.join(record_folder+"/"+camera_id, f'snapshot_{int(time.time())}.jpg')
        cv2.imwrite(filename, frame)
        print(f'Snapshot saved: {filename}')
    else:
        print("No dataset folder exists. Please create a dataset first.")

# Create a new dataset folder
def create_dataset(camera_id):
    global record_folder
    camera_id = str(camera_id)
    if record_folder==None:
        record_folder = get_next_dataset_folder()
        os.makedirs(record_folder, exist_ok=True)
        print(f"Created dataset folder: {record_folder}")
    try:     
        if not os.path.isdir(record_folder+"/"+camera_id):
            os.makedirs(record_folder+"/"+camera_id, exist_ok=True)
            print(f"Created camera id folder inside dataset folder: {record_folder+"/"+camera_id}") 
    except Exception as e:
        print("dfd : "+str(e))

# Merge all datasets and snapshots into common_dataset
def merge_datasets():
    common_folder = 'datasets/common_dataset'
    os.makedirs(common_folder, exist_ok=True)
    # Merge datasets
    dataset_folders = [folder for folder in os.listdir('./datasets') if os.path.isdir(folder) and folder.startswith('dataset_')]
    for folder in dataset_folders:
        for file in os.listdir(folder):
            src = os.path.join(folder, file)
            dst = os.path.join(common_folder, f'{folder}_{file}')
            shutil.copy2(src, dst)
    print(f"All datasets and snapshots have been merged into '{common_folder}'.")

def main_program(camera_id,camera):
    print("inside main loop: "+str(camera_id))
    # Initialize Pygame
    pygame.init()
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Dataset tranning - camera: '+str(camera_id))

    # Set fonts
    font = pygame.font.SysFont(None, 40)
    
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
                    create_dataset(camera_id)

                if snap_button.collidepoint(event.pos):
                    # Convert Pygame surface back to OpenCV format
                    snapshot = pygame.surfarray.array3d(frame_rgb)
                    snapshot = cv2.transpose(snapshot)
                    snapshot = cv2.cvtColor(snapshot, cv2.COLOR_RGB2BGR)
                    save_snapshot(camera_id,snapshot)
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

for camera_id in camera_index_list:
    try:  
        camera = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        if not camera.isOpened():
            print(f"Error: Could not open camera with index {camera_id}.")
            continue          
        t1 = threading.Thread(target=main_program, args=(camera_id,camera,))
        thread_list.append(t1)
        t1.start()
    except Exception as e:
        print("Exception at opening camera :"+ str(e))

for t1 in thread_list:
    t1.join()
