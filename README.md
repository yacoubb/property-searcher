# property-searcher

Python script used to check [Rightmove](https://www.rightmove.co.uk/) for new properties that meet user-specified search criteria.

## Requirements

You'll need a TFL api key and app id, get a pair from the [TFL website](https://api.tfl.gov.uk/). Once you have both, add them to `credentials.json` under the keys `tfl_app_key` and `tfl_app_id`.

Then make sure you have the rightmove python package installed - `pip install rightmove-webscraper`

## Perform a filtered search

Start by editing `search_criteria.json` to match your requirements. When you set the location make sure to add it's rightmove code to `location_index.json`. Location codes can be got from rightmove URLs, if you go on rightmove and search for properties in a location the location code will show up in the URL.

When you run `get_rightmove_properties.py` the results are saved in a folder locally, so if you try lots of different filters you don't have to run the webscraper multiple times.

Run `get_rightmove_properties.py`

Then `get_directions.py`

Then `property_filter.py`

And the results will end up in `good_properties.json`. Open them all simletaneously by running `open_properties_in_browser.py`
