import tkinter as tk
from tkinter import ttk


class NewsFeed:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)

        # News feed title
        news_label = ttk.Label(self.frame, text="Market News", font=("", 11, "bold"))
        news_label.pack(fill=tk.X, padx=5, pady=5)

        # News feed list
        self.news_frame = ttk.Frame(self.frame)
        self.news_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.news_list = tk.Listbox(self.news_frame, height=10, width=50)
        self.news_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.news_frame, orient=tk.VERTICAL, command=self.news_list.yview)
        self.news_list.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def update(self, news_feed):
        self.news_list.delete(0, tk.END)

        # Insert news items in reverse order (newest first)
        for news_item in news_feed:
            self.news_list.insert(0, news_item)

    def get_frame(self):
        return self.frame
