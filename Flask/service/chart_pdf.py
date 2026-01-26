from service import main
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.font_manager as fm
import os, json
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# Matplotlib 폰트 설정 (한글 깨짐 방지)
try:
    plt.rcParams['font.family'] = 'Malgun Gothic'
except:
    font_path = 'NanumGothic.ttf' 
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        plt.rcParams['font.family'] = 'NanumGothic'
    else:
        plt.rcParams['font.family'] = 'sans-serif' 
plt.rcParams['axes.unicode_minus'] = False

def to_py(v):
    if v is None:
        return None
    return int(v) if hasattr(v, "item") else v

def to_json_for_db(df):
    """
    Long Format DataFrame을 Spring Boot SeoulDTO 리스트 형태의 JSON으로 변환
    - DB의 컬럼명과 DTO의 필드명(sectorName, salesAmount, salesCount)에 맞춰 변환합니다.
    """
    
    # DTO 구조에 맞춰 컬럼명 변경 (SeoulDTO: sectorName, salesAmount, salesCount)
    df_db = df.rename(columns={
        "업종": "sectorName",
        "매출액": "salesAmount",
        "매출건수": "salesCount"
    })
    
    # 필요한 컬럼만 선택하여 DB 순서에 맞출 수 있습니다.
    df_db = df_db[['연도', '분기', 'sectorName', 'salesAmount', 'salesCount']]
    
    # JSON 형식으로 변환 (records: 리스트 안에 딕셔너리 형태)
    json_data = df_db.to_json(orient='records') 
    
    print(f"[{main.time_stamp()}] [Flask] Data converted to JSON for DB insertion.")
    return json_data

def to_chart_data(df):
    
    # 연도와 분기를 합쳐 분기_코드 생성
    df['분기_코드'] = df['연도'].astype(str) + '-Q' + df['분기'].astype(str)

    # (Index=분기_코드, Columns=업종, Values=매출액/매출건수)
    
    # --- 매출액 Pivot ---
    sales_pivot = pd.pivot_table(
        df,
        values='매출액',
        index='분기_코드',
        columns='업종',
        aggfunc='sum'      # 같은 분기에 데이터가 여러 개일 경우 합산
    ).fillna(0)            # NaN 값은 0으로 채움
    
    sales_pivot.columns = [f"{col}매출" for col in sales_pivot.columns]
    
    # --- 매출건수 Pivot ---
    count_pivot = pd.pivot_table(
        df,
        values='매출건수',
        index='분기_코드',
        columns='업종',
        aggfunc='sum'
    ).fillna(0)
    
    count_pivot.columns = [f"{col}건수" for col in count_pivot.columns]
    
    # 두 Pivot Table을 '분기_코드'를 기준으로 병합
    final_df = sales_pivot.merge(count_pivot, left_index=True, right_index=True, how='outer').fillna(0).reset_index()
    
    # 컬럼 순서 재정렬
    # 컬럼 리스트 생성
    sorted_cols = ['분기_코드']
    sectors = sorted(df['업종'].unique().tolist()) # 업종 순서대로 정렬
    
    for sector in sectors:
        sorted_cols.append(f"{sector}매출")
        sorted_cols.append(f"{sector}건수")
        
    final_df = final_df[sorted_cols]
    
    # Wide Format CSV로 저장
    final_df.to_csv("static/filter_csv/업종별_매출_건수_wide_format.csv", index=False, encoding="utf-8-sig")
    print(f"[{main.time_stamp()}] [Flask] Create Wide Format CSV File.")
    
    return final_df

def create_pyplot_chart(wide_df, chart_type='매출액', filename="sales_chart.png"):
    """
    plt
    """
    x_axis = wide_df['분기_코드']
    
    if chart_type == '매출액':
        cols_to_plot = [col for col in wide_df.columns if col.endswith('매출')]
        title = "분기별 업종별 매출액 변화 (Pyplot)"
        y_label = "매출액 (원)"
        
    else:   # 매출건수
        cols_to_plot = [col for col in wide_df.columns if col.endswith('건수')]
        title = "분기별 업종별 매출건수 변화 (Pyplot)"
        y_label = "매출건수 (건)"
        
    
    # 차트 그리기
    plt.figure(figsize=(15, 7))
    
    for col in cols_to_plot:
        label = col.replace('매출', '') if chart_type == '매출액' else col.replace('건수', '')
        plt.plot(x_axis, wide_df[col], marker='o', label=label)

    plt.title(title, fontsize=16)
    plt.xlabel("분기")
    plt.ylabel(y_label)
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(loc='best')
    plt.tight_layout()
    
    # 이미지 저장
    save_path = f"static/charts/{filename}"
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path)
    plt.close()
    
    print(f"[{main.time_stamp()}] [Flask] Pyplot Chart created and saved: {save_path}")
    return save_path

def to_chartjs_json(wide_df, chart_type='매출액', pred_df=None):
    """
    Chart.js
    """
    # numpy 타입 → python 기본 타입 변환
    def to_py(v):
        if v is None:
            return None
        return v.item() if hasattr(v, "item") else v

    labels = wide_df['분기_코드'].tolist()
    datasets = []

    if chart_type == '매출액':
        cols_to_plot = [col for col in wide_df.columns if col.endswith('매출')]
    else:
        cols_to_plot = [col for col in wide_df.columns if col.endswith('건수')]

    colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']

    # ===============================
    # 실제 데이터
    # ===============================
    for i, col in enumerate(cols_to_plot):
        color = colors[i % len(colors)]
        label = col.replace('매출', '').replace('건수', '')

        real_values = [to_py(v) for v in wide_df[col].tolist()]

        datasets.append({
            'label': label,
            'data': real_values,
            'borderColor': color,
            'backgroundColor': color + '40',
            'fill': False,
            'tension': 0.1
        })

    # ===============================
    # 예측 데이터
    # ===============================
    if pred_df is not None and not pred_df.empty:
        pred_labels = pred_df['분기_코드'].tolist()

        if chart_type == '매출액':
            pred_cols = [col for col in pred_df.columns if col.endswith('매출')]
        else:
            pred_cols = [col for col in pred_df.columns if col.endswith('건수')]

        for i, col in enumerate(pred_cols):
            color = colors[i % len(colors)]
            sector = col.replace('매출', '').replace('건수', '')

            last_real_value = to_py(wide_df[col].iloc[-1])
            pred_values = [to_py(v) for v in pred_df[col].tolist()]

            padded_data = (
                [None] * (len(labels) - 1)
                + [last_real_value]
                + pred_values
            )

            datasets.append({
                'label': f'{sector} (예측)',
                'data': padded_data,
                'borderColor': color,
                'borderDash': [6, 4],
                'pointRadius': 5,
                'fill': False,
                'tension': 0.1
            })

        # X축 확장
        labels = labels + pred_labels

    return {
        'labels': labels,
        'datasets': datasets
    }


def create_pdf(rows):
    # rows → DataFrame 변환 + 컬럼명 정리
    df = pd.DataFrame(rows)
    df = df.rename(columns={
        "year": "연도",
        "quarter": "분기",
        "sectorName": "업종",
        "salesAmount": "매출액",
        "salesCount": "매출건수"
    })

    # 연도 → 분기 기준 정렬
    df = df.sort_values(by=["연도", "분기"])

    # 기존 데이터의 마지막 연도 (예측 구분 기준)
    base_year = df["연도"].max()

    # 차트 생성을 위한 wide 형태 데이터
    wide_df = to_chart_data(df)

    # 매출액 / 매출건수 그래프 각각 생성
    sales_chart_path = create_pyplot_chart(
        wide_df, chart_type="매출액", filename="sales_amount.png"
    )
    count_chart_path = create_pyplot_chart(
        wide_df, chart_type="매출건수", filename="sales_count.png"
    )

    # PDF 기본 설정
    pdf_path = "static/report/예측_보고서.pdf"
    os.makedirs("static/report", exist_ok=True)

    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # 한글 폰트 등록
    pdfmetrics.registerFont(TTFont("Malgun", "C:/Windows/Fonts/malgun.ttf"))
    c.setFont("Malgun", 16)

    # 제목 + 생성일
    c.drawCentredString(width / 2, height - 40, "업종별 매출 분석 보고서")
    c.setFont("Malgun", 10)
    c.drawCentredString(
        width / 2, height - 60,
        f"생성일시: {main.time_stamp()}"
    )

    # 그래프 배치 (위: 매출액 / 아래: 매출건수)
    c.drawImage(sales_chart_path, 40, height - 330, width=520, height=220)
    c.drawImage(count_chart_path, 40, height - 580, width=520, height=220)

    # 리스트 출력 (연도 기준)
    start_y = height - 620
    line_height = 14
    current_year = None

    c.setFont("Malgun", 9)

    y = start_y - line_height

    for _, row in df.iterrows():

        # 연도 변경 시 연도 타이틀 출력
        if current_year != row["연도"]:
            current_year = row["연도"]

            y -= line_height
            c.setFont("Malgun", 10)

            # 예측 연도 여부 표시
            if current_year > 2024:
                year_title = f"─── {current_year}년 (예측) ───"
            else:
                year_title = f"─── {current_year}년 ───"

            c.drawString(40, y, year_title)

            y -= line_height
            c.setFont("Malgun", 9)
            c.drawString(40, y, "연도 | 분기 | 업종 | 매출액 | 매출건수")
            y -= line_height

        # 데이터 한 줄 출력
        c.drawString(
            40, y,
            f'{row["연도"]} | {row["분기"]} | {row["업종"]} | '
            f'{row["매출액"]:,} | {row["매출건수"]:,}'
        )
        y -= line_height

        # 페이지 하단 도달 시 새 페이지
        if y < 50:
            c.showPage()
            c.setFont("Malgun", 9)
            y = height - 50

    c.save()
    return pdf_path

