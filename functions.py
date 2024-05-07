import pandas as pd
import json
import requests
import geopandas as gpd
import streamlit as st

# '----------------법정동 코드 불러오기--------------'
df_lesi = pd.read_csv('./code.txt', sep='\t')
df_lesi = df_lesi.loc[df_lesi['폐지여부'] == '존재']


# '----------------함수 정의--------------'
#필요 함수 정의
def get_data(key, pnuCode):
    """
    연속지적도

    종류: 2D 데이터API 2.0
    분류: 토지
    서비스명: 연속지적도
    서비스ID: LP_PA_CBND_BUBUN
    제공처: 국토교통부
    버전: 1.0
    - key: Vworld Open API 인증키
    - pnuCode: PNU코드 19자리
    """
    # 엔드포인트
    endpoint = "http://api.vworld.kr/req/data"

    # 요청 파라미터
    service = "data"
    request = "GetFeature"
    data = "LP_PA_CBND_BUBUN"
    page = 1
    size = 1000
    attrFilter = f"pnu:=:{pnuCode}"

    # 요청 URL
    url = f"{endpoint}?service={service}&request={request}&data={data}&key={key}&attrFilter={attrFilter}&page={page}&size={size}"
    # 요청 결과
    res = json.loads(requests.get(url).text)
    # GeoJson 생성
    featureCollection = res["response"]["result"]["featureCollection"]

    return featureCollection

#'읍면동'인 경우와 '리'인 경우를 나누어야함
#읍면동인 경우 법정동코드 앞 8자리 가져온 후 뒤에 '00'을 추가
#리인 경우 법정동코드 앞 10자리 

def get_pnu(txt):
    #txt는 정식 지번 주소
    # 법정동 추출
    adm = ' '.join(txt.split(' ')[:-1])
    if adm[-1] != '리':
        adm_cd = str(df_lesi.loc[df_lesi['법정동명'].str.contains(adm),'법정동코드'].values)[1:9]
        adm_cd = f'{adm_cd}00'
    else:
        adm_cd = str(df_lesi.loc[df_lesi['법정동명'].str.contains(adm),'법정동코드'].values)[1:-1]

    # 본번 및 지목구분 추출
    bonbun, *rest = txt.split(' ')[-1].split('-')
    gubun = '2' if '산' in bonbun else '1'
    bonbun = bonbun.strip('산').zfill(4)

    # 부번추출
    bubun = rest[0].zfill(4) if rest else '0000'
    return adm_cd + gubun + bonbun + bubun

def calculate_centroid(polygon):
    x_sum = 0
    y_sum = 0
    num_points = 0

    for polygon in polygon:
        for ring in polygon:
            for point in ring:
                x_sum += point[0]
                y_sum += point[1]
                num_points += 1

    centroid_x = x_sum / num_points
    centroid_y = y_sum / num_points

    return centroid_x, centroid_y

#위, 경도 좌표와 용도지역 검색용 중심점 생성함수
def calculate_centroid_test(poly):
    centroid = poly.centroid
    x = centroid.x
    y = centroid.y
    # 폴리곤 내부에 중심점이 있는지 확인
    if poly.contains(centroid):
        # 중심점이 폴리곤 내부에 있으면 그대로 사용
        point_inside_poly = centroid
    else:
        # 중심점이 폴리곤 외부에 있으면 폴리곤 내부의 가장 가까운 점으로 이동
        nearest_point_inside_poly, _ = nearest_points(poly, centroid)
        point_inside_poly = nearest_point_inside_poly
    s_t = str(point_inside_poly).split('(')
    s1 = s_t[0].strip(' ').lower()
    s2 = s_t[1]
    geom = '('.join([s1,s2])
    return x, y, geom

def get_prps(key, geom):
    """
    연속지적도

    종류: 2D 데이터API 2.0
    분류: 토지
    서비스명: 연속지적도
    서비스ID: LP_PA_CBND_BUBUN
    제공처: 국토교통부
    버전: 1.0
    - key: Vworld Open API 인증키
    - pnuCode: PNU코드 19자리
    """
    # 엔드포인트
    endpoint = "http://api.vworld.kr/req/data"
    # endpoint = "https://api.vworld.kr/ned/data/getLandUseAttr"   
    # 요청 파라미터
    service = "data"
    request = "GetFeature"
    data = "LT_C_UQ111"
    page = 1
    geomFilter = geom
    size = 1000

    # 요청 URL
    url = f"{endpoint}?service={service}&request={request}&data={data}&key={key}&geomfilter={geomFilter}&page={page}&size={size}"
    # 요청 결과
    res = json.loads(requests.get(url).text)
    # GeoJson 생성
    featureCollection = res['response']['result']['featureCollection']['features'][0]['properties']

    # return featureCollection
    return featureCollection





