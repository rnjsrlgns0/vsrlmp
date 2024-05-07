import streamlit as st
from streamlit_folium import st_folium
from shapely.geometry import Point, MultiPolygon, Polygon, MultiLineString,MultiPoint

import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from tqdm import tqdm

import folium 
from folium.features import DivIcon 
from functions import *

import urllib.request
import urllib.parse
from urllib.request import urlopen, Request
from urllib.parse import urlencode, quote_plus    
from urllib.request import urlretrieve
import requests
import xmltodict
import json

# api_key = st.text_input('key를 입력하세요: ')
api_key = '2EA147E4-BEDA-3115-BBD0-8E09F3DD0FED'
#### pnu 수집
poi = st.text_input('원하는 장소의 정확한 지번주소를 넣어주세요, ex) 경기도 시흥시 은행동 599-1, 경기도 시흥시 은행동 599-2:  ')
li_poi = poi.split(', ')
li_pnu = []

# '----------------데이터 프레임 및 폴리움 지도 생성--------------'
region_nm = ' '.join(li_poi[0].split(' ')[:-1])
for i in li_poi:
    if len(i.split(' ')) > 3:
        i = i
    else:
        i = region_nm + ' ' + i
    li_pnu.append(get_pnu(i))

#중심점 좌표를 통한 배경지도 가져오기
pnu_center = li_pnu[len(li_pnu)//2]
#중심점 구하기
polygon_center = MultiPolygon(get_data(api_key, pnu_center)['features'][0]['geometry']['coordinates'])
x_c, y_c, _ = calculate_centroid_test(polygon_center)


tiles = "http://mt0.google.com/vt/lyrs=s&hl=ko&x={x}&y={y}&z={z}"
# 속성 설정
attr = "Google"

# folium 지도 생성하기
m = folium.Map(
    location=[y_c, x_c],
    zoom_start=22,
    tiles = tiles,
    attr = attr
)
df = pd.DataFrame(columns=['지번주소', '공시지가', '지목', 'area', '토지이용계획'],
                  index = range(1, len(li_pnu)+1)) #index 1번부터 나가게 조정 토지 위 마커와 일치해야함

#리턴되지 않는 주소 모음
li_error = []

# 수집한 pnu로 geometry 가져오기
for i, j in zip(li_pnu, range(1,len(li_pnu)+1)):
    try: 
        geo = get_data(api_key,i)
        geo_center =  MultiPolygon(geo['features'][0]['geometry']['coordinates'])
        # x_c_1, y_c_1 = calculate_centroid(geo_center)
        x_c_1, y_c_1, _ = calculate_centroid_test(geo_center)
        geo_plan = get_prps(api_key, _)


        folium.map.Marker([y_c_1, x_c_1],
                            icon = DivIcon(
                                    icon_size = (20, 20),
                                    html = f'<div style = "font-size: 12pt; font-weight: bold; color: white;">{j}</div>'                                  
                            )
                            ).add_to(m)
        folium.GeoJson(data=geo,
                    name="geojson",
                    tooltip=folium.GeoJsonTooltip(fields=('pnu', 'addr', 'jibun','jiga','gosi_year','gosi_month'),
                                                    aliases=('PNU코드', '주소','지번/지목','공시지가','기준연도','기준월'))
                    ).add_to(m)
        addr = geo['features'][0]['properties']['addr'] # 지자체명 포함 지번주소
        try:
            jiga = format(int(geo['features'][0]['properties']['jiga']),',')+'원' # 최신공시지가
        except:
            jiga = geo['features'][0]['properties']['jiga']
        prps = geo['features'][0]['properties']['jibun'][-1]

        plan = geo_plan['uname']

        df.loc[j, '토지이용계획'] = plan
        df.loc[j,'지번주소'] = addr
        df.loc[j,'공시지가'] = jiga
        df.loc[j,'지목'] = prps
    except:
        li_error.append(i)
        pass

# call to render Folium map in Streamlit

# '----------------데이터 프레임 생성--------------'
df = df.loc[~df['공시지가'].isna()]
st.table(df)

# '----------------지도 생성--------------'
st_data = st_folium(m, width=1450)

