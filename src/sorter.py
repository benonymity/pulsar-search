import io
import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from pulsars import fetch_pulsar_coordinates
from PIL import Image, ImageTk, ImageDraw, ImageEnhance


class PulsarSorter:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Pulsar Viewer")
        self.window.geometry("890x660")  # Increased width to accommodate new info
        self.window.resizable(False, False)
        self.current_images = []
        self.current_image_index = 0

        self.pulsar_listbox = tk.Listbox(self.window, width=15)
        self.pulsar_listbox.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.image_frame = ttk.Frame(self.window)
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.info_frame = ttk.Frame(self.window)
        self.info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

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

        # Add contrast slider
        self.contrast_slider = ttk.Scale(
            self.info_frame,
            from_=0,
            to=20,
            orient=tk.HORIZONTAL,
            command=self.update_image,
        )
        self.contrast_slider.set(10)  # Default contrast
        ttk.Label(self.info_frame, text="Contrast").pack(side=tk.TOP, fill=tk.X)
        self.contrast_slider.pack(side=tk.TOP, fill=tk.X, pady=0)

        # Add brightness slider
        self.brightness_slider = ttk.Scale(
            self.info_frame,
            from_=0,
            to=20,
            orient=tk.HORIZONTAL,
            command=self.update_image,
        )
        self.brightness_slider.set(10)  # Default brightness
        ttk.Label(self.info_frame, text="Brightness").pack(side=tk.TOP, fill=tk.X)
        self.brightness_slider.pack(side=tk.TOP, fill=tk.X, pady=0)

        def update_zoom(value):
            self.current_zoom = float(value)
            self.update_image()

        # Add zoom slider
        self.zoom_slider = ttk.Scale(
            self.info_frame,
            from_=1,
            to=5,
            orient=tk.HORIZONTAL,
        )
        self.zoom_slider.set(1.0)  # Default zoom
        self.zoom_slider.config(command=update_zoom)
        ttk.Label(self.info_frame, text="Zoom").pack(side=tk.TOP, fill=tk.X)
        self.zoom_slider.pack(side=tk.TOP, fill=tk.X, pady=0)

        # Add method to handle zoom changes

        ttk.Separator(self.info_frame, orient="horizontal").pack(fill="x", pady=10)

        self.sort_frame = ttk.Frame(self.info_frame)
        self.sort_frame.pack(side=tk.TOP, fill=tk.X)

        self.default_button = ttk.Button(
            self.sort_frame,
            text="Smart Sort",
            command=lambda: self.sort_pulsars("default"),
        )
        self.default_button.pack(side=tk.TOP, fill=tk.X, pady=2)

        self.alphabetical_button = ttk.Button(
            self.sort_frame,
            text="Sort Alphabetically",
            command=lambda: self.sort_pulsars("alphabetical"),
        )
        self.alphabetical_button.pack(side=tk.TOP, fill=tk.X, pady=2)

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

        # self.circles_button = ttk.Button(
        #     self.sort_frame,
        #     text="Sort by Circles",
        #     command=lambda: self.sort_pulsars("circles"),
        # )
        # self.circles_button.pack(side=tk.TOP, fill=tk.X, pady=2)

        self.noise_button = ttk.Button(
            self.sort_frame,
            text="Sort by Noise",
            command=lambda: self.sort_pulsars("noise"),
        )
        self.noise_button.pack(side=tk.TOP, fill=tk.X, pady=2)

        ttk.Separator(self.sort_frame, orient="horizontal").pack(fill="x", pady=10)

        self.denoise_button = ttk.Button(
            self.sort_frame,
            text="Denoise",
            command=self.denoise,
        )
        self.denoise_button.pack(side=tk.TOP, fill=tk.X, pady=2)

        ttk.Separator(self.sort_frame, orient="horizontal").pack(fill="x", pady=10)

        def copy_to_clipboard_with_feedback():
            self.copy_to_clipboard()
            original_text = self.copy_button["text"]
            self.copy_button["text"] = "Copied!"
            self.window.after(2000, lambda: self.copy_button.config(text=original_text))

        self.copy_button = ttk.Button(
            self.sort_frame,
            text="Copy Image",
            command=copy_to_clipboard_with_feedback,
        )
        self.copy_button.pack(side=tk.TOP, fill=tk.X, pady=2)

        self.window.bind("-", self.zoom_out)
        self.window.bind("=", self.zoom_in)
        self.window.bind("<Left>", self.show_previous_image)
        self.window.bind("<Right>", self.show_next_image)
        self.window.bind("<Up>", self.show_previous_pulsar)
        self.window.bind("<Down>", self.show_next_pulsar)
        if os.name == "posix" and os.uname().sysname == "Darwin":  # macOS
            self.window.bind(
                "<Command-c>", lambda event: copy_to_clipboard_with_feedback()
            )
        else:  # Windows and other Unix-like systems
            self.window.bind(
                "<Control-c>", lambda event: copy_to_clipboard_with_feedback()
            )

        self.pulsar_listbox.bind("<<ListboxSelect>>", self.on_pulsar_selected)
        self.window.bind("<Motion>", self.on_mouse_move)

        self.current_zoom = 1.0
        self.current_pulsar = None
        self.pulsar_image_dict = self.create_pulsar_image_dict()
        self.current_survey = "CDS/P/VPHAS/DR4/Halpha"
        self.pulsar_attributes = {}
        self.populate_listbox()
        self.calculate_all_pulsar_attributes()
        self.load_pulsar_images()

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
        for pulsar, surveys in self.pulsar_image_dict.items():
            for survey, image_file in surveys.items():
                image_path = os.path.join("images", image_file)
                if os.path.exists(image_path):
                    pulsar, survey, attributes = self.calculate_image_attributes(
                        pulsar, survey, image_path
                    )
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
                "num_circles": None,
                "noise": noise,
            },
        )

    def copy_to_clipboard(self):
        if self.current_images:
            try:
                output = io.BytesIO()
                image, details, hips = self.current_images[self.current_image_index]

                # Apply zoom
                crop_width = int(image.width / self.current_zoom)
                crop_height = int(image.height / self.current_zoom)
                left = (image.width - crop_width) // 2
                top = (image.height - crop_height) // 2
                right = left + crop_width
                bottom = top + crop_height
                cropped_image = image.crop((left, top, right, bottom))
                cropped_image = cropped_image.resize((500, 500))

                cropped_image.convert("RGB").save(output, "PNG")
                data = output.getvalue()
                output.close()

                if os.name == "posix":  # macOS
                    import pasteboard

                    pb = pasteboard.Pasteboard()
                    pb.set_contents(data, pasteboard.PNG)
                elif os.name == "nt":  # Windows
                    import win32clipboard
                    from io import BytesIO

                    output = BytesIO()
                    cropped_image.convert("RGB").save(output, "BMP")
                    data = output.getvalue()[14:]
                    output.close()

                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                    win32clipboard.CloseClipboard()
                else:
                    messagebox.showwarning(
                        "Clipboard Error",
                        "Clipboard functionality is not supported on this operating system.",
                    )
            except ImportError as e:
                messagebox.showwarning(
                    "Clipboard Error",
                    f"Required modules not found: {str(e)}. Please install them to use this feature.",
                )
        else:
            messagebox.showinfo("No Image", "No image is currently selected.")

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
            elif sort_type == "alphabetical":
                return (pulsar,)
            else:  # default
                if noise > 50:
                    return (1, noise, brightness, contrast)
                brightness_score = brightness
                contrast_score = contrast
                return (0, brightness_score, contrast_score, 0)

        if sort_type == "alphabetical":
            sorted_pulsars = sorted(self.pulsar_attributes.keys())
        else:
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

    def denoise(self):
        if not self.current_images:
            return

        image, details, hips = self.current_images[self.current_image_index]

        try:

            # Convert PIL Image to OpenCV format (grayscale)
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            denoised_image = cv2.fastNlMeansDenoising(cv_image, None, 10, 7, 21)
            denoised_pil = Image.fromarray(denoised_image)
            self.current_images[self.current_image_index] = (
                denoised_pil,
                details,
                hips,
            )

            self.update_image()
        except:
            pass

    def update_image(self, contrast_value=None):
        if len(self.current_images) == 0:
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

        if not attributes["num_circles"]:
            attributes["num_circles"] = 0

        self.circles_label.config(text=f"Detected Circles: {attributes['num_circles']}")
        self.noise_label.config(text=f"Noise: {attributes['noise']:.2f}")

        crop_width = int(image.width / self.current_zoom)
        crop_height = int(image.height / self.current_zoom)

        left = (image.width - crop_width) // 2
        top = (image.height - crop_height) // 2
        right = left + crop_width
        bottom = top + crop_height

        cropped_image = image.crop((left, top, right, bottom))
        cropped_image = cropped_image.resize((550, 550))

        # Adjust contrast
        contrast_value = self.contrast_slider.get() / 10
        brightness_value = self.brightness_slider.get() / 10
        contrast = ImageEnhance.Contrast(cropped_image)
        cropped_image = contrast.enhance(contrast_value)
        brightness = ImageEnhance.Brightness(cropped_image)
        cropped_image = brightness.enhance(brightness_value)

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
        self.rounded_image = rounded_image
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
        image_label.pack(side=tk.TOP, pady=10)

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

    def on_mouse_move(self, event):
        if not hasattr(self, "rounded_image"):
            return

        x, y = event.x, event.y
        image_width, image_height = self.rounded_image.size

        if 0 <= x < image_width and 0 <= y < image_height:
            r, g, b, _ = self.rounded_image.getpixel((x, y))
            if not hasattr(self, "rgb_label"):
                self.rgb_label = ttk.Label(self.image_frame, text="")
                self.rgb_label.pack()
            if self.rgb_label.winfo_exists():
                self.rgb_label.config(text=f"RGB: ({r}, {g}, {b})")
                self.rgb_label.place(
                    x=event.x_root - self.image_frame.winfo_rootx() + 10,
                    y=event.y_root - self.image_frame.winfo_rooty() + 10,
                )
                self.rgb_label.lift()  # Ensure the label is on top
            else:
                self.rgb_label = ttk.Label(
                    self.image_frame, text=f"RGB: ({r}, {g}, {b})"
                )
                self.rgb_label.place(
                    x=event.x_root - self.image_frame.winfo_rootx() + 10,
                    y=event.y_root - self.image_frame.winfo_rooty() + 10,
                )
                self.rgb_label.lift()  # Ensure the label is on top

        else:
            if hasattr(self, "rgb_label"):
                self.rgb_label.config(text="")
                self.rgb_label.place_forget()

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
        self.pulsar_listbox.focus_set()
        if current_index > 0:
            self.pulsar_listbox.selection_clear(0, tk.END)
            self.pulsar_listbox.selection_set(current_index)
            self.pulsar_listbox.event_generate("<<ListboxSelect>>")

    def show_next_pulsar(self, event=None):
        current_index = self.pulsar_listbox.curselection()[0]
        self.pulsar_listbox.focus_set()
        if current_index == 0:
            self.pulsar_listbox.selection_clear(0, tk.END)
            self.pulsar_listbox.selection_set(1)
            self.pulsar_listbox.event_generate("<<ListboxSelect>>")
        elif current_index < self.pulsar_listbox.size() - 1:
            self.pulsar_listbox.selection_clear(0, tk.END)
            self.pulsar_listbox.selection_set(current_index)
            self.pulsar_listbox.event_generate("<<ListboxSelect>>")

    def update_button_states(self):
        if hasattr(self, "prev_button") and self.prev_button.winfo_exists():
            self.prev_button["state"] = (
                "normal" if self.current_image_index > 0 else "disabled"
            )
        if hasattr(self, "next_button") and self.next_button.winfo_exists():
            self.next_button["state"] = (
                "normal"
                if self.current_image_index < len(self.current_images) - 1
                else "disabled"
            )

    def zoom_in(self, event):
        if self.current_zoom < 10:
            self.current_zoom *= 1.25
            self.zoom_slider.set(self.current_zoom)
        self.update_image()

    def zoom_out(self, event):
        if self.current_zoom > 1:
            self.current_zoom /= 1.25
            self.zoom_slider.set(self.current_zoom)
        self.update_image()


if __name__ == "__main__":
    root = tk.Tk()
    root.iconphoto(False, tk.PhotoImage(file="icon.png"))
    root.withdraw()  # Hide the root window
    app = PulsarSorter(root)
    app.window.mainloop()
