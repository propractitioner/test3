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
        # 지도 그리기
        fig, ax = plt.subplots(figsize=(12, 8))
        korea_japan.plot(ax=ax, color='lightgrey', edgecolor='black')
        
        # 온도 범위 설정
        temp_min = min(valid_temperatures.values())
        temp_max = max(valid_temperatures.values())
        temp_range = max(abs(temp_min - 15), abs(temp_max - 15))
        vmin, vmax = 15 - temp_range, 15 + temp_range
        
        for city, temp in valid_temperatures.items():
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

    # 표 형태로도 데이터 표시 (이 줄은 if-else 블록 바깥에 있어야 함)
    st.write(temperatures)
