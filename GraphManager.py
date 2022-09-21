"""
To get the names of all shared folders with their ids
    self.GRAPH_API_ENDPOINT + f'/me/drive/sharedwithme'
to get shared one by id:
    self.GRAPH_API_ENDPOINT + f'/drives/{DRIVE_ID}/items/{BAU_FOLDER_ID}
"""
import base64
import os
import shutil
from pathlib import Path

import msal
import requests

# Drive id of Derla Device, where we have the BAU and other folders!
DRIVE_ID = "b!t3YEe8U8mkSNKqGW2Jx1iTQpNwrZTC5Bob7-032a29z3_1Qd4gMtTo_N_SKBLQH0"
BAU_FOLDER_ID = "01A6QGC52KCABYH3NEJRDYM37SPH5MQPYF"



class GraphManager:
    access_token = None
    client = None
    headers = None
    GRAPH_API_ENDPOINT = None
    path_id_dict = {}

    download_folder = Path("onedrive_data/download")
    upload_folder = Path("onedrive_data/upload")

    def __init__(self):
        self.GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'
        self.update_athentication_token()
        self.headers = {
            'authorization': 'Bearer {}'.format(self.access_token),
        }
        self.clean_cloud_onedrive_folder()

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
                                                                 password="", scopes=scopes)
        self.access_token = access_token_req["access_token"]

    def encode_file(self, local_path):
        with open(local_path, 'rb') as upload:
            media_content = upload.read()
        return media_content

    def download_file(self, file, path_to_store):

        response = requests.get(
            self.GRAPH_API_ENDPOINT + f'/drives/{DRIVE_ID}/items/{file["id"]}/content',
            headers=self.headers,
        )
        Path(path_to_store).mkdir(parents=True, exist_ok=True)
        download_path = Path(path_to_store) / file["name"]
        with open(download_path, "wb") as handler:
            handler.write(response.content)


    def upload_file(self, local_path, drive_folder):
        file_name = Path(local_path).name
        media_content = self.encode_file(local_path)
        response = requests.put(
            # GRAPH_API_ENDPOINT + f'/users/user_id/robotics@dl-projects.de/drive/items/root:/{file_name}:/content',
            self.GRAPH_API_ENDPOINT + f'/drives/{DRIVE_ID}/items/{drive_folder["id"]}:/{file_name}:/content',
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
            iter_nvt_folders = [folder for folder in iter_nvt_folders if "NVT" in folder["name"]]
            nvt_folders += iter_nvt_folders
        return nvt_folders



    def get_item(self, parent_id, item_name):
        """
            Returns a dict of an item.
        """
        response = requests.get(
            self.GRAPH_API_ENDPOINT + f'/drives/{DRIVE_ID}/items/{parent_id}/children',
            # self.GRAPH_API_ENDPOINT + f'/shares/{parent_id}/driveItem?$expand=children',
            headers=self.headers,
        )

        children = response.json()["value"]

        for child in children:
            if child["name"] == item_name:
                return child
        return None



    def get_path_id(self, path):
        """Path start with BAU, since we have the id of BAU
        , we can get the other ids recursively
        Example: path =
        """
        next_id = BAU_FOLDER_ID
        for name in Path(path).parts[1:]: # [1:] for execluding BAU
            print("name: ", name)
            next_id = self.get_item(next_id, name)["id"]
            print("next_id: ", next_id)
        return next_id

    def get_nvt_data_ids(self, nvt_id, nvt_path):
        # nvt_id: to Upload montageliste:
        # nvt_montage_id: to download the current montageliste
        # telkom_addresses_id: to get telekom addresses
        # automated_data folder id: to upload a new telekom list
        # json_file_id to read the current telekom data

        automated_folder_id = self.get_item(nvt_id, "automated_data")
        json_file_id = self.get_item(automated_folder_id, "nvt_telekom_data.json")
        telkom_addresses_id = self.get_item(automated_folder_id, "telekom_addresses.xlsx")


    def clean_cloud_onedrive_folder(self):
        """Just to delete all data after finishing from the current nvt
            Simply: by deleting the folder and creating it again :)
        """
        if os.path.exists(self.download_folder):
            shutil.rmtree(self.download_folder)
        if os.path.exists(self.upload_folder):
            shutil.rmtree(self.upload_folder)
        os.mkdir(self.download_folder)
        os.mkdir(self.upload_folder)


class MicrosoftGraphNVTManager:
    graph_manager = None
    nvt_mg_obj = None
    nvt_number = None
    automated_data_folder_mg_obj = None

    # paths
    nvt_to_upload_path = None # the path of the json that we are gonna generate
    nvt_download_path = None

    def __init__(self, graph_manager: GraphManager, nvt_mg_obj):
        self.graph_manager = graph_manager
        self.nvt_mg_obj = nvt_mg_obj
        self.nvt_number = self.nvt_mg_obj["name"].replace("NVT ", "")
        self.automated_data_folder_mg_obj = self.graph_manager.get_item(self.nvt_mg_obj["id"], "automated_data")
        # paths
        self.nvt_download_path = self.graph_manager.download_folder / "NVT {}".format(self.nvt_number)
        self.nvt_to_upload_path = self.graph_manager.upload_folder / "NVT {}".format(self.nvt_number)
    def download_automated_data_folder(self):
        os.mkdir(self.nvt_download_path)
        # 1- Downloading automated_folder

        automated_data_mg_obj_items = self.graph_manager.get_folder_items_by_id(self.automated_data_folder_mg_obj["id"])
        for item in automated_data_mg_obj_items:
            self.graph_manager.download_file(item, self.nvt_download_path / "automated_data")

        # 2- Download montage excel file
        montage_excel_mg_obj = self.graph_manager.get_item(self.nvt_mg_obj["id"], "Montageliste_{}.xlsx".format(self.nvt_number))
        self.graph_manager.download_file(montage_excel_mg_obj, self.nvt_download_path)

    def upload_nvt_json_file(self):
        self.graph_manager.upload_file(self.nvt_to_upload_path / "automated_data" / "nvt_telekom_data.json", self.nvt_mg_obj)


if __name__ == "__main__":
    graph_manager = GraphManager()

    nvt_mg_list = graph_manager.get_nvt_ids("BAU/RV-07 Dresden-Cottbus/BVH-01 Dresden Cotta/Cotta Ost/Baupläne (HK+NVT)")
    nvt_mg_obj = nvt_mg_list[0]

    nvt_mgm = MicrosoftGraphNVTManager(graph_manager, nvt_mg_obj)
    nvt_mgm.download_automated_data_folder()





