import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib #모델 저장용
from service import main

MODEL_DIR  = "models"  #모델 저장 폴더
os.makedirs(MODEL_DIR, exist_ok=True)

def train_all_models_from_db(dataframe): #json을 pandas 변환 및 모든 데이터 학습 
    print(f"[{main.time_stamp()}] [Flask] Model training start...") 
    df  = pd.DataFrame(dataframe)
    df = df.rename(columns={
        "year" : "연도",
        "quarter" : "분기",
        "sector_name" : "업종",
        "sales_amount" : "매출액",
        "sales_count" : "건수",
    })
    models = {}
    
    categories = df["업종"].unique()
    print(f"[{main.time_stamp()}] [Flask] Total categories: {len(categories)}")

    #업종별로 반복
    for idx, category in enumerate(categories, start=1):
        print(f"[{main.time_stamp()}] [Flask] ({idx}/{len(categories)}) Training category: {category}")
        df_cat = df[df["업종"] == category].copy()
        if df_cat.empty:
            print(f"[{main.time_stamp()}] [Flask] Skip empty category: {category}")
            continue

        # 업종 단위 모델 학습
        model = train_model_for_category(df_cat)
        #모델 파일 저장
        save_model(model,category)

        #메모리에도 저장
        models[category] = model
    print(f"[{main.time_stamp()}] [Flask] Model training finish")
    return models

def train_model_for_category(df_cat: pd.DataFrame):
    #입력 
    X = df_cat[["연도","분기"]]
    #예측 대상
    y = df_cat[["매출액","건수"]]

    #70학습 30 테스트
    X_train, X_test, y_train, y_test = train_test_split(
        X,y, test_size=0.3, shuffle= False
    )

    # 선형 회귀 모델 생성
    model = LinearRegression()

    #모델 학습 수행
    model.fit(X_train,y_train)
    return model

#-----------학습된 모델을 로컬 파일로 저장-------
def save_model(model,category_name: str):
    path = os.path.join(MODEL_DIR,f"model_{category_name}.pkl")
    joblib.dump(model,path)


def load_model(category_name : str):
    path = os.path.join(MODEL_DIR, f"model_{category_name}.pkl")
    if not os.path.exists(path):
        return None
    return joblib.load(path)
#-----------------------------------------------


#특정 업종만 학습
def retrain_one_category(dataframe,category_name: str):
    df = pd.DataFrame(dataframe)
    df = df.rename(columns={
        "year" : "연도",
        "quarter" : "분기",
        "sector_name" : "업종",
        "sales_amount" : "매출액",
        "sales_count" : "건수",
    })
    #해당 업종 데이터만 필터링
    df_cat = df[df["업종"] == category_name].copy()

    #학습할 데이터가 없으면 중단
    if df_cat.empty:
        return None
    #재학습
    model = train_model_for_category(df_cat)
    #기존 모델 파일 덮어쓰기
    save_model(model, category_name)
    return model


def predict_for_one_input(year: int, quarter: int, category_name: str): #단일 예측
    #업종 모델 불러오기
    model = load_model(category_name)

    if model is None:
        return None #모델이 없으면
    
    #입력 데이터 구조
    X_new = pd.DataFrame(
        [[year, quarter]],
        columns=["연도","분기"]
    )

    #예측 수행
    y_pred = model.predict(X_new)
    #매출액,건수(0은 매출액, 1은 건수) 예 ( y_pred[0][0] = 매출액, y_pred[0][1] = 건수)
    return y_pred[0]