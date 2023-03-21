import os
from flask_sqlalchemy import SQLAlchemy

# --- CONNECT PostgreSQL DATABASE

DB_ADDRESS = os.environ.get("DATABASE_ADDRESS")
DB_PORT = os.environ.get("DATABASE_PORT")
DB_NAME = os.environ.get("DATABASE_NAME")
DB_UNAME = os.environ.get("DATABASE_USR")
DB_PASSW = os.environ.get("DATABASE_PWD")
DB_URL = f"postgresql://{DB_UNAME}:{DB_PASSW}@{DB_ADDRESS}:{DB_PORT}/{DB_NAME}"


db = SQLAlchemy()
db_app = None


# --- DEFINE TABLE SCHEMA

class Price(db.Model):

    __tablename__ = "price"
    __table_args__ = (
        db.UniqueConstraint("part", "trade", "model", "year", name="unique_prices"),
    )

    id = db.Column(db.Integer, primary_key=True)
    part = db.Column(db.String(23), unique=False, nullable=False)
    trade = db.Column(db.String(50), unique=False, nullable=True)
    model = db.Column(db.String(50), unique=False, nullable=True)
    year = db.Column(db.Integer, unique=False, nullable=True)
    price_repair = db.Column(db.Integer, nullable=True)
    price_replace = db.Column(db.Integer, nullable=True)

    def __init__(self, part, trade, model, year, price_repair, price_replace):
        self.part = part
        self.trade = trade
        self.model = model
        self.year = year
        self.price_repair = price_repair
        self.price_replace = price_replace


# --- INIT


def init_db(app):

    global db_app
    db_app = app

    # app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL

    try:
        db.init_app(app)
        with db_app.app_context():
            db.create_all()
    except Exception as e:
        print(f"#### ERROR #### Invalid PostgreSQL config: {DB_URL} ({e})")


def get_db_price(trade: str, model: str, year: int, part: str, action: str) -> int:

    try:
        price = None

        with db_app.app_context():

            # --- search exact price

            trade_v = None if trade is None or trade == "" else trade.lower()
            model_v = None if model is None or model == "" else model.lower()
            year_v = None if year is None or year == "" else str(year)
            part_v = part.replace('_damage', '')

            part_price = Price.query.filter(
                Price.part == part_v,
                Price.trade == trade_v,
                Price.model == model_v,
                Price.year == year_v,
            ).all()

            # --- If the price can't be find with the provided parameters
            # --- we fall back to the avarage part prices

            if len(part_price) == 0:
                part_price = Price.query.filter(
                    Price.part == part_v,
                    Price.trade == None,
                    Price.model == None,
                    Price.year == None,
                ).all()

            # --- return price according to the recommended action

            if len(part_price) > 0:
                if action == "REPAIR":
                    price = part_price[0].price_repair
                elif action == "REPLACE":
                    price = part_price[0].price_replace

        return price
    except Exception as e:
        print(f"#### get_db_price ERROR #### {e}")


def demo_queries():

    try:
        with db_app.app_context():

            print("===========================================")

            allEntries = db.session.query(Price).all()
            for entry in allEntries:
                print("==>", entry.id, entry.part, entry.trade, entry.model, entry.year, entry.price_repair, entry.price_replace)

            # oneEntry = db.session.query(Item).get(
            # oneEntry = db.session.query(Item).filter(db.Item.id==2)
            oneEntry = Price.query.get(2)
            print("=====>", oneEntry.id, oneEntry.part, oneEntry.trade, oneEntry.model, oneEntry.year, oneEntry.price_repair, oneEntry.price_replace)

            oneEntry = Price.query.filter(Price.part == "hood").all()[0]
            print("=====>", oneEntry.id, oneEntry.part, oneEntry.trade, oneEntry.model, oneEntry.year, oneEntry.price_repair, oneEntry.price_replace)

            oneEntry = Price.query.filter(
                Price.part == "front_bumper", Price.trade == "toyota"
            ).all()[0]
            print("=====>", oneEntry.id, oneEntry.part, oneEntry.trade, oneEntry.model, oneEntry.year, oneEntry.price_repair, oneEntry.price_replace)

            oneEntry = Price.query.filter(
                Price.part == "nopart", Price.trade == "toyota"
            ).all()
            print("=====>", oneEntry, type(db))

            print("===========================================")

    except Exception as e:
        print(f"#### demo_queries ERROR #### {e}")
