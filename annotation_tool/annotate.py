#! /usr/bin/env python3
# coding: utf-8

import logging
import pathlib
import glob

import tkinter as tk
from tkinter import PhotoImage, Label, Button, Entry, filedialog, LEFT
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

    input_folder = None
    output_folder = None
    img_list = []
    img_index = 0
    img_label = None

    select_value_make = None
    select_value_model = None
    select_value_year = None
    select_value_inout = None
    select_value_newold = None
    select_value_prepost = None

    dataframe = pd.DataFrame(
        columns=["make", "model", "year", "inout", "newold", "prepost", "oldname", "newname"]
    )

    checkbox_values = {}
    checkbox_coords = (
        (145, 12),
        (145, 30),
        (145, 80),
        (145, 150),
        (60, 100),
        (225, 100),
        (15, 120),
        (265, 120),
        (145, 260),
        (15, 260),
        (270, 260),
        (15, 440),
        (270, 440),
        (145, 515),
        (60, 55),
        (225, 55),
        (80, 490),
        (205, 490),
        (40, 220),
        (245, 220),
        (40, 300),
        (245, 300),
        (60, 390),
        (225, 390),
        (145, 420),
        (145, 480),
        (80, 220),
        (205, 220),
        (80, 300),
        (205, 300),
    )

    def __init__(self):
        print("Annotator initialized")

        logging.basicConfig(
            filename="annotate.log",
            level=logging.INFO,
            format="\n%(asctime)s %(message)s\n",
        )

        window.unbind("<Control-k>")

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

        # TODO here we need to make the various car section clickable so we can define which part is damaged and how severe is the damage.
        # For instance, it could be a cycle (on each section) to change a square from white (no dmg), to yellow (low dmg), to red (medium dmg), to black (strong dmg)
        image = PhotoImage(file=pathlib.Path("media", "car_schema.png"))

        label = Label(self.left_frame, image=image)
        label.image = image
        label.grid(column=0, row=0)

        for i, (x, y) in enumerate(self.checkbox_coords):
            self.checkbox_values[i] = tk.IntVar()
            tk.Checkbutton(
                self.left_frame,
                text=i + 1,
                variable=self.checkbox_values[i],
                onvalue=1,
                offvalue=0,
                # command=self.checkit,
            ).place(x=x, y=y, anchor="nw")

    # def checkit(self):
    #    print("checkit:", self.checkbox_values[1].get())

    def display_current_car(self):

        # Check if the picture is already in the annotation's dataframe
        filename = pathlib.Path(self.img_list[self.img_index]).stem
        if (
            filename in self.dataframe.oldname.values
            or filename in self.dataframe.newname.values
        ):
            self.get_next_car()
            return None

        # Otherwise...
        img_src = Image.open(self.img_list[self.img_index])
        h, w = img_src.size
        max_size = self.img_frame.winfo_height()
        max_v = max(h, w, max_size)
        ratio = max_size / max_v

        img_resized = img_src.resize((int(h * ratio), int(w * ratio)), Image.LANCZOS)
        img_display = ImageTk.PhotoImage(img_resized)

        self.clear_frame(self.img_frame)

        self.img_label = Label(self.img_frame, image=img_display)
        self.img_label.image = img_display
        self.img_label.pack(fill="both", expand=True, side="top")

        self.display_schema()
        self.display_form()

    def display_form(self):

        pX, pY = 0, 0

        self.clear_frame(self.form_frame)

        # BRAND_SELECT
        # TODO we need to load the brands from an external file (xml ?)
        self.select_value_make = self.create_select(
            "The make of the car:",
            (
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
                "<Unknown>",
            ),
            pX=pX,
            pY=pY + 1,
            current_index=0,
        )

        # MODEL_SELECT
        # TODO we need to load the modes from an external file (xml ?)
        # and change it accordingly to the selected brand
        self.select_value_model = self.create_select(
            "The model of the car:",
            ("Undefined", "M1", "M2", "M3", "M4"),
            pX=pX,
            pY=pY + 2,
            current_index=0,
        )

        # YEAR SELECT
        self.select_value_year = self.create_select(
            "The year of the car:",
            ['Unknown'] + list((x for x in reversed(range(1990, 2022 + 1)))),
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
            ("Undefined", "Old", "New"),
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
        filepath = pathlib.Path(self.output_folder, filename)
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
        # TODO Collect damaged parts & severity
        print("New name & path: TODO")
        print("DONE")

        file_name = pathlib.Path(self.img_list[self.img_index]).stem

        new_entry = pd.DataFrame(
            [
                {
                    "make": self.select_value_make.get(),
                    "model": self.select_value_model.get(),
                    "year": self.select_value_year.get(),
                    "inout": self.select_value_inout.get(),
                    "newold": self.select_value_newold.get(),
                    "prepost": self.select_value_prepost.get(),
                    "oldname": file_name,
                    "newname": "TODO",
                }
            ]
        )

        self.dataframe = pd.concat([self.dataframe, new_entry])

        print("DATAFRAME:", self.dataframe)

        self.dataframe.to_csv(pathlib.Path(self.output_folder, "annotations.csv"))


# -- Initialize the main class

annotator = Annotator()

if __name__ == "__main__":
    window.mainloop()
