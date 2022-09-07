from entities import Address

class ExcelAddress:
    address = None
    hk = None
    htn = None
    we = None
    datum_gbgs = None
    bemerkungen = None
    Kommentare = None
    vzk_anbindung = None
    he_erledigt = None
    passed_plus = None
    kabel_erledigt = None
    einblasdatum = None
    lange = None
    einblasprotokoll = None
    kabel_verantwortlicher = None
    nvt = None
    hup = None
    messung = None
    messprotokoll = None
    montage_verantwortlicher = None
    hc_gezeichnet = None
    hp_gezeichnet = None
    vermessung_verantwortlicher = None

    def init_from_excel_row(self, row: "Pandas Series"):
        self.address = Address()
        self.address.postal = row["PLZ"]
        if len(self.address.postal) < 5:
            number_of_zeros = 5 - len(self.address.postal)
            zeros = "0" * number_of_zeros
            self.address.postal = zeros + self.address.postal
        self.address.city = row["Ort"]
        self.address.street = row["Straße"]
        self.address.house_number = row["Hausnr."]
        self.address.house_char = row[4] # because it's nan in the header!
        self.hk = row["HK"]
        self.htn = row["HTN"]
        self.we = row["WE"]
        self.address.status = row["Status"]
        self.datum_gbgs = row["Datum GBGS"]
        self.address.kundentermin_start = row["Kundentermin Beginn"]
        self.address.kundentermin_end = row["Kundentermin Ende"]
        self.bemerkungen = row["Bemerkungen"]
        self.Kommentare = row["Kommentare "]
        self.he_erledigt = row["HE erledigt"]
        self.passed_plus = row["passed plus"]
        self.kabel_erledigt = row["Erledigt KB"]
        self.einblasdatum = row["Einblasdatum"]
        self.lange = row["Länge"]
        self.einblasprotokoll = row["Einblasprotokoll"]
        self.kabel_verantwortlicher = row["Verantwortlicher KB"]
        self.nvt = row["NVT"]
        self.hup = row["HÜP"]
        self.messung = row["Messung"]
        self.messprotokoll = row["Messprotokoll"]
        self.montage_verantwortlicher = row ["Verantwortlicher MT"]
        self.hc_gezeichnet = row["HC gezeichnet"]
        self.hp_gezeichnet = row["HP gezeichnet"]
        self.vermessung_verantwortlicher = row["Verantwortlicher VM"]


    def export_to_df_dict(self):
        return {'PLZ': self.address.postal,
            'Ort': self.address.city,
            'Straße': self.address.street,
            'Hausnr.': self.address.house_number,
            'Hauschar': self.address.house_char,
            'HK': self.hk,
            'HTN': self.htn,
            'WE': self.address.we,
            'Status': self.address.status,
            'Datum GBGS': self.datum_gbgs,
            'Kundentermin Beginn': self.address.kundentermin_start,
            'Kundentermin Ende': self.address.kundentermin_end,
            'Bemerkungen': self.bemerkungen,
            'Kommentare ': self.Kommentare,
            'VZK Anbindung': self.vzk_anbindung,
            'HE erledigt': self.he_erledigt,
            'passed plus': self.passed_plus,
            'Erledigt KB': self.kabel_erledigt,
            'Einblasdatum': self.einblasdatum,
            'Länge': self.lange,
            'Einblasprotokoll': self.einblasprotokoll,
            'Verantwortlicher KB': self.kabel_verantwortlicher,
            'NVT': self.nvt,
            'HÜP': self.hup,
            'Messung': self.messung,
            'Messprotokoll': self.messprotokoll,
            'Verantwortlicher MT': self.montage_verantwortlicher,
            'HC gezeichnet': self.hc_gezeichnet,
            'HP gezeichnet': self.hp_gezeichnet,
            'Verantwortlicher VM': self.vermessung_verantwortlicher}


"""
    def export_to_list(self): # to be used as a row in a df
        return [self.address.postal,
                self.address.city,
                self.address.street,
                self.address.house_number,
                self.address.house_char,
                self.hk,
                self.htn,
                self.we,
                self.address.status,
                self.datum_gbgs,
                self.address.kundentermin_start,
                self.address.kundentermin_end,
                self.bemerkungen,
                self.Kommentare,

                self.he_erledigt,
                self.passed_plus,
                self.kabel_erledigt,
                self.einblasdatum,
                self.lange,
                self.einblasprotokoll,
                self.kabel_verantwortlicher,
                self.nvt,
                self.hup,
                self.messung,
                self.messprotokoll,
                self.montage_verantwortlicher,
                self.hc_gezeichnet,
                self.hp_gezeichnet,
                self.vermessung_verantwortlicher
                ]
"""
