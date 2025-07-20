import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from models import Match
from constants import Players_fifa25, Teams_fifa25, Stadiums_fifa25, Leagues_fifa25

URL = "https://football.esportsbattle.com"

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)

def get_live_matches():
    driver = create_driver()
    driver.get(URL)
    time.sleep(5)  # aguarda o carregamento dos cards

    matches = []
    cards = driver.find_elements(By.CSS_SELECTOR, ".match-card")

    for card in cards:
        try:
            # Times
            teams = card.find_elements(By.CSS_SELECTOR, ".match-card__team-name")
            if len(teams) != 2:
                continue
            team1 = teams[0].text.strip()
            team2 = teams[1].text.strip()
            if team1 not in Teams_fifa25 or team2 not in Teams_fifa25:
                continue

            # Jogadores
            players = card.find_elements(By.CSS_SELECTOR, ".match-card__player-nick")
            if len(players) != 2:
                continue
            player1 = players[0].text.strip()
            player2 = players[1].text.strip()
            if player1 not in Players_fifa25 or player2 not in Players_fifa25:
                continue

            # Data/Hora
            raw_time = card.find_element(By.CSS_SELECTOR, ".match-card__time").text.strip()
            match_time = datetime.strptime(raw_time, "%H:%M")

            # Estádio
            stadium_elem = card.find_element(By.CSS_SELECTOR, ".match-card__stadium")
            stadium = stadium_elem.text.strip() if stadium_elem else "Unknown"
            if stadium not in Stadiums_fifa25:
                continue

            # Liga
            league_elem = card.find_element(By.CSS_SELECTOR, ".match-card__tournament-name")
            league = league_elem.text.strip() if league_elem else "Unknown"
            if league not in Leagues_fifa25:
                continue

            # Objeto Match (sem placar e winner pois ainda está ao vivo)
            match = Match(
                team1=team1,
                team2=team2,
                player1=player1,
                player2=player2,
                datetime=datetime.now(),  # pode ajustar para usar match_time
                score1=None,
                score2=None,
                winner=None,
                stadium=stadium,
                league=league,
                source="live"
            )
            matches.append(match)

        except Exception as e:
            print(f"[❌] Erro ao processar card: {e}")
            continue

    driver.quit()
    return matches
