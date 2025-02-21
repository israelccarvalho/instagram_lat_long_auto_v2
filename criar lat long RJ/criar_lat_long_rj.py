import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from geopy.distance import geodesic

# Baixar os limites do estado do RJ diretamente do IBGE
url = "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2023/UFs/RJ/RJ_UF_2023.zip"
gdf = gpd.read_file(url)  # Lê o arquivo ZIP direto do IBGE

# Filtrar apenas o estado do Rio de Janeiro (código IBGE: 33)
rj = gdf[gdf["CD_UF"] == "33"]

# Definir os limites do estado
minx, miny, maxx, maxy = rj.total_bounds

# Criar grade de pontos espaçados aproximadamente 1 km
points = []
lat = miny
while lat <= maxy:
    lon = minx
    while lon <= maxx:
        point = Point(lon, lat)
        if rj.geometry.contains(point).any():  # Verifica se está dentro do RJ
            points.append((lat, lon))
        lon += 1 / 111  # Aproximadamente 1 km em longitude
    lat += 1 / 111  # Aproximadamente 1 km em latitude

# Salvar em CSV
df = pd.DataFrame(points, columns=["latitude", "longitude"])
df.to_csv("pontos_rj.csv", index=False)

print("Arquivo pontos_rj.csv gerado com sucesso!")
