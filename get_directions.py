import os
import json
import requests
import datetime
import time
from tqdm import tqdm
from multiprocessing import Pool


def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]


def get_new_directions(res):
    request_string = (
        "https://api.tfl.gov.uk/Journey/JourneyResults/"
        + res["address"].replace(" ", "%20").replace(",", "%2C")
        + "/to/Gower%20Street?nationalSearch=false&journeyPreference=LeastTime&app_key=a6f6f11944e68b4c571b358fe9a8bffa&app_id=187f5018"
    )

    response = requests.get(url=request_string)
    return response.json()


def convert_direction_json_to_routes(directions):
    if not "journeys" in directions.keys():
        return []
    routes = []
    for journey in directions["journeys"]:
        route = {}
        legs = []
        for leg in journey["legs"]:
            dest = leg["instruction"]["summary"].split(" to ")[-1]
            if "Walk " in leg["instruction"]["summary"]:
                legs.append(("walk", dest, leg["duration"]))
            elif " line " in leg["instruction"]["summary"]:
                line = leg["instruction"]["summary"].split(" to ")[0]
                legs.append(("tube", line, dest, leg["duration"]))
            else:
                # TODO get bus number
                legs.append(("bus", dest, leg["duration"]))
        route["legs"] = legs
        route["total_duration"] = sum(map(lambda x: x[-1], legs))
        routes.append(route)
    return routes


def download_and_save_directions_single(path):
    prop = json.load(open(path + "/property.json", "r"))
    directions = get_new_directions(prop)
    routes = convert_direction_json_to_routes(directions)
    with open(path + "/directions.json", "w+") as directions_file:
        directions_file.write(json.dumps(directions, indent=4))
    for i in range(len(routes)):
        with open(path + "/route_" + str(i) + ".json", "w+") as route_file:
            route_file.write(json.dumps(routes[i], indent=4))


def download_and_save_directions():
    start = datetime.datetime.now()
    file_paths = []
    with open("property_index.json", "r") as index_file:
        file_paths = json.load(index_file)
    print("getting directions for", len(file_paths), "properties")
    split_file_paths = list(divide_chunks(file_paths, 450))
    for i in range(len(split_file_paths)):
        chunk_of_paths = split_file_paths[i]
        print("starting on chunk", i, "of length", len(chunk_of_paths))
        with Pool(len(chunk_of_paths)) as p:
            print("worker pool started, requesting and downloading data...")
            p.map(download_and_save_directions_single, chunk_of_paths)
        if i + 1 < len(split_file_paths):
            # need to wait cause TFL doesn't allow more than 500 requests per minute
            print("waiting")
            for t in tqdm(range(6000)):
                time.sleep(0.01)
    print("done,", (datetime.datetime.now() - start).total_seconds(), "s")


def check_all_properties_have_directions():
    file_paths = []
    with open("property_index.json", "r") as index_file:
        file_paths = json.load(index_file)
    disambugations = []
    for path in file_paths:
        if not os.path.exists(path + "/property.json") or not os.path.exists(
            path + "/directions.json"
        ):
            print(path)
        with open(path + "/directions.json", "r") as dir_file:
            directions = json.load(dir_file)
            if not "journeys" in directions:
                print(path + "/directions.json")
                disambugations.append(path)
    print(len(disambugations))


if __name__ == "__main__":
    # download_and_save_directions()
    check_all_properties_have_directions()
