
"""
    1- Firstly we give the root path to the city
    2- We get all NVT paths and we istantiate an object for each of them!
"""
import glob
import os.path
import shutil
import sys
from pathlib import Path
import time
import warnings

import pandas as pd
from openpyxl.reader.excel import load_workbook

from GraphManager import MicrosoftGraphNVTManager, GraphManager
from my_functions import log
from navigator import Navigator
from nvt import NVT


warnings.simplefilter(action='ignore', category=UserWarning)

""" 11.10.2022
    To be refactored:
    self.navigator and NAVIGATOR are the same object
"""

class City:
    name = None
    root_path = None
    navigator = None

    # list of nvts with their elements
    nvt_list = None # key: nvt_number, value: {path, place, nvt_telekom_list}
    nvt_path_list = None # contains all paths to nvt_folders

    def __init__(self, name, path, navigator):
        self.name = name
        self.root_path = Path(path)
        self.navigator = navigator
        self.nvt_list = []
        self.nvt_path_list = []

    def create_city_folder_tree(self):
        self.root_path.mkdir(parents=True, exist_ok=True)

    def initialize_nvt_dict_using_web_navigator_mg(self):
        """
            Here we are only talking about the json files:
            So what we need:
                1- All nvt names to use by filtering the Telekom UI
                2- All automated_data ids to upload the new json files
                3- All already existed json files to read them!
        """
        graph_manager = GraphManager()
        mg_nvts = graph_manager.get_nvt_ids(self.root_path)

        # Applying filter to be deleted later!
        # filtered_list = ["42V1016"] # "42V1014", "42V1011", "42V1013", "42V1014"
        # mg_nvts = [mg_nvt for mg_nvt in mg_nvts if mg_nvt["name"].replace("NVT ", "") in filtered_list]

        for mg_nvt in mg_nvts: # mg_nvt: a Microsoft Graph object contains id, name...
            # nvt_scrapping_done = False
            # while nvt_scrapping_done == False:
            try:
                nvt_path = self.root_path / mg_nvt["name"]
                nvt_number = mg_nvt["name"].replace("NVT ", "")
                log("Start scrapping NVT: " + str(nvt_number))
                #### Now we need nvt and nvt_mgm objects
                nvt_mgm = MicrosoftGraphNVTManager(graph_manager, mg_nvt, nvt_path)
                nvt = NVT(nvt_number=nvt_number, city=self, nvt_mgm=nvt_mgm)
                automated_folder_mg_obj = graph_manager.get_next_item_in_path(mg_nvt["id"], "automated_data")
                if automated_folder_mg_obj != None:
                    nvt_mgm.download_automated_data_folder(nvt.path)
                    if nvt.is_json_recently_updated():
                        log("NVT {} is already updated".format(nvt_mgm.nvt_number))
                        continue
                nvt.initialize_using_web_scrapper() # path is okay
                nvt_mgm.upload_nvt_json_file()
                nvt_mgm.upload_exploration_protocols_pdfs()
                self.nvt_list.append(nvt)
                self.navigator.click_reset_filter_button()
                # nvt_scrapping_done = True
            except Exception as e:
                assert 1 == 2 # quit the program, since we will not start with already updated nvts
                self.navigator = Navigator('dieaa.aled@dl-projects.de', 'dieaaALED123#@')
                self.navigator.take_screenshot()
                print("Exception: ", str(e))
                log("Repeat the scrapping process for NVT {}".format(mg_nvt["name"]))
                continue





    def load_nvt_dict_from_stored_json_mg(self, graph_manager):
        mg_nvts = graph_manager.get_nvt_ids(self.root_path)
        log("ATTENTION: Operations on this subcity will be on the following nvts: ")
        # To apply filter for test
        # mg_nvts = [mg_nvt for mg_nvt in mg_nvts if mg_nvt["name"] in ["NVT 42V1025", "NVT 42V1026"]]

        to_print_nvts = [mg_nvt["name"].replace("NVT ", "") for mg_nvt in mg_nvts]

        print(to_print_nvts)
        for mg_nvt in mg_nvts:
            nvt_path = self.root_path / mg_nvt["name"]
            nvt_mgm = MicrosoftGraphNVTManager(graph_manager, mg_nvt, nvt_path)
            nvt_mgm.download_automated_data_folder(nvt_path)

            log("Reading from json NVT: " + str(nvt_mgm.nvt_number))




            generated_json_path = nvt_mgm.get_nvt_json_path()
            nvt = NVT(nvt_mgm.nvt_number, city=self, nvt_mgm=nvt_mgm)
            if not os.path.exists(generated_json_path):
                log("No gbgs json for NVT {}".format(nvt_mgm.nvt_number))
                log("Creating empty NVT object for {}".format(nvt_mgm.nvt_number))
                nvt.create_empty_content()
            else:
                nvt.read_from_json()
            self.nvt_list.append(nvt)


    def update_montage_lists(self, nvts_to_update):
        for nvt in self.nvt_list:
            if len(nvts_to_update) > 0:
                if nvt.nvt_number in nvts_to_update:
                    nvt.generate_montage_excel()
            else:
                nvt.generate_montage_excel()



    def export_all_montage_to_one_df(self, montage_template_columns):
        dfs = []
        for nvt in self.nvt_list:
            df = nvt.montage_excel_parser.export_updated_addresses_to_df(montage_template_columns)
            df = df.fillna('').reset_index(drop=True)
            # df.insert(0, "NVT", [nvt.nvt_number for i in range(len(df))])
            df["NVT"] = [nvt.nvt_number for i in range(len(df))]
            dfs.append(df)

        if len(dfs) == 0:
            log("There is no Masterlist to generate")
            return None

        return pd.concat(dfs)


    def export_all_montage_to_one_excel(self, montage_template_columns):
        df = self.export_all_montage_to_one_df(montage_template_columns)
        if df == None:
            return
        saving_path_folder = Path(self.root_path) / "telekom_list"
        saving_path_folder.mkdir(parents=True, exist_ok=True)
        saving_path = saving_path_folder / "Masterliste_{}.xlsx".format(self.name)
        book = load_workbook(saving_path)  # assuming that the new template is there
        writer = pd.ExcelWriter(saving_path, engine='openpyxl')
        writer.book = book
        writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

        print("Log: Writing on Excel")

        sheet = book["HA_Auswertung"]
        sheet["A1"] = "All Montage: " + self.name

        df.to_excel(writer, index=False, startrow=7, startcol=0, sheet_name='HA_Auswertung', header=False)

        writer.save()

    def export_every_nvt_montage_telekom_excel_from_city_montage_telekom_excel(self):
        city_df = pd.read_excel(Path(self.root_path) / "telekom_list" / "telekom_addresses.xlsx", dtype={'postal': str})

        print(city_df)

        #### Creating the dictionary:
        nvt_dict = {}
        for i in range(len(city_df)):
            nvt = city_df.iloc[i]["nvt"]
            if nvt not in nvt_dict.keys():
                nvt_dict[nvt] = []
            else:
                nvt_dict[nvt].append(city_df.iloc[i])

        for nvt in self.nvt_list:
            if nvt.nvt_number in nvt_dict.keys():
                print("one series: ", nvt_dict[nvt.nvt_number][0])

                nvt_df = pd.DataFrame(nvt_dict[nvt.nvt_number])
                nvt_df.to_excel(nvt.path / "automated_data" / "telekom_addresses.xlsx", index=False)
            else:
                log("NVT {} is not existed in the city Telekom montage file!".format(nvt.nvt_number))


    def print(self):
        print("Details of city {} of path {}".format(self.name, self.root_path))
        for nvt in self.nvt_list:
            nvt.print()











