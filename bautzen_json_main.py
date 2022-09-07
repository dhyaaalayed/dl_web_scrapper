
from city import City

from dresden_json_main import update_montage_with_new_template
from my_functions import log


class LoadFromJson:
    cities = []
    navigator = None
    def __init__(self, root_paths):
        for path in root_paths:
            city = City("Bautzen", path, self.navigator)
            city.load_nvt_dict_from_stored_json()

            self.cities.append( city )



if __name__ == "__main__":

    def export_every_nvt_montage_telekom_excel_from_city_montage_telekom_excel(main):
        for city in main.cities:
            city.export_every_nvt_montage_telekom_excel_from_city_montage_telekom_excel()


    roots_list = [
        "/Users/dlprojectsit/Library/CloudStorage/OneDrive-DLProjectsGmbH/BAU/RV-09 Bautzen-Mitte/BVH-01 Bautzen/Baupläne (HK+NVT)"
                ]

    main = LoadFromJson(roots_list)
    # update_montage_with_new_template(main, [])
    for city in main.cities:
        for nvt in city.nvt_list:
            log("Unarchive nvt {}".format(nvt.nvt_number))
            nvt.unarchive_montage_excel()
