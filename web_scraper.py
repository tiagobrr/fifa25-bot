from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
import time

def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.binary_location = "/opt/chrome/chrome"  # Caminho correto no Render
    return uc.Chrome(options=options)

def get_live_matches():
    url = "https://football.esportsbattle.com"
    driver = create_driver()
    driver.get(url)
    time.sleep(7)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    matches = soup.find_all("div", class_="match-card")

    partidas = []
    data_coleta = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for match in matches:
        try:
            team_names = match.find_all("div", class_="participant__nickname")
            if len(team_names) != 2:
                continue

            team1 = team_names[0].text.strip()
            team2 = team_names[1].text.strip()

            players = match.find_all("div", class_="participant__name")
            player1 = players[0].text.strip()
            player2 = players[1].text.strip()

            league = match.find("div", class_="match__league").text.strip()
            stadium = match.find("div", class_="match__stadium").text.strip()
            datetime_real = match.find("div", class_="match__date").text.strip()

            partidas.append({
                "horario_coleta": data_coleta,
                "player1": player1,
                "player2": player2,
                "team1": team1,
                "team2": team2,
                "league": league,
                "stadium": stadium,
                "datetime_real": datetime_real
            })

        except Exception as e:
            print("Erro ao processar uma partida:", e)

    driver.quit()

    df = pd.DataFrame(partidas)
    df.to_csv("partidas_ao_vivo.csv", index=False)
    print(f"{len(df)} partidas salvas com sucesso.")
