import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import logging

def create_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # 🚨 Caminho fixo do Chrome no Render
    options.binary_location = "/usr/bin/google-chrome"

    return uc.Chrome(options=options)

def get_live_matches():
    url = "https://football.esportsbattle.com/"
    driver = create_driver()
    driver.get(url)

    time.sleep(7)  # ou use WebDriverWait para mais precisão

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    matches = soup.find_all("div", class_="match")

    print(f"🔍 {len(matches)} partidas encontradas")

    driver.quit()
    return matches
