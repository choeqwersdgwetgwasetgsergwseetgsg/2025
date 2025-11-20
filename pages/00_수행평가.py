# pages/00_수행 키.py (pages 폴더)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# --- 데이터 로드 함수 (CP949 인코딩 및 분리 문자 수정 반영) ---
@st.cache_data
def load_data():
    """루트 폴더에서 'cm.csv' 파일을 로드하고 '구분' 컬럼을 인덱스로 정리합니다."""
    csv_path = Path("cm.csv")
    
    if not csv_path.exists():
        st.error(f"⚠️ 데이터 파일을 찾을 수 없습니다: {csv_path.name}")
        st.stop()
    
    try:
        # 1. 파일 로드: 인코딩 및 공백 포함 분리 문자(sep='\s*,\s*') 처리
        df = pd.read_csv(
            csv_path, 
            # 쉼표 앞뒤의 공백을 모두 분리 문자로 인식
            sep='\s*,\s*', 
            encoding='cp949', # 인코딩 오류 해결
            engine='python' # 정규 표현식 sep 사용을 위해 필요
        )
        
        # 2. 컬럼 이름 앞뒤의 불필요한 공백 제거
        df.columns = df.columns.str.strip() 

        # 3. '구분' 컬럼을 인덱스로 설정하고 공백 제거
        df = df.set_index('구분')
        df.index = df.index.str.strip()
        
        # 4. '검사인원' 컬럼만 추출 및 데이터 타입 정리
        df = df[['검사인원']].copy()
        df['검사인원'] = pd.to_numeric(df['검사인원'], errors='coerce').fillna(0).astype(int)
        
        return df
    except Exception as e:
        # 디버깅을 위해 상세 오류 출력
        st.error(f"데이터 로드 및 처리 중 치명적인 오류가 발생했습니다: {e}")
        st.info("CSV 파일의 인코딩(cp949 또는 euc-kr) 및 헤더에 '구분', '검사인원'이 포함되어 있는지 확인해주세요.")
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
    
    # 색상 설정: 1위는 빨간색, 나머지는 파란색 계열 그라데이션
    colors = []
    n_groups = len(df_sorted)
    colors.append('red') 
    
    n_others = n_groups - 1
    for i in range(1, n_groups):
        if n_others > 0:
            lightness_ratio = i / n_others
        else:
            lightness_ratio = 0
            
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
            'text': '**2024 신채검사 키 비율 막대그래프**',
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
        st.warning("데이터의 총 인원수가 0이거나 데이터가 비어있어 그래프를 그릴 수 없습니다.")
        return

    st.subheader(f"총 검사 인원: **{total_pop:,}명**")
    
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
