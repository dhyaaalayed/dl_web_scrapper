import json
 
# Opening JSON file
from city import City
from my_functions import log
from navigator import Navigator

with open('city_config.json') as json_file:
    conf_dict = json.load(json_file)
city_dict = conf_dict["cities"]

for city_key in city_dict.keys():
    city_obj = city_dict[city_key]
    if city_obj["scrapping_activated"] == True:
        log("Scrapping activated for {}".format(city_key))
        user_name = city_obj["user_name"]
        password = city_obj["password"]
        navigator = Navigator(user_name, password)
        for path in city_obj["paths"]:
            city = City(city_key, path, navigator)
            city.initialize_nvt_dict_using_web_navigator(already_downloaded_list=[])
            log("Finishing scrapping subcity of {} of path {}".format(city_key, path))


