from city import City
from my_functions import log


def update_montage_with_new_template(main: "instance of class main!", nvt_list):
    for city in main.cities:
        for nvt in city.nvt_list:
            if nvt.nvt_number not in nvt_list:
                log("Operation on NVT {}".format(nvt.nvt_number))

                log("Archiving current montage")
                nvt.archive_montage_excel()

                log("Update montage excel")
                nvt.initialize_montage_excel_parser()
                nvt.montage_excel_parser.update_addresses_from_web()

                #### To be called later:
                nvt.montage_excel_parser.update_addresses_from_telekom_excel()

                # Now using the new template:
                log("Using the new Montage Excel template")
                nvt.copy_montage_template_to_montage_excel_path()

                nvt.montage_excel_parser.export_current_data_to_excel(nvt.nvt_number)
                print("__________Finish________\n\n\n")

        # city.export_all_montage_to_one_excel()


class LoadFromJson:
    cities = []
    navigator = None
    def __init__(self, root_paths):
        for path in root_paths:
            city = City("Dresden", path, self.navigator)
            city.load_nvt_dict_from_stored_json()
            nvts_to_update = []
            # city.update_montage_lists(nvts_to_update)
            self.cities.append(city)



if __name__ == "__main__":

    def export_every_nvt_montage_telekom_excel_from_city_montage_telekom_excel(main):
        for city in main.cities:
            city.export_every_nvt_montage_telekom_excel_from_city_montage_telekom_excel()



    roots_list = [
          "/Users/dlprojectsit/Library/CloudStorage/OneDrive-DLProjectsGmbH/BAU/RV-07 Dresden/BVH-01 Dresden Cotta/Cotta West/Baupläne (HK+NVT)"
        , "/Users/dlprojectsit/Library/CloudStorage/OneDrive-DLProjectsGmbH/BAU/RV-07 Dresden/BVH-01 Dresden Cotta/Cotta Ost/Baupläne (HK+NVT)"
        ]

    main = LoadFromJson(roots_list)
    # update_montage_with_new_template(main, nvt_list = [])
    # export_every_nvt_montage_telekom_excel_from_city_montage_telekom_excel(main)

    for city in main.cities:
        for nvt in city.nvt_list:
            log("Unarchive nvt {}".format(nvt.nvt_number))
            nvt.unarchive_montage_excel()



"""
["42V1031", "42V1020", "42V1018"
,"42V1019", "42V1014"
,"42V1011", "42V1010"
"42V1012", "42V1013"
                                                       , "42V1016", "42V1030"
                                                       ,"42V1015", "42V1027"
                                                       ,"42V1026", "42V1025", "42V1029"
                                                       ,"42V1017", "42V1028", "42V1020"
                                                       , "42V1010", "42V1012"]
"""