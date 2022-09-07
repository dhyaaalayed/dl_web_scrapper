
from city import City

from dresden_json_main import update_montage_with_new_template

class LoadFromJson:
    cities = []
    navigator = None
    def __init__(self, root_paths):
        for path in root_paths:
            city = City("Cottbus", path, self.navigator)
            city.load_nvt_dict_from_stored_json()

            self.cities.append( city )



if __name__ == "__main__":

    def export_every_nvt_montage_telekom_excel_from_city_montage_telekom_excel(main):
        for city in main.cities:
            city.export_every_nvt_montage_telekom_excel_from_city_montage_telekom_excel()

    roots_list = [
        "/Users/dlprojectsit/Library/CloudStorage/OneDrive-DLProjectsGmbH/BAU/RV-07 Dresden/BVH-02 Cottbus/Baupläne (HK+NVT)"
        ]


    main = LoadFromJson(roots_list)
    update_montage_with_new_template(main, [])
    # for city in main.cities:
    #     for nvt in city.nvt_list:
    #         nvt.export_anshprechpartner_to_excel()

"""
Functions to be executed only once:

To divide the big telekom city file on each nvt folder:
    export_every_nvt_montage_telekom_excel_from_city_montage_telekom_excel(main)
"""