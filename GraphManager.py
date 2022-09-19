"""
To get the names of all shared folders with their ids
    self.GRAPH_API_ENDPOINT + f'/me/drive/sharedwithme'
to get shared one by id:
    self.GRAPH_API_ENDPOINT + f'/drives/{DRIVE_ID}/items/{BAU_FOLDER_ID}
"""
import base64
from pathlib import Path

import msal
import requests

# Drive id of Derla Device, where we have the BAU and other folders!
from IPython.core.display_functions import display

DRIVE_ID = "b!t3YEe8U8mkSNKqGW2Jx1iTQpNwrZTC5Bob7-032a29z3_1Qd4gMtTo_N_SKBLQH0"
BAU_FOLDER_ID = "01A6QGC52KCABYH3NEJRDYM37SPH5MQPYF"
BAU_FOLDER_URL = "https://derlatiefbau-my.sharepoint.com/personal/data_management_derla-tiefbau_de/Documents/BAU"
# BAU_FOLDER_URL = "u!" + str(base64.b64encode( bytes(BAU_FOLDER_URL, 'utf-8') )).replace('/', '_').replace('+', '-')[2:-3]
# print("BAU_FOLDER_URL", str(BAU_FOLDER_URL))

# just to test
SUBCITY_URL = "https://derlatiefbau-my.sharepoint.com/personal/data_management_derla-tiefbau_de/Documents/BAU/RV-07%20Dresden-Cottbus/BVH-01%20Dresden%20Cotta/Cotta%20West/Baupl%C3%A4ne%20(HK+NVT)"

shared_folders = {
    "BAU": {
        "id": "01A6QGC52KCABYH3NEJRDYM37SPH5MQPYF",
    },
    "shared_with_telekom": { # For MasterListe
        "Dresden": {
            "id": "01A6QGC55DPQV75GHFYNALMTB5RLTWQYU3"
        },
        "Cottbus": {
            "id": "01A6QGC53CHKYNQLNVPJD2E6HRBHM4NJN2"
        },
        "Bautzen": {
            "id": "01A6QGC5ZMZCRSH4MKEZB3Y2HATRLG6E2D"
        },
        "Pulsnitz": {
            "id": "01A6QGC54PGFPMKNH73VCY4RY3XVT5BNXB"
        },
        "Prignitz": {
            "id": "01A6QGC55ATH5NI67C7NCIUKRCNU35Y7QJ"
        }
    }
}

class GraphManager:
    access_token = None
    client = None
    headers = None
    GRAPH_API_ENDPOINT = None



    def __init__(self):
        self.GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'
        self.update_athentication_token()
        self.headers = {
            'authorization': 'Bearer {}'.format(self.access_token),
        }

    def encode64_url(self, url):
        return "u!" + str(base64.b64encode( bytes(url, 'utf-8') )).replace('/', '_').replace('+', '-')[2:-3]

    def update_athentication_token(self):
        app_id = '10e05687-0807-45cd-8866-6bc87d5fc388'
        client_secret = '4-V8Q~oxz-HS_wO2K2GSATguJB2mUXJ5IfkWIbQ6'
        scopes = ['User.Read', 'Files.ReadWrite.All']
        client = msal.ClientApplication(
            app_id, authority="https://login.microsoftonline.com/organizations/",
            client_credential=client_secret,
        )
        access_token_req = client.acquire_token_by_username_password(username="robotics@dl-projects.de",
                                                                 password="Daf14576", scopes=scopes)
        self.access_token =  access_token_req["access_token"]

    def encode_file(self, local_path):
        with open(local_path, 'rb') as upload:
            media_content = upload.read()
        return media_content

    def download_file(self, local_path, drive_path):
        requests.get(
            self.GRAPH_API_ENDPOINT + f'/me'
        )

    def upload_file(self, local_path, drive_path):
        media_content = self.encode_file(local_path)
        response = requests.put(
            # GRAPH_API_ENDPOINT + f'/users/user_id/robotics@dl-projects.de/drive/items/root:/{file_name}:/content',
            self.GRAPH_API_ENDPOINT + f'/me/drive/items/root:/{drive_path}:/content',
            headers=self.headers,
            data=media_content
        )
        return response

    def get_folder_items_by_id(self, id):
        """
            Items are folders and files
        """
        response = requests.get(
            self.GRAPH_API_ENDPOINT + f'/drives/{DRIVE_ID}/items/{id}/children',
            headers=self.headers,
        )
        return response.json()["value"]


    def get_folder_subfolders_by_id(self, id):
        items = self.get_folder_items_by_id(id)
        return [item for item in items if "folder" in item.keys()]

    def copy_file(self, src_path, dest_path):
        pass

    def get_nvt_ids(self, subcity_path):
        """
            city folder
        """
        subcity_id = self.get_path_id(subcity_path)

        hk_folders = self.get_folder_subfolders_by_id(subcity_id)
        hk_folders = [folder for folder in hk_folders if "NVT" in folder["name"]]
        nvt_folders = []
        for hk_folder in hk_folders:
            iter_nvt_folders = self.get_folder_subfolders_by_id(hk_folder["id"])
            iternvt_folders = [folder for folder in iter_nvt_folders if "NVT" in folder["name"]]
            nvt_folders += iternvt_folders
        return nvt_folders



    def get_folder_id(self, parent_id, folder_name):
        response = requests.get(
            self.GRAPH_API_ENDPOINT + f'/drives/{DRIVE_ID}/items/{parent_id}/children',
            # self.GRAPH_API_ENDPOINT + f'/shares/{parent_id}/driveItem?$expand=children',
            headers=self.headers,
        )
        print("response.json(): ", response.json())

        children = response.json()["value"]

        for child in children:
            if "folder" in child.keys():
                if child["name"] == folder_name:
                    return child["id"]
        return None



    def get_path_id(self, path):
        """Path start with BAU, since we have the id of BAU
        , we can get the other ids recursively
        Example: path =
        """
        next_id = BAU_FOLDER_ID
        for name in Path(path).parts[1:]: # [1:] for execluding BAU
            print("name: ", name)
            next_id = self.get_folder_id(next_id, name)
            print("next_id: ", next_id)
        return next_id


#users/user_id/data.management@derla-tiefbau.de

if __name__ == "__main__":
    graph_manager = GraphManager()



    folders = graph_manager.get_nvt_ids("BAU/RV-07 Dresden-Cottbus/BVH-01 Dresden Cotta/Cotta Ost/Baupläne (HK+NVT)")
    print("folders: ", folders)
