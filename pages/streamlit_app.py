# streamlit_app.py (루트 폴더)
import streamlit as st

st.set_page_config(
    page_title="검사 데이터 분석 대시보드",
    page_icon="📈",
    layout="wide"
)

st.title("📊 키 그룹별 검사 인원 비율 분석")
st.write("👈 왼쪽 사이드바에서 **'Height Ratio'** 페이지를 선택하여 분석을 시작하세요.")
st.write("---")

st.markdown(
    """
    이 앱은 업로드하신 `cm.csv` 파일을 기반으로 **키 그룹별 검사 인원 비율**을 Plotly 막대 그래프로 시각화합니다.
    가장 많은 비율을 차지하는 그룹은 **빨간색**으로 강조됩니다.
    """
)
