# Basic functions and methods for the GUI generations.

import tkinter as tk

class drawGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Chips Battle : Stock Market Simulator")
        self.label = tk.Label(self.master, text="Hello, Tkinter!")
        self.label.pack()
        self.button = tk.Button(self.master, text="Quit", command=self.master.quit)
        self.button.pack()

    def run(self):
        self.master.mainloop()

