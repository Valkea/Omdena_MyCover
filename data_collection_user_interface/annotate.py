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

        self.initialize_menu()

    def initialize_menu(self):

        pX, pY = 0, 11

        # Select input folder
        input_button = Button(text="Select input folder", command=self.select_folder)
        input_button.grid(row=pY, column=pX)

        # Select ouput folder
        input_button = Button(text="Select output folder", command=self.select_folder)
        input_button.grid(row=pY, column=pX + 1)

        # Exit the program
        exit_button = Button(text="Exit Game", command=window.destroy)
        exit_button.grid(row=pY, column=pX + 2)

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

        if len(self.img_list) == 0:
            return

        self.display_schema()
        self.display_current_car(car_index=0)
        self.display_brand_select()
        self.display_model_select()
        self.display_inout_select()
        self.display_newold_select()

    def display_schema(self):

        image = PhotoImage(file=pathlib.Path("media", "car_schema.png"))

        label = Label(image=image)
        label.image = image
        label.grid(column=0, row=0, rowspan=10, columnspan=2)
        # btn_nr = -1
        # btns = []
        # btns.append(Button(window, image=image, command=lambda: self.click_part))

        # btn_nr = 0
        # btns[btn_nr].grid(row=1, column=btn_nr)
        # btns[btn_nr].img = image  # keep a reference so it's not garbage collected

    def display_current_car(self, car_index):

        pX, pY = 2, 0

        img_src = Image.open(self.img_list[car_index])
        img_resized = img_src.resize((300, 205), Image.LANCZOS)
        img_display = ImageTk.PhotoImage(img_resized)

        label1 = Label(image=img_display)
        label1.image = img_display
        label1.grid(column=pX, row=pY, columnspan=2, rowspan=2)
        # label1.place(x=350, y=25)

    def display_select(self, label_txt, values, pX, pY, current_index=0):

        # label
        label = Label(
            window, text=label_txt, font=("Times New Roman", 10)
        )
        label.grid(column=pX, row=pY, padx=10, pady=5)

        # Combobox creation
        n = tk.StringVar()
        select = Combobox(window, width=27, textvariable=n)

        # Adding combobox drop down list
        select["values"] = values
        select.grid(column=pX + 1, row=pY)
        select.current(current_index)

    def display_brand_select(self):

        self.display_select("Select the car brand:", ("Undefined", "Honda", "BMW", "Renaud"), pX=2, pY=3, current_index=0)

        # pX, pY = 1, 3

        # # label
        # label = Label(
        #     window, text="Select the car brand:", font=("Times New Roman", 10)
        # )
        # label.grid(column=pX, row=pY, padx=10, pady=5)

        # # Combobox creation
        # n1 = tk.StringVar()
        # select_maker = Combobox(window, width=27, textvariable=n1)

        # # Adding combobox drop down list
        # select_maker["values"] = ("Undefined", "Honda", "BMW", "Renaud")
        # select_maker.grid(column=pX + 1, row=pY)
        # select_maker.current(0)

    def display_model_select(self):

        self.display_select("Select the car model:", ("Undefined", "M1", "M2", "M3", "M4"), pX=2, pY=4, current_index=0)

        # pX, pY = 1, 4

        # # label
        # label = Label(
        #     window, text="Select the car model:", font=("Times New Roman", 10)
        # )
        # label.grid(column=pX, row=pY, padx=10, pady=5)

        # # Combobox creation
        # n2 = tk.StringVar()
        # select_model = Combobox(window, width=27, textvariable=n2)

        # # Adding combobox drop down list
        # select_model["values"] = ("Undefined", "M1", "M2", "M3")
        # select_model.grid(column=pX + 1, row=pY)
        # select_model.current(0)

    def display_inout_select(self):

        self.display_select("Select the photo model:", ("Outside", "Inside"), pX=2, pY=5, current_index=0)

        # pX, pY = 1, 5

        # # label
        # label = Label(
        #     window, text="Select the photo type", font=("Times New Roman", 10)
        # )
        # label.grid(column=pX, row=pY, padx=10, pady=5)

        # # Combobox creation
        # n3 = tk.StringVar()
        # select_inout = Combobox(window, width=27, textvariable=n3)

        # # Adding combobox drop down list
        # select_inout["values"] = ("Outside", "Inside")
        # select_inout.grid(column=pX + 1, row=pY)
        # select_inout.current(0)

    def display_newold_select(self):

        self.display_select("Select the car's condition:", ("Undefined", "Old", "New"), pX=2, pY=6, current_index=0)

        # pX, pY = 1, 6

        # # label
        # label = Label(
        #     window, text="Select the car's condition", font=("Times New Roman", 10)
        # )
        # label.grid(column=pX, row=pY, padx=10, pady=5)

        # # Combobox creation
        # n3 = tk.StringVar()
        # select_newold = Combobox(window, width=27, textvariable=n3)

        # # Adding combobox drop down list
        # select_newold["values"] = ("Undefined", "New", "Old")
        # select_newold.grid(column=pX + 1, row=pY)
        # select_newold.current(0)


# -- Initialize the main class

annotator = Annotator()

if __name__ == "__main__":
    window.mainloop()
