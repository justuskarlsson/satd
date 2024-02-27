"""
Look at:
https://github.com/langnico/global-canopy-height-model/blob/main/gchm/utils/gdal_process.py
"""

import rasterio
from osgeo import gdal
from PIL import Image
import numpy as np

gdal.UseExceptions()


def normalize_uint8(data):
    data = data.astype(np.float32)
    data = data / (1 << 14)
    data = np.clip(data * 255.0 / 0.3, a_min=0.0, a_max=255.0)
    data = data.astype(np.uint8)
    data = np.expand_dims(data, 2)
    return data


def read_band(band_path, lev=2):
    ds = gdal.Open(band_path)
    band = ds.GetRasterBand(1)
    if lev >= 0:
        ov = band.GetOverview(lev)
        data = ov.ReadAsArray()
    else:
        data = band.ReadAsArray()
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
