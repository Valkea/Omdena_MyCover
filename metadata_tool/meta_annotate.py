#! /usr/bin/env python3
# coding: utf-8

import os
import re
import sys
import shutil
import logging
import pathlib
import time

# import datetime

import tkinter as tk
from tkinter import (
    PhotoImage,
    Label,
    Button,
    Entry,
    Listbox,
    Checkbutton,
    filedialog,
    LEFT,
    CENTER,
    YES,
    END,
)
from tkinter.ttk import Combobox
from PIL import ImageTk, Image

import pandas as pd

window = tk.Tk()
window.geometry("800x600")
window.minsize(800, 600)
window.title("Let's collect cars' metadatas!")

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

    reset_selectbox = tk.IntVar(value=1)

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

    makes_list = [
        "unknown",
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
        "other",
    ]
    years_list = ["unknown"] + list((x for x in reversed(range(1990, 2022 + 1))))
    inout_list = ["outside", "inside"]
    newold_list = ["old", "new", "unknown"]
    prepost_list = ["preloss", "postloss"]

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

        self.img_label_name = Label(
            self.menu_frame,
            text="No current file",  # font=("Times New Roman", 10)
        )
        self.img_label_name.place(relx=0.5, rely=0.5, anchor=CENTER)

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
        filepath = self.get_current_car_image_path()

        if filepath is None:
            self.clear_frame(self.right_frame)
            self.clear_frame(self.left_frame)
            print("OUT")
            return

        filename = filepath.stem
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

            img_resized = img_src.resize(
                (int(h * ratio), int(w * ratio)), Image.LANCZOS
            )
            img_display = ImageTk.PhotoImage(img_resized)

            self.clear_frame(self.img_frame)

            self.img_label = Label(self.img_frame, image=img_display)
            self.img_label.image = img_display
            self.img_label.pack(fill="both", expand=True, side="top")

            if refresh_img_only is False:
                print("DEBUG:", self.reset_selectbox.get())
                self.display_schema()
                self.display_form()

        except IOError:
            logging.error(
                f"The file '{filepath}' couldn't be opened (moved to skipped folder)"
            )
            self.action_skip()

    def parse_file_name(self, filename):
        print(f"parsing: {filename}")

        self.img_label_name.config(text=filename)
        r_year, r_make, r_inout, r_prepost = None, None, None, None

        for a, b in (
            ("-", ""),
            ("pre_", "pre"),
            ("post_", "post"),
            ("exterior", "outside"),
            ("interior", "inside"),
        ):
            filename = filename.replace(a, b)

        for word in filename.split("_"):
            # print("===>", word, end='')
            if bool(re.search(r"\d{4}", word)):
                # print(" ########## C'est une date")
                if 1989 < int(word) < 2050:
                    r_year = word
            elif word.upper() in self.makes_list:
                # print(" ########## C'est une marque")
                r_make = word.upper()
            elif word.lower() in self.inout_list:
                # print(" ########## C'est un inout")
                r_inout = word.lower()
            elif word.lower() in self.prepost_list:
                # print(" ########## C'est un prepost")
                r_prepost = word.lower()
            # else:
            #    print('')

        return r_year, r_make, r_inout, r_prepost

    def display_form(self):

        pX, pY = 0, 0
        make, model, year, inout, newold, prepost = None, None, None, None, None, None

        # Search infos in the file name
        filename = self.get_current_car_image_path().stem
        year, make, inout, prepost = self.parse_file_name(filename)

        # Use previous values as default values of the select boxes
        if self.reset_selectbox.get() == 1 and len(self.dataframe) > 0:
            last_row = self.dataframe.iloc[-1]

            if make is None:
                make = last_row["make"]

            if model is None:
                model = last_row["model"]

            if year is None:
                year = last_row["year"]

            if inout is None:
                inout = last_row["inout"]

            if newold is None:
                newold = last_row["newold"]

            if prepost is None:
                prepost = last_row["prepost"]

        # Clear the form to remove old information
        self.clear_frame(self.form_frame)

        # BRAND_SELECT
        makes_list = self.makes_list
        if make is not None:
            makes_list = [make] + makes_list
            makes_list = list(dict.fromkeys(makes_list))  # remove duplicates & keep order

        try:
            make_index = makes_list.index(make)
        except Exception:
            make_index = 0

        self.select_value_make = self.create_select(
            "Make of the car:", makes_list, pX=pX, pY=pY + 1, current_index=make_index
        )

        # MODEL_SELECT
        model_list = ["Write the model name", "unknown"]
        if model is not None:
            model_list = [model] + model_list
            model_list = list(dict.fromkeys(model_list))  # remove duplicates & keep order

        try:
            model_index = model_list.index(model)
        except Exception:
            model_index = 0

        self.select_value_model = self.create_select(
            "Model of the car:",
            model_list,
            pX=pX,
            pY=pY + 2,
            current_index=model_index,
        )

        # YEAR SELECT
        try:
            year_index = self.years_list.index(int(year))
        except Exception:
            year_index = 0

        self.select_value_year = self.create_select(
            "Year of the car:",
            self.years_list,
            pX=pX,
            pY=pY + 3,
            state="readonly",
            current_index=year_index,
        )

        # INOUT_SELECT
        try:
            inout_index = self.inout_list.index(inout)
        except Exception:
            inout_index = 0

        self.select_value_inout = self.create_select(
            "Context of the photo:",
            self.inout_list,
            pX=pX,
            pY=pY + 4,
            state="readonly",
            current_index=inout_index,
        )

        # NEWOLD_SELECT
        try:
            newold_index = self.newold_list.index(newold)
        except Exception:
            newold_index = 0

        self.select_value_newold = self.create_select(
            "Condition of the car:",
            self.newold_list,
            pX=pX,
            pY=pY + 5,
            state="readonly",
            current_index=newold_index,
        )

        # PREPOST_SELECT
        try:
            prepost_index = self.prepost_list.index(prepost)
        except Exception:
            prepost_index = 0

        self.select_value_prepost = self.create_select(
            "Pre-loss or post-loss:",
            self.prepost_list,
            pX=pX,
            pY=pY + 6,
            state="readonly",
            current_index=prepost_index,
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

        Button(
            self.buttons_frame,
            text="Save",
            image=self.img_checkmark,
            compound=LEFT,
            command=self.action_save,
        ).pack(side="left")

        Button(
            self.buttons_frame,
            text="Skip (CTRL+K)",
            image=self.img_crossmark,
            compound=LEFT,
            command=self.action_skip,
        ).pack(side="left")

        Checkbutton(
            self.buttons_frame,
            # text="Keep select\nboxes' values on\nthe next car.",
            text="Keep current\nselect values\non next car.",
            variable=self.reset_selectbox,
            onvalue=1,
            offvalue=0,
            # command=print_selection
        ).pack(side="left")

        # Add keyboard bindings
        window.bind("<Control-k>", self.action_skip)

    # --- ACTION FUNCTIONS (BUTTONS)

    def action_skip(self, key=None):

        old_file_path = self.get_current_car_image_path()
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

    def get_current_car_image_path(self):
        try:
            return pathlib.Path(self.img_list[self.img_index])
        except IndexError:
            print("ALL IMAGES HAVE BEEN REVIEWED")
            return None

    def create_select(self, label_txt, values, pX, pY, state=None, current_index=0):

        # label
        label = Label(
            self.form_frame,
            text=label_txt,  # font=("Times New Roman", 10)
        )
        label.grid(column=pX, row=pY, padx=10, pady=5)

        # Combobox creation
        n = tk.StringVar()
        select = Combobox(self.form_frame, width=27, textvariable=n, state=state)

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
        print(f"Image path: {str(self.get_current_car_image_path())}")
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

        if self.select_value_model.get() == "Write the model name":
            self.select_value_model.set("unknown")

        v_make = self.select_value_make.get()
        v_model = self.select_value_model.get()
        v_year = self.select_value_year.get()
        v_inout = self.select_value_inout.get()
        v_newold = self.select_value_newold.get()
        v_prepost = self.select_value_prepost.get()

        old_file_path = pathlib.Path(str(self.get_current_car_image_path()))
        old_file_name = f"{old_file_path.stem}.{old_file_path.suffix}"
        # [your name]_[make-model]_[other_attributes]_[exterior/interior]_[number]_[pre-loss/post-loss]
        uniqueid = int(time.mktime(time.localtime()))
        new_file_name = f"{self.username}_{v_make}_{v_model}_{v_year}_{v_newold}_{v_prepost}_{uniqueid}{old_file_path.suffix}"
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
