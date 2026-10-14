
from tkinter import filedialog, messagebox
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from PIL import Image, ImageDraw

import pystray
import tkinter as tk
import threading
import src.report_sender as report_app
import yaml


PROJECT_DIR = Path(__file__).resolve().parent
CONFIG_FILE = PROJECT_DIR / "config.yaml"
CONFIG_FILE.touch(exist_ok=True)  # Create the file if it doesn't exist


def load_config():
    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def save_settings(repository: str, recipient: str, subject_prefix: str, time: str):
    try:
        time_value = time

        # Validate the daily time as HH:MM.
        from datetime import datetime
        datetime.strptime(time_value, "%H:%M")

        config = load_config()

        config["repository"] = repository
        config.setdefault("email", {})
        config["email"]["recipient"] = recipient
        config.setdefault("report", {})
        config["report"]["subject_prefix"] = subject_prefix
        config.setdefault("schedule", {})
        config["schedule"]["time"] = time_value

        if not config["repository"]:
            raise ValueError("Repository path cannot be empty.")

        if not config["email"]["recipient"]:
            raise ValueError("Recipient email cannot be empty.")

        with CONFIG_FILE.open("w", encoding="utf-8") as file:
            yaml.safe_dump(
                config,
                file,
                sort_keys=False,
                allow_unicode=True,
            )

        messagebox.showinfo(
            "Settings saved",
            "Settings saved to config.yaml.",
        )

    except ValueError as error:
        messagebox.showerror("Invalid settings", str(error))
    except Exception as error:
        messagebox.showerror("Error", str(error))


def browse_repository():
    folder = filedialog.askdirectory(
        title="Select Git repository"
    )

    if folder:
        repo_entry.delete(0, tk.END)
        repo_entry.insert(0, folder)


def run_report_in_background():
    run_button.config(state="disabled")
    status_label.config(text="Generating report... Please wait.")

    def worker():
        try:
            report_app.run_daily_git_report()
            root.after(
                0,
                lambda: status_label.config(
                    text="Report sent successfully."
                ),
            )
        except Exception as error:
            message = str(error)
            root.after(
                0,
                lambda: status_label.config(
                    text=f"Report failed: {message}"
                ),
            )
        finally:
            root.after(
                0,
                lambda: run_button.config(state="normal"),
            )

    threading.Thread(target=worker, daemon=True).start()

def start_scheduler():
    config = load_config()
    time_value = config.get("schedule", {}).get("time", "19:00")

    try:
        hour, minute = map(int, time_value.split(":"))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError
    except ValueError:
        messagebox.showerror(
            "Invalid schedule",
            "Daily send time must use HH:MM format, such as 19:00.",
        )
        return

    scheduler = BackgroundScheduler(
        timezone="Asia/Kuala_Lumpur"
    )

    scheduler.add_job(
        run_report_in_background,
        trigger="cron",
        hour=hour,
        minute=minute,
        id="daily_git_report",
        replace_existing=True,
        max_instances=1,
    )

    scheduler.start()
    status_label.config(
        text=f"Scheduled daily at {hour:02d}:{minute:02d} Malaysia time."
    )

    return scheduler

def create_tray_image():
    image = Image.new("RGB", (64, 64), "#1f8aa5")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(
        (8, 8, 56, 56),
        radius=10,
        fill="white",
    )
    draw.text((17, 20), "Git", fill="#1f8aa5")
    draw.text((13, 34), "Daily", fill="#1f8aa5")
    return image


def show_window(icon=None, item=None):
    root.after(0, root.deiconify)


def quit_app(icon=None, item=None):
    if icon:
        icon.stop()

    def close_window():
        root.destroy()

    root.after(0, close_window)


def minimize_to_tray():
    root.withdraw()


def setup_tray():
    menu = pystray.Menu(
        pystray.MenuItem("Open Git Daily Agent", show_window),
        pystray.MenuItem("Send Report Now", lambda icon, item: run_report_in_background()),
        pystray.MenuItem("Exit", quit_app),
    )

    icon = pystray.Icon(
        "GitDailyAgent",
        create_tray_image(),
        "Git Daily Agent",
        menu,
    )

    return icon

config = load_config()

root = tk.Tk()
root.title("Git Daily Agent")
root.geometry("580x310")
root.resizable(False, False)

tk.Label(
    root,
    text="Git Daily Agent Settings",
    font=("Segoe UI", 16, "bold"),
).pack(pady=(16, 12))

form = tk.Frame(root, padx=20)
form.pack(fill="x")

tk.Label(form, text="Repository path").grid(
    row=0, column=0, sticky="w", pady=7
)
repo_entry = tk.Entry(form, width=43)
repo_entry.grid(row=0, column=1, padx=8)
repo_entry.insert(0, config.get("repository", ""))

tk.Button(
    form,
    text="Browse...",
    command=browse_repository,
).grid(row=0, column=2)

tk.Label(form, text="Email recipient").grid(
    row=1, column=0, sticky="w", pady=7
)
recipient_entry = tk.Entry(form, width=43)
recipient_entry.grid(row=1, column=1, columnspan=2, sticky="w", padx=8)
recipient_entry.insert(
    0, config.get("email", {}).get("recipient", "")
)

tk.Label(form, text="Subject prefix").grid(
    row=2, column=0, sticky="w", pady=7
)
prefix_entry = tk.Entry(form, width=43)
prefix_entry.grid(row=2, column=1, columnspan=2, sticky="w", padx=8)
prefix_entry.insert(
    0,
    config.get("report", {}).get(
        "subject_prefix", "Git Daily Report"
    ),
)

tk.Label(form, text="Daily send time (HH:MM)").grid(
    row=3, column=0, sticky="w", pady=7
)
time_entry = tk.Entry(form, width=12)
time_entry.grid(row=3, column=1, sticky="w", padx=8)
time_entry.insert(
    0, config.get("schedule", {}).get("time", "19:00")
)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(
    button_frame,
    text="Save Settings",
    command=lambda: save_settings(
        repository=repo_entry.get().strip(),
        recipient=recipient_entry.get().strip(),
        subject_prefix=prefix_entry.get().strip(),
        time=time_entry.get().strip()
    ),
    width=18,
).pack(side="left", padx=5)

run_button = tk.Button(
    button_frame,
    text="Send Report Now",
    command=run_report_in_background,
    width=18,
)
run_button.pack(side="left", padx=5)

status_label = tk.Label(
    root,
    text="Ready",
    font=("Segoe UI", 9),
    wraplength=360,
)
status_label.pack(pady=(0, 10))

scheduler = start_scheduler()
tray_icon = setup_tray()

root.protocol("WM_DELETE_WINDOW", minimize_to_tray)

tray_thread = threading.Thread(target=tray_icon.run, daemon=True)
tray_thread.start()

root.mainloop()

tray_icon.stop()

if scheduler:
    scheduler.shutdown(wait=False)
