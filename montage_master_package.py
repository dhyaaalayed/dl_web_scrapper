from datetime import date

import pandas as pd
from entities import Address
from openpyxl import load_workbook
import shutil
from excel_address import ExcelAddress
from my_functions import log
import os

class MontageExcelParser:

    excel_df = None
    path_to_excel = None

    excel_addresses = []
    web_addresses = []
    telekom_addresses = []

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
        for i in range(len(df)):
            address = Address()
            address.postal = df.iloc[i, 1]
            if len(address.postal) < 5:
                number_of_zeros = 5 - len(address.postal)
                zeros = "0" * number_of_zeros
                address.postal = zeros + address.postal
            address.city = df.iloc[i, 2]
            address.street = df.iloc[i, 3]
            address.house_number = df.iloc[i, 4]
            address.house_char = df.iloc[i, 5]
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
        for web_key in web_dict.keys():
            if web_key in excel_dict.keys():
                # Update the information
                # log for updating the address, but needs to compare firstly!
                log("Updating montage address: " + web_key)
                print("old address: ")
                excel_dict[web_key].address.print()
                excel_dict[web_key].address.kundentermin_start = web_dict[web_key].kundentermin_start
                excel_dict[web_key].address.kundentermin_end = web_dict[web_key].kundentermin_end
                excel_dict[web_key].address.status = web_dict[web_key].status
                excel_dict[web_key].address.we = web_dict[web_key].we
                excel_dict[web_key].address.gfap_inst_status = web_dict[web_key].gfap_inst_status
                excel_dict[web_key].address.kls_id = web_dict[web_key].kls_id
                excel_dict[web_key].address.fold_id = web_dict[web_key].fold_id
                excel_dict[web_key].address.expl_necessary = web_dict[web_key].expl_necessary
                excel_dict[web_key].address.expl_finished = web_dict[web_key].expl_finished


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
            excel_dict[web_key].htn = "ja" # since it's in gpgs, then ja

        self.excel_addresses = [excel_dict[key] for key in excel_dict.keys()]
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









#
# class OldMontageExcelParser:
#   df = None
#   path_to_excel = None
#   stored_json_address_list = None
#   def __init__(self, path_to_excel, stored_json_address_list):
#       self.path_to_excel = path_to_excel
#       self.df = pd.read_excel(open(path_to_excel, 'rb'), header=None)
#       self.stored_json_address_list = stored_json_address_list
#
#   def _select_row(self, index):
#       return self.df.iloc[index, :]
#
#   def _get_starting_data_row_index(self):
#       for i in range(1, 100):
#           if self._select_row(i)[0] == "PLZ":
#               return i + 1
#
#   def _get_ending_data_row_index(self):
#       starting_index = self._get_starting_data_row_index()
#       for i in range(starting_index + 1, len(self.df)):
#           if pd.isna( self._select_row(i)[0] ):
#               return i - 1
#       return None
#
#   def _get_where_to_write_row_index_on_excel(self):
#       starting_index = self._get_starting_data_row_index()
#       for i in range(starting_index + 1, len(self.df)):
#           if pd.isna( self._select_row(i)[0] ):
#               return i
#       return len(self.df)
#
#   def convert_row_to_montage_address(self, row_index):
#       row = self._select_row(row_index)
#       address = Address()
#       address.postal = row[0]
#       address.city = row[1]
#       address.street = row[2]
#       address.house_number = str(row[3])
#       if not pd.isna(row[4]):
#           address.house_char = row[4]
#       return address
#
#   def get_montage_address_list(self):
#
#       start_index = self._get_starting_data_row_index()
#       end_index = self._get_ending_data_row_index()
#       if end_index is None:
#           end_index = len(self.df) - 1
#
#       montage_address_list = []
#       for i in range(start_index, end_index + 1):
#           montage_address_list.append(
#               self.convert_row_to_montage_address(i)
#               )
#       return montage_address_list
#
#   def get_new_address_list(self):
#       new_address_list = []
#       web_address_dict = {address.create_unique_key():address for address in self.stored_json_address_list}
#       current_montage_address_set = {address.create_unique_key() for address in self.get_montage_address_list()}
#       for web_address_key in web_address_dict.keys():
#           if web_address_key not in current_montage_address_set:
#               new_address_list.append(web_address_dict[web_address_key])
#       return new_address_list
#   def get_new_address_dataframe(self):
#       new_address_list = self.get_new_address_list()
#       df_dict = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[]}
#       for address in new_address_list:
#           df_dict[1].append(address.postal)
#           df_dict[2].append(address.city)
#           df_dict[3].append(address.street)
#           df_dict[4].append(int(address.house_number)) # must be int in the excel file
#           df_dict[5].append(address.house_char)
#           df_dict[6].append("") # empty value
#           df_dict[7].append(address.htn)
#
#       new_address_df = pd.DataFrame(df_dict)
#       if len(new_address_list) > 0:
#           print("Log: So we have new address: " + str(self.path_to_excel))
#           print("Log: The new addresses are: ", new_address_df)
#       else:
#           print("Log: No new addresses!")
#       return new_address_df
#
#   def get_new_montage_list_file_path(self, prefix):
#       """
#           Get the path and generate the file name according to the prefix
#       """
#       nvt_path = self.path_to_excel.parent
#       new_file_name = "{}_".format(prefix) + self.path_to_excel.stem + ".xlsx"
#       new_montage_file_path = nvt_path / new_file_name
#       return new_montage_file_path
#
#
#   def copy_montage_list_excel_file(self):
#       new_montage_file_path = self.get_new_montage_list_file_path("updated")
#       shutil.copyfile(self.path_to_excel, new_montage_file_path)
#       return new_montage_file_path
#
#   def generate_new_address_list_file(self):
#       new_montage_file_path = self.get_new_montage_list_file_path("generated")
#       df = self.df
#       relevant_df = df[df[df.columns[0]].notna()]
#       new_df = pd.concat([relevant_df, self.get_new_address_dataframe()], ignore_index=True)
#       print("self.df: ", relevant_df)
#       print("self.get_new_address_dataframe(): ", self.get_new_address_dataframe())
#       print("new_df: ", new_df)
#       new_df.to_excel(new_montage_file_path)
#
#   def add_new_columns(self, before_col_idx, number_of_cols):
#       """
#           Only for one call: to add Status, Termin Beginn and End columns
#       """
#       book = load_workbook(self.path_to_excel)
#       ws = book["HA_Auswertung"]
#       # ws.insert_cols(before_col_idx, number_of_cols)
#       ws.move_range("J6:AD6", rows=0, cols=2) # Moving header
#       ws.move_range("J7:AD1000", rows=0, cols=2) # rows=0 means we don't move rows
#       ws["I7"] = "Status"
#       ws["J7"] = "Kundentermin Beginn"
#       ws["K7"] = "Kundentermin Ende"
#       book.save(self.path_to_excel)
#
#
#
#   def update_current_montage_list_file(self):
#       # function to copy the file to a new one, return excel_path
#       print("Log: Starting generating a new montage liste file")
#       new_montage_file_path = self.copy_montage_list_excel_file()
#       # function to convert the address_list to dataframe
#       new_address_df = self.get_new_address_dataframe()
#
#       print("Log: The new df of addresses is: ", new_address_df)
#
#       # Then just write it here :)
#       book = load_workbook(new_montage_file_path)
#       writer = pd.ExcelWriter(new_montage_file_path, engine='openpyxl')
#       writer.book = book
#       writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
#
#       start_row = self._get_where_to_write_row_index_on_excel()
#       print("Log: Writing on Excel starting from: ", start_row, " at: ", self.path_to_excel)
#       new_address_df.to_excel(writer, index=False, startrow=start_row, startcol=0, sheet_name='HA_Auswertung', header=False)
#       writer.save()