#!/usr/bin/env python3
"""
Видео-скачиватель с YouTube и Rutube
Использует библиотеку yt-dlp

Примеры запуска:
  python downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  python downloader.py "https://rutube.ru/video/..."
  python downloader.py "https://www.youtube.com/playlist?list=PL..." -o "Videos"
  python downloader.py "https://rutube.ru/channel/..." --audio
"""

import argparse
from pathlib import Path
import sys

try:
    from yt_dlp import YoutubeDL
except ImportError:
    print("Ошибка: не установлен yt-dlp. Установите командой: pip install yt-dlp")
    sys.exit(1)


def download(url: str, output: str, audio_only: bool):
    outdir = Path(output).expanduser()
    outdir.mkdir(parents=True, exist_ok=True)

    ydl_opts = {
        "outtmpl": str(outdir / "%(title).200B [%(id)s].%(ext)s"),
        "format": "bestaudio/best" if audio_only else "bestvideo+bestaudio/best",
        "postprocessors": [],
    }

    if audio_only:
        ydl_opts["postprocessors"].append({
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        })

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def main():
    parser = argparse.ArgumentParser(description="Скачивание видео с YouTube и Rutube")
    parser.add_argument("url", help="Ссылка на видео/плейлист (YouTube или Rutube)")
    parser.add_argument("-o", "--output", default="downloads", help="Папка для сохранения (по умолчанию: downloads)")
    parser.add_argument("--audio", action="store_true", help="Скачать только аудио (MP3)")

    args = parser.parse_args()
    download(args.url, args.output, args.audio)


if __name__ == "__main__":
    main()
