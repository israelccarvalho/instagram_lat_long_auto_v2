import json
import os
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import INSTAGRAM_URL


def carregar_cookies(driver):
    """
    Carrega os cookies salvos para uma sessão já autenticada.
    """
    if os.path.exists("cookies.json"):
        with open("cookies.json", "r") as file:
            cookies = json.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
        print("✅ Cookies carregados com sucesso!")
        return True
    return False


def login_instagram(driver, email, password):
    """
    Realiza login no Instagram e salva os cookies de sessão.
    """
    driver.get(INSTAGRAM_URL)
    wait = WebDriverWait(driver, 30)

    # Verifica se já existem cookies salvos
    if carregar_cookies(driver):
        # Pergunta ao usuário se quer continuar com a conta salva ou fazer login com uma nova conta
        resposta = input("Conta salva encontrada. Deseja usar essa conta? (s/n): ").strip().lower()
        if resposta == 's':
            print("Usando conta salva!")
            return  # Não é necessário fazer o login novamente
        else:
            print("Fazendo login com uma nova conta...")

    try:
        # Caso não haja cookies ou o usuário opte por uma nova conta
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        # Preencher os campos de login
        email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="username"]')))
        email_input.clear()
        email_input.send_keys(email)

        password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]')))
        password_input.clear()
        password_input.send_keys(password)

        # Clicar no botão de login
        login_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[type="submit"]')))
        login_button.click()

        # Esperar algum tempo aleatório para parecer mais natural
        time.sleep(random.uniform(5, 10))

        # Salvar os cookies após o login
        cookies = driver.get_cookies()
        with open("cookies.json", "w") as file:
            json.dump(cookies, file)
        print("✅ Cookies salvos com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao realizar login: {e}")
        raise
