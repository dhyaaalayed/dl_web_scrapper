import json

# Opening JSON file
from pathlib import Path

from GraphManager import GraphManager
from city import City
from my_functions import log
from navigator import Navigator
import shutil

with open('city_config.json') as json_file:
    conf_dict = json.load(json_file)
city_dict = conf_dict["cities"]

navigator = Navigator('dieaa.aled@dl-projects.de', 'dieaaALED123#@')


if Path("BAU").exists():
    log("Removing BAU folder")
    shutil.rmtree("BAU")
for city_key in city_dict.keys(): # city_key is the city name
    city_obj = city_dict[city_key]
    if city_obj["scrapping_activated"] == True:
        log("Scrapping activated for {}".format(city_key))
        for path in city_obj["paths"]:
            city = City(city_key, path, navigator)
            city.create_city_folder_tree()
            city.initialize_nvt_dict_using_web_navigator_mg()
            log("Finishing scrapping subcity of {} of path {}".format(city_key, path))
navigator.browser.close()



















                