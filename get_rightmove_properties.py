from rightmove_webscraper import rightmove_data
import pandas as pd
import json
import shutil
import os
import random


def request_new_rightmove():
    print("requesting new rightmove data")
    url = "https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=STATION%5E3317&maxBedrooms=5&minBedrooms=4&maxPrice=5000&radius=3.0&propertyTypes=&includeLetAgreed=false&mustHave=&dontShow=&furnishTypes=&keywords="
    search_results = rightmove_data(url).get_results
    search_results = search_results.T.to_dict().values()
    print("got", len(search_results), "results")
    parsed = []

    if os.path.isdir("results"):
        shutil.rmtree("results")
    os.mkdir("results")

    for res in search_results:
        if "share" in res["type"] or "Share" in res["type"]:
            continue
        res["id"] = "".join(
            [random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for i in range(10)]
        )
        res["weekly_price_per_head"] = float(res["price"]) / float(
            res["number_bedrooms"]
        )
        if res["price"] > 2000:
            res["weekly_price_per_head"] *= 7 / 31
        res["weekly_price_per_head"] = round(res["weekly_price_per_head"], 2)
        res["search_date"] = str(res["search_date"])
        res["postcode"] = str(res["postcode"])
        os.mkdir("results/" + res["id"])
        with open("results/" + res["id"] + "/property.json", "w+") as property_file:
            property_file.write(json.dumps(res, indent=4))
        res["filepath"] = os.path.abspath("results/" + res["id"])
        parsed.append(res["filepath"])

    with open("property_index.json", "w+") as index:
        index.write(json.dumps(parsed, indent=4))
    print("stored new rightmove data")


if __name__ == "__main__":
    request_new_rightmove()
