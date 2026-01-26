from flask import Flask,request,jsonify,send_file,redirect
from service import main, models as mod, chart_pdf as cp
import os,requests
from service.errors import register_error_handlers

app = Flask(__name__)
register_error_handlers(app)

@app.route("/init_program")
def init_program():
    """ 스프링 부트 서버 부팅시 csv 전처리 """
    
    filter_csv = main.set_csv()
    return (filter_csv.to_dict(orient="records"))

@app.route("/read_csv", methods=["POST"])
def read_csv():
    """ CSV 처리 """
    
    file = request.files["file"]
    
    df = main.pd.read_csv(file)
    df = main.preprocess(df)
    
    return df.to_dict(orient="records")

@app.route("/read_json", methods=["POST"])
def read_json():
    """ Json 파일 처리 """
    
    file = request.files["file"]
       
    df = main.pd.read_json(file)
    df = main.preprocess(df)
    
    return df.to_dict(orient="records")

@app.route("/image_reader",methods = ["POST"])
def image_reader():
    """ OCR 읽기 """
    
    img = request.files["img"]  
    
    info = main.ocr_reader(img)
    
    payload = {
        "lines": info
    }
    res = requests.post(
        "http://localhost:8765/ocr_result",
        json=payload
    )

    return redirect("http://localhost:8765/viewpage")

@app.route("/sklearn_run", methods= ["POST"])
def sklearn_run():
    """모델 전체 학습"""
    
    #spring 에서 json 받기 
    df_json = request.json
    
    mod.train_all_models_from_db(df_json) #json 에서 pandas 변환
    
    return "전체 모델 학습 완료",200

@app.route("/sklearn_run_single", methods= ["POST"])
def sklearn_run_single():
    """ 모델 단일 항목 학습 """

    df_json = request.json
    category_name = request.args.get("category_name")
    model = mod.retrain_one_category(df_json,category_name)

    return  f"{category_name} 업종 모델 재학습 완료", 200

@app.route("/sklearn_predict", methods= ["POST"])
def sklearn_predict():
    """가추어진 모델을 이용해서 에측값 반환"""
    
    payload = request.json
    
    try:
        year = int(payload["year"]) 
        quarter = int(payload["quarter"])
        category_name = payload["sector_name"]
    except(KeyError, TypeError,ValueError):
        return "year, quarter,sector_name 필드가 필요",400
    
    y_pred = mod.predict_for_one_input(year,quarter,category_name)

    if y_pred is None:
        return f"{category_name} 업종 모델이 없습니다 학습을 수행해주세요",400
    
    # 예측한 값 json 으로 넘김
    return jsonify({
        "year" : year,
        "quarter": quarter,
        "sector_name": category_name,
        "pred_sales_amount": float(y_pred[0]),
        "pred_sales_count": float(y_pred[1]),
    })

# --- 파일 다운로드 엔드포인트 ---
@app.route('/download-csv', methods=['GET'])
def download_csv():
    """ 
    전처리된 CSV 파일을 다운로드합니다.
    """
    
    # 파일 경로 설정
    csv_path = "static/filter_csv/업종별_매출_건수_wide_format.csv"
    
    if not os.path.exists(csv_path):
        print(f"[{main.time_stamp()}] [Flask] Error: CSV file not found at {csv_path}")
        return "Error: CSV file not found. Please run the preprocessing step first.", 404
    
    try:
        print(f"[{main.time_stamp()}] [Flask] Starting CSV file download: {csv_path}")
        return send_file(
            csv_path,
            mimetype='text/csv',
            as_attachment=True,
            download_name="업종별_매출_데이터.csv"
        )
    except Exception as e:
        print(f"[{main.time_stamp()}] [Flask] CSV download error: {e}")
        return "An error occurred during CSV download.", 500

@app.route("/create_pdf",methods = ["POST"])
def create_pdf():
    """ PDF파일 생성 """
    
    payload = request.json
    rows = payload["rows"]
    cp.create_pdf(rows)
    return "PDF 생성 완료", 200

@app.route('/download-pdf', methods=['GET'])
def download_pdf():
    """
    보고서 PDF 파일을 다운로드합니다.
    """
    pdf_path = "static/report/예측_보고서.pdf"
    
    # PDF 파일 생성 로직
    if not os.path.exists(pdf_path):
        print(f"[{main.time_stamp()}] [Flask] Error: PDF file not found at {pdf_path}")
        return "Error: PDF report file not found. Generation required.", 404
        
    try:
        # send_file 함수를 사용하여 파일 전송
        print(f"[{main.time_stamp()}] [Flask] Starting PDF file download: {pdf_path}")
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name="업종별_매출_분석_보고서.pdf"
        )
    except Exception as e:
        print(f"[{main.time_stamp()}] [Flask] PDF download error: {e}")
        return "An error occurred during PDF download.", 500

@app.route("/chart_data", methods=["POST"])
def chart_data():
    payload = request.json
    rows = payload.get("rows")
    pred_rows = payload.get("pred_rows")
    
    df = main.pd.DataFrame(rows)

    df = df.rename(columns={
        "year": "연도",
        "quarter": "분기",
        "sectorName": "업종",
        "salesAmount": "매출액",
        "salesCount": "매출건수"
    })

    wide_df = cp.to_chart_data(df)
    pred_df = None
    if pred_rows:
        pred_df = main.pd.DataFrame(pred_rows)
        pred_df = pred_df.rename(columns={
            "year": "연도",
            "quarter": "분기",
            "sectorName": "업종",
            "salesAmount": "매출액",
            "salesCount": "매출건수"
        })
        pred_df = cp.to_chart_data(pred_df)
        
    sales_chart = cp.to_chartjs_json(wide_df, "매출액", pred_df)
    count_chart = cp.to_chartjs_json(wide_df, "매출건수", pred_df)

    return jsonify({
        "sales": sales_chart,
        "count": count_chart
    })


if __name__ == "__main__":
    print(f"[{main.time_stamp()}] Serving Flask port: 5678")
    app.run(debug=True,port=5678)#포트번호 5678