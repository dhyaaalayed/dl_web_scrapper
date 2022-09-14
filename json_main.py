import json
 
# Opening JSON file
import shutil
from pathlib import Path
from uuid import uuid4

import pandas as pd

from city import City
from my_functions import log, get_template_columns, write_bvh_dfs_to_excel

with open('city_config.json') as json_file:
    conf_dict = json.load(json_file)

templates_dict = conf_dict["templates"]
montage_template_path = templates_dict["montage_template"]["path"]
montage_number_of_columns = templates_dict["montage_template"]["number_of_columns"]

master_template_path = templates_dict["master_template"]["path"]
master_number_of_columns = templates_dict["master_template"]["number_of_columns"]

montage_template_columns = get_template_columns(montage_template_path, montage_number_of_columns)
master_template_columns = get_template_columns(master_template_path, master_number_of_columns)

MASTER_STORING_PATH = Path("/Users/dlprojectsit/Library/CloudStorage/OneDrive-DLProjectsGmbH/BAU/gbgs_config/masterlists")
MASTER_TEMPLATE_PATH = Path("/Users/dlprojectsit/Library/CloudStorage/OneDrive-DLProjectsGmbH/BAU/gbgs_config/Templates/Montageliste_Template_Final - Master.xlsx")

city_dict = conf_dict["cities"]

nvt_archive_key = str(uuid4()).replace("-", "_")
for city_key in city_dict.keys(): # city key is for the whole BVH area
    city_obj = city_dict[city_key]
    if city_obj["loading_json_activated"] == False:
        continue
    print("after continue city: {}".format(city_key))
    paths = city_obj["paths"]
    bvh_dfs = []
    for path in paths:
        city = City(city_key, path, None)
        city.load_nvt_dict_from_stored_json()
        # city.export_every_nvt_montage_telekom_excel_from_city_montage_telekom_excel()
        for nvt in city.nvt_list:
            if nvt.nvt_number not in []:
                if city_obj["generating_ansprechpartner"] == True:
                    log("Operation on NVT {}:".format(nvt.nvt_number))
                    log("Generating ansprechpartner liste")
                    nvt.export_anshprechpartner_to_excel() # no need to archive the prev one

                if city_obj["updating_montage_activated"] == True:
                    log("Archiving current montage")
                    nvt.archive_montage_excel(nvt_archive_key)
                
                    log("Update montage excel")
                    nvt.initialize_montage_excel_parser()
                    nvt.montage_excel_parser.update_addresses_from_web()
               
                    #### To be called later:
                    nvt.montage_excel_parser.update_addresses_from_telekom_excel()
                
                    # Now using the new template:
                    log("Using the new Montage Excel template")
                    nvt.copy_montage_template_to_montage_excel_path(montage_template_path)
                    nvt.montage_excel_parser.export_current_data_to_excel(nvt.nvt_number, montage_template_columns)

        # log("Exporting Masterliste for {}".format(city.name))
        # city.copy_master_liste_template()
        # city.export_all_montage_to_one_excel(master_template_columns)
        df = city.export_all_montage_to_one_df(master_template_columns)
        bvh_dfs.append(df)
    log("Starting BVH process of {}".format(city_key))
    bvh_df = pd.concat(bvh_dfs)
    bvh_storing_path = MASTER_STORING_PATH / "Masterliste_{}.xlsx".format(city_key)
    shutil.copy(MASTER_TEMPLATE_PATH, bvh_storing_path)
    write_bvh_dfs_to_excel(bvh_storing_path, city_key , bvh_df) # Including copying template to the same path