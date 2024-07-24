import tkinter as tk
import subprocess
import threading

# An example function to run a command and display its output in a text widget

def run_command(command, text_widget):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        output = process.stdout.readline().decode('utf-8')
        if output == '' and process.poll() is not None:
            break
        if output:
            text_widget.insert(tk.END, output)
    process.wait()

def start_command():
    command = "your_command_here"  # 将这里替换为您要运行的实际命令
    threading.Thread(target=run_command, args=(command, text_widget)).start()

root = tk.Tk()

text_widget = tk.Text(root)
text_widget.pack()

button = tk.Button(root, text="Run Command", command=start_command)
button.pack()

root.mainloop()