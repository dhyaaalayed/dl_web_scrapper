import os
import shutil
import uuid
from datetime import date
from pathlib import Path

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import time
from entities import Kls, Address, Person, Owner
from my_functions import log

chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument('--start-maximized')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--disable-setuid-sandbox")

exploration_protocols_download_path = Path('BAU/exploration_protocols')
exploration_protocols_download_path.mkdir(parents=True, exist_ok=True)
download_option = {'download.default_directory': str(exploration_protocols_download_path)}

chrome_options.add_experimental_option('prefs', download_option)

"""
ATTENTION:
xpath does not work inside an element, it works inside the whole web page instead!
Therefore, using css selector is better.
Examples:
Finding eye_link inside eye_row using css selector, by using xpath, it will find all eye_links over all rows! 
"""

class Navigator:

    browser = None

    def __init__(self, user_name, password):
        self.browser = Chrome(options = chrome_options)
        self.login_with_dieaa()
        log("Loging in")
        self.move_to_the_search_page()
        log("Moving to the search page")

        # self.apply_first_filter() # Disabled upon Hakan request!
        # log("Applying Gap installation Filter")

    def login(self, user_name, password):

        URL = "https://glasfaser.telekom.de/auftragnehmerportal-ui/home?a-cid=50708"
        self.browser.get(URL)
        self.browser.find_element('id', 'username').send_keys(user_name) # 'ertugrul.yilmaz@dl-projects.de'
        self.browser.find_element('id', 'password').send_keys(password) # 'Ertu2022!'
        self.browser.find_element('name', 'login').click()

    def logout(self):
        URL = "https://glasfaser.telekom.de/auftragnehmerportal-ui/logout"
        self.browser.get(URL)
        # Attention: we need to wait for an element to be loaded after logout
        # and regarding Telekom website it's a bit difficult


    def login_with_dieaa(self):
        URL = "https://glasfaser.telekom.de/auftragnehmerportal-ui/home?a-cid=50708"
        self.browser.get(URL)
        self.browser.find_element('id', 'username').send_keys('dieaa.aled@dl-projects.de')
        self.browser.find_element('id', 'password').send_keys('Dieaa1234!')
        self.browser.find_element('name', 'login').click()


    def move_to_the_search_page(self):
        self.browser.get("https://glasfaser.telekom.de/auftragnehmerportal-ui/property/search")

    def apply_first_filter(self): # GFAP_INSTALLATION Filter
        time.sleep(2)
        # Get the select of the filter value directly and click on it!
        gap_installation_option = self.browser.find_element('xpath', '//option[@value="GFAP_INSTALLATION"]')
        # gap_installation_option.click()
        self.browser.execute_script("arguments[0].click();", gap_installation_option);
        time.sleep(3)

    def get_all_nvt_data(self, nvt_number: str, nvt_path, already_downloaded_exploration_protocols):
        """
            This is the main function and the main goal of this class
            The main goal is just to return the kls_list
            Because the nvt is just a list of kls :)
        """
        self.filter_in_nvt(nvt_number)
        kls_list = self.visit_eyes_pages(nvt_number, nvt_path, already_downloaded_exploration_protocols)
        if kls_list == None:
            self.refresh_page()
        return kls_list


    def visit_eyes_pages(self, nvt_number: str, nvt_path, already_downloaded_exploration_protocols: list):
        kls_list = []
        for i in range(1, 1000):
            number_of_rows = self.log_number_of_eyes_of_current_page(i)
            if number_of_rows == 0:
                return None

            kls_list += self.get_eyes_data(nvt_number, nvt_path, already_downloaded_exploration_protocols)

            if not self.navigate_to_next_page(i + 1):
                break
        return kls_list

    def filter_in_nvt(self, nvt_number):
        log("Start filtering in kls list according to nvt_number: " + nvt_number)
        self._enter_nvt_number(nvt_number)

        log("Clicking the search button")
        self.click_the_search_button()

    def take_screenshot(self):
        self.browser.set_window_size(1920, 1400)
        self.browser.save_screenshot('/Users/dlprojectsit/Desktop/Github_local/web_scrapper/screenshot.png')

    def refresh_page(self):
        self.browser.refresh()
        WebDriverWait(self.browser, 100).until(EC.presence_of_element_located((By.ID,  "searchCriteriaForm:nvtArea")))

    def _enter_nvt_number(self, nvt_number):
        log(nvt_number)
        WebDriverWait(self.browser, 100).until(EC.presence_of_element_located((By.ID,  "searchCriteriaForm:nvtArea")))
        self.take_screenshot()
        # First we need to click on nvt div to show the input of entering nvt number:
        nvt_filter_div = self.browser.find_element("id", "searchCriteriaForm:nvtArea")
        self.browser.execute_script("arguments[0].click();", nvt_filter_div)

        WebDriverWait(self.browser, 100).until(EC.presence_of_element_located((By.ID,  "searchCriteriaForm:nvtArea_input")))

        # the id of the input field to enter nvt number: searchCriteriaForm: nvtArea_input
        nvt_input_field = self.browser.find_element('xpath', '//input[@id="searchCriteriaForm:nvtArea_input"]')
        nvt_input_field.send_keys(nvt_number)
        # self.browser.execute_script("arguments[0].setAttribute('value', '{}');".format(nvt_number), nvt_input_field)

        # Waiting for drowpdown spans to select the nvt number


        log("Waiting for dropdown list to select the span of the nvt")

        nvt_span = WebDriverWait(self.browser, 100).until(EC.presence_of_element_located((By.CLASS_NAME, "ui-autocomplete-query")))
        log("Clicking on the nvt span")
        self.browser.execute_script("arguments[0].click();", nvt_span)

        log("Waiting for NVT Filtering until loading li element of NVT: {}".format(nvt_number))
        # self.take_screenshot()
        WebDriverWait(self.browser, 100).until(EC.presence_of_element_located((By.XPATH, '//li[@data-token-value="{}"]'.format(nvt_number))))
        log("Li element of NVT {} is loaded".format(nvt_number))

    def click_the_search_button(self):
        search_button_element = self.browser.find_element('id', 'searchCriteriaForm:searchButton')
        search_button_element.click()

        table_rows = EC.presence_of_element_located((By.XPATH, '//tr[@data-ri="0" and @role="row"]'))
        no_result_span = EC.presence_of_element_located((By.XPATH, '//span[text()="{}"]'.format("The search did not yield any results.")))
        any_of = EC.any_of(
            no_result_span,
            table_rows
        )

        log("Waiting for loading the table after pressing the search button")

        WebDriverWait(self.browser, 100).until(any_of)
        # WebDriverWait(self.browser, 100).until( EC.invisibility_of_element_located((By.XPATH, '//span[text()="{}"]'.format("The search did not yield any results."))))

    def click_reset_filter_button(self):
        reset_button = self.browser.find_element('id', 'searchCriteriaForm:resetButton')
        reset_button.click()

        log("Waiting after clicking the reset button")
        WebDriverWait(self.browser, 100).until(
            EC.presence_of_element_located((By.XPATH, '//tr[@class="ui-widget-content ui-datatable-empty-message"]')))

    def navigate_to_address_page(self, eye_button):
        print("Log: Navigating to address page")
        self.browser.execute_script("arguments[0].click();", eye_button)
        # time.sleep(2)

    def get_next_page_button(self, index):
        next_page_button = self.browser.find_elements("xpath", '//a[@aria-label="Page {}"]'.format(index))
        if len(next_page_button) > 0:
            return next_page_button[0]
        return None



    def navigate_to_next_page(self, index):
        next_page_button = self.get_next_page_button(index)
        if next_page_button == None:
            return False
        else:
            self.browser.execute_script("arguments[0].click();", next_page_button)
            log("Waiting after pressing next page button")
            WebDriverWait(self.browser, 100).until(
                EC.presence_of_element_located((By.XPATH, '//a[@class="ui-paginator-page ui-state-default ui-corner-all ui-state-active" and @aria-label="Page {}"]'.format(str(index)) )))
            return True

    def log_number_of_eyes_of_current_page(self, i):
        eys_links = self.browser.find_elements("xpath", '//a[contains(@id,":viewSelectedRowItem")]')
        print("Log: Number of rows is ", len(eys_links), " in Page ", str(i))
        return len(eys_links)

    def download_exploration_protocol(self, nvt_path, address_key):
        """
            Downloads the pdf if the button is enabled and returns true.
            Returns false if the button is disabled.
        """
        download_button = self.browser.find_element("id", "processPageForm:explorationProtocol")
        pdf_name = "Auskundungsprotokolle_{}_date_{}_id_{}.pdf".format(address_key, date.today().strftime('%Y_%m_%d'), str(uuid.uuid4()))
        pdf_path: Path = nvt_path / "Auskundungsprotokolle" / pdf_name
        
        if download_button.get_attribute("aria-disabled") == "false":
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            log("Downloading Auskundungsprotokolle {}:".format(pdf_name))
            self.browser.execute_script("arguments[0].click();", download_button)
            log("Wait until download is completed")
            # we need to wait until downloading the file and also until the extension is pdf,
            # otherwise another extension like .pdf.crdownload will be returned before continuing the download process!
            while len(os.listdir(exploration_protocols_download_path)) == 0 or os.listdir(exploration_protocols_download_path)[0].endswith(".crdownload"):
                time.sleep(1)
            downloaded_pdf_name = os.listdir(exploration_protocols_download_path)[0]
            log("The name of the downloaded pdf {}".format(downloaded_pdf_name))
            log("Moving the pdf to {}".format(str(pdf_path)))
            # rename with pathlib = moving files :)
            downloaded_pdf_path: Path = exploration_protocols_download_path / downloaded_pdf_name

            log("Moving the pdf: ")
            log("src: {}".format(str(downloaded_pdf_path) ))
            log("dst: {}".format(str(pdf_path) ))
            shutil.move(src=str(downloaded_pdf_path), dst=str(pdf_path))
            # another moving method, but it did not work!
            # downloaded_pdf_path.rename(pdf_path) # Moving procedure
            return True
        return False


    def get_eye_data(self, eye_button, nvt_path, already_downloaded_exploration_protocols: list):
        """
            eye_date: means one kls record that contains:
                    kls_id
                    address
                    list of people
                    list of owners

            nvt_path: very important parameter to store Auskundigung protocol!
            already_downloaded_exploration_protocols: a list parsed from the stored json of the nvt
                to check if the exploration protocol is included in the list or not
        """

        kls = Kls()
        self.browser.find_elements("xpath", '//a[contains(@id,":viewSelectedRowItem")]')
        self.navigate_to_address_page(eye_button)
        kls_id, address = self.get_address_data_with_kls_id()
        kls.id = kls_id
        kls.address = address
        address_key = address.create_unique_key()
        if address_key not in already_downloaded_exploration_protocols:
            kls.address.exploration_protocol_already_downloaded = self.download_exploration_protocol(nvt_path, address_key)
        else:
            kls.address.exploration_protocol_already_downloaded = True

        self.navigate_to_contact_people_tab()
        kls.people = self.get_contact_people_list()
    
        self.navigate_to_owner_tab()
        kls.owners = self.get_owners_list()
    
        self.close_address_page()
        return kls

    def get_and_refresh_eyes_rows(self):
        # tbody: is an html element contains all rows
        tbody = self.browser.find_element("id", 'searchResultForm:propertySearchSRT_data')
        return tbody.find_elements("css selector", 'tr')

    def get_exploration_necessary(self, html_column):
        exp_necessary = html_column.find_element("css selector", 'input').get_attribute("aria-checked")
        return True if exp_necessary == "true" else False

    def get_finished_properties(self, html_column):
        exp_finished = html_column.find_element("css selector", 'input').get_attribute("aria-checked")
        return True if exp_finished == "true" else False

    def get_eyes_data(self, nvt_number, nvt_path, already_downloaded_exploration_protocols):
        kls_list = []
        eyes_rows = self.get_and_refresh_eyes_rows()
        number_of_rows = len(eyes_rows)
        for eye_row_index in range(number_of_rows):

            # refresh eys_lin
            eye_row = eyes_rows[eye_row_index]
            html_columns = eye_row.find_elements('css selector', 'td')

            status = html_columns[2].find_element("css selector", "span").text
            expl_necessary = html_columns[4].find_element("css selector", "input").get_attribute("aria-checked")
            expl_finished = html_columns[8].find_element("css selector", "input").get_attribute("aria-checked")
            kundentermin_start = html_columns[12].find_element("css selector", "span").text
            kundentermin_end = html_columns[13].find_element("css selector", "span").text
            gfap_inst_status = html_columns[10].find_element("css selector", "span").text
            we = html_columns[14].find_element("css selector", "span").text
            kls_nvt_number = html_columns[23].find_element("css selector", "span").text
            if nvt_number != kls_nvt_number:
                log("Error: nvt number is different, readed {}, expected {}".format(kls_nvt_number, nvt_number))

            log("reading kls status: " + status)
            log("reading kls kundentermin_start: " + kundentermin_start)
            log("reading kls kundentermin_end: " + kundentermin_end)
            log("reading kls nvt")


            eye_link = html_columns[0].find_element("css selector", 'a')

            # Creating Kls object
            kls = self.get_eye_data(eye_link, nvt_path, already_downloaded_exploration_protocols) # here an eye link should be given
            kls.address.status = status
            kls.address.kundentermin_start = kundentermin_start
            kls.address.kundentermin_end = kundentermin_end
            kls.address.we = we
            kls.address.gfap_inst_status = gfap_inst_status
            kls.address.expl_necessary = expl_necessary
            kls.address.expl_finished = expl_finished
            kls_list.append(kls)
            # Just to refresh
            eyes_rows = self.get_and_refresh_eyes_rows()
        return kls_list

    def get_address_data_with_kls_id(self):
        address = Address()
        kls_element = WebDriverWait(self.browser, 100).until(EC.presence_of_element_located((By.ID, 'processPageForm:klsId')))
        kls_id = kls_element.text
        log("Starting with kls: " + kls_id)
        address.kls_id = kls_element.text
        address.fold_id = self.browser.find_element("id", "processPageForm:folId").text
        address.street = self.browser.find_element("id", "processPageForm:street").text
        address.house_number = self.browser.find_element("id", "processPageForm:houseNumber").text
        address.postal = self.browser.find_element("id", "processPageForm:postalCode").text
        address.city = self.browser.find_element("id", "processPageForm:city").text
        address.house_char = self.browser.find_element("id", "processPageForm:houseNumberApp").text
        return kls_id, address

    def navigate_to_contact_people_tab(self):
        log("Navigating to contact tab")
        contact_tab_button = self.browser.find_element("xpath", '//a[@href="#processPageForm:propertyTabView:contactData"]')
        self.browser.execute_script("arguments[0].click();", contact_tab_button);
        WebDriverWait(self.browser, 100).until(EC.presence_of_element_located((By.ID, 'processPageForm:propertyTabView:contactDataTable_data')))

    def get_contact_people_list(self):
        contact_table = self.browser.find_element("id", "processPageForm:propertyTabView:contactDataTable_data")
        if "No contact persons available" in contact_table.get_attribute("outerHTML"):
            print("There is no contact people!")
            return []
        contact_peaple_rows = contact_table.find_elements('css selector', 'tr')
        contact_peaple_list = []
        for pearson_row in contact_peaple_rows:
            html_columns = pearson_row.find_elements('css selector', 'td')
            person = Person()
            person.name = html_columns[0].find_element('css selector', 'span').text
            person.role = html_columns[1].find_element('css selector', 'span').text
            person.fixedline = html_columns[2].find_element('css selector', 'span').text
            person.mobile = html_columns[3].find_element('css selector', 'span').text
            person.email = html_columns[4].find_element('css selector', 'span').text
            person.sms = html_columns[5].find_element('css selector', 'span').text
            person.preferred = html_columns[6].find_element('css selector', 'span').text
            contact_peaple_list.append(person)
            log("Reading contact person: " + str(person))
        return contact_peaple_list

    def navigate_to_owner_tab(self):
        log("Navigating to owner tab")
        owner_tab_button = self.browser.find_element("xpath", '//a[@href="#processPageForm:propertyTabView:propertyOwner"]')
        self.browser.execute_script("arguments[0].click();", owner_tab_button);
        WebDriverWait(self.browser, 100).until(EC.presence_of_element_located((By.ID, 'processPageForm:propertyTabView:propertyOwnerTable_data')))

    def get_owners_list(self):
        owners_list = []
        owners_table = self.browser.find_element("id", "processPageForm:propertyTabView:propertyOwnerTable_data")
        owners_rows = owners_table.find_elements('css selector', 'tr')
        for owner_row in owners_rows:
            html_columns = owner_row.find_elements('css selector', 'td')
            owner = Owner()
            owner.name = html_columns[0].find_element('css selector', 'span').text
            owner.email = html_columns[1].find_element('css selector', 'span').text
            owner.mobil = html_columns[2].find_element('css selector', 'span').text
            owner.linenumber = html_columns[3].find_element('css selector', 'span').text
            owner.postcode = html_columns[4].find_element('css selector', 'span').text
            owner.city = html_columns[5].find_element('css selector', 'span').text
            owner.street = html_columns[6].find_element('css selector', 'span').text
            owner.housenumber = html_columns[7].find_element('css selector', 'span').text
            owner.decisionmaker = html_columns[8].find_element('css selector', 'input').get_attribute("aria-checked")
            log("Reading owner: " + str(owner))
            owners_list.append(owner)
        return owners_list

    def close_address_page(self):
        log("Pressing close button of address page")
        close_button = self.browser.find_element('id', 'page-header-form:closePropertyDetailsPage')
        self.browser.execute_script("arguments[0].click();", close_button)

        log("Waiting for closing address page")
        WebDriverWait(self.browser, 100).until(
            EC.presence_of_element_located((By.ID, "searchResultForm:propertySearchSRT:col_klsId:filter_label")))

















