import os
import time
import getpass
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from config import CHROMEDRIVER_PATH
from auth import login_instagram
from crawler import fetch_external_ids
from storage import navigate_and_download_images


def check_internet():
    """Verifica se há conexão com a internet tentando acessar o Google."""
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False


def configure_driver():
    """
    Configura o driver Selenium.
    """
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    service = Service(executable_path=CHROMEDRIVER_PATH)

    attempt = 0
    while True:  # Tenta iniciar o driver até conseguir
        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except WebDriverException as e:
            wait_time = min(2 ** attempt, 60)
            print(f"⚠️ Erro ao iniciar o WebDriver: {e}. Tentando novamente em {wait_time} segundos...")
            time.sleep(wait_time)
            attempt += 1


def main():
    driver = configure_driver()

    attempt = 0
    while True:  # Loop de reconexão global
        if check_internet():
            try:
                # Solicita email e senha ao usuário de forma segura
                email = input("📧 Digite o e-mail: ")
                password = getpass.getpass("🔑 Digite a senha: ")

                # Autenticação
                login_instagram(driver, email, password)

                # Extração de external_ids
                fetch_external_ids(driver)

                # Download de imagens
                navigate_and_download_images(driver)

                break  # Sai do loop caso tudo funcione

            except WebDriverException as e:
                print(f"⚠️ Erro no WebDriver: {e}. Tentando novamente...")

        else:
            wait_time = min(2 ** attempt, 60)
            print(f"❌ Sem conexão com a internet. Tentando novamente em {wait_time} segundos...")
            time.sleep(wait_time)
            attempt += 1

    print("🚪 Encerrando o navegador...")
    driver.quit()


if __name__ == "__main__":
    main()
