import time
import json
import random
import pandas as pd
from selenium.webdriver.common.by import By
from config import LATLONG_CSV, EXTERNAL_ID_CSV


def fetch_external_ids(driver):
    """
    Processa latitude e longitude para extrair external_ids e salva no CSV, sobrescrevendo o arquivo.
    Durante a execução, evita duplicatas.
    """
    latlong_data = pd.read_csv(LATLONG_CSV)
    external_ids = set()  # Usamos um conjunto para evitar duplicações

    for _, row in latlong_data.iterrows():
        latitude, longitude = row['latitude'], row['longitude']
        url = f"https://www.instagram.com/location_search/?latitude={latitude}&longitude={longitude}"
        print(f"🌍 Acessando URL: {url}")
        driver.get(url)
        time.sleep(random.uniform(4, 7))  # Espera aleatória para evitar bloqueios

        try:
            response = driver.find_element(By.TAG_NAME, "pre").text
            data = json.loads(response)

            venues = data.get('venues', [])
            for venue in venues:
                external_id = venue.get('external_id')
                if external_id and external_id not in external_ids:
                    external_ids.add(external_id)
                    print(f"📍 Encontrado external_id: {external_id}")

        except Exception as e:
            print(f"❌ Erro ao buscar external_ids para latitude={latitude}, longitude={longitude}: {e}")

    # Salva os external_ids em um novo arquivo CSV
    if external_ids:
        pd.DataFrame({'external_id': list(external_ids)}).to_csv(EXTERNAL_ID_CSV, index=False)
        print(f"✅ {len(external_ids)} external_ids salvos em {EXTERNAL_ID_CSV} (arquivo sobrescrito).")
    else:
        print("🔍 Nenhum external_id encontrado.")
