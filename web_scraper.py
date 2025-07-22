from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.binary_location = "/usr/bin/google-chrome-stable"
    return webdriver.Chrome(options=options)

def main():
    driver = create_driver()
    driver.get("https://football.esportsbattle.com")
    time.sleep(7)  # aguarda carregar os cards

    cards = driver.find_elements(By.CSS_SELECTOR, ".match-card")
    print(f"Total de cards encontrados: {len(cards)}")

    for card in cards:
        print(card.text)
        print("-----")

    driver.quit()

if __name__ == "__main__":
    main()
