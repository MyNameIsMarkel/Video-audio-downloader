# Descargador

Lightweight, cross-platform desktop application with a minimalist interface that lets you download video or audio from YouTube, Twitter/X, Reddit, TikTok, Instagram, and other sites just by pasting a link.

Built with **Python**, using `customtkinter` for the interface and `yt-dlp` as the download engine.

## Features

- **Video or audio** - pick what you want for each download.
- **Quality selection** - from 360p up to the best available for video.
- **Multiple audio formats** - mp3, m4a, wav, or opus.
- **Supported sites** - YouTube, Twitter/X, Reddit, TikTok, Instagram, and more.
- **Custom destination folder** - defaults to your Downloads folder.
- **Real-time progress bar** with download speed.
- **Non-blocking** - downloads run in the background, so the window never freezes.
- **Cross-platform** - Windows, Linux, and macOS.

## Requirements

- **Python 3.8+**
- **ffmpeg** - required to convert audio to mp3 and to merge video + audio into the best quality.
- On Linux, **tkinter** may need to be installed separately (see below).

### Installing ffmpeg

| OS | Command |
|----|---------|
| Windows | `winget install ffmpeg` |
| Debian / Ubuntu | `sudo apt install ffmpeg` |
| Fedora | `sudo dnf install ffmpeg` |
| Arch | `sudo pacman -S ffmpeg` |
| macOS | `brew install ffmpeg` |

### Installing tkinter (Linux only)

| Distro | Command |
|--------|---------|
| Debian / Ubuntu | `sudo apt install python3-tk` |
| Fedora | `sudo dnf install python3-tkinter` |
| Arch | Already included with the `python` package |

## Installation & Usage

Place all files in the same folder and install the dependencies:

```bash
pip install -r requirements.txt
```

### Windows

Double-click `iniciar.bat`, or run:

```bash
python descargador.py
```

### Linux / macOS

Make the launch script executable once, then run it:

```bash
chmod +x iniciar.sh
./iniciar.sh
```

Or run it directly:

```bash
python3 descargador.py
```

## How to use

1. Paste a link into the **Enlace** field.
2. Choose **Video** or **Audio**.
3. Pick the quality (video) or format (audio).
4. Optionally change the destination folder.
5. Click **Descargar**.

## Project structure

```
.
├── descargador.py      # Main application
├── requirements.txt    # Python dependencies
├── iniciar.bat         # Launch script (Windows)
├── iniciar.sh          # Launch script (Linux / macOS)
└── README.md
```

## Notes

- Without ffmpeg, video downloads still work but are limited in quality, and audio won't be converted to mp3.
- Only single videos are downloaded by default (playlists are skipped).
