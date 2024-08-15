import tkinter as tk
from tkinter import ttk
import concurrent.futures
import subprocess
from pulsars import list_pulsars, save_pulsar
from sorter import PulsarSorter
import numpy as np


class PulsarDownloader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.iconphoto(False, tk.PhotoImage(file="icon.png"))

        self.title("Pulsar Image Downloader")
        self.geometry("400x380")  # Smaller window size
        self.resizable(False, False)

        # Settings Frame
        settings_frame = ttk.Frame(self)
        settings_frame.pack(pady=10)

        # HIPS Settings
        hips_label = ttk.Label(settings_frame, text="Select HIPS Survey:")
        hips_label.pack(side=tk.TOP)

        self.hips_options = {
            "All": "ALL",
            "VPHAS": "CDS/P/VPHAS/DR4/Halpha",
            "VPHAS": "CDS/P/VPHAS/DR4/Halpha+",
            "IPHAS": "CDS/P/IPHAS/DR2/halpha",
            "SHS": "CDS/P/SHS/",
            "WISE 12um": "CDS/P/allWISE/W3",
            "WISE 22um": "CDS/P/allWISE/W4",
        }

        self.selected_hips = tk.StringVar(value=list(self.hips_options.keys())[0])
        hips_dropdown = ttk.OptionMenu(
            settings_frame,
            self.selected_hips,
            list(self.hips_options.keys())[0],
            *self.hips_options.keys(),
        )
        hips_dropdown.pack(side=tk.TOP)

        # Pulsar Search Options
        self.pulsar_options = {
            "max_dec": tk.StringVar(value="0"),
            "min_dec": tk.StringVar(value="-90"),
            "max_gb": tk.StringVar(value="5"),
            "min_gb": tk.StringVar(value="-5"),
            "min_year": tk.StringVar(value="2012"),
            "max_error": tk.StringVar(value="1"),
            "pulsar_name": tk.StringVar(value=""),
        }
        for key, var in self.pulsar_options.items():
            frame = ttk.Frame(settings_frame)
            frame.pack(side=tk.TOP)
            label = ttk.Label(frame, text=f"{key.replace('_', ' ').title()}:")
            label.pack(side=tk.LEFT)
            entry = ttk.Entry(frame, textvariable=var)
            entry.pack(side=tk.LEFT)

        # FOV Entry
        fov_frame = ttk.Frame(settings_frame)
        fov_frame.pack(side=tk.TOP)
        fov_label = ttk.Label(fov_frame, text="FOV (arcmin):")
        fov_label.pack(side=tk.LEFT)
        self.fov = tk.StringVar(value="1")
        fov_entry = ttk.Entry(fov_frame, textvariable=self.fov)
        fov_entry.pack(side=tk.LEFT)

        # Button Frame
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        # Download Button
        self.download_button = ttk.Button(
            button_frame, text="Download Images", command=self.start_download
        )
        self.download_button.pack(side=tk.LEFT, padx=5)

        # Sort Pulsars Button
        self.sort_button = ttk.Button(
            button_frame,
            text="Sort Pulsars",
            command=self.open_sorter,  # Change to open_sorter method
            # state=tk.ENABLED,
        )
        self.sort_button.pack(side=tk.LEFT, padx=5)

        # Progress Bar
        progress_frame = ttk.Frame(self)
        progress_frame.pack()
        self.progress_label_text = tk.StringVar(value="-/-")
        self.progress_label = ttk.Label(
            progress_frame, textvariable=self.progress_label_text
        )
        self.progress_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.progress = ttk.Progressbar(
            progress_frame, orient="horizontal", length=300, mode="determinate"
        )
        self.progress.pack(side=tk.LEFT)
        self.downloading = False

        # Center the window
        self.eval(f"tk::PlaceWindow . center")

    def start_download(self):
        if not self.downloading:
            self.downloading = True
            self.download_button.config(
                text="Stop Download", command=self.stop_download
            )
            self.progress["value"] = 0
            self.sort_button.config(state=tk.DISABLED)

            self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            self.future = self.executor.submit(self.download_thread_func)
            self.check_future()

    def stop_download(self):
        self.download_button.config(text="Download Images", command=self.start_download)
        self.downloading = False
        self.progress["value"] = 0
        self.progress_label_text.set("-/-")
        self.sort_button.config(state=tk.DISABLED)
        if hasattr(self, "executor"):
            self.executor.shutdown(wait=False)

    def check_future(self):
        if self.future.done():
            self.download_button.config(
                text="Download Images", command=self.start_download
            )
            self.downloading = False
            self.sort_button.config(state=tk.NORMAL)
        else:
            self.after(100, self.check_future)

    def download_thread_func(self):
        pulsar_options = {}
        for key, value in self.pulsar_options.items():
            try:
                if key == "pulsar_name":
                    pulsar_options[key] = value.get()
                else:
                    pulsar_options[key] = float(value.get())
            except ValueError:
                # Handle empty string or invalid input
                pulsar_options[key] = None
        pulsars = list_pulsars(pulsar_options)
        total_pulsars = len(pulsars)
        if self.selected_hips.get() == "All":
            total_pulsars *= 5
        self.progress["maximum"] = total_pulsars

        for i, pulsar in enumerate(pulsars):
            if not self.downloading:
                break
            if self.selected_hips.get() != "All":
                save_pulsar(
                    pulsar,
                    self.hips_options[self.selected_hips.get()],
                    self.fov.get(),
                )
                if self.downloading:
                    self.progress["value"] = i + 1
                    self.progress_label_text.set(f"{i + 1}/{total_pulsars}")
                    self.update_idletasks()  # Update the GUI
            else:
                for hips_option in self.hips_options.values():
                    if hips_option != "ALL":
                        save_pulsar(
                            pulsar,
                            hips_option,
                            self.fov.get(),
                        )
                        if self.downloading:
                            self.progress["value"] += 1
                            self.progress_label_text.set(
                                f"{self.progress['value']}/{total_pulsars}"
                            )
                            self.update_idletasks()  # Update the GUI

    def open_sorter(self):
        sorter_window = PulsarSorter(self)  # Pass self as the parent window


if __name__ == "__main__":
    app = PulsarDownloader()
    app.mainloop()
