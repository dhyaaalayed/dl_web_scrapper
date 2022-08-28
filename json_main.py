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

            # to generate new montage liste files without templates
            # for nvt in city.nvt_list:
            #     nvt.export_anshprechpartner_to_excel()
                # nvt.clean_generated_anshprechpartner_files()
                # nvt.clean_generated_montage_list_files()

            # to update current montage liste files and copy the old ones
            for nvt in city.nvt_list:
                if nvt.nvt_number in []:
                    continue
                log("Renaming in nvt" + str(nvt.path))
                nvt.rename_ansprech_files()

        # for city in self.cities:
            # Update MasterListe



if __name__ == "__main__":
    roots_list = [
          "/Users/dlprojectsit/Library/CloudStorage/OneDrive-SharedLibraries-DLProjectsGmbH/Data Management DL Projects - BAU/RV-07 Dresden/BVH-01 Dresden Cotta/Cotta West/Baupläne (HK+NVT)"
        , "/Users/dlprojectsit/Library/CloudStorage/OneDrive-SharedLibraries-DLProjectsGmbH/Data Management DL Projects - BAU/RV-07 Dresden/BVH-01 Dresden Cotta/Cotta Ost/Baupläne (HK+NVT)"
        ]

    main = LoadFromJson(roots_list)
