from city import City
from navigator import Navigator


class LoadFromWebMain:
    """
        City class is only used, when we load the data for the first time, or when we want to overwrite the current json files
    """

    cities = []
    navigator = None

    def __init__(self, root_paths):
        self.navigator = Navigator()
        for path in root_paths:
            city = City("Dresden", path, self.navigator)

            already_downloaded_list = ["1016", "1015", "1030", "1018", "1019", "1014", "1011", "1010", "1012"]
            city.initialize_nvt_dict_using_web_navigator(already_downloaded_list=[])
            self.cities.append(city)




if __name__ == "__main__":
    roots_list = [
          "/Users/dlprojectsit/Library/CloudStorage/OneDrive-SharedLibraries-DLProjectsGmbH/Data Management DL Projects - BAU/RV-07 Dresden/BVH-01 Dresden Cotta/Cotta West/Baupläne (HK+NVT)"
        , "/Users/dlprojectsit/Library/CloudStorage/OneDrive-SharedLibraries-DLProjectsGmbH/Data Management DL Projects - BAU/RV-07 Dresden/BVH-01 Dresden Cotta/Cotta Ost/Baupläne (HK+NVT)"
        ]

    LoadFromWebMain(roots_list)