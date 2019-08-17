import json
import sys
import os

max_duration = 60
max_walk_duration = 40


def check_routes(routes):
    valid_routes = []
    for i in range(len(routes)):
        # if the total travel time is more than the max duration
        if routes[i]["total_duration"] > max_duration:
            continue

        # if we have to do any more than walk, bus/tube, walk
        if len(routes[i]["legs"]) > 3:
            continue

        # if any of the walk components are longer than max walk duration
        good_route = True
        for leg in routes[i]["legs"]:
            if leg["type"] == "walk" and leg["duration"] > max_walk_duration:
                good_route = False
        if not good_route:
            continue

        # if we have to take a tube and a bus or vice versa
        if len(list(filter(lambda x: x["type"] != "walk", routes[i]["legs"]))) > 1:
            continue

        valid_routes.append(routes[i])
    return valid_routes


def load_properties():
    property_paths = []
    with open("property_index.json", "r") as index_file:
        property_paths = json.load(index_file)

    properties = []
    for path in property_paths:
        prop = json.load(open(path + "/property.json", "r"))
        routes = []
        i = 0
        while os.path.exists(path + "/route_" + str(i) + ".json"):
            routes.append(json.load(open(path + "/route_" + str(i) + ".json", "r")))
            i += 1
        properties.append((prop, routes, path))
    return properties


if __name__ == "__main__":
    print("loading properties")
    properties = load_properties()
    properties = list(filter(lambda x: len(check_routes(x[1])) > 0, properties))
    properties = list(filter(lambda x: x[0]["weekly_price_per_head"] < 180, properties))
    parsed = {4: [], 5: []}
    for prop, routes, path in properties:
        routes = check_routes(routes)
        if not int(prop["number_bedrooms"]) in parsed:
            parsed[int(prop["number_bedrooms"])] = []
        parsed[int(prop["number_bedrooms"])].append(
            {"path": path, "property": prop, "routes": routes}
        )
    for key in parsed:
        parsed[key] = sorted(
            parsed[key], key=lambda x: x["property"]["weekly_price_per_head"]
        )
    print("found", len(properties), "properties")
    with open("good_properties.json", "w+") as good_json:
        good_json.write(json.dumps(parsed, indent=4))

