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
from notifier import NOTIFIER
from security_config import user_name, password
from entities import Address

# Drive id of Derla Device, where we have the BAU and other folders!
DRIVE_ID = "b!t3YEe8U8mkSNKqGW2Jx1iTQpNwrZTC5Bob7-032a29z3_1Qd4gMtTo_N_SKBLQH0"
BAU_FOLDER_ID = "01A6QGC52KCABYH3NEJRDYM37SPH5MQPYF"



class GraphManager:
    access_token = None
    client = None
    headers = None
    GRAPH_API_ENDPOINT = None
    path_id_dict = {}

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
        scopes = ['User.Read', 'Files.ReadWrite.All', 'Mail.Send', 'Mail.ReadWrite']
        client = msal.ClientApplication(
            app_id, authority="https://login.microsoftonline.com/organizations/",
            client_credential=client_secret,
        )
        access_token_req = client.acquire_token_by_username_password(username=user_name,
                                                                 password=password, scopes=scopes)
        print("access_token_req: ", access_token_req)
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

    def upload_file(self, local_path: Path, drive_folder_id):
        file_size = local_path.stat().st_size
        media_content = self.encode_file(local_path)
        file_name = Path(local_path).name
        if file_size > 4000000:
            log("Upload large file")
            upload_url = self.create_upload_session(file_name, drive_folder_id)
            log("upload_url {}: ".format(upload_url))
            response = self.upload_large_file(file_size=file_size, media_content=media_content, upload_url=upload_url)
            requests.delete(upload_url)  # to cancel the upload session
            log("response: ")
            print(response.json())
        else:
            response = self.upload_small_file(file_name, media_content, drive_folder_id)
        print("response.status_code: ", response.status_code)
        if response.status_code == 200:
            log("Uploading succeded of {}".format(local_path.name))
        elif response.status_code == 201:
            log("Uploading succeded of {} for the FIRST TIME!".format(local_path.name))
        else:
            logging_string = "Uploading failed of {}".format(local_path.name)
            NOTIFIER.add_failed_uploaded_file(local_path.name)
            log(logging_string)
        return response

    def upload_small_file(self, file_name, media_content, drive_folder_id):

        response = requests.put(
            self.GRAPH_API_ENDPOINT + f'/drives/{DRIVE_ID}/items/{drive_folder_id}:/{file_name}:/content',
            headers=self.headers,
            data=media_content
        )
        return response

    def create_upload_session(self, file_name: str, drive_folder_id: str):
        """
            For Large files > 4 MB, we need to create an upload session
            We need to get the upload_url from the session in order to be able to upload the file.
        """
        response = requests.post(
            self.GRAPH_API_ENDPOINT + f'/drives/{DRIVE_ID}/items/{drive_folder_id}:/{file_name}:/createUploadSession',
            headers = self.headers,

        )
        upload_url = response.json()["uploadUrl"]
        return upload_url

    def upload_large_file(self, file_size: int, media_content: bytes, upload_url: str):

        headers = {
            "Content-Length": "{}".format(file_size),
            "Content-Range": "bytes 0-{}/{}".format(file_size - 1, file_size)
        }
        return requests.put(
            upload_url,
            headers = headers,
            data=media_content
        )


    def upload_folder_files(self, local_folder_path: Path, drive_folder_id: str):
        """
            We assume that the local folder contains only files not folders
        """
        for file in local_folder_path.glob("*.pdf"):
            log("Uploading file: {}".format(str(file)))
            response = self.upload_file(file, drive_folder_id)

            log("Upload file response: ")
            print(response.json())

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
        """ this is a gbgs function
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

    # Non gbgs function
    def get_nvt_ids_and_hk_city_bvh_rv_for_project_one(self, subcity_path):
        """
            This function does not belong to gbgs, it's just to migrate the data to projects-one
            Example:
                {
                    hk1:{
                        nvt1:{},
                        nvt2:{}
                    },
                    hk2:{
                        nvt3:{},
                        nvt4:{}
                    }
                }

        """
        subcity_id = self.get_path_id(subcity_path)

        hks_dict = {} # contains dict of hks as keys and for each key we have dict of nvts
        hk_folders = self.get_folder_subfolders_by_id(subcity_id)
        hk_folders = [folder for folder in hk_folders if "NVT" in folder["name"]]
        for hk_folder in hk_folders:

            iter_nvt_folders = self.get_folder_subfolders_by_id(hk_folder["id"])
            iter_nvt_folders = [folder for folder in iter_nvt_folders if "NVT" in folder["name"]]

            # adding the hk with it's nvts together
            hk_name = hk_folder["name"].split(" ")[1] # Ex. "HK 1R22 + NVT 1100" then we take only 1R22
            hks_dict[hk_name] = {nvt_folder["name"].replace("NVT ", ""): {} for nvt_folder in iter_nvt_folders}

        return hks_dict



    def get_next_item_in_path(self, parent_id, item_name):
        """
            Returns a dict of an item.
        """
        response = requests.get(
            self.GRAPH_API_ENDPOINT + f"/drives/{DRIVE_ID}/items/{parent_id}/children('{item_name}')",
            headers=self.headers,
        )
        if response.status_code == 200:
            return response.json()
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
            Creates a new folder and returns the mg obj of it
            Params:
                parent_id: folder id that we want to create the new folder in
                new_folder_name: the name of the new folder
        """
        headers = self.headers

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

    def create_or_get_mg_folder_if_existed(self, parent_id: str, new_folder_name: str):
        """
            Gets the mg obj of a folder, or creates a new folder and returns the mg obj for it if it's not existed
        """
        folder_mg_obj = self.get_next_item_in_path(parent_id=parent_id, item_name=new_folder_name)
        if folder_mg_obj == None:
            folder_mg_obj = self.create_new_folder(parent_id=parent_id, new_folder_name=new_folder_name)
        return folder_mg_obj


    def print_all_shared_folders_with_their_ids(self):
        """
            This function is used by adding a new BVH shared folder for Telekom
            then, we copy the id of it manually to the city_config.json file
            in order to be used by mg_json_main.py to put the master excel inside it
        """
        response = requests.get(
            graph_manager.GRAPH_API_ENDPOINT + f'/me/insights/shared',
            headers=graph_manager.headers,
        )
        # json.dumps with intend = 4 parameter just to print the json object in a pretty way
        print(json.dumps(response.json(), indent = 4) )

    def send_email(self, message:str, recipients: list):

        request_body = {
            "message": {
                    "subject": "GBGS Automatic Mail",
                    "body": {
                        "contentType": "Text",
                        "content": message
                    },
            "toRecipients": [
                    {"emailAddress":{"address": mail}} for mail in recipients
                    ],
                },

            }
        return requests.post(
            self.GRAPH_API_ENDPOINT + '/me/sendMail',
            headers=self.headers,
            json=request_body
        )
    def download_bulk_addresses_json(self):
        BULK_ADDRESSES_STORE_PATH = Path('BAU') / 'gbgs_bulk_addresses'
        BULK_ADDRESSES_JSON_FILE_NAME = "gbgs_bulk_addresses.json"

        download_folder = Path("BAU") / "downloaded_gbgs_bulk_addresses"

        download_folder.mkdir(parents=True, exist_ok=True)
        json_mg_obj = self.get_path_mg_obj(BULK_ADDRESSES_STORE_PATH / BULK_ADDRESSES_JSON_FILE_NAME)
        self.download_file(json_mg_obj, download_folder)

    def download_bvh_telekom_addresses(self, bvh_root_path):
        download_folder = Path(bvh_root_path) / "Baupläne (HK+NVT)" / "telekom_list"
        file_name = "telekom_addresses.csv"
        download_folder.mkdir(parents=True, exist_ok=True)
        telekom_addresses_mg_obj = self.get_path_mg_obj(download_folder / file_name)
        self.download_file(telekom_addresses_mg_obj, download_folder)
        

    def get_bulk_addresses(self):
        """
            1- Call download_bulk_addresses_json
            2- Read the json and return an array of addresses as dicts
        """
        self.download_bulk_addresses_json()
        with open(Path("BAU") / "downloaded_gbgs_bulk_addresses" / "gbgs_bulk_addresses.json") as handler:
            addresses_dict = json.load(handler)

        json_format_addresses = addresses_dict["bulk_addresses"]
        parsed_addresses = []
        for json_address in json_format_addresses:
            address = Address()
            address.street = json_address["street"]
            address.house_number = json_address["number"]
            address.house_char = json_address["char"]
            address.postal = json_address["postal"]
            address.city = json_address["city"]
            address.building_part = "" # TODO: must stay like that! because telekom does not offer building part for this kind of addresses

            # other fields
            address.mobile = json_address["mobile"]
            address.person_name = json_address["person_name"]
            address.company_name = json_address["company_name"]
            address.email = json_address["mail"]
            address.kls_id = json_address["kls_id"]
            address.fold_id = json_address["fold_id"]
            
            parsed_addresses.append(address)
        return parsed_addresses



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
        self.automated_data_folder_mg_obj = self.graph_manager.create_or_get_mg_folder_if_existed(self.nvt_mg_obj["id"], "automated_data")
        self.montage_excel_mg_obj = self.get_montage_excel_mg_obj()
        self.archive_folder_mg_obj = self.graph_manager.create_or_get_mg_folder_if_existed(self.nvt_mg_obj["id"], "Archive")
        # paths
        # self.nvt_download_path = self.graph_manager.download_folder / "NVT {}".format(self.nvt_number)
        # self.nvt_to_upload_path = self.graph_manager.upload_folder / "NVT {}".format(self.nvt_number)
        self.nvt_path = nvt_path

    def get_montage_excel_mg_obj(self):
        return self.graph_manager.get_next_item_in_path(self.nvt_mg_obj["id"], "Montageliste_{}.xlsx".format(self.nvt_number))
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
        date_archive_folder_mg_obj = self.create_dated_archive_folder(archive_date)
        print("self.montage_excel_mg_obj: ", self.montage_excel_mg_obj)
        print("date_archive_folder_mg_obj: ", date_archive_folder_mg_obj)
        self.graph_manager.copy_item(self.montage_excel_mg_obj["id"]
                                     ,   "Montageliste_{}_{}.xlsx".format(self.nvt_number, generated_unique_key)
                                     , date_archive_folder_mg_obj["id"])

    def get_archived_montage_mg_obj(self, date, archived_montage_name):
        archive_montage_liste_folder = self.graph_manager.get_next_item_in_path(self.archive_folder_mg_obj["id"], "montage_liste")
        archive_date_folder_mg_obj = self.graph_manager.get_next_item_in_path(archive_montage_liste_folder["id"], date)
        return self.graph_manager.get_next_item_in_path(archive_date_folder_mg_obj["id"], archived_montage_name)

    # def download_archived_montage(self, date, archived_montage_name):

    def unarchive_montage_excel(self, date, key):
        """
            date: "2023-02-28" as an example
            key: "f4df0ce5_252d_4ab3_9508_1547949a047a"
        """
        # 1- download the archived file
        archived_montage_name = "Montageliste_{}_{}.xlsx".format(self.nvt_number, key)
        download_archived_file_folder_path = self.nvt_path / date
        download_archived_file_path = download_archived_file_folder_path / archived_montage_name
        archived_montage_mg_obj = self.get_archived_montage_mg_obj(date, archived_montage_name)
        download_archived_file_folder_path.mkdir(parents=True, exist_ok=True)
        self.graph_manager.download_file(archived_montage_mg_obj, download_archived_file_folder_path)

        # 2- rename the archived file to delete the key
        archived_montage_path_without_key = download_archived_file_path.rename("Montageliste_{}.xlsx".format(self.nvt_number))

        # 3- replace the current montage with this one
        self.graph_manager.upload_file(local_path=archived_montage_path_without_key, drive_folder_id=self.nvt_mg_obj["id"])




    def create_dated_archive_folder(self, archive_date: str):
        """
            Checks out first if there is already a created folder of the same name
            If not, then it creates one and it returns its id
            archive_date example: 2022_09_01
        """
        montage_archive_folder = self.graph_manager.create_or_get_mg_folder_if_existed(self.archive_folder_mg_obj["id"], "montage_liste")
        return self.graph_manager.create_or_get_mg_folder_if_existed(montage_archive_folder["id"], archive_date)


    def upload_nvt_json_file(self):
        path = self.nvt_path / "automated_data" / "nvt_telekom_data.json"
        if os.path.exists(path):
            self.graph_manager.upload_file(local_path=path, drive_folder_id=self.automated_data_folder_mg_obj["id"])
            log("uploading generated gpgs json to one drive")
        else:
            log("No generated gpgs json file to upload")

    def upload_nvt_ibt_json_file(self):
        path = self.nvt_path / "automated_data" / "nvt_telekom_ibt_data.json"
        if os.path.exists(path):
            self.graph_manager.upload_file(local_path=path, drive_folder_id=self.automated_data_folder_mg_obj["id"])
            log("uploading generated gpgs json to one drive")
        else:
            log("No generated gpgs json file to upload")


    def upload_nvt_telekom_addresses_excel(self):
        path = self.nvt_path / "automated_data" / "telekom_addresses.xlsx"
        if os.path.exists(path):
            self.graph_manager.upload_file(local_path=path, drive_folder_id=self.automated_data_folder_mg_obj["id"])
            log("uploading telekom_addresses.xlsx to one drive of nvt: {}".format(self.nvt_number))
        else:
            log("No telekom_addresses.xlsx file to upload of nvt: {}".format(self.nvt_number))


    def get_exploration_protocol_mg_obj(self):
        folder_mg_obj = self.graph_manager.get_next_item_in_path(self.nvt_mg_obj["id"], "Auskundungsprotokolle")
        if folder_mg_obj == None: # then we need to create a new folder
            folder_mg_obj = self.graph_manager.create_new_folder(self.nvt_mg_obj["id"], "Auskundungsprotokolle")
        return folder_mg_obj
    def upload_exploration_protocols_pdfs(self):
        local_path = self.nvt_path / "Auskundungsprotokolle"
        protocol_folder_mg_obj = self.get_exploration_protocol_mg_obj()
        self.graph_manager.upload_folder_files(local_folder_path=local_path, drive_folder_id=protocol_folder_mg_obj["id"])

    def upload_montage_excel(self):
        path = self.nvt_path / "Montageliste_{}.xlsx".format(self.nvt_number)
        self.graph_manager.upload_file(local_path=path, drive_folder_id=self.nvt_mg_obj["id"])

    def upload_ansprechspartner_excel(self):
        path = self.nvt_path / "AnsprechpartnerListe_{}.xlsx".format(self.nvt_number)
        self.graph_manager.upload_file(local_path=path, drive_folder_id=self.nvt_mg_obj["id"])

if __name__ == "__main__":
    graph_manager = GraphManager()
    graph_manager.print_all_shared_folders_with_their_ids()
    # "DL Projects - Telekom Wilsdruff"
    # graph_manager.send_email("test_mail", ["dhyaa.alayed@gmail.com", "dieaa.aled@dl-projects.de"])





