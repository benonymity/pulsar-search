import os
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from PIL import Image
import numpy as np


# Function to load and convert images to numpy arrays
def load_image(filename):
    img = Image.open(filename)
    return np.array(img)


# Get all jpg files in the current directory
image_files = [f for f in os.listdir(".") if f.endswith(".jpg")]

if len(image_files) < 3:
    raise ValueError(
        "Not enough images in the directory. Please ensure there are at least 3 jpg files."
    )

# Load the first three images
images = [load_image(image_files[i]) for i in range(3)]

# Create the main plot
fig, ax = plt.subplots(figsize=(10, 8))
plt.subplots_adjust(bottom=0.25)

# Initialize with the first image
im = ax.imshow(images[0], cmap="viridis")

# Create sliders for each image
slider_axes = [plt.axes([0.2, 0.1 + i * 0.05, 0.6, 0.03]) for i in range(3)]
sliders = [
    Slider(ax, f"{image_files[i]}", -1.0, 1.0, valinit=0.0)
    for i, ax in enumerate(slider_axes)
]


# Update function for the sliders
def update(val):
    combined_image = np.zeros_like(images[0], dtype=float)
    for i, slider in enumerate(sliders):
        combined_image += slider.val * images[i]

    # Clip values to valid range
    combined_image = np.clip(combined_image, 0, 255).astype(np.uint8)

    im.set_array(combined_image)
    fig.canvas.draw_idle()


# Attach update function to sliders
for slider in sliders:
    slider.on_changed(update)

plt.show()
