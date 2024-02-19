from satd.db.db_utils import Table, field, PRIMARY_KEY, dataclass, init_db, db
from satd.search import Feature

@dataclass(kw_only=True)
class SentinelImage(Table):
    meta_geo_index = True

    id: int = field(default=-1, metadata={PRIMARY_KEY: True})
    id_str: str
    date: str

    @staticmethod
    def from_feature(feature: Feature):
        return SentinelImage(
            id_str=feature.id,
            date=feature.datetime,
        )


__all__ = [
    SentinelImage.__name__,
]

if __name__ == "__main__":
    import sqlite3
    # init_db("/data/sentinel-2/index.db")
    SentinelImage.create_table()
    SentinelImage.insert_many([
        SentinelImage(id_str="a0", date="2024-23"),
        SentinelImage(id_str="a1", date="2024-12")
    ])
    SentinelImage.insert(SentinelImage(id_str="b0", date="2024-01"))
    res = SentinelImage.select()
    print(res)