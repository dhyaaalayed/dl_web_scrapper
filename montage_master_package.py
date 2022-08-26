import pandas as pd
from entities import Address
from openpyxl import load_workbook
import shutil


class MontageExcelParser:
	df = None
	path_to_excel = None
	stored_json_address_list = None
	def __init__(self, path_to_excel, stored_json_address_list):
		self.path_to_excel = path_to_excel
		self.df = pd.read_excel(open(path_to_excel, 'rb'), header=None)
		self.stored_json_address_list = stored_json_address_list

	def _select_row(self, index):
		return self.df.iloc[index, :]

	def _get_starting_data_row_index(self):
		for i in range(1, 100):
			if self._select_row(i)[0] == "PLZ":
				return i + 1

	def _get_ending_data_row_index(self):
		starting_index = self._get_starting_data_row_index()
		for i in range(starting_index + 1, len(self.df)):
			if pd.isna( self._select_row(i)[0] ):
				return i - 1
		return None

	def _get_where_to_write_row_index_on_excel(self):
		starting_index = self._get_starting_data_row_index()
		for i in range(starting_index + 1, len(self.df)):
			if pd.isna( self._select_row(i)[0] ):
				return i
		return len(self.df)

	def convert_row_to_montage_address(self, row_index):
		row = self._select_row(row_index)
		address = Address()
		address.postal = row[0]
		address.city = row[1]
		address.street = row[2]
		address.house_number = str(row[3])
		if not pd.isna(row[4]):
			address.house_char = row[4]
		return address

	def get_montage_address_list(self):

		start_index = self._get_starting_data_row_index()
		end_index = self._get_ending_data_row_index()
		if end_index is None:
			end_index = len(self.df) - 1

		montage_address_list = []
		for i in range(start_index, end_index + 1):
			montage_address_list.append(
				self.convert_row_to_montage_address(i)
				)
		return montage_address_list

	def get_new_address_list(self):
		new_address_list = []
		web_address_dict = {address.create_unique_key():address for address in self.stored_json_address_list}
		current_montage_address_set = {address.create_unique_key() for address in self.get_montage_address_list()}
		for web_address_key in web_address_dict.keys():
			if web_address_key not in current_montage_address_set:
				new_address_list.append(web_address_dict[web_address_key])
		return new_address_list
	def get_new_address_dataframe(self):
		new_address_list = self.get_new_address_list()
		df_dict = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[]}
		for address in new_address_list:
			df_dict[1].append(address.postal)
			df_dict[2].append(address.city)
			df_dict[3].append(address.street)
			df_dict[4].append(int(address.house_number)) # must be int in the excel file
			df_dict[5].append(address.house_char)
			df_dict[6].append("") # empty value
			df_dict[7].append(address.htn)

		new_address_df = pd.DataFrame(df_dict)
		if len(new_address_list) > 0:
			print("Log: So we have new address: " + str(self.path_to_excel))
			print("Log: The new addresses are: ", new_address_df)
		else:
			print("Log: No new addresses!")
		return new_address_df

	def get_new_montage_list_file_path(self, prefix):
		"""
			Get the path and generate the file name according to the prefix
		"""
		nvt_path = self.path_to_excel.parent
		new_file_name = "{}_".format(prefix) + self.path_to_excel.stem + ".xlsx"
		new_montage_file_path = nvt_path / new_file_name
		return new_montage_file_path


	def copy_montage_list_excel_file(self):
		new_montage_file_path = self.get_new_montage_list_file_path("updated")
		shutil.copyfile(self.path_to_excel, new_montage_file_path)
		return new_montage_file_path

	def generate_new_address_list_file(self):
		new_montage_file_path = self.get_new_montage_list_file_path("generated")
		df = self.df
		relevant_df = df[df[df.columns[0]].notna()]
		new_df = pd.concat([relevant_df, self.get_new_address_dataframe()], ignore_index=True)
		print("self.df: ", relevant_df)
		print("self.get_new_address_dataframe(): ", self.get_new_address_dataframe())
		print("new_df: ", new_df)
		new_df.to_excel(new_montage_file_path)


	def update_current_montage_list_file(self):
		# function to copy the file to a new one, return excel_path
		print("Log: Starting generating a new montage liste file")
		new_montage_file_path = self.copy_montage_list_excel_file()
		# function to convert the address_list to dataframe
		new_address_df = self.get_new_address_dataframe()

		print("Log: The new df of addresses is: ", new_address_df)

		# Then just write it here :)
		book = load_workbook(new_montage_file_path)
		writer = pd.ExcelWriter(new_montage_file_path, engine='openpyxl')
		writer.book = book
		writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
		start_row = self._get_where_to_write_row_index_on_excel()
		print("Log: Writing on Excel starting from: ", start_row, " at: ", self.path_to_excel)
		new_address_df.to_excel(writer, index=False, startrow=start_row, startcol=0, sheet_name='HA_Auswertung', header=False)
		writer.save()