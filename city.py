
"""
    1- Firstly we give the root path to the city
    2- We get all NVT paths and we istantiate an object for each of them!
"""
import shutil

from navigator import Navigator
import os
import glob
from pathlib import Path
import time
import pandas as pd
import json
from entities import Kls, Address, Person, Owner
from montage_master_package import MontageExcelParser
import numpy as np
from datetime import date
from uuid import uuid4


def log(message):
    print("Log: " + message)

import warnings

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

class NVT:
    nvt_number = None
    path = None
    city = None
    kls_list = None
    navigator = None

    def __init__(self, nvt_number, path, city, navigator): # Dresden
        log("Start NVT Constructor")
        self.nvt_number = nvt_number
        self.path = path
        self.city = city
        self.navigator = navigator
        self.nvt_telekom_list = []
        self.kls_list = []
        # self.initialize_using_web_scrapper()

    def initialize_using_web_scrapper(self):
        self.filter_in_kls_list()
        self.visit_eyes_pages()
        log("Finishing reading the whole KLS")
        log("Printing kls details..........")
        self.print()
        self.write_to_json()

    def filter_in_kls_list(self):
        log("Start filtering in kls list according to nvt_number: " + self.nvt_number)
        self.navigator.filter_according_to_nvt_number(self.nvt_number)

        log("Clicking the search button")
        self.navigator.click_the_search_button()



    def visit_eyes_pages(self):
        for i in range(1, 1000):
            self.navigator.log_number_of_eyes_of_current_page(i)

            kls_list = self.visit_current_eyes_page()
            self.kls_list += kls_list
            print("self.kls_list: ", self.kls_list)

            if not self.navigator.navigate_to_next_page(i + 1):
                break

    def visit_current_eyes_page(self):
        """ Gets the kls_dicts of the eyes of the current page
        """
        return self.navigator.get_eyes_data(self.nvt_number) # return a kls object

    def get_address_list(self):
        return [kls.address for kls in self.kls_list]

    def get_new_address_for_montage_list(self):
        #Montageliste_1018.xlsx
        montage_file = "Montageliste_{}.xlsx".format(self.nvt_number)
        montage_path = Path(self.path) / montage_file

        self.montage_excel_parser = MontageExcelParser(montage_path, self.get_address_list())
        new_montage_address_list = self.montage_excel_parser.get_new_address_list()
        print("new address at nvt: {}".format(self.nvt_number))
        if len(new_montage_address_list) > 0:
            for address in new_montage_address_list:
                address.print()
        else:
            print("There is no new addresses")
        print("___________________\n")

    def get_montage_list_parser(self):
        montage_file = "Montageliste_{}.xlsx".format(self.nvt_number)
        montage_path = Path(self.path) / montage_file
        return MontageExcelParser(montage_path, self.get_address_list())

    def generate_montage_list_files(self):
        # self.get_new_address_for_montage_list()
        montage_excel_parser = self.get_montage_list_parser()
        montage_excel_parser.generate_new_address_list_file()

    def update_montage_list_files(self):
        montage_excel_parser = self.get_montage_list_parser()
        montage_excel_parser.update_current_montage_list_file()

    def print(self):
        print(">>>>>> printing klses of nvt: {} >>>>>>>>>".format(self.nvt_number))
        for kls in self.kls_list:
            print("===== printing address, people, owners of kls: {} ==========".format(kls.id))
            print("Address: ")
            kls.address.print()
            print("Contact People: ")
            for person in kls.people:
                person.print()
                print()
            print("Owners: ")
            for owner in kls.owners:
                print("Owner: ")
                owner.print()
                print()
            print("\n\n\n\n")
        print("\n\n\n\n")
        print("________________________________")
        print("_____End Printing NVT {}_____".format(self.nvt_number))
        print("________________________________")
        print("\n\n\n\n")

    def export_to_json(self):
        nvt_json = self.__dict__.copy()
        del nvt_json["navigator"]
        nvt_json["path"] = str(nvt_json["path"])
        nvt_json["kls_list"] = [kls.export_to_json() for kls in self.kls_list]
        print ("nvt_json: ", nvt_json)
        return nvt_json
        # return {
        #     "nvt_number": self.nvt_number,
        #     "path": str(self.path),
        #     "city": self.city,
        #     "nvt_telekom_list": self.nvt_telekom_list,
        #     "kls_list": self.kls_list,
        # }

    def import_from_json(self, kls_json):
        # self.nvt_number = kls_json["nvt_number"]
        # self.path = kls_json["path"]
        # self.city = kls_json["city"]
        self.nvt_telekom_list = kls_json["nvt_telekom_list"]
        self.kls_list = []

        # To be deleted self.kls_dicts = kls_json["kls_dicts"]
        for kls_json_obj in kls_json["kls_list"]:

            # print(str(kls_json["kls_dicts"]))
            # print(str(kls_json_obj))
            # print(type(kls_json_obj))
            kls_json_obj = json.loads(kls_json_obj)
            kls = Kls(
                kls_json_obj["id"],
                Address(kls_json_obj["address"]),
                [Person(person_json) for person_json in kls_json_obj["people"]],
                [Owner(owner_json) for owner_json in kls_json_obj["owners"]]
                )
            kls.address.htn = kls_json_obj["htn"]
            self.kls_list.append(kls)

    def write_to_json(self):
        json_obj = self.export_to_json()
        store_path = self.path / 'automated_data'
        Path(store_path).mkdir(parents=True, exist_ok=True)
        with open(store_path / 'nvt_telekom_data.json', 'w') as f:
            json.dump(json_obj, f)

        log("Storing nvt json at: " + str(store_path / 'nvt_telekom_data.json'))

    def read_from_json(self):
        log("Start reading nvt {} from json file".format(self.nvt_number))
        json_path = self.path / 'automated_data' / 'nvt_telekom_data.json'
        log("path: " + str(json_path))
        with open(json_path) as json_file:
            kls_json = json.load(json_file)
        self.import_from_json(kls_json)

    # def add_new_columns(self):

    def archive_montage_list(self):
        # Just copy it and put it in archive folder
        montage_scr_path = self.path / "Montageliste_{}.xlsx".format(self.nvt_number)
        montage_dest_path = self.path / "Archive" / "montage_liste" / date.today().strftime('%Y_%m_%d')
        montage_dest_path.mkdir(parents=True, exist_ok=True)
        montage_dest_path = montage_dest_path / "Montageliste_{}_{}.xlsx".format(self.nvt_number, str(uuid4()).replace("-", "_"))
        shutil.copy(montage_scr_path, montage_dest_path)

    def rename_montage_liste_files(self):
        montage_list_current_name = "updated_Montageliste_{}.xlsx".format(self.nvt_number[-4:])
        montage_list_new_name = "Montageliste_{}.xlsx".format(self.nvt_number)
        os.rename(self.path / montage_list_current_name, self.path / montage_list_new_name)
    def archive_human_created_files(self):
        # start with montage liste
        log("Archiving for {}".format(str(self.nvt_number)))
        log("The path is: " + str(self.path))
        ansprechpartnerListe_file_name = "AnsprechpartnerListe_{}.xlsx".format(self.nvt_number[-4:])
        ansprechpartnerListe_src_path = Path(self.path) / ansprechpartnerListe_file_name
        ansprechpartnerListe_dest_path = Path(self.path) / "Archive" / "ansprechpartner_liste" / "human_created"
        ansprechpartnerListe_dest_path.mkdir(parents=True, exist_ok=True)
        ansprechpartnerListe_dest_path = ansprechpartnerListe_dest_path / ansprechpartnerListe_file_name

        montage_list_file_name = "Montageliste_{}.xlsx".format(self.nvt_number[-4:])
        montage_list_src_path =  Path(self.path) / montage_list_file_name
        montage_list_dist_path = Path(self.path) / "Archive" / "montage_liste" / "human_created"
        montage_list_dist_path.mkdir(parents=True, exist_ok=True)
        montage_list_dist_path = montage_list_dist_path / montage_list_file_name

        shutil.move(ansprechpartnerListe_src_path, ansprechpartnerListe_dest_path)
        shutil.move(montage_list_src_path, montage_list_dist_path)

    def export_anshprechpartner_to_excel(self):
        df = self.get_anshprechpartner_dataframe()
        path = Path(self.path) / "generated_anshprechpartner_list_{}.xlsx".format(self.nvt_number)
        # df.to_excel(path, engine='xlsxwriter')
        measurer = np.vectorize(len)
        columns_max_length = measurer(df.values.astype(str)).max(axis=0)
        with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
            sheet_name = "AnsprechpartnerListe_{}".format(self.nvt_number)
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            for idx, column in enumerate(df.columns):
                writer.sheets[sheet_name].set_column(idx, idx, columns_max_length[idx])
            writer.save()

    def get_anshprechpartner_dataframe(self):
        klsid = []
        ort = []
        strasse = []
        rolle = []
        name = []
        person_ort = []
        person_street = []
        telefon = []
        mobile = []
        email = []
        for kls in self.kls_list:
            address = kls.address
            people = kls.people
            owners_list = kls.owners
            for person in people:
                klsid.append(kls.id)
                ort.append(address.postal + " " + address.city)
                strasse.append(address.street + " " + address.house_number + address.house_char)
    
                rolle.append(person.role)
                name.append(person.name)
                person_ort.append("") # no ort for contact person!
                person_street.append("") # no street
                telefon.append(person.fixedline)
                mobile.append(person.mobile)
                email.append(person.email)
    
            for owner in owners_list:
                klsid.append(kls.id)
                ort.append(address.postal + " " + address.city)
                strasse.append(address.street + " " + address.house_number + address.house_char)
    
                rolle.append("Inhaber")
                name.append(owner.name)
                person_ort.append(owner.postcode + " " + owner.city)
                person_street.append(owner.street + " " + owner.housenumber)
                telefon.append(owner.linenumber)
                mobile.append(owner.mobil)
                email.append(owner.email)
    
        return pd.DataFrame(data={
            "KLSID": klsid,
            "Ort": ort,
            "Strasse": strasse,
            "Rolle": rolle,
            "Name": name,
            "Ort2": person_ort,
            "Strasse2": person_street,
            "Telefon": telefon,
            "Mobile": mobile,
            "email": email
            })


class LoadFromWebMain:
    """
        City class is only used, when we load the data for the first time, or when we want to overwrite the current json files
    """
    
    cities = []
    navigator = None

    def __init__(self, root_paths):
        self.navigator = Navigator()
        for path in root_paths:
            city = City("Dresden", path, self.navigator)

            already_downloaded_list = ["1016", "1015", "1030", "1018", "1019", "1014", "1011", "1010", "1012"]
            city.initialize_nvt_dict_using_web_navigator(already_downloaded_list = [])
            self.cities.append(city)



class LoadFromJson:
    cities = []
    navigator = None
    def __init__(self, root_paths):
        for path in root_paths:
            city = City("Dresden", path, self.navigator)
            city.load_nvt_dict_from_stored_json()
            nvts_to_update = []
            # city.update_montage_lists(nvts_to_update)
            self.cities.append( city )

            # to generate new montage liste files without templates
            # for nvt in city.nvt_list:
            #     nvt.export_anshprechpartner_to_excel()
                # nvt.clean_generated_anshprechpartner_files()
                # nvt.clean_generated_montage_list_files()

            # to update current montage liste files and copy the old ones
            for nvt in city.nvt_list:
                if nvt.nvt_number in []:
                    continue
                log("Renaming in nvt" + str(nvt.path))
                nvt.rename_ansprech_files()

        # for city in self.cities:
            # Update MasterListe



if __name__ == "__main__":
    roots_list = [
          "/Users/dlprojectsit/Library/CloudStorage/OneDrive-SharedLibraries-DLProjectsGmbH/Data Management DL Projects - BAU/RV-07 Dresden/BVH-01 Dresden Cotta/Cotta West/Baupläne (HK+NVT)"
        , "/Users/dlprojectsit/Library/CloudStorage/OneDrive-SharedLibraries-DLProjectsGmbH/Data Management DL Projects - BAU/RV-07 Dresden/BVH-01 Dresden Cotta/Cotta Ost/Baupläne (HK+NVT)"
        ]
    # 1- If we want to load from web
    LoadFromWebMain(roots_list)

    # 2- If we want to load from jsons
    # main = LoadFromJson(roots_list)

