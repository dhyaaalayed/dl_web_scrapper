from city import City
from navigator import Navigator


class LoadFromWebMain:
    """
        City class is only used, when we load the data for the first time, or when we want to overwrite the current json files
    """

    cities = []
    navigator = None

    def __init__(self, root_paths, user_name, password):
        self.navigator = Navigator(user_name, password)
        for path in root_paths:
            city = City("Cottbus", path, self.navigator)
            already_downloaded_list = ["4V1105", "4V1109", "4V1110", "4V1111", "4V1113", "4V1112", "4V1106"]
            city.initialize_nvt_dict_using_web_navigator(already_downloaded_list=already_downloaded_list)
            self.cities.append(city)




if __name__ == "__main__":
    roots_list = [
        "/Users/dlprojectsit/Library/CloudStorage/OneDrive-DLProjectsGmbH/BAU/RV-07 Dresden/BVH-02 Cottbus/Baupläne (HK+NVT)"
        ]
    print("Cottbus main")
    user_name = 'markus.lora@dl-projects.de'
    password = 'Markus2022!'
    LoadFromWebMain(roots_list, user_name, password)
"""
[15:52] Hakan Uluer | DL Projects
markus.lora@dl-projects.de

[15:52] Hakan Uluer | DL Projects
Markus2022!

[Yesterday 15:53] Hakan Uluer | DL Projects

David.peterson@dl-projects.de
[Yesterday 15:53] Hakan Uluer | DL Projects
David2022!


[Yesterday 15:54] Hakan Uluer | DL Projects
ahmet.orla@dl-project.de

[Yesterday 15:54] Hakan Uluer | DL Projects
Ahmet2022!




"""