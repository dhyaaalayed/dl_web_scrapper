from navigator import Navigator
from GraphManager import GraphManager, BAU_FOLDER_ID
from my_functions import log
from selenium.webdriver.common.by import By
import re
from pathlib import Path
import json


BULK_ADDRESSES_STORE_PATH = Path('gbgs_bulk_addresses')
BULK_ADDRESSES_JSON_FILE_NAME = "gbgs_bulk_addresses.json"


class BulkManager:
    # navigator: Navigator = Navigator("markus.lora@dl-projects.de", "Markus1234!")
    navigator = Navigator("dieaa.aled@dl-projects.de", "KXfv*u4wWGT9n#8")
    # Navigator.login("markus.lora@dl-projects.de", "Markus1234!")
    graph_manager: GraphManager = None
    store_path = BULK_ADDRESSES_STORE_PATH
    json_file_name = BULK_ADDRESSES_JSON_FILE_NAME

    def get_bulk_addressses(self):
        """ Calling all function of the process :)
        """
        self.navigator.browser.set_window_size(1600, 1200)
        # self.login("markus.lora@dl-projects.de", "Markus1234!")
        # log("Has logged in")

        self.navigate_to_bulk_page()
        self.navigator.take_screenshot()
        log("After navigating to bulk addresses")
        return self.get_companies_addresses()

    def login(self, username, password):
        self.navigator.login(username, password) # choose unused username and password yet!s

    def navigate_to_bulk_page(self):
        self.navigator.browser.get("https://glasfaser.telekom.de/auftragnehmerportal-ui/bulksupplierui/")
        self.navigator.wait_by_element(By.CSS_SELECTOR, "bulk-installation-order")

    def get_companies_addresses(self):
        companies_addresses = []
        for i in range(1, 1000):

            # self.navigator.browser.refresh()
            # log("Waiting after refresh for 10 seconds")
            # time.sleep(10)

            if self.click_on_page_link(i, "COMPANY"):
                log("Click on companies page link number {}".format(i))
                # then visit
                companies_addresses += self.get_companies_page_addresses()
            else:
                break
        return companies_addresses


    def get_companies_page_addresses(self):
        companies_page_addresses = []
        companies_buttons = self.navigator.browser.find_elements("xpath", '//bulk-installation-order')
        for company_button in companies_buttons:
            log("Clicking on a company button {}".format(company_button.text))
            company_button.click()
            log("Waiting for loading the addresses paginations and the addresses")
            self.navigator.take_screenshot()
            self.navigator.wait_by_element(By.CSS_SELECTOR, "building-order")
            log("End waiting")
            self.navigator.take_screenshot()
            log("Starting getting the clicked company addresses")
            companies_page_addresses += self.get_company_addresses()

        return companies_page_addresses


    def click_on_page_link(self, page_number, pagination_type):
        if page_number == 1:
            # then do not visit because it's already existed
            return True
        else:
            page_button = self.get_page_button(page_number, pagination_type)
            if page_button:

                # self.navigator.javascript_click(page_button)
                page_button.click()
                # TODO implement wait
                self.navigator.take_screenshot()
                if pagination_type == "COMPANY":
                    log("After clicking on companies page link")
                    # Firstly we wait until the button is active
                    self.navigator.wait_by_element(By.XPATH, '//div[@class="bulk-installation-order-list-wrapper"]//ngb-pagination//ul//li[contains(@class,"active")]//a[text()=" {} "]'.format(page_number))
                    print("Finish waiting until page numer {} is active".format(page_number))
                    self.navigator.take_screenshot()
                    # then we wait until the load of the company list
                    self.navigator.wait_by_element(By.CSS_SELECTOR, "bulk-installation-order")
                elif pagination_type == "ADDRESS":
                    # TODO: implement
                    log("After clicking on addresses page link")
                    log("The page number is {}".format(page_number))
                    self.navigator.take_screenshot()
                    self.navigator.wait_by_element(By.XPATH, '//div[@class="pagination-container ligth"]//ngb-pagination//ul//li[@class="page-item ng-star-inserted active"]//a[text()=" {} "]'.format(page_number))
                return True
            else:
                return False

    def get_page_button(self, page_number, pagination_type):
        if pagination_type == "COMPANY":
            # print("try")
            # try_array = self.navigator.browser.find_elements("xpath", '//div[@class="bulk-installation-order-list-wrapper"]')
            # print("try array div: ", try_array)
            # try_array = self.navigator.browser.find_elements("xpath", '//div[@class="bulk-installation-order-list-wrapper"]//ngb-pagination')
            # print("try array ngb-pagination: ", try_array)
            # try_array = self.navigator.browser.find_elements("xpath", '//div[@class="bulk-installation-order-list-wrapper"]//ngb-pagination//ul')
            # print("try array ul: ", try_array)
            # try_array = self.navigator.browser.find_elements("xpath", '//div[@class="bulk-installation-order-list-wrapper"]//ngb-pagination//ul//li')
            # print("try_array li: ", try_array)
            # try_array = self.navigator.browser.find_elements("xpath", '//div[@class="bulk-installation-order-list-wrapper"]//ngb-pagination//ul//li//a')
            # print("try_array a: ", [elm.text for elm in try_array])
            # try_array = self.navigator.browser.find_elements("xpath", '//div[@class="bulk-installation-order-list-wrapper"]//ngb-pagination//ul//li//a[text()=" {} "]'.format(page_number))
            # print("The page number is {}".format(page_number))
            # print("try_array a distination: ", try_array)

            # print("end try")

            page_button: list = self.navigator.browser.find_elements("xpath", '//div[@class="bulk-installation-order-list-wrapper"]//ngb-pagination//ul//li//a[text()=" {} "]'.format(page_number))
        elif pagination_type == "ADDRESS":
            page_button: list = self.navigator.browser.find_elements("xpath", '//div[@class="pagination-container ligth"]//ngb-pagination//ul//li//a[text()=" {} "]'.format(page_number))
        return page_button[0] if len(page_button) > 0 else None



    def get_company_addresses(self):
        """ Iterate over all a company paginations and getting the addresses of each page
        """
        company_addresses = []
        for i in range(1, 1000):
            if self.click_on_page_link(i, "ADDRESS"):
                log("Click on addresses page link number {}".format(i))
                company_addresses += self.get_page_addresses()
            else:
                break
        return company_addresses


    def get_page_addresses(self):
        addresses_rows = self.navigator.browser.find_elements("xpath", '//building-order')
        parsed_addresses_rows_full_text = [row.get_attribute('innerHTML') for row in addresses_rows]
        parsed_addresses_rows_full = [row.text.split('\n') for row in addresses_rows]
        print("parsed_addresses_rows_full_text: ", parsed_addresses_rows_full_text)
        print("parsed_addresses_rows_full: ", parsed_addresses_rows_full)



        parsed_addresses_rows = []
        for row in addresses_rows:
            parsed_address = self.parse_address_array(row.text.split('\n')[:2])
            # Now we have the address as this example: {street: "Dr.-Ernst-Mucke-Str.", number: 4, char: "", postal: 02625, city: Bautzen}
            #, then we need to add more attributes like name(company_name + person_name), phone, mobil, kls_id, fold_id

            try:
                mobile = row.find_element("xpath", './/div[@data-cy="contactMedium_phoneNumberFixed"]').get_attribute('innerHTML')
            except:
                log("Exception occures while reading mobile element")

                mobile = row.find_element("xpath", './/div[@data-cy="contactMedium_phoneNumberMobile"]').get_attribute('innerHTML')
                log("Mobile element after catching the exception: " + mobile)
            
            company_name = row.find_element("xpath", './/div[@data-cy="organizationDetails_organizationName"]').get_attribute('innerHTML')
            person_name = row.find_elements("xpath", './/div[@class="common-column"]//div[@class="content-text ng-star-inserted"]')[1].get_attribute('innerHTML')
            mail = row.find_element("xpath", ".//a[contains(@href, 'mailto')]").get_attribute('href')
            mail = mail.replace("mailto:", "")


            kls_id_fold_id_spans = row.find_elements("xpath", './/div[@class="common-column"]//span')
            kls_id = kls_id_fold_id_spans[0].get_attribute("innerHTML")
            fold_id = kls_id_fold_id_spans[1].get_attribute("innerHTML")
            

            more_attributes = {
                "mobile": mobile,
                "person_name": person_name,
                "company_name": company_name,
                "mail": mail,
                "kls_id": kls_id,
                "fold_id": fold_id

            }
            print("more_attributes: ", more_attributes)

            

            parsed_addresses_rows.append({**parsed_address, **more_attributes})

        # The next commented row to be deleted!
        # parsed_addresses_rows = [self.parse_address_array(row.text.split('\n')[:2]) for row in addresses_rows]
        print("getting addresses of array length {}: ".format(len(parsed_addresses_rows)), parsed_addresses_rows)
        return parsed_addresses_rows

    def parse_address_array(self, address_array):
        """ Input: ['02625 Bautzen', 'Dr.-Ernst-Mucke-Str. 4']
            Output: {
                street: "Dr.-Ernst-Mucke-Str.",
                number: 4,
                char: "",
                postal: 02625,
                city: Bautzen
            }
        """
        return {**self.parse_street_string(address_array[1]), **self.parse_plz_city_string(address_array[0])}


    def parse_street_string(self, street_elm):
        """ Input: Sachsdorfer Str. 5 A
            Output: {
                street: "Sachsdorfer Str.",
                number: 5,
                char: "A"
            }
        """
        number = re.search(r"\d+", street_elm).group()
        street, char = [elm.strip() for elm in street_elm.split(number)]
        return {
            "street": street,
            "number": number,
            "char": char
        }

    def parse_plz_city_string(self, plz_city):
        """ Input: 12345 Berlin
            Output: {
                postal: 12345,
                city: Berlin
            }
        """
        postal, city = plz_city.split(" ")
        return {
            "postal": postal,
            "city": city
        }


    def get_save_upload_addresses(self):
        log("Start the navigator process")
        bulk_addresses = self.get_bulk_addressses() # array
        log("Finish the navigator process")
        log("_________________________________")
        log("Start writing to json")
        self.write_addresses_to_json(bulk_addresses)
        log("Finish writing to json")
        log("_________________________________")
        log("Start the uploading process")
        self.upload_addresses()
        log("Finish the uploading process")
        log("_________________________________")

    def write_addresses_to_json(self, bulk_addresses):
        print("address_array of length {}:".format(len(bulk_addresses)))
        print(bulk_addresses)
        log("Writing to json...")
        self.store_path.mkdir(parents=True, exist_ok=True)
        json_obj = {"bulk_addresses": bulk_addresses}
        with open(self.store_path / self.json_file_name, 'w') as f:
            json.dump(json_obj, f)

    def upload_addresses(self):
        log("Initializing GraphManager obj...")

        self.graph_manager = GraphManager()

        full_path = self.store_path / self.json_file_name

        folder_mg_obj = self.graph_manager.create_or_get_mg_folder_if_existed(parent_id=BAU_FOLDER_ID, new_folder_name=self.store_path.name)
        upload_response = self.graph_manager.upload_file(local_path=full_path, drive_folder_id=folder_mg_obj["id"])
        log("upload_response:")
        print(upload_response)


def main():
    bulk_manager = BulkManager()

    bulk_manager.get_save_upload_addresses()




if __name__ == "__main__":
    main()



