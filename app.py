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
owm = OWM('016bdd85fc2558aef83d0e2962fdbb12', config_dict)
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
            observation = mgr.weather_at_place(f"{city},{country[:2]}")
            weather = observation.weather
            temp = weather.temperature('celsius')['temp']
            temperatures[city] = temp
    return temperatures

# 지리 데이터 로드 (예: Natural Earth 데이터 사용)
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
korea_japan = world[(world.name == 'South Korea') | (world.name == 'Japan')]

# 사용자 정의 colormap 생성
colors = ['darkblue', 'blue', 'lightblue', 'white', 'pink', 'red', 'darkred']
n_bins = 100
cmap = LinearSegmentedColormap.from_list('temp_cmap', colors, N=n_bins)

# Streamlit 앱
st.title('한국과 일본의 실시간 기온 분포')

if st.button('데이터 새로고침'):
    temperatures = get_temperatures()
    
    # 지도 그리기
    fig, ax = plt.subplots(figsize=(12, 8))
    korea_japan.plot(ax=ax, color='lightgrey', edgecolor='black')
    
    # 온도 범위 설정
    temp_min = min(temperatures.values())
    temp_max = max(temperatures.values())
    temp_range = max(abs(temp_min - 15), abs(temp_max - 15))
    vmin, vmax = 15 - temp_range, 15 + temp_range
    
    for city, temp in temperatures.items():
        # 여기서는 도시의 좌표를 수동으로 지정해야 합니다.
        # 실제 구현시에는 정확한 좌표 데이터가 필요합니다.
        x, y = 0, 0  # 각 도시의 실제 좌표로 대체해야 함
        color = cmap((temp - vmin) / (vmax - vmin))
        ax.plot(x, y, 'o', color=color, markersize=10)
        ax.annotate(f"{city}: {temp:.1f}°C", xy=(x, y), xytext=(3, 3), 
                    textcoords="offset points", fontsize=8, 
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.7))
    
    # Colorbar 추가
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, orientation='vertical', label='Temperature (°C)')
    
    plt.title('한국과 일본의 실시간 기온')
    st.pyplot(fig)

    # 표 형태로도 데이터 표시
    st.write(temperatures)
