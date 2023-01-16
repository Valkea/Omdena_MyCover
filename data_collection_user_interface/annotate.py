#! /usr/bin/env python3
# coding: utf-8

import logging
import pathlib
import glob

import tkinter as tk
from tkinter import PhotoImage, Label, Button, Entry, filedialog
from tkinter.ttk import Combobox
from PIL import ImageTk, Image

window = tk.Tk()
window.geometry("800x600")
window.title("Annotate the cars!")


class Annotator:

    input_folder = None
    img_list = []
    img_index = 0

    def __init__(self):
        print("Annotator initialized")
        logging.basicConfig(
            filename="annotate.log",
            level=logging.INFO,
            format="\n%(asctime)s %(message)s\n",
        )
        self.display_schema()
        self.display_make()

    def select_folder(self):
        self.input_folder = filedialog.askdirectory(title="Select the target directory")
        logging.info(f"SOURCE FOLDER: {self.input_folder}")

        self.get_images_list()

    def get_images_list(self):
        extensions = ["jpg", "png"]

        for extension in extensions:
            images_paths = glob.glob(
                str(pathlib.Path(self.input_folder, f"*.{extension}"))
            )
            self.img_list.extend(images_paths)

        logging.info(f"SELECTED FILES: {self.img_list}")

        self.display_current_car(car_index=0)

    def display_current_car(self, car_index):
        img_src = Image.open(self.img_list[car_index])
        img_resized = img_src.resize((300, 205), Image.LANCZOS)
        img_display = ImageTk.PhotoImage(img_resized)

        label1 = Label(image=img_display)
        label1.image = img_display

        # Position image
        # label1.place(x=350, y=25)
        label1.grid(column=1, row=0, columnspan=2)

    def click_part(self):
        print("click_part")

    def display_schema(self):
        image = PhotoImage(file=pathlib.Path("media", "car_schema.png"))

        label = Label(image=image)
        label.image = image
        label.grid(column=0, row=0, rowspan=5)
        # btn_nr = -1
        # btns = []
        # btns.append(Button(window, image=image, command=lambda: self.click_part))

        # btn_nr = 0
        # btns[btn_nr].grid(row=1, column=btn_nr)
        # btns[btn_nr].img = image  # keep a reference so it's not garbage collected

    def display_make(self):
        # label
        label = Label(window, text="Select the Month :", font=("Times New Roman", 10))
        label.grid(column=1, row=3, padx=10, pady=25)

        # Combobox creation
        n = tk.StringVar()
        monthchoosen = Combobox(window, width=27, textvariable=n)

        # Adding combobox drop down list
        monthchoosen["values"] = (" January", " February", " December")
        monthchoosen.grid(column=2, row=3)
        monthchoosen.current()


annotator = Annotator()

input_button = Button(text="Select", command=annotator.select_folder)
input_button.grid(row=6, column=0, columnspan=5)

# Affichage d'un bouton exit
exit_button = Button(text="Exit Game", command=window.destroy)
exit_button.grid(row=6, column=1, columnspan=5)

if __name__ == "__main__":
    window.mainloop()
