import geopandas as gpd

shp_path = "RJ_UF_2022.shp"  # Ajuste se necessário

# Carregar o shapefile
gdf = gpd.read_file(shp_path)

# Exibir informações gerais do arquivo
print("Dados carregados do SHP:")
print(gdf.head())
print("\nSistema de Coordenadas:", gdf.crs)
print("\nLimites do RJ:", gdf.total_bounds)
