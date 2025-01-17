import tkinter as tk
from PIL import Image, ImageTk, ImageFont, ImageDraw
import cv2
import os
import glob

def select_brush_window():
    
    # Create a new window for Select Brush
    window = tk.Tk()
    window.title("Select Brush")
    window.geometry("700x820")

    # Set background image
    bg_image = Image.open("assets/Technology Wallpaper.jpg")
    bg_image = bg_image.resize((700, 820), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(window, image=bg_photo)
    bg_label.image = bg_photo  # Keep a reference to avoid garbage collection
    bg_label.place(relwidth=1, relheight=1)

    # List all dataset folders and create buttons with custom font and image
    dataset_folders = [folder for folder in os.listdir('./datasets') if os.path.isdir(os.path.join('./datasets', folder)) and folder.startswith('dataset_')]
    font_path = "assets/Loubag-Bold.ttf"
    font_size = 70
    font = ImageFont.truetype(font_path, font_size)
    button_image_path = "assets/Button.jpg"

    # Calculate button placement dynamically
    button_width = 200
    button_height = 75
    max_buttons_per_column = (820 - 20) // (button_height + 20)
    num_columns = (len(dataset_folders) + max_buttons_per_column - 1) // max_buttons_per_column

    for idx, folder in enumerate(dataset_folders):
        # Load the button image using OpenCV
        image = cv2.imread(button_image_path)
        if image is None:
            print("Failed to load the image. Please check the path.")
            continue

        # Convert OpenCV image (BGR) to PIL format (RGB)
        image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        # Prepare to draw on the image
        draw = ImageDraw.Draw(image_pil)
        draw.text((70, 25), folder, font=font, fill="white")

        # Save the image with text
        image_with_text_path = f"assets/{folder}_button.jpg"
        image_pil.save(image_with_text_path)

        # Load the image with text for Tkinter
        button_img_pil = Image.open(image_with_text_path)
        button_img_pil = button_img_pil.resize((200, 75), Image.LANCZOS)
        button_photo = ImageTk.PhotoImage(button_img_pil)

        # Calculate button position
        column = idx // max_buttons_per_column
        row = idx % max_buttons_per_column
        x_position = 20 + column * (button_width + 20)
        y_position = 20 + row * (button_height + 20)

        # Create button
        button = tk.Button(window, image=button_photo, borderwidth=0, command=lambda folder=folder: save_brush_selection(folder, window))
        button.image = button_photo
        button.place(x=x_position, y=y_position)

    window.protocol("WM_DELETE_WINDOW", lambda: on_close(window))
    window.mainloop()

def save_brush_selection(folder, window):
    # Save the selected folder name to brush.txt
    with open("brush.txt", "w") as file:
        file.write(folder)
    print("DataSet "+str(folder)+" is selected")
    on_close(window)

def on_close(window):
    # Close the window
    window.destroy()
    # Delete all generated button images
    for file_path in glob.glob("assets/dataset_*_button.jpg"):
        os.remove(file_path)

select_brush_window()