#! /usr/bin/env python3
# coding: utf-8

import logging
import pathlib
import glob

import tkinter as tk
from tkinter import PhotoImage, Label, Button, Entry, filedialog, LEFT
from tkinter.ttk import Combobox
from PIL import ImageTk, Image

window = tk.Tk()
window.geometry("800x600")
window.title("Annotate the cars!")


class Annotator:

    input_folder = None
    output_folder = None
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

    # --- DISPLAY FUNCTIONS

    def initialize_menu(self):

        pX, pY = 0, 11

        # Select input folder
        input_button = Button(text="Select input folder", command=self.action_select_input)
        input_button.grid(row=pY, column=pX)

        # Select ouput folder
        input_button = Button(text="Select output folder", command=self.action_select_output)
        input_button.grid(row=pY, column=pX + 1)

        # Exit the program
        exit_button = Button(text="Exit", command=window.destroy)
        exit_button.grid(row=pY, column=pX + 2)

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

    def display_current_car(self):

        pX, pY = 2, 0

        img_src = Image.open(self.img_list[self.img_index])
        img_resized = img_src.resize((300, 205), Image.LANCZOS)
        img_display = ImageTk.PhotoImage(img_resized)

        label1 = Label(image=img_display)
        label1.image = img_display
        label1.grid(column=pX, row=pY, columnspan=2, rowspan=2)
        # label1.place(x=350, y=25)

        self.display_schema()
        self.display_brand_select()
        self.display_model_select()
        self.display_inout_select()
        self.display_newold_select()
        self.display_prepost_select()
        self.display_nextpass_buttons()

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
        select.focus_set()

    def display_brand_select(self):

        # TODO we need to load the brands from an external file (xml ?)
        self.display_select("The make of the car:", ("Undefined", "Honda", "BMW", "Renaud"), pX=2, pY=3, current_index=0)

    def display_model_select(self):

        # TODO we need to load the modes from an external file (xml ?)
        # and change it accordingly to the selected brand
        self.display_select("The model of the car:", ("Undefined", "M1", "M2", "M3", "M4"), pX=2, pY=4, current_index=0)

    def display_inout_select(self):

        self.display_select("The context of the photo:", ("Outside", "Inside"), pX=2, pY=5, current_index=0)

    def display_newold_select(self):

        self.display_select("The condition of the car:", ("Undefined", "Old", "New"), pX=2, pY=6, current_index=0)

    def display_prepost_select(self):

        self.display_select("Pre-loss or post-loss:", ("post-loss", "pre-loss"), pX=2, pY=7, current_index=0)

    def display_nextpass_buttons(self):
        pX, pY = 3, 8

        # Load icons
        img_src = Image.open(pathlib.Path("media", "checkmark_button.png"))
        img_resized = img_src.resize((50, 50), Image.LANCZOS)
        self.img_checkmark = ImageTk.PhotoImage(img_resized)

        img_src = Image.open(pathlib.Path("media", "crossmark_button.png"))
        img_resized = img_src.resize((50, 50), Image.LANCZOS)
        self.img_crossmark = ImageTk.PhotoImage(img_resized)

        # Regroup buttons in the same grid cell using a frame
        f1 = tk.Frame(window)

        # Create buttons
        button_save = Button(f1, text="Save", image=self.img_checkmark, compound=LEFT, command=self.action_save)
        button_skip = Button(f1, text="Skip", image=self.img_crossmark, compound=LEFT, command=self.action_skip)

        # Position buttons into the frame
        button_save.pack(side="left")
        button_skip.pack(side="right")

        # Position the frame into the grid
        f1.grid(column=pX, row=pY)

    # --- ACTION FUNCTIONS (BUTTONS)

    def action_skip(self):
        print("SKIP")
        self.img_index += 1
        try:
            self.display_current_car()
        except IndexError:
            print("ALL IMAGES HAVE BEEN REVIEWED")

    def action_save(self):
        print("SAVE")

    def action_select_input(self):
        self.input_folder = self.select_folder(title="Select the input directory")
        logging.info(f"SOURCE FOLDER: {self.input_folder}")
        self.get_images_list()

    def action_select_output(self):
        self.output_folder = self.select_folder(title="Select the output directory")
        logging.info(f"TARGET FOLDER: {self.output_folder}")

    # --- GENERIC FUNCTIONS

    def select_folder(self, title):
        return filedialog.askdirectory(title=title)

    def get_images_list(self):

        extensions = ["jpg", "png"]

        try:
            for extension in extensions:
                images_paths = glob.glob(
                    str(pathlib.Path(self.input_folder, f"*.{extension}"))
                )
                self.img_list.extend(images_paths)
        except TypeError:
            pass

        logging.info(f"SELECTED FILES: {self.img_list}")

        if len(self.img_list) == 0:
            return

        self.display_current_car()


# -- Initialize the main class

annotator = Annotator()

if __name__ == "__main__":
    window.mainloop()
