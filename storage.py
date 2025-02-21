import os
import time
import random
import requests
import pandas as pd
from selenium.webdriver.common.by import By
from config import IMAGE_DIR, EXTERNAL_ID_CSV


def download_images_with_scroll(driver, external_id):
    """
    Baixa imagens de uma página, rolando até o final de forma incremental.
    Salva cada imagem e cria um arquivo .txt contendo a URL da imagem e da postagem.
    """
    output_dir = os.path.join(IMAGE_DIR, str(external_id))
    os.makedirs(output_dir, exist_ok=True)

    # Lista de arquivos já baixados para evitar duplicação
    downloaded_files = set(os.listdir(output_dir))

    print(f"📸 Iniciando coleta de imagens para {external_id}...")
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        posts = driver.find_elements(By.CSS_SELECTOR, 'a[class*="_a6hd"]')  # Busca o elemento com a URL da postagem
        images = driver.find_elements(By.TAG_NAME, "img")  # Busca todas as imagens

        post_urls = {}
        for post in posts:
            post_href = post.get_attribute("href") or post.get_attribute("data-href")
            if post_href and "/p/" in post_href:
                post_urls[post_href] = post_href  # Armazena a URL completa

        for img in images:
            img_url = img.get_attribute("src")
            if not img_url:
                continue

            img_name = img_url.split("/")[-1].split("?")[0]  # Nome do arquivo de imagem
            img_path = os.path.join(output_dir, img_name)
            txt_path = os.path.join(output_dir, f"{img_name}.txt")  # Arquivo .txt

            # Verifica se a imagem já foi baixada
            if img_name in downloaded_files:
                continue

            try:
                response = requests.get(img_url)
                response.raise_for_status()

                # Salva a imagem
                with open(img_path, "wb") as file:
                    file.write(response.content)

                # Obtém a URL da postagem associada à imagem (se disponível)
                post_url = next(iter(post_urls.values()), "Desconhecido")

                # Salva a URL da imagem e da postagem em um arquivo de texto
                with open(txt_path, "w") as txt_file:
                    txt_file.write(f"Post URL: {post_url}\n")
                    txt_file.write(f"Image URL: {img_url}\n")

                print(f"✅ Imagem salva: {img_path}")
                print(f"📝 URL da postagem e imagem salva: {txt_path}")

            except Exception as e:
                print(f"❌ Erro ao baixar imagem de {img_url}: {e}")

        # Rolar até o final da página
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(8, 15))

        # Verificar se chegou ao final da página
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("🏁 Fim da página alcançado.")
            break
        last_height = new_height


def navigate_and_download_images(driver):
    """
    Navega para as URLs usando os external_ids e baixa as imagens.
    """
    external_ids = pd.read_csv(EXTERNAL_ID_CSV)['external_id']

    for external_id in external_ids:
        url = f"https://www.instagram.com/explore/locations/{external_id}/"
        print(f"🔗 Acessando {url}")
        driver.get(url)
        time.sleep(random.uniform(8, 20))
        download_images_with_scroll(driver, external_id)
