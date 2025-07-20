from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def get_live_matches():
    url = "https://football.esportsbattle.com/"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    driver.get(url)
    time.sleep(5)  # tempo para o site carregar

    soup = BeautifulSoup(driver.page_source, "html.parser")
    cards = soup.find_all("div", class_="match-card")

    matches = []
    for card in cards:
        try:
            league = card.find("div", class_="match__league").text.strip()
            date_time = card.find("div", class_="match__date").text.strip()
            stadium = card.find("div", class_="match__stadium").text.strip()
            teams = [team.text.strip() for team in card.find_all("div", class_="match__team-name")]
            players = [p.text.strip() for p in card.find_all("div", class_="match__player-nick")]

            match = {
                "league": league,
                "datetime": date_time,
                "stadium": stadium,
                "team1": teams[0] if len(teams) > 0 else "",
                "team2": teams[1] if len(teams) > 1 else "",
                "player1": players[0] if len(players) > 0 else "",
                "player2": players[1] if len(players) > 1 else "",
            }
            matches.append(match)
        except Exception as e:
            print("Erro ao processar um card:", e)

    driver.quit()
    return matches

