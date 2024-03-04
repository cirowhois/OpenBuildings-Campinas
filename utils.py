import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon


def calc_area(ingdf,crs):
    return ingdf["geometry"].to_crs(crs).area


def gdf_creator_from_file(inpath,mask):
    gdf = gpd.read_file(inpath,mask=mask)
    gdf = gdf.to_crs(4674)
    return gdf


def create_grid(ingdf,width):
    # Bounding box
    minx, miny, maxx, maxy = ingdf['geometry'].to_crs(31983).buffer(100).bounds.iloc[0].astype('int')
 
    # Largura do Grid  
    cell_width = width
    
    # Lista de retângulos/quadrados
    polygons = []
    for x in range(minx, maxx, cell_width):
        for y in range(miny, maxy, cell_width):
            polygons.append(Polygon([(x, y), (x + cell_width, y), (x + cell_width, y + cell_width), (x, y + cell_width)]))
    
    # GeoDataFrame
    gdf = gpd.GeoDataFrame(geometry=polygons,crs=31983)
    gdf["AREA_GRID_M2"] = gdf["geometry"].area
    gdf = gdf.to_crs(4674)
    
    # Filtra área que toca/intersecta o gdf de referência
    gdf = gdf.sjoin(ingdf,how='inner').reset_index(drop=True)
    gdf["GRID_ID"] = gdf.index
    
    return gdf


def generate_classes(ingdf,class_column,target_column,binlist,labellist):
    ingdf[class_column] = pd.cut(ingdf[target_column], bins=binlist, labels=labellist)
    ingdf[class_column] = ingdf[class_column].astype(str)
    #ingdf[class_column].replace('nan','N/A',inplace=True)
    return ingdf


def generate_quarteis(ingdf,area_column,quarteis_column,perccum_column,binlist,labellist):

    # Percentual acumulado do grid com menor área edificada ao grid com maior área edificada
    ingdf = ingdf.sort_values(by=area_column, ignore_index=True)
    ingdf[perccum_column] = (ingdf[[area_column]].cumsum() / ingdf[[area_column]].sum())*100

    # Definição dos Quartéis
    ingdf = generate_classes(ingdf, quarteis_column, perccum_column, binlist, labellist)
    ingdf.drop(perccum_column, axis=1)
    
    return ingdf