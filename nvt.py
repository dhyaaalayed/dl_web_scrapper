import shutil
import os
from pathlib import Path
import pandas as pd
import json
from entities import Kls, Address, Person, Owner
from montage_master_package import MontageExcelParser
import numpy as np
from datetime import date
from uuid import uuid4
from my_functions import log


class NVT:
    nvt_number = None
    path = None
    city = None
    kls_list = None
    navigator = None

    def __init__(self, nvt_number, path, city, navigator):  # Dresden
        log("Start NVT Constructor")
        self.nvt_number = nvt_number
        self.path = path
        self.city = city
        self.navigator = navigator
        self.nvt_telekom_list = []
        self.kls_list = []
        # self.initialize_using_web_scrapper()

    def initialize_using_web_scrapper(self):
        self.navigator.filter_in_nvt(self.nvt_number)
        self.visit_eyes_pages()
        log("Finishing reading the whole KLS")
        log("Printing kls details..........")
        self.print()
        self.write_to_json()


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
        return self.navigator.get_eyes_data(self.nvt_number)  # return a kls object

    def get_address_list(self):
        return [kls.address for kls in self.kls_list]

    def get_new_address_for_montage_list(self):
        # Montageliste_1018.xlsx
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

    def generate_montage_excel(self):
        # self.get_new_address_for_montage_list()
        montage_excel_parser = self.get_montage_list_parser()
        montage_excel_parser.generate_new_address_list_file()

    def update_montage_excel(self):
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
        print("nvt_json: ", nvt_json)
        return nvt_json

    def import_from_json(self, kls_json):
        self.nvt_telekom_list = kls_json["nvt_telekom_list"]
        self.kls_list = []
        for kls_json_obj in kls_json["kls_list"]:
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

    def archive_montage_list(self):
        # Just copy it and put it in archive folder
        montage_scr_path = self.path / "Montageliste_{}.xlsx".format(self.nvt_number)
        montage_dest_path = self.path / "Archive" / "montage_liste" / date.today().strftime('%Y_%m_%d')
        montage_dest_path.mkdir(parents=True, exist_ok=True)
        montage_dest_path = montage_dest_path / "Montageliste_{}_{}.xlsx".format(self.nvt_number,
                                                                                 str(uuid4()).replace("-", "_"))
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
        montage_list_src_path = Path(self.path) / montage_list_file_name
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
                person_ort.append("")  # no ort for contact person!
                person_street.append("")  # no street
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