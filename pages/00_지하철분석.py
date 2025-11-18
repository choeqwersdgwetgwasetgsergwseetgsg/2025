# requirements.txt
streamlit
pandas
matplotlib

###############################################
# pages/subway_app.py (Streamlit Application) #
###############################################

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from datetime import datetime

# Load CSV from parent folder
df = pd.read_csv("../subyway.csv", encoding="cp949")

st.title("🚇 2025년 10월 지하철 승하차 분석")

# Convert date field
try:
    df['date'] = df['f'].astype(str).apply(lambda x: datetime.strptime(x, "%Y%m%d"))
except:
    st.error("날짜 형식 변환 오류: 'f' 컬럼을 확인하세요.")

# Filter to October 2025
df_oct = df[(df['date'].dt.year == 2025) & (df['date'].dt.month == 10)]

# Date selection
unique_dates = sorted(df_oct['date'].dt.strftime('%Y-%m-%d').unique())
selected_date = st.selectbox("📅 날짜 선택", unique_dates)

# Line selection
unique_lines = sorted(df_oct['노선명'].unique())
selected_line = st.selectbox("🚇 호선 선택", unique_lines)

# Filtered data
df_filtered = df_oct[
    (df_oct['date'].dt.strftime('%Y-%m-%d') == selected_date) &
    (df_oct['노선명'] == selected_line)
]

# Calculate total passengers
df_filtered['총이용객수'] = df_filtered['승차총승객수'] + df_filtered['하차총승객수']

# Sort by total passengers
df_sorted = df_filtered.sort_values(by="총이용객수", ascending=False)

st.subheader(f"📊 {selected_date} | {selected_line} 승하차 순위")
st.dataframe(df_sorted[['역명', '승차총승객수', '하차총승객수', '총이용객수']])

# Create bar colors
num_stations = len(df_sorted)
colors = []
for i in range(num_stations):
    if i == 0:
        colors.append('yellow')  # 1등 노란색
    else:
        fade = 0.9 + (i * 0.01)  # 순위 내려갈수록 점점 연하게
        fade = min(fade, 1.0)
        colors.append((fade, fade, 0.2))

# Plot graph
plt.figure(figsize=(10, 6))
plt.bar(df_sorted['역명'], df_sorted['총이용객수'], color=colors)
plt.title(f"{selected_date} {selected_line} 승하차 총이용객수 순위")
plt.xticks(rotation=45, ha='right')
st.pyplot(plt)
