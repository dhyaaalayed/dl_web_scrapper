"""
    TODO Here:

        1- Download Montagetemplate only once
        By calling graph manager for that
        then, copy it normally to each nvt folder...

        2- Same for other files like:
            Master template, telekom_address_list of a city of BVH or subcity...

        3- Move MasterStoringPath to the shared folder of each sicty
            put their names in the config, then get their mg ids...

        4- Adding uploading step after each generating step!

    Plan TODO:
        1- test the current without uploading
        2- check out the generated files and the archive folders
"""
import datetime
import json

import shutil
from datetime import date
from pathlib import Path
from uuid import uuid4

import pandas as pd
import sys

from GraphManager import GraphManager
from city import City
from my_functions import log, get_template_columns, write_bvh_dfs_to_excel

def main():
    with open('city_config.json') as json_file:
        conf_dict = json.load(json_file)
    #
    templates_dict = conf_dict["templates"]
    montage_template_path: Path = Path(templates_dict["montage_template"]["path"])
    montage_number_of_columns = templates_dict["montage_template"]["number_of_columns"]
    #
    master_template_path: Path = Path(templates_dict["master_template"]["path"])
    master_number_of_columns = templates_dict["master_template"]["number_of_columns"]
    # TODO: Download Montage and Master templates in the same path of the config or change the path...
    graph_manager = GraphManager()
    # 1- Getting templates objects of microsoft graph
    master_template_mg_obj = graph_manager.get_path_mg_obj(master_template_path)
    montage_template_mg_obj = graph_manager.get_path_mg_obj(montage_template_path)
    # 2- Downloading templates by using their ids
    graph_manager.download_file(master_template_mg_obj, master_template_path.parent) # to download it in the parent folder, not to create a new folder of the file name and put the file in it!
    graph_manager.download_file(montage_template_mg_obj, montage_template_path.parent)
    # 3- Getting template columns
    montage_template_columns = get_template_columns(montage_template_path, montage_number_of_columns)
    master_template_columns = get_template_columns(master_template_path, master_number_of_columns)
    #
    city_dict = conf_dict["cities"]
    #
    nvt_archive_key = str(uuid4()).replace("-", "_")
    archive_date = date.today().strftime('%Y_%m_%d')
    #
    #
    for city_key in city_dict.keys(): # city key is for the whole BVH area
        city_obj = city_dict[city_key]
        if city_obj["loading_json_activated"] == False:
            continue
        print("after continue city: {}".format(city_key))
        paths = city_obj["paths"]
        bvh_dfs = []
        for path in paths:
            city = City(name=city_key, path=path, navigator=None)
            graph_manager = GraphManager()
            city.load_nvt_dict_from_stored_json_mg(graph_manager)
            for nvt in city.nvt_list:
                if 1 not in []:
                    if city_obj["generating_ansprechpartner"] == True:
                        log("Operation on NVT {}:".format(nvt.nvt_number))
                        log("Generating ansprechpartner liste")
                        nvt.export_anshprechpartner_to_excel() # no need to archive the prev one
                        nvt.nvt_mgm.upload_ansprechspartner_excel()
                    if city_obj["updating_montage_activated"] == True:
                        log("Archiving current montage")
                        nvt.nvt_mgm.archive_montage_excel(archive_date=archive_date, generated_unique_key=nvt_archive_key) # change the body of it to call the one that I created
                        log("Update montage excel")
                        nvt.nvt_mgm.download_montage_excel()
                        nvt.initialize_montage_excel_parser()
                        nvt.montage_excel_parser.update_addresses_from_web()
                        nvt.montage_excel_parser.update_addresses_from_telekom_excel()
                        # Now using the new template:
                        log("Using the new Montage Excel template")
                        # It's already downloaded for every nvt, we just need to copy it
                        nvt.copy_montage_template_to_montage_excel_path(montage_template_path)
                        nvt.montage_excel_parser.export_current_data_to_excel(nvt.nvt_number, montage_template_columns)
                        log("Finally: Uploading Generated Montage Excel")
                        nvt.nvt_mgm.upload_montage_excel()
            # log("Exporting Masterliste for {}".format(city.name))
            # city.copy_master_liste_template()
            # city.export_all_montage_to_one_excel(master_template_columns)
            df = city.export_all_montage_to_one_df(master_template_columns)
            bvh_dfs.append(df)
        log("Starting BVH process of {}".format(city_key))
        # Just small filter for the bvh_dfs:
        bvh_dfs = [bvh_df for bvh_df in bvh_dfs if bvh_df is not None]
        if len(bvh_dfs) > 0:
            bvh_df = pd.concat(bvh_dfs)
            # city_master_storing_path = graph_manager.get_path_id()
            bvh_storing_path: Path = Path(city_obj["bvh_master_storing_path"]) / "Masterliste_{}.xlsx".format(city_key)
            shutil.copy(master_template_path, bvh_storing_path)
            write_bvh_dfs_to_excel(bvh_storing_path, city_key, bvh_df) # Including copying template to the same path
            graph_manager.upload_file(local_path=bvh_storing_path, drive_folder_id=city_obj["master_storing_folder_id"])
        else:
            log("No Montageliste to generate the Masterlist")


if __name__ == "__main__":
    log("Starting updating excel files service")
    log("We will execute the service in the midnight")
    while True:
        current_time = datetime.datetime.now()
        current_time_number = current_time.hour + current_time.minute/100
        if 0.4 < current_time_number < 0.5:
            main()




