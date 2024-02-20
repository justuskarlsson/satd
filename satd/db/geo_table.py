from satd.db.table import (
    Table,
    str_join,
    sqlite3,
    db,
    dataclass,
    fields,
    field,
    PRIMARY_KEY,
    type_mapping,
)
from collections import namedtuple


class Bbox(namedtuple("Bbox", ["min_x", "min_y", "max_x", "max_y"])):
    def __to_db__(self):
        return ",".join(
            map(
                str,
                [
                    self.min_x,
                    self.max_x,
                    self.min_y,
                    self.max_y,
                ],
            )
        )

    @staticmethod
    def __from_db__(text):
        min_x, max_x, min_y, max_y = map(float, text.split(","))
        return Bbox(min_x, min_y, max_x, max_y)


type_mapping[Bbox] = "TEXT"

@dataclass(kw_only=True)
class GeoTable(Table):
    id: int = field(default=-1, metadata={PRIMARY_KEY: True})
    bbox: Bbox

    @classmethod
    def index_name(cls):
        return cls.__name__ + "GeoIndex"

    @classmethod
    def create_table(cls):
        super().create_table()
        statement = (
            f"CREATE VIRTUAL TABLE IF NOT EXISTS {cls.index_name()} "
            + "USING rtree(id, min_x, max_x, min_y, max_y);"
        )
        db.execute(statement)
        db.commit()

    @classmethod
    def insert(cls, obj):
        row_id = super().insert(obj)
        statement = f"INSERT INTO {cls.index_name()} VALUES (?, ?, ?, ?, ?)"
        values = (row_id,) + obj.bbox
        db.execute(statement, values)
        print(statement, values)

    @classmethod
    def select(cls):
        return super().select()

    @classmethod
    def select_point(cls, point):
        x, y = point
        table_name = cls.__name__
        index_name = cls.index_name()
        names = [field.name for field in fields(cls)]
        names = [f"{table_name}.{x}" for x in names]
        names_str = ",".join(names)
        statement = f"""
            SELECT {names_str} FROM {table_name}, {index_name}
            WHERE {table_name}.id={index_name}.id 
            AND min_x <= ? AND max_x >= ?
            AND min_y <= ? AND max_y >= ?;
        """
        values = (x, x, y, y)
        print(statement, values)
        return super()._extract_rows(db.execute(statement, values).fetchall())
