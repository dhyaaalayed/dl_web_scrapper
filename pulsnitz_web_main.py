


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
            city = City("Pulsnitz", path, self.navigator)

            city.initialize_nvt_dict_using_web_navigator(already_downloaded_list=["2V4500", "2V1400", "2V4800", "2V1127", "2V4900", "2V1300"])
            self.cities.append(city)




if __name__ == "__main__":
    roots_list = [
        "/Users/dlprojectsit/Library/CloudStorage/OneDrive-DLProjectsGmbH/BAU/RV-09 Bautzen-Mitte/BVH-02 Pulsnitz/Baupläne (HK+NVT)"
                ]

    user_name = 'ertugrul.yilmaz@dl-projects.de'
    password = 'Ertu2022!'
    LoadFromWebMain(roots_list, user_name, password)


