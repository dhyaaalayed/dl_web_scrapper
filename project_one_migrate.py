"""
    Just to migrate the data to a json dict
"""
import json
from pathlib import Path

from GraphManager import GraphManager
from city import City
from my_functions import parse_master_excel

import joblib

def get_city_from_path(path):
    """
        just to get the city name after rv and bvh from a path
        Example 1:
            Input: BAU/RV-08 Prignitz/BVH-01 Prignitz/Baupläne (HK+NVT)/2. Bad Wilsnack
            Output: 2. Bad Wilsnack
        Example 2:
            Input: BAU/RV-07 Dresden-Cottbus/BVH-02 Cottbus/Baupläne (HK+NVT)
            Output: Cottbus # taken from BVH
    """
    # 3: to delete BAU/RV/BVH
    elements = path.split("/")[3:]
    if len(elements) == 1: # the remaining element is Baupläne by assumption
        # then return BVH name, but delete BVH word from it
        # Example: BAU/RV-07 Dresden-Cottbus/BVH-02 Cottbus/Baupläne (HK+NVT)
        return " ".join(path.split("/")[2].split(" ")[1:])

    # then return the city which is not the Baupläne. Example: Baupläne (HK+NVT)/2. Bad Wilsnack
    # Another example: Cotta Ost/Baupläne (HK+NVT)
    return [elm for elm in elements if "Baupläne" not in elm][0]


def get_nvt_dict_from_hk_dict(hk_dict, nvt_number):
    for hk_key in hk_dict.keys():
        for nvt_key in hk_dict[hk_key].keys():
            if nvt_key == nvt_number:
                return nvt_key
    return None


def main():

    with open('city_config.json') as json_file:
        conf_dict = json.load(json_file)

    city_dict = conf_dict["cities"]
    templates_dict = conf_dict["templates"]
    master_number_of_columns = templates_dict["master_template"]["number_of_columns"] + 1 # + 1 because of the ansprechpartner cell :)
    migrated_data = {}
    """
        this contains the whole data in hirarichal format
        example:
        RV:{
            BVH:{
                City:{
                    HK:{
                        NVT:{
                            Address_1:{
    
                            }
                        }
                    }
                }
            }
        }
    """
    for bvh_key in city_dict.keys(): # city key is for the whole BVH area
        # city_key means bvh_key :)
        bvh_cfg = city_dict[bvh_key]
        if bvh_cfg["loading_json_activated"] == False:
            continue
        print("after continue city: {}".format(bvh_key))
        paths = bvh_cfg["paths"]
        for path in paths:


            rv = path.split("/")[1]
            bvh = path.split("/")[2]
            # 1- Add rv if it's not existed
            if rv not in migrated_data.keys():
                migrated_data[rv] = {}
            rv_dict = migrated_data[rv]

            # 2- Add bvh if it's not existed
            if bvh not in rv_dict.keys():
                rv_dict[bvh] = {}
            bvh_dict = rv_dict[bvh]

            city = get_city_from_path(path)
            # 2- Add city if it's not existed
            if city not in bvh_dict.keys():
                bvh_dict[city] = {}
            # sub_city_dict = bvh_dict[city]

            # city = City(name=city_key, path=path, navigator=None)
            graph_manager = GraphManager()

            # 3- Get the hk and nvt dict from graph manager
            bvh_dict[city] = graph_manager.get_nvt_ids_and_hk_city_bvh_rv_for_project_one(path)


            graph_manager.download_folder_files_by_id(id=bvh_cfg["master_storing_folder_id"],
                                                      path=bvh_cfg["bvh_master_storing_path"])
            bvh_storing_path: Path = Path(bvh_cfg["bvh_master_storing_path"]) / "Masterliste_{}.xlsx".format(bvh_key)
            bvh_df = parse_master_excel(bvh_storing_path, master_number_of_columns)

            for hk_key in bvh_dict[city].keys():
                hk_dict = bvh_dict[city][hk_key]
                for nvt_key in hk_dict.keys():
                    # gapminder[gapminder['year']==2002]
                    hk_dict[nvt_key] = bvh_df[bvh_df["NVT"] == nvt_key]
                    # get_nvt_df_from_bvh_df using pandas df features

    print("Finish:")
    print("migrated_data: ")
    print(migrated_data)
    with open("migrated_data.joblib", "wb") as handler:
        joblib.dump(migrated_data, handler)


    # To Load it: joblib.load("migrated_data.joblib")

if __name__ == "__main__":
    main()



