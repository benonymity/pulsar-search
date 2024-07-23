import os
import tkinter as tk
from tkinter import ttk, messagebox
from pulsars import fetch_pulsar_coordinates
from PIL import Image, ImageTk, ImageDraw, ImageStat, ImageEnhance
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from functools import partial

# import cv2


class PulsarSorter:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Pulsar Viewer")
        self.window.geometry("840x600")  # Increased width to accommodate new info
        self.window.resizable(False, False)

        self.pulsar_listbox = tk.Listbox(self.window, width=15)
        self.pulsar_listbox.pack(side=tk.LEFT, fill=tk.Y)

        self.image_frame = ttk.Frame(self.window)
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.info_frame = ttk.Frame(self.window)
        self.info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        self.name_label = ttk.Label(self.info_frame, text="", anchor="w")
        self.name_label.pack(side=tk.TOP, fill=tk.X)
        self.ra_label = ttk.Label(self.info_frame, text="", anchor="w")
        self.ra_label.pack(side=tk.TOP, fill=tk.X)
        self.dec_label = ttk.Label(self.info_frame, text="", anchor="w")
        self.dec_label.pack(side=tk.TOP, fill=tk.X)
        self.glon_label = ttk.Label(self.info_frame, text="", anchor="w")
        self.glon_label.pack(side=tk.TOP, fill=tk.X)
        self.glat_label = ttk.Label(self.info_frame, text="", anchor="w")
        self.glat_label.pack(side=tk.TOP, fill=tk.X)

        ttk.Separator(self.info_frame, orient="horizontal").pack(fill="x", pady=10)

        self.brightness_label = ttk.Label(self.info_frame, text="", anchor="w")
        self.brightness_label.pack(side=tk.TOP, fill=tk.X)
        self.contrast_label = ttk.Label(self.info_frame, text="", anchor="w")
        self.contrast_label.pack(side=tk.TOP, fill=tk.X)
        self.circles_label = ttk.Label(self.info_frame, text="", anchor="w")
        self.circles_label.pack(side=tk.TOP, fill=tk.X)
        self.noise_label = ttk.Label(self.info_frame, text="", anchor="w")
        self.noise_label.pack(side=tk.TOP, fill=tk.X)

        ttk.Separator(self.info_frame, orient="horizontal").pack(fill="x", pady=10)

        self.sort_frame = ttk.Frame(self.info_frame)
        self.sort_frame.pack(side=tk.TOP, fill=tk.X)

        self.brightness_button = ttk.Button(
            self.sort_frame,
            text="Sort by Brightness",
            command=lambda: self.sort_pulsars("brightness"),
        )
        self.brightness_button.pack(side=tk.TOP, fill=tk.X, pady=2)

        self.contrast_button = ttk.Button(
            self.sort_frame,
            text="Sort by Contrast",
            command=lambda: self.sort_pulsars("contrast"),
        )
        self.contrast_button.pack(side=tk.TOP, fill=tk.X, pady=2)

        self.circles_button = ttk.Button(
            self.sort_frame,
            text="Sort by Circles",
            command=lambda: self.sort_pulsars("circles"),
        )
        self.circles_button.pack(side=tk.TOP, fill=tk.X, pady=2)

        self.noise_button = ttk.Button(
            self.sort_frame,
            text="Sort by Noise",
            command=lambda: self.sort_pulsars("noise"),
        )
        self.noise_button.pack(side=tk.TOP, fill=tk.X, pady=2)

        self.default_button = ttk.Button(
            self.sort_frame,
            text="Smart Sort",
            command=lambda: self.sort_pulsars("default"),
        )
        self.default_button.pack(side=tk.TOP, fill=tk.X, pady=2)

        self.window.bind("-", self.zoom_out)
        self.window.bind("=", self.zoom_in)
        self.window.bind("<Left>", self.show_previous_image)
        self.window.bind("<Right>", self.show_next_image)
        self.window.bind("<Up>", self.show_previous_pulsar)
        self.window.bind("<Down>", self.show_next_pulsar)

        self.pulsar_listbox.bind("<<ListboxSelect>>", self.on_pulsar_selected)

        self.current_zoom = 1.0
        self.current_pulsar = None
        self.current_images = []
        self.current_image_index = 0
        self.pulsar_image_dict = self.create_pulsar_image_dict()
        self.current_survey = None
        self.pulsar_attributes = {}

        self.populate_listbox()
        self.calculate_all_pulsar_attributes()

        # Center the window
        parent.eval(f"tk::PlaceWindow {str(self.window)} center")

    def create_pulsar_image_dict(self):
        pulsar_image_dict = {}
        image_files = os.listdir("images")
        for image_file in image_files:
            pulsar_name, survey = image_file.split("_", 1)
            survey = survey.rsplit(".", 1)[0].replace("-", "/")
            if pulsar_name not in pulsar_image_dict:
                pulsar_image_dict[pulsar_name] = {}
            pulsar_image_dict[pulsar_name][survey] = image_file
        return pulsar_image_dict

    def populate_listbox(self):
        self.pulsar_listbox.delete(0, tk.END)
        pulsars = sorted(self.pulsar_image_dict.keys())
        for pulsar in pulsars:
            self.pulsar_listbox.insert(tk.END, pulsar)

    def calculate_all_pulsar_attributes(self):
        with ThreadPoolExecutor() as executor:
            futures = []
            for pulsar, surveys in self.pulsar_image_dict.items():
                for survey, image_file in surveys.items():
                    image_path = os.path.join("images", image_file)
                    if os.path.exists(image_path):
                        future = executor.submit(
                            self.calculate_image_attributes, pulsar, survey, image_path
                        )
                        futures.append(future)

            for future in futures:
                pulsar, survey, attributes = future.result()
                if pulsar not in self.pulsar_attributes:
                    self.pulsar_attributes[pulsar] = {}
                self.pulsar_attributes[pulsar][survey] = attributes

        self.sort_pulsars()

    def calculate_image_attributes(self, pulsar, survey, image_path):
        image = Image.open(image_path)
        img_array = np.array(image)

        # Calculate brightness
        brightness = np.mean(img_array)

        # Calculate contrast
        contrast = np.std(img_array)

        # Detect circles
        circles = None
        # img_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        # circles = cv2.HoughCircles(
        #     img_gray,
        #     cv2.HOUGH_GRADIENT,
        #     1,
        #     20,
        #     minRadius=10,
        # )
        num_circles = 0 if circles is None else len(circles[0])

        # Calculate noise from a random 100x100 spot
        h, w = img_array.shape[:2]
        x = np.random.randint(0, w - 200)
        y = np.random.randint(0, h - 200)
        random_spot = img_array[y : y + 200, x : x + 200]
        noise = np.std(random_spot)

        return (
            pulsar,
            survey,
            {
                "brightness": brightness,
                "contrast": contrast,
                "num_circles": num_circles,
                "noise": noise,
            },
        )

    def sort_pulsars(self, sort_type="default"):
        def sort_key(pulsar):
            if self.current_survey is None:
                return (float("inf"), 0, 0, 0)

            attrs = self.pulsar_attributes[pulsar].get(self.current_survey)
            if attrs is None:
                return (float("inf"), 0, 0, 0)

            brightness = attrs["brightness"]
            contrast = attrs["contrast"]
            num_circles = attrs["num_circles"]
            noise = attrs["noise"]

            if brightness == 255:
                return (float("inf"),)

            if sort_type == "brightness":
                return (brightness,)
            elif sort_type == "contrast":
                return (float("inf"), contrast) if contrast == 0 else (contrast,)
            elif sort_type == "circles":
                return (
                    (float("inf"), -num_circles)
                    if brightness == 255
                    else (-num_circles,)
                )
            elif sort_type == "noise":
                return (float("inf"), noise) if brightness == 255 else (noise,)
            else:  # default
                if noise > 50:
                    return (1, noise, brightness, contrast)
                brightness_score = brightness
                contrast_score = contrast
                circle_adjustment = min(num_circles / 10, 0.5)
                return (0, brightness_score, contrast_score, -circle_adjustment)

        sorted_pulsars = sorted(self.pulsar_attributes.keys(), key=sort_key)
        # sorted_pulsars.reverse()

        self.pulsar_listbox.delete(0, tk.END)
        for pulsar in sorted_pulsars:
            self.pulsar_listbox.insert(tk.END, pulsar)

        if self.pulsar_listbox.size() > 0:
            if self.current_pulsar:
                index = sorted_pulsars.index(self.current_pulsar)
                self.pulsar_listbox.selection_set(index)
                self.pulsar_listbox.event_generate("<<ListboxSelect>>")
            else:
                self.pulsar_listbox.selection_set(0)
                self.pulsar_listbox.event_generate("<<ListboxSelect>>")

    def on_pulsar_selected(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            self.current_pulsar = event.widget.get(index)
            self.load_pulsar_images()

    def load_pulsar_images(self):
        self.current_images = []
        if self.current_pulsar in self.pulsar_image_dict:
            for survey, image_file in self.pulsar_image_dict[
                self.current_pulsar
            ].items():
                image_path = os.path.join("images", image_file)
                if os.path.exists(image_path):
                    image = Image.open(image_path)
                    coordinates = fetch_pulsar_coordinates(f"PSR {self.current_pulsar}")
                    details = {
                        "Name": self.current_pulsar,
                        "RA": coordinates.ra.deg[0],
                        "DEC": coordinates.dec.deg[0],
                        "GLON": coordinates.galactic.l.deg[0],
                        "GLAT": coordinates.galactic.b.deg[0],
                    }
                    self.current_images.append((image, details, survey))

        if self.current_images:
            if self.current_survey and any(
                img[2] == self.current_survey for img in self.current_images
            ):
                self.current_image_index = next(
                    i
                    for i, img in enumerate(self.current_images)
                    if img[2] == self.current_survey
                )
            else:
                self.current_image_index = 0
            self.update_image()
        else:
            messagebox.showinfo(
                "Image Not Found", f"No images found for {self.current_pulsar}"
            )

    def update_image(self):
        if not self.current_images:
            return

        image, details, hips = self.current_images[self.current_image_index]
        if self.current_survey != hips:
            self.current_survey = hips
            self.sort_pulsars()  # Resort when survey changes

        self.name_label.config(text=f"Name: {details['Name']}")
        self.ra_label.config(text=f"RA: {details['RA']:.4f}")
        self.dec_label.config(text=f"DEC: {details['DEC']:.4f}")
        self.glon_label.config(text=f"GLON: {details['GLON']:.4f}")
        self.glat_label.config(text=f"GLAT: {details['GLAT']:.4f}")

        attributes = self.pulsar_attributes[self.current_pulsar][hips]
        self.brightness_label.config(text=f"Brightness: {attributes['brightness']:.2f}")
        self.contrast_label.config(text=f"Contrast: {attributes['contrast']:.2f}")
        self.circles_label.config(text=f"Detected Circles: {attributes['num_circles']}")
        self.noise_label.config(text=f"Noise: {attributes['noise']:.2f}")

        crop_width = int(image.width / self.current_zoom)
        crop_height = int(image.height / self.current_zoom)

        left = (image.width - crop_width) // 2
        top = (image.height - crop_height) // 2
        right = left + crop_width
        bottom = top + crop_height

        cropped_image = image.crop((left, top, right, bottom))
        cropped_image = cropped_image.resize((500, 500))

        # Create a new square image with rounded corners on all sides
        size = min(cropped_image.width, cropped_image.height)
        square_image = cropped_image.crop((0, 0, size, size))
        rounded_image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(rounded_image)
        draw.rounded_rectangle([(0, 0), (size, size)], 7, fill=(255, 255, 255, 255))

        # Paste the cropped image onto the rounded rectangle
        rounded_image.paste(cropped_image, (0, 0), rounded_image)

        # Draw crosshair on the rounded image
        draw = ImageDraw.Draw(rounded_image)
        center_x, center_y = rounded_image.width // 2, rounded_image.height // 2
        draw.line(
            [(center_x - 10, center_y), (center_x + 10, center_y)], fill="red", width=1
        )
        draw.line(
            [(center_x, center_y - 10), (center_x, center_y + 10)], fill="red", width=1
        )

        photo = ImageTk.PhotoImage(rounded_image)

        for widget in self.image_frame.winfo_children():
            widget.destroy()

        image_label = ttk.Label(self.image_frame, image=photo)
        image_label.image = photo
        image_label.pack(side=tk.TOP, padx=10, pady=10)

        hips_label = ttk.Label(self.image_frame, text=f"Survey: {hips}")
        hips_label.pack(side=tk.TOP, pady=(0, 10))

        if len(self.current_images) > 1:
            nav_frame = ttk.Frame(self.image_frame)
            nav_frame.pack(side=tk.TOP, pady=(0, 0))

            self.prev_button = ttk.Button(
                nav_frame, text="Previous", command=self.show_previous_image
            )
            self.prev_button.pack(side=tk.LEFT, padx=5)

            self.next_button = ttk.Button(
                nav_frame, text="Next", command=self.show_next_image
            )
            self.next_button.pack(side=tk.LEFT, padx=5)

        self.update_button_states()

    def show_previous_image(self, event=None):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.update_image()

    def show_next_image(self, event=None):
        if self.current_image_index < len(self.current_images) - 1:
            self.current_image_index += 1
            self.update_image()

    def show_previous_pulsar(self, event=None):
        current_index = self.pulsar_listbox.curselection()[0]
        if current_index > 0:
            self.pulsar_listbox.selection_clear(0, tk.END)
            self.pulsar_listbox.selection_set(current_index - 1)
            self.pulsar_listbox.event_generate("<<ListboxSelect>>")

    def show_next_pulsar(self, event=None):
        current_index = self.pulsar_listbox.curselection()[0]
        if current_index < self.pulsar_listbox.size() - 1:
            self.pulsar_listbox.selection_clear(0, tk.END)
            self.pulsar_listbox.selection_set(current_index + 1)
            self.pulsar_listbox.event_generate("<<ListboxSelect>>")

    def update_button_states(self):
        if hasattr(self, "prev_button"):
            self.prev_button.config(
                state=tk.NORMAL if self.current_image_index > 0 else tk.DISABLED
            )
        if hasattr(self, "next_button"):
            self.next_button.config(
                state=(
                    tk.NORMAL
                    if self.current_image_index < len(self.current_images) - 1
                    else tk.DISABLED
                )
            )

    def zoom_in(self, event):
        self.current_zoom *= 1.25
        self.update_image()

    def zoom_out(self, event):
        if self.current_zoom > 1:
            self.current_zoom /= 1.25
        self.update_image()


if __name__ == "__main__":
    root = tk.Tk()
    app = PulsarSorter(root)
    root.mainloop()
