import json
import webbrowser

with open("./good_properties.json", "r") as good_properties_json_file:
    properties = json.load(good_properties_json_file)

for bedroom_count in properties:
    for prop in properties[bedroom_count]:
        url = prop["property"]["url"]
        webbrowser.open(url)

