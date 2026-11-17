"""
PASCUCCI Consumer Intelligence Dashboard
Consumer Data-driven Marketing for PASCUCCI

═══════════════════════════════════════════════════════════
버전 이력 (Version History)
※ 화면의 버전·날짜 표기는 아래 첫 항목에서 자동으로 읽습니다(새 버전은 맨 위에 추가).
───────────────────────────────────────────────────────────
v2.7.0(beta) (2026-11-17)
  [브랜드] 비교군에 더벤티 추가(커피전문점 12개). 브랜드 판정을 크롤러 v3.2 규칙과 통일
           (MGC커피·'메가 아아' 문맥, '빽' 패턴·'빽빽' 제외, 오탐 가드).
  [보정] 수집 한계로 생기는 수치 왜곡 보정
         ① 언급량·SOV: 블로그는 6개월 환산치(sov_summary)로 교체, 커뮤니티는 실측.
            보정 정보가 없으면 화면에 '보정 전 수치'로 표시.
         ② 추이 분석(월별 NSS·언급 추이·Burst·트렌드·프로모션 급증·제품 추이): 검색 상한으로
            기간 전체를 덮지 못한 검색어 글과 수집 당일(부분) 글을 제외, 월별 값은 30일 환산.
         ③ 반복 샘플링(-sampler) 행은 SOV 환산에만 쓰고 분석 데이터에서 제외.
         ④ 데이터 자동 선택을 voc_master 파일로 한정(sov_summary 등 오인 방지).
  [수정] 캐시 오류: 소스·품질 필터와 브랜드 선택을 바꿔도 지표가 갱신되지 않던 문제 해결.
         작동하지 않던 사이드바 감성 필터 제거, 브랜드 필터는 화면 표시 범위로 연결.
         Parquet·xz 데이터에서 트렌드 탭이 비던 문제 해결.
  [자동화] 버전 표기와 탭 해설 박스(NSS·SOV·Burst·PMI·소비맥락·로열티·토픽)를 데이터로 생성.
           LDA 토픽 이름을 키워드로 자동 명명, 포지셔닝 레이더를 실측 지표로 계산.
  [성능] 토픽·고객군집 모델을 고정 시드 표본으로 학습한 뒤 전체 문서를 분류(비중·건수는 전체 기준).
         무거운 모델(LDA·토픽 클러스터·고객 클러스터링)은 해당 탭을 열 때 계산 → 첫 화면 로딩 단축.
         LDA '전체' 화면에서 같은 모델을 두 번 학습하던 문제 수정, 세그먼트 산점도는 4,000점만 표시,
         캐시에 미사용 문서 사본을 남기지 않도록 정리.
v2.6.15(beta) (2026-07-14)
  [핫픽스] 79K 데이터 전환 후 Community Cloud OOM(healthz reset) 대응 — 메모리 다이어트
         ① tokens 리스트 컬럼 제거: 사용처 10곳을 tokens_str.str.cat(sep=" ").split()으로
            동등 치환(검증 완료). 파이썬 리스트 객체 오버헤드 제거.
         ② 전처리 말미 무거운 미사용 컬럼 drop: comments_json·comment_text·is_rel·
            matched_keywords·sponsor_signals·co_mention_brands·matched_L2~L4.
         ③ 원본 df 명시 해제(del+gc). 피크 메모리 1.09GB → 0.67GB (-39%).
v2.6.14(beta) (2026-07-14)
  [기능] Parquet 데이터 포맷 지원 — GitHub 25MB 한도 대응 배포 포맷 전환
         DATA_FILE_GLOBS에 *.parquet/*.xz 추가(자동 탐색), load_and_preprocess에
         read_parquet 분기 추가. csv/gz/xz는 compression='infer'로 단순화.
         requirements.txt에 pyarrow 추가 필요.
v2.6.13(beta) (2026-07-01)
  [핫픽스] 프로덕션 'Oh No'(OOM) 재발 수정 — 리스트 컬럼 해싱 메모리 폭주 2차 차단
         원인: @st.cache_data 함수 `_tag_source_quality(v)`가 언더스코어 없는 df 인자로 받아,
         매 rerun 길목(v=_tag_source_quality(v))에서 brands/tokens 리스트 컬럼 해싱 실패 →
         5만행 df 통째 pickle 폴백 반복 → Community Cloud 메모리 초과 → 헬스체크 붕괴.
         (v2.6.9에서 트렌드 4함수는 _corpus로 고쳤으나 이 함수가 누락. 4,390→50,221건에서 치명화)
         해결: `_tag_source_quality(_v, sig)` + 호출부 sig 전달(len×cols)로 해싱 스킵.
         데드코드 compute_fnb_trends(v_adj)도 동일 패턴 위생 수정(_v_adj, sig).
v2.6.9(beta) (2026-06-24)
  [기능] 트렌드 조기경보 '완전 통합' — 옛 상품 트렌드 엔진(compute_trend_earlywarning)을 단일 ES 엔진으로 흡수
         기준선·카테고리 필터(전체/커피·음료/푸드류/식재료)·조기경보 신호 카드(성장조짐/안정/둔화)를 통합 데이터로 구동
         이제 커피와 푸드·식재료가 한 화면·한 엔진에서 분석됨(중복 섹션 제거)
v2.6.8(beta) (2026-06-24)
  [기능] 트렌드 조기경보 통합 재설계 1단계 — 단일 ES 엔진(커피·음료+푸드+식재료 동일 메뉴단위)
         ES 포지셔닝 버블맵(성장×평판) + 카테고리 트리맵(면적=볼륨,색=NSS) + 볼륨변화 기여도 워터폴
         + 상위 ES 월별추이 + 키워드 원문 드릴다운. (페어링 네트워크·미등록 급상승어·원문 정밀화는 2단계)
v2.6.7(beta) (2026-06-24)
  [기능] 통합 트렌드 섹션에 원문 보기 전면 보강 — ①키워드 드릴다운(급상승 키워드 선택→긍/부정 실제 원문)
         ②카테고리별 긍/부정 대표 원문 복원. '지표 시그널의 왜'를 원문으로 납득.
v2.6.6(beta) (2026-06-24)
  [기능] 트렌드 조기경보를 '통합 시장 트렌드'로 재설계 — 커피 코어 + 인접 식음료 VoC 통합 분석
         뜨는 커피·음료 / 뜨는 푸드·식재료 / 카테고리 평판 / 페어링·변형(조합) 시그널. 브랜드 지표 미반영 유지.
v2.6.5(beta) (2026-06-24)
  [기능] 트렌드 조기경보 탭 확장 — '식음료 인접 트렌드 조기경보'(커피 외 디저트·베이커리·카페푸드·식재료 VoC)
         별도 레이어로 분리(브랜드 NSS·SOV 미반영). 급상승 키워드 레이더·카테고리 볼륨/감성·대표 원문.
v2.6.4(beta) (2026-06-23)
  [기능] 2단계 데이터 필터 — ①소스(블로그/커뮤니티) ②콘텐츠 품질(VoC만/홍보·보도성만) + 소스별 특성 비교
         선택한 렌즈로 모든 분석 범위 재설정. 블로그 혜택·홍보성/보도 글 휴리스틱 태깅(_src/_ctype)
v2.6.3(beta) (2026-06-23)
  [기능] 데이터 로딩에 gzip(.csv.gz/.gz) 지원 추가, 최신 파일 선택을 파일명 날짜(YYYYMMDD) 우선으로 robust화
         (+news_master 파일은 메인 데이터 후보에서 제외)
v2.6.2(beta) (2026-06-22)
  [보안] 접근 제한 — 공유 비밀번호 관문(옵션 C). Secrets의 app_password로 사업부 전용 접근, 세션당 1회 입력 후 통과. 미설정 시 경고 후 개방.
v2.6.1(beta) (2026-06-21)
  [수정] 리포트 차트 누락 해결 — matplotlib 부재 시 네이티브 PPT 차트로 폴백(빈자리 방지)
  [기능] DOCX 리포트도 PPTX 동일 스킴(Exec Summary·5챕터·결과/의미/함의/시나리오)으로 재작성, 메뉴 '(개발 중)' 제거
  [기능] 원두선물·환율 우측 그래프 원/달러(USD)→원/유로(EUR)로 변경
v2.6.0(beta) (2026-06-21)
  [기능] 분석 리포트 전면 재설계 — 사전저작 코멘트(report_commentary.json) 기반 컨설팅형 리포트
         표지·Executive Summary·5개 챕터(결과·의미·함의·시나리오)·마지막 장 / 차트 이미지화 / 지문 동기화 가드
v2.5.7(beta) (2026-06-21)
  [수정] 리포트 템플릿 탐색 강화(대소문자·하위폴더·철자 무시 재귀) + 미발견 시 진단 슬라이드
v2.5.6(beta) (2026-06-20)
  [기능] 분석 리포트 PPTX를 브랜드 템플릿(insight_report_templete.pptx) 기반으로 전면 개편
         (표지 분석주제 자동작성·본문 데이터·마지막 장 고정 / 맑은 고딕, 챕터10·헤드라인18·본문12·차트9pt)
v2.5.5(beta) (2026-06-20)
  [기능] 분석 리포트(PPTX/DOCX)에 '2025 서울시민 먹거리조사' 외부 근거 자동 인용 연동
         (reference/seoul_food_survey_ref.json 로더 + 섹션→토픽 매핑 + 코멘트 삽입)
v2.5.4(beta) (2026-06-16)
  [디자인] 분석영역 버튼 텍스트 볼드 강제, 하위 분석탭 활성색 옅은 블루로(텍스트 가독성),
           소비자 VoC·분석 리포트 다운로드에 '(개발 중)' 표기
v2.5.3(beta) (2026-06-16)
  [디자인] 카테고리 설명 풋노트화·버튼 텍스트 확대/볼드, 활성 카테고리 버튼 옅은 블루,
           세부 분석탭 확대·볼드, PASCUCCI Brand Status 명칭, 메인 최상단 타이틀
  [기능] 원두선물·환율 명칭 정리, 포지셔닝맵 사분면 직관화, 사이드바 업로더 제거
v2.5.2(beta) (2026-06-16)
  [디자인] 분석영역 대형 카테고리 버튼 UI, 카테고리 설명문 개편, 파스쿠찌 중심화,
           페르소나 가독성(상세보기 통합·이모지·키워드 정제), 브랜드 이미지맵 명칭
  [기능] 프로모션/CA맵 원문·키워드 매칭 정확도 개선, CA맵 축 재점검·파스쿠찌 강조
v2.5.1(beta) (2026-06-15)
  [버그] 로열티 차트 파스쿠찌 막대 누적(중복행) 수정, 드라이버 원문 매칭 정확도 개선
         (속성 문장 스니펫 추출 + 감성어 동반 조건 + 관련도 정렬)
  [디자인] 사이드바 버튼 한글화(컨슈머 인텔리전스 대시보드)
v2.4.2 (2026-06-15)
  [견고성] 데이터 자동탐색에 data/(점없음)·리포 루트 추가, 미발견 시 탐색경로 안내,
           로딩 오류를 화면에 명시(Streamlit Cloud 자가진단)
v2.4.1 (2026-06-15)
  [기능] 데이터/.data·뉴스/.news GitHub 폴더 자동 로딩(최신 파일), 키워드 버블 가독성,
         원두가격·환율 풋노트, 뉴스룸 유형별 대표기사 정리, 드라이버 원문·MD/굿즈,
         프로모션 브랜드별 시계열, 페르소나 Pain-point·Key Buying Factor
v2.3.6 (2026-06-13)
  [기능] PAS 뉴스룸 브리핑 보강 — 날짜·브랜드·유형별 이모지 건수 통계 + 요약(G칼럼) 기반 종합 브리핑 기사 분리
v2.3.5 (2026-06-13)
  [기능] 원두·환율: 원화환산 가격 삭제·외부시세 버튼 복원, PAS 뉴스룸(명칭)·오늘의 뉴스 브리핑(1000자 요약)
v2.3.4 (2026-06-13)
  [기능] 소비맥락+세분화 화면 통합, 포지셔닝 레이더에 파스쿠찌(굵은 라인) 추가,
         페르소나 네이밍 실무형·크리에이티브 개편, 분석 리포트 PPT(시사점·Lessons 포함)
  [디자인] CID 버튼 분리·업로드 상단 이동, 시작화면 안내문구 삭제, 원두·환율 모니터링 명칭
v2.3.3 (2026-06-13)
  [기능] News Monitoring 자동 연동 — 최신 news_master_*.csv 자동 탐색·표시(필터·키워드·링크)
v2.3.2 (2026-06-13)
  [디버그] 토픽 카드 IndexError(cluster_colors) 수정, 토픽 클러스터링 제목 중복 제거,
           PPTX 미설치 안내 개선, 원자재 폴백 출처 설명 추가, News Monitoring 명칭,
           CID 버튼 명칭변경·리포트 상단 이동
v2.3.1 (2026-06-12)
  [디자인] 사이드바 타이틀 확대·부제 삭제, 분석 리포트로 명칭변경·위치이동, MI 버튼
  [기능] TARGET_BRANDS 파스쿠찌 포함(전 기능), Market Intelligence 모듈(원자재·환율·뉴스),
         소비자 VoC 모니터링(TBD), 분석 리포트 PPT·시장맥락 고도화
  [프로모션] 페이행사 추가, 최근 급증 프로모션·브랜드 cross 체크
  [LDA] 토픽 클러스터링 merge, 토픽 6~8개 세분화
  [고객] 페르소나 8~10개, 모듈화·라이프스타일·인접 브랜드 표시
  [키워드] 시그니처·트렌디(두쫀쿠·우베 등) 보강
v2.1.2 (2026-06-05)
  [디자인] 사이드바 버전·Copyright 표기, 필터 무채색, 푸터 Copyright
  [키워드] 디저트(아이스크림·젤라또), 프로모션(기프티콘·모바일상품권·MD) 보강
  [텍스트마이닝] 리스크탐지 브랜드 필터 정합성 수정, 무의미 부사·수식어
                  분석 집계 제외(불용어 확장)
  [기능] NSS 시사점 다각화, 찐팬지수 설명·해설 보강, 분석결과 docx 다운로드,
         촉진 반응강도 지표화 + 최근 프로모션·브랜드, 촉진활동 세부·원문 확인
v2.1.1 (이전) 19개 탭, 4대 고도화 분석
═══════════════════════════════════════════════════════════

데이터: 네이버 블로그 + 82Cook·클리앙·디시인사이드·네이트판 커뮤니티 VoC
       (data/ 폴더의 최신 voc_master 파일 + 같은 시각의 sov_summary 파일을 자동 인식)

실행 방법 (로컬):
  py -3.11 -m pip install -r requirements.txt
  py -3.11 -m streamlit run PAS_DASHBOARD_v270.py
"""

COPYRIGHT = "Copyright 2026 PAS DIVISION Paris Croissant Co., Ltd. All Rights Reserved"

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import json
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import scipy.linalg as la
import scipy.sparse as sp
import io
import os
import glob
try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
try:
    import pptx as _pptx_check  # noqa: F401
    PPTX_AVAILABLE = True
except ImportError:
    PPTX_AVAILABLE = False


# ══════════════════════════════════════════════════════
# [v2.7.0] 버전 표기 — 상단 '버전 이력'의 첫 항목에서 자동으로 읽음
#   새 버전을 이력 맨 위에 적기만 하면 사이드바 표기가 함께 바뀐다.
# ══════════════════════════════════════════════════════
def _version_from_changelog():
    txt = globals().get("__doc__") or ""
    if not txt:
        try:
            with open(__file__, encoding="utf-8") as _f:
                txt = _f.read(8000)
        except Exception:
            txt = ""
    m = re.search(r"^\s*(v\d+\.\d+\.\d+(?:\([^)]*\))?)\s*\((\d{4}-\d{2}-\d{2})\)", txt, re.M)
    return (m.group(1), m.group(2)) if m else ("v?", "")


APP_VERSION, APP_DATE = _version_from_changelog()

# ══════════════════════════════════════════════════════
# 기본 설정
# ══════════════════════════════════════════════════════
st.set_page_config(
    page_title="PASCUCCI Consumer Intelligence Dashboard",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp { background-color: #F7F9FC; }
    .main .block-container { background-color: #F7F9FC; padding-top: 1.5rem; max-width: 1400px; }

    [data-testid="stSidebar"] { background-color: #EDF1F5 !important; border-right: 2px solid #CBD5E0; }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div { color: #2D3748 !important; }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: #1B2A4A !important; font-size: 1rem; font-weight: 700; }
    [data-testid="stSidebar"] hr { border-color: #CBD5E0; }
    [data-testid="stSidebar"] .stMarkdown { color: #2D3748 !important; }

    .stTabs [data-baseweb="tab-list"] {
        background-color: #FFFFFF; border-radius: 10px; padding: 4px 6px;
        gap: 2px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); border: 1px solid #E2E8F0;
    }
    .stTabs [data-baseweb="tab"] {
        color: #4A5568; font-size: 13px; font-weight: 600;
        border-radius: 7px; padding: 7px 14px; background: transparent;
    }
    .stTabs [aria-selected="true"] { background-color: #DCE9F7 !important; color: #1B2A4A !important; }
    .stTabs [aria-selected="true"] p { color: #1B2A4A !important; }

    h1, h2, h3, h4 { color: #1B2A4A !important; }
    p, li { color: #2D3748; }

    .kpi-card {
        background: #FFFFFF; border: 1px solid #E2E8F0;
        border-top: 4px solid #2D6BC4; border-radius: 10px;
        padding: 18px 14px; text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .kpi-icon { font-size: 1.5rem; }
    .kpi-value { font-size: 1.8rem; font-weight: 800; color: #1B2A4A; margin: 4px 0; }
    .kpi-label { font-size: 0.82rem; color: #718096; font-weight: 500; }

    .section-title {
        font-size: 1.05rem; font-weight: 700; color: #1B2A4A;
        border-left: 4px solid #2D6BC4; padding: 8px 12px;
        margin: 20px 0 12px 0; background: #EBF4FF;
        border-radius: 0 6px 6px 0;
    }
    .insight-box {
        background: #EBF8FF; border-left: 4px solid #2D6BC4;
        border-radius: 0 8px 8px 0; padding: 12px 16px;
        margin: 8px 0; font-size: 0.9rem; color: #1B2A4A;
    }
    .warning-box {
        background: #FFFBEB; border-left: 4px solid #F5A623;
        border-radius: 0 8px 8px 0; padding: 12px 16px;
        margin: 8px 0; font-size: 0.9rem; color: #744210;
    }
    .danger-box {
        background: #FFF5F5; border-left: 4px solid #E53E3E;
        border-radius: 0 8px 8px 0; padding: 12px 16px;
        margin: 8px 0; font-size: 0.9rem; color: #742A2A;
    }
    .success-box {
        background: #F0FFF4; border-left: 4px solid #27AE60;
        border-radius: 0 8px 8px 0; padding: 12px 16px;
        margin: 8px 0; font-size: 0.9rem; color: #1A4731;
    }
    [data-testid="stDataFrame"] { border-radius: 8px; border: 1px solid #E2E8F0; }
    .stTextInput input { background-color: #FFFFFF; color: #1B2A4A; border: 1.5px solid #CBD5E0; border-radius: 7px; }
    .stSelectbox > div > div { background-color: #FFFFFF; border: 1.5px solid #CBD5E0; border-radius: 7px; }
    /* [디자인 3] 필터 multiselect 선택 태그 무채색 계열 */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #64748B !important;
        color: #FFFFFF !important;
        border-radius: 5px !important;
    }
    .stMultiSelect [data-baseweb="tag"] span { color: #FFFFFF !important; }
    .stMultiSelect [data-baseweb="tag"] svg { fill: #E2E8F0 !important; }
    [data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
        background-color: #64748B !important;
    }
    hr { border-color: #E2E8F0; }
    footer { color: #A0AEC0 !important; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# [v2.6.2] 접근 제한 — 공유 비밀번호 관문(사업부 구성원 전용, 옵션 C)
#   · Streamlit Cloud → Manage app → Settings → Secrets 에 app_password 설정
#   · 세션당 1회 입력 후 통과(재입력 불필요). 미설정 시 경고 후 개방(잠금 해제).
# ════════════════════════════════════════════════════════════════════
def _require_login():
    if st.session_state.get("_pcid_authed"):
        return
    try:
        _pw = str(st.secrets["app_password"]) if "app_password" in st.secrets else ""
    except Exception:
        _pw = ""
    if not _pw:
        st.session_state["_pcid_authed"] = True
        st.warning("⚠ 접근 비밀번호(app_password)가 설정되지 않아 접근 제한이 비활성화되어 있습니다. "
                   "Streamlit Cloud → Manage app → Settings → Secrets 에 app_password 를 추가하세요.")
        return
    _l, _c, _r = st.columns([1, 1.5, 1])
    with _c:
        st.markdown("<div style='height:7vh'></div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align:center;font-weight:800;font-size:1.5rem;color:#1B2A4A'>"
                    "PASCUCCI Consumer Intelligence Dashboard</div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align:center;color:#71808F;margin:6px 0 18px'>"
                    "🔒 사업부 구성원 전용 — 접근 비밀번호를 입력하세요</div>", unsafe_allow_html=True)
        with st.form("_pcid_login", clear_on_submit=False):
            _pwin = st.text_input("비밀번호", type="password",
                                  label_visibility="collapsed", placeholder="접근 비밀번호")
            _ok = st.form_submit_button("입장", use_container_width=True)
        if _ok:
            if _pwin == _pw:
                st.session_state["_pcid_authed"] = True
                st.rerun()
            else:
                st.error("비밀번호가 올바르지 않습니다. 다시 시도해 주세요.")
        st.caption("문의: 사업부 대시보드 운영자")
    st.stop()


_require_login()

# ══════════════════════════════════════════════════════
# 공통 상수
# ══════════════════════════════════════════════════════
BRAND_COLORS = {
    "스타벅스":    "#E74C3C",
    "투썸플레이스": "#8E44AD",
    "메가커피":    "#27AE60",
    "컴포즈커피":  "#16A085",
    "이디야":      "#1D6A3A",
    "폴바셋":      "#0F6E56",
    "테라로사":    "#2980B9",
    "빽다방":      "#E67E22",
    "블루보틀":    "#D35400",
    "할리스":      "#7F8C8D",
    "더벤티":      "#B7950B",
    "파스쿠찌":    "#C0392B",
}
# [v2.7.0] 평가 대상 = 당사 + 경쟁 '커피전문점' 12개 (베이커리·도넛·엔제리너스는 제외)
TARGET_BRANDS = ["파스쿠찌","스타벅스","투썸플레이스","메가커피","컴포즈커피","이디야","폴바셋","테라로사","빽다방","블루보틀","할리스","더벤티"]
# 해설 박스 자동 생성용 브랜드 묶음 (가격대·포지션 기준)
BRAND_GROUPS = {
    "가성비(저가)":      ["메가커피", "컴포즈커피", "빽다방", "더벤티"],
    "프리미엄·스페셜티": ["폴바셋", "테라로사", "블루보틀"],
    "대형·중가":         ["스타벅스", "투썸플레이스", "이디야", "할리스"],
}

# ── [v2.7.0] 브랜드 판정 규칙 — 크롤러 v3.2(keyword_config.py)와 동일 ──
#   · 별칭(소문자 포함 여부) → '빽' 정규식 → '메가' 문맥 약칭 순으로 판정
#   · 크롤러 규칙을 바꾸면 여기도 같이 맞출 것
BRAND_ALIASES = {
    "파스쿠찌":    ["파스쿠찌", "파스쿠치", "pascucci"],
    "스타벅스":    ["스타벅스", "스벅", "별다방", "starbucks"],
    "투썸플레이스": ["투썸플레이스", "투썸"],
    "메가커피":    ["메가커피", "메가mgc", "메가 커피", "mgc커피", "메가엠지씨"],
    "컴포즈커피":  ["컴포즈커피", "컴포즈"],
    "이디야":      ["이디야"],
    "빽다방":      ["빽다방"],
    "폴바셋":      ["폴바셋"],
    "블루보틀":    ["블루보틀"],
    "테라로사":    ["테라로사"],
    "할리스":      ["할리스"],
    "더벤티":      ["더벤티"],
}
_BRAND_PATTERNS = {"빽다방": re.compile(r"(?<![빽뺵~])빽(?![빽뺵~]|보이|햄)")}
_CTX_WIN = 20
_COFFEE_CTX_RE = re.compile(r"아아|아메리카노|커피|라떼|카페|음료|스무디|빙수|메뉴|원두|프라페|에이드|디저트|쿠폰|기프티콘")
_CONTEXT_ALIASES = {
    "메가커피": (re.compile(r"(?<![가-힣A-Za-z])메가(?!박스|스터디|톤|바이트|시티|와트|헤르츠|비트|픽셀|트렌드|히트|쇼|볼트"
                            r"|맨|폰|급|딜|세일|마트|스토어|커피|mgc|MGC|엠지씨)"), _COFFEE_CTX_RE),
}


def _ctx_spans(text, brand):
    rule = _CONTEXT_ALIASES.get(brand)
    if not rule:
        return []
    tok, ctx = rule
    return [m.span() for m in tok.finditer(text)
            if ctx.search(text[max(0, m.start() - _CTX_WIN): m.end() + _CTX_WIN])]


def detect_brands_v32(text):
    """글에 언급된 대상 브랜드 목록 (TARGET_BRANDS 순서)."""
    text = str(text or "")
    tl = text.lower()
    found = []
    for b in TARGET_BRANDS:
        if any(a in tl for a in BRAND_ALIASES.get(b, [b])):
            found.append(b)
            continue
        pat = _BRAND_PATTERNS.get(b)
        if pat is not None and pat.search(text):
            found.append(b)
            continue
        if b in _CONTEXT_ALIASES and _ctx_spans(text, b):
            found.append(b)
    return found


def count_brand_v32(text, brand):
    """브랜드 언급 횟수 (겹치는 표기는 1회)."""
    text = str(text or "")
    tl = text.lower()
    spans = []
    for a in BRAND_ALIASES.get(brand, [brand]):
        i = tl.find(a)
        while i >= 0:
            spans.append((i, i + len(a)))
            i = tl.find(a, i + len(a))
    pat = _BRAND_PATTERNS.get(brand)
    if pat is not None:
        spans += [m.span() for m in pat.finditer(text)]
    spans += _ctx_spans(text, brand)
    n, end = 0, -1
    for s_, e_ in sorted(spans):
        if s_ >= end:
            n += 1
        end = max(end, e_)
    return n


# ── [v2.7.0] 수집 검색어 계획 (시즌별) — 추이 분석의 '검색 상한' 판정에 사용 ──
#   행에 seed_query 열이 있으면 그것을 쓰고, 없으면 아래 목록으로 어느 검색어에서 온 글인지 추정.
#   크롤러 keyword_config.py의 DEPTH_MENU_SEEDS·TREND_SEEDS와 같은 내용 (시즌이 바뀌면 추가)
_SEED_PLANS = {
    "2026Q4": {
        "depth": {
            "파스쿠찌": ["그라니따", "젤라또", "티라미수", "흑임자", "여주 쌀"],
            "스타벅스": ["돌체라떼", "자몽허니블랙티", "글레이즈드", "고구마 라떼", "토피넛 라떼"],
            "투썸플레이스": ["스초생", "아박", "케이크", "밤 생크림 케이크", "고구마 생크림 케이크"],
            "메가커피": ["메가리카노", "하우스밀크 라떼", "오르조라떼", "골든애플 블랙티", "팥크림치즈빵"],
            "컴포즈커피": ["아메리카노", "바닐라크림라떼", "클라우드 라떼", "딥라떼", "밤 티라미수"],
            "이디야": ["토피넛라떼", "티라미수", "산리오", "밤 크림 라떼", "흑임자 크림 라떼"],
            "빽다방": ["원조커피", "앗메리카노", "사라다빵", "빽스치노", "블랙벨벳"],
            "할리스": ["바닐라딜라이트", "할리치노", "고구마라떼", "흑임자", "호감 스무디"],
            "폴바셋": ["룽고", "아이스크림라떼", "밀크아이스크림", "유자"],
            "블루보틀": ["뉴올리언스", "드립커피", "라떼", "원두"],
            "테라로사": ["핸드드립", "원두", "베이커리", "아이스크림"],
            "더벤티": ["아메리카노", "흑당라떼", "과일주스", "쉐이크"],
            "엔제리너스": ["아메리치노", "반미", "팡도르", "케이크"],
            "파리바게뜨": ["케이크", "소금빵", "샌드위치", "크루아상"],
            "뚜레쥬르": ["케이크", "소금빵", "도넛", "식빵"],
            "던킨": ["도넛", "먼치킨", "커피", "베이글"],
            "크리스피크림": ["오리지널글레이즈드", "도넛", "더즌", "커피"],
        },
        "trend": ["말차 디저트", "소금빵", "저가 커피", "카페 신메뉴", "얼먹젤리", "버터떡", "우베",
                  "요아정", "약과", "디카페인", "흑임자 디저트", "호지차", "밤 디저트"],
    },
    "2026Q3": {
        "depth": {
            "파스쿠찌": ["그라니따", "베리베리 그라니따", "젤라또", "티라미수", "파니니"],
            "스타벅스": ["프라푸치노", "카페 브륄레", "돌체라떼", "자몽허니블랙티", "콜드브루"],
            "투썸플레이스": ["스초생", "아박", "크런치 아박", "파인생", "케이크"],
            "메가커피": ["메가리카노", "컵빙수", "꿀수박주스", "자몽톡톡 스무디", "말차 팥빙"],
            "컴포즈커피": ["아메리카노", "논산 수박주스", "저당 복숭아 스무디", "제주 한라봉 스무디", "바닐라크림라떼"],
            "이디야": ["토피넛라떼", "빙수", "컵팥절빙", "티라미수"],
            "빽다방": ["원조커피", "앗메리카노", "사라다빵", "빽스치노", "통단팥컵빙"],
            "할리스": ["바닐라딜라이트", "할리치노", "고구마라떼", "컵빙수"],
            "폴바셋": ["룽고", "아이스크림라떼", "밀크아이스크림", "라벤더"],
            "블루보틀": ["뉴올리언스", "드립커피", "라떼", "원두"],
            "테라로사": ["핸드드립", "원두", "베이커리", "아이스크림"],
            "더벤티": ["아메리카노", "흑당라떼", "과일주스", "쉐이크"],
            "엔제리너스": ["아메리치노", "반미", "팡도르", "케이크"],
            "파리바게뜨": ["케이크", "소금빵", "샌드위치", "크루아상"],
            "뚜레쥬르": ["케이크", "소금빵", "도넛", "식빵"],
            "던킨": ["도넛", "먼치킨", "커피", "베이글"],
            "크리스피크림": ["오리지널글레이즈드", "도넛", "더즌", "커피"],
        },
        "trend": ["말차 디저트", "소금빵", "저가 커피", "카페 신메뉴", "두쫀쿠", "두바이초콜릿",
                  "카다이프", "피스타치오", "아사이볼", "흑임자"],
    },
}
SAMPLER_TAG = "-sampler"          # 반복 샘플링 행 표시 (seed_season 끝)
TS_MIN_MONTH_DAYS = 10            # 월별 추이: 기간 안에 든 날이 이보다 적은 달은 제외
NSS_MIN_N = 20                    # 월별 NSS: 브랜드·월 표본이 이보다 적으면 표시하지 않음
SENT_COLORS = {"긍정": "#27AE60", "중립": "#F39C12", "부정": "#E74C3C"}
TOPIC_LABELS = ["브랜드선택·대안","디카페인·건강","맛·원두품질","카페공간·작업","가격·가성비","불매·이슈","선물·추천"]
TOPIC_COLORS = ["#2980B9","#16A085","#27AE60","#E67E22","#8E44AD","#E74C3C","#F39C12"]

STOPWORDS = set(
    "이 가 을 를 은 는 에 의 도 로 고 그 하다 있다 되다 않다 이다 것 수 나 저 우리 그리고 하지만 "
    "정말 진짜 너무 좀 더 제 여기 거기 그냥 있어요 없어요 해요 했어요 같아요 입니다 합니다 그게 "
    "이게 에서 한테 보다 있고 하고 하면 그래서 아니고 아니라 있는데 많이 제가 지금 먹고 마시고 "
    "가서 먹는 먹어요 사람 사람이 다른 하나 이렇게 그렇게 요즘 분들 내가 아주 엄청 무슨 이거 "
    "저거 저도 나도 저는 나는 우리 댓글 같이 항상 어디 얼마 있는 하는 그런 이런 같은 근데 이제 "
    "그래도 해서 있어서 없는 없고 것도 사람들이 사람들 누가 보면 얼마나 하는데 없어서 가끔 정도 "
    "다시 바로 오늘 시간 감사 아니".split()
)

# [텍스트마이닝 2] 의미 추론이 어려운 부사·수식어 — 토큰엔 남기되
# 대응일치분석(CA)·토픽모델링(LDA)·키워드 집계 등 '지표 집계'에서만 제외.
# 이들 단어만으로는 사용 맥락을 알 수 없어 해석 신뢰도를 떨어뜨리기 때문.
MEANINGLESS_MODIFIERS = set(
    "많이 아니면 거의 조금 약간 매우 굉장히 엄청 되게 너무 진짜 정말 완전 그냥 좀 더 덜 "
    "아주 워낙 훨씬 가장 제일 무척 상당히 꽤 별로 그다지 다소 어느정도 대체로 대부분 "
    "보통 아마 혹시 만약 일단 우선 결국 그냥 막 살짝 슬쩍 딱 그저 단지 오직 마치 "
    "이런 저런 그런 어떤 무슨 이렇게 저렇게 그렇게 어떻게 왜 언제 어디 누가 "
    "그리고 그러나 하지만 그래서 그래도 또한 또 즉 따라서 게다가 다만 한편 "
    "있다 없다 하다 되다 같다 이다 보다 들다 나다 오다 가다 주다 받다".split()
)

ATTR_DICT = {
    "맛·품질":    ["맛있","맛나","달콤","진한","부드럽","식감","쓴맛","산미","향","원두","에스프레소"],
    "가격·가성비": ["가격","비싸","저렴","가성비","합리","인상","할인","쿠폰"],
    "공간·분위기": ["카페","분위기","인테리어","좌석","조용","넓은","공부","작업","콘센트","카공"],
    "서비스":     ["직원","서비스","친절","속도","주문","대기","청결","응대"],
    "접근성":     ["위치","매장","점포","테이크아웃","드라이브","배달","픽업"],
    "브랜드이미지": ["이미지","브랜드","선호","느낌","감성","프리미엄","불매"],
    "프로모션·혜택":["이벤트","프로모션","혜택","한정","쿠폰","멤버십","상품권","환불"],
    "MD·굿즈":     ["굿즈","md","엠디","다이어리","텀블러","머그","키링","리유저블","콜라보","컬래버","한정판","피규어","스티커"],
    "디카페인":   ["디카페인","디카페","카페인"],
}

RISK_PATTERNS = {
    "🔥 정치·이슈":  ["불매","일베","정용진","이마트","신세계","극우","광주","멸공"],
    "💳 환불·쿠폰":  ["환불","상품권","쿠폰","잔액","기프티콘","카드"],
    "💸 가격":      ["비싸","인상","가격","원가","올린"],
    "😞 품질 실망": ["맛없","실망","별로","최악","부족","아쉽"],
    "🚶 접근성":    ["없어서","품절","재고","대체","매장에"],
}

OCCASION_DICT = {
    "공부·업무": ["공부","작업","노트북","콘센트","카공","업무","혼자"],
    "만남·미팅": ["친구","약속","만남","미팅","모임","데이트","커플","같이","함께"],
    "출근·이동": ["출근","이동","테이크아웃","픽업","드라이브"],
    "선물·기념": ["선물","기념","생일","기프트","굿즈"],
    "배달·홈카페":["배달","집에서","홈카페","캡슐","드립백","인스턴트"],
}

# ── 제품 사전 (커피·음료·디저트·푸드 망라) [항목 4] ──
PRODUCT_DICT = {
    # 커피·음료
    "아메리카노":["아메리카노","아아","뜨아"], "카페라떼":["카페라떼","라떼"],
    "에스프레소":["에스프레소"], "콜드브루":["콜드브루","콜브"],
    "카푸치노":["카푸치노"], "디카페인":["디카페인","디카페"],
    "프라푸치노":["프라푸치노","프라푸"], "에이드":["에이드"],
    "스무디":["스무디"], "밀크티":["밀크티"], "말차라떼":["말차"],
    "녹차·티":["녹차","얼그레이","루이보스","호지차"], "초콜릿음료":["핫초코","초콜릿라떼"],
    # 디저트
    "케이크":["케이크","케익"], "마카롱":["마카롱"], "티라미수":["티라미수"],
    "타르트":["타르트","에그타르트"], "크로플":["크로플"], "쿠키":["쿠키"],
    "빙수":["빙수"], "푸딩":["푸딩"],
    "아이스크림":["아이스크림"], "젤라또":["젤라또","젤라토"],
    # 트렌디·시그니처 [v2.3.1]
    "두바이초콜릿":["두바이초콜릿","두바이","쪼꼬바"], "두쫀쿠":["두쫀쿠","두바이쿠키","쪼득쿠키"],
    "우베":["우베","우베라떼","자색고구마"], "피스타치오":["피스타치오","피스타치오라떼"],
    "흑임자":["흑임자","흑임자라떼"], "말차디저트":["말차케이크","말차티라미수"],
    # 베이커리·푸드
    "소금빵":["소금빵"], "크로와상":["크로와상","크로아상"],
    "베이글":["베이글"], "스콘":["스콘"], "머핀":["머핀"],
    "빵·베이커리":["베이커리","식빵","바게트"],
    "샌드위치":["샌드위치","파니니"], "샐러드":["샐러드"],
}

# ── 프로모션 사전 [항목 5] ──
PROMO_DICT = {
    "통신·카드할인": ["통신할인","카드할인","제휴할인","KT","SKT","LG유플","삼성카드","현대카드","멤버십할인"],
    "이벤트":       ["이벤트","응모","참여","추첨","경품"],
    "프로모션·행사": ["프로모션","행사","페스타","페어"],
    "1+1·증정":     ["1+1","원플러스원","증정","사은품"],
    "굿즈·MD":      ["굿즈","MD","엠디","다이어리","텀블러","프리퀀시","스티커","리유저블","머그","키링"],
    "기프티콘·상품권":["기프티콘","기프트콘","모바일상품권","모바일쿠폰","교환권","e쿠폰","상품권"],
    "페이 행사":     ["네이버페이","카카오페이","토스페이","페이백","간편결제","네이버페이","제로페이"],
    "쿠폰·적립":    ["쿠폰","적립","스탬프","포인트"],
    "신메뉴·출시":  ["신메뉴","출시","새로나온","리뉴얼","한정"],
}

# 촉진 반응 강도 [항목 5]
PROMO_REACTION = {
    "강한 긍정": (["개꿀","꿀이","필참","머스트","잇템","갓","혜자","대박","무조건","사야","존맛","꼭사"], 2.0),
    "긍정":      (["좋아","괜찮","유용","이득","득템","쏠쏠","갖고싶","사고싶","혹하"], 1.0),
    "부정":      (["별로","아쉽","쓸데","꽝","손해","실망","비싸기만","글쎄"], -1.0),
}

# ── 트렌드 카테고리 분류 [항목 10] ──
TREND_CATEGORY = {
    "커피·음료": ["디카페인","말차·녹차","콜드브루","오트밀크","흑당","유자·시트러스"],
    "푸드류":    ["소금빵","크로플","바스크치즈","티라미수","두바이초콜릿"],
    "식재료":    ["크림치즈","피스타치오","흑임자·전통"],
}

def chart_style(fig, height=420, showlegend=True):
    fig.update_layout(
        plot_bgcolor="#FFFFFF", paper_bgcolor="#F7F9FC",
        font=dict(color="#2D3748", size=12), height=height,
        showlegend=showlegend,
        margin=dict(l=50, r=30, t=50, b=45),
        title_font=dict(color="#1B2A4A", size=14, family="Arial"),
        legend=dict(bgcolor="#FFFFFF", bordercolor="#E2E8F0", borderwidth=1,
                    font=dict(size=11, color="#2D3748")),
        xaxis=dict(gridcolor="#EDF2F7", zerolinecolor="#CBD5E0",
                   tickfont=dict(color="#4A5568"), title_font=dict(color="#4A5568")),
        yaxis=dict(gridcolor="#EDF2F7", zerolinecolor="#CBD5E0",
                   tickfont=dict(color="#4A5568"), title_font=dict(color="#4A5568")),
    )
    return fig

# ══════════════════════════════════════════════════════
# [v2.7.0] 데이터 입출력 공통 — 모든 로더가 같은 방식으로 읽음 (parquet·csv·gz·xz·xlsx)
# ══════════════════════════════════════════════════════
def _read_data_file(path, usecols=None):
    name = str(getattr(path, "name", path))
    if name.endswith(".parquet"):
        df = pd.read_parquet(path)
        if usecols:
            df = df[[c for c in usecols if c in df.columns]]
        return df.astype({c: str for c in df.columns if c == "doc_id"})
    if name.endswith((".csv", ".csv.gz", ".gz", ".csv.xz", ".xz")):
        if usecols:
            hdr = pd.read_csv(path, encoding="utf-8-sig", compression="infer", nrows=0).columns
            usecols = [c for c in usecols if c in hdr]
        # 모두 문자열로 읽음: 숫자처럼 생긴 doc_id(예: 1234e5678901)가 숫자로 바뀌어 빠지는 문제 방지
        return pd.read_csv(path, encoding="utf-8-sig", compression="infer", dtype=str,
                           usecols=usecols, low_memory=False)
    df = pd.read_excel(path, dtype=str)
    return df[[c for c in usecols if c in df.columns]] if usecols else df


def _to_dt(series):
    """[v2.7.0] 날짜 파싱 — 형식이 섞여 있어도(예: '2026-10-29'와 '2026-10-29 13:05') 모두 읽음.
    pandas는 첫 값의 형식으로 나머지를 읽어, 형식이 다른 행이 조용히 빈 값(NaT)이 되던 문제 방지."""
    try:
        return pd.to_datetime(series, errors="coerce", format="mixed")
    except (TypeError, ValueError):
        return pd.to_datetime(series, errors="coerce")


def _file_sig(path):
    try:
        s = os.stat(path)
        return f"{os.path.basename(str(path))}:{int(s.st_mtime)}:{s.st_size}"
    except Exception:
        return str(path)


def _session_starts(ts_sorted, gap_hours=18):
    """정렬된 수집 시각 → 수집 세션 시작 시각들 (gap_hours 넘게 비면 다른 수집으로 봄)."""
    if len(ts_sorted) == 0:
        return ts_sorted
    gaps = np.diff(ts_sorted) > np.timedelta64(int(gap_hours * 3600), "s")
    return np.concatenate([ts_sorted[:1], ts_sorted[1:][gaps]])


def _query_key(layer, brand, season, title, body):
    """블로그 행이 어느 검색어에서 왔는지 추정 (검색어 계획의 메뉴·트렌드어가 글에 있는지로 판정)."""
    plan = _SEED_PLANS.get(season) or {}
    if layer == "sov":
        return brand or "sov||미상"
    if layer == "depth":
        menus = (plan.get("depth") or {}).get(brand)
        if menus:
            comp = (title + " " + body).replace(" ", "")
            for m in menus:
                if m.replace(" ", "") in comp:
                    return f"{brand} {m}"
        return f"depth|{brand}|미상"
    if layer == "trend":
        terms = plan.get("trend")
        if terms:
            txt = title + " " + body
            for t in terms:
                if all(w in txt for w in t.split()):
                    return t
        return "trend||미상"
    return f"{layer or 'blog'}|{brand}|기타"


CAP_MIN_N = 300   # 이보다 글이 적은 검색어는 1,000건 상한에 걸렸을 수 없음 → 늦게 시작해도 자연 발생으로 봄


@st.cache_data(show_spinner="수집 범위 점검 중...")
def compute_coverage(path, fsig, period_from=""):
    """[v2.7.0] 추이 분석에 쓸 수 있는 글 판정.
    네이버 검색은 검색어당 최신 1,000건까지만 주므로, 글이 많은 검색어는 최근 며칠만 담긴다.
    이런 검색어의 글을 월별 추이에 넣으면 최근 달이 부풀려지므로, 수집 기간 전체를 빠짐없이 덮은
    흐름(검색어·게시판 단위)의 글만 _ts_ok=True로 표시한다. 수집 당일(부분 수집) 글도 제외."""
    cols = ["doc_id", "source_type", "source_name", "board_id", "collection_layer", "seed_brand",
            "seed_season", "seed_query", "title", "body", "created_at", "collected_at"]
    try:
        df = _read_data_file(path, usecols=cols)
    except Exception:
        return None
    if "doc_id" not in df.columns or "created_at" not in df.columns:
        return None
    df = df[df["doc_id"].astype(str).str.match(r"^[a-f0-9]{12}$", na=False)]
    for c in cols:
        if c not in df.columns:
            df[c] = ""
        df[c] = df[c].fillna("").astype(str)
    samp = df["seed_season"].str.endswith(SAMPLER_TAG)
    n_sampler = int(samp.sum())
    df = df[~samp].copy()
    if len(df) == 0:
        return None

    day = _to_dt(df["created_at"]).dt.normalize()
    cts = _to_dt(df["collected_at"])
    # 수집 세션별 '마지막 완전한 날' = 세션 시작일 전날
    run_end = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")
    sess = pd.Series(-1, index=df.index)
    for _src, idx in df.groupby("source_name").groups.items():
        t = cts.loc[idx]
        ok = t.notna()
        if not ok.any():
            continue
        starts = _session_starts(np.unique(t[ok].values))
        pos = np.searchsorted(starts, t[ok].values, side="right") - 1
        sess.loc[t[ok].index] = pos
        run_end.loc[t[ok].index] = (pd.to_datetime(starts[pos]).normalize() - pd.Timedelta(days=1)).values
    partial = day.notna() & run_end.notna() & (day > run_end)

    win_start = pd.Timestamp(period_from).normalize() if period_from else day.min()
    if pd.isna(win_start):
        return None
    win_end = min(day.max(), run_end.max()) if run_end.notna().any() else day.max() - pd.Timedelta(days=1)
    span = max(1, (win_end - win_start).days + 1)

    is_blog = df["source_type"].eq("blog") | df["source_name"].eq("네이버블로그")
    layer = df["collection_layer"].str.strip()
    season = df["seed_season"].str.split("-").str[0]
    qkey = pd.Series("", index=df.index, dtype=object)
    has_sq = df["seed_query"].str.strip().ne("")
    qkey[has_sq] = df.loc[has_sq, "seed_query"]
    need = is_blog & ~has_sq
    if need.any():
        sub = df[need]
        qkey[need] = [_query_key(l, b, s, t, bd[:4000]) for l, b, s, t, bd in
                      zip(layer[need], sub["seed_brand"], season[need], sub["title"], sub["body"])]
    comm = ~is_blog & ~has_sq
    qkey[comm] = df.loc[comm, "board_id"] + "|" + df.loc[comm, "seed_brand"]

    g = pd.DataFrame({"src": df["source_name"], "board": df["board_id"], "layer": layer, "q": qkey,
                      "sess": sess, "brand": df["seed_brand"], "day": day, "run_end": run_end,
                      "blog": is_blog})
    keys = ["src", "board", "layer", "q", "sess"]

    Q_TAIL = 0.02   # 블로그: 다른 검색어에서 섞여 들어온 소수의 옛 글은 무시 (하위 2% 날짜)

    stats = g.groupby(keys, dropna=False).agg(n=("day", "size"), d_min=("day", "min"),
                                              d_q=("day", lambda s: s.dropna().quantile(Q_TAIL) if s.notna().sum() >= 50 else s.min()),
                                              run_end=("run_end", "min"), brand=("brand", "first"),
                                              blog=("blog", "first")).reset_index()
    stats["d0"] = stats["d_q"].where(stats["blog"], stats["d_min"])
    tol = np.maximum(2, np.ceil(3 * span / stats["n"].clip(lower=1)))
    tol = tol + np.where(stats["blog"] & (stats["n"] >= 50), np.ceil(Q_TAIL * span * 1.5), 0)
    late = (stats["d0"] - win_start).dt.days
    starts_ok = (late <= tol) | (stats["n"] < CAP_MIN_N)
    ends_ok = stats["run_end"].isna() | ((win_end - stats["run_end"]).dt.days <= 2)
    stats["full"] = (starts_ok & ends_ok & stats["d0"].notna()).astype(bool)
    # 검색어를 못 정한 글: 같은 브랜드·레이어의 검색어가 모두 기간 전체를 덮을 때만 인정
    unk = stats["q"].astype(str).str.endswith("|미상")
    if unk.any():
        fam = ["src", "layer", "brand", "sess"]
        known_full = stats[~unk].groupby(fam)["full"].all()
        for i in stats.index[unk]:
            k = tuple(stats.loc[i, fam])
            stats.loc[i, "full"] = bool(stats.loc[i, "full"]) and bool(known_full.get(k, True))
    full_map = stats.set_index(keys)["full"]
    row_full = pd.Series(full_map.reindex(pd.MultiIndex.from_frame(g[keys])).values,
                         index=df.index).fillna(False).astype(bool)
    ts_ok = row_full & day.notna() & (day >= win_start) & (day <= win_end) & ~partial

    capped = stats[stats["blog"] & ~stats["full"] & (stats["n"] >= CAP_MIN_N)]
    capped = capped.sort_values("n", ascending=False)
    meta = {
        "win_start": win_start, "win_end": win_end, "n_rows": int(len(df)),
        "n_ts": int(ts_ok.sum()), "n_sampler": n_sampler, "n_partial": int(partial.sum()),
        "n_blog": int(is_blog.sum()), "n_blog_ts": int((ts_ok & is_blog).sum()),
        "n_comm": int((~is_blog).sum()), "n_comm_ts": int((ts_ok & ~is_blog).sum()),
        "capped_queries": [str(q) for q in capped["q"].head(12)],
        "n_capped": int(len(capped)),
    }
    flags = pd.DataFrame({"doc_id": df["doc_id"].values, "_ts_ok": ts_ok.values,
                          "_partial": partial.values})
    return {"flags": flags, "meta": meta, "streams": stats.drop(columns=["blog", "d_q", "d_min"])}


def _attach_coverage(df, cov):
    """로더 결과에 추이 분석 플래그(_ts_ok·_partial)와 날짜(_day)를 붙임."""
    df["_day"] = _to_dt(df["created_at"]).dt.normalize()
    if cov is None:
        df["_ts_ok"] = df["_day"].notna()
        df["_partial"] = False
        return df
    f = cov["flags"].drop_duplicates("doc_id").set_index("doc_id")
    df["_ts_ok"] = df["doc_id"].map(f["_ts_ok"]).fillna(False).astype(bool)
    df["_partial"] = df["doc_id"].map(f["_partial"]).fillna(False).astype(bool)
    return df


# ══════════════════════════════════════════════════════
# 데이터 로딩 및 전처리
# ══════════════════════════════════════════════════════
@st.cache_data(show_spinner="데이터 전처리 중...")
def load_and_preprocess(path, fsig="", period_from=""):
    df = _read_data_file(path)
    df = df[df["doc_id"].astype(str).str.match(r"^[a-f0-9]{12}$", na=False)].copy()
    # [v2.7.0] 반복 샘플링 행은 SOV 환산 전용 → 분석 데이터에서 제외
    if "seed_season" in df.columns:
        df = df[~df["seed_season"].fillna("").astype(str).str.endswith(SAMPLER_TAG)].copy()
    for _c in ("title", "body", "comments_json", "brand_mentions", "created_at"):
        if _c not in df.columns:
            df[_c] = np.nan

    coffee_kw = ["커피","카페","아메리카노","라떼","에스프레소","스타벅스","스벅","투썸","이디야",
                 "메가커피","컴포즈","빽다방","할리스","폴바셋","파스쿠찌","블루보틀","테라로사",
                 "더벤티","드립","콜드브루","디카페인","원두","핸드드립"]

    def get_comments(j):
        try:
            return " ".join(c.get("body","") for c in json.loads(j)) if pd.notna(j) else ""
        except:
            return ""

    df["comment_text"] = df["comments_json"].apply(get_comments)
    df["full_text"] = (df["title"].fillna("") + " " +
                       df["body"].fillna("") + " " +
                       df["comment_text"])

    # [v2.7.0] 브랜드 판정은 크롤러 v3.2 규칙(detect_brands_v32)으로 통일
    df["brands"] = df["full_text"].apply(detect_brands_v32)
    # 분석 대상 = 커피 관련어가 있거나 대상 커피전문점(12개)을 언급한 글
    #   (베이커리·도넛 등 비교군 밖 브랜드만 언급한 글은 브랜드 분석에서 제외 — 트렌드 탭에는 그대로 반영)
    df["is_rel"] = (
        df["full_text"].apply(lambda t: any(k in t for k in coffee_kw)) |
        (df["brands"].apply(len) > 0)
    )
    v = df[df["is_rel"]].copy()

    pos_kw = ["맛있","좋아","좋다","추천","최고","만족","친절","합리","가성비","저렴","달콤","훌륭","깔끔","즐겨","단골","완벽"]
    neg_kw = ["맛없","별로","실망","불만","최악","비싸","불친절","느리","아쉽","안좋","싫","불매","후회","환불","절대","다시는"]

    def detect_primary_brand(t, bs):
        """본문에서 가장 많이 언급된 '주요 브랜드' 판별 (리스크 필터용)"""
        if not bs:
            return ""
        if len(bs) == 1:
            return bs[0]
        counts = {b: count_brand_v32(t, b) for b in bs}
        return max(counts, key=counts.get)

    def get_sentiment(t):
        p = sum(1 for k in pos_kw if k in str(t))
        n = sum(1 for k in neg_kw if k in str(t))
        return "긍정" if p > n else ("부정" if n > p else "중립")

    def tokenize(t):
        return [w for w in re.findall(r"[가-힣]{2,6}", str(t)) if w not in STOPWORDS]

    def get_occasion(t):
        for oc, kws in OCCASION_DICT.items():
            if any(k in str(t) for k in kws):
                return oc
        return "기타"

    v["primary_brand"] = [detect_primary_brand(t, bs) for t, bs in zip(v["full_text"], v["brands"])]
    v["sentiment"]  = v["full_text"].apply(get_sentiment)
    v["tokens_str"] = v["full_text"].apply(lambda t: " ".join(tokenize(t)))  # [v2.6.15] tokens 리스트 컬럼 제거(메모리 절감)
    v["occasion"]   = v["full_text"].apply(get_occasion)
    v["created_at"] = _to_dt(v["created_at"])
    v["year_month"] = v["created_at"].dt.to_period("M").astype(str)
    # [v2.7.0] 추이 분석 플래그(_ts_ok: 기간 전체를 덮는 흐름의 글, 수집 당일 글 제외)
    v = _attach_coverage(v, compute_coverage(path, fsig, period_from))

    # [v2.6.15] 메모리 다이어트 — 하류에서 사용하지 않는 무거운 컬럼 제거 (Community Cloud OOM 방지)
    _heavy_unused = ["comments_json", "comment_text", "is_rel", "matched_keywords",
                     "sponsor_signals", "co_mention_brands", "matched_L2_product",
                     "matched_L3_occasion", "matched_L4_competitive", "brand_mentions"]
    v = v.drop(columns=[c for c in _heavy_unused if c in v.columns])
    import gc as _gc
    del df
    _gc.collect()

    return v

# ══════════════════════════════════════════════════════
# 분석 함수 모음
# ══════════════════════════════════════════════════════
FNB_CATS = {
    "디저트": ["디저트","케이크","마카롱","다쿠아즈","쿠키","타르트","푸딩","마들렌","휘낭시에","스콘","크로플","와플","도넛","빙수","젤라또","아이스크림","초코","초콜릿","티라미수","에그타르트","슈크림","약과","까눌레"],
    "베이커리": ["베이커리","크루아상","바게트","소금빵","식빵","단팥빵","앙버터","프레첼","페이스트리","크림빵","빵집","모닝빵","마늘빵"],
    "카페푸드": ["샌드위치","파니니","샐러드","베이글","브런치","토스트","핫도그","키슈","그릭요거트","에그마요"],
    "식재료·플레이버": ["피스타치오","두바이","흑임자","말차","녹차","쑥","인절미","생크림","오트밀","그래놀라","크림치즈","연유","단호박","고구마","얼그레이","바닐라","캐러멜","헤이즐넛","딸기","블루베리","흑당"],
}
_FNB_POS = ["맛있","좋아","좋다","추천","최고","만족","친절","합리","가성비","저렴","달콤","훌륭","깔끔","즐겨","단골","완벽","부드럽","촉촉","고소"]
_FNB_NEG = ["맛없","별로","실망","불만","최악","비싸","불친절","느리","아쉽","안좋","싫","불매","후회","환불","절대","다시는","퍽퍽","느끼"]
_COFFEE_KW = ["커피","카페","아메리카노","라떼","에스프레소","스타벅스","스벅","투썸","이디야","메가커피","컴포즈","빽다방","할리스","폴바셋","파스쿠찌","블루보틀","테라로사","더벤티","드립","콜드브루","디카페인","원두","핸드드립"]


@st.cache_data(show_spinner="인접 식음료 트렌드 준비 중...")
def build_adjacent_food_voc(uploaded_file):
    """커피·브랜드 무관 글 중 디저트·베이커리·카페푸드·식재료 VoC만 추출(트렌드 센싱용).
    브랜드 분석(v)과 완전 분리 — NSS·SOV 등에 절대 반영되지 않음."""
    if hasattr(uploaded_file, "seek"):
        try: uploaded_file.seek(0)
        except Exception: pass
    _name = getattr(uploaded_file, "name", str(uploaded_file))
    try:
        if _name.endswith((".csv", ".csv.gz", ".gz")):
            df = pd.read_csv(uploaded_file, encoding="utf-8-sig",
                             compression=("gzip" if _name.endswith(".gz") else "infer"))
        else:
            df = pd.read_excel(uploaded_file)
    except Exception:
        return pd.DataFrame()
    if "doc_id" not in df.columns:
        return pd.DataFrame()
    df = df[df["doc_id"].astype(str).str.match(r"^[a-f0-9]{12}$", na=False)].copy()

    def _gc(j):
        try:
            return " ".join(c.get("body", "") for c in json.loads(j)) if pd.notna(j) else ""
        except Exception:
            return ""
    df["comment_text"] = df["comments_json"].apply(_gc) if "comments_json" in df.columns else ""
    df["full_text"] = (df.get("title", pd.Series([""] * len(df))).fillna("").astype(str) + " " +
                       df.get("body", pd.Series([""] * len(df))).fillna("").astype(str) + " " +
                       df["comment_text"].astype(str))
    is_coffee = df["full_text"].apply(lambda t: any(k in t for k in _COFFEE_KW))
    if "brand_mentions" in df.columns:
        is_coffee = is_coffee | (df["brand_mentions"].notna() & df["brand_mentions"].astype(str).str.strip().ne(""))
    adj = df[~is_coffee].copy()
    adj["food_cats"] = adj["full_text"].apply(lambda t: [c for c, kws in FNB_CATS.items() if any(k in t for k in kws)])
    adj = adj[adj["food_cats"].apply(len) > 0].copy()

    def _senti(t):
        p = sum(1 for k in _FNB_POS if k in t); n = sum(1 for k in _FNB_NEG if k in t)
        return "긍정" if p > n else ("부정" if n > p else "중립")
    adj["sentiment"] = adj["full_text"].apply(_senti)
    adj["created_at"] = pd.to_datetime(adj["created_at"], errors="coerce")
    adj["year_month"] = adj["created_at"].dt.to_period("M").astype(str)
    return adj


@st.cache_data(show_spinner=False)
def compute_fnb_trends(_v_adj, sig=""):
    v_adj = _v_adj  # [v2.6.13] _v_adj(언더스코어)로 받아 해싱 스킵 — 리스트 컬럼 OOM 차단
    if v_adj is None or len(v_adj) == 0:
        return pd.DataFrame(), pd.DataFrame()
    months = sorted([m for m in v_adj["year_month"].dropna().unique() if m and m != "NaT"])
    recent = months[-1] if months else None
    base = months[:-1] if len(months) > 1 else months
    rows = []
    for cat, kws in FNB_CATS.items():
        for kw in kws:
            hit = v_adj["full_text"].str.contains(kw, regex=False, na=False)
            tot = int(hit.sum())
            if tot < 5:
                continue
            sub = v_adj[hit]
            rc = int((sub["year_month"] == recent).sum()) if recent else 0
            bc = sub[sub["year_month"].isin(base)].groupby("year_month").size() if base else pd.Series(dtype=int)
            base_avg = float(bc.mean()) if len(bc) else 0.0
            mom = round(rc / base_avg, 2) if base_avg > 0 else float(rc)
            pos = (sub["sentiment"] == "긍정").mean() * 100
            neg = (sub["sentiment"] == "부정").mean() * 100
            rows.append({"키워드": kw, "카테고리": cat, "총언급": tot, "최근월": rc,
                         "기준평균": round(base_avg, 1), "모멘텀": mom, "NSS": round(pos - neg, 1)})
    kw_df = (pd.DataFrame(rows).sort_values("모멘텀", ascending=False).reset_index(drop=True)
             if rows else pd.DataFrame())
    ex = v_adj.explode("food_cats")
    crows = []
    for cat, g in ex.groupby("food_cats"):
        pos = (g["sentiment"] == "긍정").mean() * 100
        neg = (g["sentiment"] == "부정").mean() * 100
        crows.append({"카테고리": cat, "건수": len(g), "긍정%": round(pos, 0),
                      "부정%": round(neg, 0), "NSS": round(pos - neg, 1)})
    cat_df = (pd.DataFrame(crows).sort_values("건수", ascending=False).reset_index(drop=True)
              if crows else pd.DataFrame())
    return kw_df, cat_df


_BEV_KW = ["아메리카노","카페라떼","라떼","콜드브루","콜드폼","아인슈페너","흑당","말차라떼","그린티라떼","스무디","에이드","프라페","프라푸치노","밀크티","버블티","크림라떼","디카페인","더치","플랫화이트","바닐라라떼","헤이즐넛","카푸치노","마키아토","모카","자몽","레몬에이드","유자","청귤","쑥라떼","곡물라떼","흑임자라떼","피스타치오라떼","딸기라떼","초코라떼","고구마라떼","아포가토","돌체","연유라떼","크림커피"]
MARKET_CATS = {"커피·음료": _BEV_KW, **FNB_CATS}
_COMBO_RE = r"같이|곁들|조합|꿀조합|섞어|넣어|추가해|레시피|만들어|만들 |커스텀|커스터마이|변형|응용|페어링|곁들여|찍어|발라|올려|토핑|믹스"


@st.cache_data(show_spinner="시장 트렌드 통합 데이터 준비 중...")
def build_market_trend_corpus(path, fsig="", period_from=""):
    """[v2.6.6] 트렌드 조기경보 전용 통합 코퍼스 = 커피 코어 + 인접 식음료.
    시장 전체(음료·푸드·식재료)를 폭넓게 조망하기 위한 트렌드 전용 레이어. 브랜드 지표엔 미반영.
    [v2.7.0] parquet·xz 지원, 반복 샘플링 행 제외, 추이 분석 플래그(_ts_ok) 부착."""
    try:
        df = _read_data_file(path)
    except Exception:
        return pd.DataFrame()
    if "doc_id" not in df.columns:
        return pd.DataFrame()
    df = df[df["doc_id"].astype(str).str.match(r"^[a-f0-9]{12}$", na=False)].copy()
    if "seed_season" in df.columns:
        df = df[~df["seed_season"].fillna("").astype(str).str.endswith(SAMPLER_TAG)].copy()
    if "created_at" not in df.columns:
        return pd.DataFrame()

    def _gc(j):
        try:
            return " ".join(c.get("body", "") for c in json.loads(j)) if pd.notna(j) else ""
        except Exception:
            return ""
    df["comment_text"] = df["comments_json"].apply(_gc) if "comments_json" in df.columns else ""
    df["full_text"] = (df.get("title", pd.Series([""] * len(df))).fillna("").astype(str) + " " +
                       df.get("body", pd.Series([""] * len(df))).fillna("").astype(str) + " " +
                       df["comment_text"].astype(str))

    df["market_cats"] = df["full_text"].apply(lambda t: [c for c, kws in MARKET_CATS.items() if any(k in t for k in kws)])
    corp = df[df["market_cats"].apply(len) > 0].copy()
    corp["_layer"] = corp["market_cats"].apply(lambda cs: "커피·음료" if "커피·음료" in cs else "푸드·식재료")

    def _senti(t):
        p = sum(1 for k in _FNB_POS if k in t); n = sum(1 for k in _FNB_NEG if k in t)
        return "긍정" if p > n else ("부정" if n > p else "중립")
    corp["sentiment"] = corp["full_text"].apply(_senti)
    corp = _attach_coverage(corp, compute_coverage(path, fsig, period_from))
    corp["created_at"] = _to_dt(corp["created_at"])
    corp["year_month"] = corp["created_at"].dt.to_period("M").astype(str)
    corp["_combo"] = corp["full_text"].str.contains(_COMBO_RE, regex=True, na=False)
    # [v2.7.0] 메모리 절감 — 트렌드 탭에서 쓰는 열만 유지
    _keep = ["doc_id", "title", "full_text", "created_at", "year_month", "sentiment", "market_cats",
             "_layer", "_combo", "author_id", "post_url", "source_name", "board_name",
             "_day", "_ts_ok", "_partial"]
    return corp[[c for c in _keep if c in corp.columns]].copy()


# ── [v2.7.0] 추이 분석 공통 규칙 ─────────────────────────────
#   ① 기간 전체를 빠짐없이 덮은 흐름의 글(_ts_ok)만 사용 (검색 상한 걸린 검색어·수집 당일 글 제외)
#   ② 월별 값은 '기간 안 날짜 수'로 나눠 30일 환산 (첫·마지막 부분 달 보정, 10일 미만 달은 제외)
def _ts_rows(df):
    if df is None or len(df) == 0:
        return df
    if "_ts_ok" in df.columns:
        return df[df["_ts_ok"]]
    return df[_to_dt(df["created_at"]).notna()]


def _month_days(win_start, win_end):
    """기간 안 월별 날짜 수 {YYYY-MM: 일수} (TS_MIN_MONTH_DAYS 미만 달 제외)."""
    try:
        rng = pd.date_range(pd.Timestamp(win_start), pd.Timestamp(win_end), freq="D")
    except Exception:
        return {}
    if len(rng) == 0:
        return {}
    cnt = pd.Series(1, index=rng).groupby(rng.to_period("M").astype(str)).sum()
    return {m: int(n) for m, n in cnt.items() if n >= TS_MIN_MONTH_DAYS}


def _norm_monthly(counts, mdays):
    """월별 건수(Series/dict) → 30일 환산 리스트 (mdays 월 순서)."""
    get = counts.get if hasattr(counts, "get") else (lambda k, d=0: d)
    return [round(float(get(m, 0)) / d * 30.0, 2) for m, d in sorted(mdays.items())]


def _period_bounds(win_start, win_end, recent_days=30, base_days=90):
    """최근 구간 [r0, we]와 비교 구간 [b0, b1] (비교 구간은 수집 시작일 이후로 자름)."""
    we = pd.Timestamp(win_end)
    r0 = we - pd.Timedelta(days=recent_days - 1)
    b1 = r0 - pd.Timedelta(days=1)
    b0 = max(r0 - pd.Timedelta(days=base_days), pd.Timestamp(win_start))
    return r0, we, b0, b1


def _recent_vs_base(day_series, win_start, win_end, recent_days=30, base_days=90):
    """최근 recent_days일 건수와, 그 이전 비교 구간 건수를 같은 일수로 환산한 값."""
    r0, we, b0, b1 = _period_bounds(win_start, win_end, recent_days, base_days)
    d = day_series.dropna()
    rc = int(((d >= r0) & (d <= we)).sum())
    bdays = max(1, (b1 - b0).days + 1)
    bc = int(((d >= b0) & (d <= b1)).sum())
    return rc, bc * recent_days / bdays


@st.cache_data(show_spinner=False)
def compute_market_trends(_corpus, sig=""):
    corpus = _corpus
    if corpus is None or len(corpus) == 0:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 0
    months = sorted([m for m in corpus["year_month"].dropna().unique() if m and m != "NaT"])
    recent = months[-1] if months else None
    base = months[:-1] if len(months) > 1 else months
    rows = []
    for cat, kws in MARKET_CATS.items():
        for kw in kws:
            hit = corpus["full_text"].str.contains(kw, regex=False, na=False)
            tot = int(hit.sum())
            if tot < 5:
                continue
            sub = corpus[hit]
            rc = int((sub["year_month"] == recent).sum()) if recent else 0
            bc = sub[sub["year_month"].isin(base)].groupby("year_month").size() if base else pd.Series(dtype=int)
            base_avg = float(bc.mean()) if len(bc) else 0.0
            mom = round(rc / base_avg, 2) if base_avg > 0 else float(rc)
            pos = (sub["sentiment"] == "긍정").mean() * 100
            neg = (sub["sentiment"] == "부정").mean() * 100
            rows.append({"키워드": kw, "카테고리": cat, "총언급": tot, "최근월": rc,
                         "기준평균": round(base_avg, 1), "모멘텀": mom, "NSS": round(pos - neg, 1)})
    kw_df = (pd.DataFrame(rows).sort_values("모멘텀", ascending=False).reset_index(drop=True)
             if rows else pd.DataFrame())
    ex = corpus.explode("market_cats")
    crows = []
    for cat, g in ex.groupby("market_cats"):
        pos = (g["sentiment"] == "긍정").mean() * 100
        neg = (g["sentiment"] == "부정").mean() * 100
        crows.append({"카테고리": cat, "건수": len(g), "긍정%": round(pos, 0),
                      "부정%": round(neg, 0), "NSS": round(pos - neg, 1)})
    cat_df = (pd.DataFrame(crows).sort_values("건수", ascending=False).reset_index(drop=True)
              if crows else pd.DataFrame())
    # 페어링: 변형·조합 글에서 음료×푸드 동시언급 상위
    from collections import Counter
    combo = corpus[corpus["_combo"]]
    food_kws = [k for c, ks in FNB_CATS.items() for k in ks]
    pc = Counter()
    for t in combo["full_text"].head(6000):
        bevs = [k for k in _BEV_KW if k in t][:3]
        foods = [k for k in food_kws if k in t][:3]
        for b in bevs:
            for f in foods:
                pc[(b, f)] += 1
    pair_df = (pd.DataFrame([{"음료": b, "푸드·식재료": f, "동시언급": n}
                            for (b, f), n in pc.most_common(15)]) if pc else pd.DataFrame())
    return kw_df, cat_df, pair_df, int(corpus["_combo"].sum())


def _spring_layout(node_ids, edges, iterations=90, seed=42):
    """의존성 없는 수동 force-directed 레이아웃(numpy). 원형 초기화 + 반발력 강화."""
    import numpy as np
    n = len(node_ids)
    if n == 0:
        return {}
    idx = {v: i for i, v in enumerate(node_ids)}
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
    pos = np.c_[np.cos(ang), np.sin(ang)] + np.random.default_rng(seed).normal(0, 0.02, (n, 2))
    W = np.zeros((n, n))
    for a, b, w in edges:
        if a in idx and b in idx:
            W[idx[a], idx[b]] = w
            W[idx[b], idx[a]] = w
    Wn = W / (W.max() if W.max() > 0 else 1.0)
    k = 2.2 / np.sqrt(n)
    temp = 0.30
    for it in range(iterations):
        disp = np.zeros((n, 2))
        for i in range(n):
            delta = pos[i] - pos
            dist = np.linalg.norm(delta, axis=1)
            dist[dist < 1e-3] = 1e-3
            rep = ((k * k / dist)[:, None]) * (delta / dist[:, None])
            rep[i] = 0
            disp[i] += rep.sum(axis=0)
            att = ((dist / k)[:, None] * delta) * (Wn[i][:, None])
            disp[i] -= att.sum(axis=0)
        d = np.linalg.norm(disp, axis=1)
        d[d < 1e-3] = 1e-3
        pos += (disp / d[:, None]) * np.minimum(d, temp)[:, None]
        temp *= 0.96
    pos -= pos.mean(0)
    mx = np.abs(pos).max()
    if mx > 0:
        pos /= mx
    return {v: pos[idx[v]] for v in node_ids}


def _kw_snippet(text, kw, win=55):
    """키워드가 등장한 위치 주변만 발췌(앞부분 cut 문제 해결)."""
    text = str(text)
    i = text.find(kw)
    if i < 0:
        return text[:110]
    s = max(0, i - win)
    e = min(len(text), i + len(kw) + win)
    snip = text[s:e].strip()
    return ("…" + snip if s > 0 else snip) + ("…" if e < len(text) else "")


def _kw_neighbor_sentiment(text, kw, win=40):
    """글 전체가 아니라 키워드 주변 문맥의 감성으로 판정(오귀속 방지)."""
    text = str(text)
    i = text.find(kw)
    window = text if i < 0 else text[max(0, i - win):min(len(text), i + len(kw) + win)]
    p = sum(1 for w in _FNB_POS if w in window)
    n = sum(1 for w in _FNB_NEG if w in window)
    return "긍정" if p > n else ("부정" if n > p else "중립")


@st.cache_data(show_spinner=False)
def compute_pairing_network(_corpus, sig=""):
    corpus = _corpus
    """페어링·변형 글에서 메뉴/식재료 동시언급 네트워크(노드=메뉴, 엣지=함께 등장)."""
    from collections import Counter
    from itertools import combinations
    if corpus is None or len(corpus) == 0:
        return pd.DataFrame(), []
    combo = corpus[corpus["_combo"]]
    allkw = [(kw, cat) for cat, kws in MARKET_CATS.items() for kw in kws]
    kw2cat = {kw: cat for kw, cat in allkw}
    kws_only = [kw for kw, _ in allkw]
    node_freq = Counter()
    pair = Counter()
    for t in combo["full_text"]:
        present = [kw for kw in kws_only if kw in t]
        present = list(dict.fromkeys(present))[:8]
        for kw in present:
            node_freq[kw] += 1
        for a, b in combinations(sorted(present), 2):
            pair[(a, b)] += 1
    if not pair:
        return pd.DataFrame(), []
    edges = [(a, b, w) for (a, b), w in pair.most_common(45) if w >= 2]
    nodeset = set()
    for a, b, w in edges:
        nodeset.add(a); nodeset.add(b)
    nodes = pd.DataFrame([{"키워드": k, "카테고리": kw2cat.get(k, "기타"), "빈도": node_freq[k]} for k in nodeset])
    return nodes, edges


_EMERGENT_HEADS = ["라떼", "아메리카노", "에스프레소", "콜드브루", "스무디", "에이드", "프라페", "밀크티",
                   "버블티", "쉐이크", "빙수", "젤라또", "치즈케이크", "케이크", "쿠키", "타르트", "푸딩",
                   "마카롱", "다쿠아즈", "마들렌", "휘낭시에", "스콘", "크로플", "와플", "도넛", "초콜릿",
                   "크림", "무스", "베이글", "크루아상", "바게트", "소금빵", "식빵", "토스트", "샌드위치",
                   "파니니", "샐러드", "요거트", "티라미수", "브륄레", "약과", "호떡", "꽈배기"]
_EMERGENT_CLASSIFIER = ["원두", "메뉴", "품종", "원산지", "로스팅", "블렌드"]
_EMERGENT_BLOCK = set(["여러번", "환불신청", "재방문", "한가지", "이번달", "지난번", "몇번", "처음으로"])


@st.cache_data(show_spinner=False)
def compute_emergent_terms(_corpus, sig="", win_start="", win_end=""):
    """[v2.6.10] 사전 비의존 미등록 급상승어 — F&B 머리어/분류어 패턴으로 식음료만 추출.
    [v2.7.0] 기간 전체를 덮는 글만 쓰고, 최근월·기준월을 30일 환산해 비교."""
    import numpy as np
    import re as _re
    from collections import Counter
    corpus = _ts_rows(_corpus)
    if corpus is None or len(corpus) == 0:
        return pd.DataFrame()
    mdays = _month_days(win_start, win_end)
    months = sorted(mdays)
    if len(months) < 2:
        return pd.DataFrame()
    recent = months[-1]
    base = months[:-1]
    known = set(k for kws in MARKET_CATS.values() for k in kws) | set(_EMERGENT_HEADS)
    heads = sorted(set(_EMERGENT_HEADS), key=len, reverse=True)
    suffix_re = _re.compile(r"[가-힣]{1,5}(?:" + "|".join(map(_re.escape, heads)) + r")")
    cls_re = _re.compile(r"([가-힣]{2,6})\s*(?:" + "|".join(_EMERGENT_CLASSIFIER) + r")")

    def extract(t):
        out = set()
        for tok in suffix_re.findall(t):
            if tok not in known and tok not in _EMERGENT_BLOCK:
                out.add((tok, "복합메뉴"))
        for w in cls_re.findall(t):
            if w and w not in known and w not in _EMERGENT_BLOCK and len(w) >= 2:
                out.add((w, "분류어인접"))
        return out

    rec = corpus[corpus["year_month"] == recent]
    cand = Counter(); cauth = {}; cpat = {}
    for t, au in zip(rec["full_text"], rec.get("author_id", pd.Series([""] * len(rec)))):
        for w, pat in extract(str(t)):
            cand[w] += 1
            cauth.setdefault(w, set()).add(au)
            cpat[w] = pat
    bc = {m: Counter() for m in base}
    for m in base:
        for t in corpus[corpus["year_month"] == m]["full_text"]:
            for w, pat in extract(str(t)):
                bc[m][w] += 1
    rows = []
    for w, c in cand.items():
        if c < 5 or len(cauth[w]) < 4:
            continue
        c30 = c / mdays[recent] * 30.0
        bavg = float(np.mean([bc[m].get(w, 0) / mdays[m] * 30.0 for m in base])) if base else 0.0
        mom = round(c30 / bavg, 1) if bavg > 0 else round(c30, 1)
        if mom < 2:
            continue
        rows.append({"신규어": w, "패턴": cpat[w], "최근월": c, "작성자수": len(cauth[w]),
                     "기준평균": round(bavg, 1), "모멘텀": mom})
    return pd.DataFrame(rows).sort_values("모멘텀", ascending=False).reset_index(drop=True) if rows else pd.DataFrame()


@st.cache_data(show_spinner=False)
def compute_market_es(_corpus, sig="", win_start="", win_end=""):
    """[v2.6.7] 통합 단일 ES 엔진 — 커피·음료/푸드/식재료를 동일 '메뉴 단위'로 ES 산출.
    볼륨·모멘텀·성장기울기·NSS를 결합한 ES점수 + 월별추이(_monthly). 브랜드 지표 미반영.
    [v2.7.0] 추이(볼륨·모멘텀·기울기·월별)는 기간 전체를 덮는 글만으로 30일 환산해 계산,
    NSS는 전체 글로 계산(비율 지표라 수집 상한 영향이 작음)."""
    import numpy as np
    full = _corpus
    corpus = _ts_rows(_corpus)
    mdays = _month_days(win_start, win_end)
    months = sorted(mdays)
    if corpus is None or len(corpus) == 0 or len(months) < 2:
        return pd.DataFrame(), months, 0.0
    recent = months[-1]
    base = months[:-1]
    rows = []
    for cat, kws in MARKET_CATS.items():
        for kw in kws:
            hit = corpus["full_text"].str.contains(kw, regex=False, na=False)
            tot = int(hit.sum())
            if tot < 8:
                continue
            sub = corpus[hit]
            mvals = _norm_monthly(sub.groupby("year_month").size(), mdays)
            mser = pd.Series(mvals, index=months)
            rc = float(mser.get(recent, 0))
            bvals = [float(mser.get(m, 0)) for m in base]
            bavg = float(np.mean(bvals)) if bvals else 0.0
            mom = round(rc / bavg, 2) if bavg > 0 else round(rc, 2)
            y = mser.values.astype(float)
            slope = float(np.polyfit(np.arange(len(y)), y, 1)[0]) if (len(y) >= 2 and y.sum() > 0) else 0.0
            fhit = full[full["full_text"].str.contains(kw, regex=False, na=False)]
            pos = (fhit["sentiment"] == "긍정").mean() * 100
            neg = (fhit["sentiment"] == "부정").mean() * 100
            rows.append({"메뉴": kw, "카테고리": cat, "볼륨": tot, "최근월": round(rc, 1),
                         "기준평균": round(bavg, 1), "모멘텀": mom, "성장기울기": round(slope, 2),
                         "NSS": round(pos - neg, 1), "_monthly": [round(float(x), 1) for x in mser.values]})
    if not rows:
        return pd.DataFrame(), months, 0.0
    df = pd.DataFrame(rows)

    def _n(x):
        x = x.astype(float); rng = x.max() - x.min()
        return (x - x.min()) / rng if rng > 0 else x * 0
    mom_n = _n(df["모멘텀"].clip(upper=df["모멘텀"].quantile(0.95)))
    slope_n = _n(df["성장기울기"].clip(lower=0))
    vol_n = _n(np.log1p(df["볼륨"]))
    nss_n = _n(df["NSS"])
    df["ES점수"] = (100 * (0.45 * mom_n + 0.25 * slope_n + 0.15 * vol_n + 0.15 * nss_n)).round(1)
    # 기준선(스테이플 아메리카노·라떼 월평균, 30일 환산) 대비 상대배수
    staple = corpus["full_text"].str.contains("아메리카노|라떼", regex=True, na=False)
    sm = pd.Series(_norm_monthly(corpus[staple].groupby("year_month").size(), mdays), index=months)
    baseline_avg = float(np.mean([sm.get(m, 0) for m in base])) if base else float(sm.mean())
    df["상대배수"] = (df["최근월"] / baseline_avg).round(2) if baseline_avg > 0 else df["최근월"].astype(float)
    _GROUP = {"커피·음료": "커피·음료", "디저트": "푸드류", "베이커리": "푸드류",
              "카페푸드": "푸드류", "식재료·플레이버": "식재료"}
    df["_group"] = df["카테고리"].map(_GROUP).fillna("기타")

    def _alert(r):
        if r["모멘텀"] >= 1.5 and r["성장기울기"] > 0:
            return "성장 조짐"
        if r["모멘텀"] < 0.8 or r["성장기울기"] < -0.3:
            return "둔화"
        return "안정"
    df["경보"] = df.apply(_alert, axis=1)
    df = df.sort_values("ES점수", ascending=False).reset_index(drop=True)
    return df, months, round(baseline_avg, 1)


SOV_RATIO_MIN = 30   # 브랜드 비율(품질·감성) 추정에 sov 레이어 표본이 이보다 적으면 블로그 전체 표본 사용


@st.cache_data(show_spinner="브랜드 지표 계산 중...")
def compute_brand_stats(_vall, sig="", _summary=None, use_blog=True, use_comm=True):
    """[v2.7.0] 브랜드 언급량·감성·SOV (수집 한계 보정).
    · 커뮤니티: 게시판 전체를 훑어 모은 실측 건수 그대로.
    · 블로그: 네이버 검색이 검색어당 최신 1,000건까지만 줘서 수집 건수가 실제 규모를 반영하지 못함.
      → sov_summary의 6개월 환산 언급량(blog_est_6m)에, 그 브랜드 표본에서 잰
        '선택한 품질 필터 통과 비율'과 '긍정·부정 비율'을 곱해 추정.
      sov_summary가 없으면 수집 건수를 그대로 쓰고 '보정 전'으로 표시.
    _vall: 필터 적용 전 전체 데이터 (_inlens = 현재 소스·품질 필터 통과 여부)."""
    vall = _vall
    est_map = {}
    if _summary is not None and use_blog:
        for _, r in _summary.iterrows():
            val = pd.to_numeric(r.get("blog_est_6m"), errors="coerce")
            if pd.notna(val) and float(val) >= 0:
                est_map[str(r["brand"])] = float(val)
    is_blog = vall["_src"].eq("블로그")
    is_comm = vall["_src"].eq("커뮤니티")
    inlens = vall["_inlens"].astype(bool)
    layer = (vall["collection_layer"].fillna("").astype(str) if "collection_layer" in vall.columns
             else pd.Series("", index=vall.index))
    is_pos = vall["sentiment"].eq("긍정")
    is_neg = vall["sentiment"].eq("부정")
    rows = []
    for b in TARGET_BRANDS:
        hasb = vall["brands"].apply(lambda x: b in x)
        samp_mask = hasb & inlens & ((is_blog & use_blog) | (is_comm & use_comm))
        n_samp = int(samp_mask.sum())
        if n_samp < 3:
            continue
        c_mask = hasb & inlens & is_comm if use_comm else pd.Series(False, index=vall.index)
        c_n, c_pos, c_neg = int(c_mask.sum()), int((c_mask & is_pos).sum()), int((c_mask & is_neg).sum())
        b_n = b_pos = b_neg = 0.0
        how = "실측" if not use_blog else "보정 전"
        if use_blog:
            braw = hasb & is_blog
            if b in est_map and braw.any():
                S = braw & layer.eq("sov")
                if int(S.sum()) < SOV_RATIO_MIN:
                    S = braw
                S_l = S & inlens
                ns, nl = int(S.sum()), int(S_l.sum())
                r_lens = nl / ns if ns else 0.0
                b_n = est_map[b] * r_lens
                b_pos = b_n * (int((S_l & is_pos).sum()) / nl if nl else 0.0)
                b_neg = b_n * (int((S_l & is_neg).sum()) / nl if nl else 0.0)
                how = "6개월 환산"
            else:
                bl = braw & inlens
                b_n, b_pos, b_neg = float(bl.sum()), float((bl & is_pos).sum()), float((bl & is_neg).sum())
        n = b_n + c_n
        if n <= 0:
            continue
        pos, neg = b_pos + c_pos, b_neg + c_neg
        rows.append({
            "브랜드": b, "_n": n, "_pos": pos, "_neg": neg,
            "언급량": int(round(n)), "긍정": int(round(pos)), "부정": int(round(neg)),
            "중립": int(round(n - pos - neg)),
            "긍정률": round(pos / n * 100, 1), "부정률": round(neg / n * 100, 1),
            "NSS": round((pos - neg) / n * 100, 1),
            "블로그": int(round(b_n)), "커뮤니티": int(c_n), "표본수": n_samp, "산출": how,
        })
    df = pd.DataFrame(rows)
    if len(df) == 0:
        return pd.DataFrame(columns=["브랜드", "언급량", "긍정", "부정", "중립", "긍정률", "부정률", "NSS",
                                     "SOV_전체", "SOV_긍정", "SOV_부정", "블로그", "커뮤니티", "표본수", "산출"])
    tn, tp, tg = df["_n"].sum(), df["_pos"].sum(), df["_neg"].sum()
    df["SOV_전체"] = (df["_n"] / tn * 100).round(1) if tn > 0 else 0.0
    df["SOV_긍정"] = (df["_pos"] / tp * 100).round(1) if tp > 0 else 0.0
    df["SOV_부정"] = (df["_neg"] / tg * 100).round(1) if tg > 0 else 0.0
    return df.drop(columns=["_n", "_pos", "_neg"])


@st.cache_data(show_spinner="월별 NSS 계산 중...")
def compute_monthly_nss(_v, sig="", win_start="", win_end=""):
    """[v2.7.0] 월별 NSS — 기간 전체를 덮는 글만 사용, 브랜드·월 표본 NSS_MIN_N건 이상만 표시."""
    tv = _ts_rows(_v)
    months = sorted(_month_days(win_start, win_end))
    rows = []
    if tv is None or len(tv) == 0:
        return pd.DataFrame(columns=["브랜드", "월", "NSS", "문서수"]), months
    for b in TARGET_BRANDS:
        bd = tv[tv["brands"].apply(lambda x: b in x)]
        for m in months:
            sub = bd[bd["year_month"] == m]
            t = len(sub)
            if t < NSS_MIN_N:
                continue
            p = (sub["sentiment"] == "긍정").sum()
            n = (sub["sentiment"] == "부정").sum()
            rows.append({"브랜드": b, "월": m, "NSS": round((p - n) / t * 100, 1), "문서수": t})
    return pd.DataFrame(rows, columns=["브랜드", "월", "NSS", "문서수"]), months

@st.cache_data(show_spinner="속성 드라이버 분석 중...")
def compute_absa(_v, sig=""):
    pos_kw = ["맛있","좋아","좋다","추천","최고","만족","친절","합리","가성비","저렴","달콤","훌륭"]
    neg_kw = ["맛없","별로","실망","불만","최악","비싸","불친절","느리","아쉽","안좋","싫","불매","후회","환불"]
    rows = []
    for attr, kws in ATTR_DICT.items():
        pat  = "|".join(kws)
        mask = _v["full_text"].str.contains(pat, na=False)
        sub  = _v[mask]
        if len(sub) < 3:
            continue
        s   = sub["sentiment"].value_counts()
        tot = len(sub)
        pos = s.get("긍정", 0)
        neg = s.get("부정", 0)
        rows.append({
            "속성":    attr, "문서수": tot,
            "긍정":   int(pos), "부정": int(neg),
            "긍정률": round(pos / tot * 100, 1),
            "부정률": round(neg / tot * 100, 1),
            "NSS":    round((pos - neg) / tot * 100, 1),
        })
    if not rows:
        return pd.DataFrame(columns=["속성", "문서수", "긍정", "부정", "긍정률", "부정률", "NSS"])
    return pd.DataFrame(rows).sort_values("NSS", ascending=False)

# [v2.7.0] 토픽·군집 모델은 고정 시드 표본(최대 MODEL_FIT_MAX건)으로 학습하고,
#          전체 문서는 학습된 모델로 분류만 한다 → 8만 건 기준 첫 로딩 3분 이상 → 수십 초.
#          토픽 비중·문서 수·브랜드 분포는 그대로 전체 문서 기준.
MODEL_FIT_MAX = 8000


def _fit_idx(n, cap=MODEL_FIT_MAX, seed=42):
    if n <= cap:
        return np.arange(n)
    return np.sort(np.random.default_rng(seed).choice(n, size=cap, replace=False))


@st.cache_data(show_spinner="LDA 토픽 모델링 중...")
def compute_lda(_v, sig=""):
    docs = _v[_v["tokens_str"].str.len() > 5]["tokens_str"].tolist()
    if len(docs) < 20:
        return None, None, None, None, None
    tfidf = TfidfVectorizer(max_features=500, min_df=2, max_df=0.85,
                             token_pattern=r"[가-힣]{2,6}",
                             stop_words=list(MEANINGLESS_MODIFIERS))
    X     = tfidf.fit_transform(docs)
    vocab = tfidf.get_feature_names_out()
    lda   = LatentDirichletAllocation(n_components=7, random_state=42,
                                       max_iter=30, learning_method="batch")
    lda.fit(X[_fit_idx(X.shape[0])])
    doc_t    = lda.transform(X)
    topic_dist = doc_t.mean(axis=0)
    if hasattr(tfidf, "stop_words_"):   # 제외 어휘 목록(수십만 개)은 캐시 크기만 키우므로 비움
        tfidf.stop_words_ = None
    return lda, tfidf, vocab, doc_t, topic_dist

CA_STOP = {
    "때문에","보고","있습니다","같습니다","합니다","입니다","였습니다","됩니다","했습니다","드립니다",
    "그리고","하지만","그래서","그런데","근데","해서","하고","에서","으로","까지","부터","보면","보니",
    "대한","대해","관련","위해","통해","따라","정도","경우","생각","약간","정말","너무","완전","많이","조금",
    "이라고","라고","처럼","만큼","에게","우리","저는","제가","그냥","이거","저거","요즘","내가",
    "커피를","커피는","커피가","맛이","마시","마셔","먹고","가서","있는","없는","같이","위해서",
    "라떼","아메리카노","음료","메뉴","그리고요","근데요","했는데","하는데","인데","그게","이게","저게"}
_CA_END = ("습니다", "됩니다", "입니다", "였습니다", "때문에", "이라고", "라고요",
           "하는데", "있는데", "면서", "거나", "지만", "어서요", "아서요")


def _ca_meaningful(w):
    if (w in STOPWORDS or w in MEANINGLESS_MODIFIERS or w in CA_STOP or len(w) < 2):
        return False
    if w.endswith(_CA_END):
        return False
    return True


# [v2.7.0] 급증 키워드·토픽 이름용 엄격 필터 — 서술어 활용형(…했는데, …보이네요, …좋아요)까지 제외
_VERB_END = ("는데", "은데", "던데", "네요", "어요", "아요", "여요", "해요", "에요", "예요", "까요", "을까", "할까",
             "더라", "거든", "잖아", "군요", "구요", "고요", "었다", "았다", "였다", "했다", "니다", "세요",
             "해서", "어서", "아서", "라서", "면서", "지만", "는지", "니까")
# 토픽 이름에 쓰지 않을 브랜드·상호 (비교군 + 제외 브랜드 + 생활 브랜드)
_OTHER_BRAND_WORDS = ("파리바게뜨", "파바", "뚜레쥬르", "뚜쥬", "던킨", "크리스피", "엔제리너스", "엔제리",
                      "배스킨", "배라", "맥도날드", "버거킹", "롯데리아", "올리브영", "다이소", "무신사",
                      "쿠팡", "이마트", "코스트코", "스벅", "투썸", "컴포즈", "빽다방", "메가커피", "이디야",
                      "할리스", "폴바셋", "테라로사", "블루보틀", "더벤티", "파스쿠찌")


def _kw_meaningful(w):
    return _ca_meaningful(w) and not w.endswith(_VERB_END)


def _is_brand_word(w):
    wl = str(w).lower()
    return (any(a in wl for als in BRAND_ALIASES.values() for a in als)
            or any(b in wl for b in _OTHER_BRAND_WORDS))


@st.cache_data(show_spinner="대응일치분석 계산 중...")
def compute_ca(_v, sig=""):
    excl = {"커피","카페","스벅","스타벅스","있는","하는","그런","이런","같은","근데","이제",
            "맛이","커피를","커피는","커피가","카페에서","라떼","있고","없는","없고","것도","해서","있어서"}
    all_toks = _v["tokens_str"].str.cat(sep=" ").split()
    top_kws  = [w for w, _ in Counter(all_toks).most_common(260)
                if w not in excl and _ca_meaningful(w)][:40]
    ca_brands = [b for b in TARGET_BRANDS
                 if _v["brands"].apply(lambda x: b in x).sum() >= 5]
    if len(ca_brands) < 2:
        return None
    cont = pd.DataFrame(0, index=ca_brands, columns=top_kws)
    for b in ca_brands:
        bd  = _v[_v["brands"].apply(lambda x: b in x)]
        cnt = Counter(bd["tokens_str"].str.cat(sep=" ").split())
        for kw in top_kws:
            cont.loc[b, kw] = cnt.get(kw, 0)
    N_ca = cont.values.astype(float) + 0.5
    r_ca = N_ca.sum(axis=1); c_ca = N_ca.sum(axis=0); tot = N_ca.sum()
    P    = N_ca / tot; rv = r_ca / tot; cv = c_ca / tot
    Dr   = np.diag(1 / np.sqrt(rv)); Dc = np.diag(1 / np.sqrt(cv))
    S    = Dr @ (P - np.outer(rv, cv)) @ Dc
    U, sigma, Vt = la.svd(S, full_matrices=False)
    row_c = Dr @ U[:, :2] * sigma[:2]
    col_c = Dc @ Vt[:2, :].T
    expl  = sigma[:2] ** 2 / (sigma ** 2).sum() * 100
    return {"brands": ca_brands, "row_x": row_c[:, 0], "row_y": row_c[:, 1],
            "col_x": col_c[:, 0], "col_y": col_c[:, 1],
            "kws": top_kws, "expl": expl, "cont": cont}

BURST_RECENT_DAYS, BURST_BASE_DAYS = 30, 90


@st.cache_data(show_spinner="Burst 탐지 중...")
def compute_burst(_v, sig="", win_start="", win_end=""):
    """[v2.7.0] 최근 30일 vs 직전 90일(30일로 환산) 키워드 증가율.
    연도를 고정해 비교하던 방식(2026 최근 2개월 vs 2025 3개월)을 수집 기간 기준으로 바꾸고,
    기간 전체를 덮는 글만 사용 (검색 상한 때문에 최근 글만 담긴 검색어가 '급증'으로 보이는 착시 방지)."""
    cols = ["키워드", "최근30일", "직전(30일 환산)", "증가율(배)"]
    tv = _ts_rows(_v)
    if tv is None or len(tv) == 0 or not win_end:
        return pd.DataFrame(columns=cols)
    r0, we, b0, b1 = _period_bounds(win_start, win_end, BURST_RECENT_DAYS, BURST_BASE_DAYS)
    if b1 < b0:
        return pd.DataFrame(columns=cols)
    bdays = (b1 - b0).days + 1
    d = tv["_day"]
    rec = tv[(d >= r0) & (d <= we)]
    r_cnt = Counter(rec["tokens_str"].str.cat(sep=" ").split())
    p_cnt = Counter(tv[(d >= b0) & (d <= b1)]["tokens_str"].str.cat(sep=" ").split())
    rows = []
    for kw, cnt in r_cnt.most_common(600):
        if (kw in STOPWORDS or kw in MEANINGLESS_MODIFIERS or len(kw) < 2 or cnt < 5
                or not _kw_meaningful(kw)):
            continue
        prev30 = p_cnt.get(kw, 0) * BURST_RECENT_DAYS / bdays
        rows.append({"키워드": kw, "최근30일": int(cnt), "직전(30일 환산)": round(prev30, 1),
                     "증가율(배)": round(cnt / (prev30 + 1), 1)})
    if not rows:
        return pd.DataFrame(columns=cols + ["부정비중", "긍정비중"])
    out = pd.DataFrame(rows, columns=cols).sort_values("증가율(배)", ascending=False).head(20)
    # 최근 구간에서 그 키워드가 든 글의 감성 비중 → 위험 신호 판정에 사용
    neg, pos = [], []
    for kw in out["키워드"]:
        hit = rec[rec["tokens_str"].str.contains(kw, regex=False, na=False)]
        n = max(len(hit), 1)
        neg.append(round((hit["sentiment"] == "부정").sum() / n * 100, 1))
        pos.append(round((hit["sentiment"] == "긍정").sum() / n * 100, 1))
    out["부정비중"], out["긍정비중"] = neg, pos
    return out

@st.cache_data(show_spinner="PMI 계산 중...")
def compute_pmi(_v, sig=""):
    N  = len(_v)
    bd = {b: set(_v[_v["brands"].apply(lambda x: b in x)].index) for b in TARGET_BRANDS}
    rows = []
    for i, b1 in enumerate(TARGET_BRANDS):
        for b2 in TARGET_BRANDS[i + 1:]:
            co  = len(bd.get(b1, set()) & bd.get(b2, set()))
            p1  = len(bd.get(b1, set())) / N
            p2  = len(bd.get(b2, set())) / N
            pco = co / N
            pmi = round(np.log2(pco / (p1 * p2) + 1e-9), 2) if pco > 0 else -99
            rows.append({"브랜드1": b1, "브랜드2": b2, "공출현수": co, "PMI": pmi})
    return pd.DataFrame(rows).sort_values("PMI", ascending=False)

# ══════════════════════════════════════════════════════
# 4대 고도화 분석 함수
# ══════════════════════════════════════════════════════

# ── 고도화 A: 브랜드 로열티(찐팬) 지수 ──────────────────
LOYALTY_SIGNALS = [
    ("독점 충성", ["여기 아니면", "무조건", "만 먹", "만 마셔", "만 가", "아니면 안", "밖에 안"], 3.0),
    ("강한 애착", ["최애", "푹 빠졌", "단골", "사랑", "진심", "믿고", "인생", "내 최애"], 2.0),
    ("반복 소비", ["자주", "매일", "또 갔", "또 가", "재방문", "늘 먹", "맨날", "항상"], 1.0),
]

@st.cache_data(show_spinner="브랜드 로열티 지수 계산 중...")
def compute_loyalty(_v, sig=""):
    def loyalty_score_of_doc(text):
        t = str(text)
        for name, kws, w in LOYALTY_SIGNALS:
            if any(k in t for k in kws):
                return w
        return 0.0
    def loyalty_tier_of_doc(text):
        t = str(text)
        for name, kws, w in LOYALTY_SIGNALS:
            if any(k in t for k in kws):
                return name
        return "일반"
    rows = []
    for b in TARGET_BRANDS:  # [v2.5.1] 파스쿠찌 중복 제거(이미 포함)
        bd = _v[_v["brands"].apply(lambda x: b in x)]
        n = len(bd)
        if n < 3:
            continue
        scores = bd["full_text"].apply(loyalty_score_of_doc)
        tiers  = bd["full_text"].apply(loyalty_tier_of_doc)
        fan_docs = int((scores > 0).sum())
        loyalty_idx = round(scores.mean() / 3 * 100, 1)
        fan_ratio   = round(fan_docs / n * 100, 1)
        tier_counts = tiers.value_counts()
        # NSS도 함께
        pos = (bd["sentiment"] == "긍정").sum()
        neg = (bd["sentiment"] == "부정").sum()
        nss = round((pos - neg) / n * 100, 1)
        rows.append({
            "브랜드": b, "언급량": n,
            "로열티지수": loyalty_idx,
            "찐팬비율": fan_ratio,
            "찐팬문서수": fan_docs,
            "독점충성": int(tier_counts.get("독점 충성", 0)),
            "강한애착": int(tier_counts.get("강한 애착", 0)),
            "반복소비": int(tier_counts.get("반복 소비", 0)),
            "NSS": nss,
        })
    if not rows:
        return pd.DataFrame(columns=["브랜드", "언급량", "로열티지수", "찐팬비율", "찐팬문서수",
                                     "독점충성", "강한애착", "반복소비", "NSS"])
    return pd.DataFrame(rows).drop_duplicates("브랜드").sort_values("로열티지수", ascending=False)


# ── 고도화 B: 소비맥락 세분화 (15유형) ──────────────────
OCCASION_DETAILED = {
    "집중 카공":     ["카공", "공부", "노트북", "콘센트", "집중", "과제"],
    "그룹 스터디":   ["스터디", "팀플", "모임공부", "같이공부"],
    "업무 미팅":     ["미팅", "회의", "업무", "비즈니스", "외근"],
    "친구 수다":     ["친구", "수다", "만나", "웃긴", "친구들"],
    "데이트":        ["데이트", "커플", "남친", "여친", "기념일"],
    "가족 나들이":   ["가족", "부모님", "아이", "엄마", "아빠", "애들"],
    "혼카페 힐링":   ["혼자", "혼카", "힐링", "멍때", "여유"],
    "책읽기·사색":   ["책", "독서", "읽기"],
    "아침·출근":     ["출근", "아침", "모닝", "등굣"],
    "테이크아웃":    ["테이크아웃", "포장", "픽업", "들고"],
    "드라이브":      ["드라이브", "차에서", "드스루"],
    "디저트 타임":   ["디저트", "케이크", "달달", "당충전"],
    "선물·기프티콘": ["선물", "기프티콘", "상품권", "기프트"],
    "배달·홈카페":   ["배달", "집에서", "홈카페", "캡슐"],
    "여행·나들이":   ["여행", "나들이", "바다", "놀러"],
}

@st.cache_data(show_spinner="소비맥락 세분화 분석 중...")
def compute_occasion_detailed(_v, sig=""):
    rows = []
    for oc, kws in OCCASION_DETAILED.items():
        pat = "|".join(kws)
        mask = _v["full_text"].str.contains(pat, na=False)
        sub  = _v[mask]
        n = len(sub)
        if n < 2:
            continue
        pos = (sub["sentiment"] == "긍정").sum()
        neg = (sub["sentiment"] == "부정").sum()
        nss = round((pos - neg) / n * 100, 1)
        rows.append({"소비맥락": oc, "언급량": int(n), "긍정률": round(pos/n*100,1),
                     "NSS": nss})
    if not rows:
        return pd.DataFrame(columns=["소비맥락", "언급량", "긍정률", "NSS"])
    return pd.DataFrame(rows).sort_values("언급량", ascending=False)

@st.cache_data(show_spinner="맥락 × 브랜드 교차 분석 중...")
def compute_occasion_brand_matrix(_v, sig=""):
    occ_list = list(OCCASION_DETAILED.keys())
    mat = pd.DataFrame(0, index=occ_list, columns=TARGET_BRANDS)
    for oc, kws in OCCASION_DETAILED.items():
        pat = "|".join(kws)
        oc_docs = _v[_v["full_text"].str.contains(pat, na=False)]
        for b in TARGET_BRANDS:
            mat.loc[oc, b] = int(oc_docs["brands"].apply(lambda x: b in x).sum())
    return mat


_TOPIC_THEMES = [
    ("가격·가성비", ["가격", "비싸", "저렴", "가성비", "할인", "쿠폰", "인상", "원가", "천원"]),
    ("디카페인·건강", ["디카페인", "디카페", "카페인", "건강", "임산부", "저당", "제로", "당뇨"]),
    ("맛·원두품질", ["맛있", "원두", "에스프레소", "산미", "고소", "진한", "드립", "로스팅", "바디감"]),
    ("카페공간·작업", ["공부", "카공", "노트북", "작업", "공간", "분위기", "좌석", "콘센트", "인테리어", "매장"]),
    ("디저트·베이커리", ["케이크", "디저트", "마카롱", "베이커리", "쿠키", "소금빵", "티라미수", "도넛", "케익"]),
    ("선물·기프티콘", ["선물", "기프티콘", "생일", "상품권", "교환권", "기프트"]),
    ("굿즈·프로모션", ["굿즈", "이벤트", "프로모션", "텀블러", "다이어리", "증정", "프리퀀시", "적립"]),
    ("신메뉴·시즌", ["신메뉴", "출시", "시즌", "한정", "가을", "겨울", "여름", "크리스마스"]),
    ("불매·이슈", ["불매", "이슈", "논란", "환불", "사과", "정치"]),
    ("브랜드 비교·추천", ["추천", "비교", "고민", "대신", "차라리", "어디가"]),
]


def _label_topics(words_list):
    """[v2.7.0] 토픽 키워드로 이름 자동 부여 (테마 사전과 겹치는 정도로 배정, 중복 없이). 맞는 테마가 없으면 상위 키워드 2개."""
    scores = []
    for ti, ws in enumerate(words_list):
        ws = [w for w in ws if not _is_brand_word(w)]
        for th, kws in _TOPIC_THEMES:
            sc = sum((len(ws) - r) for r, w in enumerate(ws) if any(k in w for k in kws))
            if sc > 0:
                scores.append((sc, ti, th))
    labels, used = {}, set()
    for sc, ti, th in sorted(scores, reverse=True):
        if ti in labels or th in used:
            continue
        labels[ti] = th
        used.add(th)
    _generic = {"커피", "카페", "음료", "메뉴", "후기", "오늘", "방문", "리뷰", "포스팅", "블로그", "사진"}

    def _fallback(i, ws):
        nb = [w for w in ws if not _is_brand_word(w) and _kw_meaningful(w) and w not in _generic]
        if len(nb) >= 2:
            return "·".join(nb[:2])
        if len(nb) == 1:
            return nb[0] + " 중심"
        return "브랜드 언급 중심" if ws else f"토픽{i + 1}"
    return [labels.get(i) or _fallback(i, ws) for i, ws in enumerate(words_list)]


# ── 고도화 C: LDA 토픽 클러스터링 (토픽×브랜드 중첩) ─────
@st.cache_data(show_spinner="토픽 클러스터링 중...")
def compute_topic_clustering(_v, sig=""):
    sub = _v[_v["tokens_str"].str.len() > 5].copy().reset_index(drop=True)
    if len(sub) < 20:
        return None
    tfidf = TfidfVectorizer(max_features=300, min_df=2, max_df=0.85,
                             token_pattern=r"[가-힣]{2,6}",
                             stop_words=list(MEANINGLESS_MODIFIERS))
    X = tfidf.fit_transform(sub["tokens_str"])
    vocab = tfidf.get_feature_names_out()
    n_topics = 6  # [v2.3.1] 4~5개 → 6개 세분화
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42, max_iter=20)
    lda.fit(X[_fit_idx(X.shape[0])])          # [v2.7.0] 표본 학습 → 전체 문서 분류
    doc_topics = lda.transform(X)
    sub["main_topic"] = doc_topics.argmax(axis=1)

    topic_words = []
    for t in range(n_topics):
        top_idx = lda.components_[t].argsort()[-8:][::-1]
        topic_words.append([vocab[i] for i in top_idx])

    # 토픽 × 브랜드 매트릭스
    tb_mat = pd.DataFrame(0, index=[f"T{i}" for i in range(n_topics)], columns=TARGET_BRANDS)
    for t in range(n_topics):
        t_docs = sub[sub["main_topic"] == t]
        for b in TARGET_BRANDS:
            tb_mat.loc[f"T{t}", b] = int(t_docs["brands"].apply(lambda x: b in x).sum())

    # 토픽 × 감성
    ts_mat = pd.DataFrame(0, index=[f"T{i}" for i in range(n_topics)], columns=["긍정","중립","부정"])
    for t in range(n_topics):
        t_docs = sub[sub["main_topic"] == t]
        for s in ["긍정","중립","부정"]:
            ts_mat.loc[f"T{t}", s] = int((t_docs["sentiment"] == s).sum())

    # [항목 6] 토픽 의미 자동 정의 (키워드 기반 규칙)
    def define_topic_meaning(words):
        ws = " ".join(words)
        if any(k in ws for k in ["디카페인","디카페","카페인","건강","임산부"]):
            return "건강·디카페인 니즈"
        if any(k in ws for k in ["가격","비싸","불매","환불","쿠폰","할인"]):
            return "가격·이슈 담론"
        if any(k in ws for k in ["맛있","맛","원두","에스프레소","향","진한"]):
            return "맛·품질 평가"
        if any(k in ws for k in ["공부","카공","노트북","작업","공간","분위기"]):
            return "카페 공간·작업"
        if any(k in ws for k in ["추천","후기","어디","비교","고민"]):
            return "브랜드 탐색·비교"
        if any(k in ws for k in ["케이크","디저트","빵","마카롱","베이커리"]):
            return "디저트·베이커리"
        if any(k in ws for k in ["선물","기프티콘","생일","굿즈"]):
            return "선물·기프트"
        return "일상 카페 소비"

    # [항목 6] 토픽별 주요 소비자 유형(소비맥락 기반)
    # [v2.7.0] 키워드 기반 자동 명명 (중복 이름 방지)
    topic_meanings = _label_topics(topic_words)
    topic_occasions = []
    for t in range(n_topics):
        t_docs = sub[sub["main_topic"] == t]
        if "occasion" in t_docs.columns and len(t_docs) > 0:
            occ_top = t_docs["occasion"].value_counts().head(2).index.tolist()
        else:
            occ_top = []
        topic_occasions.append(occ_top)

    # 토픽별 대표 브랜드
    topic_brands = []
    for t in range(n_topics):
        t_docs = sub[sub["main_topic"] == t]
        tb = Counter(b for bs in t_docs["brands"] for b in bs)
        topic_brands.append([b for b, _ in tb.most_common(3)])

    return {
        "n_topics": n_topics, "topic_words": topic_words,   # [v2.7.0] 미사용 문서 사본(sub·doc_topics)은 캐시에 남기지 않음
        "tb_mat": tb_mat, "ts_mat": ts_mat,
        "topic_sizes": [int((sub["main_topic"]==t).sum()) for t in range(n_topics)],
        "topic_meanings": topic_meanings,
        "topic_labels": topic_meanings,
        "topic_occasions": topic_occasions,
        "topic_brands": topic_brands,
    }


# ── 고도화 D: 상대평가 트렌드 조기경보 ──────────────────
BASELINE_PRODUCTS = ["아메리카노", "라떼", "아이스아메리카노", "아아"]
EMERGING_CANDIDATES = {
    "디카페인": ["디카페인", "디카페"],
    "말차·녹차": ["말차", "녹차라떼"],
    "크림치즈": ["크림치즈"],
    "소금빵": ["소금빵"],
    "피스타치오": ["피스타치오", "피스타"],
    "오트밀크": ["오트밀크", "오트라떼", "귀리"],
    "흑임자·전통": ["흑임자", "미숫가루", "콩가루"],
    "콜드브루": ["콜드브루", "콜브"],
    "티라미수": ["티라미수"],
    "두바이초콜릿": ["두바이", "카다이프"],
    "크로플": ["크로플"],
    "유자·시트러스": ["유자", "레몬"],
    "바스크치즈": ["바스크"],
    "흑당": ["흑당", "버블티"],
}

@st.cache_data(show_spinner="트렌드 조기경보 계산 중...")
def compute_trend_earlywarning(_v):
    months = sorted([m for m in _v["year_month"].dropna().unique()
                     if "NaT" not in str(m) and ("2025" in str(m) or "2026" in str(m))])
    if len(months) < 3:
        return None

    # 기준선: 안정 제품군 월평균 언급량
    baseline_monthly = []
    for m in months:
        sub = _v[_v["year_month"] == m]
        cnt = sub["full_text"].apply(lambda t: any(b in str(t) for b in BASELINE_PRODUCTS)).sum()
        baseline_monthly.append(int(cnt))
    baseline_avg = np.mean(baseline_monthly) if baseline_monthly else 1
    if baseline_avg < 1:
        baseline_avg = 1

    rows = []
    for prod, kws in EMERGING_CANDIDATES.items():
        pat = "|".join(kws)
        monthly = []
        for m in months:
            sub = _v[_v["year_month"] == m]
            monthly.append(int(sub["full_text"].str.contains(pat, na=False).sum()))
        total = sum(monthly)
        if total < 2:
            continue
        recent = np.mean(monthly[-2:]) if len(monthly) >= 2 else 0
        rel_ratio = round(recent / baseline_avg, 2)
        # 가속도 (최근 4개월 기울기)
        if len(monthly) >= 3:
            tail = monthly[-4:] if len(monthly) >= 4 else monthly
            x = np.arange(len(tail))
            slope = round(float(np.polyfit(x, tail, 1)[0]), 2) if len(set(tail)) > 1 else 0.0
        else:
            slope = 0.0
        # 브랜드 확산도
        prod_docs = _v[_v["full_text"].str.contains(pat, na=False)]
        brand_spread = len(set(b for bs in prod_docs["brands"] for b in bs))
        # 감성
        pos = (prod_docs["sentiment"] == "긍정").sum()
        neg = (prod_docs["sentiment"] == "부정").sum()
        nss = round((pos - neg) / max(len(prod_docs),1) * 100, 1)
        # Emerging Signal Score
        es = round(rel_ratio * 10 + slope * 5 + brand_spread * 2, 1)
        # 경보 등급
        if rel_ratio >= 0.8 and slope > 0:
            alert = "🚨 강한 신호"
        elif slope > 0.5:
            alert = "📈 성장 조짐"
        elif slope < -0.5:
            alert = "📉 둔화"
        else:
            alert = "➡️ 안정"
        rows.append({
            "제품·식재료": prod, "총언급": total,
            "상대배수": rel_ratio, "성장기울기": slope,
            "브랜드확산": brand_spread, "NSS": nss,
            "ES점수": es, "경보": alert, "_monthly": monthly,
        })
    result_df = pd.DataFrame(rows).sort_values("ES점수", ascending=False)
    # 트렌드 카테고리 매핑 [항목 10]
    prod_to_cat = {}
    for cat, items in TREND_CATEGORY.items():
        for it in items:
            prod_to_cat[it] = cat
    result_df["카테고리"] = result_df["제품·식재료"].map(prod_to_cat).fillna("기타")
    return {"df": result_df, "months": months, "baseline_avg": round(baseline_avg,1),
            "baseline_monthly": baseline_monthly}


# ── 고도화: 브랜드별 제품 언급·감성 분석 [항목 4] ──────
@st.cache_data(show_spinner="브랜드별 제품 분석 중...")
def compute_brand_products(_v, brand, sig=""):
    bdocs = _v[_v["brands"].apply(lambda x: brand in x)]
    if len(bdocs) < 2:
        return pd.DataFrame()
    rows = []
    for prod, kws in PRODUCT_DICT.items():
        pat = "|".join(kws)
        sub = bdocs[bdocs["full_text"].str.contains(pat, na=False)]
        n = len(sub)
        if n < 1:
            continue
        pos = (sub["sentiment"] == "긍정").sum()
        neg = (sub["sentiment"] == "부정").sum()
        nss = round((pos - neg) / n * 100, 1)
        # 카테고리 분류
        if prod in ["아메리카노","카페라떼","에스프레소","콜드브루","카푸치노","디카페인",
                    "프라푸치노","에이드","스무디","밀크티","말차라떼","녹차·티","초콜릿음료"]:
            cat = "커피·음료"
        elif prod in ["케이크","마카롱","티라미수","타르트","크로플","쿠키","빙수","푸딩","아이스크림","젤라또"]:
            cat = "디저트"
        else:
            cat = "베이커리·푸드"
        rows.append({"제품": prod, "카테고리": cat, "언급량": int(n),
                     "긍정": int(pos), "부정": int(neg), "NSS": nss})
    return pd.DataFrame(rows).sort_values("언급량", ascending=False) if rows else pd.DataFrame()

@st.cache_data(show_spinner="제품 월별 추이 분석 중...")
def compute_product_trend(_v, brand, product, sig="", win_start="", win_end=""):
    """[v2.7.0] 기간 전체를 덮는 글만, 월별 언급량은 30일 환산. NSS는 5건 이상인 달만."""
    tv = _ts_rows(_v)
    mdays = _month_days(win_start, win_end)
    if tv is None or len(tv) == 0 or not mdays:
        return pd.DataFrame(columns=["월", "언급량", "NSS", "표본"])
    bdocs = tv[tv["brands"].apply(lambda x: brand in x)]
    kws = PRODUCT_DICT.get(product, [product])
    pat = "|".join(kws)
    sub = bdocs[bdocs["full_text"].str.contains(pat, na=False)]
    rows = []
    for m, days in sorted(mdays.items()):
        msub = sub[sub["year_month"] == m]
        n = len(msub)
        pos = (msub["sentiment"] == "긍정").sum()
        neg = (msub["sentiment"] == "부정").sum()
        nss = round((pos - neg) / n * 100, 1) if n >= 5 else None
        rows.append({"월": m, "언급량": round(n / days * 30, 1), "NSS": nss, "표본": int(n)})
    return pd.DataFrame(rows)


# ── 고도화: 프로모션 모니터링 [항목 5] ─────────────────
@st.cache_data(show_spinner="프로모션 모니터링 중...")
def compute_promotion(_v, sig=""):
    # 프로모션 유형별 × 브랜드 언급
    promo_brand = pd.DataFrame(0, index=list(PROMO_DICT.keys()), columns=TARGET_BRANDS)
    promo_total = {}
    for promo, kws in PROMO_DICT.items():
        pat = "|".join(kws)
        pdocs = _v[_v["full_text"].str.contains(pat, na=False, case=False)]
        promo_total[promo] = int(len(pdocs))
        for b in TARGET_BRANDS:
            promo_brand.loc[promo, b] = int(pdocs["brands"].apply(lambda x: b in x).sum())
    promo_total_df = pd.DataFrame(
        [{"프로모션": k, "언급량": v} for k, v in promo_total.items()]
    ).sort_values("언급량", ascending=False)
    return promo_brand, promo_total_df

@st.cache_data(show_spinner="최근 프로모션 추세 분석 중...")
def compute_promo_recent(_v, sig="", win_start="", win_end=""):
    """[기능 4] 최근 60일 가장 많이 언급된 프로모션 + 가장 열심히 하는 브랜드
    [v2.7.0] 최근 구간은 기간 전체를 덮는 글만 사용 (검색 상한으로 최근 글이 몰린 검색어 제외)."""
    tv = _ts_rows(_v)
    if tv is None or len(tv) == 0 or not win_end:
        return pd.DataFrame(), pd.DataFrame()
    r0, we, _b0, _b1 = _period_bounds(win_start, win_end, 60, 0)
    recent = tv[(tv["_day"] >= r0) & (tv["_day"] <= we)]
    rows = []
    for promo, kws in PROMO_DICT.items():
        pat = "|".join(kws)
        rdocs = recent[recent["full_text"].str.contains(pat, na=False, case=False)]
        n = len(rdocs)
        if n < 1:
            continue
        # 가장 열심히 하는(많이 언급된) 브랜드
        bc = Counter()
        for _, r in rdocs.iterrows():
            for b in r["brands"]:
                bc[b] += 1
        top_brand = bc.most_common(1)[0][0] if bc else "—"
        top_brand_cnt = bc.most_common(1)[0][1] if bc else 0
        rows.append({"프로모션": promo, "최근언급": int(n),
                     "주력브랜드": top_brand, "주력브랜드_언급": int(top_brand_cnt)})
    recent_df = (pd.DataFrame(rows).sort_values("최근언급", ascending=False) if rows
                 else pd.DataFrame(columns=["프로모션", "최근언급", "주력브랜드", "주력브랜드_언급"]))

    # 브랜드별 프로모션 적극도 (전체 기간)
    brand_promo_rows = []
    for b in TARGET_BRANDS:
        bdocs = _v[_v["brands"].apply(lambda x: b in x)]
        if len(bdocs) < 1:
            continue
        all_promo_kws = [kw for kws in PROMO_DICT.values() for kw in kws]
        ppat = "|".join(all_promo_kws)
        promo_cnt = int(bdocs["full_text"].str.contains(ppat, na=False, case=False).sum())
        ratio = round(promo_cnt / len(bdocs) * 100, 1)
        brand_promo_rows.append({"브랜드": b, "프로모션언급": promo_cnt,
                                  "전체언급": int(len(bdocs)), "프로모션비중": ratio})
    brand_promo_df = (pd.DataFrame(brand_promo_rows).sort_values("프로모션언급", ascending=False) if brand_promo_rows
                      else pd.DataFrame(columns=["브랜드", "프로모션언급", "전체언급", "프로모션비중"]))
    return recent_df, brand_promo_df


@st.cache_data(show_spinner="급증 프로모션 탐지 중...")
def compute_promo_surge(_v, sig="", win_start="", win_end=""):
    """[v2.3.1] 최근 급증 프로모션 + 프로모션×브랜드 cross 매트릭스
    [v2.7.0] 최근 30일 vs 직전 90일(30일 환산), 기간 전체를 덮는 글만 사용."""
    tv = _ts_rows(_v)
    if tv is None or len(tv) == 0 or not win_end:
        return pd.DataFrame(), pd.DataFrame()
    r0, we, b0, b1 = _period_bounds(win_start, win_end, 30, 90)
    if b1 < b0:
        return pd.DataFrame(), pd.DataFrame()
    bdays = (b1 - b0).days + 1
    d = tv["_day"]
    recent = tv[(d >= r0) & (d <= we)]
    prior = tv[(d >= b0) & (d <= b1)]
    rows = []
    for promo, kws in PROMO_DICT.items():
        pat = "|".join(kws)
        r = int(recent["full_text"].str.contains(pat, na=False, case=False).sum())
        p_total = int(prior["full_text"].str.contains(pat, na=False, case=False).sum())
        p_avg = p_total * 30 / bdays
        growth = (r / p_avg - 1) * 100 if p_avg > 0 else (100.0 if r > 0 else 0.0)
        rows.append({"프로모션": promo, "최근월": r, "직전월평균": round(p_avg, 1),
                     "증감률": round(growth, 1), "급증": "🔥" if growth >= 50 and r >= 2 else ""})
    surge_df = pd.DataFrame(rows).sort_values("증감률", ascending=False)
    r60, _we, _x0, _x1 = _period_bounds(win_start, win_end, 60, 0)
    recent2 = tv[(d >= r60) & (d <= we)]
    cross = pd.DataFrame(0, index=list(PROMO_DICT.keys()), columns=TARGET_BRANDS)
    for promo, kws in PROMO_DICT.items():
        pat = "|".join(kws)
        pdocs = recent2[recent2["full_text"].str.contains(pat, na=False, case=False)]
        for _, rr in pdocs.iterrows():
            for b in rr["brands"]:
                if b in cross.columns:
                    cross.loc[promo, b] += 1
    return surge_df, cross

@st.cache_data(show_spinner="촉진 반응강도 측정 중...")
def compute_promo_reaction(_v, sig=""):
    """[기능 4] 반응 강도를 0~100 지표로 정규화하여 관리"""
    all_promo_kws = [kw for kws in PROMO_DICT.values() for kw in kws]
    promo_pat = "|".join(all_promo_kws)
    promo_docs = _v[_v["full_text"].str.contains(promo_pat, na=False, case=False)]
    rows = []
    for reaction, (kws, weight) in PROMO_REACTION.items():
        pat = "|".join(kws)
        cnt = int(promo_docs["full_text"].str.contains(pat, na=False).sum())
        rows.append({"반응": reaction, "언급량": cnt, "가중치": weight})
    react_df = pd.DataFrame(rows)
    # 프로모션 유형별 반응 강도 — 원점수 + 0~100 정규화 지표
    type_reaction = []
    for promo, pkws in PROMO_DICT.items():
        ppat = "|".join(pkws)
        pdocs = _v[_v["full_text"].str.contains(ppat, na=False, case=False)]
        if len(pdocs) < 1:
            continue
        pos_strong = pdocs["full_text"].str.contains("|".join(PROMO_REACTION["강한 긍정"][0]), na=False).sum()
        pos = pdocs["full_text"].str.contains("|".join(PROMO_REACTION["긍정"][0]), na=False).sum()
        neg = pdocs["full_text"].str.contains("|".join(PROMO_REACTION["부정"][0]), na=False).sum()
        raw_score = (pos_strong * 2 + pos * 1 - neg * 1) / len(pdocs)
        type_reaction.append({"프로모션": promo, "반응강도_raw": round(raw_score, 2),
                               "강한긍정": int(pos_strong), "긍정": int(pos), "부정": int(neg),
                               "언급량": int(len(pdocs))})
    type_react_df = pd.DataFrame(type_reaction)
    # 0~100 정규화 (반응강도 지표화)
    if len(type_react_df) > 0:
        rmin, rmax = type_react_df["반응강도_raw"].min(), type_react_df["반응강도_raw"].max()
        if rmax > rmin:
            type_react_df["반응강도지표"] = ((type_react_df["반응강도_raw"] - rmin) / (rmax - rmin) * 100).round(1)
        else:
            type_react_df["반응강도지표"] = 50.0
        type_react_df = type_react_df.sort_values("반응강도지표", ascending=False)
    return react_df, type_react_df, int(len(promo_docs))

def _kw_sentence(text, kws):
    """[v2.5.2] 키워드가 포함된 문장만 발췌 — 전체 글 대신 관련 부분만 노출(공용)."""
    t = str(text)
    for s in re.split(r"(?<=[.!?。…])\s+|\n+", t):
        if any(k in s for k in kws):
            s2 = re.sub(r"\s+", " ", s).strip()
            if len(s2) >= 6:
                return s2[:180]
    for k in kws:
        i = t.find(k)
        if i >= 0:
            return re.sub(r"\s+", " ", t[max(0, i - 40):i + 110]).strip()[:180]
    return ""


def get_promo_detail_docs(_v, promo_type):
    """[기능 5/v2.5.2] 프로모션 유형 원문 — 키워드가 실제 든 '문장'을 발췌하고
    무관 글은 제외, 관련도(키워드 빈도+제목 포함) 순 정렬."""
    kws = PROMO_DICT.get(promo_type, [])
    if not kws:
        return _v.iloc[0:0].copy()
    pat = "|".join(map(re.escape, kws))
    pdocs = _v[_v["full_text"].str.contains(pat, na=False, case=False)].copy()
    if len(pdocs) == 0:
        return pdocs
    pdocs["발췌"] = pdocs["full_text"].apply(lambda t: _kw_sentence(t, kws))
    pdocs = pdocs[pdocs["발췌"].str.len() > 0].copy()
    if len(pdocs) == 0:
        return pdocs

    def _rel(r):
        ft = str(r["full_text"]); ti = str(r.get("title", ""))
        return sum(ft.count(k) for k in kws) + (3 if any(k in ti for k in kws) else 0)
    pdocs["_rel"] = pdocs.apply(_rel, axis=1)
    return pdocs.sort_values("_rel", ascending=False)


# ── 고도화: 고객 클러스터링 & 페르소나 [항목 7] ─────────
# [v2.3.1] 라이프스타일·관심도 추론 사전 / 커피 외 동시언급 브랜드
LIFESTYLE_DICT = {
    "맛집·미식 탐방": ["맛집","미식","존맛","빵지순례","디저트투어","베이커리투어"],
    "여행·나들이":   ["여행","나들이","드라이브","호캉스","카페투어","제주","바다"],
    "예술·문화 관여": ["전시","공연","영화","뮤지컬","미술관","독서","콘서트","연극"],
    "운동·건강":     ["운동","헬스","러닝","요가","필라테스","다이어트","등산"],
    "육아·가족":     ["육아","아기","엄마","가족","키즈","아이랑"],
    "재택·디지털":   ["재택","카공","작업","노트북","유튜브","넷플릭스"],
    "패션·뷰티":     ["패션","화장품","뷰티","올리브영","무신사"],
}
COMPANION_BRANDS = ["배스킨라빈스","맥도날드","버거킹","롯데리아",   # [v2.7.0] 베이커리 브랜드 제외
                    "올리브영","다이소","무신사","CGV","넷플릭스","쿠팡","이마트","코스트코","애플"]
@st.cache_data(show_spinner="고객 클러스터링 중...")
def compute_customer_clustering(_v, k=8, sig=""):
    sub = _v[_v["tokens_str"].str.len() > 5].copy().reset_index(drop=True)
    if len(sub) < 30:
        return None
    # 피처: TF-IDF 텍스트
    tfidf = TfidfVectorizer(max_features=200, min_df=3, max_df=0.85,
                             token_pattern=r"[가-힣]{2,6}",
                             stop_words=list(MEANINGLESS_MODIFIERS))
    X_text = tfidf.fit_transform(sub["tokens_str"])   # [v2.7.0] 희소행렬 유지 (메모리 절약)
    # 행동 피처: 감성, 소비상황, 브랜드 수
    sent_map = {"긍정": 1, "중립": 0, "부정": -1}
    feat_sent = sub["sentiment"].map(sent_map).fillna(0).values.reshape(-1, 1)
    feat_nbrand = sub["brands"].apply(len).values.reshape(-1, 1)
    feat_loyalty = sub["full_text"].apply(
        lambda t: 1 if any(k in str(t) for k in ["단골","최애","자주","매일","항상"]) else 0
    ).values.reshape(-1, 1)
    feat_decaf = sub["full_text"].apply(
        lambda t: 1 if any(k in str(t) for k in ["디카페인","디카페","카페인"]) else 0
    ).values.reshape(-1, 1)
    # 결합 (텍스트 70% + 행동 30%)
    behav = np.hstack([feat_sent, feat_nbrand, feat_loyalty, feat_decaf]).astype(float)
    behav = StandardScaler().fit_transform(behav)
    X = sp.hstack([X_text * 0.7, sp.csr_matrix(behav * 0.3)]).tocsr()

    # [v2.7.0] 표본(최대 16,000건)으로 학습 → 전체 문서 배정. 세그먼트 비중·프로파일은 전체 기준
    fit_i = _fit_idx(X.shape[0], cap=MODEL_FIT_MAX * 2)
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X[fit_i])
    sub["cluster"] = km.predict(X)
    # PCA 2D
    pca = PCA(n_components=2, random_state=42)
    pca.fit(X[fit_i].toarray())
    coords = np.vstack([pca.transform(X[i:i + 20000].toarray()) for i in range(0, X.shape[0], 20000)])
    sub["pca_x"] = coords[:, 0]
    sub["pca_y"] = coords[:, 1]

    # 클러스터별 프로파일
    profiles = []
    vocab = tfidf.get_feature_names_out()
    for c in range(k):
        cdocs = sub[sub["cluster"] == c]
        n = len(cdocs)
        if n == 0:
            continue
        # 대표 키워드
        ctoks = cdocs["tokens_str"].str.cat(sep=" ").split()
        top_kw = [w for w, _ in Counter(ctoks).most_common(8)]
        # 주요 브랜드
        cbrands = Counter(b for bs in cdocs["brands"] for b in bs)
        top_brands = [b for b, _ in cbrands.most_common(3)]
        # 감성
        pos_r = round((cdocs["sentiment"] == "긍정").mean() * 100, 1)
        neg_r = round((cdocs["sentiment"] == "부정").mean() * 100, 1)
        nss = round(pos_r - neg_r, 1)
        # 충성도
        loyalty_r = round(cdocs["full_text"].apply(
            lambda t: any(k in str(t) for k in ["단골","최애","자주","매일"])).mean() * 100, 1)
        # 디카페인 관심
        decaf_r = round(cdocs["full_text"].apply(
            lambda t: any(k in str(t) for k in ["디카페인","디카페"])).mean() * 100, 1)
        # 주요 소비상황
        occ_top = cdocs["occasion"].value_counts().head(2).index.tolist() if "occasion" in cdocs.columns else []

        # [v2.3.1] 라이프스타일·관심도·동행 브랜드 추론
        ftext = " ".join(cdocs["full_text"].astype(str))
        life_scored = [(cat, sum(ftext.count(k) for k in kws)) for cat, kws in LIFESTYLE_DICT.items()]
        lifestyle = [cat for cat, sc in sorted(life_scored, key=lambda x: -x[1]) if sc > 0][:3]
        co_scored = [(b, ftext.count(b)) for b in COMPANION_BRANDS]
        co_brands = [b for b, sc in sorted(co_scored, key=lambda x: -x[1]) if sc > 0][:4]
        profiles.append({
            "cluster": c, "n": n, "top_kw": top_kw, "top_brands": top_brands,
            "pos_r": pos_r, "neg_r": neg_r, "nss": nss,
            "loyalty_r": loyalty_r, "decaf_r": decaf_r, "occ_top": occ_top,
            "lifestyle": lifestyle, "co_brands": co_brands,
        })
    # [v2.3.1] 브랜드 PCA 센트로이드 — 세그먼트 인접 브랜드 포지셔닝용
    brand_centroids = {}
    for b in TARGET_BRANDS:
        bd = sub[sub["brands"].apply(lambda x: b in x)]
        if len(bd) >= 5:
            brand_centroids[b] = (float(bd["pca_x"].mean()), float(bd["pca_y"].mean()))
    # [v2.7.0] 화면에 쓰는 열만 반환 (본문 등 큰 열을 캐시에 복제하지 않음)
    _keep = [c for c in ["cluster", "pca_x", "pca_y", "title", "sentiment", "tokens_str", "brands"] if c in sub.columns]
    return {"sub": sub[_keep], "profiles": profiles, "k": k, "brand_centroids": brand_centroids,
            "pca_var": [round(x*100,1) for x in pca.explained_variance_ratio_]}


KW_NAV_STOP = {
    "다음","이전","목록","처음","마지막","검색","클릭","링크","답글","댓글","대댓글","원문","출처",
    "사진","이미지","첨부","파일","수정","삭제","신고","공유","스크랩","조회","추천수","비추","페이지",
    "로그인","회원","가입","커피를","커피가","커피는","커피도","커피랑","커피만",
    "때문에","그리고","하지만","그래서","근데","해서","에서","으로","까지","부터","정도","경우","생각",
    "약간","정말","너무","완전","많이","조금","대한","관련","위해","보고","같이"}


def _kw_clean(words, n=12):
    """[v2.5.2] 관심 키워드에서 조사·종결어미·네비게이션 등 의미 없는 토큰 제거(공용)."""
    out = []
    for w in words:
        if w in KW_NAV_STOP or w in STOPWORDS or len(w) < 2:
            continue
        if w.endswith(("습니다", "입니다", "됩니다", "이라고", "하는데", "있는데")):
            continue
        if w not in out:
            out.append(w)
        if len(out) >= n:
            break
    return out


def make_persona(profile):
    """[v2.5.2] 클러스터 프로파일 → 직관적·간결한 페르소나 네이밍 + 키워드 정제"""
    kw = _kw_clean(profile["top_kw"], 12)
    brands = profile["top_brands"]
    nss = profile["nss"]
    loyalty = profile["loyalty_r"]
    decaf = profile["decaf_r"]
    lifestyle = profile.get("lifestyle", [])
    life0 = lifestyle[0] if lifestyle else ""

    # 라이프스타일 → (짧은 한 단어 태그, 맞춤 마케팅 액티비티)
    LIFE_TAG = {
        "맛집·미식 탐방": ("미식파", "신메뉴 시식단·한정 디저트 선출시"),
        "여행·나들이":   ("여행파", "여행지 팝업스토어·시즌 MD"),
        "예술·문화 관여": ("컬처파", "전시·공연 제휴 쿠폰·아트 콜라보"),
        "운동·건강":     ("웰니스파", "프로틴·저당 메뉴·러닝 크루 제휴"),
        "육아·가족":     ("패밀리", "키즈존·가족 세트·주말 패밀리데이"),
        "재택·디지털":   ("카공파", "카공 패키지·콘센트 좌석·롱블랙 무한리필"),
        "패션·뷰티":     ("트렌드파", "뷰티 브랜드 콜라보 굿즈·포토존"),
    }
    tag, life_mkt = LIFE_TAG.get(life0, ("", ""))
    _suffix = f" ({tag})" if tag else ""

    if decaf > 25:
        base = "디카페인 웰니스"
        name = f"오후의 디카페인족{_suffix}"
        desc = "오후·저녁에 디카페인·논카페인을 찾는 건강 지향 고객. 카페인 부담 없이 즐기고 싶어 함"
        ua = "오후·저녁 디카페인 / 임산부·수유부 가능 / 저당·저자극 선호"
        mkt = f"디카페인 라인 전면 노출 + {life_mkt or '오후 타임딜·저녁 논카페인 추천'}"
    elif loyalty > 35:
        base = "충성 단골"
        name = f"한 브랜드 찐단골{_suffix}"
        desc = "특정 브랜드만 반복 방문하는 고충성 고객. 출근길·일상 루틴에 카페가 자리잡음"
        ua = "매일·자주 방문 / 출근길 루틴 / 멤버십·적립 적극 활용"
        mkt = f"멤버십 등급·리워드 강화 + {life_mkt or '단골 전용 시크릿 메뉴·선공개'}"
    elif nss < -10:
        base = "이탈 위험"
        name = f"떠나려는 이탈주의 고객{_suffix}"
        desc = "가격·품질·서비스 불만이 쌓여 브랜드 전환을 저울질하는 고객. 즉각 케어가 필요"
        ua = "가격·품질·서비스 불만 / 대안 적극 탐색 / 불매 동참 가능"
        mkt = "VOC 신속 대응·보상 쿠폰 + 재방문 유도 윈백(win-back) 캠페인"
    elif any(k in ["추천", "후기", "비교", "맛집", "신메뉴"] for k in kw) or life0 == "맛집·미식 탐방":
        base = "탐색·전파"
        name = f"신메뉴 얼리어답터{_suffix}"
        desc = "신메뉴·맛집을 먼저 시도하고 SNS로 후기를 퍼뜨리는 오피니언 리더"
        ua = "신메뉴 빠른 시도 / SNS 인증·후기 / 카페 투어"
        mkt = f"신메뉴 선공개·체험단·해시태그 챌린지 + {life_mkt or 'SNS 인증 리워드'}"
    elif life0:
        base = "라이프스타일"
        name = f"{life0.split('·')[0]} 취향 소비자{_suffix}"
        desc = f"{life0}에 관심이 많아, 카페를 취향·활동의 연장선으로 즐기는 소비자"
        ua = f"{life0} 연계 방문 / 취향 기반 메뉴·공간 선택"
        mkt = life_mkt or "관심사 기반 제휴·콘텐츠 마케팅"
    else:
        base = "일상 소비"
        name = "가성비 데일리족"
        desc = "특별한 선호보다 접근성·편의·가성비로 카페를 이용하는 대중 소비자"
        ua = "테이크아웃·이동 중 소비 / 가성비 중시 / 가까운 매장"
        mkt = "가성비 세트·앱 전용 쿠폰·접근성 기반 입지 마케팅"

    # [v2.4.1] Pain-point · Key Buying Factor 추론
    PAIN_BY_BASE = {
        "디카페인 웰니스": "오후 카페인 부담·당·자극 / 논카페인 선택지 부족",
        "충성 단골": "리워드 체감 부족·대기시간 / 혜택 매너리즘",
        "이탈 위험": "가격 인상·품질 편차·서비스 불만 누적",
        "탐색·전파": "신메뉴 품절·정보 과부하 / 기대 대비 실망",
        "라이프스타일": "취향·활동과 카페 경험의 연결 부족",
        "일상 소비": "가격 민감·접근성 / 차별점 부재",
    }
    KBF_BY_BASE = {
        "디카페인 웰니스": "디카페인·저당 옵션, 건강 신뢰",
        "충성 단골": "멤버십 혜택·적립, 일관된 품질·접근성",
        "이탈 위험": "가성비·문제 해결 속도, 보상",
        "탐색·전파": "신메뉴 화제성·SNS 인증성, 한정성",
        "라이프스타일": "취향 적합도·공간 경험·콜라보",
        "일상 소비": "가격·접근성·속도(편의)",
    }
    pain = PAIN_BY_BASE.get(base, "—")
    kbf = KBF_BY_BASE.get(base, "—")
    return {"name": name, "base": base, "desc": desc, "ua": ua, "marketing": mkt,
            "pain": pain, "kbf": kbf,
            "brands": brands, "nss": nss, "loyalty": loyalty, "decaf": decaf,
            "n": profile["n"], "kw": kw,
            "lifestyle": profile.get("lifestyle", []),
            "co_brands": profile.get("co_brands", []),
            "occ": profile.get("occ_top", []),
            "pos_r": profile.get("pos_r", 0), "neg_r": profile.get("neg_r", 0)}



# ══════════════════════════════════════════════════════
# Market Intelligence 모듈 [v2.3.1]
# ══════════════════════════════════════════════════════
@st.cache_data(show_spinner="시장 데이터 로딩 중...", ttl=3600)
def fetch_market_series():
    """원두 선물(KC=F)·환율 시계열. yfinance 사용, 실패 시 None 반환."""
    try:
        import yfinance as yf
        tickers = {"원두선물": "KC=F", "USD/KRW": "KRW=X", "USD/BRL": "BRL=X",
                   "EUR/KRW": "EURKRW=X", "DXY": "DX-Y.NYB"}
        out = {}
        for name, tk in tickers.items():
            h = yf.Ticker(tk).history(period="6mo")["Close"].dropna()
            if len(h) > 5:
                out[name] = h
        return out if out else None
    except Exception:
        return None


def _series_metrics(s):
    cur = float(s.iloc[-1])
    ma20 = float(s.tail(20).mean())
    ma60 = float(s.tail(60).mean())
    base = s[s.index <= (s.index[-1] - pd.Timedelta(days=30))]
    mom = (cur / float(base.iloc[-1]) - 1) * 100 if len(base) else float("nan")
    hi = float(s.tail(63).max())
    lo = float(s.tail(63).min())
    return {"cur": cur, "ma20": ma20, "ma60": ma60, "mom": mom, "hi": hi, "lo": lo}


# ── [v2.3.3] News Monitoring 자동 연동 ─────────────────
NEWS_FILE_GLOB = "news_master_*.csv"   # 크롤러(naver_news_crawler.py) 산출물 패턴

def _find_latest_news_file():
    """대시보드 폴더 / ./news / 현재 경로에서 최신 news_master_*.csv 탐색."""
    try:
        base = os.path.dirname(os.path.abspath(__file__))
    except Exception:
        base = "."
    cands = []
    for d in (base, os.path.join(base, "news"), os.path.join(base, ".news"), ".", "news", ".news"):
        try:
            cands += glob.glob(os.path.join(d, NEWS_FILE_GLOB))
        except Exception:
            pass
    cands = list(set(cands))
    if not cands:
        return None
    return max(cands, key=os.path.getmtime)  # 가장 최근 수정본 = 최신본


# [v2.4.1] 데이터 자동 로딩 — GitHub 리포지토리 .data 폴더 최신 CSV
DATA_FILE_GLOBS = ("*.parquet", "*.csv", "*.csv.gz", "*.gz", "*.csv.xz", "*.xz", "*.xlsx")  # [v2.6.14] parquet·xz 지원

def _data_search_dirs():
    try:
        base = os.path.dirname(os.path.abspath(__file__))
    except Exception:
        base = "."
    return [os.path.join(base, "data"), os.path.join(base, ".data"),
            "data", ".data", base, "."]


_NOT_DATA = ("news_master", "sov_summary", "coverage", "manifest")


def _find_latest_data_file():
    """data / .data 폴더(및 앱 폴더·리포 루트)에서 최신 데이터 파일 자동 탐색.
    [v2.7.0] 이름에 voc_master가 든 파일만 후보 (sov_summary 등 다른 CSV를 데이터로 오인하지 않음).
    voc_master 파일이 하나도 없을 때만 예전처럼 나머지 데이터 파일에서 고름."""
    cands = []
    for d in _data_search_dirs():
        for g in DATA_FILE_GLOBS:
            try:
                cands += glob.glob(os.path.join(d, g))
            except Exception:
                pass
    cands = {os.path.abspath(c) for c in cands if os.path.isfile(c)}
    cands = [c for c in cands if not any(k in os.path.basename(c).lower() for k in _NOT_DATA)]
    vm = [c for c in cands if "voc_master" in os.path.basename(c).lower()]
    pool = vm or cands
    if not pool:
        return None

    def _key(p):
        m = re.search(r"(20\d{6})(?:_(\d{6}))?", os.path.basename(p))
        return (int(m.group(1)) if m else 0, int(m.group(2) or 0) if m else 0, os.path.getmtime(p))
    return max(pool, key=_key)


def _find_sov_summary(data_path):
    """[v2.7.0] 데이터 파일과 같은 시각(YYYYMMDD_HHMMSS)의 sov_summary를 찾음.
    같은 시각이 없으면 같은 날짜 중 최신, 그것도 없으면 None (다른 날 요약표로 보정하지 않음)."""
    if not data_path:
        return None
    m = re.search(r"(20\d{6})(?:_(\d{6}))?", os.path.basename(str(data_path)))
    if not m:
        return None
    date, hms = m.group(1), m.group(2)
    dirs = [os.path.dirname(os.path.abspath(str(data_path)))] + _data_search_dirs()
    cands = set()
    for d in dirs:
        cands |= {os.path.abspath(c) for c in glob.glob(os.path.join(d, "*sov_summary*.csv"))}
    if hms:
        exact = [c for c in cands if f"{date}_{hms}" in os.path.basename(c)]
        if exact:
            return sorted(exact)[-1]
    same_day = [c for c in cands if date in os.path.basename(c)]
    return max(same_day, key=os.path.getmtime) if same_day else None


@st.cache_data(show_spinner=False)
def load_sov_summary(path, fsig=""):
    try:
        s = pd.read_csv(path, encoding="utf-8-sig")
    except Exception:
        return None
    if not {"brand", "blog_est_6m"}.issubset(s.columns):
        return None
    s["brand"] = s["brand"].astype(str)
    for c in ("blog_est_6m", "blog_share_est", "blog_collected", "comm_total", "comm_share"):
        if c in s.columns:
            s[c] = pd.to_numeric(s[c], errors="coerce")
    return s


@st.cache_data(ttl=120, show_spinner=False)
def load_news_csv(path, _mtime):
    """뉴스 CSV 로드(+표준 컬럼 보정). _mtime은 파일 변경 시 캐시 무효화용."""
    df = pd.read_csv(path)
    for col in ["일자", "브랜드", "유형", "제목", "언론사", "링크", "요약"]:
        if col not in df.columns:
            df[col] = ""
    df["일자"] = df["일자"].astype(str)
    return df


TYPE_EMOJI = {"신제품 출시": "🆕", "혜택/프로모션/이벤트": "🎁", "굿즈/MD": "🛍️", "기타 이슈": "📌"}


def news_today_stats(today_df, latest_day):
    """[v2.3.6 1.1] 날짜·브랜드·유형별 기사 수를 이모지로 시인성 있게 (HTML 반환)."""
    if len(today_df) == 0:
        return "<div class='insight-box'>오늘자 뉴스가 없습니다.</div>"
    n = len(today_df)
    by_brand = today_df["브랜드"].value_counts()
    by_type = today_df["유형"].value_counts()
    brand_lines = "　".join(f"☕ {b} <b>{c}건</b>" for b, c in by_brand.items())
    type_lines = "<br>".join(f"{TYPE_EMOJI.get(t, '📰')} {t} <b>{c}건</b>" for t, c in by_type.items())
    return (
        "<div style='background:#F7F9FC;border:1px solid #E2E8F0;border-radius:8px;"
        "padding:12px 16px;font-size:0.9rem;color:#2D3748;line-height:1.7;'>"
        f"📅 <b>{latest_day}</b> · 오늘 수집 뉴스 총 <b>{n}건</b><br><br>"
        f"<b>🏷️ 브랜드별</b><br>{brand_lines}<br><br>"
        f"<b>🗂️ 유형별</b><br>{type_lines}"
        "</div>")


def make_news_briefing(today_df, latest_day, llm_only=False):
    """[v2.3.6 1.2] 요약(G칼럼) 내용을 다시 종합 → 1000자 이내 브리핑 기사.
    ANTHROPIC_API_KEY 있으면 Claude 자연어 요약, 없으면 규칙기반 합성(기본)."""
    if len(today_df) == 0:
        return "" if llm_only else "오늘자 뉴스가 없습니다. 크롤러를 실행해 최신 뉴스를 수집하세요."
    key = os.getenv("ANTHROPIC_API_KEY")
    if key:
        try:
            import anthropic
            clips = "\n".join(
                f"- [{r['브랜드']}/{r['유형']}] {r['제목']} :: {str(r.get('요약', ''))[:120]}"
                for _, r in today_df.head(60).iterrows())
            model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")
            cli = anthropic.Anthropic(api_key=key)
            res = cli.messages.create(
                model=model, max_tokens=700,
                messages=[{"role": "user", "content":
                           "다음은 오늘 국내 커피 업계 뉴스의 제목과 요약이다. 이를 종합하여 한국어로 "
                           "1000자 이내의 '오늘의 업계 종합 브리핑' 기사를 자연스러운 문장으로 작성하라. "
                           "브랜드별 핵심 움직임과 시사점을 포함하라.\n\n" + clips}])
            txt = "".join(getattr(b, "text", "") for b in res.content)
            if txt.strip():
                return txt.strip()[:1000]
        except Exception:
            pass
    if llm_only:
        return ""  # AI 요약 전용 호출 시, 키 없거나 실패하면 빈 문자열
    # 규칙기반 합성(기본) — 요약(G칼럼) 기반 유형별 종합 기사
    n = len(today_df)
    type_order = today_df["유형"].value_counts().index.tolist()
    lead = f"{latest_day} 국내 커피 업계에서는 총 {n}건의 뉴스가 포착됐다. "
    sents = []
    for typ in type_order:
        grp = today_df[today_df["유형"] == typ]
        brands = ", ".join(pd.unique(grp["브랜드"])[:4])
        descs = [re.sub(r"\s+", " ", str(d)).strip()
                 for d in grp["요약"] if str(d).strip() and str(d) != "nan"]
        rep = descs[0] if descs else re.sub(r"\s+", " ", str(grp["제목"].iloc[0]))
        rep = rep[:70]
        sents.append(f"{typ} 분야에서는 {brands} 등을 중심으로 {len(grp)}건이 다뤄졌으며, "
                     f"대표적으로 '{rep}…' 등이 보도됐다.")
    return (lead + " ".join(sents))[:1000]


def _title_sim(a, b):
    """제목 토큰 자카드 유사도 — 중복 기사 제거용."""
    ta = set(re.findall(r"[가-힣A-Za-z]{2,}", str(a)))
    tb = set(re.findall(r"[가-힣A-Za-z]{2,}", str(b)))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def news_reps_by_type(today_df, k=3):
    """[v2.4.1] 유형별로 유사·반복되는 대표기사 2~3건 선별 (중복 제거).
    반환: {유형: [(제목, 요약, 링크, 브랜드), ...]}"""
    res = {}
    if len(today_df) == 0:
        return res
    for typ, grp in today_df.groupby("유형"):
        all_tok = []
        for t in grp["제목"].astype(str):
            all_tok += re.findall(r"[가-힣A-Za-z]{2,}", t)
        freq = Counter(all_tok)
        scored, seen = [], []
        for _, r in grp.iterrows():
            title = str(r.get("제목", "")).strip()
            if not title or any(_title_sim(title, s) >= 0.6 for s in seen):
                continue
            seen.append(title)
            toks = re.findall(r"[가-힣A-Za-z]{2,}", title)
            score = sum(freq[w] for w in toks)  # 반복 테마일수록 高
            summary = re.sub(r"\s+", " ", str(r.get("요약", "") or "")).strip()
            scored.append((score, title, summary, str(r.get("링크", "") or ""),
                           str(r.get("브랜드", "") or "")))
        scored.sort(key=lambda x: -x[0])
        res[typ] = [(t, s, u, b) for _, t, s, u, b in scored[:k]]
    return res


def render_market_intelligence(view, v, brand_df):
    if view == "mi_raw":
        st.markdown("<div class='section-title'>🌐 원두 선물 · 국제 환율</div>",
                    unsafe_allow_html=True)
        series = fetch_market_series()
        if series is None or "원두선물" not in series:
            st.warning("⚠️ 라이브 시장 데이터(yfinance) 연결에 실패했습니다. "
                       "`pip install yfinance` 및 네트워크(야후 파이낸스) 접근을 확인하세요.")
            c1, c2 = st.columns(2)
            c1.link_button("ICE Coffee C Futures", "https://www.ice.com/products/15/coffee-c-futures/data?marketId=7455479")
            c2.link_button("investing.com 아라비카 커피", "https://kr.investing.com/commodities/arabica-coffee-4-5")
            st.caption(
                "ⓘ **ICE Coffee C Futures** — 미국 ICE(인터컨티넨탈 거래소)의 아라비카 원두 국제 선물 가격. "
                "전 세계 원두 거래의 기준 시세로, 원가 동향 파악의 1차 지표입니다.  　"
                "ⓘ **investing.com 아라비카 커피** — 같은 아라비카 커피 선물의 실시간 시세·차트를 무료로 제공하는 "
                "금융정보 사이트로, ICE 시세를 보조 확인하는 용도입니다.")
            return
        # [상단] 핵심 지표 5종
        st.markdown("**핵심 지표**")
        order = ["원두선물", "USD/KRW", "USD/BRL", "EUR/KRW", "DXY"]
        cols = st.columns(5)
        metr = {}
        for i, name in enumerate(order):
            if name in series:
                m = _series_metrics(series[name])
                metr[name] = m
                cols[i].metric(name, f"{m['cur']:,.2f}",
                               f"{m['mom']:+.1f}% (전월대비)" if m['mom'] == m['mom'] else "—")
        # [v2.4.1] 핵심 지표 5종 풋노트
        st.caption(
            "ⓘ **원두선물(KC=F)** 미국 ICE 아라비카 커피 국제 선물(¢/lb) — 원가의 기준 시세　|　"
            "**USD/KRW** 원/달러 환율 — 수입 원가의 원화 부담　|　"
            "**USD/BRL** 달러/헤알 — 최대 생산국 브라질 통화로 산지 공급가에 영향　|　"
            "**EUR/KRW** 유로/원 — 유럽산 장비·원부자재 수입가 참고　|　"
            "**DXY** 달러인덱스 — 달러 강세 정도로 원자재 가격 전반의 방향성 가늠")
        # [v2.6.1] 좌: 원두선물(20/60 MA), 우: EUR/KRW
        cL, cR = st.columns(2)
        with cL:
            s = series["원두선물"]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=s.index, y=s.values, name="원두선물(KC=F)", line=dict(color="#6F4E37", width=2)))
            fig.add_trace(go.Scatter(x=s.index, y=s.rolling(20).mean(), name="20일 MA", line=dict(color="#E67E22", width=1, dash="dot")))
            fig.add_trace(go.Scatter(x=s.index, y=s.rolling(60).mean(), name="60일 MA", line=dict(color="#2980B9", width=1, dash="dash")))
            fig.update_layout(title="원두 선물 (Coffee C, ¢/lb)")
            chart_style(fig, height=340)
            st.plotly_chart(fig, use_container_width=True)
            m = metr.get("원두선물", {})
            if m:
                st.caption(f"최근 3개월 고점 {m['hi']:,.1f} / 저점 {m['lo']:,.1f}")
        with cR:
            if "EUR/KRW" in series:
                s2 = series["EUR/KRW"]
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(x=s2.index, y=s2.values, name="EUR/KRW", line=dict(color="#1B2A4A", width=2)))
                fig2.add_trace(go.Scatter(x=s2.index, y=s2.rolling(20).mean(), name="20일 MA", line=dict(color="#E67E22", width=1, dash="dot")))
                fig2.update_layout(title="원/유로 환율 (EUR/KRW)")
                chart_style(fig2, height=340)
                st.plotly_chart(fig2, use_container_width=True)
                m2 = metr.get("EUR/KRW", {})
                if m2:
                    st.caption(f"최근 3개월 고점 {m2['hi']:,.1f} / 저점 {m2['lo']:,.1f}")
        # [v2.3.5] 그래프 하단 외부 시세 사이트 접근 버튼 (복원)
        st.markdown("---")
        bcol1, bcol2 = st.columns(2)
        bcol1.link_button("ICE Coffee C Futures",
                          "https://www.ice.com/products/15/coffee-c-futures/data?marketId=7455479",
                          use_container_width=True)
        bcol2.link_button("investing.com 아라비카 커피",
                          "https://kr.investing.com/commodities/arabica-coffee-4-5",
                          use_container_width=True)
        st.caption("ⓘ **ICE Coffee C Futures** — 미국 ICE(인터컨티넨탈 거래소)의 아라비카 원두 국제 선물 가격(전 세계 기준 시세).　"
                   "ⓘ **investing.com 아라비카 커피** — 동일 선물의 실시간 시세·차트를 무료 제공(보조 확인용).")

    elif view == "mi_news":
        st.markdown("<div class='section-title'>📰 PAS 뉴스룸 (국내 언론)</div>",
                    unsafe_allow_html=True)
        npath = _find_latest_news_file()
        if npath is None:
            st.warning("최신 뉴스 CSV를 찾지 못했습니다.")
            st.caption(f"크롤러(naver_news_crawler.py)가 생성한 `{NEWS_FILE_GLOB}` 파일을 "
                       "대시보드와 같은 폴더(또는 ./news 폴더)에 두면 업로드 없이 자동으로 최신본을 읽어옵니다.")
            st.link_button("📧 뉴스 사내 이메일로 공유",
                           "https://hubmail.spc.co.kr/Mail/Message/CubeMessageMaster.aspx")
            return
        import datetime as _dt
        mtime = os.path.getmtime(npath)
        ndf = load_news_csv(npath, mtime)
        updated = _dt.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
        cap_l, cap_r = st.columns([4, 1])
        cap_l.caption(f"🔗 자동 연동: {os.path.basename(npath)} · 총 {len(ndf):,}건 · 갱신 {updated} "
                      "(크롤러 실행 후 새로고침하면 최신본 자동 반영)")
        if cap_r.button("🔄 새로고침", key="news_reload", use_container_width=True):
            st.cache_data.clear(); st.rerun()

        # 오늘의 업계 뉴스 Keywords — 최신 일자 제목 빈도 상위
        latest_day = ndf["일자"].max()
        day_titles = " ".join(ndf[ndf["일자"] == latest_day]["제목"].astype(str))
        toks = [w for w in re.findall(r"[가-힣A-Za-z]{2,}", day_titles)
                if w not in STOPWORDS and w not in TARGET_BRANDS]
        top_kw = [w for w, _ in Counter(toks).most_common(6)]
        st.markdown(f"**오늘의 업계 뉴스 Keywords**  ({latest_day})")
        if "news_kw" not in st.session_state:
            st.session_state["news_kw"] = None
        kwcols = st.columns(max(len(top_kw), 1) + 1)
        for i, kw in enumerate(top_kw):
            if kwcols[i].button(f"#{kw}", key=f"newskw_{kw}", use_container_width=True):
                st.session_state["news_kw"] = kw
        if kwcols[-1].button("전체", key="newskw_all", use_container_width=True):
            st.session_state["news_kw"] = None

        # 필터 (데이터에 실제 존재하는 값으로)
        brands_in = sorted([b for b in ndf["브랜드"].dropna().unique() if str(b).strip()])
        types_in = sorted([t for t in ndf["유형"].dropna().unique() if str(t).strip()])
        c1, c2 = st.columns(2)
        with c1:
            sel_b = st.multiselect("브랜드 필터", brands_in, default=brands_in, key="news_brand_sel")
        with c2:
            sel_t = st.multiselect("뉴스 유형", types_in, default=types_in, key="news_type_sel")

        fdf = ndf[ndf["브랜드"].isin(sel_b) & ndf["유형"].isin(sel_t)].copy()
        active_kw = st.session_state.get("news_kw")
        if active_kw:
            fdf = fdf[fdf["제목"].astype(str).str.contains(active_kw, na=False)]
            st.caption(f"🔎 키워드 필터 적용: #{active_kw}  ('전체' 버튼으로 해제)")
        fdf = fdf.sort_values("일자", ascending=False)

        # [v2.4.1] 오늘의 뉴스 브리핑 = (1.1) 이모지 통계 + (선택)AI요약 + (1.2) 유형별 대표기사
        st.markdown("<div class='section-title'>📋 오늘의 뉴스 브리핑</div>", unsafe_allow_html=True)
        _today = ndf[ndf["일자"] == latest_day]
        st.markdown(news_today_stats(_today, latest_day), unsafe_allow_html=True)
        st.markdown("")  # 줄바꿈(가독성)
        _ai = make_news_briefing(_today, latest_day, llm_only=True)
        if _ai:
            st.markdown(f"<div class='insight-box'><b>🤖 AI 종합 브리핑</b><br>{_ai}</div>",
                        unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📰 오늘의 핵심 뉴스 — 유형별 대표기사</div>",
                    unsafe_allow_html=True)
        st.caption("유형별로 유사·반복되는 대표기사 2~3건을 추려 요약과 함께 정리했습니다. (제목 옆 '원문 보기'로 기사 확인)")
        _reps = news_reps_by_type(_today)
        if not _reps:
            st.caption("오늘자 대표기사가 없습니다.")
        for _typ, _items in _reps.items():
            with st.expander(f"{TYPE_EMOJI.get(_typ, '📰')} {_typ} · 대표기사 {len(_items)}건", expanded=True):
                for _title, _summary, _url, _brand in _items:
                    _link = f"  [원문 보기]({_url})" if str(_url).startswith("http") else ""
                    st.markdown(f"**[{_brand}] {_title}**{_link}")
                    if _summary and _summary != "nan":
                        st.caption(_summary)

        st.markdown(f"**뉴스 목록** — {len(fdf):,}건")
        show = fdf[["일자", "브랜드", "유형", "제목", "언론사", "링크"]]
        st.dataframe(
            show, use_container_width=True, hide_index=True, height=460,
            column_config={
                "링크": st.column_config.LinkColumn("링크", display_text="기사보기"),
                "제목": st.column_config.TextColumn("제목", width="large"),
            })
        st.link_button("📧 뉴스 사내 이메일로 공유",
                       "https://hubmail.spc.co.kr/Mail/Message/CubeMessageMaster.aspx")

    elif view == "mi_voc":
        st.markdown("<div class='section-title'>🗣️ 소비자 VoC 모니터링 시스템</div>",
                    unsafe_allow_html=True)
        st.warning("🚧 **To Be Developed** — 소비자 불만 데이터를 VoC 서버 API와 연동하여 "
                   "불만 유형/지역별/점포별로 자동 분석·시각화하는 기능입니다. "
                   "현재 API 연동 이슈로 개발 대기 중입니다.")
        c1, c2, c3 = st.columns(3)
        c1.markdown("**불만 유형 분석**\n\n(TBD)")
        c2.markdown("**지역별 분포**\n\n(TBD)")
        c3.markdown("**점포별 분포**\n\n(TBD)")


# ══════════════════════════════════════════════════════
# 사이드바
# ══════════════════════════════════════════════════════
with st.sidebar:
    # [디자인 v2.3.1] 타이틀 +15% 확대, 부제 삭제
    st.markdown(
        "<div style='font-size:1.5rem;font-weight:800;color:#1B2A4A;line-height:1.22;'>"
        "☕ PASCUCCI<br><span style='font-size:1.17rem;font-weight:700;'>"
        "Consumer Intelligence Dashboard</span></div>",
        unsafe_allow_html=True)
    # [디자인 1] 버전 표시
    st.markdown(
        f"<div style='color:#1B2A4A;font-weight:700;font-size:0.82rem;margin-top:2px;'>"
        f"{APP_VERSION} <span style='color:#718096;font-weight:400;'>({APP_DATE})</span></div>",
        unsafe_allow_html=True)
    # [디자인 2] Copyright 작은 글씨
    st.markdown(
        f"<div style='color:#A0AEC0;font-size:0.62rem;line-height:1.3;margin-top:3px;'>"
        f"{COPYRIGHT}</div>",
        unsafe_allow_html=True)
    st.markdown("---")
    # [v2.3.4] Consumer Intelligence Dashboard — MI에서 분리, 데이터 업로드 위로 이동
    if "view" not in st.session_state:
        st.session_state["view"] = "dashboard"
    if st.button("📊 컨슈머 인텔리전스 대시보드", use_container_width=True, key="nav_dash"):
        st.session_state["view"] = "dashboard"
    # [v2.5.3] 데이터 파일 업로드 위젯 제거 — 배포 버전은 데이터를 자동 인식하므로 불필요
    # (로컬 업로드가 필요한 버전에서만 재도입; 다운스트림 호환 위해 uploaded=None 유지)
    uploaded = None
    st.markdown("---")
    # [v2.3.4] Market Intelligence 네비게이션 (CID 분리)
    st.markdown("**🧭 Market Intelligence**")
    if st.button("🌐 원두선물·환율 모니터링", use_container_width=True, key="nav_raw"):
        st.session_state["view"] = "mi_raw"
    if st.button("📰 PAS 뉴스룸", use_container_width=True, key="nav_news"):
        st.session_state["view"] = "mi_news"
    if st.button("🗣️ 소비자 VoC (개발 중)", use_container_width=True, key="nav_voc"):
        st.session_state["view"] = "mi_voc"
    st.markdown("---")
    # [v2.3.1→2] 분석 리포트 다운로드 — 네비 아래 배치(데이터 로드 후 채움)
    report_dl_slot = st.empty()
    st.markdown("---")

# [v2.4.1] 업로드가 없으면 GitHub .data 폴더의 최신 파일을 자동 사용
auto_data_path = None
if uploaded is None:
    auto_data_path = _find_latest_data_file()

if uploaded is None and auto_data_path is None:
    st.markdown("""
    <div style='text-align:center; padding:60px 20px;'>
        <div style='font-size:4rem'>☕</div>
        <h1 style='color:#1B2A4A; margin:20px 0 10px;'>PASCUCCI Consumer Intelligence Dashboard</h1>
        <h3 style='color:#2D6BC4; font-weight:400;'>Consumer Data-driven Marketing for PASCUCCI</h3>
    </div>""", unsafe_allow_html=True)
    cols = st.columns(4)
    features = [
        ("📊", "Overview",       "KPI · 감성분포 · 언급량"),
        ("📈", "NSS 평판",       "Net Sentiment 월별 추이"),
        ("📣", "SOV 분석",       "담론 점유율 매트릭스"),
        ("🔍", "드라이버 분석",  "ABSA 속성별 긍/부정"),
        ("🗺️", "브랜드 이미지맵",  "브랜드 이미지 맵 - 대응일치분석(CA)"),
        ("🎯", "LDA 토픽",      "7-토픽 모델링 결과"),
        ("⚡", "Burst 탐지",    "급증 키워드 Burst Detection"),
        ("🔗", "PMI 분석",      "브랜드 공출현 강도"),
        ("📍", "포지셔닝맵",    "버블차트 · 레이더"),
        ("☁️", "키워드 버블",   "브랜드별 연관어"),
        ("🎯", "소비 맥락",     "Occasion × 브랜드"),
        ("🚨", "리스크 탐지",   "부정 드라이버 맵"),
    ]
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 4]:
            st.markdown(f"""
            <div style='background:#FFFFFF;border:1px solid #E2E8F0;border-top:3px solid #2D6BC4;
                        border-radius:10px;padding:14px;text-align:center;margin-bottom:10px;
                        box-shadow:0 2px 6px rgba(0,0,0,0.05)'>
                <div style='font-size:1.6rem'>{icon}</div>
                <div style='color:#1B2A4A;font-weight:700;margin:5px 0;font-size:0.9rem'>{title}</div>
                <div style='color:#718096;font-size:0.75rem'>{desc}</div>
            </div>""", unsafe_allow_html=True)
    st.info("ℹ️ 데이터를 자동으로 찾지 못했습니다. "
            "GitHub 리포지토리의 **data/ 폴더(점 없이)**에 voc_master 파일(과 같은 시각의 sov_summary)을 커밋하세요. "
            "(`.gitignore`에 `*.csv` 또는 `data/`가 포함되면 깃에 올라가지 않으니 확인 필요)")
    with st.expander("자동 탐색 경로 확인"):
        for _d in _data_search_dirs():
            st.caption(f"· {_d}")
    st.stop()

# ══════════════════════════════════════════════════════
# 데이터 로딩 — 업로드 우선, 없으면 data/.data 폴더 최신 파일 [v2.4.2]
# ══════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def _tag_source_quality(_v, sig=""):
    """소스(블로그/커뮤니티)+콘텐츠 유형 태깅. [v2.6.11]
    enriched 품질 컬럼(content_type/is_garbage_voc/is_sponsored/is_press_release)이 있으면 실측 사용,
    없으면 휴리스틱 폴백. _voc_ok=진성 VoC 플래그(브랜드 지표는 이 기준으로 거르는 것을 권장).
    [v2.6.13] _v(언더스코어)로 받아 cache_data 해싱 스킵 — brands/tokens 리스트 컬럼 OOM 차단. sig로 무효화 제어."""
    v = _v  # [v2.6.13] 이하 본문은 v 참조 유지 (무손실 별칭)
    import re as _re
    import pandas as _pd
    v = v.copy()
    _src = v["source_type"].astype(str) if "source_type" in v.columns \
        else _pd.Series(["community"] * len(v), index=v.index)
    v["_src"] = _src.map({"blog": "블로그", "community": "커뮤니티"}).fillna("기타")

    _enriched = ("content_type" in v.columns) and ("is_garbage_voc" in v.columns)
    if _enriched:
        _map = {"방문기·리뷰": "블로그 리뷰", "브랜드 스침": "스침(저관련)",
                "혜택·정보정리": "혜택·홍보성", "협찬·광고": "협찬·광고", "보도·뉴스": "보도·뉴스"}
        _ct = v["content_type"].astype(str).map(_map)
        _ct[v["_src"] == "커뮤니티"] = "커뮤니티 여론"
        v["_ctype"] = _ct.fillna("기타")
        _gar = _pd.to_numeric(v.get("is_garbage_voc"), errors="coerce").fillna(0)
        _spo = _pd.to_numeric(v.get("is_sponsored"), errors="coerce").fillna(0)
        _prs = _pd.to_numeric(v.get("is_press_release"), errors="coerce").fillna(0)
        _rel = _pd.to_numeric(v.get("relevance_score"), errors="coerce").fillna(0)
        _aff = _pd.to_numeric(v.get("has_affiliate"), errors="coerce").fillna(0)
        _ad = _pd.to_numeric(v.get("ad_score"), errors="coerce").fillna(0)
        _txt2 = v["full_text"].astype(str) if "full_text" in v.columns \
            else (v.get("title", "").fillna("").astype(str) + " " + v.get("body", "").fillna("").astype(str))
        # 본문 협찬 '고지' 문구(광고 '언급'이 아닌 대가성 고지) — 정밀 패턴
        _DISC = (r"협찬|원고료|소정의\s*(?:원고료|고료|수수료|혜택)|제공\s*?받아|제공받아|제공\s*?받았|무상\s*제공"
                 r"|업체로부터.{0,12}제공|대가를?\s*받|대가성|경제적\s*대가|체험단|서포터즈|기자단|표시광고"
                 r"|공정거래위원회|쿠팡\s*파트너스|파트너스\s*활동|협찬을?\s*받")
        _disc = _txt2.str.contains(_DISC, regex=True, na=False)
        _blog = v["_src"] == "블로그"
        # 일방적 추천(긍정 일색 + 강한 추천어 다수) — 소프트 협찬 의심 신호
        _promo_n = _txt2.str.count(r"강력\s*추천|강추|인생\s*?맛집|꼭\s*가보|재방문\s*의사|또\s*가고\s*싶|내돈내산|믿고\s*먹는|후회\s*?없|강력추천")
        _one_sided = (v.get("sentiment", _pd.Series("", index=v.index)).astype(str) == "긍정") & (_promo_n >= 2)
        # 진성 VoC: 협찬고지·어필리에이트·저관련(relevance<0.5)까지 추가 제외 [v2.6.12]
        v["_voc_ok"] = ((v["_src"] == "커뮤니티") |
                        ((v["_ctype"] == "블로그 리뷰") & (_gar != 1) & (_spo != 1) & (_prs != 1)
                         & (_rel >= 0.5) & (_aff != 1) & (~_disc)))
        # 협찬 의심 플래그(소프트): 고지문구·어필리에이트·강한 광고점수·일방적추천
        v["_spon_suspect"] = _blog & (_disc | (_aff == 1) | (_ad >= 0.5) | _one_sided)
    else:
        if "full_text" in v.columns:
            _txt = v["full_text"].astype(str)
        else:
            _txt = (v.get("title", "").fillna("").astype(str) + " " + v.get("body", "").fillna("").astype(str))
        _PROMO = r"배민|배달의민족|배달의 민족|쿠팡이츠|요기요|쿠폰|할인 정보|할인정보|할인코드|이벤트 정리|픽업 할인|적립 혜택|혜택 정리|혜택정리|프로모션 정리|페스타|천원의|기프티콘 이벤트"
        _PR = r"보도자료|\[알림\]|연합뉴스|뉴시스|뉴스1|조선비즈|머니투데이|이데일리|기자\]|배포일|출처\s*=|제공\s*=|보도 자료"
        _promo = _txt.str.contains(_PROMO, regex=True, na=False)
        _pr = _txt.str.contains(_PR, regex=True, na=False)
        _ct = _pd.Series("블로그 리뷰", index=v.index)
        _ct[v["_src"] == "커뮤니티"] = "커뮤니티 여론"
        _ct[(v["_src"] == "블로그") & _promo] = "혜택·홍보성"
        _ct[(v["_src"] == "블로그") & _pr] = "보도·뉴스"
        v["_ctype"] = _ct
        v["_voc_ok"] = v["_ctype"].isin(["커뮤니티 여론", "블로그 리뷰"])
        v["_spon_suspect"] = False
    return v


_data_source = uploaded if uploaded is not None else auto_data_path
_FSIG = _file_sig(_data_source)
# [v2.7.0] 같은 시각의 SOV 요약표(블로그 6개월 환산) — 있으면 언급량·SOV 보정에 사용
_SUM_PATH = _find_sov_summary(_data_source)
sov_summary = load_sov_summary(_SUM_PATH, _file_sig(_SUM_PATH)) if _SUM_PATH else None
_PERIOD_FROM = ""
if sov_summary is not None and "period_from" in sov_summary.columns and sov_summary["period_from"].notna().any():
    _PERIOD_FROM = str(sov_summary["period_from"].dropna().iloc[0])[:10]
try:
    v = load_and_preprocess(_data_source, _FSIG, _PERIOD_FROM)
except Exception as _e:
    import traceback as _tb
    st.error(f"데이터 로딩 중 오류: {type(_e).__name__}: {_e}")
    st.code(_tb.format_exc())
    st.info("데이터 파일이 크롤러 표준 스키마(voc_master)인지, 파일이 손상되지 않았는지 확인하세요.")
    st.stop()

# [v2.7.0] 추이 분석 기간·표본 (검색 상한·수집 당일 글 제외 기준)
COV = compute_coverage(_data_source, _FSIG, _PERIOD_FROM)
COV_META = COV["meta"] if COV else {}
WIN_START = str(COV_META["win_start"].date()) if COV_META.get("win_start") is not None else ""
WIN_END = str(COV_META["win_end"].date()) if COV_META.get("win_end") is not None else ""

v = _tag_source_quality(v, sig=_FSIG)  # [v2.6.13] sig로 캐시 무효화 제어

with st.sidebar:
    st.markdown("**🔧 필터**")
    # [v2.7.0] 브랜드 필터 = 화면 표시 범위 (점유율 등 계산은 12개 브랜드 전체 기준 유지)
    brand_filter = st.multiselect(
        "표시 브랜드", TARGET_BRANDS, default=TARGET_BRANDS,
        help="차트·표에 보여줄 브랜드. SOV 등 점유율은 12개 브랜드 전체 대비 비중으로 계산됩니다.")
    st.markdown("---")
    st.markdown("**🧭 데이터 소스 (1단계)**")
    _src_all = [x for x in ["블로그", "커뮤니티"] if x in set(v["_src"])]
    src_sel = st.multiselect("소스 선택", _src_all, default=_src_all,
                             help="블로그=노출·후기 / 커뮤니티=여론·리스크. 두 소스는 성격이 달라 분리해 봐야 합니다.")
    st.markdown("**🎯 콘텐츠 품질 (2단계)**")
    qual_sel = st.radio("필터", ["전체", "VoC만 (리뷰·여론)", "홍보·보도성만"], index=1,
                        help="VoC만=협찬·홍보·보도·저관련(스침)·garbage 제외한 진성 VoC. 데이터 품질상 기본값 권장. 홍보·보도성만=역점검용.")
    with st.expander("📊 소스별 특성 비교", expanded=False):
        _rows = []
        for _sname, _g in v.groupby("_src"):
            _pos = (_g["sentiment"] == "긍정").mean() * 100
            _neg = (_g["sentiment"] == "부정").mean() * 100
            _rows.append({"소스": _sname, "건수": len(_g), "긍정%": round(_pos, 1),
                          "부정%": round(_neg, 1), "NSS": round(_pos - _neg, 1)})
        if _rows:
            st.dataframe(pd.DataFrame(_rows).set_index("소스"), use_container_width=True)
            st.caption("같은 시장이라도 소스에 따라 감성·구성이 크게 달라집니다.")
        if "_spon_suspect" in v.columns:
            _blog_n = int((v["_src"] == "블로그").sum())
            _susp_n = int(v["_spon_suspect"].sum())
            _voc_blog = int(((v["_src"] == "블로그") & v.get("_voc_ok", False)).sum())
            st.caption(f"🚩 협찬 의심(고지문구·어필리에이트·강광고·일방적추천) 블로그 {_susp_n:,}건 / "
                       f"진성 VoC로 분류된 블로그 {_voc_blog:,}건. "
                       f"'VoC만' 필터는 협찬고지·어필리에이트·저관련(relevance<0.5)을 이미 제외합니다.")
    st.markdown("---")
    # [v2.7.0] 데이터·보정 현황 (자동 생성)
    _fname = os.path.basename(str(_data_source)) if _data_source else "—"
    _bits = [f"🔗 <b>{_fname}</b>", f"분석 대상 {len(v):,}건"]
    if WIN_START and WIN_END:
        _bits.append(f"수집 기간 {WIN_START} ~ {WIN_END}")
    if sov_summary is not None:
        _bits.append(f"✅ 블로그 언급량·SOV: 6개월 환산 적용 ({os.path.basename(_SUM_PATH)})")
    else:
        _bits.append("⚠️ 블로그 언급량·SOV: 보정 정보(sov_summary) 없음 → 수집 건수 기준(보정 전)")
    if COV_META:
        _bits.append(f"📈 추이 분석 표본 {COV_META.get('n_ts', 0):,}건 "
                     f"(블로그 {COV_META.get('n_blog_ts', 0):,} · 커뮤니티 {COV_META.get('n_comm_ts', 0):,})")
        _ex = []
        if COV_META.get("n_capped"):
            _ex.append(f"검색 상한 검색어 {COV_META['n_capped']}개")
        if COV_META.get("n_partial"):
            _ex.append(f"수집 당일 글 {COV_META['n_partial']:,}건")
        if COV_META.get("n_sampler"):
            _ex.append(f"반복 샘플링 {COV_META['n_sampler']:,}건")
        if _ex:
            _bits.append("추이 제외: " + " · ".join(_ex))
    st.markdown("<div style='font-size:0.72rem;line-height:1.55;color:#4A5568;'>" + "<br>".join(_bits) + "</div>",
                unsafe_allow_html=True)
    if COV_META.get("capped_queries"):
        with st.expander("검색 상한에 걸린 검색어 (추이 분석 제외)", expanded=False):
            st.caption("네이버 검색은 검색어당 최신 1,000건까지만 제공해, 아래 검색어는 최근 일부 기간만 담겼습니다. "
                       "언급량·SOV는 6개월 환산치로 보정하고, 월별 추이·급증 분석에서는 제외합니다.")
            st.markdown("<div style='font-size:0.72rem;color:#4A5568;'>" +
                        " · ".join(COV_META["capped_queries"]) + "</div>", unsafe_allow_html=True)

# ── 소스/품질 필터 적용: 선택한 렌즈로 분석 범위 재설정(모든 분석에 반영) ──
_mask = v["_src"].isin(src_sel)
if qual_sel == "VoC만 (리뷰·여론)":
    _mask &= v["_voc_ok"] if "_voc_ok" in v.columns else v["_ctype"].isin(["커뮤니티 여론", "블로그 리뷰"])
elif qual_sel == "홍보·보도성만":
    _mask &= (~v["_voc_ok"]) if "_voc_ok" in v.columns else v["_ctype"].isin(["혜택·홍보성", "보도·뉴스"])
if not _mask.any():
    st.warning("선택한 소스/품질 조건에 맞는 데이터가 없습니다. 필터를 완화하세요.")
    st.stop()

# [v2.7.0] 캐시 키: 데이터 파일 + 선택한 소스·품질 (예전에는 키에 데이터가 빠져 필터를 바꿔도 지표가 그대로였음)
_VSIG = f"{_FSIG}|{'+'.join(sorted(src_sel))}|{qual_sel}"
_SUM_SIG = _file_sig(_SUM_PATH) if _SUM_PATH else "none"
v["_inlens"] = _mask
brand_df_all = compute_brand_stats(v, f"{_VSIG}|{_SUM_SIG}", sov_summary,
                                   "블로그" in src_sel, "커뮤니티" in src_sel)
v = v[_mask].drop(columns=["_inlens"]).copy()
st.sidebar.caption(f"🔍 현재 분석 범위: {' + '.join(src_sel) if src_sel else '없음'} · {qual_sel} · {len(v):,}건")
SEL_BRANDS = [b for b in TARGET_BRANDS if b in brand_filter] or list(TARGET_BRANDS)

# 분석 실행 (계산은 12개 브랜드 전체 기준)
monthly_nss_all, all_months = compute_monthly_nss(v, _VSIG, WIN_START, WIN_END)
absa_df   = compute_absa(v, _VSIG)
ca_result = compute_ca(v, _VSIG)
burst_df  = compute_burst(v, _VSIG, WIN_START, WIN_END)
pmi_all   = compute_pmi(v, _VSIG)
loyalty_all = compute_loyalty(v, _VSIG)
occ_detail_df = compute_occasion_detailed(v, _VSIG)
occ_brand_all = compute_occasion_brand_matrix(v, _VSIG)
market_corpus = build_market_trend_corpus(_data_source, _FSIG, _PERIOD_FROM)
market_es = compute_market_es(market_corpus, _FSIG, WIN_START, WIN_END)
pair_net = compute_pairing_network(market_corpus, _FSIG)
emergent_df = compute_emergent_terms(market_corpus, _FSIG, WIN_START, WIN_END)
promo_brand_all, promo_total_df = compute_promotion(v, _VSIG)
promo_react_df, promo_type_react_df, promo_doc_count = compute_promo_reaction(v, _VSIG)
promo_recent_df, brand_promo_all = compute_promo_recent(v, _VSIG, WIN_START, WIN_END)
promo_surge_df, promo_cross_all = compute_promo_surge(v, _VSIG, WIN_START, WIN_END)
# LDA·토픽 클러스터·고객 클러스터링은 해당 탭에서 계산(지연 계산)


# [v2.7.0] 화면 표시 범위 = 사이드바에서 고른 브랜드
def _keep_brands(df, *cols):
    if df is None or len(df) == 0 or not all(c in df.columns for c in cols):
        return df
    m = pd.Series(True, index=df.index)
    for c in cols:
        m &= df[c].isin(SEL_BRANDS)
    return df[m].reset_index(drop=True)


def _keep_brand_cols(mat):
    if mat is None or len(getattr(mat, "columns", [])) == 0:
        return mat
    return mat[[c for c in mat.columns if c in SEL_BRANDS]]


brand_df = _keep_brands(brand_df_all, "브랜드")
monthly_nss_df = _keep_brands(monthly_nss_all, "브랜드")
pmi_df = _keep_brands(pmi_all, "브랜드1", "브랜드2")
loyalty_df = _keep_brands(loyalty_all, "브랜드")
occ_brand_mat = _keep_brand_cols(occ_brand_all)
promo_brand_mat = _keep_brand_cols(promo_brand_all)
promo_cross_df = _keep_brand_cols(promo_cross_all)
brand_promo_df = _keep_brands(brand_promo_all, "브랜드")
BLOG_CORRECTED = sov_summary is not None and "블로그" in src_sel

# ══════════════════════════════════════════════════════
# [v2.5.5] 외부 근거 — 2025 서울시민 먹거리조사 참조 연동
# ══════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def load_survey_ref():
    """reference/seoul_food_survey_ref.json 자동 탐색·로드 → dict (없으면 {})."""
    cands = []
    for d in _data_search_dirs():
        cands.append(os.path.join(d, "reference", "seoul_food_survey_ref.json"))
        cands.append(os.path.join(d, "seoul_food_survey_ref.json"))
    for p in cands:
        try:
            if os.path.exists(p):
                with open(p, encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            continue
    return {}


SURVEY_REF = load_survey_ref()

# 리포트 섹션 → 조사 토픽 매핑
REPORT_REF_MAP = {
    "intro":   ["price_perception", "food_cost_burden", "diet_lifestyle"],
    "nss":     ["diet_lifestyle", "nutrition_label"],
    "loyalty": ["info_channels"],
    "trend":   ["coffee", "zero_drinks", "zero_foods", "sweet_drinks"],
    "promo":   ["food_cost_burden", "price_perception"],
    "persona": ["dining_out", "diet_lifestyle"],
    "risk":    ["diet_lifestyle", "wellbeing"],
}


def survey_meta_line():
    m = (SURVEY_REF or {}).get("meta", {})
    if not m:
        return "2025 서울시민 먹거리조사"
    return f"{m.get('title', '2025 서울시민 먹거리조사')} ({m.get('sample', '')})"


def survey_comment(section_key, max_topics=2, max_findings=2):
    """섹션 키 → 해당 조사 토픽의 근거 코멘트 리스트(없으면 [])."""
    topics = (SURVEY_REF or {}).get("topics", {})
    if not topics:
        return []
    out = []
    for tk in REPORT_REF_MAP.get(section_key, [])[:max_topics]:
        t = topics.get(tk)
        if not t:
            continue
        fnd = " / ".join(t.get("findings", [])[:max_findings])
        use = t.get("pcid_use", "")
        line = f"[{t.get('label', tk)}] {fnd}"
        if use:
            line += f" → {use}"
        out.append(line)
    return out


# ══════════════════════════════════════════════════════
# [기능 3] 분석 결과 요약·인사이트 docx 생성
# ══════════════════════════════════════════════════════
def build_summary_docx():
    """[v2.6.1] 사전저작 코멘트(report_commentary.json) 기반 워드 리포트 → bytes.
    PPTX와 동일 스킴: 표제/Executive Summary/5개 챕터(결과·의미·함의·시나리오·시장근거)/마무리.
    차트는 matplotlib 이미지(가능 시)·표(폴백), 폰트 맑은 고딕, 데이터 지문 가드 포함."""
    import io, tempfile
    from docx import Document
    from docx.shared import Pt as DPt, Inches as DInches, RGBColor as DRGB
    from docx.oxml.ns import qn as _dqn
    from docx.enum.text import WD_ALIGN_PARAGRAPH as WDA

    NAVY = DRGB(0x1B, 0x2A, 0x4A); RED = DRGB(0xC0, 0x39, 0x2B)
    GRAY = DRGB(0x71, 0x80, 0x96); GOLD = DRGB(0xB4, 0x8A, 0x3C); DARK = DRGB(0x2D, 0x37, 0x48)

    com = load_report_commentary()
    REG = {}
    for nm in ("brand_df", "absa_df", "loyalty_df", "occ_detail_df", "promo_type_react_df"):
        if nm in globals():
            REG[nm] = globals()[nm]

    PLT = None; KFP = None
    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as _plt
        from matplotlib import font_manager as _fm
        fpath = _kfont_path()
        if fpath:
            _fm.fontManager.addfont(fpath); KFP = _fm.FontProperties(fname=fpath)
        _plt.rcParams["axes.unicode_minus"] = False
        PLT = _plt
    except Exception:
        PLT = None

    doc = Document()
    # 기본 폰트 맑은 고딕
    try:
        st_normal = doc.styles["Normal"]
        st_normal.font.name = "맑은 고딕"; st_normal.font.size = DPt(11)
        st_normal.element.rPr.rFonts.set(_dqn('w:eastAsia'), "맑은 고딕")
    except Exception:
        pass

    def kfont(run, size=None, bold=None, color=None):
        run.font.name = "맑은 고딕"
        rPr = run._element.get_or_add_rPr()
        rF = rPr.find(_dqn('w:rFonts'))
        if rF is None:
            rF = rPr.makeelement(_dqn('w:rFonts'), {}); rPr.append(rF)
        rF.set(_dqn('w:eastAsia'), "맑은 고딕")
        if size is not None: run.font.size = DPt(size)
        if bold is not None: run.font.bold = bold
        if color is not None: run.font.color.rgb = color

    def para(text="", size=11, bold=False, color=None, align=None, after=4, bold_token="파스쿠찌"):
        p = doc.add_paragraph(); p.paragraph_format.space_after = DPt(after)
        if align is not None: p.alignment = align
        import re
        for seg in (re.split(r'(' + bold_token + r')', text) if bold_token else [text]):
            if seg == "": continue
            r = p.add_run(seg); kfont(r, size, bold or seg == bold_token, color)
        return p

    def label_body(label, body, lcolor=NAVY):
        if not body: return
        p = doc.add_paragraph(); p.paragraph_format.space_after = DPt(2)
        r = p.add_run("▪ " + label + "  "); kfont(r, 11, True, lcolor)
        import re
        for seg in re.split(r'(파스쿠찌)', body):
            if seg == "": continue
            r2 = p.add_run(seg); kfont(r2, 11, seg == "파스쿠찌", DARK)

    def render_bar_png(cats, vals, title=None):
        cats = [str(c) for c in cats]; vals = [float(x) for x in vals]
        o = sorted(range(len(vals)), key=lambda i: vals[i])
        cats = [cats[i] for i in o]; vals = [vals[i] for i in o]
        fig, ax = PLT.subplots(figsize=(6.6, 3.6), dpi=180)
        CN = "#1B2A4A"; CR = "#C03929"; CD = "#2D3748"
        for i, (c, val) in enumerate(zip(cats, vals)):
            if c == "파스쿠찌":
                ax.barh(i, val, color=CR, edgecolor=CR, height=0.62, zorder=3)
            elif val < 0:
                ax.barh(i, val, facecolor="white", edgecolor=CN, hatch="////", linewidth=0.6, height=0.62, zorder=3)
            else:
                ax.barh(i, val, color=CN, edgecolor=CN, height=0.62, zorder=3)
        ax.set_yticks(range(len(vals))); ax.set_yticklabels(cats, fontproperties=KFP, fontsize=9)
        for t, c in zip(ax.get_yticklabels(), cats):
            if c == "파스쿠찌": t.set_fontweight("bold"); t.set_color(CR)
        for lab in ax.get_xticklabels():
            if KFP: lab.set_fontproperties(KFP)
            lab.set_fontsize(8)
        span = (max(vals) - min(vals)) or 1
        for i, val in enumerate(vals):
            off = span * 0.013; c = cats[i]
            ax.text(val + (off if val >= 0 else -off), i, f"{val:.1f}", va="center",
                    ha=("left" if val >= 0 else "right"), fontsize=9, fontproperties=KFP,
                    color=(CR if c == "파스쿠찌" else CD), fontweight=("bold" if c == "파스쿠찌" else "normal"), zorder=4)
        ax.axvline(0, color="#888888", linewidth=0.6, zorder=2)
        ax.grid(axis="x", color="#CCCCCC", linewidth=0.4, zorder=0); ax.set_axisbelow(True)
        for sp in ("top", "right", "left"): ax.spines[sp].set_visible(False)
        ax.spines["bottom"].set_color("#BBBBBB"); ax.spines["bottom"].set_linewidth(0.5)
        ax.set_xlim(min(0, min(vals)) * 1.15 - 2, max(0, max(vals)) * 1.18 + 4); ax.margins(y=0.02)
        if title: ax.set_title(title, fontproperties=KFP, fontsize=11, fontweight="bold", color=CD)
        fig.tight_layout(pad=0.4)
        fn = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
        fig.savefig(fn, dpi=180, transparent=False, bbox_inches="tight"); PLT.close(fig)
        return fn

    def add_chart(sec):
        ch = sec.get("chart", {}) or {}
        if ch.get("type") == "barh":
            src = REG.get(ch.get("source")); cat = ch.get("cat"); val = ch.get("val")
            if src is not None and cat in src.columns and val in src.columns:
                d = src[[cat, val]].dropna()
                if PLT is not None:
                    try:
                        fn = render_bar_png(d[cat].tolist(), d[val].tolist(), ch.get("title"))
                        doc.add_picture(fn, width=DInches(6.3)); return
                    except Exception:
                        pass
                # 표 폴백
                try:
                    dd = d.sort_values(val, ascending=False)
                    tb = doc.add_table(rows=1, cols=2); tb.style = "Light Grid Accent 1"
                    h = tb.rows[0].cells; h[0].text = str(cat); h[1].text = str(val)
                    for _, rrow in dd.iterrows():
                        c = tb.add_row().cells
                        c[0].text = str(rrow[cat]); c[1].text = f"{float(rrow[val]):.1f}"
                    return
                except Exception:
                    pass
        # text형: 데이터 요약 bullet
        for b in ch.get("bullets", []):
            p = doc.add_paragraph(style="List Bullet"); r = p.add_run(b); kfont(r, 10.5, False, DARK)

    # ===== 표제 =====
    es = com.get("executive_summary", {}); meta = com.get("meta", {}); fp = meta.get("fingerprint", {}) or {}
    live_docs = len(v) if "v" in globals() else None
    stale = (fp.get("docs") is not None and live_docs is not None and fp.get("docs") != live_docs)
    para("PASCUCCI 브랜드 컨슈머 인텔리전스 리포트", 20, True, NAVY, WDA.CENTER, after=2)
    _period = APP_DATE[:7].replace("-", ".") if isinstance(APP_DATE, str) and len(APP_DATE) >= 7 else "2026.06"
    para(f"{_period}  ·  {APP_VERSION}  ·  분석 문서 {live_docs:,}건", 10, False, GRAY, WDA.CENTER, after=10)
    if stale:
        para(f"⚠ 데이터가 갱신됨(현재 {live_docs}건 ≠ 코멘트 {fp.get('docs')}건) — 코멘트 재생성 필요", 10, True, RED, after=8)

    # ===== Executive Summary =====
    if es:
        para("Executive Summary", 15, True, NAVY, after=4)
        para(es.get("headline", ""), 12, True, DARK, after=8)
        para("핵심 인사이트", 12, True, NAVY, after=2)
        for c in es.get("key_insights", []):
            p = doc.add_paragraph(style="List Bullet"); p.paragraph_format.space_after = DPt(2)
            r = p.add_run(f"[{c.get('area','')}] "); kfont(r, 11, True, GOLD)
            import re
            for seg in re.split(r'(파스쿠찌)', c.get("text", "")):
                if seg == "": continue
                rr = p.add_run(seg); kfont(rr, 11, seg == "파스쿠찌", DARK)
        para("", 4)
        para("Key Recommendations", 12, True, RED, after=2)
        for it in es.get("recommendations", []):
            p = doc.add_paragraph(style="List Bullet"); p.paragraph_format.space_after = DPt(2)
            import re
            for seg in re.split(r'(파스쿠찌)', it):
                if seg == "": continue
                rr = p.add_run(seg); kfont(rr, 11, seg == "파스쿠찌", DARK)

    # ===== 챕터별 섹션 =====
    chno = 0; cur = None
    for sec in com.get("sections", []):
        try:
            ch = sec.get("chapter", "")
            if ch != cur:
                cur = ch; chno += 1
                doc.add_page_break()
                para(f"Chapter {chno}.  {ch}", 16, True, NAVY, after=6)
            para(sec.get("tag", ch), 10, True, GOLD, after=1)
            para(sec.get("headline", ""), 13, True, DARK, after=6)
            add_chart(sec)
            para("", 2)
            label_body("의미 (So what)", sec.get("meaning", ""))
            label_body("함의 (Implication)", sec.get("implication", ""))
            scs = sec.get("scenarios", [])
            if scs:
                p = doc.add_paragraph(); p.paragraph_format.space_after = DPt(1)
                r = p.add_run("▪ 실행 시나리오 (Action)"); kfont(r, 11, True, RED)
                for s2 in scs:
                    pp = doc.add_paragraph(style="List Bullet"); pp.paragraph_format.space_after = DPt(1)
                    import re
                    for seg in re.split(r'(파스쿠찌)', s2):
                        if seg == "": continue
                        rr = pp.add_run(seg); kfont(rr, 11, seg == "파스쿠찌", DARK)
            mv = sec.get("market_view", "")
            if mv:
                p = doc.add_paragraph(); p.paragraph_format.space_after = DPt(8)
                r = p.add_run("시장 근거 · 서울 먹거리조사  "); kfont(r, 9.5, True, GOLD)
                r2 = p.add_run(mv); kfont(r2, 9.5, False, GRAY)
        except Exception:
            continue

    if not com.get("sections"):
        para("reference/report_commentary.json 을 리포에 올리면 분석 서술이 반영됩니다.", 11, False, GRAY)

    para("", 6)
    foot = para(COPYRIGHT if "COPYRIGHT" in globals() else "© PAS DIVISION", 9, False, GRAY, WDA.CENTER)

    buf = io.BytesIO(); doc.save(buf); buf.seek(0)
    return buf.getvalue()


def _report_template_path():
    """리포트 템플릿(insight_report_templ*.pptx) 자동 탐색 — 대소문자·하위폴더·철자 무시."""
    bases = []
    try:
        bases.append(os.path.dirname(os.path.abspath(__file__)))
    except Exception:
        pass
    bases += [os.getcwd(), "."]
    names = ["insight_report_templete.pptx", "insight_report_template.pptx"]
    # 1) 흔한 위치 직접 확인
    for b in bases:
        for sub in ("reference", "templates", "data", ".data", ""):
            for nm in names:
                p = os.path.join(b, sub, nm)
                if os.path.isfile(p):
                    return p
    # 2) 대소문자·철자·폴더 무시 재귀 탐색
    seen = set()
    for b in bases:
        try:
            b = os.path.abspath(b)
        except Exception:
            continue
        if b in seen:
            continue
        seen.add(b)
        for root, dirs, files in os.walk(b):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", ".venv", "venv", "node_modules")]
            for f in files:
                fl = f.lower()
                if fl.endswith(".pptx") and fl.startswith("insight_report_templ"):
                    return os.path.join(root, f)
    return None


def _list_repo_pptx():
    """진단용: 작업 경로 하위 모든 .pptx 상대경로 목록."""
    out = []
    try:
        base = os.getcwd()
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", ".venv", "venv", "node_modules")]
            for f in files:
                if f.lower().endswith(".pptx"):
                    out.append(os.path.relpath(os.path.join(root, f), base))
    except Exception:
        pass
    return out


def _kfont_path():
    """matplotlib용 한글 폰트 경로 탐색(Noto CJK·나눔 등)."""
    import glob
    cands = ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
             "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"]
    for pat in ("/usr/share/fonts/**/*NotoSansCJK*", "/usr/share/fonts/**/*NotoSansKR*",
                "/usr/share/fonts/**/*Nanum*"):
        cands += glob.glob(pat, recursive=True)
    for p in cands:
        if os.path.exists(p):
            return p
    return None


@st.cache_data(show_spinner=False)
def load_report_commentary():
    """reference/report_commentary.json 자동 탐색·로드 → dict(없으면 {})."""
    for d in _data_search_dirs():
        for p in (os.path.join(d, "reference", "report_commentary.json"),
                  os.path.join(d, "report_commentary.json")):
            try:
                if os.path.isfile(p):
                    with open(p, encoding="utf-8") as f:
                        return json.load(f)
            except Exception:
                continue
    return {}


def build_summary_pptx():
    """[v2.6.0] 브랜드 템플릿 + 사전저작 코멘트(report_commentary.json) 기반
    컨설팅형 분석 리포트 → bytes. 표지/Exec Summary/5개 챕터(분석별 결과·의미·함의·시나리오)
    /마지막 장. 차트는 라이브 데이터 이미지, 서술은 코멘트 파일에서 반영(지문 동기화 가드 포함).
    폰트 맑은 고딕(자간 좁게), 챕터 10·헤드라인 18·본문 12·범례·수치 9pt."""
    import io, copy, math, tempfile
    from pptx import Presentation
    from pptx.util import Inches, Pt as PPt
    from pptx.dml.color import RGBColor as PRGB
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.oxml.ns import qn as _qn

    MALGUN = "맑은 고딕"
    NAVY = PRGB(0x1B, 0x2A, 0x4A); RED = PRGB(0xC0, 0x39, 0x2B); GRAY = PRGB(0x71, 0x80, 0x96)
    DARK = PRGB(0x2D, 0x37, 0x48); PANEL = PRGB(0xF4, 0xF6, 0xF9); LINE = PRGB(0xE3, 0xE8, 0xEF)
    GOLD = PRGB(0xB4, 0x8A, 0x3C); BLACK = PRGB(0x11, 0x11, 0x11)
    CARD = PRGB(0xF7, 0xF8, 0xFA); CARDLINE = PRGB(0xDD, 0xE3, 0xEC)

    tpl = _report_template_path()
    if not tpl:
        prs = Presentation(); s = prs.slides.add_slide(prs.slide_layouts[6])
        tf = s.shapes.add_textbox(Inches(0.5), Inches(0.6), Inches(9.0), Inches(5.5)).text_frame
        tf.word_wrap = True
        _found = _list_repo_pptx()
        for i, ln in enumerate([
            "리포트 템플릿을 찾지 못했습니다. (진단 정보)",
            f"· 작업 경로(cwd): {os.getcwd()}",
            f"· 리포 내 .pptx 파일: {', '.join(_found) if _found else '(하나도 없음)'}",
            "→ reference/insight_report_templete.pptx 가 main 브랜치에 올라가 있는지 확인하세요."]):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            r = p.add_run(); r.text = ln; r.font.size = PPt(13)
        buf = io.BytesIO(); prs.save(buf); buf.seek(0); return buf.getvalue()

    com = load_report_commentary()

    # ---- matplotlib 차트 렌더 준비 ----
    PLT = None; KFP = None
    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as _plt
        from matplotlib import font_manager as _fm
        fpath = _kfont_path()
        if fpath:
            _fm.fontManager.addfont(fpath); KFP = _fm.FontProperties(fname=fpath)
        _plt.rcParams["axes.unicode_minus"] = False
        PLT = _plt
    except Exception:
        PLT = None

    REG = {}
    for nm in ("brand_df", "absa_df", "loyalty_df", "occ_detail_df", "promo_type_react_df"):
        if nm in globals():
            REG[nm] = globals()[nm]

    prs = Presentation(tpl)
    SW = prs.slide_width / 914400

    def _setface(rPr):
        rPr.set('spc', '-80')
        for t in ("a:latin", "a:ea", "a:cs"):
            e = rPr.find(_qn(t))
            if e is None: e = rPr.makeelement(_qn(t), {}); rPr.append(e)
            e.set("typeface", MALGUN)

    def kf(run, size, bold=False, color=None):
        run.font.size = PPt(size); run.font.bold = bold
        if color is not None: run.font.color.rgb = color
        _setface(run._r.get_or_add_rPr())

    def addrich(p, text, size, bold, color):
        import re
        for seg in re.split(r'(파스쿠찌)', text):
            if seg == "": continue
            r = p.add_run(); r.text = seg; kf(r, size, bold or seg == "파스쿠찌", color)

    def txt(sl, x, y, w, h, lines, size, bold=False, color=DARK, sp=2):
        tf = sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)).text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.04); tf.margin_top = tf.margin_bottom = Inches(0.02)
        first = True
        for ln in (lines if isinstance(lines, list) else [lines]):
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            p.space_after = PPt(sp); addrich(p, ln, size, bold, color); first = False
        return tf

    def setpara(p, text):
        rs = p.runs
        if rs:
            rs[0].text = text
            for r in rs[1:]: r._r.getparent().remove(r._r)
            _setface(rs[0]._r.get_or_add_rPr())
        else:
            r = p.add_run(); r.text = text; _setface(r._r.get_or_add_rPr())

    def resize_logo(sl, scale=0.9):
        for sh in sl.shapes:
            if sh.shape_type == 13 and sh.width:
                w = sh.width; sh.width = int(w * scale); sh.height = int(sh.height * scale)
                sh.left = sh.left + (w - sh.width)
                return sh.left / 914400
        return SW - 1.5

    def dup(i):
        src = prs.slides[i]; dest = prs.slides.add_slide(src.slide_layout)
        for sh in list(dest.shapes): sh._element.getparent().remove(sh._element)
        for sh in src.shapes: dest.shapes._spTree.append(copy.deepcopy(sh._element))
        for _r, rel in src.part.rels.items():
            if "image" in rel.reltype: dest.part.rels.get_or_add(rel.reltype, rel._target)
        dest._logo_left = resize_logo(dest, 0.9)
        return dest

    def reorder(order):
        lst = prs.slides._sldIdLst; by = {}
        for s in list(lst):
            by[id(prs.part.related_part(s.get(_qn('r:id'))))] = s; lst.remove(s)
        for sl in order: lst.append(by[id(sl.part)])

    def topline(sl, y=0.36):
        x2 = min(getattr(sl, "_logo_left", SW - 1.5) - 0.15, SW - 0.6)
        ln = sl.shapes.add_connector(2, Inches(0.6), Inches(y), Inches(x2), Inches(y))
        ln.line.color.rgb = BLACK; ln.line.width = PPt(0.5); ln.shadow.inherit = False

    def head(sl, tag, headline):
        topline(sl)
        txt(sl, 0.6, 0.45, SW - 1.2, 0.30, tag, 10, bold=True, color=GOLD)
        txt(sl, 0.6, 0.74, SW - 1.2, 0.95, headline, 18, bold=True, color=NAVY)

    def panel(sl, x, y, w, h, fill=PANEL, line=LINE, rounded=False):
        shp = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
        sp = sl.shapes.add_shape(shp, Inches(x), Inches(y), Inches(w), Inches(h))
        sp.fill.solid(); sp.fill.fore_color.rgb = fill; sp.line.color.rgb = line
        sp.line.width = PPt(0.75); sp.shadow.inherit = False
        if rounded:
            try: sp.adjustments[0] = 0.06
            except Exception: pass
        return sp

    def rightcol(sl, sec, x=6.15, y=1.82, w=4.15, h=4.55):
        panel(sl, x, y, w, h); ix = x + 0.16; iw = w - 0.32; cy = y + 0.16
        for lbl, key, col in [("의미 (So what)", "meaning", NAVY), ("함의 (Implication)", "implication", NAVY)]:
            body = sec.get(key, "")
            if not body: continue
            txt(sl, ix, cy, iw, 0.3, "▪ " + lbl, 13, bold=True, color=col, sp=1); cy += 0.32
            txt(sl, ix + 0.02, cy, iw - 0.02, 1.0, body, 12, color=DARK, sp=1)
            cy += 0.205 * max(1, math.ceil(len(body) / 22)) + 0.10
        scs = sec.get("scenarios", [])
        if scs:
            txt(sl, ix, cy, iw, 0.3, "▪ 실행 시나리오 (Action)", 13, bold=True, color=RED, sp=1); cy += 0.32
            for sc in scs:
                txt(sl, ix + 0.02, cy, iw - 0.02, 0.6, "· " + sc, 12, color=DARK, sp=1)
                cy += 0.205 * max(1, math.ceil(len(sc) / 21)) + 0.06

    def market_band(sl, text, y=6.5):
        if not text: return
        sp = panel(sl, 0.55, y, SW - 1.1, 0.64, fill=PRGB(0xF7, 0xF2, 0xE8), line=PRGB(0xE6, 0xD8, 0xBE))
        tf = sp.text_frame; tf.word_wrap = True
        tf.margin_left = Inches(0.12); tf.margin_right = Inches(0.12)
        tf.margin_top = Inches(0.05); tf.margin_bottom = Inches(0.05)
        p = tf.paragraphs[0]; r = p.add_run(); r.text = "시장 근거 · 서울 먹거리조사   "; kf(r, 10, True, GOLD)
        addrich(p, text, 10, False, GRAY)

    def textbox_left(sl, title, bullets, x=0.55, y=1.82, w=5.35, h=4.55):
        panel(sl, x, y, w, h, fill=PRGB(0xFB, 0xFC, 0xFD), line=LINE)
        if title:
            txt(sl, x + 0.18, y + 0.16, w - 0.36, 0.32, title, 12, bold=True, color=NAVY)
        cy = y + 0.62
        for b in bullets:
            txt(sl, x + 0.18, cy, w - 0.36, 0.6, ("· " + b) if b[:1] not in ("·", "▪", "→", "(") else b, 12, color=DARK, sp=1)
            cy += 0.205 * max(1, math.ceil(len(b) / 30)) + 0.10

    def render_bar_png(cats, vals, title=None, w=5.5, h=4.3):
        cats = [str(c) for c in cats]; vals = [float(x) for x in vals]
        o = sorted(range(len(vals)), key=lambda i: vals[i])
        cats = [cats[i] for i in o]; vals = [vals[i] for i in o]
        fig, ax = PLT.subplots(figsize=(w, h), dpi=200)
        CN = "#1B2A4A"; CR = "#C03929"; CD = "#2D3748"
        for i, (c, val) in enumerate(zip(cats, vals)):
            if c == "파스쿠찌":
                ax.barh(i, val, color=CR, edgecolor=CR, height=0.62, zorder=3)
            elif val < 0:
                ax.barh(i, val, facecolor="white", edgecolor=CN, hatch="////", linewidth=0.6, height=0.62, zorder=3)
            else:
                ax.barh(i, val, color=CN, edgecolor=CN, height=0.62, zorder=3)
        ax.set_yticks(range(len(vals)))
        ax.set_yticklabels(cats, fontproperties=KFP, fontsize=9)
        for t, c in zip(ax.get_yticklabels(), cats):
            if c == "파스쿠찌": t.set_fontweight("bold"); t.set_color(CR)
        for lab in ax.get_xticklabels():
            if KFP: lab.set_fontproperties(KFP)
            lab.set_fontsize(8)
        span = (max(vals) - min(vals)) or 1
        for i, val in enumerate(vals):
            off = span * 0.013; c = cats[i]
            ax.text(val + (off if val >= 0 else -off), i, f"{val:.1f}",
                    va="center", ha=("left" if val >= 0 else "right"), fontsize=9,
                    fontproperties=KFP, color=(CR if c == "파스쿠찌" else CD),
                    fontweight=("bold" if c == "파스쿠찌" else "normal"), zorder=4)
        ax.axvline(0, color="#888888", linewidth=0.6, zorder=2)
        ax.grid(axis="x", color="#CCCCCC", linewidth=0.4, zorder=0); ax.set_axisbelow(True)
        for sp in ("top", "right", "left"): ax.spines[sp].set_visible(False)
        ax.spines["bottom"].set_color("#BBBBBB"); ax.spines["bottom"].set_linewidth(0.5)
        ax.set_xlim(min(0, min(vals)) * 1.15 - 2, max(0, max(vals)) * 1.18 + 4); ax.margins(y=0.02)
        if title:
            ax.set_title(title, fontproperties=KFP, fontsize=11, fontweight="bold", color=CD)
        fig.tight_layout(pad=0.4)
        fn = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
        fig.savefig(fn, dpi=200, transparent=True, bbox_inches="tight"); PLT.close(fig)
        return fn

    def _native_bar(sl, cats, vals, title):
        """matplotlib 미사용 폴백 — 네이티브 PPT 가로막대(외부 의존성 없음, PowerPoint에서 항상 렌더)."""
        from pptx.chart.data import CategoryChartData
        from pptx.enum.chart import XL_CHART_TYPE
        pairs = sorted(zip([str(c) for c in cats], [float(x) for x in vals]), key=lambda t: t[1])
        cs = [p[0] for p in pairs]; vs = [p[1] for p in pairs]
        cd = CategoryChartData(); cd.categories = cs; cd.add_series(title or "값", vs)
        gf = sl.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(0.5), Inches(1.85), Inches(5.6), Inches(4.3), cd)
        chart = gf.chart; chart.has_legend = False
        try:
            chart.font.size = PPt(9); chart.font.name = MALGUN
            txPr = chart._chartSpace.find(_qn('c:txPr'))
            if txPr is not None:
                for d in txPr.iter(_qn('a:defRPr')):
                    for t in ('a:ea', 'a:cs'):
                        e = d.find(_qn(t))
                        if e is None: e = d.makeelement(_qn(t), {}); d.append(e)
                        e.set('typeface', MALGUN)
        except Exception: pass
        try:
            ser = chart.series[0]
            ser.format.fill.solid(); ser.format.fill.fore_color.rgb = NAVY
            if "파스쿠찌" in cs:
                pt = ser.points[cs.index("파스쿠찌")]
                pt.format.fill.solid(); pt.format.fill.fore_color.rgb = RED
        except Exception: pass
        try:
            plot = chart.plots[0]; plot.has_data_labels = True
            plot.data_labels.font.size = PPt(9); plot.data_labels.font.name = MALGUN
            plot.data_labels.font.color.rgb = DARK
            plot.data_labels.number_format = '0.0'; plot.data_labels.number_format_is_linked = False
        except Exception: pass
        try:
            va = chart.value_axis; va.has_major_gridlines = True
            va.major_gridlines.format.line.color.rgb = PRGB(0xCC, 0xCC, 0xCC)
            va.major_gridlines.format.line.width = PPt(0.4)
            chart.category_axis.has_major_gridlines = False
        except Exception: pass

    def chart_left(sl, sec):
        ch = sec.get("chart", {}) or {}
        ctype = ch.get("type", "text")
        if ctype == "barh":
            src = REG.get(ch.get("source"))
            cat = ch.get("cat"); val = ch.get("val")
            if src is not None and cat in src.columns and val in src.columns:
                d = src[[cat, val]].dropna()
                cats = d[cat].tolist(); vals = d[val].tolist()
                if PLT is not None:
                    try:
                        fn = render_bar_png(cats, vals, ch.get("title"))
                        sl.shapes.add_picture(fn, Inches(0.5), Inches(1.78), width=Inches(5.6))
                        return
                    except Exception:
                        pass
                try:
                    _native_bar(sl, cats, vals, ch.get("title")); return
                except Exception:
                    pass
            textbox_left(sl, ch.get("title"), ["(차트 데이터를 불러올 수 없어 요약으로 대체합니다.)"])
        else:
            textbox_left(sl, ch.get("title"), ch.get("bullets", []))

    # ===== 표지 =====
    cover = prs.slides[0]; closing = prs.slides[2]; body = []
    es = com.get("executive_summary", {})
    meta = com.get("meta", {}); fp = meta.get("fingerprint", {}) or {}
    live_docs = len(v) if "v" in globals() else None
    stale = (fp.get("docs") is not None and live_docs is not None and fp.get("docs") != live_docs)
    _period = APP_DATE[:7].replace("-", ".") if isinstance(APP_DATE, str) and len(APP_DATE) >= 7 else "2026.06"
    cover_map = {"분석 주제를 입력하세요": "PASCUCCI 브랜드 컨슈머 인텔리전스 리포트",
                 "YYYY.MM": _period, "1.0": APP_VERSION, "Draft / Final": "Final", "Team / Owner": "PAS DIVISION"}
    for sh in cover.shapes:
        if not sh.has_text_frame: continue
        for p in sh.text_frame.paragraphs:
            if p.text.strip() in cover_map: setpara(p, cover_map[p.text.strip()])

    # ===== Executive Summary =====
    if es:
        s = dup(1); head(s, "EXECUTIVE SUMMARY", es.get("headline", "핵심 요약"))
        if stale:
            txt(s, 0.6, 1.55, SW - 1.2, 0.26, f"⚠ 데이터가 갱신됨(현재 {live_docs}건 ≠ 코멘트 {fp.get('docs')}건) — 코멘트 재생성 필요", 10, bold=True, color=RED)
        ky = 1.9 if not stale else 2.02
        txt(s, 0.6, ky, SW - 1.2, 0.34, "핵심 인사이트", 13, bold=True, color=NAVY)
        cards = es.get("key_insights", []); n = max(1, len(cards)); gap = 0.25
        cw = (SW - 1.2 - gap * (n - 1)) / n; cx = 0.6; cyy = ky + 0.42; chh = 1.9
        for c in cards:
            panel(s, cx, cyy, cw, chh, fill=CARD, line=CARDLINE, rounded=True)
            txt(s, cx + 0.14, cyy + 0.13, cw - 0.28, 0.3, c.get("area", ""), 10, bold=True, color=GOLD, sp=1)
            txt(s, cx + 0.14, cyy + 0.5, cw - 0.28, chh - 0.55, c.get("text", ""), 12, color=DARK, sp=1)
            cx += cw + gap
        ry0 = cyy + chh + 0.25
        txt(s, 0.6, ry0, SW - 1.2, 0.34, "Key Recommendations", 13, bold=True, color=RED)
        ry = ry0 + 0.43
        for it in es.get("recommendations", []):
            txt(s, 0.62, ry, SW - 1.25, 0.5, "· " + it, 12, color=DARK, sp=1)
            ry += 0.205 * max(1, math.ceil(len(it) / 56)) + 0.10
        body.append(s)

    # ===== 챕터별 섹션 =====
    chno = 0; cur = None
    for sec in com.get("sections", []):
        try:
            ch = sec.get("chapter", "")
            if ch != cur:
                cur = ch; chno += 1
                d = dup(1)
                txt(d, 0.6, 2.85, SW - 1.2, 0.5, f"CHAPTER {chno}", 16, bold=True, color=GOLD)
                txt(d, 0.6, 3.35, SW - 1.2, 0.9, ch, 30, bold=True, color=NAVY)
                subs = [x.get("tag", "").split(" · ")[-1] for x in com["sections"] if x.get("chapter") == ch]
                txt(d, 0.6, 4.45, SW - 1.2, 0.5, " · ".join(subs), 13, color=GRAY)
                body.append(d)
            s = dup(1); head(s, sec.get("tag", ch), sec.get("headline", ""))
            chart_left(s, sec)
            rightcol(s, sec)
            market_band(s, sec.get("market_view", ""))
            body.append(s)
        except Exception:
            continue

    if not body:
        s = dup(1); head(s, "NOTICE", "코멘트 파일을 찾지 못했습니다")
        textbox_left(s, "안내", ["reference/report_commentary.json 을 리포에 올리면 분석 서술이 반영됩니다.",
                                 "차트·수치는 라이브 데이터에서 생성됩니다."])
        body.append(s)

    reorder([cover] + body + [closing])
    buf = io.BytesIO(); prs.save(buf); buf.seek(0)
    return buf.getvalue()


with report_dl_slot.container():
    st.markdown("**📄 분석 리포트 다운로드**")
    # [v2.3.4] PPT를 기본 리포트로(상단), 시사점·Lessons 포함
    if PPTX_AVAILABLE:
        try:
            pptx_bytes = build_summary_pptx()
            st.download_button(
                label="📊 분석 리포트 (.pptx · 권장)",
                data=pptx_bytes,
                file_name=f"PASCUCCI_분석리포트_{APP_DATE}.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True,
            )
        except Exception as e:
            st.caption(f"pptx 생성 오류: {e}")
    else:
        st.caption("📊 PPT 리포트(권장): `python-pptx` 미설치 상태입니다. "
                   "`pip install python-pptx` 후 앱을 재시작하세요 "
                   "(requirements.txt 포함 — `pip install -r requirements.txt`).")
    # docx는 보조 포맷
    if DOCX_AVAILABLE:
        try:
            docx_bytes = build_summary_docx()
            st.download_button(
                label="📄 분석 리포트 (.docx · 보조)",
                data=docx_bytes,
                file_name=f"PASCUCCI_분석리포트_{APP_DATE}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        except Exception as e:
            st.caption(f"docx 생성 오류: {e}")

# [v2.3.1] MI 뷰 라우팅 — 대시보드가 아니면 MI 화면 표시 후 종료
if st.session_state.get("view", "dashboard") != "dashboard":
    render_market_intelligence(st.session_state["view"], v, brand_df)
    st.markdown("---")
    st.markdown(f"<p style='text-align:center;color:#A0AEC0;font-size:11px;'>{COPYRIGHT}</p>",
                unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════
# 탭 구성 — 12개
# ══════════════════════════════════════════════════════
# [v2.5.1] 탭은 카테고리별 렌더 함수 + 하단 디스패치(_CATS)로 구성

# ════════════════════════════════════════════════════
# [v2.7.0] 해설 박스 자동 생성 — 고정 문구 대신 그때그때의 계산 결과로 작성
#   각 함수는 (박스 종류, 제목, 본문 HTML)을 돌려주고 _box()가 그린다.
# ════════════════════════════════════════════════════
def _box(kind, title, body):
    st.markdown(f"<div class='{kind}-box'><b>{title}</b><br>{body}</div>", unsafe_allow_html=True)


_RADAR_AXES = ["SOV 규모", "NSS 평판", "맛·품질", "공간·분위기", "가격·가성비", "디카페인 관심", "브랜드 이미지"]


@st.cache_data(show_spinner=False)
def _radar_metrics(_v, _bdf, sig=""):
    """[v2.7.0] 포지셔닝 레이더 실측 지표 (원값). SOV·NSS는 보정 지표, 속성 축은 해당 속성 언급 글의 NSS."""
    rows = {}
    for _, r in _bdf.iterrows():
        b = r["브랜드"]
        bd = _v[_v["brands"].apply(lambda x: b in x)]
        vals = {"SOV 규모": float(r["SOV_전체"]), "NSS 평판": float(r["NSS"])}
        for ax, attr in [("맛·품질", "맛·품질"), ("공간·분위기", "공간·분위기"),
                         ("가격·가성비", "가격·가성비"), ("브랜드 이미지", "브랜드이미지")]:
            sub = bd[bd["full_text"].str.contains("|".join(ATTR_DICT[attr]), na=False)]
            vals[ax] = (((sub["sentiment"] == "긍정").sum() - (sub["sentiment"] == "부정").sum()) / len(sub) * 100
                        if len(sub) >= 10 else np.nan)
        vals["디카페인 관심"] = (float(bd["full_text"].str.contains("디카페인|디카페", na=False).mean() * 100)
                             if len(bd) >= 10 else np.nan)
        rows[b] = vals
    if not rows:
        return _RADAR_AXES, None
    return _RADAR_AXES, pd.DataFrame(rows).T[_RADAR_AXES]


def _mlabel(m):
    return str(m).replace("-", ".")


def _sov_method_text():
    if BLOG_CORRECTED:
        return ("블로그 언급량은 네이버 검색 상한(검색어당 최신 1,000건)을 보정한 6개월 환산치, 커뮤니티는 실측 건수입니다. "
                "긍정·부정 비중은 브랜드별 수집 표본에서 잰 비율을 적용했습니다.")
    if "블로그" in src_sel:
        return ("⚠ 보정 정보(sov_summary)가 없어 블로그는 수집 건수 기준입니다. 검색 상한 때문에 언급이 많은 "
                "브랜드일수록 실제보다 작게 잡힐 수 있습니다.")
    return "커뮤니티 실측 건수 기준입니다."


def _volume_note():
    st.caption("ⓘ " + _sov_method_text())


def _wavg_nss(df):
    n = df["언급량"].sum()
    return float((df["긍정"].sum() - df["부정"].sum()) / n * 100) if n > 0 else float("nan")


def _ins_nss_shift(mn):
    """최근 달 NSS가 직전 달들 평균 대비 가장 크게 움직인 브랜드."""
    if mn is None or len(mn) == 0:
        return ("insight", "최근 평판 변화", "월별로 비교할 만큼 표본이 쌓인 브랜드가 아직 없습니다.")
    best = None
    for b, g in mn.sort_values("월").groupby("브랜드"):
        if len(g) < 2:
            continue
        last, prev = g.iloc[-1], g.iloc[:-1]
        base = float(prev["NSS"].mean())
        delta = float(last["NSS"]) - base
        if best is None or abs(delta) > abs(best["delta"]):
            best = {"b": b, "m": last["월"], "nss": float(last["NSS"]), "n": int(last["문서수"]),
                    "base": base, "k": len(prev), "delta": delta}
    if best is None:
        return ("insight", "최근 평판 변화", "월별로 비교할 만큼 표본이 쌓인 브랜드가 아직 없습니다.")
    d = best["delta"]
    if abs(d) < 5:
        return ("insight", "최근 평판 변화",
                f"최근 달 NSS 변동이 가장 큰 브랜드도 <b>{best['b']}</b> {d:+.1f}p 수준으로, 뚜렷한 평판 변화는 없습니다.")
    kind = "danger" if d < 0 else "success"
    return (kind, f"최근 평판 변화가 가장 큰 브랜드: {best['b']}",
            f"{_mlabel(best['m'])} NSS <b>{best['nss']:+.1f}</b> (표본 {best['n']}건) · "
            f"직전 {best['k']}개월 평균 <b>{best['base']:+.1f}</b><br>"
            f"→ <b>{abs(d):.1f}p {'하락' if d < 0 else '상승'}</b>")


def _ins_nss_market(bdf):
    if bdf is None or len(bdf) < 2:
        return ("insight", "시장 전반 관점", "비교할 브랜드가 2개 이상 필요합니다.")
    s = bdf.sort_values("NSS", ascending=False).reset_index(drop=True)
    avg = float(bdf["NSS"].mean())
    lines = [f"• 평판 1위: <b>{s.iloc[0]['브랜드']}</b> (NSS {s.iloc[0]['NSS']:+.1f})",
             f"• 평판 최하위: <b>{s.iloc[-1]['브랜드']}</b> (NSS {s.iloc[-1]['NSS']:+.1f})",
             f"• 브랜드 평균 NSS: <b>{avg:+.1f}</b>"]
    if "파스쿠찌" in s["브랜드"].values:
        r = int(s.index[s["브랜드"] == "파스쿠찌"][0]) + 1
        pn = float(s.loc[s["브랜드"] == "파스쿠찌", "NSS"].iloc[0])
        lines.append(f"• 파스쿠찌: {len(s)}개 중 <b>{r}위</b> (평균 대비 {pn - avg:+.1f}p)")
    return ("insight", "시장 전반 관점", "<br>".join(lines))


def _ins_group(gname, gbrands, bdf):
    g = bdf[bdf["브랜드"].isin(gbrands)] if bdf is not None and len(bdf) else bdf
    if g is None or len(g) == 0:
        return ("insight", f"{gname} 관점", "표시 중인 해당 브랜드가 없습니다.")
    o = bdf[~bdf["브랜드"].isin(gbrands)]
    g_nss, o_nss = _wavg_nss(g), (_wavg_nss(o) if len(o) else float("nan"))
    g_sov = float(g["SOV_전체"].sum())
    top = g.sort_values("NSS", ascending=False).iloc[0]
    names = "·".join(g["브랜드"].tolist())
    gap = g_nss - o_nss if o_nss == o_nss else float("nan")
    if gap != gap:
        verdict, kind = "", "insight"
    elif gap >= 5:
        verdict, kind = f"나머지 브랜드보다 평판이 <b>{gap:.1f}p 높음</b>", "success"
    elif gap <= -5:
        verdict, kind = f"나머지 브랜드보다 평판이 <b>{abs(gap):.1f}p 낮음</b>", "warning"
    else:
        verdict, kind = f"나머지 브랜드와 평판 차이 {gap:+.1f}p로 비슷한 수준", "insight"
    body = (f"{names}: 합산 SOV <b>{g_sov:.1f}%</b> · 평균 NSS <b>{g_nss:+.1f}</b>"
            + (f" (그 외 {o_nss:+.1f})" if o_nss == o_nss else "") + "<br>"
            + (verdict + "<br>" if verdict else "")
            + f"묶음 내 평판 1위: <b>{top['브랜드']}</b> (NSS {top['NSS']:+.1f})")
    return (kind, f"{gname} 관점", body)


def _ins_sov_leader(bdf):
    if bdf is None or len(bdf) == 0:
        return ("insight", "SOV 1위 브랜드", "표시할 브랜드가 없습니다.")
    top = bdf.sort_values("SOV_전체", ascending=False).iloc[0]
    gap = float(top["SOV_부정"] - top["SOV_전체"])
    eff = bdf.assign(_e=bdf["SOV_긍정"] - bdf["SOV_전체"]).sort_values("_e", ascending=False).iloc[0]
    head = (f"<b>{top['브랜드']}</b>: 전체 SOV {top['SOV_전체']:.1f}% · 긍정 SOV {top['SOV_긍정']:.1f}% · "
            f"부정 SOV {top['SOV_부정']:.1f}%")
    if gap > 3:
        kind, title, msg = "danger", f"{top['브랜드']}: 규모보다 부정 담론 비중이 큼", f"부정 SOV가 전체 SOV보다 <b>{gap:.1f}p</b> 높아 담론의 양과 질이 어긋남"
    elif gap < -3:
        kind, title, msg = "success", f"{top['브랜드']}: 규모 대비 부정 담론이 적음", f"부정 SOV가 전체 SOV보다 <b>{abs(gap):.1f}p</b> 낮음"
    else:
        kind, title, msg = "insight", f"SOV 1위 {top['브랜드']}", "부정 SOV가 전체 SOV와 비슷해 규모만큼의 부정 담론 수준"
    tail = (f"<br>규모 대비 긍정 담론이 가장 많은 브랜드: <b>{eff['브랜드']}</b> "
            f"(긍정 SOV − 전체 SOV {eff['SOV_긍정'] - eff['SOV_전체']:+.1f}p)")
    return (kind, title, head + "<br>" + msg + tail)


def _ins_sov_target(bdf_all, target="파스쿠찌"):
    if bdf_all is None or len(bdf_all) == 0 or target not in bdf_all["브랜드"].values:
        return ("insight", f"{target} 위치", f"{target} 언급이 부족해 비교할 수 없습니다.")
    s = bdf_all.sort_values("SOV_전체", ascending=False).reset_index(drop=True)
    r = int(s.index[s["브랜드"] == target][0]) + 1
    p = s[s["브랜드"] == target].iloc[0]
    lo, hi = p["SOV_전체"] * 0.5, p["SOV_전체"] * 2.0
    peers = s[(s["브랜드"] != target) & s["SOV_전체"].between(lo, hi)].head(4)
    peer_txt = ", ".join(f"{x['브랜드']}({x['SOV_전체']:.1f}%·NSS {x['NSS']:+.0f})" for _, x in peers.iterrows()) or "없음"
    eff = float(p["SOV_긍정"] - p["SOV_전체"])
    kind = "success" if eff >= 0 else "warning"
    msg = ("긍정 SOV가 전체 SOV보다 높아 <b>규모 대비 긍정 담론 우위</b>" if eff >= 0
           else "긍정 SOV가 전체 SOV보다 낮아 <b>규모 대비 긍정 담론 부족</b>")
    return (kind, f"{target} 위치",
            f"전체 SOV <b>{p['SOV_전체']:.1f}%</b> ({len(s)}개 중 {r}위) · 긍정 SOV {p['SOV_긍정']:.1f}% · "
            f"NSS {p['NSS']:+.1f}<br>{msg} ({eff:+.1f}p)<br>비슷한 규모(0.5~2배): {peer_txt}")


_RISK_WORDS = sorted({k for ks in RISK_PATTERNS.values() for k in ks}, key=len, reverse=True)


def _is_risk_kw(kw):
    return any(k in kw for k in _RISK_WORDS)


def _burst_period_text():
    if not WIN_END:
        return "최근 구간 vs 이전 구간"
    r0, we, b0, b1 = _period_bounds(WIN_START, WIN_END, BURST_RECENT_DAYS, BURST_BASE_DAYS)
    return (f"최근 {BURST_RECENT_DAYS}일({r0:%m.%d}~{we:%m.%d}) vs 직전 {(b1 - b0).days + 1}일"
            f"({b0:%m.%d}~{b1:%m.%d}, {BURST_RECENT_DAYS}일 환산)")


def _burst_is_risk(r):
    """리스크 유형 단어이거나, 최근 그 단어가 든 글이 긍정보다 부정이 많으면 위험 신호."""
    neg, pos = float(r.get("부정비중", 0) or 0), float(r.get("긍정비중", 0) or 0)
    return _is_risk_kw(r["키워드"]) or neg > pos


def _ins_burst(bdf):
    if bdf is None or len(bdf) == 0:
        return [("insight", "급증 신호", "비교 구간에 충분한 데이터가 없어 급증 키워드를 계산하지 않았습니다.")]
    risk = bdf.apply(_burst_is_risk, axis=1)
    rk, up = bdf[risk], bdf[~risk].head(3)

    def _rate(r):   # 직전에 거의 없던 단어는 배수 대신 '신규 등장'으로 표기
        prev = float(r.get("직전(30일 환산)", 0) or 0)
        if prev < 1:
            return f"신규 등장 (최근 {int(r['최근30일'])}회 · 직전 거의 없음)"
        return f"{r['증가율(배)']:.1f}배 (최근 {int(r['최근30일'])}회 · 직전 {prev:.1f}회)"
    out = []
    if len(up):
        out.append(("success", "상승 신호 (긍정·중립 맥락의 급증 상위)", "<br>".join(
            f"• <b>{r['키워드']}</b> {_rate(r)}" for _, r in up.iterrows())))
    if len(rk):
        out.append(("danger", "위험 신호 (부정 맥락·리스크 단어의 급증)", "<br>".join(
            f"• <b>{r['키워드']}</b> {_rate(r)} · 부정 글 비중 {r.get('부정비중', 0):.0f}%"
            for _, r in rk.head(4).iterrows()) + "<br>원문은 '리스크 탐지' 탭에서 확인하세요."))
    else:
        out.append(("insight", "위험 신호", "급증 키워드 중 부정 맥락이 우세하거나 리스크 유형(정치·이슈, 환불, 가격, 품질 실망 등)에 해당하는 단어는 없습니다."))
    return out


def _ins_pmi(pdf, min_co=5):
    if pdf is None or len(pdf) == 0:
        return [("insight", "브랜드 연관", "브랜드 공출현 데이터가 부족합니다.")]
    ok = pdf[(pdf["공출현수"] >= min_co) & (pdf["PMI"] > -5)]
    out = []
    if len(ok):
        top = ok[ok["PMI"] > 0].sort_values("PMI", ascending=False).head(3)
        if len(top) == 0:
            out.append(("insight", "함께 비교되는 브랜드 쌍", "우연 수준보다 자주 함께 언급되는 브랜드 쌍(PMI > 0)이 없습니다."))
        else:
            out.append(("insight", "함께 비교되는 브랜드 쌍 (우연보다 자주 함께 언급)", "<br>".join(
                f"• <b>{r['브랜드1']} ↔ {r['브랜드2']}</b> PMI {r['PMI']:.2f} (함께 언급 {int(r['공출현수'])}건)"
                for _, r in top.iterrows())))
        long = pd.concat([ok[["브랜드1", "PMI"]].rename(columns={"브랜드1": "b"}),
                          ok[["브랜드2", "PMI"]].rename(columns={"브랜드2": "b"})])
        avg = long.groupby("b")["PMI"].mean().sort_values()
        if len(avg):
            lo = avg.index[0]
            out.append(("warning", f"독자적으로 회자되는 브랜드: {lo}",
                        f"함께 언급되는 다른 브랜드와의 평균 PMI {avg.iloc[0]:.2f}로 가장 낮음 → 비교 대상보다 "
                        f"단독 화제로 이야기되는 경향"))
        pas = ok[((ok["브랜드1"] == "파스쿠찌") | (ok["브랜드2"] == "파스쿠찌")) & (ok["PMI"] > 0)].sort_values("PMI", ascending=False).head(2)
        if len(pas):
            names = [r["브랜드2"] if r["브랜드1"] == "파스쿠찌" else r["브랜드1"] for _, r in pas.iterrows()]
            out[0] = (out[0][0], out[0][1], out[0][2] + "<br>파스쿠찌와 가장 함께 비교되는 브랜드: <b>" + ", ".join(names) + "</b>")
    else:
        out.append(("insight", "브랜드 연관", f"함께 언급 {min_co}건 이상인 브랜드 쌍이 없습니다."))
    return out


def _ins_occasion(mat, target="파스쿠찌"):
    if mat is None or len(mat) == 0 or target not in getattr(mat, "columns", []):
        return ("insight", f"{target} 소비 상황", f"{target} 언급이 부족해 상황별 비교를 하지 않았습니다.")
    m = mat.drop(index=[i for i in mat.index if i == "기타"], errors="ignore").astype(float)
    tot_t, tot_all = m[target].sum(), m.values.sum()
    if tot_t < 10 or tot_all <= 0:
        return ("insight", f"{target} 소비 상황", f"{target}의 상황별 언급이 10건 미만이라 비교를 생략했습니다.")
    m = m[m.sum(axis=1) >= 20]                       # 시장 언급 20건 미만 상황은 비교에서 제외
    idx = (m[target] / tot_t) / (m.sum(axis=1) / tot_all)
    idx = idx.replace([np.inf, -np.inf], np.nan).dropna().sort_values(ascending=False)
    lead = {occ: m.loc[occ].idxmax() for occ in m.index if m.loc[occ].sum() > 0}
    st_ = idx[(idx >= 1.15) & (m[target].reindex(idx.index) >= 3)].head(2)
    wk_ = idx[idx <= 0.85].tail(2)
    strong = ", ".join(f"{o}({x:.2f})" for o, x in st_.items()) or "뚜렷한 강점 없음(지수 1.15 이상 없음)"
    weak = ", ".join(f"{o}({x:.2f})" for o, x in wk_.items()) or "뚜렷한 약점 없음(지수 0.85 이하 없음)"
    big = m.sum(axis=1).sort_values(ascending=False).head(2).index
    lead_txt = ", ".join(f"{o} → {lead[o]}" for o in big if o in lead)
    return ("insight", f"{target} 소비 상황 포지션",
            f"상황 비중 지수(시장 평균=1.00) 강점: <b>{strong}</b> · 약점: <b>{weak}</b><br>"
            f"언급이 가장 많은 상황의 1위 브랜드: {lead_txt}<br>"
            f"지수가 낮은 상황은 경쟁사가 선점한 영역, 높은 상황은 {target}가 차별화할 수 있는 영역으로 봅니다.")


def _ins_occasion_detail(mat, odf, target="파스쿠찌"):
    kind, title, body = _ins_occasion(mat, target)
    extra = []
    if odf is not None and len(odf):
        big = odf.sort_values("언급량", ascending=False).head(3)
        good = odf[odf["언급량"] >= 20].sort_values("NSS", ascending=False).head(2)
        extra.append("언급 많은 상황: " + ", ".join(f"{r['소비맥락']}({int(r['언급량']):,}건)" for _, r in big.iterrows()))
        if len(good):
            extra.append("호감(NSS) 높은 상황: " + ", ".join(f"{r['소비맥락']}(NSS {r['NSS']:+.0f})" for _, r in good.iterrows()))
    return ("success", "전략 활용 — " + title, body + ("<br>" + "<br>".join(extra) if extra else ""))


def _ins_promo(react_df, recent_df, bp_df, target="파스쿠찌"):
    lines = []
    if react_df is not None and len(react_df) and "반응강도지표" in react_df.columns:
        rr = react_df[react_df["언급량"] >= 10].sort_values("반응강도지표", ascending=False).head(2)
        if len(rr):
            lines.append("반응 강도 상위 촉진: " + ", ".join(
                f"<b>{r['프로모션']}</b>(지표 {r['반응강도지표']:.0f}, {int(r['언급량']):,}건)" for _, r in rr.iterrows()))
    if recent_df is not None and len(recent_df):
        rt = recent_df.sort_values("최근언급", ascending=False).head(2)
        lines.append("최근 60일 화제 촉진과 주도 브랜드: " + ", ".join(
            f"{r['프로모션']} → {r['주력브랜드']}" for _, r in rt.iterrows()))
    if bp_df is not None and len(bp_df) and target in bp_df["브랜드"].values:
        s_ = bp_df.sort_values("프로모션비중", ascending=False).reset_index(drop=True)
        r = int(s_.index[s_["브랜드"] == target][0]) + 1
        val = float(s_.loc[s_["브랜드"] == target, "프로모션비중"].iloc[0])
        lines.append(f"{target} 글 중 프로모션 언급 비중 <b>{val:.1f}%</b> ({len(s_)}개 중 {r}위, "
                     f"평균 {s_['프로모션비중'].mean():.1f}%)")
    if not lines:
        return ("insight", "전략 활용", "프로모션 데이터가 부족합니다.")
    return ("success", "전략 활용 — 반응 좋은 촉진은 도입, 경쟁사 주도 영역은 차별화", "<br>".join(lines))


def _ins_loyalty(ldf):
    if ldf is None or len(ldf) < 2:
        return ("insight", "로열티 해석", "비교할 브랜드가 부족합니다.")
    most = ldf.sort_values("찐팬문서수", ascending=False).iloc[0]
    rank = ldf.sort_values("로열티지수", ascending=False).reset_index(drop=True)
    r = int(rank.index[rank["브랜드"] == most["브랜드"]][0]) + 1
    top = rank.iloc[0]
    if r > 1:
        body = (f"충성 신호 글이 가장 많은 <b>{most['브랜드']}</b>({int(most['찐팬문서수']):,}건)는 로열티 지수 "
                f"<b>{len(rank)}개 중 {r}위</b>입니다. 로열티 지수·찐팬 비율은 '충성 신호 글 ÷ 그 브랜드 전체 글' 비율이라, "
                f"언급이 많은 브랜드는 충성 글이 많아도 비율로는 희석됩니다.<br>"
                f"충성도 밀도 1위: <b>{top['브랜드']}</b> (지수 {top['로열티지수']:.1f} · 찐팬 {top['찐팬비율']:.1f}%). "
                f"'많이 회자되는 브랜드'와 '찐팬이 두터운 브랜드'를 구분해서 보세요.")
        return ("warning", f"왜 {most['브랜드']}는 충성 글 수는 많은데 지수는 {r}위일까?", body)
    return ("success", f"{most['브랜드']}: 충성 글 수·밀도 모두 1위",
            f"충성 신호 글 {int(most['찐팬문서수']):,}건, 로열티 지수 {most['로열티지수']:.1f}로 규모와 밀도 모두 앞섭니다.")


def _ins_topics(tc, target="파스쿠찌"):
    if tc is None:
        return ("insight", "활용", "토픽 데이터가 부족합니다.")
    tb = tc["tb_mat"].astype(float)
    labels = tc.get("topic_labels") or tc.get("topic_meanings") or [str(i) for i in range(len(tb))]
    if target not in tb.columns or tb[target].sum() < 10:
        return ("insight", "활용", f"{target} 언급이 부족해 토픽별 비교를 생략했습니다.")
    share_t = tb[target] / tb[target].sum()
    share_all = tb.sum(axis=1) / tb.values.sum()
    idx = (share_t / share_all).replace([np.inf, -np.inf], np.nan)
    order = idx.dropna().sort_values()
    if len(order) == 0:
        return ("insight", "활용", "비교할 토픽이 없습니다.")
    lo, hi = order.index[0], order.index[-1]
    li, hiidx = int(str(lo).lstrip("T")), int(str(hi).lstrip("T"))
    comp = tb.drop(columns=[target]).loc[lo]
    lead = comp.idxmax() if comp.sum() > 0 else "—"
    return ("success", "토픽으로 본 담론 공백과 강점",
            f"{target} 비중 지수(시장 평균=1.00) 최저: <b>T{li} {labels[li]}</b> ({order.iloc[0]:.2f}) — "
            f"이 주제는 <b>{lead}</b>의 언급이 가장 많아 경쟁사 강점 영역<br>"
            f"최고: <b>T{hiidx} {labels[hiidx]}</b> ({order.iloc[-1]:.2f}) — {target}가 상대적으로 많이 이야기되는 주제<br>"
            f"지수가 낮은 주제는 '담론 공백 → 선점 기회', 높은 주제는 '강점 유지'로 해석합니다.")


# ════════════════════════════════════════════════════
# TAB 1 — Overview
# ════════════════════════════════════════════════════
def _rt_ov():
    # [v2.5.2] 파스쿠찌 중심 스냅샷 — 담당자가 들어오면 가장 먼저 보이는 패널
    _pb = brand_df[brand_df["브랜드"] == "파스쿠찌"]
    _tot = brand_df["브랜드"].nunique()
    if len(_pb):
        _row = _pb.iloc[0]
        _ment = int(_row["언급량"]); _nss = float(_row["NSS"])
        _sov_col = "SOV_전체" if "SOV_전체" in brand_df.columns else ("SOV" if "SOV" in brand_df.columns else None)
        _sov = float(_row[_sov_col]) if _sov_col else float("nan")
        _ment_rank = int((brand_df["언급량"] > _ment).sum()) + 1
        _nss_rank = int((brand_df["NSS"] > _nss).sum()) + 1
        _loy = None; _loy_rank = None; _loy_tot = 0
        try:
            if loyalty_df is not None and "파스쿠찌" in set(loyalty_df["브랜드"]):
                _lr = loyalty_df[loyalty_df["브랜드"] == "파스쿠찌"].iloc[0]
                _loy = float(_lr["로열티지수"]); _loy_tot = len(loyalty_df)
                _loy_rank = int((loyalty_df["로열티지수"] > _loy).sum()) + 1
        except Exception:
            pass
        st.markdown("""
        <div style='background:linear-gradient(135deg,#7A1F2B 0%,#A52A35 100%);
                    border-radius:14px;padding:16px 22px;margin-bottom:10px;color:#FFF;
                    box-shadow:0 4px 14px rgba(122,31,43,0.3);'>
            <span style='font-size:1.6rem;vertical-align:middle;'>☕</span>
            <span style='font-weight:800;font-size:1.25rem;letter-spacing:0.5px;vertical-align:middle;'>&nbsp;PASCUCCI Brand Status</span>
            <span style='font-size:0.8rem;opacity:0.88;'>&nbsp;— 핵심 지표 요약</span>
        </div>""", unsafe_allow_html=True)

        def _pcard(col, icon, val, lbl, sub):
            with col:
                st.markdown(f"""
                <div style='background:#FFF;border:1px solid #EBD9DB;border-top:4px solid #A52A35;
                            border-radius:12px;padding:14px 10px;text-align:center;'>
                    <div style='font-size:1.4rem;'>{icon}</div>
                    <div style='font-size:1.5rem;font-weight:800;color:#7A1F2B;line-height:1.2;'>{val}</div>
                    <div style='font-size:0.78rem;color:#4A5568;font-weight:700;'>{lbl}</div>
                    <div style='font-size:0.72rem;color:#A0AEC0;'>{sub}</div>
                </div>""", unsafe_allow_html=True)
        _h1, _h2, _h3, _h4 = st.columns(4)
        _pcard(_h1, "💬", f"{_ment:,}", "언급량(6개월 환산)" if BLOG_CORRECTED else "언급량(수집 기준)",
               f"{_tot}개 중 {_ment_rank}위")
        _pcard(_h2, "😊", f"{_nss:+.1f}", "NSS(평판)", f"{_tot}개 중 {_nss_rank}위")
        _pcard(_h3, "📣", (f"{_sov:.1f}%" if _sov == _sov else "—"), "SOV(점유율)",
               f"{len(TARGET_BRANDS)}개 브랜드 언급 중 비중")
        _pcard(_h4, "💎", (f"{_loy:.1f}" if _loy is not None else "—"), "로열티지수",
               (f"{_loy_tot}개 중 {_loy_rank}위" if _loy_rank else "—"))
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>📊 종합 현황 (시장 전체)</div>", unsafe_allow_html=True)
    _pas_arr = brand_df[brand_df['브랜드'] == '파스쿠찌']['NSS'].values
    _pas_nss_txt = f"NSS {_pas_arr[0]:+.1f}" if len(_pas_arr) else "NSS —"
    c1, c2, c3, c4, c5 = st.columns(5)
    metrics = [
        ("📝", f"{len(v):,}건",     "분석 문서 수"),
        ("🏢", f"{brand_df['브랜드'].nunique()}개사", "언급 브랜드"),
        ("😊", f"{(v['sentiment']=='긍정').mean()*100:.1f}%", "전체 긍정률"),
        ("😡", f"{(v['sentiment']=='부정').mean()*100:.1f}%", "전체 부정률"),
        ("☕", _pas_nss_txt, "파스쿠찌 NSS"),
    ]
    for col, (icon, val, lbl) in zip([c1,c2,c3,c4,c5], metrics):
        with col:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-icon'>{icon}</div>
                <div class='kpi-value'>{val}</div>
                <div class='kpi-label'>{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("")
    _volume_note()
    c1, c2 = st.columns([1.4, 1])
    with c1:
        _bd = brand_df.sort_values("언급량", ascending=False)
        fig = go.Figure()
        for _part, _col in [("블로그", "#2D6BC4"), ("커뮤니티", "#E67E22")]:
            if _part in _bd.columns and _bd[_part].sum() > 0:
                fig.add_trace(go.Bar(x=_bd["브랜드"], y=_bd[_part], name=_part, marker_color=_col,
                                     hovertemplate="%{x} · " + _part + " %{y:,}건<extra></extra>"))
        fig.add_trace(go.Scatter(x=_bd["브랜드"], y=_bd["언급량"], mode="text",
                                 text=_bd["언급량"].apply(lambda x: f"{x:,}"), textposition="top center",
                                 showlegend=False, hoverinfo="skip"))
        fig.update_layout(barmode="stack",
                          title=("브랜드별 언급량 (블로그 6개월 환산 + 커뮤니티 실측)" if BLOG_CORRECTED
                                 else "브랜드별 언급량 (수집 건수 기준 · 보정 전)"))
        chart_style(fig, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        sent_cnt = v["sentiment"].value_counts().reset_index()
        sent_cnt.columns = ["감성", "수"]
        fig2 = px.pie(sent_cnt, names="감성", values="수",
                      color="감성", color_discrete_map=SENT_COLORS,
                      hole=0.52, title="전체 감성 분포")
        fig2.update_traces(textinfo="percent+label", textfont_size=13)
        chart_style(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='section-title'>브랜드별 월별 언급 추이 (지수: 브랜드별 기간 평균 = 100)</div>",
                unsafe_allow_html=True)
    # [v2.7.0] 기간 전체를 덮는 글만으로 월별 건수를 30일 환산한 뒤, 브랜드마다 자기 평균 대비 지수로 표시
    #   (검색 상한 때문에 브랜드 간 '수준' 비교는 불가 → 같은 브랜드 안의 '흐름'만 비교)
    _tv = _ts_rows(v)
    _md = _month_days(WIN_START, WIN_END)
    top6_brands = brand_df.sort_values("언급량", ascending=False).head(6)["브랜드"].tolist()
    if "파스쿠찌" in brand_df["브랜드"].values and "파스쿠찌" not in top6_brands:
        top6_brands = top6_brands[:5] + ["파스쿠찌"]
    ts_rows_ov = []
    for b in top6_brands:
        bdocs = _tv[_tv["brands"].apply(lambda x: b in x)] if _tv is not None and len(_tv) else _tv
        if bdocs is None or len(bdocs) < 30 or not _md:
            continue
        vals = _norm_monthly(bdocs.groupby("year_month").size(), _md)
        avg = float(np.mean(vals)) if vals else 0.0
        if avg <= 0:
            continue
        for (m, d), val in zip(sorted(_md.items()), vals):
            ts_rows_ov.append({"브랜드": b, "월": m, "지수": round(val / avg * 100, 1),
                               "표본(건)": int((bdocs["year_month"] == m).sum())})
    if ts_rows_ov:
        ts_ov_df = pd.DataFrame(ts_rows_ov)
        fig_ts = px.line(
            ts_ov_df, x="월", y="지수", color="브랜드", markers=True,
            color_discrete_map=BRAND_COLORS, hover_data=["표본(건)"],
            title="월별 언급 추이 지수 (월 30일 환산 · 기간 전체를 덮는 데이터 기준)",
        )
        fig_ts.add_hline(y=100, line_dash="dot", line_color="#A0AEC0")
        fig_ts.update_traces(line=dict(width=2.5), marker=dict(size=6))
        chart_style(fig_ts, height=380)
        st.plotly_chart(fig_ts, use_container_width=True)
        st.caption("검색 상한으로 최근 일부만 담긴 검색어의 글과 수집 당일 글은 제외했습니다. "
                   "브랜드 간 언급 규모 비교는 위 '브랜드별 언급량'을 보세요. (표본 30건 미만 브랜드 제외)")
    else:
        st.info("기간 전체를 덮는 데이터가 부족해 월별 추이를 표시하지 않습니다.")

    st.markdown("<div class='section-title'>브랜드별 감성 누적 비율</div>", unsafe_allow_html=True)
    sp = brand_df.melt(id_vars="브랜드", value_vars=["긍정률","부정률"],
                       var_name="감성", value_name="비율")
    sp["감성"] = sp["감성"].str.replace("률","")
    fig3 = px.bar(
        brand_df.sort_values("NSS"),
        x="브랜드", y=["긍정률","부정률"],
        title="브랜드별 긍정/부정 비율 (%)",
        color_discrete_map={"긍정률": "#27AE60", "부정률": "#E74C3C"},
        labels={"value":"비율(%)","variable":"감성"},
        text_auto=".0f",
    )
    chart_style(fig3, height=350)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<div class='section-title'>브랜드 종합 지표 테이블</div>", unsafe_allow_html=True)
    _cols = [c for c in ["브랜드","언급량","블로그","커뮤니티","긍정","부정","중립","긍정률","부정률","NSS",
                         "SOV_전체","SOV_긍정","SOV_부정","표본수","산출"] if c in brand_df.columns]
    st.dataframe(brand_df[_cols].sort_values("NSS", ascending=False),
                 use_container_width=True, hide_index=True)
    st.caption("언급량·긍정·부정 = 블로그(6개월 환산 또는 수집 건수) + 커뮤니티(실측). "
               "표본수 = 실제 수집되어 분석에 쓰인 글 수. NSS·SOV는 보정된 언급량 기준.")

# ════════════════════════════════════════════════════
# TAB 2 — NSS 평판
# ════════════════════════════════════════════════════
def _rt_nss():
    st.markdown("<div class='section-title'>📈 Net Sentiment Score 평판 진단</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='insight-box'>
    <b>NSS = (긍정 − 부정) / 전체 × 100</b><br>
    단순 긍정률보다 평판의 '방향성'을 민감하게 포착합니다.
    +100에 가까울수록 압도적 긍정, 0 이하면 부정이 긍정을 추월한 상태입니다.
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns([1.2, 1])
    with c1:
        sorted_b = brand_df.sort_values("NSS")
        fig = px.bar(
            sorted_b, x="NSS", y="브랜드", orientation="h",
            color="NSS", color_continuous_scale=["#E74C3C","#FFFFFF","#27AE60"],
            color_continuous_midpoint=0,
            title="브랜드별 NSS",
            text=sorted_b["NSS"].apply(lambda x: f"{x:+.1f}"),
        )
        fig.update_traces(textposition="outside")
        fig.add_vline(x=0, line_color="#E53E3E", line_width=2)
        fig.add_vline(x=brand_df["NSS"].mean(), line_color="#718096",
                      line_width=1.5, line_dash="dot",
                      annotation_text=f"평균 {brand_df['NSS'].mean():.1f}",
                      annotation_position="top right")
        chart_style(fig, height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        for _, row in brand_df.sort_values("NSS", ascending=False).iterrows():
            nss = row["NSS"]
            color = BRAND_COLORS.get(row["브랜드"], "#2D6BC4")
            grade = "🟢 우수" if nss >= 50 else ("🟡 양호" if nss >= 0 else "🔴 위험")
            st.markdown(f"""
            <div style='background:#FFFFFF;border:1px solid #E2E8F0;border-left:4px solid {color};
                        border-radius:0 8px 8px 0;padding:9px 12px;margin-bottom:6px;
                        display:flex;justify-content:space-between;align-items:center;'>
                <span style='font-weight:700;color:{color};font-size:0.9rem;'>{row['브랜드']}</span>
                <span style='color:#4A5568;font-size:0.8rem;'>긍 {row['긍정률']}% / 부 {row['부정률']}%</span>
                <span style='font-weight:800;color:{color};font-size:1rem;'>NSS {nss:+.1f}</span>
                <span>{grade}</span>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>월별 NSS 추이</div>", unsafe_allow_html=True)
    _mn = monthly_nss_df
    if len(_mn) > 0:
        _ok_b = _mn.groupby("브랜드")["월"].nunique()
        _mn = _mn[_mn["브랜드"].isin(_ok_b[_ok_b >= 2].index)]
    if len(_mn) > 0:
        fig_t = px.line(
            _mn, x="월", y="NSS", color="브랜드",
            color_discrete_map=BRAND_COLORS, markers=True, hover_data=["문서수"],
            title=f"브랜드별 월별 NSS 추이 (브랜드·월 표본 {NSS_MIN_N}건 이상만 표시)",
            labels={"월": "월", "NSS": "Net Sentiment Score"},
        )
        fig_t.add_hline(y=0, line_color="#E53E3E", line_width=1.5, line_dash="dash")
        chart_style(fig_t, height=380)
        st.plotly_chart(fig_t, use_container_width=True)
        st.caption("기간 전체를 덮는 데이터(검색 상한 검색어·수집 당일 글 제외)로 계산합니다.")
    else:
        st.info(f"월별로 비교할 만큼(브랜드·월 {NSS_MIN_N}건 이상) 기간 전체를 덮는 데이터가 쌓인 브랜드가 없습니다.")

    # [v2.7.0] 해설 박스 — 모두 데이터에서 자동 생성
    col1, col2 = st.columns(2)
    with col1:
        _box(*_ins_nss_shift(_mn))
    with col2:
        _box(*_ins_nss_market(brand_df))
    st.markdown("<div class='section-title'>다각도 시사점</div>", unsafe_allow_html=True)
    _gcols = st.columns(len(BRAND_GROUPS))
    for _gc, (_gname, _gbrands) in zip(_gcols, BRAND_GROUPS.items()):
        with _gc:
            _box(*_ins_group(_gname, _gbrands, brand_df))

# ════════════════════════════════════════════════════
# TAB 3 — SOV 분석
# ════════════════════════════════════════════════════
def _rt_sov():
    st.markdown("<div class='section-title'>📣 Share of Voice 분석</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='insight-box'>
    <b>SOV(담론 점유율)</b>: 전체 vs 긍정 vs 부정 SOV를 분리해 브랜드별 담론 질을 진단합니다.<br>
    전체 SOV가 높아도 부정 SOV가 압도적이면 실질 경쟁력이 낮은 상태입니다.<br>
    <span style='color:#5A6678'>{_sov_method_text()}</span>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        fig = px.pie(brand_df, names="브랜드", values="SOV_전체",
                     color="브랜드", color_discrete_map=BRAND_COLORS,
                     title="전체 SOV", hole=0.45)
        # 표시 브랜드만 골라도 12개 전체 대비 SOV 값을 그대로 표기
        fig.update_traces(text=brand_df["SOV_전체"].apply(lambda x: f"{x:.1f}%"),
                          textinfo="label+text", textfont_size=11)
        chart_style(fig, height=340)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        sorted_sov = brand_df.sort_values("SOV_긍정", ascending=True)
        fig2 = px.bar(sorted_sov, x="SOV_긍정", y="브랜드", orientation="h",
                      color="브랜드", color_discrete_map=BRAND_COLORS,
                      title="긍정 SOV (%)",
                      text=sorted_sov["SOV_긍정"].apply(lambda x: f"{x:.1f}%"))
        fig2.update_traces(textposition="outside")
        chart_style(fig2, height=340, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
    with c3:
        sorted_sov2 = brand_df.sort_values("SOV_부정", ascending=True)
        fig3 = px.bar(sorted_sov2, x="SOV_부정", y="브랜드", orientation="h",
                      color="브랜드", color_discrete_map=BRAND_COLORS,
                      title="부정 SOV (%)",
                      text=sorted_sov2["SOV_부정"].apply(lambda x: f"{x:.1f}%"))
        fig3.update_traces(textposition="outside")
        chart_style(fig3, height=340, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<div class='section-title'>SOV 매트릭스 — 전체 SOV × 긍정 SOV (버블=부정 SOV)</div>", unsafe_allow_html=True)
    fig4 = go.Figure()
    for _, row in brand_df.iterrows():
        color = BRAND_COLORS.get(row["브랜드"], "#2D6BC4")
        fig4.add_trace(go.Scatter(
            x=[row["SOV_전체"]], y=[row["SOV_긍정"]],
            mode="markers+text", name=row["브랜드"],
            marker=dict(
                size=max(row["SOV_부정"] * 6, 12),
                color=color, opacity=0.8,
                line=dict(color="white", width=2)
            ),
            text=[row["브랜드"]], textposition="top center",
            textfont=dict(size=11, color=color, family="Arial Black"),
            hovertemplate=(
                f"<b>{row['브랜드']}</b><br>"
                f"전체 SOV: {row['SOV_전체']:.1f}%<br>"
                f"긍정 SOV: {row['SOV_긍정']:.1f}%<br>"
                f"부정 SOV: {row['SOV_부정']:.1f}%<extra></extra>"
            ),
        ))
    fig4.add_hline(y=brand_df["SOV_긍정"].mean(), line_dash="dot", line_color="#A0AEC0")
    fig4.add_vline(x=brand_df["SOV_전체"].mean(), line_dash="dot", line_color="#A0AEC0")
    fig4.update_layout(
        title="SOV 매트릭스 (버블 크기 = 부정 SOV)",
        xaxis_title="전체 담론 점유율 (%)",
        yaxis_title="긍정 담론 점유율 (%)",
        showlegend=False,
    )
    chart_style(fig4, height=450)
    st.plotly_chart(fig4, use_container_width=True)

    # [v2.7.0] 소스별 SOV 비교 (블로그 6개월 환산 vs 커뮤니티 실측)
    _ba = brand_df_all
    if len(_ba) and {"블로그", "커뮤니티"}.issubset(_ba.columns) and _ba["블로그"].sum() > 0 and _ba["커뮤니티"].sum() > 0:
        st.markdown("<div class='section-title'>소스별 SOV — 블로그 vs 커뮤니티</div>", unsafe_allow_html=True)
        _sv = _ba[["브랜드", "블로그", "커뮤니티"]].copy()
        _sv["블로그 SOV"] = (_sv["블로그"] / _sv["블로그"].sum() * 100).round(1)
        _sv["커뮤니티 SOV"] = (_sv["커뮤니티"] / _sv["커뮤니티"].sum() * 100).round(1)
        _sv = _sv[_sv["브랜드"].isin(SEL_BRANDS)].sort_values("블로그 SOV", ascending=False)
        _m = _sv.melt(id_vars="브랜드", value_vars=["블로그 SOV", "커뮤니티 SOV"], var_name="소스", value_name="SOV(%)")
        figs = px.bar(_m, x="브랜드", y="SOV(%)", color="소스", barmode="group",
                      color_discrete_map={"블로그 SOV": "#2D6BC4", "커뮤니티 SOV": "#E67E22"},
                      text=_m["SOV(%)"].apply(lambda x: f"{x:.1f}"),
                      title=("블로그(6개월 환산) vs 커뮤니티(실측) 점유율" if BLOG_CORRECTED
                             else "블로그(수집 건수·보정 전) vs 커뮤니티(실측) 점유율"))
        figs.update_traces(textposition="outside")
        chart_style(figs, height=380)
        st.plotly_chart(figs, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        _box(*_ins_sov_leader(brand_df))
    with col2:
        _box(*_ins_sov_target(brand_df_all))

# ════════════════════════════════════════════════════
# TAB 4 — 드라이버 분석 (ABSA)
# ════════════════════════════════════════════════════
def _rt_absa():
    st.markdown("<div class='section-title'>🔍 평판 드라이버 분석 (Aspect-Based Sentiment)</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='insight-box'>
    <b>ABSA</b>: 속성(맛·배송·가격 등)별로 긍정/부정 리뷰를 분해합니다.
    '왜 좋은가? 왜 싫은가?'를 구체적인 속성 수준에서 파악합니다.
    </div>""", unsafe_allow_html=True)

    sel_b = st.selectbox("브랜드 선택 (전체 또는 개별)", ["전체"] + SEL_BRANDS, key="absa_brand")
    if sel_b == "전체":
        absa_target = v
    else:
        absa_target = v[v["brands"].apply(lambda x: sel_b in x)]

    absa_computed = compute_absa(absa_target, f"{_VSIG}|{sel_b}")

    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        df_absa = absa_computed.sort_values("NSS")
        fig.add_trace(go.Bar(
            name="긍정", y=df_absa["속성"], x=df_absa["긍정률"],
            orientation="h", marker_color="#27AE60",
            text=df_absa["긍정률"].apply(lambda x: f"{x:.0f}%"),
            textposition="inside", textfont=dict(color="white", size=11),
        ))
        fig.add_trace(go.Bar(
            name="부정", y=df_absa["속성"], x=-df_absa["부정률"],
            orientation="h", marker_color="#E74C3C",
            text=df_absa["부정률"].apply(lambda x: f"{x:.0f}%"),
            textposition="inside", textfont=dict(color="white", size=11),
        ))
        fig.update_layout(
            barmode="relative",
            title=f"속성별 긍정/부정 비율 — {sel_b}",
            xaxis=dict(
                tickvals=[-100,-75,-50,-25,0,25,50,75,100],
                ticktext=["100%","75%","50%","25%","0","25%","50%","75%","100%"],
                title="비율 (%)"
            ),
        )
        chart_style(fig, height=400)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = px.bar(
            absa_computed.sort_values("NSS"), x="NSS", y="속성",
            orientation="h", color="NSS",
            color_continuous_scale=["#E74C3C","#FFFFFF","#27AE60"],
            color_continuous_midpoint=0,
            title=f"속성별 NSS — {sel_b}",
            text=absa_computed.sort_values("NSS")["NSS"].apply(lambda x: f"{x:+.1f}"),
        )
        fig2.update_traces(textposition="outside")
        fig2.add_vline(x=0, line_color="#4A5568", line_width=1.5)
        chart_style(fig2, height=400, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='section-title'>브랜드별 속성 NSS 히트맵</div>", unsafe_allow_html=True)
    heat = {}
    for b in SEL_BRANDS:
        bd = v[v["brands"].apply(lambda x: b in x)]
        row = {}
        for attr, kws in ATTR_DICT.items():
            pat  = "|".join(kws)
            sub  = bd[bd["full_text"].str.contains(pat, na=False)]
            if len(sub) < 2:
                row[attr] = 0
                continue
            p = (sub["sentiment"] == "긍정").sum()
            n = (sub["sentiment"] == "부정").sum()
            t = len(sub)
            row[attr] = round((p - n) / t * 100, 1)
        heat[b] = row
    heat_df = pd.DataFrame(heat).T
    fig3 = px.imshow(
        heat_df,
        color_continuous_scale=["#E74C3C","#FFFFFF","#27AE60"],
        color_continuous_midpoint=0,
        title="브랜드 × 속성 NSS 히트맵 (빨강=부정 강함, 초록=긍정 강함)",
        text_auto=".1f", aspect="auto", zmin=-60, zmax=80,
    )
    fig3.update_traces(textfont=dict(color="#1B2A4A", size=11))
    chart_style(fig3, height=360, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<div class='section-title'>칭찬 vs 불만 드라이버 TOP 3</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        for _, row in absa_computed.nlargest(3, "NSS").iterrows():
            st.markdown(f"""
            <div style='background:#F0FFF4;border-left:4px solid #27AE60;border-radius:0 8px 8px 0;
                        padding:10px 14px;margin:6px 0'>
                <b style='color:#276749'>{row['속성']}</b>
                <span style='float:right;color:#27AE60;font-weight:700'>NSS {row['NSS']:+.1f} / 긍정 {row['긍정률']}%</span>
                <div style='color:#718096;font-size:0.82rem;margin-top:4px'>
                    분석 {row['문서수']}건 · 긍정 {row['긍정']}건 · 부정 {row['부정']}건
                </div>
            </div>""", unsafe_allow_html=True)
    with col2:
        for _, row in absa_computed.nsmallest(3, "NSS").iterrows():
            st.markdown(f"""
            <div style='background:#FFF5F5;border-left:4px solid #E53E3E;border-radius:0 8px 8px 0;
                        padding:10px 14px;margin:6px 0'>
                <b style='color:#C53030'>{row['속성']}</b>
                <span style='float:right;color:#E74C3C;font-weight:700'>NSS {row['NSS']:+.1f} / 부정 {row['부정률']}%</span>
                <div style='color:#718096;font-size:0.82rem;margin-top:4px'>
                    분석 {row['문서수']}건 · 긍정 {row['긍정']}건 · 부정 {row['부정']}건
                </div>
            </div>""", unsafe_allow_html=True)

    # [v2.4.1] 칭찬/불만 드라이버 Top3 원문 확인
    st.markdown("<div class='section-title'>🔎 드라이버 Top 3 원문 확인</div>", unsafe_allow_html=True)
    st.caption("각 드라이버를 펼치면 해당 속성 키워드가 포함된 문장만 발췌해 보여줍니다(전체 글이 아닌 관련 부분). 칭찬/불만은 그 문장에 감성어가 함께 있는 글을 우선 노출합니다. [v2.5.1 정확도 개선]")

    _DRV_POS = ["맛있", "좋", "추천", "최고", "만족", "친절", "합리", "가성비", "저렴",
                "달콤", "훌륭", "대박", "꿀", "인생", "강추", "최애"]
    _DRV_NEG = ["맛없", "별로", "실망", "불만", "최악", "비싸", "불친절", "느리", "아쉽",
                "안좋", "싫", "불매", "후회", "환불", "논란", "줄였", "항의"]

    def _aspect_snippet(text, kws):
        """키워드가 포함된 문장만 발췌 — 전체 문서 대신 속성 관련 부분만 노출."""
        t = str(text)
        for s in re.split(r"(?<=[.!?。…])\s+|\n+", t):
            if any(kw in s for kw in kws):
                s2 = re.sub(r"\s+", " ", s).strip()
                if len(s2) >= 6:
                    return s2[:170]
        for kw in kws:
            i = t.find(kw)
            if i >= 0:
                return re.sub(r"\s+", " ", t[max(0, i - 40):i + 90]).strip()[:170]
        return ""

    def _driver_docs(attr, sentiment, k=3):
        # [v2.5.1] 정확도 개선: 속성 키워드가 든 문장을 발췌하고, 그 문장에 해당 감성어가
        # 함께 있을 때만 그 속성에 대한 칭찬/불만으로 채택. 관련도 높은 순으로 정렬.
        kws = ATTR_DICT.get(attr, [])
        if not kws:
            return []
        senti_kw = _DRV_POS if sentiment == "긍정" else _DRV_NEG
        strict, loose = [], []
        for _, rr in absa_target.iterrows():
            ft = str(rr.get("full_text", ""))
            if not any(kw in ft for kw in kws):
                continue
            snip = _aspect_snippet(ft, kws)
            if not snip:
                continue
            title = str(rr.get("title", "")).strip() or "(제목 없음)"
            url = str(rr.get("post_url", "") or "")
            relev = sum(ft.count(kw) for kw in kws) + (3 if any(kw in title for kw in kws) else 0)
            item = (relev, title, snip, url)
            (strict if any(sw in snip for sw in senti_kw) else loose).append(item)
        strict.sort(key=lambda x: -x[0])
        loose.sort(key=lambda x: -x[0])
        picked = strict[:k] + loose[:max(0, k - len(strict))]
        return [(t, s, u) for _, t, s, u in picked]

    dcol1, dcol2 = st.columns(2)
    with dcol1:
        st.markdown("**👍 칭찬 드라이버 원문**")
        for _, row in absa_computed.nlargest(3, "NSS").iterrows():
            with st.expander(f"{row['속성']} · NSS {row['NSS']:+.1f}"):
                docs = _driver_docs(row['속성'], "긍정")
                if not docs:
                    st.caption("표시할 원문이 충분치 않습니다.")
                for title, body, url in docs:
                    link = f" [원문 보기]({url})" if url.startswith("http") else ""
                    st.markdown(f"- **{title}** — {body}…{link}")
    with dcol2:
        st.markdown("**👎 불만 드라이버 원문**")
        for _, row in absa_computed.nsmallest(3, "NSS").iterrows():
            with st.expander(f"{row['속성']} · NSS {row['NSS']:+.1f}"):
                docs = _driver_docs(row['속성'], "부정")
                if not docs:
                    st.caption("표시할 원문이 충분치 않습니다.")
                for title, body, url in docs:
                    link = f" [원문 보기]({url})" if url.startswith("http") else ""
                    st.markdown(f"- **{title}** — {body}…{link}")

# ════════════════════════════════════════════════════
# TAB 5 — CA 이미지 맵
# ════════════════════════════════════════════════════
def _rt_ca():
    st.markdown("<div class='section-title'>🗺️ 브랜드 이미지 맵 — 대응일치분석 (CA)</div>", unsafe_allow_html=True)
    if ca_result is None:
        st.info("CA 분석을 위한 데이터가 부족합니다.")
    else:
        n_kw = st.slider("표시 키워드 수", 15, 40, 30, key="ca_kw")
        expl  = ca_result["expl"]
        brands = ca_result["brands"]
        top_kws = ca_result["kws"][:n_kw]
        cont    = ca_result["cont"][top_kws]
        kw_sizes = [cont[kw].sum() for kw in top_kws]
        kw_max   = max(kw_sizes) if kw_sizes else 1

        col_x = ca_result["col_x"][:n_kw]
        col_y = ca_result["col_y"][:n_kw]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=col_x, y=col_y, mode="markers+text",
            marker=dict(
                size=[10 + int(s / kw_max * 18) for s in kw_sizes],
                color="#A0AEC0", opacity=0.65,
                line=dict(color="white", width=1)
            ),
            text=top_kws, textposition="top center",
            textfont=dict(size=10, color="#4A5568"),
            hovertemplate="<b>%{text}</b><extra>키워드</extra>",
            name="키워드",
        ))
        for i, b in enumerate(brands):
            if b not in SEL_BRANDS:   # [v2.7.0] 표시 브랜드만 (좌표는 12개 전체로 계산)
                continue
            color = BRAND_COLORS.get(b, "#2D6BC4")
            rx, ry = ca_result["row_x"][i], ca_result["row_y"][i]
            dists = [(np.sqrt((col_x[j]-rx)**2+(col_y[j]-ry)**2), j) for j in range(len(top_kws))]
            for _, j in sorted(dists)[:4]:
                fig.add_trace(go.Scatter(
                    x=[rx, col_x[j]], y=[ry, col_y[j]],
                    mode="lines", line=dict(color=color, width=1.2, dash="dot"),
                    opacity=0.35, showlegend=False, hoverinfo="skip",
                ))
            _is_pas = (b == "파스쿠찌")
            fig.add_trace(go.Scatter(
                x=[rx], y=[ry], mode="markers+text", name=b,
                marker=dict(size=36 if _is_pas else 22,
                            symbol="star" if _is_pas else "circle",
                            color=color,
                            line=dict(color="#C0392B" if _is_pas else "white",
                                      width=4 if _is_pas else 2.5)),
                text=[("★ " + b) if _is_pas else b], textposition="top right",
                textfont=dict(size=16 if _is_pas else 12,
                              color="#C0392B" if _is_pas else color, family="Arial Black"),
                hovertemplate=f"<b>{b}</b><extra>브랜드</extra>",
            ))
        fig.add_hline(y=0, line_color="#CBD5E0", line_dash="dot", line_width=1)
        fig.add_vline(x=0, line_color="#CBD5E0", line_dash="dot", line_width=1)
        # [v2.5.2] 축 라벨을 데이터(양 극단 키워드) 기반으로 — CA 차원 부호는 데이터마다 달라짐
        _cx = np.asarray(col_x); _cy = np.asarray(col_y)
        _ox = np.argsort(_cx); _oy = np.argsort(_cy)
        _xl = " · ".join(top_kws[i] for i in _ox[:3])
        _xr = " · ".join(top_kws[i] for i in _ox[-3:][::-1])
        _yb = " · ".join(top_kws[i] for i in _oy[:3])
        _yt = " · ".join(top_kws[i] for i in _oy[-3:][::-1])
        fig.update_layout(
            title=f"브랜드 이미지 맵  (차원1: {expl[0]:.1f}% | 차원2: {expl[1]:.1f}% | 누적: {sum(expl[:2]):.1f}%)",
            xaxis_title=f"차원 1 ({expl[0]:.1f}%):  ← {_xl}　|　{_xr} →",
            yaxis_title=f"차원 2 ({expl[1]:.1f}%):  ↓ {_yb}　|　{_yt} ↑",
        )
        chart_style(fig, height=620)
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📘 브랜드 이미지 맵 읽는 방법"):
            st.markdown("""
            - **브랜드 ●** 와 **키워드 ●** 가 **가까울수록** 해당 브랜드 담론에서 그 키워드가 자주 등장합니다.
            - **축의 의미는 고정이 아니라 데이터로 결정됩니다.** 각 축 양 끝의 키워드(축 제목에 표시)가 그 방향의 성격이며, 데이터가 바뀌면 축 방향·해석도 달라집니다.
            - 원점(0,0)에서 **멀수록 개성이 뚜렷한** 이미지, 가까울수록 평균적 이미지입니다.
            - 점선 = 브랜드와 가장 가까운 키워드 TOP 4 연결.
            - **★ 파스쿠찌**는 별 마커로 강조됩니다 — 어떤 키워드 쪽에 위치하는지 먼저 확인하세요.
            """)

# ════════════════════════════════════════════════════
# TAB 6 — LDA 토픽 모델링
# ════════════════════════════════════════════════════
def _rt_lda():
    st.markdown("<div class='section-title'>🎯 LDA 토픽 모델링 (7-토픽)</div>", unsafe_allow_html=True)
    # [v2.7.0] 무거운 토픽 모델은 이 탭을 열 때만 계산 (첫 화면 로딩 단축, 결과는 캐시)
    lda_model, tfidf_vec, vocab, doc_topics, topic_dist = compute_lda(v, _VSIG)
    topic_cluster = compute_topic_clustering(v, _VSIG)
    if lda_model is None:
        st.warning("LDA 분석을 위한 데이터가 부족합니다.")
    else:
        sel_b6 = st.selectbox("브랜드 선택", ["전체"] + SEL_BRANDS, key="lda_brand")
        if sel_b6 == "전체":
            # [v2.7.0] 전체는 이미 계산한 모델을 그대로 사용 (같은 모델을 두 번 학습하던 문제 수정)
            lm, tv, vc, dt, tdist = lda_model, tfidf_vec, vocab, doc_topics, topic_dist
        else:
            lda_target = v[v["brands"].apply(lambda x: sel_b6 in x)]
            lm, tv, vc, dt, tdist = compute_lda(lda_target, f"{_VSIG}|{sel_b6}")
        if lm is None:
            st.info("선택한 브랜드의 문서가 부족합니다.")
        else:
            # [v2.7.0] 토픽 이름을 고정 목록 대신 각 토픽의 상위 키워드로 자동 부여
            _lbl = _label_topics([[vc[j] for j in lm.components_[t].argsort()[-10:][::-1]] for t in range(7)])
            c1, c2 = st.columns([1.4, 1])
            with c1:
                fig = make_subplots(
                    rows=4, cols=2,
                    subplot_titles=[f"T{i+1}: {_lbl[i]}" for i in range(7)],
                    vertical_spacing=0.08, horizontal_spacing=0.1,
                )
                for ti in range(7):
                    r, ci = ti // 2 + 1, ti % 2 + 1
                    top_idx = lm.components_[ti].argsort()[-10:][::-1]
                    tw = [vc[j] for j in top_idx]
                    tv_vals = lm.components_[ti][top_idx]
                    tv_vals = tv_vals / tv_vals.sum()
                    fig.add_trace(
                        go.Bar(x=tv_vals, y=tw, orientation="h",
                               marker_color=TOPIC_COLORS[ti], showlegend=False,
                               hovertemplate="%{y}: %{x:.3f}<extra></extra>"),
                        row=r, col=ci,
                    )
                    fig.update_yaxes(autorange="reversed", row=r, col=ci,
                                     tickfont=dict(size=9, color="#2D3748"))
                    fig.update_xaxes(tickfont=dict(size=8, color="#718096"), row=r, col=ci)
                fig.update_layout(
                    height=700, paper_bgcolor="#F7F9FC", plot_bgcolor="#FFFFFF",
                    font=dict(color="#2D3748"),
                    title_text=f"{sel_b6} — 7개 토픽 키워드",
                    title_font=dict(color="#1B2A4A", size=14),
                )
                for ann in fig.layout.annotations:
                    ann.font.color = "#1B2A4A"; ann.font.size = 11
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                dist = dt.mean(axis=0)
                fig2 = go.Figure(go.Pie(
                    labels=[f"T{i+1}: {_lbl[i]}" for i in range(7)],
                    values=dist, hole=0.5,
                    marker=dict(colors=TOPIC_COLORS, line=dict(color="white", width=2)),
                    textfont=dict(color="#1B2A4A", size=10),
                ))
                fig2.update_layout(title=f"{sel_b6} — 토픽 비중")
                chart_style(fig2, height=360)
                st.plotly_chart(fig2, use_container_width=True)

                dom = dt.argmax(axis=1)
                dom_cnt = pd.Series(dom).value_counts().sort_index()
                fig3 = px.bar(
                    x=[_lbl[i] for i in dom_cnt.index],
                    y=dom_cnt.values,
                    color=[_lbl[i] for i in dom_cnt.index],
                    color_discrete_sequence=TOPIC_COLORS,
                    title="지배 토픽별 문서 수",
                    text=dom_cnt.values,
                    labels={"x":"토픽","y":"문서 수"},
                )
                fig3.update_traces(textposition="outside")
                chart_style(fig3, height=300, showlegend=False)
                st.plotly_chart(fig3, use_container_width=True)

        if sel_b6 == "전체":
            st.markdown("<div class='section-title'>브랜드별 토픽 분포 히트맵</div>", unsafe_allow_html=True)
            _lbl_all = _label_topics([[vocab[j] for j in lda_model.components_[t].argsort()[-10:][::-1]] for t in range(7)])
            brand_topic = {}
            # [v2.7.0] 문서별 토픽 분포(doc_topics)를 재사용 — 브랜드마다 다시 추론하지 않음
            _docs_all = v[v["tokens_str"].str.len() > 5]
            _aligned = doc_topics is not None and len(_docs_all) == len(doc_topics)
            for b in SEL_BRANDS:
                bmask = _docs_all["brands"].apply(lambda x: b in x).to_numpy()
                if bmask.sum() < 5:
                    continue
                if _aligned:
                    bt = doc_topics[bmask].mean(axis=0)
                else:
                    bt = lda_model.transform(tfidf_vec.transform(_docs_all.loc[bmask, "tokens_str"])).mean(axis=0)
                brand_topic[b] = {f"T{i+1} {_lbl_all[i]}": round(float(bt[i])*100, 1) for i in range(7)}
            if brand_topic:
                bt_df = pd.DataFrame(brand_topic).T
                fig4 = px.imshow(
                    bt_df, color_continuous_scale="Blues",
                    title="브랜드 × 토픽 집중도 히트맵 (%)",
                    text_auto=".1f", aspect="auto",
                )
                fig4.update_traces(textfont=dict(color="#1B2A4A", size=11))
                chart_style(fig4, height=380, showlegend=False)
                st.plotly_chart(fig4, use_container_width=True)

# ════════════════════════════════════════════════════
# TAB 7 — Burst 탐지
# ════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("<div class='section-title'>🧩 토픽 클러스터링 — 토픽 × 브랜드 × 감성 중첩 분석</div>", unsafe_allow_html=True)
    st.caption("※ LDA 토픽 모델링과 토픽 클러스터링을 한 화면에서 함께 분석 [v2.3.1 merge]")
    st.markdown("""
    <div class='insight-box'>
    LDA 토픽을 나열식으로 보지 않고, <b>어떤 토픽이 어떤 브랜드·고객 감성과 중첩되는지</b>를 분석합니다.<br>
    토픽 × 브랜드 히트맵으로 "어떤 브랜드가 어떤 주제로 이야기되는가"를 파악합니다.
    </div>""", unsafe_allow_html=True)

    if topic_cluster is None:
        st.info("토픽 클러스터링을 위한 데이터가 부족합니다.")
    else:
        n_t = topic_cluster["n_topics"]
        topic_words = topic_cluster["topic_words"]
        topic_meanings = topic_cluster.get("topic_meanings", [""]*n_t)
        topic_occasions = topic_cluster.get("topic_occasions", [[]]*n_t)
        topic_brands_list = topic_cluster.get("topic_brands", [[]]*n_t)
        topic_labels_cl = [f"T{i}: {topic_meanings[i]}" for i in range(n_t)]

        st.markdown("<div class='section-title'>토픽별 의미 · 핵심 키워드 · 소비자 유형</div>", unsafe_allow_html=True)
        tcols = st.columns(n_t)
        cluster_colors = ["#2980B9", "#16A085", "#E67E22", "#8E44AD", "#E74C3C",
                          "#D4A017", "#C0392B", "#117A65"]  # [v2.3.2] 6~8토픽 대응
        for i, col in enumerate(tcols):
            with col:
                kw_html = "".join([
                    f"<span style='display:inline-block;background:{cluster_colors[i % len(cluster_colors)]}22;"
                    f"color:{cluster_colors[i % len(cluster_colors)]};border-radius:10px;padding:2px 8px;"
                    f"margin:2px;font-size:11px;'>{w}</span>"
                    for w in topic_words[i][:6]])
                occ_str = ", ".join(topic_occasions[i]) if topic_occasions[i] else "—"
                brand_str = ", ".join(topic_brands_list[i]) if topic_brands_list[i] else "—"
                st.markdown(f"""
                <div style='background:#FFFFFF;border-top:3px solid {cluster_colors[i % len(cluster_colors)]};
                            border:1px solid #E2E8F0;border-radius:8px;padding:10px;'>
                    <div style='font-weight:800;color:{cluster_colors[i % len(cluster_colors)]};font-size:0.9rem;'>토픽 {i}</div>
                    <div style='color:#1B2A4A;font-weight:700;font-size:0.82rem;margin:3px 0;'>{topic_meanings[i]}</div>
                    <div style='color:#718096;font-size:11px;'>{topic_cluster['topic_sizes'][i]}건</div>
                    <div style='margin-top:6px;'>{kw_html}</div>
                    <div style='margin-top:8px;padding-top:6px;border-top:1px dashed #E2E8F0;font-size:0.72rem;color:#4A5568;'>
                        <b>주요 소비상황</b>: {occ_str}<br>
                        <b>주요 브랜드</b>: {brand_str}
                    </div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div class='section-title'>토픽 × 브랜드 중첩 히트맵</div>", unsafe_allow_html=True)
        tb = topic_cluster["tb_mat"].copy()
        tb.index = topic_labels_cl
        fig = px.imshow(
            tb, color_continuous_scale="Blues",
            title="어떤 브랜드가 어떤 토픽으로 이야기되는가",
            text_auto=True, aspect="auto",
        )
        fig.update_traces(textfont=dict(color="#1B2A4A", size=11))
        chart_style(fig, height=380, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='section-title'>토픽 × 감성 분포</div>", unsafe_allow_html=True)
            ts = topic_cluster["ts_mat"].copy()
            ts.index = [f"T{i}" for i in range(n_t)]
            fig2 = px.bar(
                ts, barmode="stack",
                color_discrete_map={"긍정":"#27AE60","중립":"#F39C12","부정":"#E74C3C"},
                title="토픽별 감성 구성",
                labels={"value":"문서 수","index":"토픽","variable":"감성"},
            )
            chart_style(fig2, height=340)
            st.plotly_chart(fig2, use_container_width=True)
        with c2:
            st.markdown("<div class='section-title'>토픽 규모 비중</div>", unsafe_allow_html=True)
            fig3 = go.Figure(go.Pie(
                labels=topic_labels_cl, values=topic_cluster["topic_sizes"],
                hole=0.5,
                marker=dict(colors=cluster_colors[:n_t], line=dict(color="white", width=2)),
                textfont=dict(size=10),
            ))
            fig3.update_layout(title="토픽 규모 분포")
            chart_style(fig3, height=340)
            st.plotly_chart(fig3, use_container_width=True)

        _box(*_ins_topics(topic_cluster))


# ════════════════════════════════════════════════════
# TAB — 소비맥락 세분화 (3축 결합) [고도화 B]
# ════════════════════════════════════════════════════

def _rt_burst():
    st.markdown("<div class='section-title'>⚡ Burst Detection — 급증 키워드 탐지</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='warning-box'>
    <b>Burst Detection</b>: {_burst_period_text()} 키워드 증가율을 비교합니다.
    급증 키워드는 브랜드 위기 또는 새로운 소비 담론의 선행 신호입니다.<br>
    증가율 = 최근 30일 언급 ÷ (직전 30일 환산 + 1) · 직전에 거의 없던 단어는 해설에서 '신규 등장'으로 표기합니다.<br>
    <span style='color:#7B6A3A'>검색 상한으로 최근 글만 담긴 검색어와 수집 당일 글은 제외해, 수집 방식 때문에 생기는 '가짜 급증'을 걸러냅니다.</span>
    </div>""", unsafe_allow_html=True)

    if burst_df is None or len(burst_df) == 0:
        st.info("비교 구간에 충분한 데이터가 없어 급증 키워드를 계산하지 않았습니다.")
        return
    c1, c2 = st.columns([1.3, 1])
    with c1:
        top15 = burst_df.head(15).sort_values("증가율(배)")
        fig = px.bar(
            top15, x="증가율(배)", y="키워드", orientation="h",
            title="급증 키워드 TOP 15 (증가율 배수 · 빨강 = 부정 맥락·리스크 단어)",
            text=top15["증가율(배)"].apply(lambda x: f"{x:.1f}x"),
        )
        fig.update_traces(textposition="outside",
                          marker_color=["#E74C3C" if _burst_is_risk(r) else "#2980B9" for _, r in top15.iterrows()])
        chart_style(fig, height=460, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        # 급증 1위 키워드의 월별 추이 (기간 전체를 덮는 글 · 30일 환산)
        _kw = burst_df.iloc[0]["키워드"]
        _tv = _ts_rows(v)
        _md = _month_days(WIN_START, WIN_END)
        if _tv is not None and len(_tv) and _md:
            _hit = _tv[_tv["tokens_str"].str.contains(_kw, regex=False, na=False)]
            _vals = _norm_monthly(_hit.groupby("year_month").size(), _md)
            fig2 = go.Figure(go.Scatter(
                x=[_mlabel(m) for m in sorted(_md)], y=_vals, mode="lines+markers+text",
                line=dict(color="#27AE60", width=2.5), marker=dict(size=8, color="#27AE60"),
                fill="tozeroy", fillcolor="rgba(39,174,96,0.12)",
                text=[f"{x:.0f}" for x in _vals], textposition="top center",
                textfont=dict(size=11, color="#1A4731")))
            fig2.update_layout(title=f"급증 1위 '{_kw}' 월별 언급 (30일 환산)", xaxis_title="월", yaxis_title="문서 수")
            chart_style(fig2, height=240, showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)
        for _b in _ins_burst(burst_df):
            _box(*_b)

    st.markdown("<div class='section-title'>급증 키워드 상세 데이터</div>", unsafe_allow_html=True)
    st.dataframe(burst_df, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════
# TAB 8 — PMI 분석
# ════════════════════════════════════════════════════
def _rt_pmi():
    st.markdown("<div class='section-title'>🔗 PMI — 브랜드 공출현 강도 분석</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='insight-box'>
    <b>PMI (Pointwise Mutual Information)</b>: 두 브랜드가 같은 문서에서 함께 언급될 때
    우연 대비 얼마나 더 자주 함께 등장하는지를 측정합니다.
    PMI가 높을수록 소비자가 두 브랜드를 비교·연관해서 인식하는 경향이 강합니다.
    </div>""", unsafe_allow_html=True)

    pmi_top = pmi_df[pmi_df["PMI"] > -5].head(15)
    fig = px.bar(
        pmi_top, x="PMI", y=pmi_top["브랜드1"] + " ↔ " + pmi_top["브랜드2"],
        orientation="h", color="PMI",
        color_continuous_scale=["#BEE3F8","#2D6BC4"],
        title="브랜드 간 공출현 PMI 상위 15쌍",
        text=pmi_top["PMI"].apply(lambda x: f"{x:.2f}"),
        labels={"y":"브랜드 쌍"},
    )
    fig.update_traces(textposition="outside")
    chart_style(fig, height=480, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-title'>PMI 매트릭스 히트맵</div>", unsafe_allow_html=True)
    pmi_matrix = pmi_df.pivot_table(index="브랜드1", columns="브랜드2",
                                    values="PMI", fill_value=0)
    all_b = sorted(set(pmi_df["브랜드1"].tolist() + pmi_df["브랜드2"].tolist()))
    pmi_full = pd.DataFrame(0.0, index=all_b, columns=all_b)
    for _, row in pmi_df.iterrows():
        pmi_full.loc[row["브랜드1"], row["브랜드2"]] = row["PMI"]
        pmi_full.loc[row["브랜드2"], row["브랜드1"]] = row["PMI"]
    # 발산형 컬러스케일: 음(파랑) - 0(흰색) - 양(빨강)으로 명확히 구분
    pmi_vals = pmi_full.values
    pmi_abs_max = max(abs(pmi_vals.min()), abs(pmi_vals.max())) if pmi_vals.size else 1
    fig2 = px.imshow(
        pmi_full,
        color_continuous_scale=["#2166AC","#67A9CF","#F7F7F7","#EF8A62","#B2182B"],
        color_continuous_midpoint=0,
        zmin=-pmi_abs_max, zmax=pmi_abs_max,
        title="브랜드 공출현 PMI 매트릭스 (빨강=강한 연관, 파랑=약한 연관)",
        text_auto=".2f", aspect="auto",
    )
    fig2.update_traces(textfont=dict(color="#1B2A4A", size=11))
    chart_style(fig2, height=440, showlegend=True)
    st.plotly_chart(fig2, use_container_width=True)

    _pb = _ins_pmi(pmi_df)
    _pcs = st.columns(len(_pb))
    for _c, _b in zip(_pcs, _pb):
        with _c:
            _box(*_b)

    st.markdown("<div class='section-title'>PMI 상세 데이터</div>", unsafe_allow_html=True)
    st.dataframe(pmi_df[pmi_df["공출현수"] > 0].sort_values("PMI", ascending=False),
                 use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════
# TAB 9 — 포지셔닝맵
# ════════════════════════════════════════════════════
def _rt_pos():
    st.markdown("<div class='section-title'>📍 브랜드 포지셔닝맵</div>", unsafe_allow_html=True)

    def norm01(s):
        mn, mx = s.min(), s.max()
        return (s - mn) / (mx - mn + 1e-9)

    pos_df = brand_df.copy()
    pos_df["norm_total"]  = norm01(pos_df["언급량"])
    pos_df["norm_nss"]    = norm01(pos_df["NSS"])
    pos_df["norm_pos"]    = norm01(pos_df["긍정률"])
    pos_df["neg_risk"]    = norm01(100 - pos_df["긍정률"])

    st.caption("두 장의 사분면 지도로 브랜드 위치를 직관적으로 읽습니다. 점선은 브랜드 평균선이며, 모서리의 회색 라벨이 그 칸(사분면)의 의미입니다.")

    def _quad_labels(_fig, tl, tr, bl, br):
        """사분면 네 모서리에 의미 라벨(paper 좌표)."""
        for _x, _y, _t, _xa, _ya in [
            (0.015, 0.985, tl, "left", "top"), (0.985, 0.985, tr, "right", "top"),
            (0.015, 0.015, bl, "left", "bottom"), (0.985, 0.015, br, "right", "bottom")]:
            _fig.add_annotation(x=_x, y=_y, xref="paper", yref="paper", text=_t,
                                showarrow=False, align=_xa, xanchor=_xa, yanchor=_ya,
                                font=dict(size=10.5, color="#8A98AC"),
                                bgcolor="rgba(247,249,252,0.65)", borderpad=2)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.scatter(
            pos_df, x="norm_total", y="NSS",
            size="언급량", color="브랜드",
            color_discrete_map=BRAND_COLORS, text="브랜드",
            size_max=70, title="① 화제성 × 호감도",
        )
        fig.update_traces(textposition="top center",
                          textfont=dict(size=10, color="#1B2A4A", family="Arial Black"))
        fig.add_hline(y=pos_df["NSS"].mean(), line_dash="dot", line_color="#A0AEC0")
        fig.add_vline(x=pos_df["norm_total"].mean(), line_dash="dot", line_color="#A0AEC0")
        fig.update_layout(
            xaxis_title="◀ 적게 언급　　　화제성 (언급량) — 얼마나 많이　　　많이 언급 ▶",
            yaxis_title="◀ 호감 낮음　　호감도 (NSS) — 얼마나 좋게　　호감 높음 ▶")
        _quad_labels(fig,
            "💎 알짜 호감<br>호감 높음·인지도 낮음",
            "🏆 시장 리더<br>많이 + 좋게 언급",
            "🌱 잠재·약세<br>인지도·호감 모두 낮음",
            "⚠️ 논란형<br>많이 언급되나 호감 약함")
        chart_style(fig, height=450, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = px.scatter(
            pos_df, x="긍정률", y="부정률",
            size="언급량", color="브랜드",
            color_discrete_map=BRAND_COLORS, text="브랜드",
            size_max=70, title="② 긍정 비율 × 부정 비율(리스크)",
        )
        fig2.update_traces(textposition="top center",
                           textfont=dict(size=10, color="#1B2A4A", family="Arial Black"))
        fig2.add_hline(y=pos_df["부정률"].mean(), line_dash="dot", line_color="#A0AEC0")
        fig2.add_vline(x=pos_df["긍정률"].mean(), line_dash="dot", line_color="#A0AEC0")
        fig2.update_layout(
            xaxis_title="◀ 긍정 적음　　　긍정 비율 (%)　　　긍정 많음 ▶",
            yaxis_title="◀ 리스크 낮음　　부정 비율 (%)　　리스크 높음 ▶")
        _quad_labels(fig2,
            "🚨 평판 위험<br>긍정 적고 부정 많음",
            "🔥 양극화<br>호불호 뚜렷",
            "😐 무관심·중립<br>긍·부정 모두 적음",
            "😀 안정 호감<br>긍정 많고 부정 적음")
        chart_style(fig2, height=450, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    <div class='insight-box' style='font-size:0.82rem;'>
    <b>사분면 읽는 법</b> &nbsp;① <b>화제성×호감도</b>: 오른쪽 위일수록 '많이 + 좋게' 언급되는 강자,
    오른쪽 아래는 화제는 많지만 평판이 약한 '논란형'입니다. &nbsp;
    ② <b>긍정×부정</b>: 오른쪽 아래(긍정↑·부정↓)가 가장 안전한 '안정 호감', 왼쪽 위(긍정↓·부정↑)는 '평판 위험'입니다.
    점선은 브랜드 평균선입니다.
    </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>경쟁 브랜드 경쟁력 레이더차트</div>", unsafe_allow_html=True)
    # [v2.7.0] 고정 추정치 대신 실측 지표로 계산 (축마다 표시 브랜드 중 최저 0 ~ 최고 100으로 환산)
    radar_axes, radar_raw = _radar_metrics(v, brand_df, f"{_VSIG}|{','.join(SEL_BRANDS)}")
    if radar_raw is None or len(radar_raw) < 2:
        st.info("레이더를 그릴 만큼 브랜드별 데이터가 충분하지 않습니다.")
        return
    _rb = brand_df.sort_values("언급량", ascending=False)["브랜드"].tolist()
    _show = [b for b in _rb if b != "파스쿠찌" and b in radar_raw.index][:5]
    _scaled = radar_raw.apply(lambda c: (c - c.min()) / (c.max() - c.min()) * 100 if c.max() > c.min() else c * 0 + 50)
    st.caption("파스쿠찌(굵은 선)와 언급량 상위 5개 브랜드 비교 · 축마다 브랜드 중 최저=0, 최고=100 · "
               "속성 축은 해당 속성을 언급한 글의 NSS(표본 10건 미만은 빈칸)")
    fig3 = go.Figure()
    colors_radar = ["#1B6CA8","#E8511D","#2CA02C","#9467BD","#D62728"]
    for name, color in zip(_show, colors_radar):
        vals = [None if pd.isna(x) else round(float(x), 1) for x in _scaled.loc[name, radar_axes]]
        fig3.add_trace(go.Scatterpolar(
            r=vals + [vals[0]], theta=radar_axes + [radar_axes[0]],
            fill=None, name=name, connectgaps=True,
            line=dict(color=color, width=1.8),
            marker=dict(size=4, color=color), opacity=0.7,
            customdata=[None if pd.isna(x) else round(float(x), 1) for x in radar_raw.loc[name, radar_axes]] + [None],
            hovertemplate="%{theta}: %{customdata}<extra>" + name + "</extra>",
        ))
    if "파스쿠찌" in _scaled.index:
        pv = [None if pd.isna(x) else round(float(x), 1) for x in _scaled.loc["파스쿠찌", radar_axes]]
        fig3.add_trace(go.Scatterpolar(
            r=pv + [pv[0]], theta=radar_axes + [radar_axes[0]],
            fill="toself", fillcolor="rgba(192,57,43,0.13)", name="★ 파스쿠찌", connectgaps=True,
            line=dict(color="#C0392B", width=5),
            marker=dict(size=9, color="#C0392B"),
            customdata=[None if pd.isna(x) else round(float(x), 1) for x in radar_raw.loc["파스쿠찌", radar_axes]] + [None],
            hovertemplate="%{theta}: %{customdata}<extra>파스쿠찌</extra>",
        ))
    fig3.update_layout(
        polar=dict(
            bgcolor="#FFFFFF",
            radialaxis=dict(visible=True, range=[0, 100],
                            gridcolor="#E2E8F0", tickfont=dict(color="#718096")),
            angularaxis=dict(gridcolor="#E2E8F0",
                             tickfont=dict(color="#2D3748", size=12)),
        ),
        legend=dict(bgcolor="#FFFFFF", bordercolor="#E2E8F0", borderwidth=1,
                    font=dict(color="#2D3748", size=12)),
        title="경쟁 브랜드 경쟁력 레이더 (선형 비교)",
        paper_bgcolor="#F7F9FC", height=500,
    )
    st.plotly_chart(fig3, use_container_width=True)

# ════════════════════════════════════════════════════
# TAB 10 — 키워드 버블
# ════════════════════════════════════════════════════
def _rt_kw():
    st.markdown("<div class='section-title'>☁️ 브랜드별 키워드 버블차트</div>", unsafe_allow_html=True)
    sel_b10 = st.selectbox("브랜드", SEL_BRANDS, key="kw_brand")
    n_kw10  = st.slider("표시 키워드 수", 15, 40, 25, key="kw_n")

    b10_docs = v[v["brands"].apply(lambda x: sel_b10 in x)]
    tokens10 = b10_docs["tokens_str"].str.cat(sep=" ").split()
    topN     = Counter(tokens10).most_common(n_kw10)

    if topN:
        words, counts = zip(*topN)
        # [v2.5.1] 트리맵 — 면적·색 농도=빈도, 인접 배치로 키워드 군집을 직관 파악
        base_color = BRAND_COLORS.get(sel_b10, "#2D6BC4")
        kw_df = pd.DataFrame({"키워드": list(words), "빈도": [int(c) for c in counts]})
        fig = px.treemap(
            kw_df, path=[px.Constant(f"{sel_b10} 키워드"), "키워드"], values="빈도",
            color="빈도", color_continuous_scale=["#EAF1FB", "#7FA8DC", base_color],
            title=f"{sel_b10} — 키워드 트리맵 (면적·색 = 언급 빈도)",
        )
        fig.update_traces(
            textinfo="label+value",
            textfont=dict(size=15),
            marker=dict(line=dict(width=1.5, color="white")),
            tiling=dict(pad=2),
        )
        fig.update_layout(height=520, margin=dict(t=50, b=10, l=10, r=10),
                          paper_bgcolor="#F7F9FC")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("사각형 크기·색 농도 = 언급 빈도. 인접한 키워드일수록 함께 묶여 보이므로, "
                   "양뿐 아니라 키워드 간 군집·연관 맥락에서 기획 영감을 얻을 수 있습니다.")

    st.markdown("<div class='section-title'>감성별 키워드 비교</div>", unsafe_allow_html=True)
    st.caption(f"선택 브랜드({sel_b10})의 긍정/부정 리뷰 TOP 키워드")
    c1, c2 = st.columns(2)
    for col, sent in zip([c1, c2], ["긍정","부정"]):
        with col:
            s_toks = b10_docs.loc[b10_docs["sentiment"]==sent, "tokens_str"].str.cat(sep=" ").split()
            s_top  = Counter(s_toks).most_common(12)
            if s_top:
                sw, sc = zip(*s_top)
                fig_s = px.bar(
                    x=list(sc), y=list(sw), orientation="h",
                    color=list(sc),
                    color_continuous_scale=["#EBF4FF", SENT_COLORS[sent]],
                    title=f"{sent} 리뷰 TOP 키워드",
                    text=[str(c) for c in sc],
                    labels={"x":"빈도","y":"키워드"},
                )
                fig_s.update_traces(textposition="outside")
                fig_s.update_layout(yaxis=dict(autorange="reversed"))
                chart_style(fig_s, height=380, showlegend=False)
                st.plotly_chart(fig_s, use_container_width=True)

    # [항목 3] 전체 데이터 기준 + 키워드 유형별(속성 카테고리) 감성 키워드 비교
    st.markdown("<div class='section-title'>전체 데이터 — 키워드 유형별 감성 비교</div>", unsafe_allow_html=True)
    st.caption("브랜드 무관 전체 VoC에서 속성 유형(맛·가격·공간 등)별로 긍정/부정 키워드를 구분해 비교")
    kw_type = st.selectbox("키워드 유형 선택", ["전체"] + list(ATTR_DICT.keys()), key="kwtype_sel")
    if kw_type == "전체":
        type_docs = v
    else:
        pat_t = "|".join(ATTR_DICT[kw_type])
        type_docs = v[v["full_text"].str.contains(pat_t, na=False)]
    cc1, cc2 = st.columns(2)
    for col, sent in zip([cc1, cc2], ["긍정","부정"]):
        with col:
            st_toks = type_docs.loc[type_docs["sentiment"]==sent, "tokens_str"].str.cat(sep=" ").split()
            # 유형 선택 시 해당 유형 키워드 위주로 필터
            if kw_type != "전체":
                attr_kws = ATTR_DICT[kw_type]
                st_toks = [t for t in st_toks if any(a in t for a in attr_kws)] or st_toks
            st_top = Counter(st_toks).most_common(12)
            if st_top:
                tw, tc = zip(*st_top)
                fig_t = px.bar(
                    x=list(tc), y=list(tw), orientation="h",
                    color=list(tc),
                    color_continuous_scale=["#EBF4FF", SENT_COLORS[sent]],
                    title=f"[{kw_type}] {sent} 키워드 (전체 {len(type_docs)}건)",
                    text=[str(c) for c in tc],
                    labels={"x":"빈도","y":"키워드"},
                )
                fig_t.update_traces(textposition="outside")
                fig_t.update_layout(yaxis=dict(autorange="reversed"))
                chart_style(fig_t, height=380, showlegend=False)
                st.plotly_chart(fig_t, use_container_width=True)

# ════════════════════════════════════════════════════
# TAB 11 — 소비 맥락
# ════════════════════════════════════════════════════
def _rt_occ():
    st.markdown("<div class='section-title'>🎯 소비 맥락 (Occasion) 분석</div>", unsafe_allow_html=True)

    occ_cnt = v["occasion"].value_counts().reset_index()
    occ_cnt.columns = ["상황","문서수"]
    fig = px.bar(
        occ_cnt, x="문서수", y="상황", orientation="h",
        color="문서수", color_continuous_scale=["#BEE3F8","#2D6BC4"],
        title="소비 상황별 언급량",
        text="문서수",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(yaxis=dict(autorange="reversed"))
    chart_style(fig, height=320, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-title'>소비 상황 × 브랜드 히트맵</div>", unsafe_allow_html=True)
    occs = [o for o in OCCASION_DICT.keys()] + ["기타"]
    occ_simple = pd.DataFrame(0, index=occs, columns=SEL_BRANDS)   # [v2.7.0] 전역 상세 매트릭스와 이름 분리
    for occ in occs:
        sub = v[v["occasion"] == occ]
        for b in SEL_BRANDS:
            cnt = sub["brands"].apply(lambda x: b in x).sum()
            occ_simple.loc[occ, b] = cnt
    fig2 = px.imshow(
        occ_simple,
        color_continuous_scale="Blues",
        title="소비 상황 × 브랜드 언급 히트맵 (건수)",
        text_auto=True, aspect="auto",
    )
    fig2.update_traces(textfont=dict(color="#1B2A4A", size=11))
    chart_style(fig2, height=380, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='section-title'>소비 상황별 감성 분포</div>", unsafe_allow_html=True)
    occ_sent = v.groupby(["occasion","sentiment"]).size().reset_index(name="수")
    fig3 = px.bar(
        occ_sent, x="occasion", y="수", color="sentiment",
        color_discrete_map=SENT_COLORS, barmode="stack",
        title="소비 상황별 감성 누적",
        labels={"occasion":"소비 상황","수":"문서 수"},
    )
    chart_style(fig3, height=340)
    st.plotly_chart(fig3, use_container_width=True)

    _box(*_ins_occasion(occ_simple))

    st.markdown("---")
    st.markdown("<div class='section-title'>🗂️ 소비맥락 세분화 (15유형) — 같은 화면 통합 [v2.3.4]</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🗂️ 소비맥락 세분화 — 15유형 × 브랜드 결합</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='insight-box'>
    기존 5~6개 일반 맥락을 <b>15개 세부 상황</b>으로 분화하고, <b>브랜드·감성과 교차</b>합니다.<br>
    "누가, 언제, 왜, 어떤 브랜드를" 선택하는지 입체적으로 파악해 타깃 마케팅 인사이트를 도출합니다.
    </div>""", unsafe_allow_html=True)

    if len(occ_detail_df) == 0:
        st.info("소비맥락 분석을 위한 데이터가 부족합니다.")
    else:
        c1, c2 = st.columns([1.3, 1])
        with c1:
            fig = px.bar(
                occ_detail_df.sort_values("언급량"),
                x="언급량", y="소비맥락", orientation="h",
                color="NSS", color_continuous_scale=["#E74C3C","#FFFFFF","#27AE60"],
                color_continuous_midpoint=0,
                title="15개 세부 소비맥락 언급량 (색상=NSS)",
                text="언급량",
            )
            fig.update_traces(textposition="outside")
            chart_style(fig, height=480, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown("<div class='section-title'>맥락별 긍정률 TOP</div>", unsafe_allow_html=True)
            for _, row in occ_detail_df.nlargest(8, "긍정률").iterrows():
                st.markdown(f"""
                <div style='background:#F0FFF4;border-left:3px solid #27AE60;
                            border-radius:0 6px 6px 0;padding:7px 11px;margin-bottom:5px;'>
                    <b style='color:#276749;font-size:0.85rem;'>{row['소비맥락']}</b>
                    <span style='float:right;color:#27AE60;font-weight:700;'>긍정 {row['긍정률']}%</span>
                    <div style='color:#718096;font-size:0.72rem;'>{row['언급량']}건 · NSS {row['NSS']:+.1f}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div class='section-title'>소비맥락 × 브랜드 교차 히트맵</div>", unsafe_allow_html=True)
        st.caption("각 소비 상황에서 어떤 브랜드가 주로 선택되는지 — 빈 셀이 파스쿠찌 진입 기회")
        fig2 = px.imshow(
            occ_brand_mat,
            color_continuous_scale="Blues",
            title="소비맥락 × 브랜드 언급 매트릭스",
            text_auto=True, aspect="auto",
        )
        fig2.update_traces(textfont=dict(color="#1B2A4A", size=10))
        chart_style(fig2, height=520, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

        _box(*_ins_occasion_detail(occ_brand_mat, occ_detail_df))


# ════════════════════════════════════════════════════
# TAB 12 — 리스크 탐지
# ════════════════════════════════════════════════════
def _rt_risk():
    st.markdown("<div class='section-title'>🚨 리스크 탐지 — 부정 드라이버 맵</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='danger-box'>
    <b>리스크 탐지</b>: 부정 리뷰에서 반복 등장하는 불만 패턴을 자동 감지합니다.
    빈도가 높고 여러 브랜드에 걸쳐 나타나는 키워드일수록 구조적 리스크 신호입니다.
    </div>""", unsafe_allow_html=True)

    neg_docs = v[v["sentiment"] == "부정"].copy()
    neg_tokens_all = neg_docs["tokens_str"].str.cat(sep=" ").split()
    neg_top40 = Counter(neg_tokens_all).most_common(40)

    c1, c2 = st.columns([1.2, 1])
    with c1:
        if neg_top40:
            nwords, ncounts = zip(*neg_top40)
            nc_arr = np.array(ncounts, dtype=float)
            np.random.seed(7)
            angles = np.linspace(0, 4*np.pi, len(nwords))
            radii  = np.linspace(0.1, 1.0, len(nwords))
            nx = radii*np.cos(angles) + np.random.uniform(-0.1, 0.1, len(nwords))
            ny = radii*np.sin(angles) + np.random.uniform(-0.1, 0.1, len(nwords))
            sizes = (nc_arr / nc_arr.max()) * 100 + 15
            fig = go.Figure()
            for word, cnt, xi, yi, sz in zip(nwords, ncounts, nx, ny, sizes):
                op = 0.4 + (cnt / nc_arr.max()) * 0.6
                fig.add_trace(go.Scatter(
                    x=[xi], y=[yi], mode="markers+text",
                    marker=dict(size=sz, color="#E74C3C", opacity=op,
                                line=dict(color="white", width=1.5)),
                    text=[word], textposition="middle center",
                    textfont=dict(size=max(8, min(14, int(sz/5))),
                                  color="#FFFFFF" if sz > 40 else "#742A2A"),
                    hovertemplate=f"<b>{word}</b><br>빈도: {cnt}회<extra></extra>",
                    showlegend=False,
                ))
            fig.update_layout(
                title="부정 리뷰 키워드 버블맵 (크기=빈도)",
                xaxis=dict(visible=False, range=[-1.5, 1.5]),
                yaxis=dict(visible=False, range=[-1.5, 1.5]),
                plot_bgcolor="#FFF5F5", paper_bgcolor="#F7F9FC", height=480,
            )
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("**브랜드별 주요 불만 키워드**")
        for b in SEL_BRANDS:
            neg_b   = v[(v["brands"].apply(lambda x: b in x)) & (v["sentiment"] == "부정")]
            neg_tok = neg_b["tokens_str"].str.cat(sep=" ").split()
            top5    = Counter(neg_tok).most_common(5)
            if not top5:
                continue
            color   = BRAND_COLORS.get(b, "#2D6BC4")
            kw_str  = "  ·  ".join([f"<b>{w}</b>({c})" for w, c in top5])
            st.markdown(f"""
            <div style='background:#FFFFFF;border:1px solid #E2E8F0;border-left:4px solid {color};
                        border-radius:0 8px 8px 0;padding:8px 12px;margin-bottom:6px'>
                <span style='font-weight:700;color:{color};font-size:0.88rem'>{b}</span>
                <div style='color:#C53030;font-size:0.82rem;margin-top:4px'>{kw_str}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>리스크 유형별 브랜드 히트맵</div>", unsafe_allow_html=True)
    risk_rows = []
    for risk_type, kws in RISK_PATTERNS.items():
        pat = "|".join(kws)
        for b in SEL_BRANDS:
            nb  = v[(v["brands"].apply(lambda x: b in x)) & (v["sentiment"] == "부정")]
            cnt = nb["full_text"].str.contains(pat, na=False).sum()
            risk_rows.append({"리스크 유형": risk_type, "브랜드": b, "빈도": cnt})
    risk_df = pd.DataFrame(risk_rows)
    risk_pivot = risk_df.pivot_table(index="브랜드", columns="리스크 유형",
                                     values="빈도", fill_value=0)
    if not risk_pivot.empty:
        fig2 = px.imshow(
            risk_pivot,
            color_continuous_scale=["#FFFFFF","#FED7D7","#E53E3E"],
            title="브랜드 × 리스크 유형 히트맵 (부정 리뷰 빈도)",
            text_auto=True, aspect="auto",
        )
        fig2.update_traces(textfont=dict(color="#1B2A4A", size=12))
        chart_style(fig2, height=320, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='section-title'>부정 리뷰 원문 탐색</div>", unsafe_allow_html=True)
    st.caption("브랜드 필터는 '주요 브랜드(본문 내 최다 언급)' 기준 — 곁가지로 스친 브랜드는 제외되어 정합성을 높였습니다.")
    rcol1, rcol2 = st.columns([1, 1])
    with rcol1:
        rb  = st.selectbox("브랜드 필터", ["전체"] + SEL_BRANDS, key="risk_b")
    with rcol2:
        rmode = st.radio("필터 기준", ["주요 브랜드만", "언급된 전체"], horizontal=True, key="risk_mode")
    rkw = st.text_input("키워드 검색", placeholder="예: 환불, 불매, 비싸", key="risk_kw")
    if rb == "전체":
        neg_show = neg_docs
    elif rmode == "주요 브랜드만":
        # [수정] primary_brand가 선택 브랜드인 문서만 — 무관 원문 혼입 방지
        neg_show = neg_docs[neg_docs["primary_brand"] == rb]
    else:
        neg_show = neg_docs[neg_docs["brands"].apply(lambda x: rb in x)]
    if rkw:
        neg_show = neg_show[neg_show["full_text"].str.contains(rkw, na=False)]
    show_cols = ["title","body","primary_brand","year_month","sentiment"]
    show_df = neg_show[show_cols].copy()
    show_df.columns = ["제목","본문","주요브랜드","작성월","감성"]
    show_df["본문"] = show_df["본문"].str[:200]
    st.dataframe(show_df.head(30), use_container_width=True, height=300,
                 column_config={"본문": st.column_config.TextColumn(width="large")})
    st.caption(f"{min(30, len(show_df))}건 표시 / 전체 {len(show_df)}건")

# ════════════════════════════════════════════════════
# TAB — 브랜드 로열티 (찐팬 지수) [고도화 A]
# ════════════════════════════════════════════════════
def _rt_loyalty():
    st.markdown("<div class='section-title'>💎 브랜드 로열티 (찐팬) 지수</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='insight-box'>
    단순 호불호(NSS)를 넘어, <b>"이 브랜드의 찐팬 비중"</b>을 측정합니다.<br>
    <b>독점충성</b>("여기 아니면 안 가", 가중치 3.0) · <b>강한애착</b>("최애·단골", 2.0) · <b>반복소비</b>("자주·매일", 1.0)
    신호어를 문서에서 탐지해 <b>로열티 지수(0~100)</b>와 <b>찐팬 비율(%)</b>로 산출합니다.
    </div>""", unsafe_allow_html=True)

    if len(loyalty_df) == 0:
        st.info("로열티 분석을 위한 데이터가 부족합니다.")
    else:
        c1, c2 = st.columns([1.3, 1])
        with c1:
            sorted_l = loyalty_df.sort_values("로열티지수")
            fig = px.bar(
                sorted_l, x="로열티지수", y="브랜드", orientation="h",
                color="로열티지수", color_continuous_scale=["#F5E6E0", "#E67E22", "#C0392B"],
                title="브랜드별 로열티 지수 (0~100)",
                text=sorted_l["로열티지수"].apply(lambda x: f"{x:.1f}"),
            )
            fig.update_traces(textposition="outside")
            fig.add_vline(x=loyalty_df["로열티지수"].mean(), line_dash="dot",
                          line_color="#718096",
                          annotation_text=f"평균 {loyalty_df['로열티지수'].mean():.1f}")
            chart_style(fig, height=420, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            for _, row in loyalty_df.head(6).iterrows():
                color = BRAND_COLORS.get(row["브랜드"], "#2D6BC4")
                st.markdown(f"""
                <div style='background:#FFFFFF;border:1px solid #E2E8F0;border-left:4px solid {color};
                            border-radius:0 8px 8px 0;padding:9px 12px;margin-bottom:6px;'>
                    <span style='font-weight:700;color:{color};font-size:0.9rem;'>{row['브랜드']}</span>
                    <span style='float:right;font-weight:800;color:{color};'>찐팬 {row['찐팬비율']}%</span>
                    <div style='color:#718096;font-size:0.78rem;margin-top:3px;'>
                        로열티 {row['로열티지수']} · 독점 {row['독점충성']} / 애착 {row['강한애착']} / 반복 {row['반복소비']}
                    </div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div class='section-title'>로열티 지수 × NSS 매트릭스</div>", unsafe_allow_html=True)
        st.caption("우상단 = 호감도와 충성도 모두 높은 '찐팬 보유 브랜드' / 우하단 = 호감은 있으나 충성 약함(재방문 유도 필요)")
        fig2 = go.Figure()
        for _, row in loyalty_df.iterrows():
            color = BRAND_COLORS.get(row["브랜드"], "#2D6BC4")
            fig2.add_trace(go.Scatter(
                x=[row["NSS"]], y=[row["로열티지수"]],
                mode="markers+text",
                marker=dict(size=max(row["언급량"]/8, 14), color=color, opacity=0.8,
                            line=dict(color="white", width=2)),
                text=[row["브랜드"]], textposition="top center",
                textfont=dict(size=11, color=color),
                name=row["브랜드"],
                hovertemplate=f"<b>{row['브랜드']}</b><br>NSS: {row['NSS']:+.1f}<br>로열티: {row['로열티지수']}<br>찐팬비율: {row['찐팬비율']}%<extra></extra>",
            ))
        fig2.add_hline(y=loyalty_df["로열티지수"].mean(), line_dash="dot", line_color="#A0AEC0")
        fig2.add_vline(x=loyalty_df["NSS"].mean(), line_dash="dot", line_color="#A0AEC0")
        fig2.update_layout(title="로열티 × NSS (버블=언급량)",
                           xaxis_title="NSS (호감도)", yaxis_title="로열티 지수 (충성도)",
                           showlegend=False)
        chart_style(fig2, height=460)
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<div class='section-title'>충성 신호 구성 (Stacked)</div>", unsafe_allow_html=True)
        fig3 = px.bar(
            loyalty_df.sort_values("찐팬비율"),
            x="브랜드", y=["독점충성", "강한애착", "반복소비"],
            title="브랜드별 충성 신호 문서 수 구성 (절대량)",
            color_discrete_map={"독점충성": "#C0392B", "강한애착": "#E67E22", "반복소비": "#F5C77E"},
            labels={"value": "문서 수", "variable": "충성 등급"},
        )
        chart_style(fig3, height=350)
        st.plotly_chart(fig3, use_container_width=True)

        # [기능 2] 절대량 ↔ 지수 차이 해설 — [v2.7.0] 데이터로 자동 생성
        _box(*_ins_loyalty(loyalty_df))

        st.dataframe(
            loyalty_df[["브랜드","언급량","로열티지수","찐팬비율","독점충성","강한애착","반복소비","NSS"]],
            use_container_width=True, hide_index=True,
        )


# ════════════════════════════════════════════════════
# TAB — 토픽 클러스터링 (토픽×브랜드×고객 중첩) [고도화 C]
# ════════════════════════════════════════════════════
# ════════════════════════════════════════════════════
# TAB — 트렌드 조기경보 (상대평가) [고도화 D]
# ════════════════════════════════════════════════════
def _rt_trend():
    """[v2.6.9] 통합 시장 트렌드 조기경보 — 단일 ES 엔진(커피·음료+푸드+식재료) 완전 통합."""
    st.markdown("<div class='section-title'>🌐 시장 트렌드 조기경보 — 커피·음료 + 푸드·식재료 통합 ES 엔진</div>",
                unsafe_allow_html=True)
    st.markdown("""
    <div class='insight-box'>
    커피 코어 VoC와 새로 발굴한 인접 식음료 VoC를 <b>하나의 ES 엔진</b>으로 통합 분석합니다.
    모든 메뉴·음료·식재료가 <b>동일 기준</b>(볼륨·모멘텀·성장기울기·평판)으로 비교되어, 시장 전체에서
    뜨는 시그널을 폭넓게 포착합니다. <span style='color:#94A3B8'>※ 브랜드 언급이 없어 NSS·SOV 등 브랜드 지표에는 반영되지 않는 트렌드 전용 레이어입니다.</span>
    </div>""", unsafe_allow_html=True)
    if market_corpus is None or len(market_corpus) == 0:
        st.info("통합 트렌드 데이터가 충분하지 않습니다.")
        return
    es_all, _months, _baseline = market_es
    if es_all is None or es_all.empty:
        st.info("통합 트렌드 데이터가 충분하지 않습니다.")
        return

    st.markdown(f"""
    <div class='warning-box'>
    <b>기준선(아메리카노·라떼) 월평균 언급량 = {_baseline}건 (30일 환산)</b><br>
    각 메뉴·식재료의 최근 언급량을 이 기준선과 비교해 <b>상대배수</b>를, 자체 추세로 <b>모멘텀·ES점수</b>를 산출합니다.<br>
    <span style='color:#7B6A3A'>추이는 기간 전체를 덮는 데이터(검색 상한 검색어·수집 당일 글 제외)로 계산하고
    월별 값은 30일 기준으로 환산합니다{(' · 분석 기간 ' + WIN_START + ' ~ ' + WIN_END) if WIN_START else ''}.</span>
    </div>""", unsafe_allow_html=True)

    # 카테고리 그룹 필터(커피·음료 / 푸드류 / 식재료)
    sel_g = st.radio("카테고리 구분", ["전체", "커피·음료", "푸드류", "식재료"], horizontal=True, key="mkt_grp")
    es_df = es_all if sel_g == "전체" else es_all[es_all["_group"] == sel_g]

    # 그룹 요약 카드
    gcols = st.columns(3)
    gemoji = {"커피·음료": "☕", "푸드류": "🥐", "식재료": "🧂"}
    for col, g in zip(gcols, ["커피·음료", "푸드류", "식재료"]):
        gd = es_all[es_all["_group"] == g]
        top = gd.iloc[0] if len(gd) else None
        with col:
            st.markdown(f"""
            <div style='background:#FFFFFF;border:1px solid #E2E8F0;border-top:3px solid #E67E22;
                        border-radius:8px;padding:10px;text-align:center;'>
                <div style='font-size:1.3rem;'>{gemoji[g]}</div>
                <div style='font-weight:700;color:#1B2A4A;font-size:0.85rem;'>{g}</div>
                <div style='color:#718096;font-size:0.72rem;'>{len(gd)}개 항목</div>
                <div style='color:#E67E22;font-weight:700;font-size:0.78rem;margin-top:3px;'>
                    TOP: {top['메뉴'] if top is not None else '—'} (ES {(top['ES점수'] if top is not None else 0):.0f})
                </div>
            </div>""", unsafe_allow_html=True)

    if len(es_df) == 0:
        st.info(f"{sel_g} 카테고리에 해당하는 항목이 없습니다.")
        return

    bev_n = int((market_corpus["_layer"] == "커피·음료").sum())
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("통합 분석 아이템", f"{len(es_all):,}개")
    m2.metric("커피·음료", f"{bev_n:,}건")
    m3.metric("푸드·식재료", f"{len(market_corpus) - bev_n:,}건")
    m4.metric("ES 1위", f"{es_all.iloc[0]['메뉴']}")

    cL, cR = st.columns([1.45, 1])
    with cL:
        st.markdown("<div class='section-title'>🎯 ES 포지셔닝 맵 — 성장 × 평판</div>", unsafe_allow_html=True)
        st.caption("우상단=기회(성장↑·호감↑) · 우하단=주의 · 좌상단=안정 강점 · 좌하단=쇠퇴 · 버블=볼륨")
        plot = es_df[es_df["볼륨"] >= 8].copy()
        if len(plot):
            _cap = plot["모멘텀"].quantile(0.95)
            plot["_momd"] = plot["모멘텀"].clip(upper=_cap)
            fig = px.scatter(plot, x="_momd", y="NSS", size="볼륨", color="카테고리", hover_name="메뉴",
                             size_max=44, hover_data={"_momd": False, "볼륨": True, "모멘텀": True, "ES점수": True},
                             labels={"_momd": "모멘텀(성장 배수)", "NSS": "평판(NSS)"})
            for _, r in plot.sort_values("ES점수", ascending=False).head(10).iterrows():
                fig.add_annotation(x=min(r["모멘텀"], _cap), y=r["NSS"], text=r["메뉴"],
                                   showarrow=False, font=dict(size=9, color="#1B2A4A"), yshift=10)
            fig.add_vline(x=plot["_momd"].median(), line_dash="dot", line_color="#A0AEC0")
            fig.add_hline(y=0, line_dash="dash", line_color="#A0AEC0")
            chart_style(fig, height=480)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("표시할 데이터가 부족합니다.")
    with cR:
        st.markdown("<div class='section-title'>조기경보 신호</div>", unsafe_allow_html=True)
        amap = {"성장 조짐": ("🚀", "#E67E22"), "안정": ("➡️", "#2980B9"), "둔화": ("📉", "#7F8C8D")}
        for _, r in es_df.head(8).iterrows():
            ic, clr = amap.get(r["경보"], ("•", "#2980B9"))
            st.markdown(f"""
            <div style='background:#FFFFFF;border:1px solid #E2E8F0;border-left:4px solid {clr};
                        border-radius:0 8px 8px 0;padding:8px 12px;margin-bottom:5px;'>
                <b style='color:{clr};font-size:0.85rem;'>{ic} {r['경보']} {r['메뉴']}</b>
                <div style='color:#718096;font-size:0.72rem;margin-top:2px;'>
                    상대배수 {r['상대배수']}배 · 기울기 {r['성장기울기']:+.1f} · 모멘텀 {r['모멘텀']:.1f} · NSS {r['NSS']:+.1f}
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>🗺️ 카테고리 트리맵 "
                "<span style='font-size:0.62em;color:#94A3B8;font-weight:600'>· 면적=볼륨, 색=평판(NSS)</span></div>",
                unsafe_allow_html=True)
    figt = px.treemap(es_df, path=[px.Constant("시장"), "카테고리", "메뉴"], values="볼륨",
                      color="NSS", color_continuous_scale=["#E74C3C", "#F4D03F", "#27AE60"],
                      color_continuous_midpoint=0)
    figt.update_traces(textinfo="label+value")
    figt.update_layout(margin=dict(t=10, l=0, r=0, b=0), height=440)
    st.plotly_chart(figt, use_container_width=True)

    st.markdown("<div class='section-title'>💧 카테고리 볼륨 변화 기여도 "
                "<span style='font-size:0.62em;color:#94A3B8;font-weight:600'>· 어떤 세부 메뉴가 끌어올렸나</span></div>",
                unsafe_allow_html=True)
    _cats = es_df["카테고리"].unique().tolist()
    sel_cat = st.selectbox("카테고리 선택", _cats, key="mkt_wf_cat")
    sub = es_df[es_df["카테고리"] == sel_cat].copy()
    sub["기여"] = sub["최근월"] - sub["기준평균"]
    sub = sub.sort_values("기여", ascending=False)
    contrib = pd.concat([sub.head(6), sub.tail(3)]).drop_duplicates("메뉴")
    start = float(sub["기준평균"].sum()); end = float(sub["최근월"].sum())
    measures = ["absolute"] + ["relative"] * len(contrib) + ["total"]
    xlab = ["기준월 평균"] + contrib["메뉴"].tolist() + ["최근월"]
    yval = [round(start, 1)] + contrib["기여"].round(1).tolist() + [round(end, 1)]
    txt = [f"{v:.0f}" if m != "relative" else f"{v:+.0f}" for v, m in zip(yval, measures)]
    figw = go.Figure(go.Waterfall(orientation="v", measure=measures, x=xlab, y=yval, text=txt,
                                  textposition="outside", increasing=dict(marker_color="#27AE60"),
                                  decreasing=dict(marker_color="#E74C3C"), totals=dict(marker_color="#1B2A4A"),
                                  connector=dict(line=dict(color="#B0B8C4", width=1))))
    figw.update_layout(title=f"{sel_cat} 볼륨 변화 (기준 {start:.0f} → 최근 {end:.0f}, {end-start:+.0f})", height=400)
    chart_style(figw, height=400, showlegend=False)
    st.plotly_chart(figw, use_container_width=True)

    if _months:
        st.markdown("<div class='section-title'>📈 상위 ES 시그널 월별 추이</div>", unsafe_allow_html=True)
        ts_rows = []
        for _, r in es_df.head(6).iterrows():
            for mi, m in enumerate(_months):
                ts_rows.append({"메뉴": r["메뉴"], "월": m,
                                "언급": r["_monthly"][mi] if mi < len(r["_monthly"]) else 0})
        figl = px.line(pd.DataFrame(ts_rows), x="월", y="언급", color="메뉴", markers=True,
                       title="상위 ES 6개 월별 언급 추이 (30일 환산)")
        chart_style(figl, height=340)
        st.plotly_chart(figl, use_container_width=True)

    with st.expander("📋 통합 ES 랭킹 상세"):
        st.dataframe(es_df[["메뉴", "카테고리", "_group", "볼륨", "상대배수", "모멘텀", "성장기울기", "NSS", "ES점수", "경보"]].head(40),
                     use_container_width=True, hide_index=True)

    # ── 페어링·변형 네트워크 ──
    st.markdown("<div class='section-title'>🔗 페어링·변형 네트워크 "
                "<span style='font-size:0.62em;color:#94A3B8;font-weight:600'>· 뭐랑 같이 먹고 어떻게 변형하나</span></div>",
                unsafe_allow_html=True)
    _nodes, _edges = pair_net
    if _nodes is None or len(_nodes) == 0:
        st.caption("페어링·변형 신호가 충분하지 않습니다.")
    else:
        _pos = _spring_layout(list(_nodes["키워드"]), _edges)
        _ex, _ey, _ew = [], [], []
        _maxw = max((w for _, _, w in _edges), default=1)
        for a, b, w in _edges:
            if a in _pos and b in _pos:
                _ex += [_pos[a][0], _pos[b][0], None]
                _ey += [_pos[a][1], _pos[b][1], None]
        edge_tr = go.Scatter(x=_ex, y=_ey, mode="lines",
                             line=dict(color="#CBD5E0", width=1.2), hoverinfo="none")
        _ccolor = {"커피·음료": "#6B4226", "디저트": "#E91E63", "베이커리": "#FF9800",
                   "카페푸드": "#4CAF50", "식재료·플레이버": "#3F51B5"}
        _kw = list(_nodes["키워드"])
        node_tr = go.Scatter(
            x=[_pos[k][0] for k in _kw], y=[_pos[k][1] for k in _kw],
            mode="markers+text", text=_kw, textposition="top center",
            marker=dict(size=(_nodes["빈도"].clip(upper=40) / 40 * 28 + 12),
                        color=[_ccolor.get(c, "#888") for c in _nodes["카테고리"]],
                        line=dict(color="white", width=1.2)),
            textfont=dict(size=10, color="#1B2A4A"),
            hovertext=[f"{k} · {c} · {f}건" for k, c, f in zip(_kw, _nodes["카테고리"], _nodes["빈도"])],
            hoverinfo="text")
        fign = go.Figure([edge_tr, node_tr])
        chart_style(fign, height=470, showlegend=False)
        fign.update_xaxes(visible=False)
        fign.update_yaxes(visible=False)
        st.plotly_chart(fign, use_container_width=True)
        st.caption("노드 크기=조합 글 등장 빈도 · 색=카테고리 · 연결선=함께 등장(가까울수록 자주). "
                   "예: 라떼 허브에 어떤 디저트·식재료가 매달려 있는지 = 신메뉴/세트 힌트")

    # ── 미등록 급상승어 레이더 (F&B 전용) ──
    st.markdown("<div class='section-title'>🌱 미등록 급상승어 레이더 "
                "<span style='font-size:0.62em;color:#94A3B8;font-weight:600'>· 사전에 없지만 최근 급증한 식음료 신조어</span></div>",
                unsafe_allow_html=True)
    st.caption("F&B 머리어(X라떼·X빵·X케이크…)·분류어 인접(○○ 원두/메뉴…) 패턴으로 식음료 후보만 추출합니다. "
               "사람이 원문 확인 후 사전에 편입하는 반자동 신호입니다.")
    if emergent_df is None or emergent_df.empty:
        st.caption("현재 조건을 만족하는 미등록 급상승 후보가 없습니다.")
    else:
        _show = emergent_df.head(12).sort_values("모멘텀")
        figm = px.bar(_show, x="모멘텀", y="신규어", orientation="h", color="패턴",
                      text=_show["최근월"].apply(lambda x: f"{x}건"),
                      title="미등록 급상승 식음료 후보 (모멘텀 = 최근월 ÷ 기준월 평균)")
        figm.update_traces(textposition="outside")
        chart_style(figm, height=380)
        st.plotly_chart(figm, use_container_width=True)
        _em_sel = st.selectbox("후보 원문 확인", emergent_df.head(12)["신규어"].tolist(), key="em_sel")
        if _em_sel:
            _eh = market_corpus[market_corpus["full_text"].str.contains(_em_sel, regex=False, na=False)]
            st.caption(f"'{_em_sel}' 관련 원문 {len(_eh):,}건 — 식음료 신조어인지 원문으로 확인 후 사전 편입")
            for _, r in _eh.head(3).iterrows():
                _sn = _kw_snippet(r["full_text"], _em_sel).replace("<", "&lt;").replace(">", "&gt;")
                _sn = _sn.replace(_em_sel, f"<b style='color:#E67E22'>{_em_sel}</b>")
                st.markdown(f"<div style='background:#FFF;border:1px solid #E2E8F0;border-left:4px solid #E67E22;"
                            f"border-radius:0 8px 8px 0;padding:7px 11px;margin-bottom:6px;'>"
                            f"<div style='color:#475569;font-size:0.76rem'>{_sn}</div></div>", unsafe_allow_html=True)

    # ── 키워드 원문 보기 (정밀: 문장 발췌 + 하이라이트 + 주변 감성) ──
    st.markdown("<div class='section-title'>🔎 키워드 원문 보기 "
                "<span style='font-size:0.62em;color:#94A3B8;font-weight:600'>· 키워드 문장 발췌 + 하이라이트 + 주변 감성</span></div>",
                unsafe_allow_html=True)
    _topkw = es_df.head(25)["메뉴"].tolist()
    if _topkw:
        sel_kw = st.selectbox("트렌드 키워드 선택", _topkw, key="mkt_kw_drill")
        if sel_kw:
            _hit = market_corpus[market_corpus["full_text"].str.contains(sel_kw, regex=False, na=False)].copy()
            _hit["_nsent"] = _hit["full_text"].apply(lambda t: _kw_neighbor_sentiment(t, sel_kw))
            _hit["_snip"] = _hit["full_text"].apply(lambda t: _kw_snippet(t, sel_kw))
            _hit = _hit[_hit["_snip"].astype(str).str.len().between(10, 280)]
            _p = (_hit["_nsent"] == "긍정").mean() * 100 if len(_hit) else 0
            _n = (_hit["_nsent"] == "부정").mean() * 100 if len(_hit) else 0
            st.caption(f"'{sel_kw}' 관련 원문 {len(_hit):,}건 · 키워드 주변 기준 긍정 {_p:.0f}% / 부정 {_n:.0f}%")
            dc1, dc2 = st.columns(2)
            for _col, _se, _sc, _lbl in [(dc1, "긍정", "#27AE60", "👍 긍정 원문"), (dc2, "부정", "#E74C3C", "👎 부정 원문")]:
                with _col:
                    st.markdown(f"**{_lbl}**")
                    _sub = _hit[_hit["_nsent"] == _se].head(3)
                    if len(_sub) == 0:
                        st.caption("해당 감성의 원문이 없습니다.")
                    for _, r in _sub.iterrows():
                        _snip = str(r["_snip"]).replace("<", "&lt;").replace(">", "&gt;")
                        _snip = _snip.replace(sel_kw, f"<b style='color:{_sc}'>{sel_kw}</b>")
                        src = str(r.get("source_name", ""))
                        st.markdown(f"<div style='background:#FFF;border:1px solid #E2E8F0;border-left:4px solid {_sc};"
                                    f"border-radius:0 8px 8px 0;padding:7px 11px;margin-bottom:6px;'>"
                                    f"<div style='color:#475569;font-size:0.76rem'>{_snip}</div>"
                                    f"<div style='color:#94A3B8;font-size:0.66rem;margin-top:3px'>· {src}</div></div>",
                                    unsafe_allow_html=True)


def _rt_product():
    st.markdown("<div class='section-title'>🛍️ 브랜드별 제품 언급·감성 분석</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='insight-box'>
    브랜드별로 가장 많이 언급되는 <b>제품(커피·음료·디저트·푸드 망라)</b>과 그 제품의
    <b>언급량·감성(NSS)·월별 추이</b>를 확인합니다. 시그니처 제품 발굴과 상품 기획에 활용합니다.
    </div>""", unsafe_allow_html=True)

    sel_bp = st.selectbox("브랜드 선택", SEL_BRANDS, key="product_brand")
    prod_df = compute_brand_products(v, sel_bp, _VSIG)

    if len(prod_df) == 0:
        st.info(f"{sel_bp}의 제품 언급 데이터가 부족합니다.")
    else:
        c1, c2 = st.columns([1.4, 1])
        with c1:
            top_prod = prod_df.head(15).sort_values("언급량")
            fig = px.bar(
                top_prod, x="언급량", y="제품", orientation="h",
                color="NSS", color_continuous_scale=["#E74C3C","#FFFFFF","#27AE60"],
                color_continuous_midpoint=0,
                title=f"{sel_bp} — 제품별 언급량 (색상=NSS)",
                text="언급량",
                hover_data=["카테고리","긍정","부정"],
            )
            fig.update_traces(textposition="outside")
            chart_style(fig, height=480, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown("<div class='section-title'>카테고리별 비중</div>", unsafe_allow_html=True)
            cat_sum = prod_df.groupby("카테고리")["언급량"].sum().reset_index()
            fig2 = px.pie(cat_sum, names="카테고리", values="언급량", hole=0.5,
                          color_discrete_sequence=["#2D6BC4","#E67E22","#27AE60"],
                          title="제품 카테고리 비중")
            chart_style(fig2, height=300)
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("<div class='section-title'>최다 언급 제품 TOP 5</div>", unsafe_allow_html=True)
            for _, row in prod_df.head(5).iterrows():
                nss_color = "#27AE60" if row["NSS"] > 0 else "#E74C3C"
                st.markdown(f"""
                <div style='background:#FFFFFF;border:1px solid #E2E8F0;border-left:3px solid {nss_color};
                            border-radius:0 6px 6px 0;padding:6px 10px;margin-bottom:4px;'>
                    <b style='font-size:0.85rem;'>{row['제품']}</b>
                    <span style='float:right;color:{nss_color};font-weight:700;'>NSS {row['NSS']:+.0f}</span>
                    <div style='color:#718096;font-size:0.72rem;'>{row['카테고리']} · {row['언급량']}건</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div class='section-title'>제품별 월별 언급량 · 감성 추이</div>", unsafe_allow_html=True)
        sel_prod = st.selectbox("제품 선택", prod_df["제품"].tolist(), key="product_item")
        ptrend = compute_product_trend(v, sel_bp, sel_prod, _VSIG, WIN_START, WIN_END)
        if len(ptrend) > 0 and ptrend["언급량"].sum() > 0:
            fig3 = make_subplots(specs=[[{"secondary_y": True}]])
            fig3.add_trace(go.Bar(
                x=ptrend["월"], y=ptrend["언급량"], name="언급량(30일 환산)",
                marker_color="#2D6BC4", opacity=0.75, customdata=ptrend["표본"],
                hovertemplate="%{x}: %{y:.1f}건 (표본 %{customdata}건)<extra></extra>",
            ), secondary_y=False)
            fig3.add_trace(go.Scatter(
                x=ptrend["월"], y=ptrend["NSS"], name="NSS", mode="lines+markers",
                line=dict(color="#E67E22", width=3), marker=dict(size=7),
            ), secondary_y=True)
            fig3.add_hline(y=0, line_dash="dot", line_color="#A0AEC0", secondary_y=True)
            fig3.update_layout(
                title=f"{sel_bp} — {sel_prod} 월별 언급량(30일 환산) & 감성 추이 · NSS는 5건 이상인 달만",
                paper_bgcolor="#F7F9FC", plot_bgcolor="#FFFFFF",
                font=dict(color="#2D3748"), height=400,
                legend=dict(orientation="h", y=1.1),
            )
            fig3.update_yaxes(title_text="언급량", secondary_y=False)
            fig3.update_yaxes(title_text="NSS", secondary_y=True, range=[-100, 100])
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info(f"{sel_prod}의 월별 추이 데이터가 부족합니다.")

        st.dataframe(prod_df, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════
# TAB — 프로모션 모니터링 [항목 5]
# ════════════════════════════════════════════════════
def _rt_promo():
    st.markdown("<div class='section-title'>🎁 프로모션 모니터링</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='insight-box'>
    통신·카드할인, 이벤트, 1+1, 굿즈 증정 등 <b>촉진(프로모션) 관련 담론</b>을 브랜드별로 모니터링하고,
    "할인 개꿀", "이벤트 필참", "잇템" 등 <b>고객 반응 강도</b>를 측정합니다.
    (전체 {promo_doc_count}건의 프로모션 언급 분석)
    </div>""", unsafe_allow_html=True)

    # [v2.4.1] 브랜드별 프로모션 언급량 시계열
    st.markdown("<div class='section-title'>📈 브랜드별 프로모션 언급량 추이 (시계열)</div>", unsafe_allow_html=True)
    _promo_pat = "|".join(sum(PROMO_DICT.values(), []))
    # [v2.7.0] 기간 전체를 덮는 글만, 월별 건수는 30일 환산
    _tvp = _ts_rows(v)
    _pv = _tvp[_tvp["full_text"].str.contains(_promo_pat, na=False)] if _tvp is not None and len(_tvp) else _tvp
    _md_p = _month_days(WIN_START, WIN_END)
    if _pv is not None and len(_pv) and _md_p:
        _rows_p = []
        for b in SEL_BRANDS:
            bd = _pv[_pv["brands"].apply(lambda x: b in x)]
            if len(bd) < 10:
                continue
            for (m, d), val in zip(sorted(_md_p.items()), _norm_monthly(bd.groupby("year_month").size(), _md_p)):
                _rows_p.append({"월": str(m), "브랜드": b, "언급량": val})
        if _rows_p:
            fig_pts = px.line(pd.DataFrame(_rows_p), x="월", y="언급량", color="브랜드",
                              color_discrete_map=BRAND_COLORS, markers=True,
                              title="브랜드별 월간 프로모션 언급량 추이 (30일 환산)")
            chart_style(fig_pts, height=380)
            st.plotly_chart(fig_pts, use_container_width=True)
            st.caption("프로모션 키워드 포함 글을 브랜드·월별 집계 · 기간 전체를 덮는 데이터 기준 "
                       "(검색 상한 검색어·수집 당일 글 제외, 표본 10건 미만 브랜드 제외). 브랜드 간 규모보다 흐름 비교용입니다.")
        else:
            st.caption("브랜드별 시계열을 표시할 데이터가 부족합니다.")
    else:
        st.caption("월별 데이터가 부족합니다.")

    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("<div class='section-title'>프로모션 유형별 언급량</div>", unsafe_allow_html=True)
        fig = px.bar(
            promo_total_df.sort_values("언급량"), x="언급량", y="프로모션",
            orientation="h", color="언급량",
            color_continuous_scale=["#FDE9D9","#E67E22"],
            title="촉진 유형별 언급량", text="언급량",
        )
        fig.update_traces(textposition="outside")
        chart_style(fig, height=340, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("<div class='section-title'>촉진 반응 강도 분포</div>", unsafe_allow_html=True)
        fig2 = px.bar(
            promo_react_df, x="반응", y="언급량",
            color="반응",
            color_discrete_map={"강한 긍정":"#C0392B","긍정":"#E67E22","부정":"#7F8C8D"},
            title="프로모션 반응 강도 분포", text="언급량",
        )
        fig2.update_traces(textposition="outside")
        chart_style(fig2, height=340, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # [v2.3.1] 최근 급증 프로모션 + 브랜드 cross 체크
    st.markdown("<div class='section-title'>🔥 최근 급증한 프로모션 활동</div>", unsafe_allow_html=True)
    st.caption("최근 30일 언급량을 직전 90일의 30일 환산 평균과 비교 — 🔥는 언급 2건 이상 & 50% 이상 급증 "
               "(기간 전체를 덮는 데이터 기준: 검색 상한 검색어·수집 당일 글 제외)")
    if len(promo_surge_df) > 0:
        cc1, cc2 = st.columns(2)
        with cc1:
            st.dataframe(promo_surge_df, use_container_width=True, hide_index=True, height=330)
        with cc2:
            fig_s = px.bar(promo_surge_df.sort_values("증감률"), x="증감률", y="프로모션",
                           orientation="h", color="증감률",
                           color_continuous_scale=["#2980B9", "#EDF1F5", "#E74C3C"],
                           color_continuous_midpoint=0, title="프로모션별 최근 증감률 (%)")
            chart_style(fig_s, height=330)
            st.plotly_chart(fig_s, use_container_width=True)
    st.markdown("**프로모션 × 브랜드 Cross 체크 (최근 60일) — 어떤 브랜드가 어떤 촉진을 주도했는가**")
    if hasattr(promo_cross_df, "values") and promo_cross_df.values.sum() > 0:
        fig_c = px.imshow(promo_cross_df, text_auto=True, aspect="auto",
                          color_continuous_scale="Oranges",
                          labels=dict(x="브랜드", y="프로모션", color="언급"))
        chart_style(fig_c, height=380)
        st.plotly_chart(fig_c, use_container_width=True)
    else:
        st.caption("최근 60일 프로모션 교차 데이터가 충분하지 않습니다.")

    # [기능 4] 최근 많이 언급된 프로모션 + 주력 브랜드
    st.markdown("<div class='section-title'>📅 최근 가장 많이 언급된 프로모션 & 주력 브랜드</div>", unsafe_allow_html=True)
    st.caption("최근 60일 기준(기간 전체를 덮는 데이터) — 어떤 촉진 활동이 화제이고, 어떤 브랜드가 그 활동을 주도하는지")
    if len(promo_recent_df) > 0:
        rc1, rc2 = st.columns([1.3, 1])
        with rc1:
            fig_r = px.bar(
                promo_recent_df.sort_values("최근언급"),
                x="최근언급", y="프로모션", orientation="h",
                color="최근언급", color_continuous_scale=["#FDE9D9","#E67E22"],
                title="최근 60일 프로모션 언급량", text="최근언급",
            )
            fig_r.update_traces(textposition="outside")
            chart_style(fig_r, height=320, showlegend=False)
            st.plotly_chart(fig_r, use_container_width=True)
        with rc2:
            st.markdown("**프로모션별 주력 브랜드**")
            for _, row in promo_recent_df.head(7).iterrows():
                bcolor = BRAND_COLORS.get(row["주력브랜드"], "#64748B")
                st.markdown(f"""
                <div style='background:#FFFFFF;border:1px solid #E2E8F0;border-left:3px solid {bcolor};
                            border-radius:0 6px 6px 0;padding:6px 10px;margin-bottom:4px;'>
                    <b style='font-size:0.82rem;'>{row['프로모션']}</b>
                    <span style='float:right;color:{bcolor};font-weight:700;font-size:0.8rem;'>{row['주력브랜드']}</span>
                    <div style='color:#718096;font-size:0.7rem;'>최근 {row['최근언급']}건 · 주력 {row['주력브랜드_언급']}건</div>
                </div>""", unsafe_allow_html=True)

    # [기능 4] 브랜드별 프로모션 적극도
    st.markdown("<div class='section-title'>브랜드별 프로모션 적극도</div>", unsafe_allow_html=True)
    st.caption("프로모션 언급 비중 = 해당 브랜드 프로모션 언급 ÷ 전체 언급. 프로모션을 가장 활발히 하는 브랜드 식별")
    if len(brand_promo_df) > 0:
        fig_bp = px.bar(
            brand_promo_df.sort_values("프로모션언급"),
            x="프로모션언급", y="브랜드", orientation="h",
            color="프로모션비중", color_continuous_scale=["#FDE9D9","#C0392B"],
            title="브랜드별 프로모션 언급량 (색상=프로모션 비중%)",
            text=brand_promo_df.sort_values("프로모션언급").apply(
                lambda r: f"{r['프로모션언급']}건 ({r['프로모션비중']}%)", axis=1),
        )
        fig_bp.update_traces(textposition="outside")
        chart_style(fig_bp, height=340, showlegend=True)
        st.plotly_chart(fig_bp, use_container_width=True)

    st.markdown("<div class='section-title'>프로모션 유형 × 브랜드 히트맵</div>", unsafe_allow_html=True)
    st.caption("어떤 브랜드가 어떤 촉진 활동으로 가장 많이 회자되는지 — 빈 셀은 파스쿠찌 차별화 기회")
    fig3 = px.imshow(
        promo_brand_mat, color_continuous_scale="Oranges",
        title="프로모션 유형 × 브랜드 언급 매트릭스",
        text_auto=True, aspect="auto",
    )
    fig3.update_traces(textfont=dict(color="#1B2A4A", size=11))
    chart_style(fig3, height=360, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

    # [기능 4] 촉진 활동별 반응 강도 — 0~100 지표화
    st.markdown("<div class='section-title'>촉진 활동별 반응 강도 지표 (0~100)</div>", unsafe_allow_html=True)
    st.caption("반응강도지표 = (강한긍정×2 + 긍정×1 − 부정×1)/언급량 을 0~100으로 정규화. 지속 관리용 지표")
    if len(promo_type_react_df) > 0:
        fig4 = px.bar(
            promo_type_react_df.sort_values("반응강도지표"),
            x="반응강도지표", y="프로모션", orientation="h",
            color="반응강도지표", color_continuous_scale=["#E74C3C","#F5C77E","#27AE60"],
            range_color=[0, 100],
            title="촉진 유형별 반응 강도 지표 (0~100)",
            text=promo_type_react_df.sort_values("반응강도지표")["반응강도지표"].apply(lambda x: f"{x:.0f}"),
            hover_data=["언급량","강한긍정","긍정","부정"],
        )
        fig4.update_traces(textposition="outside")
        chart_style(fig4, height=340, showlegend=True)
        st.plotly_chart(fig4, use_container_width=True)

    # [기능 5] 촉진 활동 세부 + 원문 출처 확인
    st.markdown("<div class='section-title'>🔎 프로모션 활동 세부 & 원문 확인</div>", unsafe_allow_html=True)
    st.caption("프로모션 유형을 선택하면 해당 키워드가 실제 포함된 문장을 발췌해 보여줍니다(무관 글 제외, 관련도순). [v2.5.2 정확도 개선]")
    sel_promo = st.selectbox("프로모션 유형 선택", list(PROMO_DICT.keys()), key="promo_detail_sel")
    detail_docs = get_promo_detail_docs(v, sel_promo)
    if len(detail_docs) == 0:
        st.info(f"{sel_promo} 관련 언급이 없습니다.")
    else:
        dc1, dc2 = st.columns([1, 2])
        with dc1:
            st.markdown(f"**{sel_promo} — 브랜드별 언급**")
            bc = Counter()
            for _, r in detail_docs.iterrows():
                for b in r["brands"]:
                    bc[b] += 1
            if bc:
                bc_df = pd.DataFrame([{"브랜드": b, "언급": c} for b, c in bc.most_common()])
                fig_d = px.bar(
                    bc_df.sort_values("언급"), x="언급", y="브랜드", orientation="h",
                    color="언급", color_continuous_scale=["#FDE9D9","#E67E22"],
                    text="언급",
                )
                fig_d.update_traces(textposition="outside")
                chart_style(fig_d, height=300, showlegend=False)
                st.plotly_chart(fig_d, use_container_width=True)
        with dc2:
            st.markdown(f"**{sel_promo} — 원문 출처 ({len(detail_docs)}건)**")
            _cols = ["title","발췌","primary_brand","year_month"] + (["post_url"] if "post_url" in detail_docs.columns else [])
            detail_show = detail_docs[_cols].copy()
            detail_show.columns = ["제목","원문 발췌(키워드 문장)","주요브랜드","작성월"] + (["원문링크"] if "post_url" in detail_docs.columns else [])
            st.dataframe(detail_show.head(20), use_container_width=True, height=320,
                         column_config={
                             "원문 발췌(키워드 문장)": st.column_config.TextColumn(width="large"),
                             "원문링크": st.column_config.LinkColumn(width="small") if "post_url" in detail_docs.columns else None,
                         })
            st.caption(f"{min(20, len(detail_show))}건 표시 / 전체 {len(detail_show)}건")

    _box(*_ins_promo(promo_type_react_df, promo_recent_df, brand_promo_all))


# ════════════════════════════════════════════════════
# TAB — 고객 클러스터링 & 페르소나 [항목 7]
# ════════════════════════════════════════════════════
def _rt_cluster():
    st.markdown("<div class='section-title'>👥 고객 클러스터링 & 페르소나</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:#F4F6FA;border:1px dashed #B6C2D6;border-radius:8px;
                padding:10px 14px;margin:2px 0 10px;color:#5A6678;font-size:0.86rem;'>
    <b style='color:#7A8699;'>ℹ️ 분석 설명</b> &nbsp; 고객을 <b>성향·특성·관심사</b>로 군집화해 <b>페르소나</b>를 도출하고,
    각 페르소나의 카페·커피 U&A, 관심사, 주요 브랜드를 정리합니다.
    <span style='color:#9AA6B8;'>(TF-IDF 텍스트 70% + 감성·충성도·브랜드수·디카페인 관심 등 행동 피처 30%)</span>
    </div>""", unsafe_allow_html=True)

    customer_cluster = compute_customer_clustering(v, 8, _VSIG)   # [v2.7.0] 탭을 열 때만 계산
    if customer_cluster is None:
        st.info("고객 클러스터링을 위한 데이터가 부족합니다. (30건 이상 필요)")
    else:
        sub_c = customer_cluster["sub"]
        profiles = customer_cluster["profiles"]
        pca_var = customer_cluster["pca_var"]

        st.markdown("<div class='section-title'>고객 세그먼트 분포 (PCA 2D)</div>", unsafe_allow_html=True)
        cluster_palette = ["#2D6BC4","#E67E22","#27AE60","#8E44AD","#E74C3C","#16A085",
                           "#D4A017","#C0392B","#5D6D7E","#117A65"]
        fig = go.Figure()
        # [v2.7.0] 화면에는 무작위 표본 점만 표시 (수만 개 점 렌더링으로 브라우저가 멈추는 문제 방지)
        _plot_c = sub_c.sample(n=min(len(sub_c), 4000), random_state=42) if len(sub_c) > 4000 else sub_c
        for prof in profiles:
            c = prof["cluster"]
            cdocs = _plot_c[_plot_c["cluster"] == c]
            persona = make_persona(prof)
            fig.add_trace(go.Scatter(
                x=cdocs["pca_x"], y=cdocs["pca_y"], mode="markers",
                name=f"C{c}: {persona['name']}",
                marker=dict(size=8, color=cluster_palette[c % len(cluster_palette)],
                            opacity=0.6, line=dict(color="white", width=0.5)),
                hovertemplate=f"<b>{persona['name']}</b><br>%{{text}}<extra></extra>",
                text=cdocs["title"].str[:30],
            ))
        bc_cent = customer_cluster.get("brand_centroids", {})
        if bc_cent:
            fig.add_trace(go.Scatter(
                x=[xy[0] for xy in bc_cent.values()], y=[xy[1] for xy in bc_cent.values()],
                mode="markers+text", text=list(bc_cent.keys()), textposition="top center",
                textfont=dict(size=11, color="#1B2A4A"),
                marker=dict(symbol="diamond", size=14, color="#1B2A4A",
                            line=dict(color="white", width=1.2)),
                name="브랜드 위치", hoverinfo="text"))
        fig.update_layout(
            title=f"고객 세그먼트 분포 + 인접 브랜드 (PC1 {pca_var[0]}% · PC2 {pca_var[1]}%)",
            xaxis_title="주성분 1", yaxis_title="주성분 2",
            paper_bgcolor="#F7F9FC", plot_bgcolor="#FFFFFF",
            font=dict(color="#2D3748"), height=480,
            legend=dict(bgcolor="#FFFFFF", bordercolor="#E2E8F0", borderwidth=1),
        )
        st.plotly_chart(fig, use_container_width=True)
        if len(_plot_c) < len(sub_c):
            st.caption(f"점은 전체 {len(sub_c):,}건 중 무작위 {len(_plot_c):,}건만 표시 · 세그먼트 비중과 페르소나 프로파일은 전체 문서 기준")

        st.markdown("<div class='section-title'>도출된 고객 페르소나</div>", unsafe_allow_html=True)
        st.caption("각 페르소나 카드 아래 '📂 상세 분석 보기'를 펼치면 마케팅 활용 정보와 감성·키워드 차트를 볼 수 있습니다.")
        for prof in profiles:
            persona = make_persona(prof)
            c = prof["cluster"]
            color = cluster_palette[c % len(cluster_palette)]
            brands_str = ", ".join(persona["brands"][:3]) if persona["brands"] else "특정 브랜드 없음"
            kw_str = ", ".join(persona["kw"][:6])
            life_str = " · ".join(persona["lifestyle"]) if persona["lifestyle"] else "—"
            co_str = ", ".join(persona["co_brands"]) if persona["co_brands"] else "—"
            st.markdown(f"""
            <div style='background:#FFFFFF;border:1px solid #E2E8F0;border-left:5px solid {color};
                        border-radius:10px;padding:14px 16px;margin:10px 0 0;
                        box-shadow:0 2px 6px rgba(0,0,0,0.05);'>
                <div style='color:{color};font-weight:800;font-size:1.05rem;'>C{c}. {persona['name']}</div>
                <div style='color:#718096;font-size:0.76rem;margin:2px 0 8px;'>👥 n={persona['n']}명 · 😊 NSS {persona['nss']:+.0f} · 💎 충성 {persona['loyalty']}% · 🌙 디카페인 {persona['decaf']}%</div>
                <div style='color:#2D3748;font-size:0.86rem;margin-bottom:8px;'>{persona['desc']}</div>
                <div style='font-size:0.78rem;color:#4A5568;'>
                    🏷️ <b>주요 브랜드</b>: {brands_str}　🌿 <b>라이프스타일</b>: {life_str}<br>
                    🔑 <b>관심 키워드</b>: {kw_str}
                </div>
            </div>""", unsafe_allow_html=True)
            with st.expander(f"📂 C{c}. {persona['name']} — 상세 분석 보기"):
                dc1, dc2 = st.columns([1, 1])
                with dc1:
                    st.markdown(f"📝 **설명** — {persona['desc']}")
                    st.markdown(f"☕ **카페·커피 U&A** — {persona['ua']}")
                    st.markdown(f"🎯 **추천 마케팅 액티비티** — {persona.get('marketing', '—')}")
                    st.markdown(f"😣 **Pain-point** — {persona.get('pain', '—')}")
                    st.markdown(f"🛒 **Key Buying Factor** — {persona.get('kbf', '—')}")
                    st.markdown(f"🌿 **라이프스타일·관심도** — {' · '.join(persona['lifestyle']) or '—'}")
                    st.markdown(f"📍 **주요 소비상황** — {', '.join(persona['occ']) or '—'}")
                    st.markdown(f"🏷️ **커피 브랜드** — {', '.join(persona['brands'][:3]) or '—'}")
                    st.markdown(f"🤝 **커피 외 동시언급 브랜드** — {', '.join(persona['co_brands']) or '—'}")
                    st.markdown(f"🔑 **관심 키워드** — {', '.join(persona['kw'][:8])}")
                with dc2:
                    cdocs = sub_c[sub_c["cluster"] == c]
                    sent_cnt = cdocs["sentiment"].value_counts()
                    if len(sent_cnt) > 0:
                        figp = px.pie(values=sent_cnt.values, names=sent_cnt.index, hole=0.5,
                                      color=sent_cnt.index, color_discrete_map=SENT_COLORS,
                                      title="세그먼트 감성 분포")
                        chart_style(figp, height=240)
                        st.plotly_chart(figp, use_container_width=True, key=f"persona_sent_{c}")
                    _alltok = cdocs["tokens_str"].str.cat(sep=" ").split()
                    _allow = set(_kw_clean(_alltok, 10000))
                    kwc = Counter([t for t in _alltok if t in _allow]).most_common(8)
                    if kwc:
                        figk = px.bar(x=[val for _, val in kwc][::-1], y=[k for k, _ in kwc][::-1],
                                      orientation="h", title="대표 키워드 Top 8 (정제)",
                                      color_discrete_sequence=["#8E44AD"])
                        chart_style(figk, height=240)
                        st.plotly_chart(figk, use_container_width=True, key=f"persona_kw_{c}")

        st.markdown("<div class='section-title'>세그먼트 × 브랜드 언급 히트맵</div>", unsafe_allow_html=True)
        seg_brand = pd.DataFrame(0, index=[f"C{p['cluster']}" for p in profiles], columns=SEL_BRANDS)
        for prof in profiles:
            c = prof["cluster"]
            cdocs = sub_c[sub_c["cluster"] == c]
            for b in SEL_BRANDS:
                seg_brand.loc[f"C{c}", b] = int(cdocs["brands"].apply(lambda x: b in x).sum())
        fig2 = px.imshow(
            seg_brand, color_continuous_scale="Purples",
            title="고객 세그먼트 × 브랜드 언급 매트릭스",
            text_auto=True, aspect="auto",
        )
        fig2.update_traces(textfont=dict(color="#1B2A4A", size=11))
        chart_style(fig2, height=320, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)


# ════════════════════════════════════════════════════
# [v2.5.1] 카테고리(segmented control) → 세부 탭 디스패치
# ════════════════════════════════════════════════════
_CATS = {
    "📊 시장·브랜드 진단": [
        ("📊 Overview", _rt_ov), ("📈 NSS 평판", _rt_nss), ("📣 SOV 분석", _rt_sov),
        ("💎 브랜드 로열티", _rt_loyalty), ("📍 포지셔닝맵", _rt_pos),
    ],
    "🧠 고객 이해": [
        ("👥 고객 클러스터링", _rt_cluster), ("🎯 소비 맥락", _rt_occ),
        ("🔍 드라이버 분석", _rt_absa), ("🗺️ 브랜드 이미지맵", _rt_ca),
    ],
    "🛍️ 상품기획 지원": [
        ("🛍️ 브랜드별 제품", _rt_product), ("📡 트렌드 조기경보", _rt_trend),
        ("☁️ 키워드 버블", _rt_kw),
    ],
    "📣 커뮤니케이션 인텔리전스": [
        ("🎯 LDA·토픽 클러스터", _rt_lda), ("🎁 프로모션 모니터링", _rt_promo),
        ("🔗 PMI 분석", _rt_pmi),
    ],
    "🚨 이슈 캐처": [
        ("⚡ Burst 탐지", _rt_burst), ("🚨 리스크 탐지", _rt_risk),
    ],
}
_CAT_DESC = {
    "📊 시장·브랜드 진단": "브랜드별 Status는? — 언급량·평판·SOV·로열티·포지셔닝 등",
    "🧠 고객 이해": "우리의 고객은 어떤 사람들인가? — 고객 프로파일링, 성향·특성·관심사별 군집분석, 만족/불만족 동인, 브랜드 이미지 매핑 등",
    "🛍️ 상품기획 지원": "지금 사람들의 관심 제품은 무엇인가? — 제품 담론 분석, 제품 유형별 트렌드 캐칭, 브랜드별 주요 키워드 등",
    "📣 커뮤니케이션 인텔리전스": "고객을 움직이는 것은 무엇인가? — 주제별 담론 분석, 프로모션 모니터, 경쟁 인식 분석 등",
    "🚨 이슈 캐처": "무엇을 조심할까? — 이상 급증·리스크 신호",
}
_cat_names = list(_CATS.keys())
# [v2.5.3] 메인 최상단 타이틀 + 대형 카테고리 버튼 + 세부탭 스타일
st.markdown("""
<style>
/* [v2.5.4] 카테고리 대형 버튼 — 글씨 키우고 볼드(라벨 내부 p/div까지 강제) */
div[data-testid="stHorizontalBlock"] .stButton button {
    min-height: 72px; font-size: 1.12rem; font-weight: 800;
    white-space: normal; line-height: 1.25; border-radius: 12px; padding: 8px 8px;
}
div[data-testid="stHorizontalBlock"] .stButton button p,
div[data-testid="stHorizontalBlock"] .stButton button div {
    font-weight: 800 !important;
}
/* [D2] 활성(선택) 버튼 — 진한 남색 대신 옅은 블루 배경 + 진한 글씨로 가독성 확보 */
div[data-testid="stHorizontalBlock"] .stButton button[kind="primary"],
div[data-testid="stHorizontalBlock"] .stButton button[data-testid="baseButton-primary"] {
    background-color: #DCE9F7 !important; border: 2px solid #4A89DC !important; color: #1B2A4A !important;
}
div[data-testid="stHorizontalBlock"] .stButton button[kind="primary"]:hover,
div[data-testid="stHorizontalBlock"] .stButton button[data-testid="baseButton-primary"]:hover {
    background-color: #CFE0F3 !important; border-color: #4A89DC !important; color: #1B2A4A !important;
}
/* [D2] 세부 분석 탭 — 영역/폰트 키우고 볼드 */
div[data-baseweb="tab-list"] { gap: 6px; }
button[data-baseweb="tab"] { padding-top: 12px !important; padding-bottom: 12px !important; }
button[data-baseweb="tab"] div[data-testid="stMarkdownContainer"] p,
button[data-baseweb="tab"] p {
    font-size: 1.06rem !important; font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)
# [D4] 메인 화면 최상단 타이틀
st.markdown("<div style='font-weight:800;font-size:1.6rem;color:#1B2A4A;"
            "margin:0 0 12px;letter-spacing:0.3px;'>Consumer Intelligence Dashboard</div>",
            unsafe_allow_html=True)
if st.session_state.get("cat_sel") not in _cat_names:
    st.session_state["cat_sel"] = _cat_names[0]
st.markdown("<div style='font-weight:800;font-size:1.08rem;color:#1B2A4A;margin:2px 0 8px;'>"
            "🧭 분석 영역</div>", unsafe_allow_html=True)
_bcols = st.columns(len(_cat_names))
for _i, _ck in enumerate(_cat_names):
    with _bcols[_i]:
        _active = (st.session_state["cat_sel"] == _ck)
        if st.button(_ck, key=f"catbtn_{_i}", use_container_width=True,
                     type=("primary" if _active else "secondary")):
            st.session_state["cat_sel"] = _ck
            (st.rerun if hasattr(st, "rerun") else st.experimental_rerun)()
_cat = st.session_state["cat_sel"]
# [D1] 카테고리 설명 — 풋노트(inform) 형태로 축소
st.markdown(
    f"<div style='background:#F4F7FB;border-left:3px solid #9DB8DC;border-radius:6px;"
    f"padding:5px 11px;margin:6px 0 12px;font-size:0.78rem;color:#6B7888;'>"
    f"ⓘ <b style='color:#5A6678;'>{_cat}</b> · {_CAT_DESC.get(_cat, '')}</div>",
    unsafe_allow_html=True)
_items = _CATS[_cat]
_subtabs = st.tabs([_lbl for _lbl, _ in _items])
for (_lbl, _fn), _tb in zip(_items, _subtabs):
    with _tb:
        _fn()


# ── 푸터 ──────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<p style='text-align:center;color:#A0AEC0;font-size:11px;'>"
    f"{COPYRIGHT}"
    f"</p>",
    unsafe_allow_html=True,
)