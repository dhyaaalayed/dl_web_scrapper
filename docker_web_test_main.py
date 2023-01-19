

from city import City
from nvt import NVT
from my_functions import log
from navigator import Navigator



from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# chrome_options = Options()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--no-sandbox')

# d = webdriver.Chrome('/usr/local/bin',chrome_options=chrome_options)
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--disable-setuid-sandbox")
# chrome_options.add_argument("--headless")
# # chrome_options.add_argument('--start-maximized')
# chrome_options.add_argument('--disable-dev-shm-usage')
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument("--disable-setuid-sandbox")
# chrome_options.experimental_options[""] #("useAutomationExtension", False);



if __name__ == "__main__":
    user_name = "David.peterson@dl-projects.de"
    password = "David2022!"
    navigator = Navigator(user_name, password)
    navigator.move_to_the_search_page()
    nvt = NVT("42V1018", "", city = "DockerCity", navigator = navigator)
    nvt.initialize_using_web_scrapper()
