import os
from glob import glob
import numpy as np

from satd.db.geo_table import GeoTable, dataclass, Bbox
from satd.search import Feature
import satd.raster as raster

@dataclass(kw_only=True)
class SentinelImage(GeoTable):
    id_str: str
    cloud_cover: float
    datetime: str
    product_type: str
    s3_href: str

    @staticmethod
    def from_feature(feature: Feature):
        return SentinelImage(
            id_str=feature.id,
            date=feature.datetime,
        )

    @staticmethod
    def from_json(data):
        return SentinelImage(
            bbox=Bbox(*data["bbox"]),
            id_str=data["id"],
            cloud_cover=data["properties"]["cloudCover"],
            datetime=data["properties"]["datetime"],
            product_type=data["properties"]["productType"],
            s3_href=data["assets"]["PRODUCT"]["alternate"]["s3"]["href"],
        )

    def get_rgb(self, dir_path: str, lev: int = 2) -> np.ndarray:
        row_dir = os.path.join(dir_path, self.id_str)
        imgs = sorted(glob(row_dir + "/GRANULE/*/IMG_DATA/*/*B0*_10m.jp2"))
        rgb = list(reversed(imgs[:3]))
        return raster.read_rgb(rgb, lev)
    
    def get_rgb_photos(self, dir_path: str) -> list[raster.Photo]:
        row_dir = os.path.join(dir_path, self.id_str)
        imgs = sorted(glob(row_dir + "/GRANULE/*/IMG_DATA/*/*B0*_10m.jp2"))
        rgb = list(reversed(imgs[:3]))
        return [raster.Photo(path) for path in rgb]
    
__all__ = [
    SentinelImage.__name__,
]

if __name__ == "__main__":
    # init_db("/data/sentinel-2/index.db")
    SentinelImage.create_table()
    # SentinelImage.insert_many(
    #     [
    #         SentinelImage(id_str="a0", date="2024-23", bbox=Bbox(0, 0, 2, 2)),
    #         SentinelImage(id_str="a1", date="2024-12", bbox=Bbox(0, 0, 2, 2)),
    #     ]
    # )
    SentinelImage.insert(SentinelImage(bbox=Bbox(0, 0, 4, 4)))
    SentinelImage.insert(SentinelImage(bbox=Bbox(14, 57, 16, 59)))
    print("Select all:\n", SentinelImage.select())
    print("Select (15, 58):\n", SentinelImage.select_point((15, 58)))
