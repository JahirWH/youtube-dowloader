import tkinter as tk
from tkinter import ttk, messagebox
from pytube import YouTube
import os

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # URL Entry
        self.url_label = ttk.Label(root, text="Enter YouTube URL:")
        self.url_label.pack(pady=10)
        
        self.url_entry = ttk.Entry(root, width=60)
        self.url_entry.pack(pady=5)
        
        # Quality Selection
        self.quality_label = ttk.Label(root, text="Select Quality:")
        self.quality_label.pack(pady=10)
        
        self.quality_var = tk.StringVar()
        self.quality_var.set("highest")
        
        qualities = ["highest", "lowest", "audio_only"]
        self.quality_menu = ttk.Combobox(root, textvariable=self.quality_var, values=qualities)
        self.quality_menu.pack(pady=5)
        
        # Download Button
        self.download_button = ttk.Button(root, text="Download", command=self.download_video)
        self.download_button.pack(pady=20)
        
        # Progress Bar
        self.progress_label = ttk.Label(root, text="")
        self.progress_label.pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(root, length=400, mode='determinate')
        self.progress_bar.pack(pady=5)
        
    def progress_check(self, stream, chunk, bytes_remaining):
        size = stream.filesize
        bytes_downloaded = size - bytes_remaining
        percentage = (bytes_downloaded / size) * 100
        self.progress_label.config(text=f"Downloading: {percentage:.2f}%")
        self.progress_bar['value'] = percentage
        self.root.update()
        
    def download_video(self):
        try:
            url = self.url_entry.get()
            if not url:
                messagebox.showerror("Error", "Please enter a YouTube URL")
                return
            
            yt = YouTube(url, on_progress_callback=self.progress_check)
            quality = self.quality_var.get()
            
            if quality == "audio_only":
                stream = yt.streams.filter(only_audio=True).first()
            elif quality == "highest":
                stream = yt.streams.filter(progressive=True).get_highest_resolution()
            else:
                stream = yt.streams.filter(progressive=True).get_lowest_resolution()
            
            # Get the download path (current directory)
            download_path = os.path.dirname(os.path.abspath(__file__))
            
            # Download the video
            stream.download(download_path)
            
            messagebox.showinfo("Success", "Download completed successfully!")
            self.progress_label.config(text="")
            self.progress_bar['value'] = 0
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.progress_label.config(text="")
            self.progress_bar['value'] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()
