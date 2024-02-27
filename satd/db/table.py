from dataclasses import dataclass, field, fields
from functools import wraps
from typing import ClassVar
import sqlite3
from sqlite3 import Connection
import os

PRIMARY_KEY = "PRIMARY KEY"

type_mapping = {
    int: "INTEGER",
    str: "TEXT",
    float: "REAL",
}

db_primitives = set([
    int, str, float,
])

def type_to_sqlite_type(t):
    if t not in type_mapping:
        raise Exception(f"No valid sqlite conversion type conversion from {t} ")
    return type_mapping[t]


def str_join(*args, sep=" "):
    return sep.join([str(x) for x in args if x is not None])



@dataclass
class Table:
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
            f"CREATE TABLE IF NOT EXISTS {table_name}(",
            "  " + ",\n  ".join(field_statements),
            ");",
            sep="\n",
        )
        get_db().execute(statement)
        get_db().commit()

    @classmethod
    def _get_insert_row(cls, obj):
        row = []
        for field in fields(cls):
            val = getattr(obj, field.name)
            if PRIMARY_KEY in field.metadata:
                pass
            elif hasattr(val, "__to_db__"):
                row.append(val.__to_db__())
            elif type(val) in db_primitives:
                row.append(val)
            else:
                raise Exception(f"{type(val)} has no method __to_db__")
        return row

    @classmethod
    def insert(cls, obj):
        field_names = [
            field.name for field in fields(cls) if PRIMARY_KEY not in field.metadata
        ]
        row = cls._get_insert_row(obj)

        qs = ", ".join(["?"] * len(field_names))
        statement = (
            f"INSERT INTO {cls.__name__} ({', '.join(field_names)}) VALUES ({qs});"
        )
        cur = get_db().execute(statement, row)
        get_db().commit()
        return cur.lastrowid


    @classmethod
    def _extract_row(cls, row):
        dict_row = {}
        for i, field in enumerate(fields(cls)):
            field_cls = field.type
            val = row[i]
            if hasattr(field_cls, "__from_db__"):
                val = field_cls.__from_db__(val)
            # Maybe log err if not primitive?
            dict_row[field.name] = val
        
        return cls(**dict_row)

    @classmethod
    def _extract_rows(cls, rows):
        return [cls._extract_row(row) for row in rows]

    @classmethod
    def select(cls):
        field_names = [field.name for field in fields(cls)]
        statement = f"SELECT {' ,'.join(field_names)} FROM {cls.__name__};"
        return cls._extract_rows(get_db().execute(statement).fetchall())

    @classmethod
    def contains(cls, id, id_key: str ="id"):
        statement = f"SELECT id FROM {cls.__name__} WHERE {id_key}=?;"
        res = get_db().execute(statement, [id]).fetchall()
        return len(res) > 0


db: Connection = sqlite3.connect(":memory:")

def init_db(db_path: str):
    global db
    db = sqlite3.connect(db_path)

def get_db():
    return db

if __name__ == "__main__":
    table = Table(1)
    Table.create_table()
