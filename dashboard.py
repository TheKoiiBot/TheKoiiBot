import tkinter as tk
from tkinter import scrolledtext, messagebox
from threading import Thread
import queue
import sys

class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KoiiBot Dashboard")
        self.geometry("520x640")
        self.configure(bg="#0E121D")
        self.tweet_count = 0
        self.tweet_log = []
        self.status = "Inactive"
        self.queue = queue.Queue()
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(100, self._process_queue)

    def _build_ui(self):
        # Status Indicator
        self.status_label = tk.Label(self, text="Inactive", bg="#23273A", fg="#fff", font=("Segoe UI", 18, "bold"), width=12, pady=8)
        self.status_label.pack(pady=(28, 8))
        self.status_label.configure(relief="flat", bd=0, highlightthickness=0)
        self.status_label.bind("<Enter>", lambda e: self._update_status_badge(self.status))
        self.status_label.bind("<Leave>", lambda e: self._update_status_badge(self.status))
        self._update_status_badge("Inactive")

        # Daily Tweet Counter
        self.daily_tweet_count = 0
        self.daily_counter_label = tk.Label(self, text="Tweets sent today: 0", bg="#0E121D", fg="#7EC4FF", font=("Segoe UI", 13, "bold"))
        self.daily_counter_label.pack(pady=(0, 2))

        # Tweet Counter
        self.tweet_count = 0
        self.counter_label = tk.Label(self, text="Tweets Sent: 0", bg="#0E121D", fg="#fff", font=("Segoe UI", 15, "bold"))
        self.counter_label.pack(pady=(0, 2))

        # Tweet Log
        self.log_frame = tk.Frame(self, bg="#0E121D")
        self.log_frame.pack(padx=18, pady=10, fill=tk.BOTH, expand=True)
        self.log_box = scrolledtext.ScrolledText(self.log_frame, height=20, width=62, state='disabled', font=("Segoe UI", 11), bg="#181C2A", fg="#fff", bd=0, relief="flat", highlightthickness=0, wrap=tk.WORD)
        self.log_box.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        self.log_box.configure(borderwidth=0, highlightbackground="#23273A", highlightcolor="#23273A")
        self.log_box.bind("<FocusIn>", lambda e: self.log_box.config(bg="#20243A"))
        self.log_box.bind("<FocusOut>", lambda e: self.log_box.config(bg="#181C2A"))
        self.log_frame.configure(highlightbackground="#23273A", highlightcolor="#23273A", highlightthickness=2, bd=0)

        # STOP Badge/Button (aligned with status area)
        self.stop_button = tk.Label(
            self,
            text="STOP",
            bg="#D9534F",
            fg="#fff",
            font=("Segoe UI", 18, "bold"),
            width=12,
            pady=8,
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2"
        )
        self.stop_button.pack(pady=(28, 8))
        self.stop_button.configure(relief="flat", bd=0, highlightthickness=0)
        self.stop_button.bind("<Button-1>", lambda e: self._on_stop_bot())
        self.stop_button.bind("<Enter>", lambda e: self.stop_button.config(bg="#b52b27"))
        self.stop_button.bind("<Leave>", lambda e: self.stop_button.config(bg="#D9534F"))

        # Message label for STOP countdown (hidden by default)
        self.stop_msg_label = tk.Label(
            self,
            text="",
            bg="#0E121D",
            fg="#FFD700",
            font=("Segoe UI", 13, "bold"),
            pady=6
        )
        self.stop_msg_label.pack(pady=(0, 0))

    def _update_status_badge(self, status):
        self.status = status
        if status == "Active":
            self.status_label.config(text="Active", bg="#28a745", fg="#fff")
        else:
            self.status_label.config(text="Inactive", bg="#dc3545", fg="#fff")

    def set_status(self, status):
        self.status = status
        self._update_status_badge(status)

    def increment_daily_counter(self):
        self.daily_tweet_count += 1
        self.daily_counter_label.config(text=f"Tweets sent today: {self.daily_tweet_count}")

    def reset_daily_counter(self):
        self.daily_tweet_count = 0
        self.daily_counter_label.config(text="Tweets sent today: 0")

    def schedule_daily_reset(self):
        import datetime
        import threading
        now = datetime.datetime.now()
        tomorrow = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        seconds_until_midnight = (tomorrow - now).total_seconds()
        def reset_and_reschedule():
            self.reset_daily_counter()
            self.schedule_daily_reset()
        threading.Timer(seconds_until_midnight, reset_and_reschedule).start()

    def add_tweet(self, timestamp, text):
        self.tweet_count += 1
        self.counter_label.config(text=f"Tweets Sent: {self.tweet_count}")
        self.increment_daily_counter()
        self.tweet_log.insert(0, (timestamp, text))
        self._refresh_log()
        print(f"[INFO] Tweet added to dashboard at {timestamp}")

    def _refresh_log(self):
        self.log_box.config(state='normal')
        self.log_box.delete(1.0, tk.END)
        for ts, txt in self.tweet_log:
            self.log_box.insert(tk.END, f"[{ts}]\n{txt}\n\n")
        self.log_box.config(state='disabled')

    def _process_queue(self):
        try:
            while True:
                msg_type, data = self.queue.get_nowait()
                if msg_type == "tweet_success":
                    self.add_tweet(data['timestamp'], data['text'])
                elif msg_type == "tweet_error":
                    messagebox.showerror("Error", f"Failed to send tweet: {data}")
        except queue.Empty:
            pass
        self.after(100, self._process_queue)

    def on_close(self):
        self.destroy()

    def force_start_timer(self, seconds=3600):
        """Force the countdown timer to start/reset from outside the dashboard."""
        self.next_tweet_seconds = seconds
        self._timer_running = True
        self._update_timer()

    def _on_stop_bot(self):
        import threading
        from tkinter import messagebox
        if messagebox.askokcancel("Stop Bot", "Are you sure you want to stop the bot?"):
            msg = "Bot manually stopped by user. Closing in 10 seconds..."
            print(msg)
            self.stop_msg_label.config(text=msg)
            def do_exit():
                self.destroy()
                sys.exit(0)
            threading.Timer(10, do_exit).start() 