import os
import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
from pyowm import OWM
from pyowm.utils.config import get_default_config
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# OpenWeatherMap API 설정
config_dict = get_default_config()
config_dict['language'] = 'ko'
api_key = os.getenv('OPENWEATHERMAP_API_KEY')  # 환경 변수에서 API 키 가져오기
owm = OWM(api_key, config_dict)
mgr = owm.weather_manager()

# 한국과 일본의 주요 도시 리스트 (예시)
cities = {
    'Korea': ['Seoul', 'Busan', 'Incheon', 'Daegu', 'Daejeon', 'Gwangju', 'Ulsan'],
    'Japan': ['Tokyo', 'Osaka', 'Yokohama', 'Nagoya', 'Sapporo', 'Fukuoka', 'Kobe']
}

def get_temperatures():
    temperatures = {}
    for country, city_list in cities.items():
        for city in city_list:
            try:
                observation = mgr.weather_at_place(f"{city}")  # 국가 코드 제거
                weather = observation.weather
                temp = weather.temperature('celsius')['temp']
                temperatures[city] = temp
            except Exception as e:
                st.warning(f"Could not fetch data for {city}: {str(e)}")
                temperatures[city] = None
    return temperatures

# 나머지 코드는 그대로 유지...

if st.button('데이터 새로고침'):
    temperatures = get_temperatures()
    
    # 유효한 온도 데이터만 필터링
    valid_temperatures = {k: v for k, v in temperatures.items() if v is not None}
    
    if not valid_temperatures:
        st.error("No valid temperature data available.")
    else:
        # 지도 그리기 코드...

    # 표 형태로도 데이터 표시
    st.write(temperatures)
