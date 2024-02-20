from satd.db.geo_table import GeoTable, dataclass, Bbox
from satd.search import Feature


@dataclass(kw_only=True)
class SentinelImage(GeoTable):
    id_str: str
    date: str

    # s3_href: str

    @staticmethod
    def from_feature(feature: Feature):
        return SentinelImage(
            id_str=feature.id,
            date=feature.datetime,
        )

    @staticmethod
    def from_json(data):
        return SentinelImage(
            id_str=data["id"],
            cloud_cover=data["properties"]["cloudCover"],
            datetime=data["properties"]["datetime"],
            product_type=data["properties"]["productType"],
            bbox=data["bbox"],
        )


__all__ = [
    SentinelImage.__name__,
]

if __name__ == "__main__":
    import sqlite3

    # init_db("/data/sentinel-2/index.db")
    SentinelImage.create_table()
    # SentinelImage.insert_many(
    #     [
    #         SentinelImage(id_str="a0", date="2024-23", bbox=Bbox(0, 0, 2, 2)),
    #         SentinelImage(id_str="a1", date="2024-12", bbox=Bbox(0, 0, 2, 2)),
    #     ]
    # )
    SentinelImage.insert(SentinelImage(id_str="b0", date="2024-01", bbox=Bbox(0, 0, 4, 4)))
    SentinelImage.insert(SentinelImage(id_str="b0", date="2024-01", bbox=Bbox(14, 57, 16, 59)))
    print("Select all:\n", SentinelImage.select())
    print("Select (15, 58):\n", SentinelImage.select_point((15, 58)))
