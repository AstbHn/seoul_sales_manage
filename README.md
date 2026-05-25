# 🍽️ 서울시 상권 분석 프로젝트 [음식점]

> RPA 자동화 기술을 활용하여 서울특별시 음식점 상권 데이터를 수집하고,  
> 매출 및 거래 건수를 분석·예측하는 통합 웹 시스템

---

## 📌 프로젝트 개요

방대한 공공데이터를 자동화와 머신러닝 예측 기술을 통해, 누구나 쉽게 음식점 매출을 예측하고 활용할 수 있는 시스템 구축을 목표로 합니다.

- **분기별 매출 흐름 및 예측 데이터를 차트로 시각화**하여 한눈에 확인
- **업종별 분석·예측 결과를 CSV/PDF 보고서로 저장** 가능

---

## 🛠️ 기술 스택

| 구분 | 기술 |
|------|------|
| **Language** | Java, Python |
| **Framework** | Spring Boot, Flask, Thymeleaf |
| **Database** | MySQL, MyBatis |
| **AI / ML** | Scikit-learn, Pandas |
| **Automation** | Brity RPA |
| **Frontend** | Chart.js, HTML, CSS, JavaScript |
| **Analytics** | Google Analytics |

---

## 🏗️ 시스템 아키텍처

```
[Brity RPA]
    │
    ├── 공공데이터 포털 자동 접속 → CSV 수집 (UTF-8 변환)
    └── Flask / Spring Boot 서버 자동 실행
         │
[Spring Boot] ──────────────────────── [Flask]
  - 프론트엔드 (Thymeleaf UI)            - 데이터 전처리 (Pandas)
  - 사용자 요청 라우팅                    - 머신러닝 예측 (Scikit-learn)
  - DB 연동 (MySQL / MyBatis)            - 보고서 생성 (CSV / PDF)
  - Flask API 연동                       - OCR 처리
         │
      [MySQL]
```

### 각 모듈 역할

| 폴더 | 역할 |
|------|------|
| `Spring_Boot/` | 프론트엔드(Thymeleaf) 및 사용자 요청 처리, Flask 연동 Controller |
| `Flask/` | 데이터 전처리, Scikit-learn 예측 모델, CSV/PDF 다운로드 API |
| `RPA/` | 공공데이터 자동 수집, 서버 자동 실행, 데이터 업데이트 자동화 시나리오 |

---

## ⚙️ RPA 자동화 시나리오

RPA는 다음 작업들을 자동으로 수행합니다.

**1. 데이터 수집 (`T_Get_Raw_CSV`)**
- 공공데이터 포털에 자동 접속하여 음식점 매출 CSV 다운로드
- CSV 인코딩을 UTF-8로 변환 후 지정 경로에 저장

**2. 서버 실행 (`T_Server_Boot`)**
- Flask 서버 선행 실행 → Spring Boot 서버 가동
- Spring Boot 시작 시 DB 상태 자동 점검 및 초기화

**3. 데이터 업데이트 (`T_Update_Main`)**

| 방식 | 설명 |
|------|------|
| OCR | 이미지 업로드 → 데이터 추출 → DB 저장 → 단일 재학습 |
| 직접 입력 | 사용자 입력값 → DB 업데이트 → 예측 모델 재학습 |
| CSV 업로드 | CSV 전처리(Flask) → 유효성 검사(Spring Boot) → DB 저장 |
| JSON 업로드 | JSON 전처리(Flask) → 유효성 검사(Spring Boot) → DB 저장 |

**4. 예측 및 보고서 생성 (`T_Predict_Main`, `T_Download_Files`)**
- 연도 / 분기 / 업종 입력 → Flask 예측 API 호출 → 결과 차트 시각화
- 예측 데이터를 CSV 및 PDF 파일로 다운로드

---

## 🚀 실행 방법

### 1. DB 설정

```sql
-- MySQL에서 데이터베이스 생성
CREATE DATABASE seoul_sales DEFAULT CHARACTER SET utf8mb4;
```

### 2. 서버 실행
Flask / Spring Boot 순서대로 서버를 실행시킵니다.
### 3. RPA 시나리오 실행

Brity RPA에서 시나리오를 순서대로 실행합니다.
1. `T_Get_Raw_CSV` — 원본 데이터 수집
2. `T_Server_Boot` — 서버 부팅 및 DB 초기화
3. `OPEN_PROJECT_PAGE` — 웹 서비스 접속 및 업데이트/예측 수행

---

## 👥 팀 구성

| 이름 | 역할 |
|------|------|
| 이형호 (팀장) | RPA 자동화 시나리오 설계, Spring Boot·Flask 연동, 시스템 전체 구조 설계 및 통합 관리 |
| 윤송현 | Spring Boot 프론트엔드 구현 (메인 화면, 차트 조회, 예측 결과 화면) |
| 이가은 | Scikit-learn 기반 매출 예측 모델 구현, 업종별 예측 로직 설계 |
| 최영현 | Chart.js 데이터 시각화, CSV·PDF 보고서 생성 및 다운로드 기능 구현 |

---

## 📁 프로젝트 구조

```
seoul_sales_manage/
├── Flask/          # Python Flask 백엔드 (예측 API, 전처리, 보고서)
├── Spring_Boot/    # Java Spring Boot 서버 (UI, 라우팅, DB 연동)
└── RPA/            # Brity RPA 자동화 시나리오
```

---

## 📊 주요 기능 요약

- ✅ RPA를 통한 공공데이터 **자동 수집 및 적재**
- ✅ Scikit-learn 기반 **업종별 매출 예측**
- ✅ Chart.js를 활용한 **분기별 매출 추이 시각화**
- ✅ OCR / 직접 입력 / CSV / JSON을 통한 **다양한 데이터 업데이트 방식**
- ✅ 예측 결과 **CSV · PDF 보고서 자동 생성 및 다운로드**
- ✅ Google Analytics 기반 **사용자 행동 분석**

---
