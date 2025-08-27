"""
Видео-скачиватель с YouTube и Rutube
Использует библиотеку yt-dlp

Работает даже если ffmpeg не установлен:
 - с ffmpeg: объединяет видео+аудио (лучшее качество)
 - без ffmpeg: берёт формат "best" (однофайловый)
"""

import argparse
from pathlib import Path
import shutil
import sys

try:
    from yt_dlp import YoutubeDL
except ImportError:
    print("Ошибка: не установлен yt-dlp. Установите командой: pip install yt-dlp")
    sys.exit(1)


def download(url: str, output: str, audio_only: bool):
    outdir = Path(output).expanduser()
    outdir.mkdir(parents=True, exist_ok=True)

    # Проверяем, есть ли ffmpeg
    has_ffmpeg = shutil.which("ffmpeg") is not None

    # Если ffmpeg установлен — используем "bestvideo+bestaudio/best"
    # иначе fallback на "best" (без объединения)
    if audio_only:
        ydl_format = "bestaudio/best"
    else:
        ydl_format = "bestvideo+bestaudio/best" if has_ffmpeg else "best"

    ydl_opts = {
        "outtmpl": str(outdir / "%(title).200B [%(id)s].%(ext)s"),
        "format": ydl_format,
        "postprocessors": [],
    }

    if audio_only and has_ffmpeg:
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
