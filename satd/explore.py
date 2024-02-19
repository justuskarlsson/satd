import dearpygui.dearpygui as dpg
import numpy as np
from PIL import Image
from io import BytesIO
import requests
from pathlib import Path
from satd.search import search, Feature
import os
import boto3
from dotenv import load_dotenv
import rasterio

load_dotenv()
download_dir = "/data/sentinel-2"


WIDTH = 1920
HEIGHT = 1080

PREVIEW_WIDTH = 512
PREVIEW_HEIGHT = 512

s3_session = boto3.session.Session()


def download(feature: Feature):
    product = feature.product_s3_href.split("/eodata/")[1]
    s3 = boto3.resource(
        "s3",
        endpoint_url=os.environ["endpoint_url"],
        aws_access_key_id=os.environ["aws_access_key_id"],
        aws_secret_access_key=os.environ["aws_secret_access_key"],
        region_name=os.environ["region_name"],
    )
    bucket = s3.Bucket("eodata")
    files = bucket.objects.filter(Prefix=product)
    if not list(files):
        raise FileNotFoundError(f"Could not find any files for {product}")
    dst_dir = f"{download_dir}/{feature.id}"
    for file in files:
        rel_path = file.key.split(".SAFE/")[1]
        dst_path = os.path.join(dst_dir, rel_path)
        if not os.path.isdir(dst_path):
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            bucket.download_file(file.key, dst_path)
        
        # Bands meaning 02-04 = BGR 
        # https://custom-scripts.sentinel-hub.com/custom-scripts/sentinel-2/bands/
        if file.key.endswith(".jp2"):
            print("Downloading to:", dst_path)
    print("Download done!")

dpg.create_context()


class SearchVis:
    features: list[Feature] = []
    imgs: list[np.ndarray] = []
    idx: int = 0

    def set_collection(self, features: list[Feature]):

        self.features = []
        only_2a = dpg.get_value("2A")
        max_cloud = dpg.get_value("max_cloud")
        for feature in features:
            if only_2a and not feature.is_2a:
                continue
            if feature.cloud_cover > max_cloud:
                continue
            self.features.append(feature)
        self.features.sort(reverse=True)
        self.imgs = [None] * len(features)
        self.load()

    def download(self):
        download(self.features[self.idx])

    def load(self):
        if self.idx > len(self.features) - 1:
            return
        feature = self.features[self.idx]
        dpg.set_value("idx", f"{self.idx + 1:02d}/{len(self.features):02d}")
        dpg.set_value("date", feature.datetime)
        if self.imgs[self.idx] is None:
            print("Fetching image...")
            response = requests.get(feature.quicklook_href)
            img = Image.open(BytesIO(response.content))
            print("Done.")
            img = img.resize((PREVIEW_WIDTH, PREVIEW_HEIGHT))
            rgba = np.ones((PREVIEW_HEIGHT, PREVIEW_WIDTH, 4), np.float32)
            rgb = np.array(img, dtype=np.float32) / 255.0
            rgba[..., :3] = rgb
            self.imgs[self.idx] = rgba
        dpg.set_value("texture", self.imgs[self.idx])

    def prev(self):
        self.idx = max(0, self.idx - 1)
        self.load()

    def next(self):
        self.idx = min(len(self.features) - 1, self.idx + 1)
        self.load()


search_vis = SearchVis()


def search_callback():
    time_range = dpg.get_value("time_start") + "/" + dpg.get_value("time_end")
    east = dpg.get_value("bbox_center_east")
    north = dpg.get_value("bbox_center_north")
    size = dpg.get_value("bbox_size")
    bbox = [east - size, north - size, east + size, north + size]
    collection = search(bbox=bbox, time_range=time_range)
    search_vis.set_collection(collection.features)


with dpg.texture_registry(show=False):
    buffer = np.ones((PREVIEW_HEIGHT, PREVIEW_WIDTH, 4), dtype=np.float32)
    dpg.add_raw_texture(
        width=PREVIEW_WIDTH,
        height=PREVIEW_HEIGHT,
        default_value=buffer,
        format=dpg.mvFormat_Float_rgba,
        tag="texture",
    )


with dpg.window(
    label="Preview",
    width=PREVIEW_WIDTH,
    height=PREVIEW_HEIGHT,
    pos=(WIDTH - PREVIEW_WIDTH, 0),
):
    dpg.add_text("0/0", tag="idx")
    dpg.add_text("", tag="date")
    dpg.add_button(label="Download", callback=search_vis.download)
    dpg.add_image("texture")

with dpg.window(label="Search", width=300, height=HEIGHT, pos=(0, 0)):
    dpg.add_input_text(default_value="2023-05-01", label="Time Start", tag="time_start")
    dpg.add_input_text(default_value="2023-08-30", label="Time End", tag="time_end")
    dpg.add_input_float(default_value=1000 * 1e-5, label="Size [m]", tag="bbox_size")
    dpg.add_input_float(default_value=15.612147, label="East", tag="bbox_center_east")
    dpg.add_input_float(default_value=58.419165, label="North", tag="bbox_center_north")
    dpg.add_button(label="Search", callback=search_callback)

    dpg.add_input_float(label="Max Cloud", default_value=10.0, tag="max_cloud")
    dpg.add_checkbox(label="2A", default_value=True, tag="2A")

with dpg.handler_registry():
    dpg.add_key_press_handler(dpg.mvKey_M, callback=search_vis.prev)
    dpg.add_key_press_handler(dpg.mvKey_N, callback=search_vis.next)

dpg.create_viewport(width=WIDTH, height=HEIGHT, resizable=False)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
