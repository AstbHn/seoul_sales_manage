from PIL import Image
from datetime import datetime
import pytesseract, os, re, glob, pandas as pd

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"

def time_stamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def set_csv():
    """ CSV 전처리 과정"""
    
    use_cols = ["기준_년분기_코드", 
                "서비스_업종_코드_명", 
                "당월_매출_건수", 
                "당월_매출_금액"]
    
    target_sectors = ["한식음식점", 
                      "일식음식점",
                      "양식음식점",
                      "중식음식점",
                      "패스트푸드점"]
    
    raw_csv_paths = sorted(glob.glob("static/raw_csv/*.csv"))
    print(f"[{time_stamp()}] [Flask] found CSV Path")
    frames = []
    
    for path in raw_csv_paths:
        df = pd.read_csv(path, usecols=use_cols)
        
        #연도와 분기 분할
        df["연도"] = df[use_cols[0]].astype(str).str[:4].astype(int)
        df["분기"] = df[use_cols[0]].astype(str).str[-1].astype(int)
        
        df = df[df[use_cols[1]].isin(target_sectors)]
        
        df = df.rename(columns={
                                    use_cols[1]: "업종",
                                    use_cols[2]: "매출건수",
                                    use_cols[3]: "매출액"
                                })
        #기준 년분기 코드 삭제
        df = df.drop(columns="기준_년분기_코드")
        
        frames.append(df)
    print(f"[{time_stamp()}] [Flask] Preprocessing finish")
    
    #전처리한 데이터 프레임을 하나의 데이터프레임으로 변환
    df = pd.concat(frames, ignore_index=True)
    
    #"연도", "분기", "업종" 별로 매출액,건수 합산
    df = (
    df
    .groupby(["연도", "분기", "업종"], as_index=False)
    .agg({
        "매출건수": "sum",
        "매출액": "sum"
    })
    )
    
    df.to_csv("static/filter_csv/업종별_매출_건수.csv", 
              index=False, 
              encoding="utf-8-sig")
    
    print(f"[{time_stamp()}] [Flask] Create CSV File [업종별_매출_건수.csv] route : static/filter_csv ")
    return df

def preprocess(df):
    target_sectors = [
        "한식음식점",
        "일식음식점",
        "양식음식점",
        "중식음식점",
        "패스트푸드점"
    ]

    df = df[df["서비스_업종_코드_명"].isin(target_sectors)]

    df["연도"] = df["기준_년분기_코드"].astype(str).str[:4].astype(int)
    df["분기"] = df["기준_년분기_코드"].astype(str).str[-1].astype(int)

    df = df.rename(columns={
        "서비스_업종_코드_명": "업종",
        "당월_매출_건수": "매출건수",
        "당월_매출_금액": "매출액"
    })

    df = df.groupby(["연도", "분기", "업종"], as_index=False).agg({
        "매출건수": "sum",
        "매출액": "sum"
    })

    return df


def ocr_reader(img_path):
    img = Image.open(img_path)
    custom_config = r'-c tessedit_char_blacklist="=~--" --oem 3 --psm 6'
    text_raw = pytesseract.image_to_string(img,lang="kor", config=custom_config)
    clean_lines =[]
    for line in text_raw.split("\n"):
        s=line.strip()
        if not s:
            continue
        if re.fullmatch(r"[-=*_]{3,}",s):
            continue
        special_cnt = len(re.sub(r"[A-Za-z0-9가-힣]","",s))
        if special_cnt >=len(s) *0.6: #특수문자가 60프로 이상 시 제거
            continue
        s = s.replace("—", "-") # 하이픈 조정
        s = s.strip().replace(" ", "") # 공백 제거
        print("[OCR CLEAN] >", s)
        clean_lines.append(s)
    return clean_lines

