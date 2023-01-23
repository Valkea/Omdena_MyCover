#! /usr/bin/env python3
# coding: utf-8

import os
import sys
import shutil
import logging
import pathlib

import tkinter as tk
from tkinter import (
    PhotoImage,
    Label,
    Button,
    Entry,
    Listbox,
    filedialog,
    LEFT,
    YES,
    END,
)
from tkinter.ttk import Combobox
from PIL import ImageTk, Image

import pandas as pd

window = tk.Tk()
window.geometry("800x600")
window.minsize(800, 600)
window.title("Annotate the cars!")

ico = Image.open(pathlib.Path("media", "icon.ico"))
photo = ImageTk.PhotoImage(ico)
window.wm_iconphoto(False, photo)


# Specify Grid
# Grid.rowconfigure(window, 0, weight=1)
# Grid.columnconfigure(window, 0, weight=1)
#
# Grid.rowconfigure(window, 1, weight=1)
# Grid.columnconfigure(window, 1, weight=1)


class Annotator:

    username = "Undefined"

    output_folder = None
    output_selected_folder = "selected"
    output_skipped_folder = "skipped"
    input_folder = None

    img_list = []
    img_index = 0
    img_label = None
    window_height = 600

    select_value_make = None
    select_value_model = None
    select_value_year = None
    select_value_inout = None
    select_value_newold = None
    select_value_prepost = None

    dataframe = pd.DataFrame(
        columns=[
            "make",
            "model",
            "year",
            "inout",
            "newold",
            "prepost",
            "damage_front",
            "damage_rear",
            "damage_side",
            "oldname",
            "newname",
        ]
    )

    def __init__(self):
        print("Annotator initialized")

        logging.basicConfig(
            filename="annotate.log",
            level=logging.INFO,
            format="\n%(asctime)s %(message)s\n",
        )

        window.unbind("<Control-k>")
        window.unbind("<Configure>")

        self.initialize_frames()
        self.initialize_menu()

    def initialize_frames(self):

        self.menu_frame = tk.Frame(
            window, width=800, height=50, bg="lightgrey", padx=10, pady=5
        )
        self.menu_frame.pack(fill="x", expand=False, side="bottom")

        self.left_frame = tk.Frame(
            window, width=200, height=550, bg="orange", padx=10, pady=5
        )
        self.left_frame.pack(fill="y", expand=False, side="left")

        self.right_frame = tk.Frame(
            window, width=580, height=550, bg="grey", padx=10, pady=5
        )
        self.right_frame.pack(fill="both", expand=True, side="left")

        self.img_frame = tk.Frame(self.right_frame, bg="lightgrey", padx=10, pady=5)
        self.img_frame.pack(fill="both", expand=True, side="top")

        self.form_frame = tk.Frame(self.right_frame, bg="lightgrey", padx=10, pady=5)
        self.form_frame.pack(fill="x", expand=False, side="top")

        self.buttons_frame = tk.Frame(self.right_frame, bg="lightgrey", padx=10, pady=5)
        self.buttons_frame.pack(fill="x", expand=False, side="top")

    def initialize_menu(self):

        Button(
            self.menu_frame,
            text="Select input folder",
            command=self.action_select_input,
        ).pack(side="left")

        # Button(
        #     self.menu_frame,
        #     text="Select output folder",
        #     command=self.action_select_output,
        # ).pack(side="left")

        Button(self.menu_frame, text="Exit", command=window.destroy).pack(side="right")

    # --- DISPLAY FUNCTIONS

    def display_schema(self):

        image = PhotoImage(file=pathlib.Path("media", "car_schema.png"))

        label = Label(self.left_frame, image=image)
        label.image = image
        label.grid(column=0, row=0)

        damage_types = [
            "dent",
            "scratch",
            "crack/hole",
            "corrosion/rust",
            "paint crack/peel",
            "glass shatter",
            "tire flat",
            "lamp broken",
            "side mirror damage",
        ]

        self.front_damage_list = Listbox(
            self.left_frame, selectmode="multiple", height=len(damage_types), width=18
        )
        self.front_damage_list.configure(exportselection=False)

        self.rear_damage_list = Listbox(
            self.left_frame, selectmode="multiple", height=len(damage_types), width=18
        )
        self.rear_damage_list.configure(exportselection=False)

        self.side_damage_list = Listbox(
            self.left_frame, selectmode="multiple", height=len(damage_types), width=18
        )
        self.side_damage_list.configure(exportselection=False)

        for dmg_index in range(len(damage_types)):
            self.front_damage_list.insert(END, damage_types[dmg_index])
            self.rear_damage_list.insert(END, damage_types[dmg_index])
            self.side_damage_list.insert(END, damage_types[dmg_index])
            # coloring alternative lines of listbox
            # damage_list.itemconfig(dmg_index, bg="orange" if dmg_index % 2 == 0 else "yellow")

        b1 = Button(
            self.left_frame,
            text="Front damages",
            command=lambda: self.display_damage_choices(
                self.front_damage_list, b1, 32, 75
            ),
        )
        b1.place(x=95, y=75, anchor="nw")

        b2 = Button(
            self.left_frame,
            text="Side damages",
            command=lambda: self.display_damage_choices(
                self.side_damage_list, b2, 207, 250
            ),
        )
        b2.place(x=95, y=250, anchor="nw")

        b3 = Button(
            self.left_frame,
            text="Rear damages",
            command=lambda: self.display_damage_choices(
                self.rear_damage_list, b3, 382, 420
            ),
        )
        b3.place(x=95, y=420, anchor="nw")

    def display_damage_choices(self, target, button, ylist, ybtn):
        if target.winfo_ismapped():
            button.place(x=95, y=ybtn, anchor="nw")
            target.place_forget()
        else:
            button.place_forget()
            target.place(x=83, y=ylist, anchor="nw")

    def display_current_car(self, refresh_img_only=False):

        # Check if the picture is already in the annotation's dataframe
        filepath = self.img_list[self.img_index]
        filename = pathlib.Path(filepath).stem
        if (
            filename in self.dataframe.oldname.values
            or filename in self.dataframe.newname.values
        ):
            self.get_next_car()
            return None

        # Otherwise...
        try:
            img_src = Image.open(filepath)
            h, w = img_src.size
            max_size = self.right_frame.winfo_height() - 200
            max_v = max(h, w, max_size)
            ratio = max_size / max_v

            img_resized = img_src.resize((int(h * ratio), int(w * ratio)), Image.LANCZOS)
            img_display = ImageTk.PhotoImage(img_resized)

            self.clear_frame(self.img_frame)

            self.img_label = Label(self.img_frame, image=img_display)
            self.img_label.image = img_display
            self.img_label.pack(fill="both", expand=True, side="top")

            if refresh_img_only is False:
                self.display_schema()
                self.display_form()

        except IOError:
            logging.error(f"The file '{filepath}' couldn't be opened (moved to skipped folder)")
            self.action_skip()

    def display_form(self):

        pX, pY = 0, 0

        self.clear_frame(self.form_frame)

        # BRAND_SELECT
        # TODO we need to load the brands from an external file (xml ?)
        makes_list = (
            "<Unknown>",
            "BMW",
            "CHANGAN",
            "CHEVROLET",
            "FIAT",
            "HONDA",
            "LEXUS",
            "HYUNDAI",
            "INNOSON",
            "KIA",
            "LAND ROVER",
            "MAZDA",
            "MERCEDEZ BENZ",
            "MITSUBISHI",
            "NISSAN",
            "PEUGEOT",
            "RENAULT",
            "TESLA",
            "TOYOTA",
            "VOLKSWAGEN",
            "<Other>",
        )

        self.select_value_make = self.create_select(
            "The make of the car:",
            makes_list,
            pX=pX,
            pY=pY + 1,
            current_index=0,
        )

        # MODEL_SELECT
        # TODO we need to load the modes from an external file (xml ?)
        # and change it accordingly to the selected brand
        self.select_value_model = self.create_select(
            "The model of the car:",
            ("<Unknown>", "M1", "M2", "M3", "M4"),
            pX=pX,
            pY=pY + 2,
            current_index=0,
        )

        # YEAR SELECT
        self.select_value_year = self.create_select(
            "The year of the car:",
            ["<Unknown>"] + list((x for x in reversed(range(1990, 2022 + 1)))),
            pX=pX,
            pY=pY + 3,
            current_index=0,
        )

        # INOUT_SELECT
        self.select_value_inout = self.create_select(
            "The context of the photo:",
            ("Outside", "Inside"),
            pX=pX,
            pY=pY + 4,
            current_index=0,
        )

        # NEWOLD_SELECT
        self.select_value_newold = self.create_select(
            "The condition of the car:",
            ("Old", "New", "<Unknown>"),
            pX=pX,
            pY=pY + 5,
            current_index=0,
        )

        # PREPOST_SELECT
        self.select_value_prepost = self.create_select(
            "Pre-loss or post-loss:",
            ("post-loss", "pre-loss"),
            pX=pX,
            pY=pY + 6,
            current_index=0,
        )

        self.display_nextpass_buttons()

    def display_nextpass_buttons(self):

        # Load icons
        img_src = Image.open(pathlib.Path("media", "checkmark_button.png"))
        img_resized = img_src.resize((50, 50), Image.LANCZOS)
        self.img_checkmark = ImageTk.PhotoImage(img_resized)

        img_src = Image.open(pathlib.Path("media", "crossmark_button.png"))
        img_resized = img_src.resize((50, 50), Image.LANCZOS)
        self.img_crossmark = ImageTk.PhotoImage(img_resized)

        # Create buttons
        self.clear_frame(self.buttons_frame)

        button_save = Button(
            self.buttons_frame,
            text="Save",
            image=self.img_checkmark,
            compound=LEFT,
            command=self.action_save,
        )
        button_skip = Button(
            self.buttons_frame,
            text="Skip (CTRL+K)",
            image=self.img_crossmark,
            compound=LEFT,
            command=self.action_skip,
        )

        # Position buttons into the frame
        button_save.pack(side="left")
        button_skip.pack(side="left")

        # Add keyboard bindings
        window.bind("<Control-k>", self.action_skip)

    # --- ACTION FUNCTIONS (BUTTONS)

    def action_skip(self, key=None):

        old_file_path = pathlib.Path(self.img_list[self.img_index])
        old_file_name = f"{old_file_path.stem}{old_file_path.suffix}"
        new_file_path = pathlib.Path(
            self.output_folder, self.output_skipped_folder, old_file_name
        )

        self.move_file(old_file_path, new_file_path)

        self.get_next_car()

    def action_save(self):
        try:
            self.collect_car_inputs()
            print("NEXT CAR")
            self.get_next_car()
        except Exception as e:
            logging.error(f"An error occured while collecting the data: {e}")

    def action_select_input(self):
        self.input_folder = self.select_folder(title="Select the input directory")
        self.output_folder = self.input_folder
        logging.info(f"SOURCE FOLDER: {self.input_folder}")
        self.load_previous_dataframe()
        self.get_images_list()

    def action_select_output(self):
        self.output_folder = self.select_folder(title="Select the output directory")
        logging.info(f"TARGET FOLDER: {self.output_folder}")
        self.load_previous_dataframe()

    # --- GENERIC FUNCTIONS

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def create_select(self, label_txt, values, pX, pY, current_index=0):

        # label
        label = Label(
            self.form_frame,
            text=label_txt,  # font=("Times New Roman", 10)
        )
        label.grid(column=pX, row=pY, padx=10, pady=5)

        # Combobox creation
        n = tk.StringVar()
        select = Combobox(self.form_frame, width=27, textvariable=n)

        # Adding combobox drop down list
        select["values"] = values
        select.grid(column=pX + 1, row=pY)
        select.current(current_index)

        select.focus_set()  # automatically refocus the first selectbox when changing the image

        return n

    def load_previous_dataframe(self):
        filename = "annotations.csv"
        filepath = pathlib.Path(
            self.output_folder, self.output_selected_folder, filename
        )
        if filepath.exists():
            print("Load_previous_dataframe")
            self.dataframe = pd.read_csv(filepath)

    def get_next_car(self):
        try:
            self.img_index += 1
            self.display_current_car()
        except IndexError:
            logging.info("ALL IMAGES HAVE BEEN REVIEWED")

    def select_folder(self, title):
        return filedialog.askdirectory(title=title)

    def get_images_list(self):

        try:
            images_paths = pathlib.Path(self.input_folder).glob("*.*")
            self.img_list.extend(images_paths)
        except TypeError:
            pass

        logging.info(f"SELECTED FILES: {self.img_list}")

        if len(self.img_list) == 0:
            return

        self.display_current_car()

        # Bind resize
        window.bind("<Configure>", self.resize)

    def resize(self, event):

        if self.right_frame.winfo_height() != self.window_height:
            self.window_height = self.right_frame.winfo_height()
            self.display_current_car(True)

    def collect_car_inputs(self):

        # TODO here we need to save the data in a dataframe and export it as a CSV
        # we also need to save the input image as a new image in the output folder with the right naming convention
        print("COLLECT DATA")
        print(f"Image path: {self.img_list[self.img_index]}")
        print(f"Make: {self.select_value_make.get()}")
        print(f"Model: {self.select_value_model.get()}")
        print(f"Inside/Outisde: {self.select_value_inout.get()}")
        print(f"New/Old: {self.select_value_newold.get()}")
        print(f"Pre/post-loss: {self.select_value_prepost.get()}")
        print(f"Front damages: {self.front_damage_list.curselection()}")
        print(f"Rear damages: {self.rear_damage_list.curselection()}")
        print(f"Side damages: {self.side_damage_list.curselection()}")

        # TODO Collect damaged parts & severity
        print("New name & path: TODO")
        print("DONE")

        v_make = self.select_value_make.get()
        v_model = self.select_value_model.get()
        v_year = self.select_value_year.get()
        v_inout = self.select_value_inout.get()
        v_newold = self.select_value_newold.get()
        v_prepost = self.select_value_prepost.get()

        old_file_path = pathlib.Path(self.img_list[self.img_index])
        old_file_name = f"{old_file_path.stem}.{old_file_path.suffix}"
        # [your name]_[make-model]_[other_attributes]_[exterior/interior]_[number]_[pre-loss/post-loss]
        new_file_name = f"{self.username}_{v_make}_{v_model}_{v_year}_{v_newold}_{v_prepost}{old_file_path.suffix}"
        new_file_path = pathlib.Path(
            self.output_folder, self.output_selected_folder, new_file_name
        )

        # Move file to 'selected' folder
        self.move_file(old_file_path, new_file_path)

        # Add entry to the dataframe
        new_entry = pd.DataFrame(
            [
                {
                    "make": v_make,
                    "model": v_model,
                    "year": v_year,
                    "inout": v_inout,
                    "newold": v_newold,
                    "prepost": v_prepost,
                    "damage_front": self.front_damage_list.curselection(),
                    "damage_rear": self.rear_damage_list.curselection(),
                    "damage_side": self.side_damage_list.curselection(),
                    "oldname": old_file_name,
                    "newname": new_file_name,
                }
            ]
        )

        self.dataframe = pd.concat([self.dataframe, new_entry])
        self.dataframe.to_csv(
            pathlib.Path(
                self.output_folder, self.output_selected_folder, "annotations.csv"
            ),
            index=False,
        )

        print("DATAFRAME:", self.dataframe)

    def move_file(self, old_path, new_path):

        selected_path = pathlib.Path(self.output_folder, self.output_selected_folder)
        skipped_path = pathlib.Path(self.output_folder, self.output_skipped_folder)

        if not os.path.exists(selected_path):
            os.mkdir(selected_path)

        if not os.path.exists(skipped_path):
            os.mkdir(skipped_path)

        shutil.move(old_path, new_path)


# -- Initialize the main class

annotator = Annotator()

if __name__ == "__main__":

    try:
        annotator.username = sys.argv[1]
        print(f"Starting session for {annotator.username}")

        window.mainloop()

    except Exception:
        print(
            " please pass your name as first argument ==> python annotate.py 'Letremble Emmanuel'"
        )
