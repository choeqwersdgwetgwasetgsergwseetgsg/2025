# pages/00_수행 키.py (pages 폴더)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# --- 데이터 로드 함수 (CP949 인코딩 적용) ---
@st.cache_data
def load_data():
    """루트 폴더에서 'cm.csv' 파일을 로드하고 '구분' 컬럼을 인덱스로 정리합니다."""
    csv_path = Path("cm.csv")
    
    if not csv_path.exists():
        st.error(f"⚠️ 데이터 파일을 찾을 수 없습니다: {csv_path.name}")
        st.stop()
    
    try:
        # CP949 인코딩을 사용하여 한국어 CSV 파일을 안전하게 로드합니다.
        df = pd.read_csv(
            csv_path, 
            sep=',', 
            encoding='cp949', # <--- 인코딩 오류 해결을 위해 'cp949' 적용
            skipinitialspace=True
        )
        
        # '구분' 컬럼을 인덱스로 설정하고 공백 제거
        df = df.set_index('구분')
        df.index = df.index.str.strip()
        
        # '검사인원' 컬럼만 사용
        df = df[['검사인원']].copy()
        
        # '검사인원'을 정수형으로 변환 (변환 불가능한 값은 0으로 처리)
        df['검사인원'] = pd.to_numeric(df['검사인원'], errors='coerce').fillna(0).astype(int)
        
        return df
    except Exception as e:
        st.error(f"데이터 로드 및 처리 중 오류가 발생했습니다. 인코딩 또는 파일 형식을 확인해주세요: {e}")
        st.stop()

# --- Plotly 그래프 생성 함수 ---
def create_height_ratio_bar_chart(df):
    """
    키 그룹별 인원 비율 막대 그래프를 생성합니다.
    1위는 빨간색, 나머지는 그라데이션으로 표시합니다.
    """
    df_sorted = df.sort_values(by='검사인원', ascending=False)
    total_population = df_sorted['검사인원'].sum()
    
    if total_population == 0:
        return None, 0

    df_sorted['Ratio'] = (df_sorted['검사인원'] / total_population) * 100
    
    # 1위는 빨간색, 나머지는 파란색 계열 그라데이션
    colors = []
    n_groups = len(df_sorted)
    colors.append('red') 
    
    n_others = n_groups - 1
    for i in range(1, n_groups):
        if n_others > 0:
            lightness_ratio = i / n_others
        else:
            lightness_ratio = 0
            
        # Lightness: 비율이 낮을수록 (i가 클수록) 밝은 색 (50% -> 90%)
        lightness = 50 + (40 * lightness_ratio)
        color = f'hsl(240, 70%, {lightness:.1f}%)'
        colors.append(color)

    fig = go.Figure(data=[
        go.Bar(
            x=df_sorted.index,
            y=df_sorted['Ratio'],
            marker_color=colors,
            text=df_sorted['Ratio'].apply(lambda x: f'{x:.1f}%'),
            textposition='outside'
        )
    ])

    fig.update_layout(
        title={
            'text': '**키 그룹별 검사 인원 비율**',
            'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'
        },
        xaxis_title="키 그룹 ('구분')",
        yaxis_title="비율 (%)",
        yaxis_range=[0, df_sorted['Ratio'].max() * 1.15],
        template='plotly_white'
    )
    
    return fig, total_population

# --- Streamlit 앱 본문 ---
def main():
    st.title("📈 키 그룹별 인원 비율 시각화")
    st.markdown("---")

    df_raw = load_data()
    
    if df_raw is None:
        return

    # 그래프 생성 및 표시
    fig, total_pop = create_height_ratio_bar_chart(df_raw)
    
    if fig is None:
        st.warning("데이터의 총 인원수가 0이어서 그래프를 그릴 수 없습니다.")
        return

    st.subheader(f"총 검사 인원: **{total_pop:,}명**")
    
    # Plotly 그래프 표시
    st.plotly_chart(fig, use_container_width=True) 

    # 요약 테이블
    st.subheader("비율 상세 정보")
    
    df_summary = df_raw[df_raw['검사인원'] > 0].copy()
    total_population = df_summary['검사인원'].sum()
    df_summary['비율 (%)'] = (df_summary['검사인원'] / total_population) * 100
    
    df_summary = df_summary.sort_values(by='검사인원', ascending=False)
    
    st.dataframe(
        df_summary.rename(
            columns={'검사인원': '검사 인원'}
        )[['검사 인원', '비율 (%)']].style.format({"비율 (%)": "{:.2f}%"}),
        use_container_width=True
    )

if __name__ == "__main__":
    main()
