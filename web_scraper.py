from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
import time


class FIFA25Scraper:
    def __init__(self):
        self.driver = self.init_driver()

    def init_driver(self) -> WebDriver:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    def get_live_matches(self):
        url = "https://football.esportsbattle.com"
        self.driver.get(url)
        time.sleep(5)  # Espera carregar o JavaScript

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        matches = []

        match_cards = soup.select("div.matches-list__match")
        for card in match_cards:
            try:
                status = card.select_one("div.match__status").text.strip()
                if status.lower() != "live":
                    continue

                time_match = card.select_one("div.match__time").text.strip()
                stadium = card.select_one("div.match__stadium").text.strip()
                league = card.select_one("div.match__tournament").text.strip()

                team1 = card.select_one("div.match__team--left div.match__team-name").text.strip()
                team2 = card.select_one("div.match__team--right div.match__team-name").text.strip()

                player1 = card.select_one("div.match__team--left div.match__team-player").text.strip()
                player2 = card.select_one("div.match__team--right div.match__team-player").text.strip()

                match_data = {
                    "status": status,
                    "time": time_match,
                    "stadium": stadium,
                    "league": league,
                    "team1": team1,
                    "team2": team2,
                    "player1": player1,
                    "player2": player2,
                }
                matches.append(match_data)
            except Exception:
                continue  # Ignora erros em algum card malformado

        return matches

    def close(self):
        self.driver.quit()

