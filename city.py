
"""
    1- Firstly we give the root path to the city
    2- We get all NVT paths and we istantiate an object for each of them!
"""
import glob
from pathlib import Path
import time
import warnings

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
        self.nvt_path_list = [Path(path) for path in glob.glob(self.root_path + "/*/*") if "NVT" in Path(path).stem]

    def initialize_nvt_dict_using_web_navigator(self, already_downloaded_list = []):
        log("Start: initialize_nvt_dict")
        
        for nvt_path in self.nvt_path_list:
            # hk_number = nvt_path.parent.stem.split("+")[0].replace("HK ", "").replace(" ", "") # There is no need to it
            nvt_number = nvt_path.stem.replace("NVT " ,"")
            if nvt_number in already_downloaded_list and len(already_downloaded_list) > 0:
                log(str(nvt_number) + " is already downloaded!")
                log("Moving to the next one...")
            else:
                log("Start scrapping NVT: " + str(nvt_number))
                nvt = NVT(nvt_number, nvt_path, city = self.name, navigator = self.navigator)
                nvt.initialize_using_web_scrapper()
                self.nvt_list.append(nvt)
                self.navigator.click_reset_filter_button()
                log("Reseting current nvt list filter")
                time.sleep(5)
                print("____________________________________")
                print("____________________________________")

    def load_nvt_dict_from_stored_json(self):
        for nvt_path in self.nvt_path_list:
            nvt_number = nvt_path.stem.replace("NVT " ,"")
            log("Parsed nvt_number: " + nvt_number)
            log("Parsed nvt_path: " + str(nvt_path))
            nvt = NVT(nvt_number, nvt_path, city = self.name, navigator = None)
            nvt.read_from_json()
            log("nvt_number after json: " + nvt_number)
            log("nvt_path after json: " + str(nvt_path))
            self.nvt_list.append(nvt)

    def update_montage_lists(self, nvts_to_update):
        for nvt in self.nvt_list:
            if len(nvts_to_update) > 0:
                if nvt.nvt_number in nvts_to_update:
                    nvt.generate_montage_list_files()
            else:
                nvt.generate_montage_list_files()

    def print(self):
        print("Details of city {} of path {}".format(self.name, self.root_path))
        for nvt in self.nvt_list:
            nvt.print()











