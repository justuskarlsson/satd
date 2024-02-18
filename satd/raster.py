import rasterio
from osgeo import gdal
from PIL import Image
import numpy as np
gdal.UseExceptions()

directory = "Sentinel-2/MSI/L2A/2023/06/15/S2A_MSIL2A_20230615T102031_N0509_R065_T33VWE_20230615T193401.SAFE/GRANULE/L2A_T33VWE_A041675_20230615T102026/IMG_DATA/R10m"
path = directory + "/T33VWE_20230615T102031_B{:02d}_10m.jp2"


def normalize_uint8(data):
    data = data.astype(np.float32)
    data = data / (1<<14)
    data = np.clip(data * 255.0 * 3.0, a_min=0.0, a_max=255.0)
    data = data.astype(np.uint8)
    data = np.expand_dims(data, 2)
    return data

def read_lev(band, lev=2):
    ds = gdal.Open(path.format(band))
    band = ds.GetRasterBand(1)
    if lev >= 0:
        ov = band.GetOverview(lev)
        data = ov.ReadAsArray()
    else:
        data = band.ReadAsArray()
    print(data.shape, data.dtype, np.max(data), np.min(data))
    return normalize_uint8(data)



if __name__ == "__main__":
    red = read_lev(4)
    green = read_lev(3)
    blue = read_lev(2)

    rgb = np.concatenate([red, green, blue], axis=2)
    img = Image.fromarray(rgb)
    # png takes such a long time
    img.save("resources/images/tmp.jpg")
