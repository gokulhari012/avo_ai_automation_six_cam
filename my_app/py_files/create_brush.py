import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

brush_name_list_path = "json/brush_name_list.txt"

# Function to add a new brush name to the file
def add_brush_name():
    brush_name = brush_name_entry.get()
    if brush_name:
        with open(brush_name_list_path, "a") as file:
            file.write(brush_name + "\n")
        status_label.config(text=f"Brush '{brush_name}' added successfully!", fg="green")
        brush_name_entry.delete(0, tk.END)  # Clear the entry field after saving
        update_brush_list()
    else:
        status_label.config(text="Please enter a brush name.", fg="red")

# Function to delete the selected brush name from the file
def delete_brush_name():
    selected_brush = brush_listbox.get(tk.ACTIVE)
    if selected_brush:
        # Read all brush names into a list
        with open(brush_name_list_path, "r") as file:
            brush_names = file.readlines()
        
        # Remove the selected brush name from the list
        brush_names = [name for name in brush_names if name.strip() != selected_brush]
        
        # Rewrite the remaining names back to the file
        with open(brush_name_list_path, "w") as file:
            file.writelines(brush_names)
        
        status_label.config(text=f"Brush '{selected_brush}' deleted successfully!", fg="green")
        update_brush_list()
    else:
        messagebox.showwarning("Selection Error", "Please select a brush name to delete.")

# Function to update the listbox of brush names
def update_brush_list():
    # Clear the listbox
    brush_listbox.delete(0, tk.END)
    
    # Read all brush names from the file and add them to the listbox
    try:
        with open(brush_name_list_path, "r") as file:
            brush_names = file.readlines()
            for brush_name in brush_names:
                brush_listbox.insert(tk.END, brush_name.strip())
    except FileNotFoundError:
        pass  # If the file doesn't exist, we do nothing



def on_close(window_close):
    # Close the window
    window_close.destroy()

# Set up the main Tkinter window
root = tk.Tk()
root.title("Brush Name Management")
root.geometry("700x820")

# Set background image
bg_image = Image.open("assets/Technology Wallpaper.jpg")
bg_image = bg_image.resize((700, 820), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(root, image=bg_photo)
bg_label.image = bg_photo  # Keep a reference to avoid garbage collection
bg_label.place(relwidth=1, relheight=1)

# Create a label, entry field, and buttons for adding and deleting brush names
brush_name_label = tk.Label(root, text="Enter Brush Name", font=("Helvetica", 15, "bold"))
brush_name_label.pack(pady=10)

brush_name_entry = tk.Entry(root, width=30, font=("Helvetica", 15), bd=5, insertwidth=4, insertborderwidth=3)
brush_name_entry.pack(padx=20, pady=10)


# add_button = tk.Button(root, text="Add Brush Name", command=add_brush_name)
# add_button.pack(pady=5)
add_brush_image = Image.open("assets/add_brush.jpg")
add_brush_image = add_brush_image.resize((200, 75), Image.LANCZOS)
add_brush_photo = ImageTk.PhotoImage(add_brush_image)
add_brush_button = tk.Button(root, image=add_brush_photo, command=add_brush_name, borderwidth=0)
add_brush_button.image = add_brush_photo
add_brush_button.pack(pady=5)

# Listbox to display the brush names
brush_listbox = tk.Listbox(root, width=30, height=18, font=("Helvetica", 15), bd=5)
brush_listbox.pack(padx=20,pady=10)

delete_brush_image = Image.open("assets/delete_brush.jpg")
delete_brush_image = delete_brush_image.resize((200, 75), Image.LANCZOS)
delete_brush_photo = ImageTk.PhotoImage(delete_brush_image)
delete_brush_button = tk.Button(root, image=delete_brush_photo, command=delete_brush_name, borderwidth=0)
delete_brush_button.image = delete_brush_photo
delete_brush_button.pack(pady=5)

# Status label to show success or error messages
status_label = tk.Label(root, text="", fg="black", font=("Helvetica", 15, "bold"))
status_label.pack(pady=5)

# Initial update of the brush list
update_brush_list()

root.protocol("WM_DELETE_WINDOW", lambda: on_close(root))

# Run the Tkinter main loop
root.mainloop()

