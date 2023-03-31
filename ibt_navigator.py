from navigator import Navigator
from entities import Kls, Address
from my_functions import log
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json

class IBTNavigator(Navigator):

    def move_to_the_search_page(self):
        print("Moving to ibt_order_page")
        self.browser.get("https://glasfaser.telekom.de/auftragnehmerportal-ui/order/ibtorder/search")

    def get_and_refresh_eyes_rows(self):
        # tbody: is an html element contains all rows
        tbody = self.browser.find_element("id", 'searchResultForm:orderSRT_data')
        return tbody.find_elements("css selector", 'tr')


    def get_eyes_data(self, nvt_number, nvt_path, already_downloaded_exploration_protocols):
        addresses = []
        eyes_rows = self.get_and_refresh_eyes_rows()
        number_of_rows = len(eyes_rows)
        for eye_row_index in range(number_of_rows):
            self.take_screenshot()
            # refresh eys_lin
            eye_row = eyes_rows[eye_row_index]
            html_columns = eye_row.find_elements('css selector', 'td')

            print("html_columns[8]: ", html_columns[8].get_attribute("outerHTML"))

            postal = html_columns[9].find_element("css selector", "span").text
            city = html_columns[10].find_element("css selector", "span").text
            street = html_columns[11].find_element("css selector", "span").text
            house_number = html_columns[12].find_element("css selector", "span").text
            house_char = html_columns[13].find_element("css selector", "span").text

            next_activity = html_columns[2].find_element("css selector", "span").text
            status = html_columns[3].find_element("css selector", "span").text
            print("status: ", status)
            kls_nvt_number = html_columns[23].find_element("css selector", "span").text
            if nvt_number != kls_nvt_number:
                log("Error: nvt number is different, readed {}, expected {}".format(kls_nvt_number, nvt_number))




            eye_link = html_columns[0].find_element("css selector", 'a')
            print("eye_link: ", eye_link.get_attribute("outerHTML"))
            # Creating Kls object
            address = self.get_eye_data(eye_link, nvt_path, already_downloaded_exploration_protocols) # here an eye link should be given

            address["postal"] = postal
            address["city"] = city
            address["street"] = street
            address["house_number"] = house_number
            address["house_char"] = house_char
            address["status"] = status
            address["next_activity"] = next_activity

            addresses.append(address)
            # Just to refresh
            eyes_rows = self.get_and_refresh_eyes_rows()
        return addresses


    def get_eye_data(self, eye_button, nvt_path, already_downloaded_exploration_protocols: list):

        self.browser.find_elements("xpath", '//a[contains(@id,":viewSelectedRowItem")]')
        self.navigate_to_address_page(eye_button)
        self.wait_by_element("xpath", '//div[@id="processPageForm:addressPanel_header"]')
        print("after waiting")
        self.take_screenshot()
        address = self.get_address()
        self.take_screenshot()
    
        self.close_address_page()
        return address


    def get_address(self):
        address = {}
        kls_element = WebDriverWait(self.browser, 100).until(EC.presence_of_element_located((By.ID, 'processPageForm:klsId')))
        kls_id = kls_element.text
        log("Starting with kls: " + kls_id)
        address["kls_id"] = kls_element.text
        address["fold_id"] = self.browser.find_element("id", "processPageForm:folId").text
        address["building_part"] = self.browser.find_element("id", "processPageForm:buildingPart").text
        
        return address

    def close_address_page(self):
        log("Pressing close button of address page")
        close_button = self.browser.find_element('id', 'page-header-form:closeCioDetailsPage')
        self.browser.execute_script("arguments[0].click();", close_button)
        self.take_screenshot()
        log("Waiting for closing address page")
        WebDriverWait(self.browser, 100).until(
            EC.presence_of_element_located((By.ID, "searchResultForm:orderSRT:col_orderId:filter_label")))


def main():
    print("starting")
    ibt_navigator = IBTNavigator('dieaa.aled@dl-projects.de', 'S8jN##BUq_y6zbu')
    ibt_navigator.browser.set_window_size(1920, 1400)
    ibt_navigator.move_to_the_search_page()
    addresses = ibt_navigator.get_all_nvt_data("42V1010", "", [])
    print(addresses)

if __name__ == "__main__":
    main()