import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import time
import schedule
import threading

# File type categories
FILE_TYPES = {
    "Images": ['.jpg', '.png', '.gif'],
    "Videos": ['.mp4', '.mkv', '.avi'],
    "Documents": ['.pdf', '.docx', '.txt'],
    "Music": ['.mp3', '.wav']
}

UNDO_LOG = []

def get_category(file_ext):
    for category, extensions in FILE_TYPES.items():
        if file_ext.lower() in extensions:
            return category
    return "Others"

def organize_files(folder_path):
    if not folder_path:
        return "No folder selected."

    log_entries = []
    UNDO_LOG.clear()

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if os.path.isfile(file_path):
            file_ext = os.path.splitext(filename)[1]
            category = get_category(file_ext)
            dest_folder = os.path.join(folder_path, category)

            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)

            new_path = os.path.join(dest_folder, filename)

            try:
                shutil.move(file_path, new_path)
                log_entries.append(f"Moved: {filename} → {category}")
                UNDO_LOG.append((new_path, file_path))  # For undo
            except Exception as e:
                log_entries.append(f"Error moving {filename}: {str(e)}")

    log_path = os.path.join(folder_path, "log.txt")
    with open(log_path, "a") as log_file:
        log_file.write(f"\n--- Run at {time.ctime()} ---\n")
        for entry in log_entries:
            log_file.write(entry + "\n")

    return "\n".join(log_entries) if log_entries else "No files to organize."

def undo_last_operation():
    for src, dest in reversed(UNDO_LOG):
        if os.path.exists(src):
            try:
                shutil.move(src, dest)
            except Exception as e:
                print(f"Failed to undo move for {src}: {e}")
    UNDO_LOG.clear()
    messagebox.showinfo("Undo", "Last operation has been undone.")

# GUI Setup
def browse_folder():
    folder = filedialog.askdirectory()
    folder_path_var.set(folder)

def run_organizer():
    folder = folder_path_var.get()
    result = organize_files(folder)
    messagebox.showinfo("Result", result)

def run_scheduler():
    try:
        minutes = int(schedule_entry.get())
        schedule.clear()
        schedule.every(minutes).minutes.do(lambda: organize_files(folder_path_var.get()))

        def schedule_loop():
            while True:
                schedule.run_pending()
                time.sleep(1)

        threading.Thread(target=schedule_loop, daemon=True).start()
        messagebox.showinfo("Scheduled", f"Auto-organization scheduled every {minutes} minutes.")
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter a valid number of minutes.")

# GUI Window
root = tk.Tk()
root.title("File Organizer")
root.geometry("400x250")

folder_path_var = tk.StringVar()

tk.Label(root, text="Select Folder to Organize:").pack(pady=10)
tk.Entry(root, textvariable=folder_path_var, width=50).pack()
tk.Button(root, text="Browse", command=browse_folder).pack(pady=5)

tk.Button(root, text="Run Organizer", command=run_organizer, bg="green", fg="white").pack(pady=10)

tk.Button(root, text="Undo Last Operation", command=undo_last_operation, bg="orange").pack(pady=5)

tk.Label(root, text="Auto-run every X minutes:").pack()
schedule_entry = tk.Entry(root)
schedule_entry.pack()
tk.Button(root, text="Set Schedule", command=run_scheduler).pack(pady=5)

root.mainloop()
