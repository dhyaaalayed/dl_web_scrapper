from city import City
from dresden_json_main import update_montage_with_new_template
from my_functions import log





class LoadFromJson:
    cities = []
    navigator = None
    def __init__(self, root_paths):
        for path in root_paths:
            city = City("Pulsnitz", path, self.navigator)
            city.load_nvt_dict_from_stored_json(["2V4800", "2V1300", "2V4500"])
            nvts_to_update = []
            # city.update_montage_lists(nvts_to_update)
            self.cities.append(city)
            # no ansprechpartner list: 2V1127



if __name__ == "__main__":

    def export_every_nvt_montage_telekom_excel_from_city_montage_telekom_excel(main):
        for city in main.cities:
            city.export_every_nvt_montage_telekom_excel_from_city_montage_telekom_excel()



    roots_list = [
        "/Users/dlprojectsit/Library/CloudStorage/OneDrive-DLProjectsGmbH/BAU/RV-09 Bautzen-Mitte/BVH-02 Pulsnitz/Baupläne (HK+NVT)"
    ]

    main = LoadFromJson(roots_list)
    for city in main.cities:
        for nvt in city.nvt_list:
            if nvt.nvt_number not in []:
                log("Operation on NVT {}: " + nvt.nvt_number)
                update_montage_with_new_template(main,[]) # archive is inside




