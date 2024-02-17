import dearpygui.dearpygui as dpg
import numpy as np
from PIL import Image
from io import BytesIO
import requests

from satd.search import search, Feature

WIDTH = 1920
HEIGHT = 1080

PREVIEW_WIDTH = 512
PREVIEW_HEIGHT = 512




dpg.create_context()

class SearchVis:
    features: list[Feature] = []
    imgs: list[np.ndarray] = []
    idx: int = 0

    def set_collection(self, features: list[Feature]):
        self.features = features
        self.features.sort(reverse=True)
        self.imgs = [None] * len(features)
        self.load()

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
    lkpg = [15.618669973441541, 58.40504766611348, 15.628669973441541, 58.41504766611348]
    collection = search(bbox=lkpg, time_range="2023-12-01/2024-02-17")
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


with dpg.window(label="Preview", width=PREVIEW_WIDTH, height=PREVIEW_HEIGHT, pos=(WIDTH-PREVIEW_WIDTH, 0)):
    dpg.add_text("0/0", tag="idx")
    dpg.add_text("", tag="date")
    dpg.add_image("texture")

with dpg.window(label="Search", width=300, height=HEIGHT, pos=(0, 0)):
    dpg.add_button(label="Search", callback=search_callback)

with dpg.handler_registry():
    dpg.add_key_press_handler(dpg.mvKey_M, callback=search_vis.prev)
    dpg.add_key_press_handler(dpg.mvKey_N, callback=search_vis.next)

dpg.create_viewport(width=WIDTH, height=HEIGHT, resizable=False)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
