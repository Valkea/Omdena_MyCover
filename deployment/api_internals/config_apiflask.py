from apiflask import APIFlask, Schema
from apiflask.fields import Integer, String, File, List, Nested, Boolean
from apiflask.validators import Length


# --- Define input and outputs for APIFlask documentation ---


class DamagesIn(Schema):
    file = File(required=True)
    trade = String(required=False)
    model = String(required=False)
    year = String(required=False)


class PlatesIn(Schema):
    file = File(required=True)


damage_sample = [
    {
        "action": "REPLACE",
        "type": "headlight_damage",
        "coords": [420.0, 206.0, 552.0, 294.0],
        "severity": "0.5441662",
        "severity_model": "severity_model_001.onnx",
        "price": "111$",
        "file": "my_photo.jpg",
        "probable_duplicate": False,
    },
]

plate_sample = [
    {
        "coords": [294.0, 215.0, 440.0, 262.0],
        "text": "NDC 6300",
        "invalid": ["LAGOS (50.00%)", "Center of excellence (12.00%)"],
        "file": "my_photo.jpg",
    }
]


class DamagesOut(Schema):
    type = String()
    coords = List(Integer(), many=True, validate=Length(4, 4))
    severity = String()
    severity_model = String()
    action = String()
    price = String()
    file = String()
    probable_duplicate = Boolean()


class DamagesFullOut(Schema):
    damage_model = String(load_default="car_damage_detect.pt")
    damages = List(Nested(DamagesOut), load_default=damage_sample)


class PlatesOut(Schema):
    coords = List(Integer(), many=True, validate=Length(4, 4))
    text = String()
    invalid = List(String())
    file = String()


class PlatesFullOut(Schema):
    plate_model = String(load_default="car_damage_detect.pt")
    plates = List(Nested(PlatesOut), load_default=plate_sample)
