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


app_key = ""
app_id = ""
with open("tfl_credentials.json", "r") as cred_file:
    creds = json.load(cred_file)
    app_key = creds["app_key"]
    app_id = creds["app_id"]


def get_new_directions(res):
    torrington_place_id = "1013720"
    request_string = (
        "https://api.tfl.gov.uk/Journey/JourneyResults/"
        + res["address"].replace(" ", "%20").replace(",", "%2C")
        + "/to/"
        + torrington_place_id
        + "?nationalSearch=false&journeyPreference=LeastTime&app_key="
        + app_key
        + "&app_id="
        + app_id
    )

    response = requests.get(url=request_string)
    try:
        return response.json()
    except json.JSONDecodeError as err:
        print(err)
        return {"status": "fail"}


def convert_direction_json_to_routes(directions):
    if not "journeys" in directions.keys():
        return []
    routes = []
    for journey in directions["journeys"]:
        route = {}
        legs = []
        for leg in journey["legs"]:
            summary = leg["instruction"]["summary"]
            dest = summary.split(" to ")[-1]
            if "Walk " in summary:
                legs.append({"type": "walk", "dest": dest, "duration": leg["duration"]})
            elif " line " in summary:
                line = summary.split(" to ")[0]
                legs.append(
                    {
                        "type": "tube",
                        "dest": dest,
                        "duration": leg["duration"],
                        "line": line,
                    }
                )
            else:
                bus_num = summary.split(" bus ")[0]
                legs.append(
                    {
                        "type": "bus",
                        "dest": dest,
                        "duration": leg["duration"],
                        "line": bus_num,
                    }
                )
        route["legs"] = legs
        route["total_duration"] = sum(map(lambda x: x["duration"], legs))
        already_exists = False
        for other_route in routes:
            if len(other_route["legs"]) == len(route["legs"]):
                match = True
                for i in range(len(route["legs"])):
                    match = (
                        match
                        and route["legs"][i]["type"] == other_route["legs"][i]["type"]
                    )
                    if match:
                        match = (
                            match
                            and route["legs"][i]["dest"]
                            == other_route["legs"][i]["dest"]
                        )
                        if route["legs"][i]["type"] != "walk":
                            match = (
                                match
                                and route["legs"][i]["line"]
                                == other_route["legs"][i]["line"]
                            )
                if match:
                    already_exists = True
                    break
        if not already_exists:
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
    for path in file_paths:
        if os.path.exists(path + "/directions.json"):
            os.remove(path + "/directions.json")
        i = 0
        while os.path.exists(path + "/route_" + str(i) + ".json"):
            os.remove(path + "/route_" + str(i) + ".json")
            i += 1
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
                # print(path + "/directions.json")
                disambugations.append(path)
    print("got", len(disambugations), "disambugations")


if __name__ == "__main__":
    download_and_save_directions()
    check_all_properties_have_directions()
