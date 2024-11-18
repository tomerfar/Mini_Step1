import tkinter as tk
from PIL import Image, ImageTk

# Create the main window
m = tk.Tk()
m.title("Board Game")

# Load and resize the image
image_path = "./pic/board.PNG"
original_image = Image.open(image_path)
resized_image = original_image.resize((1280, 720), Image.Resampling.LANCZOS)
board_image = ImageTk.PhotoImage(resized_image)

# Create a label to display the image
image_label = tk.Label(m, image=board_image)
image_label.pack()

# Start the main loop
m.mainloop()