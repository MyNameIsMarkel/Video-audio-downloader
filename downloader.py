"""
Video / Audio Downloader
========================
Minimal desktop app for Windows that downloads video or audio
from YouTube, Twitter/X, Reddit, Instagram, TikTok, and hundreds of other sites.

Engine: yt-dlp | Interface: customtkinter
"""

import os
import sys
import threading
import queue
import re

import customtkinter as ctk
from tkinter import filedialog
import yt_dlp


# ----------------------------- Appearance ---------------------------------- #
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


ACCENT = "#637C9A"
ACCENT_HOVER = "#637C9A"
BG = "#1A1A1A"
CARD = "#111111"
TEXT_DIM = "#656565"
OK = "#637C9A"
ERR = "#B14441"


def remove_ansi(text: str) -> str:
    """Remove ANSI color codes that yt-dlp may include in messages."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text or "")


class Downloader(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Downloader")
        self.geometry("560x600")
        self.minsize(520, 560)
        self.configure(fg_color=BG)

        # Default destination folder: the user's Downloads folder
        self.download_folder = os.path.join(os.path.expanduser("~"), "Downloads")

        # Queue used to communicate between the download thread and the UI
        self.message_queue = queue.Queue()
        self.is_downloading = False

        self._build_ui()
        self.after(100, self._process_queue)

    # ------------------------------ UI -------------------------------------- #
    def _build_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=28, pady=24)

        # --- Title ---
        ctk.CTkLabel(
            container,
            text="Downloader",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#FFFFFF",
        ).pack(anchor="w")

        ctk.CTkLabel(
            container,
            text="YouTube · Twitter · Reddit · TikTok · Instagram and more",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_DIM,
        ).pack(anchor="w", pady=(2, 22))

        # --- URL field ---
        ctk.CTkLabel(
            container,
            text="LINK",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_DIM,
        ).pack(anchor="w")

        self.url_entry = ctk.CTkEntry(
            container,
            height=46,
            corner_radius=12,
            fg_color=CARD,
            border_color=CARD,
            border_width=2,
            placeholder_text="Paste the video link here...",
            font=ctk.CTkFont(size=14),
        )
        self.url_entry.pack(fill="x", pady=(6, 18))
        self.url_entry.bind("<Return>", lambda event: self._start_download())

        # --- Video / Audio selector ---
        ctk.CTkLabel(
            container,
            text="WHAT DO YOU WANT TO DOWNLOAD",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_DIM,
        ).pack(anchor="w")

        self.download_mode = ctk.StringVar(value="Video")
        self.mode_selector = ctk.CTkSegmentedButton(
            container,
            values=["Video", "Audio"],
            variable=self.download_mode,
            height=44,
            corner_radius=12,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=CARD,
            selected_color=ACCENT,
            selected_hover_color=ACCENT_HOVER,
            unselected_color=CARD,
            unselected_hover_color="#2A2D35",
            command=self._change_mode,
        )
        self.mode_selector.pack(fill="x", pady=(6, 18))

        # --- Quality / format selector ---
        self.option_row = ctk.CTkFrame(container, fg_color="transparent")
        self.option_row.pack(fill="x", pady=(0, 18))

        self.option_label = ctk.CTkLabel(
            self.option_row,
            text="QUALITY",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_DIM,
        )
        self.option_label.pack(anchor="w")

        self.option_menu = ctk.CTkOptionMenu(
            self.option_row,
            values=["Best available", "1080p", "720p", "480p", "360p"],
            height=42,
            corner_radius=12,
            fg_color=CARD,
            button_color=CARD,
            button_hover_color="#2A2D35",
            dropdown_fg_color=CARD,
            font=ctk.CTkFont(size=13),
        )
        self.option_menu.pack(fill="x", pady=(6, 0))

        # --- Destination folder ---
        ctk.CTkLabel(
            container,
            text="SAVE TO",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_DIM,
        ).pack(anchor="w")

        folder_row = ctk.CTkFrame(container, fg_color="transparent")
        folder_row.pack(fill="x", pady=(6, 22))

        self.folder_label = ctk.CTkLabel(
            folder_row,
            text=self.download_folder,
            anchor="w",
            fg_color=CARD,
            corner_radius=12,
            height=42,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_DIM,
        )
        self.folder_label.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            folder_row,
            text="Change",
            width=90,
            height=42,
            corner_radius=12,
            fg_color=CARD,
            hover_color="#2A2D35",
            font=ctk.CTkFont(size=13),
            command=self._choose_folder,
        ).pack(side="right")

        # --- Download button ---
        self.download_button = ctk.CTkButton(
            container,
            text="Download",
            height=50,
            corner_radius=12,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._start_download,
        )
        self.download_button.pack(fill="x", pady=(4, 14))

        # --- Progress bar ---
        self.progress_bar = ctk.CTkProgressBar(
            container,
            height=8,
            corner_radius=4,
            fg_color=CARD,
            progress_color=ACCENT,
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x")

        # --- Status ---
        self.status_label = ctk.CTkLabel(
            container,
            text="Ready",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_DIM,
        )
        self.status_label.pack(anchor="w", pady=(10, 0))

    # --------------------------- Interactions ------------------------------- #
    def _change_mode(self, value):
        if value == "Video":
            self.option_label.configure(text="QUALITY")
            self.option_menu.configure(
                values=["Best available", "1080p", "720p", "480p", "360p"]
            )
            self.option_menu.set("Best available")
        else:
            self.option_label.configure(text="AUDIO FORMAT")
            self.option_menu.configure(values=["mp3", "m4a", "wav", "opus"])
            self.option_menu.set("mp3")

    def _choose_folder(self):
        selected_folder = filedialog.askdirectory(initialdir=self.download_folder)
        if selected_folder:
            self.download_folder = selected_folder
            self.folder_label.configure(text=selected_folder)

    def _start_download(self):
        if self.is_downloading:
            return

        url = self.url_entry.get().strip()
        if not url:
            self._set_status("Paste a link first", ERR)
            return

        self.is_downloading = True
        self.download_button.configure(state="disabled", text="Downloading...")
        self.progress_bar.set(0)
        self._set_status("Connecting...", TEXT_DIM)

        worker_thread = threading.Thread(
            target=self._download,
            args=(
                url,
                self.download_mode.get(),
                self.option_menu.get(),
                self.download_folder,
            ),
            daemon=True,
        )
        worker_thread.start()

    # --------------------------- yt-dlp logic ------------------------------- #
    def _download(self, url, mode, option, folder):
        """Run the download in a separate thread so the UI stays responsive."""
        try:
            ydl_options = {
                "outtmpl": os.path.join(folder, "%(title)s.%(ext)s"),
                "progress_hooks": [self._progress_hook],
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
                "ignoreerrors": False,
            }

            if mode == "Video":
                if option == "Best available":
                    ydl_options["format"] = "bestvideo+bestaudio/best"
                else:
                    max_height = option.replace("p", "")
                    ydl_options["format"] = (
                        f"bestvideo[height<={max_height}]+bestaudio/"
                        f"best[height<={max_height}]/best"
                    )
                ydl_options["merge_output_format"] = "mp4"
            else:
                ydl_options["format"] = "bestaudio/best"
                ydl_options["postprocessors"] = [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": option,
                        "preferredquality": "192",
                    }
                ]

            with yt_dlp.YoutubeDL(ydl_options) as ydl:
                ydl.download([url])

            self.message_queue.put(("done", None))

        except Exception as exc:
            self.message_queue.put(("error", remove_ansi(str(exc))))

    def _progress_hook(self, data):
        """Called by yt-dlp during download from the worker thread."""
        if data["status"] == "downloading":
            total_bytes = data.get("total_bytes") or data.get("total_bytes_estimate")
            downloaded_bytes = data.get("downloaded_bytes", 0)
            speed = data.get("speed")

            progress_fraction = (downloaded_bytes / total_bytes) if total_bytes else None
            speed_text = ""
            if speed:
                speed_text = f" · {speed / 1_048_576:.1f} MB/s"

            self.message_queue.put(("progress", (progress_fraction, speed_text)))

        elif data["status"] == "finished":
            self.message_queue.put(("processing", None))

    # ----------------------- Thread -> UI bridge ---------------------------- #
    def _process_queue(self):
        try:
            while True:
                message_type, payload = self.message_queue.get_nowait()

                if message_type == "progress":
                    progress_fraction, speed_text = payload
                    if progress_fraction is not None:
                        self.progress_bar.set(progress_fraction)
                        self._set_status(
                            f"Downloading {int(progress_fraction * 100)}%{speed_text}",
                            TEXT_DIM,
                        )
                    else:
                        self._set_status(f"Downloading...{speed_text}", TEXT_DIM)

                elif message_type == "processing":
                    self.progress_bar.set(1)
                    self._set_status("Processing file...", TEXT_DIM)

                elif message_type == "done":
                    self.progress_bar.set(1)
                    self._set_status("Download completed", OK)
                    self._reset_button()

                elif message_type == "error":
                    self.progress_bar.set(0)
                    self._set_status(f"Error: {payload[:80]}", ERR)
                    self._reset_button()

        except queue.Empty:
            pass

        self.after(100, self._process_queue)

    def _reset_button(self):
        self.is_downloading = False
        self.download_button.configure(state="normal", text="Download")

    def _set_status(self, text, color):
        self.status_label.configure(text=text, text_color=color)


if __name__ == "__main__":
    app = Downloader()
    app.mainloop()