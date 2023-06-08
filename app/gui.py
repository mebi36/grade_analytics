from pathlib import Path
import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

import result_file_io


BASE_DIR = Path(__file__).parent.parent
config_path = os.path.join(BASE_DIR, "config.txt")


def browse_files():
    with open(config_path) as config:
        last_path = config.readline() or BASE_DIR

    filenames = filedialog.askopenfilenames(
        initialdir=last_path,
        title="Select result file",
        filetypes=(
            ("xlsx files", "*.xlsx"),
            ("Text files",  "*.csv"),
        )
    )
    with open(config_path, "w") as config:
        config.write(Path(filenames[0]).parent.__str__())

    label_file_explorer.configure(text="File Opened: "+'\n'.join(filenames))

    # for filename in filenames:
    #     file_con = result_file_io.read_file(filename)
    #     result_file_io.process_result_file_content(file_con)
    result_file_io.generate_analytics(filenames)

window = Tk()

window.title("Grade Analytics")

window.geometry("500x500")

label_file_explorer = Label(
    window, text="File Explorer using Tkinter", width=100, height=4, fg="blue"
)

button_explore = Button(
    window, text="Select Result File", command=browse_files)

button_exit = Button(window, text="Exit", command=exit)

label_file_explorer.grid(column=1, row=1)

button_explore.grid(column=1, row=2)

button_exit.grid(column=1, row=3)

window.mainloop()
