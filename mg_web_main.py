import json

# Opening JSON file
from GraphManager import GraphManager
from city import City
from my_functions import log
from navigator import Navigator
print("11111")
with open('city_config.json') as json_file:
    conf_dict = json.load(json_file)
city_dict = conf_dict["cities"]

navigator = Navigator("user_name", "password")

for city_key in city_dict.keys():
    city_obj = city_dict[city_key]
    if city_obj["scrapping_activated"] == True:
        log("Scrapping activated for {}".format(city_key))
        # user_name = city_obj["user_name"]
        # password = city_obj["password"]
        for path in city_obj["paths"]:

            path = path.replace("/Users/dlprojectsit/Library/CloudStorage/OneDrive-DLProjectsGmbH/", "")

            city = City(city_key, path, navigator)

            graph_manager = GraphManager()
            # nvt_mg_list = graph_manager.get_nvt_ids("BAU/RV-07 Dresden-Cottbus/BVH-01 Dresden Cotta/Cotta Ost/Baupläne (HK+NVT)")


            city.initialize_nvt_dict_using_web_navigator_mg(graph_manager)
            log("Finishing scrapping subcity of {} of path {}".format(city_key, path))


