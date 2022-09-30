"""
To get the names of all shared folders with their ids
    self.GRAPH_API_ENDPOINT + f'/me/drive/sharedwithme'
to get shared one by id:
    self.GRAPH_API_ENDPOINT + f'/drives/{DRIVE_ID}/items/{BAU_FOLDER_ID}
"""
import base64
import json
import os
import shutil
from pathlib import Path

import msal
import requests

from my_functions import log
from security_config import user_name, password

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
        access_token_req = client.acquire_token_by_username_password(username=user_name,
                                                                 password=password, scopes=scopes)
        self.access_token = access_token_req["access_token"]

    def encode_file(self, local_path):
        with open(local_path, 'rb') as upload:
            media_content = upload.read()
        return media_content

    def download_file(self, file: "mg object", path_to_store):
        """
            path_to_store: is a path to a folder, the file name is not included.
        """

        response = requests.get(
            self.GRAPH_API_ENDPOINT + f'/drives/{DRIVE_ID}/items/{file["id"]}/content',
            headers=self.headers,
        )
        Path(path_to_store).mkdir(parents=True, exist_ok=True)
        download_path = Path(path_to_store) / file["name"]
        with open(download_path, "wb") as handler:
            handler.write(response.content)


    def upload_file(self, local_path, drive_folder_id):
        file_name = Path(local_path).name
        media_content = self.encode_file(local_path)
        response = requests.put(
            # GRAPH_API_ENDPOINT + f'/users/user_id/robotics@dl-projects.de/drive/items/root:/{file_name}:/content',
            self.GRAPH_API_ENDPOINT + f'/drives/{DRIVE_ID}/items/{drive_folder_id}:/{file_name}:/content',
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

    def get_folder_files_by_id(self, id):
        items = self.get_folder_items_by_id(id)
        return [item for item in items if "file" in item.keys()]

    def download_folder_files_by_id(self, id, path):
        files = self.get_folder_files_by_id(id)
        for file in files:
            log("downloading {} at {}".format(file["name"], str(path)))
            self.download_file(file=file, path_to_store=path)

    def copy_item(self, item_id: str, item_new_name: str, dest_id: str) -> None:
        """
            This function can copy both files and folders
            item_id: item that we need to copy
            item_new_name: the name of the new copied created item
            dest_id: the folder that we need to put the new copy in
        """
        response = requests.post(
            self.GRAPH_API_ENDPOINT + f'/drives/{DRIVE_ID}/items/{item_id}/copy',
            headers=self.headers,
            json={
                "parentReference": {
                    "driveId": DRIVE_ID,
                    "id": dest_id
                },
                "name": item_new_name

            }
        )
        log("The response of the copy function: ")
        print(response)
        return response

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



    def get_next_item_in_path(self, parent_id, item_name):
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





    def get_path_mg_obj(self, path):
        """
            Similar to get_path_id, but it returns the whole object instead of the id
        """
        next_id = BAU_FOLDER_ID
        item_mg_obj = None
        for name in Path(path).parts[1:]: # [1:] for execluding BAU
            print("name: ", name)
            item_mg_obj = self.get_next_item_in_path(next_id, name)
            next_id = item_mg_obj["id"]
            print("next_id: ", next_id)
        return item_mg_obj

    def get_path_id(self, path):
        """Path start with BAU, since we have the id of BAU
        , we can get the other ids recursively
        Example: path = "BAU/gbgs_config/Templates/Montageliste_Template_Final - Master.xlsx"
        """
        return self.get_path_mg_obj(path)["id"]

    def get_nvt_data_ids(self, nvt_id, nvt_path):
        # nvt_id: to Upload montageliste:
        # nvt_montage_id: to download the current montageliste
        # telkom_addresses_id: to get telekom addresses
        # automated_data folder id: to upload a new telekom list
        # json_file_id to read the current telekom data

        automated_folder_id = self.get_next_item_in_path(nvt_id, "automated_data")
        json_file_id = self.get_next_item_in_path(automated_folder_id, "nvt_telekom_data.json")
        telkom_addresses_id = self.get_next_item_in_path(automated_folder_id, "telekom_addresses.xlsx")

    def create_new_folder(self, parent_id: str, new_folder_name: str):
        """
            parent_id: folder id that we want to create the new folder in
            new_folder_name: the name of the new folder
        """
        headers = self.headers
        # headers["Content-Type"] = "application/json"

        response = requests.post(
            self.GRAPH_API_ENDPOINT + f'/drives/{DRIVE_ID}/items/{parent_id}/children',
            headers=headers,
            json={
                "name": new_folder_name,
                "folder": {},
            }
        )
        log("Creating new folder response")
        return response.json()

    def print_all_shared_folders_with_their_ids(self):
        """
            This functions is used by adding a new BVH shared folder for Telekom
            then, we copy the id of it manually to the city_config.json file
            in order to be used by mg_json_main.py to put the master excel inside it
        """
        response = requests.get(
            graph_manager.GRAPH_API_ENDPOINT + f'/me/insights/shared',
            headers=graph_manager.headers,
        )
        # json.dumps with intend = 4 parameter just to print the json object in a pretty way
        print(json.dumps(response.json(), indent = 4) )


class MicrosoftGraphNVTManager:
    """
        This class get the folowing for one nvt:
            1- automated_data_folder_mg_obj
            2- Montage_excel_mg_obj

    """
    graph_manager = None
    nvt_mg_obj = None
    nvt_number = None
    automated_data_folder_mg_obj = None
    montage_excel_mg_obj = None
    archive_folder_mg_obj = None

    nvt_path: Path = None # the path locally in the cloud
    def __init__(self, graph_manager: GraphManager, nvt_mg_obj: "Microsoft Graph Obj", nvt_path: Path):

        self.graph_manager = graph_manager
        self.nvt_mg_obj = nvt_mg_obj
        self.nvt_number = self.nvt_mg_obj["name"].replace("NVT ", "")
        self.automated_data_folder_mg_obj = self.graph_manager.get_next_item_in_path(self.nvt_mg_obj["id"], "automated_data")
        self.montage_excel_mg_obj = self.graph_manager.get_next_item_in_path(self.nvt_mg_obj["id"], "Montageliste_{}.xlsx".format(self.nvt_number))
        self.archive_folder_mg_obj = self.graph_manager.get_next_item_in_path(self.nvt_mg_obj["id"], "Archive")
        # paths
        # self.nvt_download_path = self.graph_manager.download_folder / "NVT {}".format(self.nvt_number)
        # self.nvt_to_upload_path = self.graph_manager.upload_folder / "NVT {}".format(self.nvt_number)
        self.nvt_path = nvt_path
    def get_nvt_json_path(self):
        """
            Returns the local path of the generated json.
                To be used by mg_json_main to update Montage and generate Ansprech...
        """
        return self.nvt_path / "automated_data" / "nvt_telekom_data.json"


    def download_automated_data_folder(self, nvt_path: Path):
        """
            1- Initiaize nvt folder if it's not initialized
            2- Download the automated folder inside it
            Example: nvt_path: BAU/RV-07 Dresden-Cottbus/BVH-01 Dresden Cotta/Cotta Ost/Baupläne (HK+NVT)/42V1020
        """
        if self.automated_data_folder_mg_obj == None:
            return
        automated_data_path = nvt_path / "automated_data"
        automated_data_path.mkdir(parents=True, exist_ok=True)
        # 1- Downloading automated_folder
        automated_data_mg_obj_items = self.graph_manager.get_folder_items_by_id(self.automated_data_folder_mg_obj["id"])
        for item in automated_data_mg_obj_items:
            self.graph_manager.download_file(item, automated_data_path)


    def download_montage_excel(self):
        self.nvt_path.mkdir(parents=True, exist_ok=True)
        # Download montage excel file
        self.graph_manager.download_file(self.montage_excel_mg_obj, self.nvt_path)

    def archive_montage_excel(self, archive_date: str, generated_unique_key: str):
        """
            One one drive: copy the current Montageliste to Archive folder
            We need to get the archive date folder
            If it's None, then we need to create one
            Paramters:
                archive_date: It's good to take it from json_main, in order to archive all nvts in the same date
                archive_date example: 2022_09_01
                generated_unique_key: UUI4 key
        """
        date_archive_folder_mg_obj = self.created_dated_archive_folder(archive_date)
        print("self.montage_excel_mg_obj: ", self.montage_excel_mg_obj)
        print("date_archive_folder_mg_obj: ", date_archive_folder_mg_obj)
        self.graph_manager.copy_item(self.montage_excel_mg_obj["id"]
                                     ,   "Montageliste_{}_{}.xlsx".format(self.nvt_number, generated_unique_key)
                                     , date_archive_folder_mg_obj["id"])

    def created_dated_archive_folder(self, archive_date: str):
        """
            Checks out first if there is already a created folder of the same name
            If not, then it creates one and it returns its id
            archive_date example: 2022_09_01
        """
        montage_archive_folder = self.graph_manager.get_next_item_in_path(self.archive_folder_mg_obj["id"], "montage_liste")
        dated_archive_folder_mg_obj = self.graph_manager.get_next_item_in_path(montage_archive_folder["id"], archive_date)
        if dated_archive_folder_mg_obj != None:
            return dated_archive_folder_mg_obj

        return self.graph_manager.create_new_folder(montage_archive_folder["id"], archive_date)



    def upload_nvt_json_file(self):
        path = self.nvt_path / "automated_data" / "nvt_telekom_data.json"
        if os.path.exists(path):
            self.graph_manager.upload_file(local_path=path, drive_folder_id=self.automated_data_folder_mg_obj["id"])
            log("uploading generated gpgs json to one drive")
        else:
            log("No generated gpgs json file to upload")

    def upload_montage_excel(self):
        path = self.nvt_path / "Montageliste_{}.xlsx".format(self.nvt_number)
        self.graph_manager.upload_file(local_path=path, drive_folder_id=self.nvt_mg_obj["id"])

    def upload_ansprechspartner_excel(self):
        path = self.nvt_path / "AnsprechpartnerListe_{}.xlsx".format(self.nvt_number)
        self.graph_manager.upload_file(local_path=path, drive_folder_id=self.nvt_mg_obj["id"])

if __name__ == "__main__":
    graph_manager = GraphManager()

    graph_manager.print_all_shared_folders_with_their_ids()






