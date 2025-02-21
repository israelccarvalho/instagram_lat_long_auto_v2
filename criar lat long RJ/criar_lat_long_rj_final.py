import geopandas as gpd
import pandas as pd
import numpy as np
import requests
import zipfile
import os
from shapely.geometry import Point
from tqdm import tqdm

# URL do IBGE
url = "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2022/UFs/RJ/RJ_UF_2022.zip"

# Nome do arquivo ZIP para salvar
zip_path = "RJ_UF_2022.zip"
shp_folder = "RJ_SHP"

# Baixar o arquivo ZIP se não existir
if not os.path.exists(zip_path):
    print("Baixando arquivo do IBGE...")
    response = requests.get(url, stream=True)
    with open(zip_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024):
            file.write(chunk)
    print("Download concluído!")

# Extrair os arquivos do ZIP
if not os.path.exists(shp_folder):
    print("Extraindo arquivos...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(shp_folder)
    print("Extração concluída!")

# Encontrar o arquivo SHP correto
shp_path = None
for file in os.listdir(shp_folder):
    if file.endswith(".shp"):
        shp_path = os.path.join(shp_folder, file)
        break

if shp_path is None:
    raise FileNotFoundError("Arquivo SHP não encontrado no ZIP extraído.")

# Carregar os dados
print("Carregando os dados do shapefile...")
gdf = gpd.read_file(shp_path)

# Converter CRS para EPSG:4326
gdf = gdf.to_crs("EPSG:4326")
print("CRS convertido para:", gdf.crs)

# Obter os limites do estado do RJ
minx, miny, maxx, maxy = gdf.total_bounds
print(f"Limites do RJ: min({minx}, {miny}) max({maxx}, {maxy})")

# Criar uma grade de pontos espaçados 1 km (~0.009 graus)
step = 1 / 111  # Aproximadamente 1 km em graus

# Gerar todas as combinações de latitude e longitude
lats = np.arange(miny, maxy, step)
lons = np.arange(minx, maxx, step)

# Criar meshgrid para gerar a grade
lon_grid, lat_grid = np.meshgrid(lons, lats)
lat_flat = lat_grid.ravel()
lon_flat = lon_grid.ravel()

# Criar índice espacial para otimizar buscas
rj_sindex = gdf.sindex  
print("Índice espacial construído!")

# Criar pontos e verificar se estão dentro do RJ
points = []
total = len(lat_flat)

print("Total de pontos gerados:", total)
print("Processando pontos...")

for i in tqdm(range(total)):
    point = Point(lon_flat[i], lat_flat[i])
    
    # Verificar se há interseção rápida com alguma geometria do RJ
    possible_matches = list(rj_sindex.intersection(point.bounds))
    if possible_matches:
        if any(gdf.geometry.iloc[j].contains(point) for j in possible_matches):
            points.append((lat_flat[i], lon_flat[i]))

# Debug: Exibir alguns pontos encontrados
if len(points) > 0:
    print("Primeiros pontos encontrados:")
    print(points[:5])
else:
    print("Nenhum ponto foi identificado dentro do RJ. Verifique os dados.")

# Salvar em CSV
df = pd.DataFrame(points, columns=["latitude", "longitude"])
df.to_csv("pontos_rj.csv", index=False)

print(f"Arquivo 'pontos_rj.csv' gerado com {len(points)} pontos!")
