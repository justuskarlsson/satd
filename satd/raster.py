"""
Look at:
https://github.com/langnico/global-canopy-height-model/blob/main/gchm/utils/gdal_process.py
"""

import rasterio
from osgeo import gdal
from PIL import Image
import numpy as np
import utm
from dataclasses import dataclass

gdal.UseExceptions()


def normalize_uint8(data):
    data = data.astype(np.float32)
    data = data / (1 << 14)
    data = np.clip(data * 255.0 / 0.3, a_min=0.0, a_max=255.0)
    data = data.astype(np.uint8)
    data = np.expand_dims(data, 2)
    return data

class Photo:
    def __init__(self, band_path: str):
        self.ds: gdal.Dataset = gdal.Open(band_path)
        self.cs: gdal.osr.SpatialReference = self.ds.GetSpatialRef()
        self.full_xs: int = self.ds.RasterXSize
        self.full_ys: int = self.ds.RasterYSize
        self.zone_letter: str = self.cs.GetName()[-1]
        self.zone_number: int = self.cs.GetUTMZone()

    def get_geod_size(self):
        x0, y0 = self.get_geod_pos(0, 0)
        x1, y1 = self.get_geod_pos(self.full_xs - 1, self.full_ys - 1)
        return abs(x1 - x0), abs(y1 - y0)

    def get_geod_pos(self, x, y):
        east, x_east, x_north, north, y_east, y_north = self.ds.GetGeoTransform()
        east += x_east * x
        north += y_north * y
        lat, lon = utm.to_latlon(east, north, self.zone_number, self.zone_letter)
        return lon, lat

    def get_geod_center(self):
        return self.get_geod_pos(self.full_xs // 2, self.full_ys // 2)

    def __post_init__(self):
        self.buffer = np.array([])

    def read(self, lev: int = 0) -> np.ndarray:
        band = self.ds.GetRasterBand(1)
        if lev >= 0:
            ov = band.GetOverview(lev)
            data = ov.ReadAsArray()
        else:
            data = band.ReadAsArray()
        return normalize_uint8(data)




def read_band(band_path, lev=2):
    ds = gdal.Open(band_path)
    band = ds.GetRasterBand(1)

    if lev >= 0:
        ov = band.GetOverview(lev)
        data = ov.ReadAsArray()
    else:
        data = band.ReadAsArray()
    data = np.flip(data, 0)
    return normalize_uint8(data)


def read_rgb(rgb_paths, lev=2):
    rgbs = [read_band(path) for path in rgb_paths]
    rgb = np.concatenate(rgbs, axis=2)
    return rgb


if __name__ == "__main__":
    directory = "Sentinel-2/MSI/L2A/2023/06/15/S2A_MSIL2A_20230615T102031_N0509_R065_T33VWE_20230615T193401.SAFE/GRANULE/L2A_T33VWE_A041675_20230615T102026/IMG_DATA/R10m"
    path = directory + "/T33VWE_20230615T102031_B{:02d}_10m.jp2"
    rgb = read_rgb(path.format(4), path.format(3), path.format(2))
    img = Image.fromarray(rgb)
    # png takes such a long time
    img.save("resources/images/tmp.jpg")



"""
Driver: JP2OpenJPEG/JPEG-2000 driver based on OpenJPEG library
Files: /data/sentinel-2/S2A_MSIL2A_20230622T100601_N0509_R022_T33VWE_20230622T162904.SAFE/GRANULE/L2A_T33VWE_A041775_20230622T100756/IMG_DATA/R10m/T33VWE_20230622T100601_B04_10m.jp2
Size is 10980, 10980
Coordinate System is:
PROJCRS["WGS 84 / UTM zone 33N",
    BASEGEOGCRS["WGS 84",
        ENSEMBLE["World Geodetic System 1984 ensemble",
            MEMBER["World Geodetic System 1984 (Transit)"],
            MEMBER["World Geodetic System 1984 (G730)"],
            MEMBER["World Geodetic System 1984 (G873)"],
            MEMBER["World Geodetic System 1984 (G1150)"],
            MEMBER["World Geodetic System 1984 (G1674)"],
            MEMBER["World Geodetic System 1984 (G1762)"],
            MEMBER["World Geodetic System 1984 (G2139)"],
            ELLIPSOID["WGS 84",6378137,298.257223563,
                LENGTHUNIT["metre",1]],
            ENSEMBLEACCURACY[2.0]],
        PRIMEM["Greenwich",0,
            ANGLEUNIT["degree",0.0174532925199433]],
        ID["EPSG",4326]],
    CONVERSION["UTM zone 33N",
        METHOD["Transverse Mercator",
            ID["EPSG",9807]],
        PARAMETER["Latitude of natural origin",0,
            ANGLEUNIT["degree",0.0174532925199433],
            ID["EPSG",8801]],
        PARAMETER["Longitude of natural origin",15,
            ANGLEUNIT["degree",0.0174532925199433],
            ID["EPSG",8802]],
        PARAMETER["Scale factor at natural origin",0.9996,
            SCALEUNIT["unity",1],
            ID["EPSG",8805]],
        PARAMETER["False easting",500000,
            LENGTHUNIT["metre",1],
            ID["EPSG",8806]],
        PARAMETER["False northing",0,
            LENGTHUNIT["metre",1],
            ID["EPSG",8807]]],
    CS[Cartesian,2],
        AXIS["(E)",east,
            ORDER[1],
            LENGTHUNIT["metre",1]],
        AXIS["(N)",north,
            ORDER[2],
            LENGTHUNIT["metre",1]],
    USAGE[
        SCOPE["Navigation and medium accuracy spatial referencing."],
        AREA["Between 12°E and 18°E, northern hemisphere between equator and 84°N, onshore and offshore. Austria. Bosnia and Herzegovina. Cameroon. Central African Republic. Chad. Congo. Croatia. Czechia. Democratic Republic of the Congo (Zaire). Gabon. Germany. Hungary. Italy. Libya. Malta. Niger. Nigeria. Norway. Poland. San Marino. Slovakia. Slovenia. Svalbard. Sweden. Vatican City State."],
        BBOX[0,12,84,18]],
    ID["EPSG",32633]]
Data axis to CRS axis mapping: 1,2
Origin = (499980.000000000000000,6500040.000000000000000)
Pixel Size = (10.000000000000000,-10.000000000000000)
Image Structure Metadata:
  COMPRESSION_REVERSIBILITY=LOSSLESS
Corner Coordinates:
Upper Left  (  499980.000, 6500040.000) ( 14d59'58.76"E, 58d38'26.36"N)
Lower Left  (  499980.000, 6390240.000) ( 14d59'58.79"E, 57d39'16.02"N)
Upper Right (  609780.000, 6500040.000) ( 16d53'25.95"E, 58d37'36.36"N)
Lower Right (  609780.000, 6390240.000) ( 16d50'20.44"E, 57d38'27.89"N)
Center      (  554880.000, 6445140.000) ( 15d55'55.99"E, 58d 8'39.00"N)
Band 1 Block=1024x1024 Type=UInt16, ColorInterp=Gray
  Overviews: 5490x5490, 2745x2745, 1373x1373, 687x687
  Overviews: arbitrary
  Image Structure Metadata:
    COMPRESSION=JPEG2000
    NBITS=15
"""