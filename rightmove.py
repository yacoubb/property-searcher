import json
import sys
import os

app_id = "187f5018"
app_key = "a6f6f11944e68b4c571b358fe9a8bffa"
max_duration = 40
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
            if leg[0] == "walk" and leg[2] > max_walk_duration:
                good_route = False
        if not good_route:
            continue

        # if we have to take a tube and a bus or vice versa
        if len(list(filter(lambda x: x[1] != "walk", routes[i]["legs"]))) < 2:
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
        properties.append((prop, routes))
    return properties


if __name__ == "__main__":
    print("loading properties")
    properties = load_properties()
    properties = list(filter(lambda x: len(check_routes(x[1])) > 0, properties))
    properties = list(filter(lambda x: x[0]["weekly_price_per_head"] < 180, properties))
    parsed = {4: [], 5: []}
    for prop, routes in properties:
        routes = check_routes(routes)
        parsed[int(prop["number_bedrooms"])].append(
            {"property": prop, "routes": routes}
        )
    for key in parsed:
        parsed[key] = sorted(
            parsed[key], key=lambda x: x["property"]["weekly_price_per_head"]
        )
    print("found", len(properties), "properties")
    with open("good_properties.json", "w+") as good_json:
        good_json.write(json.dumps(parsed, indent=4))

