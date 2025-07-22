import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from datetime import datetime
import pytz

def create_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return uc.Chrome(options=options)

def get_live_matches():
    driver = create_driver()
    driver.get("https://football.esportsbattle.com")
    time.sleep(7)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    cards = soup.find_all("div", class_="live-match-item")

    matches = []
    for card in cards:
        try:
            league = card.select_one(".match-league").text.strip()
            stadium = card.select_one(".match-location").text.strip()
            datetime_str = card.select_one(".match-date").text.strip()
            dt = datetime.strptime(datetime_str, "%d.%m.%Y %H:%M")
            dt = pytz.timezone("Europe/Kiev").localize(dt)

            players = card.select(".match-item .team .player-name")
            teams = card.select(".match-item .team .team-name")
            if len(players) == 2 and len(teams) == 2:
                match = {
                    "datetime": dt,
                    "league": league,
                    "stadium": stadium,
                    "player1": players[0].text.strip(),
                    "team1": teams[0].text.strip(),
                    "player2": players[1].text.strip(),
                    "team2": teams[1].text.strip()
                }
                matches.append(match)
        except Exception as e:
            print(f"Erro ao processar card: {e}")

    driver.quit()
    return matches
