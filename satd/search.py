## https://documentation.dataspace.copernicus.eu/APIs/STAC.html

import requests
import json

# Define the correct API endpoint for STAC
stac_endpoint = "https://catalogue.dataspace.copernicus.eu/stac/collections"


class Feature:
    def __init__(self, data):
        self.data = data

    @property
    def properties(self):
        return self.data["properties"]
    
    @property
    def datetime(self):
        return self.properties['datetime']

    @property
    def quicklook_href(self):
        if "QUICKLOOK" not in self.data["assets"]:
            return ""
        return self.data["assets"]["QUICKLOOK"]["href"]

    @property
    def product(self):
        return self.data["assets"]["PRODUCT"]

    @property
    def product_s3_href(self):
        return self.product["alternate"]["s3"]["href"]

    def __str__(self):
        return f"({self.datetime}) thumbnail: {self.quicklook_href}"
    
    def __lt__(self, other):
        return self.datetime < other.datetime


class FeatureCollection:
    def __init__(self, data):
        self.data = data
        self.features = [Feature(f) for f in self.data["features"]]

    def __len__(self):
        return len(self.features)

    def __getitem__(self, i) -> Feature:
        return self.features[i]

    def __str__(self):
        return "\n".join([str(f) for f in self.features])


def search(
    bbox=[12.41, 41.80, 12.52, 41.90],
    time_range="2022-01-01/2022-03-01",
    limit=100,
    sensor="SENTINEL-2",
):

    # Construct the search query
    search_params = {"bbox": ",".join([str(x) for x in bbox]), "datetime": time_range, "limit": limit}

    url = f"{stac_endpoint}/{sensor}/items?"

    # Make the API request
    response = requests.get(url, params=search_params)
    # Check if the request was successful
    if response.status_code != 200:
        print("Failed to fetch data:", response.status_code)
        return []

    collection = FeatureCollection(response.json())

    return collection


if __name__ == "__main__":
    collection = search()
    print(len(collection))
    for feature in collection:
        print(feature.quicklook_href)

    # from PIL import Image
    # from io import BytesIO
    # response = requests.get(collection[0].quicklook_href)
    # img = Image.open(BytesIO(response.content))
    # img.show()
