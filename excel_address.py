from entities import Address
import pandas as pd

"""
    Adding new columns:
    1- On this file:
    once we add a new column, then we need to add it to:
        1- the class attribute with None value
        2- init_from_excel_row function, but with if statement to check if it exists in the template
        3- export_to_df_dict function, but in the sorted order as in the excel template
    
    2- On the city_config.json
        1- Change the number of columns for both Montage and Master
"""
class ExcelAddress:
    address: Address = None
    hk = None
    htn = None
    datum_gbgs = None
    bemerkungen = None
    Kommentare = None
    hk_montage = None
    vzk_anbindung = None
    he_erledigt = None
    passed_plus = None
    kabel_erledigt = None
    einblasdatum = None
    lange = None
    einblasprotokoll = None
    kabel_verantwortlicher = None
    hup = None
    messung = None
    messprotokoll = None
    montage_verantwortlicher = None
    hc_gezeichnet = None
    hp_gezeichnet = None
    vermessung_verantwortlicher = None
    # New columns
    kunden_status = None
    nur_hup = None
    # New columns taking from beauftrag suche: 15.03.2023
    beauftrag_id = None
    phase = None

    def init_from_excel_row(self, row: "Pandas Series"):
        print("rowrow: ", row)
        self.address = Address()
        self.address.postal = str(row["PLZ"])
        if len(self.address.postal) < 5:
            number_of_zeros = 5 - len(self.address.postal)
            zeros = "0" * number_of_zeros
            self.address.postal = zeros + self.address.postal
        self.address.city = row["Ort"]
        self.address.street = row["Straße"]
        self.address.house_number = row["Hausnr."]
        self.address.house_char = row["Hauschar"] # because it's nan in the header!
        self.hk = row["HK"]
        self.htn = row["HTN"]
        self.address.we = row["WE"]
        self.address.status = row["Status"]
        self.datum_gbgs = row["Datum GBGS"]
        self.address.kundentermin_start = row["Kundentermin Beginn"]
        self.address.kundentermin_end = row["Kundentermin Ende"]
        self.bemerkungen = row["Bemerkungen"]
        self.Kommentare = row["Kommentare "]
        if "HK Montage" in row.index:
            self.hk_montage = row["HK Montage"]
        self.vzk_anbindung = row["VZK Anbindung"]
        self.he_erledigt = row["HE erledigt"]
        self.passed_plus = row["passed plus"]
        self.kabel_erledigt = row["Erledigt KB"]
        self.einblasdatum = row["Einblasdatum"]
        self.lange = row["Länge"]
        self.einblasprotokoll = row["Einblasprotokoll"]
        self.kabel_verantwortlicher = row["Verantwortlicher KB"]
        # self.nvt = row["NVT"] # deleted column (The blue nvt)
        self.hup = row["HÜP"]
        self.messung = row["Messung"]
        self.messprotokoll = row["Messprotokoll"]
        self.montage_verantwortlicher = row ["Verantwortlicher MT"]
        self.hc_gezeichnet = row["HC gezeichnet"]
        self.hp_gezeichnet = row["HP gezeichnet"]
        self.vermessung_verantwortlicher = row["Verantwortlicher VM"]
        # Here to add new rows:
        # We need an if check for each
        """
        added_columns = ["Installiert", "Kunden Status", "KLS-ID", "FOL-ID",
         "Auskundung erforderlich", "Auskundung erfolgt", "nur HÜP"]
         """

        if "Installiert" in row.index:
            self.address.gfap_inst_status = "Installed" if row["Installiert"] == "✔" else ""
            # self.address.gfap_inst_status = "" # To stop taking it from excel, we use this line to clean the excel data once we have wrong data
        if "KLS-ID" in row.index:
            self.address.kls_id = row["KLS-ID"]
        if "FOL-ID" in row.index:
            self.address.fold_id = row["FOL-ID"]

        if "Auskundung erforderlich" in row.index:
            self.address.expl_necessary = row["Auskundung erfolgt"]

        if "Auskundung erfolgt" in row.index:
            self.address.expl_finished = row["Auskundung erforderlich"]

        if "nur HÜP" in row.index:
            self.address.nur_hup = row["nur HÜP"]

        if "Kunden Status" in row.index:
            self.kunden_status = row["Kunden Status"]

        if "Vorderhaus/Hinterhaus" in row.index:
            self.address.building_part = row["Vorderhaus/Hinterhaus"]

        if "Bauauftrag-ID" in row.index:
            self.beauftrag_id = row["Bauauftrag-ID"]

        if "Phase" in row.index:
            self.phase = row["Phase"]

        # No need to import nummer_ansprechpartner from excel, beause we already have it from gbgs

    def set_address_as_installed(self):
        self.address.gfap_inst_status = "Installed"
        self.address.status = "Complete GfAP-Installation"
        self.phase = "Inventory installed"
        

    def export_to_df_dict(self):
        """
            ATTENTION: No problem if the order is not the same as in the excel
        """
        #tmp_print
        print(self.address.postal, self.address.city, self.address.street, self.address.house_number)
        return {
            'PLZ': self.address.postal,
            'Ort': self.address.city,
            'Straße': self.address.street,
            'Hausnr.': int(self.address.house_number),
            'Hauschar': self.address.house_char,
            'Nummer + Ansprechpartner': self.address.nummer_ansprechpartner,
            'Vorderhaus/Hinterhaus': self.address.building_part,
            'HK': self.hk,
            'HTN': self.htn,
            'WE': int(self.address.we) if not pd.isnull(self.address.we) else self.address.we,
            'Status': self.address.status,
            'Datum GBGS': self.datum_gbgs,
            'Kundentermin Beginn': self.address.kundentermin_start,
            'Kundentermin Ende': self.address.kundentermin_end,
            'Bemerkungen': self.bemerkungen,
            'Kommentare ': self.Kommentare,
            'HK Montage': self.hk_montage,
            'VZK Anbindung': self.vzk_anbindung,
            'HE erledigt': "✔" if self.he_erledigt == "✓" else self.he_erledigt,
            'passed plus': self.passed_plus,
            'Erledigt KB': self.kabel_erledigt,
            'Einblasdatum': self.einblasdatum,
            'Länge': self.lange,
            'Einblasprotokoll': self.einblasprotokoll,
            'Verantwortlicher KB': self.kabel_verantwortlicher,
            'HÜP': self.hup,
            'Messung': self.messung,
            'Messprotokoll': self.messprotokoll,
            'Verantwortlicher MT': self.montage_verantwortlicher,
            'HC gezeichnet': self.hc_gezeichnet,
            'HP gezeichnet': self.hp_gezeichnet,
            'Verantwortlicher VM': self.vermessung_verantwortlicher,
            # new columns
            'Installiert': "✔" if self.address.gfap_inst_status == "Installed" else "",
            'KLS-ID': self.address.kls_id,
            'FOL-ID': self.address.fold_id,
            'Auskundung erforderlich': "Ja" if self.address.expl_necessary == "true" else "Nein",
            'Auskundung erfolgt': "Ja" if self.address.expl_finished == "true" else "Nein",
            'Kunden Status': self.kunden_status,
            'nur HÜP': self.nur_hup,
            # new columns from Beauftrage Suche 15.03.2023 
            'Bauauftrag-ID': self.beauftrag_id,
            'Phase': self.phase

            }













