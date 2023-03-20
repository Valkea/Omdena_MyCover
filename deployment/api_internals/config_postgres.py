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


# --- INIT


def init_db(app):

    global db_app
    db_app = app

    # app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
    db.init_app(app)


def get_db_price(trade: str, model: str, year: int, part: str) -> int:

    print("===========================================")
    with db_app.app_context():
        db.create_all()

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

        # oneEntry = Item.query.filter(Item.title == "title0", Item.content == "content1").all()
        # print("=====>", oneEntry, type(db))
    print("===========================================")

    return oneEntry.id


def demo_queries():

    with db_app.app_context():
        db.create_all()

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
