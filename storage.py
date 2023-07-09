import datetime as dt
import uuid
from pathlib import Path
from peewee import SqliteDatabase, Model, ForeignKeyField, CharField, DateTimeField, DoubleField

import settings


IMAGES_DIR = settings.STORAGE_DIR / 'images'
DATABASE_PATH = settings.STORAGE_DIR / 'storage.db'
NEED_INIT_DATABASE = not DATABASE_PATH.exists()


DATABASE_PATH.parent.mkdir(exist_ok=True, parents=True)

_database = SqliteDatabase(DATABASE_PATH)
_database.connect()


class BaseModel(Model):
    class Meta:
        database = _database


class Upload(BaseModel):
    timestamp = DateTimeField()
    rescue_operation = CharField()


class Image(BaseModel):
    upload = ForeignKeyField(Upload, backref='images')
    timestamp = DateTimeField(null=True)
    path = CharField(unique=True)
    original_name = CharField()
    longitude = DoubleField(null=True)
    latitude = DoubleField(null=True)


class Label(BaseModel):
    image = ForeignKeyField(Image, backref='labels')
    xmin = DoubleField()
    xmax = DoubleField()
    ymin = DoubleField()
    ymax = DoubleField()
    confidence = DoubleField()

    @property
    def xc(self) -> float:
        return (self.xmax + self.xmin) / 2

    @property
    def yc(self) -> float:
        return (self.ymax + self.ymin) / 2


if NEED_INIT_DATABASE:
    _database.create_tables([Upload, Image, Label])


def upload_image(image_data, name: str) -> Path:
    date = dt.datetime.now().strftime('%Y-%m-%d')
    upload_dir = IMAGES_DIR / date
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = name.rpartition('.')[2]
    filename = uuid.uuid4().hex + '.' + ext

    path = upload_dir / filename
    path.write_bytes(image_data)

    return path.relative_to(IMAGES_DIR)
