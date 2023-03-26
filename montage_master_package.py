from datetime import date

import pandas as pd
from entities import Address
from openpyxl import load_workbook
import shutil
from excel_address import ExcelAddress
from my_functions import log
import os

from notifier import NOTIFIER



class AnspreschpartnerExcelGenerator:
    """
        The owners and people are taken from the nvt from its kls object
        we get bulk_addresses once we call set_bulk_addresses
    """

    def __init__(self, kls_list):
        self.kls_list = kls_list
        self.bulk_addresses = []

    def match_addresses_from_bulk_addresses(self, bulk_addresses_dict, montage_excel_addresses):
        for excel_address in montage_excel_addresses:
            address_key = excel_address.address.create_unique_key()
            if address_key in bulk_addresses_dict.keys():
                self.bulk_addresses.append(bulk_addresses_dict[address_key])

    def export_current_data_to_excel(self):
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

        for bulk_address in self.bulk_addresses:
            log("Adding bulk address to Anspreschpartner excel: " + bulk_address.get_one_line_address())
            klsid.append(bulk_address.kls_id)
            ort.append(bulk_address.postal + " " + bulk_address.city)
            strasse.append(bulk_address.street + " " + bulk_address.house_number + bulk_address.house_char)
            rolle.append("Inhaber")
            name.append(bulk_address.company_name + " | " + bulk_address.person_name)
            person_ort.append("")  # no ort for contact bulk_address!
            person_street.append("")  # no street
            telefon.append("")
            mobile.append(bulk_address.mobile)
            email.append(bulk_address.email)


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
##################################################


class MontageExcelParser:

    def __init__(self, path_to_excel, web_addresses):
        self.path_to_excel = path_to_excel
        self.excel_df = self._parse_excel_df()
        self.excel_addresses = self.get_addresses_from_excel()
        self.web_addresses = web_addresses
        self.telekom_addresses = self._initialize_telekom_addresses()


    def _parse_excel_df(self):
        def _get_hauschr_index(new_columns):
            for idx, column in enumerate(new_columns):
                print("idx: ", idx, " col: ", column)
                if pd.isnull(column):
                    print("inside if: ", idx, " null col: ", column)
                    return idx

        if not os.path.exists(self.path_to_excel):
            print("File is not existed")
            return pd.DataFrame(columns=["1", "2"]) # empty dataframe

        print("File is existed")
        # read current montage excel
        df = pd.read_excel(open(self.path_to_excel, 'rb'), sheet_name="HA_Auswertung")
        # then start with the 5th row, where the header of data is located
        df = df[5:]
        # set columns names
        new_columns = list(df.iloc[0])
        print("newnewcols: ", new_columns)
        # Exception case: set a column name manually, because it's nan

        hauschar_index = _get_hauschr_index(new_columns)
        log("hauschar_index in this template is on: {}".format(hauschar_index))
        print("new_columns[hauschar_index]: ", new_columns[hauschar_index], " index: ", hauschar_index)
        new_columns[hauschar_index] = "Hauschar"
        print("123newcolumns: ", new_columns)
        df.columns = new_columns

        df = df.dropna(subset=['PLZ']) # drop rows where all values are nan

        # Drop header row
        df = df[1:]
        df["Hauschar"] = df["Hauschar"].fillna("") # fill na for hauschr for comparision
        df["Vorderhaus/Hinterhaus"] = df["Vorderhaus/Hinterhaus"].fillna("")
        print("dfdf after: ", df.columns)
        return df


    def _initialize_telekom_addresses(self):
        path = self.path_to_excel.parent / "automated_data" / "telekom_addresses.xlsx"
        if not os.path.exists(path):
            return []
        df = pd.read_excel(open(path, 'rb'),
                           sheet_name="Sheet1", dtype={"postal":str})
        df.fillna("", inplace = True)
        addresses = []

        for idx, row in df.iterrows():
            address = Address()
            address.postal = row["postal"]
            if len(address.postal) < 5:
                number_of_zeros = 5 - len(address.postal)
                zeros = "0" * number_of_zeros
                address.postal = zeros + address.postal
            if "dp_name" in row.index: # because other telekom bvh do not have this column
                address.building_part = row["dp_name"]
            else:
                address.building_part = ""
            address.street = row["street"]
            address.city = row["city"]
            address.house_number = row["house_number"]
            address.house_char = row["house_char"]
            addresses.append(address)
        return addresses

    def get_addresses_from_excel(self):
        """
            Input: Excel
            Output: List of address objects
        """
        print("self.excel_df: ", self.excel_df)
        excel_addresses = []
        for idx, row in self.excel_df.iterrows():
            excel_address = ExcelAddress()
            excel_address.init_from_excel_row(row)
            excel_addresses.append(excel_address)
        return excel_addresses


    def export_updated_addresses_to_df(self, montage_template_columns):
        print("yyyyyy: ", montage_template_columns)

        df = pd.DataFrame(columns = montage_template_columns)
        for address in self.excel_addresses:
            df = df.append(address.export_to_df_dict(), ignore_index=True)
        return df

    def export_current_data_to_excel(self, nvt_number, montage_template_columns):
#       # function to copy the file to a new one, return excel_path
        log("calling export_current_data_to_excel")
        #tmp_print
        print("current_nvt: ", nvt_number)
        df = self.export_updated_addresses_to_df(montage_template_columns)

        df = df.fillna('').reset_index(drop=True)

        # Then just write it here :)
        book = load_workbook(self.path_to_excel) # assuming that the new template is there
        writer = pd.ExcelWriter(self.path_to_excel, engine='openpyxl')
        writer.book = book
        writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

        print("Log: Writing on Excel")


        sheet = book["HA_Auswertung"]
        sheet["A1"] = "NVT {}".format(nvt_number)


        df.to_excel(writer, index=False, startrow=7, startcol=0, sheet_name='HA_Auswertung', header=False)
        # self.write_df_to_excel_manually(address_list=self.excel_addresses, start_row=8, sheet=sheet)
        writer.save()

    def update_addresses_from_web(self):
        web_dict = {address.create_unique_key(): address for address in self.web_addresses}
        excel_dict = {address.address.create_unique_key(): address for address in self.excel_addresses}
        print("web_dict keys: ", [key for key in web_dict.keys()])
        print("excel_dict keys: ", [key for key in excel_dict.keys()])
        new_addresses_as_notifications = []
        for web_key in web_dict.keys():
            if web_key in excel_dict.keys():
                # Update the information
                # log for updating the address, but needs to compare firstly!
                log("Updating montage address: " + web_key)
                print("old address: ")
                excel_dict[web_key].address.print()
                excel_dict[web_key].address.kundentermin_start = web_dict[web_key].kundentermin_start
                excel_dict[web_key].address.kundentermin_end = web_dict[web_key].kundentermin_end
                excel_dict[web_key].address.we = web_dict[web_key].we
                # Disable the installed from Grundstuek suche
                # if excel_dict[web_key].address.gfap_inst_status != "Installed":
                #     excel_dict[web_key].address.gfap_inst_status = web_dict[web_key].gfap_inst_status
                excel_dict[web_key].address.kls_id = web_dict[web_key].kls_id
                excel_dict[web_key].address.fold_id = web_dict[web_key].fold_id
                excel_dict[web_key].address.expl_necessary = web_dict[web_key].expl_necessary
                excel_dict[web_key].address.expl_finished = web_dict[web_key].expl_finished

                # added at 04.11.2022
                excel_dict[web_key].address.nummer_ansprechpartner = web_dict[web_key].nummer_ansprechpartner
                # added at 04.11.2022
                excel_dict[web_key].address.building_part = web_dict[web_key].building_part

                # To send email notification: The address is existed in the red color (taken from telekom addresses excels)
                if excel_dict[web_key].address.status == "":
                    new_addresses_as_notifications.append(excel_dict[web_key].address.get_one_line_address())
                excel_dict[web_key].address.status = web_dict[web_key].status




                print("new address: ")
                excel_dict[web_key].address.print()

            if web_key not in excel_dict.keys():
                # Add it if it is not existed
                log("Adding new address from the web: " + web_key)
                excel_dict[web_key] = ExcelAddress()
                print("before exporting: ", web_dict[web_key])
                web_dict[web_key].print()
                excel_dict[web_key].address = web_dict[web_key]
                excel_dict[web_key].datum_gbgs = date.today().strftime('%Y_%m_%d')
                # To send email notification: the address does not exist in the excel at all!
                new_addresses_as_notifications.append(excel_dict[web_key].address.get_one_line_address())


            excel_dict[web_key].htn = "ja" # since it's in gpgs, then ja


        self.excel_addresses = [excel_dict[key] for key in excel_dict.keys()]

        # Adding notifications to the notifier
        if len(new_addresses_as_notifications) > 0:
            new_addresses_as_notifications = [self.path_to_excel.name] + new_addresses_as_notifications
            new_addresses_as_notifications.append("_" * 40)
            NOTIFIER.new_gbgs_addresses += new_addresses_as_notifications

    def update_addresses_from_telekom_excel(self):
        """
            Telekom addresses is an excel file inside each NVT
        """
        telekom_dict = {address.create_unique_key(): address for address in self.telekom_addresses}
        excel_addresses_keys = [address.address.create_unique_key() for address in self.excel_addresses]
        print("telekom_dict: ", [key for key in telekom_dict.keys()])
        print("excel_addresses_keys: ", excel_addresses_keys)
        for telekom_key in telekom_dict.keys():
            if telekom_key not in excel_addresses_keys:
                excel_address = ExcelAddress()
                excel_address.address = telekom_dict[telekom_key]
                excel_address.htn = "nein"
                log("Adding new address from Telekom with nein htn: " + excel_address.address.create_unique_key())
                excel_address.address.print()
                self.excel_addresses.append(excel_address)

    def update_from_installed_addresses(self, nvt_number: str, installed_addresses: "List of Address"):
        # installed_addresses_keys = [address.create_unique_key() for address in installed_addresses]
        installed_addresses_dict = {address.create_unique_key(): address for address in installed_addresses}
        new_installed_addresses_as_notifications = []
        for excel_address in self.excel_addresses:
            excel_address_key = excel_address.address.create_unique_key()
            if excel_address_key in installed_addresses_dict.keys() and excel_address.address.gfap_inst_status != "Installed":
                logging_string = "Discovering an installed at NVT {}. The address: {}".format(nvt_number, excel_address.address.get_one_line_address())
                log(logging_string)
                print("The key: ", excel_address_key)
                print("The installed: ", excel_address.address.gfap_inst_status)
                print("excel_address.address.create_unique_key() in installed_addresses_keys: ", excel_address_key in installed_addresses_dict.keys())
                print("installed_addresses_keys: ", installed_addresses_dict.keys())
                new_installed_addresses_as_notifications.append(excel_address.address.get_one_line_address())
                excel_address.address.gfap_inst_status = "Installed"
                # new columns from beauftrag
                excel_address.phase = installed_addresses_dict[excel_address_key].phase
                excel_address.beauftrag_id = installed_addresses_dict[excel_address_key].phase

        if len(new_installed_addresses_as_notifications) > 0:
            new_installed_addresses_as_notifications = [self.path_to_excel.name] + new_installed_addresses_as_notifications
            new_installed_addresses_as_notifications.append("_" * 40)
            NOTIFIER.new_installed_addresses += new_installed_addresses_as_notifications

    def update_from_ibt_addresses(self, nvt_number: str, ibt_addresses: "List of Address"):
        log("updating from ibt_addresses for nvt {}".format(nvt_number))
        ibt_addresses_dict = {address.create_unique_key(): address for address in ibt_addresses}

        for excel_address in self.excel_addresses:
            excel_address_key = excel_address.address.create_unique_key()
            if excel_address_key in ibt_addresses_dict.keys():
                excel_address.phase = ibt_addresses_dict[excel_address_key].phase
                excel_address.beauftrag_id = ibt_addresses_dict[excel_address_key].beauftrag_id

    def update_from_bulk_addresses(self, nvt_number: str, bulk_addresses_dict: "List of Address"):
        bulk_auftrag_str = "BULK Auftrag"
        new_bulk_addresses_as_notifications = []
        for excel_address in self.excel_addresses:
            excel_address_key = excel_address.address.create_unique_key()
            if excel_address_key in bulk_addresses_dict.keys():
                
                if bulk_auftrag_str.lower() not in str(excel_address.Kommentare).lower():
                    logging_string = "Discovering a bulk address at NVT {}. The address: {}".format(nvt_number, excel_address.address.get_one_line_address())
                    log(logging_string)
                    print("The key: ", excel_address_key)
                    new_bulk_addresses_as_notifications.append(excel_address.address.get_one_line_address())
                    excel_address.Kommentare = bulk_auftrag_str + ", " + str(excel_address.Kommentare)
                    excel_address.htn = "ja"

                if "Bulk Auftrag, nan" in str(excel_address.Kommentare):
                    excel_address.Kommentare = str(excel_address.Kommentare).replace("Bulk Auftrag, nan", "BULK Auftrag")
                
                if "Bulk Auftrag, BULK Auftrag" in str(excel_address.Kommentare):
                    excel_address.Kommentare = str(excel_address.Kommentare).replace("Bulk Auftrag, BULK Auftrag", "BULK Auftrag")

                if "Bulk Auftrag" in str(excel_address.Kommentare):
                    excel_address.Kommentare = str(excel_address.Kommentare).replace("Bulk Auftrag", "BULK Auftrag")

                # Update to be added to Montage files:
                excel_address.address.kls_id = bulk_addresses_dict[excel_address_key].kls_id
                excel_address.address.fold_id = bulk_addresses_dict[excel_address_key].fold_id
                excel_address.address.status = "Complete GfAP-Installation"

                log("Removing bulk address after matching one in excel")
                # we do that just to know which addresses did not match :)
                del bulk_addresses_dict[excel_address_key]
        if len(new_bulk_addresses_as_notifications) > 0:
            new_bulk_addresses_as_notifications = [self.path_to_excel.name] + new_bulk_addresses_as_notifications
            new_bulk_addresses_as_notifications.append("_" * 40)
            NOTIFIER.new_bulk_addresses += new_bulk_addresses_as_notifications































