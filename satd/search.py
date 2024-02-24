## https://documentation.dataspace.copernicus.eu/APIs/STAC.html

import requests
import json

# Define the correct API endpoint for STAC
stac_endpoint = "https://catalogue.dataspace.copernicus.eu/stac/collections"


class Feature:
    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        self.properties = self.data["properties"]
        self.datetime = self.properties["datetime"]
        self.cloud_cover = self.properties["cloudCover"]
        self.is_2a = self.properties["productType"].endswith("2A")
        self.quicklook_href = ""
        if "QUICKLOOK" in self.data["assets"]:
            self.quicklook_href = self.data["assets"]["QUICKLOOK"]["href"]
        self.product = self.data["assets"]["PRODUCT"]
        self.product_s3_href = self.product["alternate"]["s3"]["href"]


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
    with open("resources/feature_collection.json") as f:
        data = json.load(f)
        return FeatureCollection(data)
    print("Search:", bbox, time_range)
    # Construct the search query
    search_params = {
        "bbox": ",".join([str(x) for x in bbox]),
        "datetime": time_range,
        "limit": limit,
    }

    url = f"{stac_endpoint}/{sensor}/items?"

    # Make the API request
    response = requests.get(url, params=search_params)
    # Check if the request was successful
    if response.status_code != 200:
        print("Failed to fetch data:", response.status_code)
        return []

    data = response.json()
    collection = FeatureCollection(data)
    # with open("feature_collection.json", "w") as f:
    #     json.dump(data, f, indent=2)

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
