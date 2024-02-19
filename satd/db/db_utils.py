from dataclasses import dataclass, field, fields
from functools import wraps
from typing import ClassVar
import sqlite3
from sqlite3 import Connection


PRIMARY_KEY = "PRIMARY KEY"
UNIQUE = "UNIQUE"


def type_to_sqlite_type(t):
    if t == int:
        return "INTEGER"
    elif t == str:
        return "TEXT"
    elif t == float:
        return "REAL"
    else:
        raise Exception(f"No valid sqlite conversion type conversion from {t} ")


def str_join(*args, sep=" "):
    return sep.join([str(x) for x in args if x is not None])


def create_bbox_index(name):

    return (
        f"CREATE VIRTUAL TABLE IF NOT EXISTS {name}Index USING rtree("
        "id, minLon, maxLon, minLat, maxLat);"
    )


db: Connection = sqlite3.connect(":memory:")


@dataclass
class Table:
    meta_geo_index: ClassVar[bool] = False
    meta_name: ClassVar[str] = ""

    @classmethod
    def create_table(cls):
        table_name = cls.__name__
        field_statements = []
        for field in fields(cls):
            sq_type = type_to_sqlite_type(field.type)
            statement = str_join(
                field.name,
                sq_type,
                (PRIMARY_KEY) if PRIMARY_KEY in field.metadata else None,
            )
            field_statements.append(statement)
        statement = str_join(
            "CREATE TABLE ",
            table_name,
            "(\n  ",
            ",\n  ".join(field_statements),
            "\n);",
            sep="",
        )
        print(statement)
        db.execute(statement)
        if cls.meta_geo_index:
            db.execute(create_bbox_index(table_name))
        db.commit()

    @classmethod
    def insert_many(cls, objs: list):
        field_names = [
            field.name for field in fields(cls) if PRIMARY_KEY not in field.metadata
        ]
        rows = [
            tuple(getattr(obj, name) for name in field_names)
            for obj in objs
        ]
        qs = ", ".join(["?"] * len(field_names))
        statement = (
            f"INSERT INTO {cls.__name__} ({', '.join(field_names)}) VALUES ({qs});"
        )
        db.executemany(statement, rows)
        db.commit()

    @classmethod
    def insert(cls, obj):
        field_names = [
            field.name for field in fields(cls) if PRIMARY_KEY not in field.metadata
        ]
        row = tuple(getattr(obj, name) for name in field_names)

        qs = ", ".join(["?"] * len(field_names))
        statement = (
            f"INSERT INTO {cls.__name__} ({', '.join(field_names)}) VALUES ({qs});"
        )
        db.execute(statement, row)
        db.commit()

    @classmethod
    def select(cls):
        field_names = [field.name for field in fields(cls)]
        statement = f"SELECT {' ,'.join(field_names)} FROM {cls.__name__};"
        rows = db.execute(statement).fetchall()
        dict_rows = [{field_names[i]: val for i, val in enumerate(row)} for row in rows]
        return [cls(**dict_row) for dict_row in dict_rows]


def init_db(db_path: str):
    global db
    db = sqlite3.connect(db_path)


if __name__ == "__main__":
    table = Table(1)
    Table.create_table()
