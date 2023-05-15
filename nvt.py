import glob
import shutil
import os
from pathlib import Path
import pandas as pd
import json

from GraphManager import MicrosoftGraphNVTManager
from entities import Kls, Address, Person, Owner
from montage_master_package import MontageExcelParser, AnspreschpartnerExcelGenerator
import numpy as np
from datetime import date, datetime
from uuid import uuid4
from my_functions import log


class NVT:
    def __init__(self, nvt_number: str, city: "City", nvt_mgm: MicrosoftGraphNVTManager):
        log("Start NVT Constructor")
        self.nvt_number = nvt_number
        self.path = Path(city.root_path) / "NVT {}".format(nvt_number)
        self.city = city.name
        self.kls_list = None
        self.navigator = city.navigator
        self.montage_excel_path = self._get_montage_excel_path()
        self.montage_excel_parser = None
        self.anspreschpartner_excel_generator = None
        self.nvt_mgm: MicrosoftGraphNVTManager = nvt_mgm # MicrosoftGraphNVTManager objcet, used only by mg_json_main when we run the code in the cloud
        self.ibt_addresses = []
        self.ibt_installed_addresses = []

    def initialize_using_web_scrapper(self):

        #### Getting data from the navigator
        # We need to give the path parameter to get_all_nvt_data function in order
        # to download the Auskundigungprotocol at it
        already_download_exploration_protocols = self.get_already_download_exploration_protocols()
        self.kls_list = self.navigator.get_all_nvt_data(self.nvt_number, self.path, already_download_exploration_protocols)
        if self.kls_list == None:
            return []
        log("Finishing reading the whole KLS")
        log("Printing kls details..........")
        self.print()

    def filter_in_property_search_result_according_to_bvh_filters(self, cities_filters):
        self.kls_list = [kls for kls in self.kls_list if kls.address.city in cities_filters]

    def initialize_ibt_using_web_scrapper(self):
        addresses = self.navigator.get_all_nvt_data(self.nvt_number, "", [])
        if addresses == None:
            return []
        return addresses

    def filter_in_ibt_addresses_according_to_bvh_cities(self, ibt_addresses, cities_filters):
        return [address for address in ibt_addresses if address["city"] in cities_filters]

    def download_automated_data_folder(self):
        automated_data_path = self.path / "automated_data"
        automated_data_path.mkdir(parents=True, exist_ok=True)
        # 1- Downloading automated_folder

        automated_data_mg_obj_items = self.graph_manager.get_folder_items_by_id(self.automated_data_folder_mg_obj["id"])
        for item in automated_data_mg_obj_items:
            self.graph_manager.download_file(item, self.nvt_download_path / "automated_data")

        # 2- Download montage excel file
        montage_excel_mg_obj = self.graph_manager.get_next_item_in_path(self.nvt_mg_obj["id"], "Montageliste_{}.xlsx".format(self.nvt_number))
        self.graph_manager.download_file(montage_excel_mg_obj, self.nvt_download_path)

    def get_address_list_from_json(self):
        print("kls_list: ", len(self.kls_list))
        return [kls.address for kls in self.kls_list]

    def get_new_address_for_montage_list(self):
        # Montageliste_1018.xlsx
        montage_file = "Montageliste_{}.xlsx".format(self.nvt_number)
        montage_path = Path(self.path) / montage_file

        self.montage_excel_parser = MontageExcelParser(montage_path, self.get_address_list_from_json())
        new_montage_address_list = self.montage_excel_parser.get_new_address_list()
        print("new address at nvt: {}".format(self.nvt_number))
        if len(new_montage_address_list) > 0:
            for address in new_montage_address_list:
                address.print()
        else:
            print("There is no new addresses")
        print("___________________\n")


    def _get_montage_excel_path(self):
        montage_file = "Montageliste_{}.xlsx".format(self.nvt_number)
        montage_path = Path(self.path) / montage_file
        return montage_path

    def initialize_anspreschpartner_excel_generator(self, bulk_addresses_dict, montage_excel_addresses):
        self.anspreschpartner_excel_generator = AnspreschpartnerExcelGenerator(self.kls_list)
        self.anspreschpartner_excel_generator.match_addresses_from_bulk_addresses(bulk_addresses_dict, montage_excel_addresses)


    def initialize_montage_excel_parser(self):
        montage_file = "Montageliste_{}.xlsx".format(self.nvt_number)
        montage_path = Path(self.path) / montage_file
        self.montage_excel_parser = MontageExcelParser(montage_path, self.get_address_list_from_json())

    def generate_montage_excel(self):
        # self.get_new_address_for_montage_list()
        montage_excel_parser = self.initialize_montage_excel_parser()
        montage_excel_parser.generate_new_address_list_file()

    def update_montage_excel(self):
        montage_excel_parser = self.initialize_montage_excel_parser()
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
        del nvt_json["montage_excel_parser"]
        del nvt_json["montage_excel_path"]
        del nvt_json["navigator"]
        del nvt_json["nvt_mgm"]
        del nvt_json["city"]
        nvt_json["path"] = str(nvt_json["path"])
        nvt_json["kls_list"] = [kls.export_to_json() for kls in self.kls_list]
        nvt_json["creation_time"] = str(datetime.now())
        print("nvt_json: ", nvt_json)
        return nvt_json

    def create_empty_content(self):
        """
            We call this function once we don't have gbgs json for the NVT
            The empty content is simply an empty kls_list
        """
        self.kls_list = []

    def import_from_json(self, kls_json):
        log("Calling import_from_json")
        self.kls_list = []
        print('kls_json["kls_list"]: ', len(kls_json["kls_list"]))
        for kls_json_obj in kls_json["kls_list"]:
            kls_json_obj = json.loads(kls_json_obj)
            kls = Kls(
                kls_json_obj["id"],
                Address(kls_json_obj["address"]),
                [Person(person_json) for person_json in kls_json_obj["people"]],
                [Owner(owner_json) for owner_json in kls_json_obj["owners"]]
            )
            self.kls_list.append(kls)
        print('self.kls_list111: ', len(self.kls_list))

    def copy_people_and_owners_to_address(self):
        """
        02.11.2022: I have been asked to create an attribute in address that have all
        peaple and owners as a big string!
        We only need a phone and a name from each object
        """
        for kls in self.kls_list:
            kls.address.nummer_ansprechpartner = "" # init the variable
            for person in kls.people:
                kls.address.nummer_ansprechpartner += person.fixedline +", "
                kls.address.nummer_ansprechpartner += person.mobile + ", "
                kls.address.nummer_ansprechpartner += "({});".format(person.name)
            for owner in kls.owners:
                kls.address.nummer_ansprechpartner += owner.linenumber + ", "
                kls.address.nummer_ansprechpartner += owner.mobil + ", "
                kls.address.nummer_ansprechpartner += "({});".format(owner.name)


    def write_to_json(self):
        store_path = self.path / 'automated_data'
        json_obj = self.export_to_json()
        Path(store_path).mkdir(parents=True, exist_ok=True)
        with open(store_path / 'nvt_telekom_data.json', 'w') as f:
            json.dump(json_obj, f)
        log("Storing nvt json at: " + str(store_path / 'nvt_telekom_data.json'))

    def write_ibt_to_json(self, addresses):
        ibt_json_obj = {
            "data": addresses,
            "creation_time": str(datetime.now())
        }
        store_path = self.path / 'automated_data'
        Path(store_path).mkdir(parents=True, exist_ok=True)
        with open(store_path / 'nvt_telekom_ibt_data.json', 'w') as f:
            json.dump(ibt_json_obj, f)
        log("Storing nvt ibt json at: " + str(store_path / 'nvt_telekom_ibt_data.json'))


    def read_from_json(self):
        log("Start reading nvt {} from json file".format(self.nvt_number))
        json_path = self.path / 'automated_data' / 'nvt_telekom_data.json'
        log("path: " + str(json_path))
        with open(json_path) as json_file:
            kls_json = json.load(json_file)
        self.import_from_json(kls_json)

    def read_ibt_and_installed_addresses_json(self):
        log("Start reading nvt {} from json file".format(self.nvt_number))
        json_path = self.path / 'automated_data' / 'nvt_telekom_ibt_data.json'
        self.ibt_addresses = []
        self.ibt_installed_addresses = []

        if not json_path.exists():
            return

        log("path: " + str(json_path))
        with open(json_path) as json_file:
            json_obj = json.load(json_file)

        ibt_json_addresses = json_obj["data"]

        for json_address in ibt_json_addresses:
            address = Address()
            address.street = json_address["street"]
            address.house_number = json_address["house_number"]
            address.house_char = json_address["house_char"]
            address.postal = json_address["postal"]
            address.city = json_address["city"]
            address.phase = json_address["phase"]
            address.next_activity = json_address["next_activity"]
            address.beauftrag_id = json_address["order_id"]
            address.kls_id = json_address["kls_id"]
            address.fold_id = json_address["fold_id"]
            address.building_part = json_address["building_part"]
            self.ibt_addresses.append(address)
        self.ibt_installed_addresses = [address for address in self.ibt_addresses if address.next_activity == "Process completed" and address.phase == "Inventory installed"]



    def read_existed_nvt_json(self):
        json_path = self.path / 'automated_data' / 'nvt_telekom_data.json'
        if not os.path.exists(json_path):
            return False

        with open(json_path) as json_file:
            print("json_path: ", json_path)
            nvt_json = json.load(json_file)
        return nvt_json

    def read_existed_nvt_ibt_json(self):
        json_path = self.path / 'automated_data' / 'nvt_telekom_ibt_data.json'
        if not os.path.exists(json_path):
            return False
        with open(json_path) as json_file:
            print("json_path: ", json_path)
            nvt_json = json.load(json_file)
        return nvt_json


    def is_json_recently_updated(self):
        nvt_json = self.read_existed_nvt_json()

        if not nvt_json: # there is no created json file
            return False

        if "creation_time" not in nvt_json.keys():
            return False

        creation_time = nvt_json["creation_time"]
        creation_time = datetime.strptime(creation_time, "%Y-%m-%d %H:%M:%S.%f")
        time_difference = datetime.now() - creation_time
        return time_difference.seconds + time_difference.days * 24*3600  < 75000


    def is_ibt_json_recently_updated(self):
        nvt_json = self.read_existed_nvt_ibt_json()

        if not nvt_json: # there is no created json file
            return False

        if "creation_time" not in nvt_json.keys():
            return False

        creation_time = nvt_json["creation_time"]
        creation_time = datetime.strptime(creation_time, "%Y-%m-%d %H:%M:%S.%f")
        time_difference = datetime.now() - creation_time
        return time_difference.seconds + time_difference.days * 24*3600  < 75000



    def get_already_download_exploration_protocols(self):
        nvt_json = self.read_existed_nvt_json()
        if not nvt_json: # there is no created json file yet
            return [] # then we return an empty list
        klses = nvt_json["kls_list"]
        # print("klses: ", klses)
        already_download_exploration_protocols = []
        for kls in klses:
            # print("kls: ", kls)
            kls = json.loads(kls)
            address = Address(kls["address"])
            if address.exploration_protocol_already_downloaded:
                already_download_exploration_protocols.append(address.create_unique_key())
        return already_download_exploration_protocols


    def archive_montage_excel(self, key):
        # Just copy it and put it in archive folder
        montage_dest_path = self.path / "Archive" / "montage_liste" / date.today().strftime('%Y_%m_%d')
        montage_dest_path.mkdir(parents=True, exist_ok=True)
        montage_dest_path = montage_dest_path / "Montageliste_{}_{}.xlsx".format(self.nvt_number,
                                                                                 key)
        if not os.path.exists(self.montage_excel_path):
            log("There is no Montage Files yet!")
            return
        shutil.copy(self.montage_excel_path, montage_dest_path)

    def unarchive_montage_excel(self):
        montage_src_folder = self.path / "Archive" / "montage_liste" / "2022_09_05"
        csv_files = glob.glob(os.path.join(montage_src_folder, "Montageliste_{}_*.xlsx".format(self.nvt_number)))
        montage_src_path = csv_files[0]
        
        shutil.copy(montage_src_path, self.montage_excel_path)


    def copy_montage_template_to_montage_excel_path(self, montage_template_path):
        self.path.mkdir(exist_ok=True, parents=True)
        shutil.copy(montage_template_path, self.montage_excel_path)

    def archive_ansprech_excel(self):
        ansprechpartnerListe_file_name = "AnsprechpartnerListe_{}.xlsx".format(self.nvt_number)
        ansprechpartnerListe_src_path = Path(self.path) / ansprechpartnerListe_file_name
        ansprechpartnerListe_dest_path = Path(self.path) / "Archive" / "ansprechpartner_liste" / date.today().strftime('%Y_%m_%d')
        ansprechpartnerListe_dest_path.mkdir(parents=True, exist_ok=True)
        ansprechpartnerListe_dest_path = ansprechpartnerListe_dest_path / "AnsprechpartnerListe_{}_{}.xlsx".format(self.nvt_number, str(uuid4()).replace("-", "_"))
        shutil.copy(ansprechpartnerListe_src_path, ansprechpartnerListe_dest_path)

    def export_and_upload_anshprechpartner_to_excel(self, df):
        """
            This function also checks if we have addresses
        """
        # df = self.get_anshprechpartner_dataframe()
        if len(df) > 0:
            self.export_anshprechpartner_to_excel(df)
            self.nvt_mgm.upload_ansprechspartner_excel()
        log("There is no anshprechpartner addresses for NVT {}".format(self.nvt_number))

    def export_anshprechpartner_to_excel(self, df):
        path = self.path / "AnsprechpartnerListe_{}.xlsx".format(self.nvt_number)
        # df.to_excel(path, engine='xlsxwriter')
        measurer = np.vectorize(len)
        columns_max_length = measurer(df.values.astype(str)).max(axis=0)
        with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
            sheet_name = "AnsprechpartnerListe"
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            for idx, column in enumerate(df.columns):
                writer.sheets[sheet_name].set_column(idx, idx, columns_max_length[idx])
            writer.save()



    # def get_anshprechpartner_dataframe(self):
    #     klsid = []
    #     ort = []
    #     strasse = []
    #     rolle = []
    #     name = []
    #     person_ort = []
    #     person_street = []
    #     telefon = []
    #     mobile = []
    #     email = []
    #     for kls in self.kls_list:
    #         address = kls.address
    #         people = kls.people
    #         owners_list = kls.owners
    #         for person in people:
    #             klsid.append(kls.id)
    #             ort.append(address.postal + " " + address.city)
    #             strasse.append(address.street + " " + address.house_number + address.house_char)

    #             rolle.append(person.role)
    #             name.append(person.name)
    #             person_ort.append("")  # no ort for contact person!
    #             person_street.append("")  # no street
    #             telefon.append(person.fixedline)
    #             mobile.append(person.mobile)
    #             email.append(person.email)

    #         for owner in owners_list:
    #             klsid.append(kls.id)
    #             ort.append(address.postal + " " + address.city)
    #             strasse.append(address.street + " " + address.house_number + address.house_char)

    #             rolle.append("Inhaber")
    #             name.append(owner.name)
    #             person_ort.append(owner.postcode + " " + owner.city)
    #             person_street.append(owner.street + " " + owner.housenumber)
    #             telefon.append(owner.linenumber)
    #             mobile.append(owner.mobil)
    #             email.append(owner.email)

    #     return pd.DataFrame(data={
    #         "KLSID": klsid,
    #         "Ort": ort,
    #         "Strasse": strasse,
    #         "Rolle": rolle,
    #         "Name": name,
    #         "Ort2": person_ort,
    #         "Strasse2": person_street,
    #         "Telefon": telefon,
    #         "Mobile": mobile,
    #         "email": email
    #     })