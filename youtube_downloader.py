import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pytube import YouTube
import os
import threading
from datetime import timedelta

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Theme variables
        self.is_dark_theme = False
        self.configure_theme()
        
        # Download queue
        self.download_queue = []
        self.is_downloading = False
        
        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # URL Entry
        self.url_label = ttk.Label(self.main_frame, text="Enter YouTube URL:")
        self.url_label.pack(pady=5)
        
        self.url_entry = ttk.Entry(self.main_frame, width=70)
        self.url_entry.pack(pady=5)
        
        # Preview Button
        self.preview_button = ttk.Button(self.main_frame, text="Preview", command=self.preview_video)
        self.preview_button.pack(pady=5)
        
        # Video Info Frame
        self.info_frame = ttk.LabelFrame(self.main_frame, text="Video Information")
        self.info_frame.pack(fill=tk.X, pady=10)
        
        self.title_label = ttk.Label(self.info_frame, text="Title: ", wraplength=600)
        self.title_label.pack(pady=5, padx=5, anchor="w")
        
        self.duration_label = ttk.Label(self.info_frame, text="Duration: ")
        self.duration_label.pack(pady=5, padx=5, anchor="w")
        
        self.size_label = ttk.Label(self.info_frame, text="File size: ")
        self.size_label.pack(pady=5, padx=5, anchor="w")
        
        # Quality Selection
        self.quality_label = ttk.Label(self.main_frame, text="Select Quality:")
        self.quality_label.pack(pady=5)
        
        self.quality_var = tk.StringVar()
        self.quality_var.set("highest")
        
        qualities = ["highest", "lowest", "audio_only"]
        self.quality_menu = ttk.Combobox(self.main_frame, textvariable=self.quality_var, values=qualities, state="readonly")
        self.quality_menu.pack(pady=5)
        
        # Download Location
        self.location_frame = ttk.Frame(self.main_frame)
        self.location_frame.pack(fill=tk.X, pady=5)
        
        self.location_label = ttk.Label(self.location_frame, text="Download Location:")
        self.location_label.pack(side=tk.LEFT, padx=5)
        
        self.location_entry = ttk.Entry(self.location_frame, width=50)
        self.location_entry.pack(side=tk.LEFT, padx=5)
        self.location_entry.insert(0, os.path.expanduser("~/Downloads"))
        
        self.browse_button = ttk.Button(self.location_frame, text="Browse", command=self.browse_location)
        self.browse_button.pack(side=tk.LEFT)
        
        # Download Button
        self.download_button = ttk.Button(self.main_frame, text="Download", command=self.add_to_queue)
        self.download_button.pack(pady=10)
        
        # Progress Frame
        self.progress_frame = ttk.LabelFrame(self.main_frame, text="Download Progress")
        self.progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_label = ttk.Label(self.progress_frame, text="")
        self.progress_label.pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, length=400, mode='determinate')
        self.progress_bar.pack(pady=5)
        
        # Theme Toggle Button
        self.theme_button = ttk.Button(self.main_frame, text="Toggle Theme", command=self.toggle_theme)
        self.theme_button.pack(pady=5)
        
    def configure_theme(self):
        self.light_theme = {
            'bg': 'white',
            'fg': 'black',
            'select_bg': '#0078D7',
            'select_fg': 'white'
        }
        self.dark_theme = {
            'bg': '#2D2D2D',
            'fg': 'white',
            'select_bg': '#0078D7',
            'select_fg': 'white'
        }
        self.apply_theme()
    
    def apply_theme(self):
        theme = self.dark_theme if self.is_dark_theme else self.light_theme
        style = ttk.Style()
        style.configure('TFrame', background=theme['bg'])
        style.configure('TLabel', background=theme['bg'], foreground=theme['fg'])
        style.configure('TButton', background=theme['bg'])
        style.configure('TEntry', fieldbackground=theme['bg'], foreground=theme['fg'])
        self.root.configure(bg=theme['bg'])
    
    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.apply_theme()
    
    def browse_location(self):
        directory = filedialog.askdirectory()
        if directory:
            self.location_entry.delete(0, tk.END)
            self.location_entry.insert(0, directory)
    
    def format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"
    
    def preview_video(self):
        try:
            url = self.url_entry.get()
            if not url:
                messagebox.showerror("Error", "Please enter a YouTube URL")
                return
            
            yt = YouTube(url)
            self.title_label.config(text=f"Title: {yt.title}")
            self.duration_label.config(text=f"Duration: {str(timedelta(seconds=yt.length))}")
            
            quality = self.quality_var.get()
            if quality == "audio_only":
                stream = yt.streams.filter(only_audio=True).first()
            elif quality == "highest":
                stream = yt.streams.filter(progressive=True).get_highest_resolution()
            else:
                stream = yt.streams.filter(progressive=True).get_lowest_resolution()
                
            self.size_label.config(text=f"File size: {self.format_size(stream.filesize)}")
        except Exception as e:
            messagebox.showerror("Error", f"Preview failed: {str(e)}")
    
    def progress_check(self, stream, chunk, bytes_remaining):
        size = stream.filesize
        bytes_downloaded = size - bytes_remaining
        percentage = (bytes_downloaded / size) * 100
        self.progress_label.config(text=f"Downloading: {percentage:.2f}%")
        self.progress_bar['value'] = percentage
        self.root.update()
    
    def add_to_queue(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        
        self.download_queue.append({
            'url': url,
            'quality': self.quality_var.get(),
            'location': self.location_entry.get()
        })
        
        if not self.is_downloading:
            self.process_queue()
    
    def process_queue(self):
        if not self.download_queue:
            self.is_downloading = False
            return
        
        self.is_downloading = True
        download_info = self.download_queue.pop(0)
        threading.Thread(target=self.download_video, args=(download_info,), daemon=True).start()
    
    def download_video(self, download_info):
        try:
            yt = YouTube(download_info['url'], on_progress_callback=self.progress_check)
            quality = download_info['quality']
            
            if quality == "audio_only":
                stream = yt.streams.filter(only_audio=True).first()
            elif quality == "highest":
                stream = yt.streams.filter(progressive=True).get_highest_resolution()
            else:
                stream = yt.streams.filter(progressive=True).get_lowest_resolution()
            
            # Download the video
            stream.download(download_info['location'])
            
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Downloaded: {yt.title}"))
            self.root.after(0, lambda: self.progress_label.config(text=""))
            self.root.after(0, lambda: setattr(self.progress_bar, 'value', 0))
            
            # Process next download in queue
            self.root.after(0, self.process_queue)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Download failed: {str(e)}"))
            self.root.after(0, lambda: self.progress_label.config(text=""))
            self.root.after(0, lambda: setattr(self.progress_bar, 'value', 0))
            # Continue with next download even if current one failed
            self.root.after(0, self.process_queue)

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()
