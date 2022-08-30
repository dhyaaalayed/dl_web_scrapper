from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import time
from entities import Kls, Address, Person, Owner
from my_functions import log

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--start-maximized')

"""
ATTENTION:
xpath does not work inside an element, it works inside the whole web page instead!
Therefore, using css selector is better.
Examples:
Finding eye_link inside eye_row using css selector, by using xpath, it will find all eye_links over all rows! 
"""

class Navigator:

    browser = None

    def __init__(self):
        self.browser = Chrome(options = chrome_options)
        self.login()
        log("Loging in")
        self.move_to_the_search_page()
        log("Moving to the search page")

        # self.apply_first_filter() # Disabled upon Hakan request!
        # log("Applying Gap installation Filter")

    def login(self):

        URL = "https://glasfaser.telekom.de/auftragnehmerportal-ui/home?a-cid=50708"
        self.browser.get(URL)
        self.browser.find_element('id', 'username').send_keys('ertugrul.yilmaz@dl-projects.de')
        self.browser.find_element('id', 'password').send_keys('Ertu2022!')
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

    def filter_in_nvt(self, nvt_number):
        log("Start filtering in kls list according to nvt_number: " + nvt_number)
        self._enter_nvt_number(nvt_number)

        log("Clicking the search button")
        self.click_the_search_button()

    def _enter_nvt_number(self, nvt_number):
        log(nvt_number)
        # First we need to click on nvt div to show the input of entering nvt number:
        nvt_filter_div = self.browser.find_element("id", "searchCriteriaForm:nvtArea")
        self.browser.execute_script("arguments[0].click();", nvt_filter_div)

        WebDriverWait(self.browser, 100).until(EC.presence_of_element_located((By.ID,  "searchCriteriaForm:nvtArea_input")))

        # the id of the input field to enter nvt number: searchCriteriaForm: nvtArea_input
        nvt_input_field = self.browser.find_element('xpath', '//input[@id="searchCriteriaForm:nvtArea_input"]')
        nvt_input_field.send_keys(nvt_number)
        # self.browser.execute_script("arguments[0].setAttribute('value', '{}');".format(nvt_number), nvt_input_field)

        # Waiting for drowpdown spans to select the nvt number
        self.browser.set_window_size(1920, 1400)
        self.browser.save_screenshot('/Users/dlprojectsit/Desktop/Github_local/web_scrapper/screenshot.png')
        log("Waiting for dropdown list to select the span of the nvt")

        nvt_span = WebDriverWait(self.browser, 100).until(EC.presence_of_element_located((By.CLASS_NAME, "ui-autocomplete-query")))
        log("Clicking on the nvt span")
        self.browser.execute_script("arguments[0].click();", nvt_span)

        log("Waiting for NVT Filtering until loading li element of NVT: {}".format(nvt_number))
        WebDriverWait(self.browser, 100).until(EC.presence_of_element_located((By.XPATH, '//li[@data-token-value="{}"]'.format(nvt_number))))
        log("Li element of NVT {} is loaded".format(nvt_number))

    def click_the_search_button(self):
        search_button_element = self.browser.find_element('id', 'searchCriteriaForm:searchButton')
        search_button_element.click()

        log("Waiting for loading the table after pressing the search button")
        WebDriverWait(self.browser, 100).until(EC.presence_of_element_located((By.XPATH, '//tr[@data-ri="0" and @role="row"]')))

    def click_reset_filter_button(self):
        reset_button = self.browser.find_element('id', 'searchCriteriaForm:resetButton')
        reset_button.click()

    def navigate_to_address_page(self, eye_button):
        print("Log: Navigating to address page")
        self.browser.execute_script("arguments[0].click();", eye_button);
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

    def get_eye_data(self, eye_button):
        """
            eye_date: means one kls record that contains:
                    kls_id
                    address
                    list of people
                    list of owners
        """

        kls = Kls()
        self.browser.find_elements("xpath", '//a[contains(@id,":viewSelectedRowItem")]')
        self.navigate_to_address_page(eye_button)
        kls_id, address = self.get_address_data_with_kls_id()
        kls.id = kls_id
        kls.address = address
    
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

    def get_eyes_data(self, nvt_number):
        kls_list = []
        eyes_rows = self.get_and_refresh_eyes_rows()
        number_of_rows = len(eyes_rows)
        for eye_row_index in range(number_of_rows):

            # refresh eys_lin
            eye_row = eyes_rows[eye_row_index]
            html_columns = eye_row.find_elements('css selector', 'td')

            status = html_columns[2].find_element("css selector", "span").text
            kundentermin_start = html_columns[12].find_element("css selector", "span").text
            kundentermin_end = html_columns[13].find_element("css selector", "span").text
            kls_nvt_number = html_columns[23].find_element("css selector", "span").text
            if nvt_number != kls_nvt_number:
                log("Error: nvt number is different, readed {}, expected {}".format(kls_nvt_number, nvt_number))

            log("reading kls status: " + status)
            log("reading kls kundentermin_start: " + kundentermin_start)
            log("reading kls kundentermin_end: " + kundentermin_end)
            log("reading kls nvt")


            eye_link = html_columns[0].find_element("css selector", 'a')

            # Creating Kls object
            kls = self.get_eye_data(eye_link) # here an eye link should be given
            kls.address.status = status
            kls.address.kundentermin_start = kundentermin_start
            kls.address.kundentermin_end = kundentermin_end
            kls_list.append(kls)
            # Just to refresh
            eyes_rows = self.get_and_refresh_eyes_rows()
        return kls_list

    def get_address_data_with_kls_id(self):
        address = Address()
        kls_element = WebDriverWait(self.browser, 100).until(EC.presence_of_element_located((By.ID, 'processPageForm:klsId')))
        kls_id = kls_element.text
        log("Starting with kls: " + kls_id)
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

















