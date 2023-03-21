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


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    content = db.Column(db.String(120), unique=True, nullable=False)

    def __init__(self, title, content):
        self.title = title
        self.content = content


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

            trade_v = trade.lower() if trade is not None else None
            model_v = model.lower() if model is not None else None

            part_price = Price.query.filter(
                Price.part == part.replace('_damage', ''),
                Price.trade == trade_v,
                Price.model == model_v,
                Price.year == year,
            ).all()

            # --- If the price can't be find with the provided parameters
            # --- we fall back to the avarage part prices

            if len(part_price) == 0:
                print("PRICE FALLBACK")
                part_price = Price.query.filter(
                    Price.part == part.replace('_damage', ''),
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

            allEntries = db.session.query(Item).all()
            for entry in allEntries:
                print("==>", entry.id, entry.title, entry.content)

            # oneEntry = db.session.query(Item).get(
            # oneEntry = db.session.query(Item).filter(db.Item.id==2)
            oneEntry = Item.query.get(2)
            print("=====>", oneEntry.id, oneEntry.title, oneEntry.content)

            oneEntry = Item.query.filter(Item.title == "title3").all()[0]
            print("=====>", oneEntry.id, oneEntry.title, oneEntry.content)

            oneEntry = Item.query.filter(
                Item.title == "title1", Item.content == "content1"
            ).all()[0]
            print("=====>", oneEntry.id, oneEntry.title, oneEntry.content)

            oneEntry = Item.query.filter(
                Item.title == "title0", Item.content == "content1"
            ).all()
            print("=====>", oneEntry, type(db))

            print("===========================================")

    except Exception as e:
        print(f"#### demo_queries ERROR #### {e}")
