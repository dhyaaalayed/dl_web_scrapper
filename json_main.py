from city import City
from my_functions import log


class LoadFromJson:
    cities = []
    navigator = None
    def __init__(self, root_paths):
        for path in root_paths:
            city = City("Dresden", path, self.navigator)
            city.load_nvt_dict_from_stored_json()
            nvts_to_update = []
            # city.update_montage_lists(nvts_to_update)
            self.cities.append( city )



if __name__ == "__main__":
    roots_list = [
          "/Users/dlprojectsit/Library/CloudStorage/OneDrive-SharedLibraries-DLProjectsGmbH/Data Management DL Projects - BAU/RV-07 Dresden/BVH-01 Dresden Cotta/Cotta West/Baupläne (HK+NVT)"
        , "/Users/dlprojectsit/Library/CloudStorage/OneDrive-SharedLibraries-DLProjectsGmbH/Data Management DL Projects - BAU/RV-07 Dresden/BVH-01 Dresden Cotta/Cotta Ost/Baupläne (HK+NVT)"
        ]

    main = LoadFromJson(roots_list)


    for city in main.cities:
        for nvt in city.nvt_list:
            if nvt.nvt_number in ["42V1018"]:
                # nvt.archive_montage_excel()
                nvt.add_new_columns()
