import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
from pyowm import OWM
from pyowm.utils.config import get_default_config
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import os

# OpenWeatherMap API 설정
config_dict = get_default_config()
config_dict['language'] = 'ko'
api_key = os.getenv('OPENWEATHERMAP_API_KEY')  # 환경 변수에서 API 키 가져오기
owm = OWM(api_key, config_dict)
mgr = owm.weather_manager()

# 한국과 일본의 주요 도시 리스트 (예시)와 좌표
cities = {
    'Korea': {
        'Seoul': (126.9780, 37.5665),
        'Busan': (129.0756, 35.1796),
        'Incheon': (126.7052, 37.4563),
        'Daegu': (128.6014, 35.8714),
        'Daejeon': (127.3845, 36.3504),
        'Gwangju': (126.8514, 35.1595),
        'Ulsan': (129.3114, 35.5384)
    },
    'Japan': {
        'Tokyo': (139.6917, 35.6895),
        'Osaka': (135.5023, 34.6937),
        'Yokohama': (139.6380, 35.4437),
        'Nagoya': (136.9066, 35.1815),
        'Sapporo': (141.3545, 43.0621),
        'Fukuoka': (130.4017, 33.5904),
        'Kobe': (135.1955, 34.6901)
    }
}

def get_temperatures():
    temperatures = {}
    for country, city_list in cities.items():
        for city, coords in city_list.items():
            try:
                observation = mgr.weather_at_place(f"{city},{country}")  # 국가 코드 추가
                weather = observation.weather
                temp = weather.temperature('celsius')['temp']
                temperatures[city] = temp
            except Exception as e:
                st.warning(f"Could not fetch data for {city}: {str(e)}")
                temperatures[city] = None
    return temperatures

# 지리 데이터 로드
@st.cache_data
def load_geo_data():
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    korea_japan = world[(world.name == 'South Korea') | (world.name == 'Japan')]
    return korea_japan

# 지리 데이터 로드
korea_japan = load_geo_data()

# 사용자 정의 colormap 생성
colors = ['darkblue', 'blue', 'lightblue', 'white', 'pink', 'red', 'darkred']
n_bins = 100
cmap = LinearSegmentedColormap.from_list('temp_cmap', colors, N=n_bins)

# Streamlit 앱
st.title('한국과 일본의 실시간 기온 분포')

if st.button('데이터 새로고침'):
    temperatures = get_temperatures()
    
    # 유효한 온도 데이터만 필터링
    valid_temperatures = {k: v for k, v in temperatures.items() if v is not None}
    
    if not valid_temperatures:
        st.error("No valid temperature data available.")
    else:
        # 지도 그리기
        fig, ax = plt.subplots(figsize=(12, 8))
        korea_japan.plot(ax=ax, color='lightgrey', edgecolor='black')
        
        # 온도 범위 설정
        temp_min = min(valid_temperatures.values())
        temp_max = max(valid_temperatures.values())
        temp_range = max(abs(temp_min - 15), abs(temp_max - 15))
        vmin, vmax = 15 - temp_range, 15 + temp_range
        
        for city, temp in valid_temperatures.items():
            for country, city_list in cities.items():
                if city in city_list:
                    x, y = city_list[city]
                    color = cmap((temp - vmin) / (vmax - vmin))
                    ax.plot(x, y, 'o', color=color, markersize=10)
                    ax.annotate(f"{city}: {temp:.1f}°C", xy=(x, y), xytext=(3, 3), 
                                textcoords="offset points", fontsize=8, 
                                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.7))
        
        # Colorbar 추가
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, orientation='vertical', label='Temperature (°C)')
        
        plt.xlim(120, 150)  # 지도 범위를 한국과 일본 중심으로 설정
        plt.ylim(24, 46)
        plt.title('한국과 일본의 실시간 기온')
        st.pyplot(fig)

    # 표 형태로도 데이터 표시
    st.write(temperatures)
