
"""
    1- Firstly we give the root path to the city
    2- We get all NVT paths and we istantiate an object for each of them!
"""
import glob
import os.path
import shutil
from pathlib import Path
import time
import warnings

import pandas as pd
from openpyxl.reader.excel import load_workbook

from GraphManager import MicrosoftGraphNVTManager
from my_functions import log
from nvt import NVT


warnings.simplefilter(action='ignore', category=UserWarning)


class City:
    name = None
    root_path = None
    navigator = None

    # list of nvts with their elements
    nvt_list = None # key: nvt_number, value: {path, place, nvt_telekom_list}
    nvt_path_list = None # contains all paths to nvt_folders

    def __init__(self, name, path, navigator):
        self.name = name
        self.root_path = path
        self.navigator = navigator
        self.nvt_list = []
        self.nvt_path_list = []

    def initialize_nvt_dict_using_web_navigator_mg(self, graph_manager):
        """
            Here we are only talking about the json files:
            So what we need:
                1- All nvt names to use by filtering the Telekom UI
                2- All automated_data ids to upload the new json files
                3- All already existed json files to read them!
        """
        mg_nvts = graph_manager.get_nvt_ids(self.root_path)

        for mg_nvt in mg_nvts:

            nvt_mgm = MicrosoftGraphNVTManager(graph_manager, mg_nvt)
            log("Start scrapping NVT: " + str(nvt_mgm.nvt_number))
            nvt_number = mg_nvt["name"].replace("NVT ", "")
            nvt = NVT(nvt_number, path="None", city=self.name, navigator=self.navigator)

            if nvt_mgm.automated_data_folder_mg_obj != None:
                nvt_mgm.download_automated_data_folder()
                if nvt.is_json_recently_updated(nvt_mgm.nvt_download_path / "automated_data" / "nvt_telekom_data.json" ):
                    log("NVT {} is already updated".format(nvt_mgm.nvt_number))
                    continue
            nvt.initialize_using_web_scrapper(nvt_mgm.nvt_to_upload_path / "automated_data")
            nvt_mgm.upload_nvt_json_file()
            self.nvt_list.append(nvt)
            self.navigator.click_reset_filter_button()

    def initialize_nvt_dict_using_web_navigator(self, already_downloaded_list = []):
        log("Start: initialize_nvt_dict")
        self.nvt_path_list = [Path(path) for path in glob.glob(self.root_path + "/*/*") if "NVT" in Path(path).stem]
        for nvt_path in self.nvt_path_list:
            # hk_number = nvt_path.parent.stem.split("+")[0].replace("HK ", "").replace(" ", "") # There is no need to it
            nvt_number = nvt_path.stem.replace("NVT ", "")
            if nvt_number not in already_downloaded_list:
                log("Start scrapping NVT: " + str(nvt_number))
                nvt = NVT(nvt_number, nvt_path, city = self.name, navigator = self.navigator)
                if nvt.is_json_recently_updated():
                    log("NVT {} is already updated".format(nvt_number))
                    continue
                nvt.initialize_using_web_scrapper()
                self.nvt_list.append(nvt)
                self.navigator.click_reset_filter_button()
                log("Reseting current nvt list filter")
                print("____________________________________")
                print("____________________________________")

    def load_nvt_dict_from_stored_json(self):
        # initialize the list using installed one drive app
        self.nvt_path_list = [Path(path) for path in glob.glob(self.root_path + "/*/*") if "NVT" in Path(path).stem]
        for nvt_path in self.nvt_path_list:

            nvt_number = nvt_path.stem.replace("NVT ", "")
            nvt_json = nvt_path / "automated_data" / "nvt_telekom_data.json"
            if os.path.exists(nvt_json):
                log("Parsed nvt_number: " + nvt_number)
                log("Parsed nvt_path: " + str(nvt_path))
                nvt = NVT(nvt_number, nvt_path, city = self.name, navigator = None)
                nvt.read_from_json()
                log("nvt_number after json: " + nvt_number)
                log("nvt_path after json: " + str(nvt_path))
                self.nvt_list.append(nvt)

    def load_nvt_dict_from_stored_json_mg(self, graph_manager):
        mg_nvts = graph_manager.get_nvt_ids(self.root_path)
        for mg_nvt in mg_nvts:

            nvt_mgm = MicrosoftGraphNVTManager(graph_manager, mg_nvt)
            nvt_mgm.download_automated_data_folder()

            log("Reading from json NVT: " + str(nvt_mgm.nvt_number))

            nvt = NVT(nvt_mgm.nvt_number, path="None", city=self.name, navigator=self.navigator)
            # if nvt.is_json_recently_updated(nvt_mgm.nvt_download_path / "automated_data" / "nvt_telekom_data.json" ):
            #     log("NVT {} is already updated".format(nvt_mgm.nvt_number))
            #     continue
            nvt.read_from_json(nvt_mgm.nvt_to_upload_path / "automated_data" / "nvt_telekom_data.json")
            nvt.nvt_mgm = nvt_mgm
            # then uploading the updated fies:
            # nvt_mgm.upload_nvt_json_file()
            self.nvt_list.append(nvt)


    def update_montage_lists(self, nvts_to_update):
        for nvt in self.nvt_list:
            if len(nvts_to_update) > 0:
                if nvt.nvt_number in nvts_to_update:
                    nvt.generate_montage_excel()
            else:
                nvt.generate_montage_excel()


    def copy_master_liste_template(self):
        saving_path_folder = Path(self.root_path) / "telekom_list"
        saving_path_folder.mkdir(parents=True, exist_ok=True)
        saving_path = saving_path_folder / "Masterliste_{}.xlsx".format(self.name)
        shutil.copy("/Users/dlprojectsit/Library/CloudStorage/OneDrive-DLProjectsGmbH/BAU/gbgs_config/Templates/Montageliste_Template_Final - Master.xlsx", saving_path)


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











