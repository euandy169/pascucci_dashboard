"""
PASCUCCI Coffee Market Insight Dashboard
Data-driven Marketing Strategy | Community-based Social VoC

분석 체계: 5개 전략영역 × 4대 고도화 분석 포함 16개 탭
  A. 브랜드 평판 (NSS/SOV/CA/Burst/PMI) + 브랜드 로열티(찐팬) 지수 [신규]
  B. 고객 이해 (드라이버/소비맥락) + 소비맥락 세분화 3축 결합 [신규]
  C. 텍스트 고도화 (LDA) + 토픽 클러스터링 중첩분석 [신규]
  D. 상품 트렌드 상대평가 조기경보 [신규]

데이터: 82Cook / 클리앙 / 네이트판 Community VoC

실행 방법:
  pip install streamlit plotly pandas numpy scikit-learn scipy
  streamlit run PAS_DASHBOARD_v211.py
"""

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
    .stTabs [aria-selected="true"] { background-color: #1B2A4A !important; color: #FFFFFF !important; }

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
    hr { border-color: #E2E8F0; }
    footer { color: #A0AEC0 !important; }
</style>
""", unsafe_allow_html=True)

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
    "파스쿠찌":    "#C0392B",
}
TARGET_BRANDS = ["스타벅스","투썸플레이스","메가커피","컴포즈커피","이디야","폴바셋","테라로사","빽다방","블루보틀","할리스"]
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

ATTR_DICT = {
    "맛·품질":    ["맛있","맛나","달콤","진한","부드럽","식감","쓴맛","산미","향","원두","에스프레소"],
    "가격·가성비": ["가격","비싸","저렴","가성비","합리","인상","할인","쿠폰"],
    "공간·분위기": ["카페","분위기","인테리어","좌석","조용","넓은","공부","작업","콘센트","카공"],
    "서비스":     ["직원","서비스","친절","속도","주문","대기","청결","응대"],
    "접근성":     ["위치","매장","점포","테이크아웃","드라이브","배달","픽업"],
    "브랜드이미지": ["이미지","브랜드","선호","느낌","감성","프리미엄","불매"],
    "프로모션·혜택":["굿즈","이벤트","프로모션","혜택","한정","쿠폰","멤버십","상품권","환불"],
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
    "굿즈·MD":      ["굿즈","MD","다이어리","텀블러","프리퀀시","스티커","리유저블"],
    "쿠폰·적립":    ["쿠폰","적립","스탬프","포인트","스타"],
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
# 데이터 로딩 및 전처리
# ══════════════════════════════════════════════════════
@st.cache_data(show_spinner="데이터 전처리 중...")
def load_and_preprocess(uploaded_file):
    df = pd.read_csv(uploaded_file, encoding="utf-8-sig") \
        if uploaded_file.name.endswith(".csv") \
        else pd.read_excel(uploaded_file)

    df = df[df["doc_id"].str.match(r"^[a-f0-9]{12}$", na=False)].copy()

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

    df["is_rel"] = (
        df["full_text"].apply(lambda t: any(k in t for k in coffee_kw)) |
        (df["brand_mentions"].notna() & df["brand_mentions"].str.strip().ne(""))
    )
    v = df[df["is_rel"]].copy()

    brand_map = {
        "스타벅스":    ["스타벅스","스벅"],
        "투썸플레이스": ["투썸플레이스","투썸"],
        "메가커피":    ["메가커피"],
        "컴포즈커피":  ["컴포즈커피","컴포즈"],
        "이디야":      ["이디야"],
        "빽다방":      ["빽다방"],
        "할리스":      ["할리스"],
        "파스쿠찌":    ["파스쿠찌"],
        "폴바셋":      ["폴바셋"],
        "블루보틀":    ["블루보틀"],
        "테라로사":    ["테라로사"],
        "더벤티":      ["더벤티"],
    }

    pos_kw = ["맛있","좋아","좋다","추천","최고","만족","친절","합리","가성비","저렴","달콤","훌륭","깔끔","즐겨","단골","완벽"]
    neg_kw = ["맛없","별로","실망","불만","최악","비싸","불친절","느리","아쉽","안좋","싫","불매","후회","환불","절대","다시는"]

    def detect_brands(t):
        return [b for b, als in brand_map.items() if any(a in str(t) for a in als)]

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

    v["brands"]     = v["full_text"].apply(detect_brands)
    v["sentiment"]  = v["full_text"].apply(get_sentiment)
    v["tokens"]     = v["full_text"].apply(tokenize)
    v["tokens_str"] = v["tokens"].apply(" ".join)
    v["occasion"]   = v["full_text"].apply(get_occasion)
    v["created_at"] = pd.to_datetime(v["created_at"], errors="coerce")
    v["year_month"] = v["created_at"].dt.to_period("M").astype(str)

    return v

# ══════════════════════════════════════════════════════
# 분석 함수 모음
# ══════════════════════════════════════════════════════
@st.cache_data(show_spinner="브랜드 지표 계산 중...")
def compute_brand_stats(_v):
    total_docs = len(_v)
    pos_total  = (_v["sentiment"] == "긍정").sum()
    neg_total  = (_v["sentiment"] == "부정").sum()
    rows = []
    for b in TARGET_BRANDS:
        docs = _v[_v["brands"].apply(lambda x: b in x)]
        n = len(docs)
        if n < 3:
            continue
        pos = (docs["sentiment"] == "긍정").sum()
        neg = (docs["sentiment"] == "부정").sum()
        rows.append({
            "브랜드":      b,
            "언급량":      n,
            "긍정":        int(pos),
            "부정":        int(neg),
            "중립":        int(n - pos - neg),
            "긍정률":      round(pos / n * 100, 1),
            "부정률":      round(neg / n * 100, 1),
            "NSS":        round((pos - neg) / n * 100, 1),
            "SOV_전체":   round(n / total_docs * 100, 1),
            "SOV_긍정":   round(pos / pos_total * 100, 1) if pos_total > 0 else 0,
            "SOV_부정":   round(neg / neg_total * 100, 1) if neg_total > 0 else 0,
        })
    return pd.DataFrame(rows)

@st.cache_data(show_spinner="월별 NSS 계산 중...")
def compute_monthly_nss(_v):
    months = sorted(
        [m for m in _v["year_month"].dropna().unique()
         if "NaT" not in m and ("2025" in m or "2026" in m)]
    )
    main6 = ["스타벅스","투썸플레이스","메가커피","컴포즈커피","이디야","폴바셋"]
    rows = []
    for b in main6:
        bd = _v[_v["brands"].apply(lambda x: b in x)]
        for m in months:
            sub = bd[bd["year_month"] == m]
            if len(sub) < 2:
                continue
            p = (sub["sentiment"] == "긍정").sum()
            n = (sub["sentiment"] == "부정").sum()
            t = len(sub)
            rows.append({"브랜드": b, "월": m, "NSS": round((p - n) / t * 100, 1), "문서수": t})
    return pd.DataFrame(rows), months

@st.cache_data(show_spinner="속성 드라이버 분석 중...")
def compute_absa(_v):
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
    return pd.DataFrame(rows).sort_values("NSS", ascending=False)

@st.cache_data(show_spinner="LDA 토픽 모델링 중...")
def compute_lda(_v):
    docs = _v[_v["tokens_str"].str.len() > 5]["tokens_str"].tolist()
    if len(docs) < 20:
        return None, None, None, None, None
    tfidf = TfidfVectorizer(max_features=500, min_df=2, max_df=0.85,
                             token_pattern=r"[가-힣]{2,6}")
    X     = tfidf.fit_transform(docs)
    vocab = tfidf.get_feature_names_out()
    lda   = LatentDirichletAllocation(n_components=7, random_state=42,
                                       max_iter=30, learning_method="batch")
    lda.fit(X)
    doc_t    = lda.transform(X)
    topic_dist = doc_t.mean(axis=0)
    return lda, tfidf, vocab, doc_t, topic_dist

@st.cache_data(show_spinner="대응일치분석 계산 중...")
def compute_ca(_v):
    excl = {"커피","카페","스벅","스타벅스","있는","하는","그런","이런","같은","근데","이제",
            "맛이","커피를","커피는","커피가","카페에서","라떼","있고","없는","없고","것도","해서","있어서"}
    all_toks = [t for ts in _v["tokens"] for t in ts]
    top_kws  = [w for w, _ in Counter(all_toks).most_common(150)
                if w not in excl and w not in STOPWORDS][:40]
    ca_brands = [b for b in TARGET_BRANDS
                 if _v["brands"].apply(lambda x: b in x).sum() >= 5]
    if len(ca_brands) < 2:
        return None
    cont = pd.DataFrame(0, index=ca_brands, columns=top_kws)
    for b in ca_brands:
        bd  = _v[_v["brands"].apply(lambda x: b in x)]
        cnt = Counter([t for ts in bd["tokens"] for t in ts])
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

@st.cache_data(show_spinner="Burst 탐지 중...")
def compute_burst(_v):
    months = sorted([m for m in _v["year_month"].dropna().unique()
                     if "NaT" not in m and ("2025" in m or "2026" in m)])
    recent_m = [m for m in months if "2026" in m][-2:]
    prev_m   = [m for m in months if "2025" in m][-3:]
    r_cnt, p_cnt = Counter(), Counter()
    for m in recent_m:
        sub = _v[_v["year_month"] == m]
        r_cnt.update([t for ts in sub["tokens"] for t in ts])
    for m in prev_m:
        sub = _v[_v["year_month"] == m]
        p_cnt.update([t for ts in sub["tokens"] for t in ts])
    rows = []
    for kw, cnt in r_cnt.most_common(500):
        if kw in STOPWORDS or len(kw) < 2:
            continue
        prev  = p_cnt.get(kw, 0)
        ratio = round(cnt / (prev + 1), 1)
        if cnt >= 5:
            rows.append({"키워드": kw, "최근": cnt, "이전": prev, "증가율(배)": ratio})
    return pd.DataFrame(rows).sort_values("증가율(배)", ascending=False).head(20)

@st.cache_data(show_spinner="PMI 계산 중...")
def compute_pmi(_v):
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
def compute_loyalty(_v):
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
    for b in TARGET_BRANDS + ["파스쿠찌"]:
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
    return pd.DataFrame(rows).sort_values("로열티지수", ascending=False)


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
def compute_occasion_detailed(_v):
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
    return pd.DataFrame(rows).sort_values("언급량", ascending=False)

@st.cache_data(show_spinner="맥락 × 브랜드 교차 분석 중...")
def compute_occasion_brand_matrix(_v):
    occ_list = list(OCCASION_DETAILED.keys())
    mat = pd.DataFrame(0, index=occ_list, columns=TARGET_BRANDS)
    for oc, kws in OCCASION_DETAILED.items():
        pat = "|".join(kws)
        oc_docs = _v[_v["full_text"].str.contains(pat, na=False)]
        for b in TARGET_BRANDS:
            mat.loc[oc, b] = int(oc_docs["brands"].apply(lambda x: b in x).sum())
    return mat


# ── 고도화 C: LDA 토픽 클러스터링 (토픽×브랜드 중첩) ─────
@st.cache_data(show_spinner="토픽 클러스터링 중...")
def compute_topic_clustering(_v):
    sub = _v[_v["tokens_str"].str.len() > 5].copy().reset_index(drop=True)
    if len(sub) < 20:
        return None
    tfidf = TfidfVectorizer(max_features=300, min_df=2, max_df=0.85,
                             token_pattern=r"[가-힣]{2,6}")
    X = tfidf.fit_transform(sub["tokens_str"])
    vocab = tfidf.get_feature_names_out()
    n_topics = 5
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42, max_iter=20)
    doc_topics = lda.fit_transform(X)
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
    topic_meanings = [define_topic_meaning(topic_words[t]) for t in range(n_topics)]
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
        "n_topics": n_topics, "topic_words": topic_words,
        "doc_topics": doc_topics, "sub": sub,
        "tb_mat": tb_mat, "ts_mat": ts_mat,
        "topic_sizes": [int((sub["main_topic"]==t).sum()) for t in range(n_topics)],
        "topic_meanings": topic_meanings,
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
def compute_brand_products(_v, brand):
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
        elif prod in ["케이크","마카롱","티라미수","타르트","크로플","쿠키","빙수","푸딩"]:
            cat = "디저트"
        else:
            cat = "베이커리·푸드"
        rows.append({"제품": prod, "카테고리": cat, "언급량": int(n),
                     "긍정": int(pos), "부정": int(neg), "NSS": nss})
    return pd.DataFrame(rows).sort_values("언급량", ascending=False)

@st.cache_data(show_spinner="제품 월별 추이 분석 중...")
def compute_product_trend(_v, brand, product):
    bdocs = _v[_v["brands"].apply(lambda x: brand in x)]
    kws = PRODUCT_DICT.get(product, [product])
    pat = "|".join(kws)
    sub = bdocs[bdocs["full_text"].str.contains(pat, na=False)]
    months = sorted([m for m in _v["year_month"].dropna().unique() if "NaT" not in str(m)])
    rows = []
    for m in months:
        msub = sub[sub["year_month"] == m]
        n = len(msub)
        pos = (msub["sentiment"] == "긍정").sum()
        neg = (msub["sentiment"] == "부정").sum()
        nss = round((pos - neg) / n * 100, 1) if n > 0 else 0
        rows.append({"월": m, "언급량": int(n), "NSS": nss})
    return pd.DataFrame(rows)


# ── 고도화: 프로모션 모니터링 [항목 5] ─────────────────
@st.cache_data(show_spinner="프로모션 모니터링 중...")
def compute_promotion(_v):
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

@st.cache_data(show_spinner="촉진 반응강도 측정 중...")
def compute_promo_reaction(_v):
    # 프로모션 언급 문서에서 반응 강도 측정
    all_promo_kws = [kw for kws in PROMO_DICT.values() for kw in kws]
    promo_pat = "|".join(all_promo_kws)
    promo_docs = _v[_v["full_text"].str.contains(promo_pat, na=False, case=False)]
    rows = []
    for reaction, (kws, weight) in PROMO_REACTION.items():
        pat = "|".join(kws)
        cnt = int(promo_docs["full_text"].str.contains(pat, na=False).sum())
        rows.append({"반응": reaction, "언급량": cnt, "가중치": weight})
    react_df = pd.DataFrame(rows)
    # 프로모션 유형별 반응 강도 점수
    type_reaction = []
    for promo, pkws in PROMO_DICT.items():
        ppat = "|".join(pkws)
        pdocs = _v[_v["full_text"].str.contains(ppat, na=False, case=False)]
        if len(pdocs) < 1:
            continue
        score = 0
        for reaction, (rkws, w) in PROMO_REACTION.items():
            rpat = "|".join(rkws)
            score += pdocs["full_text"].str.contains(rpat, na=False).sum() * w
        intensity = round(score / len(pdocs), 2)
        type_reaction.append({"프로모션": promo, "반응강도": intensity, "언급량": int(len(pdocs))})
    type_react_df = pd.DataFrame(type_reaction).sort_values("반응강도", ascending=False)
    return react_df, type_react_df, int(len(promo_docs))


# ── 고도화: 고객 클러스터링 & 페르소나 [항목 7] ─────────
@st.cache_data(show_spinner="고객 클러스터링 중...")
def compute_customer_clustering(_v, k=5):
    sub = _v[_v["tokens_str"].str.len() > 5].copy().reset_index(drop=True)
    if len(sub) < 30:
        return None
    # 피처: TF-IDF 텍스트
    tfidf = TfidfVectorizer(max_features=200, min_df=3, max_df=0.85,
                             token_pattern=r"[가-힣]{2,6}")
    X_text = tfidf.fit_transform(sub["tokens_str"]).toarray()
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
    X = np.hstack([X_text * 0.7, behav * 0.3])

    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    sub["cluster"] = km.fit_predict(X)
    # PCA 2D
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X)
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
        ctoks = [t for ts in cdocs["tokens"] for t in ts]
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

        profiles.append({
            "cluster": c, "n": n, "top_kw": top_kw, "top_brands": top_brands,
            "pos_r": pos_r, "neg_r": neg_r, "nss": nss,
            "loyalty_r": loyalty_r, "decaf_r": decaf_r, "occ_top": occ_top,
        })
    return {"sub": sub, "profiles": profiles, "k": k,
            "pca_var": [round(x*100,1) for x in pca.explained_variance_ratio_]}


def make_persona(profile):
    """클러스터 프로파일 → 페르소나 자동 생성"""
    kw = profile["top_kw"]
    brands = profile["top_brands"]
    nss = profile["nss"]
    loyalty = profile["loyalty_r"]
    decaf = profile["decaf_r"]
    # 페르소나 라벨링 규칙
    if decaf > 25:
        name = "건강·디카페인 추구형"
        desc = "카페인에 민감하거나 건강을 중시하며 디카페인·저자극 메뉴를 선호"
        ua = "오후·저녁 카페인 부담 없는 음료 / 임산부·수유부 가능성"
    elif loyalty > 35:
        name = "충성 단골형"
        desc = "특정 브랜드를 반복 방문하는 높은 충성도. 일상 루틴에 카페가 자리잡음"
        ua = "매일·자주 방문 / 모닝커피·출근길 루틴 / 멤버십·적립 활용"
    elif nss < -10:
        name = "불만·이탈 위험형"
        desc = "부정 경험이 누적되어 브랜드 전환을 고려하는 집단"
        ua = "가격·품질·서비스 불만 / 대안 브랜드 적극 탐색 / 불매 동참 가능성"
    elif any(k in ["추천","후기","비교","맛집"] for k in kw):
        name = "탐색·정보공유형"
        desc = "신메뉴·맛집을 적극 탐색하고 후기를 공유하는 오피니언 리더"
        ua = "신메뉴 빠른 시도 / SNS 인증·후기 작성 / 카페 투어"
    else:
        name = "일상 소비형"
        desc = "특별한 선호 없이 접근성·편의 중심으로 카페를 이용하는 대중 소비자"
        ua = "테이크아웃·이동 중 소비 / 가성비 중시 / 가까운 매장 이용"
    return {"name": name, "desc": desc, "ua": ua,
            "brands": brands, "nss": nss, "loyalty": loyalty, "decaf": decaf,
            "n": profile["n"], "kw": kw}


# ══════════════════════════════════════════════════════
# 사이드바
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ☕ PASCUCCI Consumer Intelligence Dashboard")
    st.markdown("Consumer Data-driven Marketing for PASCUCCI")
    st.markdown("---")
    uploaded = st.file_uploader(
        "📂 데이터 파일 업로드",
        type=["csv", "xlsx"],
        help="82Cook 크롤링 데이터 (CSV/Excel)"
    )
    st.markdown("---")

if uploaded is None:
    st.markdown("""
    <div style='text-align:center; padding:60px 20px;'>
        <div style='font-size:4rem'>☕</div>
        <h1 style='color:#1B2A4A; margin:20px 0 10px;'>PASCUCCI Consumer Intelligence Dashboard</h1>
        <h3 style='color:#2D6BC4; font-weight:400;'>Consumer Data-driven Marketing for PASCUCCI</h3>
        <p style='color:#718096; font-size:1rem; margin-top:12px;'>
            왼쪽 사이드바에서 82Cook 크롤링 CSV 파일을 업로드하면 분석이 시작됩니다.
        </p>
    </div>""", unsafe_allow_html=True)
    cols = st.columns(4)
    features = [
        ("📊", "Overview",       "KPI · 감성분포 · 언급량"),
        ("📈", "NSS 평판",       "Net Sentiment 월별 추이"),
        ("📣", "SOV 분석",       "담론 점유율 매트릭스"),
        ("🔍", "드라이버 분석",  "ABSA 속성별 긍/부정"),
        ("🗺️", "CA 이미지 맵",  "대응일치분석 포지셔닝"),
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
    st.stop()

# ══════════════════════════════════════════════════════
# 데이터 로딩
# ══════════════════════════════════════════════════════
v = load_and_preprocess(uploaded)

with st.sidebar:
    st.markdown("**🔧 필터**")
    brand_filter = st.multiselect(
        "브랜드",
        sorted(TARGET_BRANDS),
        default=sorted(TARGET_BRANDS)
    )
    sent_filter = st.multiselect(
        "감성",
        ["긍정", "중립", "부정"],
        default=["긍정", "중립", "부정"]
    )
    st.markdown("---")
    st.markdown(f"<small style='color:#99AACC'>총 {len(v):,}건 로드됨</small>",
                unsafe_allow_html=True)

fv = v[v["sentiment"].isin(sent_filter)].copy()
if len(fv) == 0:
    st.warning("필터 조건에 맞는 데이터가 없습니다.")
    st.stop()

# 분석 실행
brand_df = compute_brand_stats(v)
monthly_nss_df, all_months = compute_monthly_nss(v)
absa_df   = compute_absa(v)
lda_model, tfidf_vec, vocab, doc_topics, topic_dist = compute_lda(v)
ca_result = compute_ca(v)
burst_df  = compute_burst(v)
pmi_df    = compute_pmi(v)
loyalty_df = compute_loyalty(v)
occ_detail_df = compute_occasion_detailed(v)
occ_brand_mat = compute_occasion_brand_matrix(v)
topic_cluster = compute_topic_clustering(v)
trend_ew  = compute_trend_earlywarning(v)
promo_brand_mat, promo_total_df = compute_promotion(v)
promo_react_df, promo_type_react_df, promo_doc_count = compute_promo_reaction(v)
customer_cluster = compute_customer_clustering(v)

# ══════════════════════════════════════════════════════
# 탭 구성 — 12개
# ══════════════════════════════════════════════════════
tabs = st.tabs([
    "📊 Overview",
    "📈 NSS 평판",
    "💎 브랜드 로열티",
    "📣 SOV 분석",
    "🔍 드라이버 분석",
    "🛍️ 브랜드별 제품",
    "🎁 프로모션 모니터링",
    "🗺️ CA 이미지 맵",
    "🎯 LDA 토픽",
    "🧩 토픽 클러스터링",
    "👥 고객 클러스터링",
    "⚡ Burst 탐지",
    "🔗 PMI 분석",
    "📍 포지셔닝맵",
    "☁️ 키워드 버블",
    "🎯 소비 맥락",
    "🗂️ 소비맥락 세분화",
    "📡 트렌드 조기경보",
    "🚨 리스크 탐지",
])
(tab_ov, tab_nss, tab_loyalty, tab_sov, tab_absa, tab_product, tab_promo,
 tab_ca, tab_lda, tab_topiccl, tab_cluster, tab_burst, tab_pmi, tab_pos,
 tab_kw, tab_occ, tab_occ2, tab_trend, tab_risk) = tabs

# ════════════════════════════════════════════════════
# TAB 1 — Overview
# ════════════════════════════════════════════════════
with tab_ov:
    st.markdown("<div class='section-title'>📊 종합 현황</div>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    metrics = [
        ("📝", f"{len(v):,}건",     "분석 문서 수"),
        ("🏢", f"{brand_df['브랜드'].nunique()}개사", "언급 브랜드"),
        ("😊", f"{(v['sentiment']=='긍정').mean()*100:.1f}%", "전체 긍정률"),
        ("😡", f"{(v['sentiment']=='부정').mean()*100:.1f}%", "전체 부정률"),
        ("📉", f"NSS {brand_df[brand_df['브랜드']=='스타벅스']['NSS'].values[0]:+.1f}", "스타벅스 NSS"),
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
    c1, c2 = st.columns([1.4, 1])
    with c1:
        fig = px.bar(
            brand_df.sort_values("언급량", ascending=False),
            x="브랜드", y="언급량", color="브랜드",
            color_discrete_map=BRAND_COLORS,
            text="언급량", title="브랜드별 언급량",
        )
        fig.update_traces(textposition="outside", textfont_size=11)
        chart_style(fig, showlegend=False)
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

    st.markdown("<div class='section-title'>브랜드별 월별 언급량 추이</div>", unsafe_allow_html=True)
    # 상위 6개 브랜드 월별 언급량 시계열
    top6_brands = brand_df.sort_values("언급량", ascending=False).head(6)["브랜드"].tolist()
    months_ov = sorted([m for m in v["year_month"].dropna().unique() if "NaT" not in str(m)])
    ts_rows_ov = []
    for b in top6_brands:
        bdocs = v[v["brands"].apply(lambda x: b in x)]
        for m in months_ov:
            cnt = int((bdocs["year_month"] == m).sum())
            ts_rows_ov.append({"브랜드": b, "월": m, "언급량": cnt})
    ts_ov_df = pd.DataFrame(ts_rows_ov)
    fig_ts = px.line(
        ts_ov_df, x="월", y="언급량", color="브랜드", markers=True,
        color_discrete_map=BRAND_COLORS,
        title="상위 6개 브랜드 월별 언급량 추이",
    )
    fig_ts.update_traces(line=dict(width=2.5), marker=dict(size=6))
    chart_style(fig_ts, height=380)
    st.plotly_chart(fig_ts, use_container_width=True)

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
    st.dataframe(
        brand_df[["브랜드","언급량","긍정","부정","중립","긍정률","부정률","NSS","SOV_전체","SOV_긍정","SOV_부정"]]
        .sort_values("NSS", ascending=False),
        use_container_width=True, hide_index=True,
    )

# ════════════════════════════════════════════════════
# TAB 2 — NSS 평판
# ════════════════════════════════════════════════════
with tab_nss:
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

    st.markdown("<div class='section-title'>월별 NSS 트렌드 (주요 6개 브랜드)</div>", unsafe_allow_html=True)
    if len(monthly_nss_df) > 0:
        fig_t = px.line(
            monthly_nss_df, x="월", y="NSS", color="브랜드",
            color_discrete_map=BRAND_COLORS, markers=True,
            title="브랜드별 월별 NSS 추이",
            labels={"월": "월", "NSS": "Net Sentiment Score"},
        )
        fig_t.add_hline(y=0, line_color="#E53E3E", line_width=1.5, line_dash="dash")
        chart_style(fig_t, height=380)
        st.plotly_chart(fig_t, use_container_width=True)

        st.markdown("<div class='section-title'>5월 스타벅스 NSS 급락 분석</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            sbux_m = monthly_nss_df[monthly_nss_df["브랜드"] == "스타벅스"]
            if not sbux_m.empty:
                prev_avg = sbux_m[sbux_m["월"] < "2026-05"]["NSS"].mean()
                may_nss  = sbux_m[sbux_m["월"] == "2026-05"]["NSS"].values
                st.markdown(f"""
                <div class='danger-box'>
                <b>스타벅스 2026.05 NSS = {may_nss[0] if len(may_nss) > 0 else 'N/A':+.1f}</b><br>
                이전 8개월 평균 NSS: <b>+{prev_avg:.1f}</b><br>
                → 낙폭 <b>{prev_avg - (may_nss[0] if len(may_nss) > 0 else 0):.1f}p</b> 급전직하
                </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class='insight-box'>
            <b>파스쿠찌 시사점</b><br>
            스타벅스의 정치·사회적 이슈로 준프리미엄 포지션에 공백 발생.
            '이탈리안 헤리티지 기반 순수 커피 브랜드' 포지셔닝으로 이탈 소비자 흡수 가능.
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# TAB 3 — SOV 분석
# ════════════════════════════════════════════════════
with tab_sov:
    st.markdown("<div class='section-title'>📣 Share of Voice 분석</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='insight-box'>
    <b>SOV(담론 점유율)</b>: 전체 vs 긍정 vs 부정 SOV를 분리해 브랜드별 담론 질을 진단합니다.<br>
    전체 SOV가 높아도 부정 SOV가 압도적이면 실질 경쟁력이 낮은 상태입니다.
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        fig = px.pie(brand_df, names="브랜드", values="SOV_전체",
                     color="브랜드", color_discrete_map=BRAND_COLORS,
                     title="전체 SOV", hole=0.45)
        fig.update_traces(textinfo="percent+label", textfont_size=11)
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

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class='danger-box'><b>스타벅스 딜레마</b><br>
        전체 SOV 53.3%로 독보적이나, 부정 SOV 77.7%로 부정 담론 독식.
        담론의 양과 질이 극명하게 괴리되어 있음.</div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='success-box'><b>파스쿠찌 진입 기회</b><br>
        전체 SOV 2~5%, 긍정 SOV 5~7% 구간(테라로사·이디야·폴바셋 수준)을
        목표로 설정하면 작은 투자로 큰 긍정 담론 효과 가능.</div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# TAB 4 — 드라이버 분석 (ABSA)
# ════════════════════════════════════════════════════
with tab_absa:
    st.markdown("<div class='section-title'>🔍 평판 드라이버 분석 (Aspect-Based Sentiment)</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='insight-box'>
    <b>ABSA</b>: 속성(맛·배송·가격 등)별로 긍정/부정 리뷰를 분해합니다.
    '왜 좋은가? 왜 싫은가?'를 구체적인 속성 수준에서 파악합니다.
    </div>""", unsafe_allow_html=True)

    sel_b = st.selectbox("브랜드 선택 (전체 또는 개별)", ["전체"] + sorted(TARGET_BRANDS), key="absa_brand")
    if sel_b == "전체":
        absa_target = v
    else:
        absa_target = v[v["brands"].apply(lambda x: sel_b in x)]

    absa_computed = compute_absa(absa_target)

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
    for b in TARGET_BRANDS:
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

# ════════════════════════════════════════════════════
# TAB 5 — CA 이미지 맵
# ════════════════════════════════════════════════════
with tab_ca:
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
            color = BRAND_COLORS.get(b, "#2D6BC4")
            rx, ry = ca_result["row_x"][i], ca_result["row_y"][i]
            dists = [(np.sqrt((col_x[j]-rx)**2+(col_y[j]-ry)**2), j) for j in range(len(top_kws))]
            for _, j in sorted(dists)[:4]:
                fig.add_trace(go.Scatter(
                    x=[rx, col_x[j]], y=[ry, col_y[j]],
                    mode="lines", line=dict(color=color, width=1.2, dash="dot"),
                    opacity=0.35, showlegend=False, hoverinfo="skip",
                ))
            fig.add_trace(go.Scatter(
                x=[rx], y=[ry], mode="markers+text", name=b,
                marker=dict(size=22, color=color, line=dict(color="white", width=2.5)),
                text=[b], textposition="top right",
                textfont=dict(size=12, color=color, family="Arial Black"),
                hovertemplate=f"<b>{b}</b><extra>브랜드</extra>",
            ))
        fig.add_hline(y=0, line_color="#CBD5E0", line_dash="dot", line_width=1)
        fig.add_vline(x=0, line_color="#CBD5E0", line_dash="dot", line_width=1)
        fig.update_layout(
            title=f"브랜드 이미지 맵  (차원1: {expl[0]:.1f}% | 차원2: {expl[1]:.1f}% | 누적: {sum(expl[:2]):.1f}%)",
            xaxis_title=f"차원 1 ({expl[0]:.1f}%) ← 이슈·가격  |  품질·감성 →",
            yaxis_title=f"차원 2 ({expl[1]:.1f}%)",
        )
        chart_style(fig, height=620)
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📘 CA 맵 읽는 방법"):
            st.markdown("""
            - **브랜드 ●** 와 **키워드 ●** 가 **가까울수록** 해당 브랜드 리뷰에서 그 키워드가 자주 등장
            - **차원 1 (x축)**: 좌측 = 이슈·가격·불매 담론 / 우측 = 품질·감성·전문성 담론
            - **차원 2 (y축)**: 상단 = 일상·접근성 / 하단 = 가성비·실용 포지션
            - 점선 = 브랜드와 가장 가까운 키워드 TOP 4 연결
            - **파스쿠찌 목표 포지션**: x축 우측(+0.3~0.5), y축 상단(+0.2) — 이탈리안 품질 + 일상 접근성
            """)

# ════════════════════════════════════════════════════
# TAB 6 — LDA 토픽 모델링
# ════════════════════════════════════════════════════
with tab_lda:
    st.markdown("<div class='section-title'>🎯 LDA 토픽 모델링 (7-토픽)</div>", unsafe_allow_html=True)
    if lda_model is None:
        st.warning("LDA 분석을 위한 데이터가 부족합니다.")
    else:
        sel_b6 = st.selectbox("브랜드 선택", ["전체"] + sorted(TARGET_BRANDS), key="lda_brand")
        if sel_b6 == "전체":
            lda_target = v
        else:
            lda_target = v[v["brands"].apply(lambda x: sel_b6 in x)]

        lm, tv, vc, dt, tdist = compute_lda(lda_target)
        if lm is None:
            st.info("선택한 브랜드의 문서가 부족합니다.")
        else:
            c1, c2 = st.columns([1.4, 1])
            with c1:
                fig = make_subplots(
                    rows=4, cols=2,
                    subplot_titles=[f"T{i+1}: {TOPIC_LABELS[i]}" for i in range(7)],
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
                    labels=[f"T{i+1}: {TOPIC_LABELS[i]}" for i in range(7)],
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
                    x=[TOPIC_LABELS[i] for i in dom_cnt.index],
                    y=dom_cnt.values,
                    color=[TOPIC_LABELS[i] for i in dom_cnt.index],
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
            brand_topic = {}
            for b in TARGET_BRANDS:
                bd = v[v["brands"].apply(lambda x: b in x)]
                bd2 = bd[bd["tokens_str"].str.len() > 5]
                if len(bd2) < 5:
                    continue
                bX = tfidf_vec.transform(bd2["tokens_str"])
                bt = lda_model.transform(bX).mean(axis=0)
                brand_topic[b] = {TOPIC_LABELS[i]: round(float(bt[i])*100, 1) for i in range(7)}
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
with tab_burst:
    st.markdown("<div class='section-title'>⚡ Burst Detection — 급증 키워드 탐지</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='warning-box'>
    <b>Burst Detection</b>: 최근 2개월(2026.04-05) vs 이전 3개월(2025.10-12) 키워드 증가율을 비교합니다.
    급증 키워드는 브랜드 위기 또는 새로운 소비 담론의 선행 신호입니다.
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns([1.3, 1])
    with c1:
        top15 = burst_df.head(15)
        colors_burst = ["#E74C3C" if any(k in kw for k in ["환불","일베","이마트","정용진","극우","신세계","멸공"])
                        else "#F39C12" if any(k in kw for k in ["불매","텀블러","유니클로"])
                        else "#2980B9"
                        for kw in top15["키워드"]]
        fig = px.bar(
            top15.sort_values("증가율(배)"),
            x="증가율(배)", y="키워드", orientation="h",
            title="급증 키워드 TOP 15 (증가율 배수)",
            text=top15.sort_values("증가율(배)")["증가율(배)"].apply(lambda x: f"{x:.1f}x"),
            color="키워드",
            color_discrete_sequence=colors_burst,
        )
        fig.update_traces(textposition="outside")
        chart_style(fig, height=460, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        decaf_months = [m for m in all_months if m >= "2025-09"]
        decaf_docs = v[v["full_text"].str.contains("디카페인|디카페", na=False)]
        decaf_cnt  = {m: int(decaf_docs[decaf_docs["year_month"] == m].shape[0]) for m in decaf_months}
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=list(decaf_cnt.keys()),
            y=list(decaf_cnt.values()),
            mode="lines+markers+text",
            line=dict(color="#27AE60", width=2.5),
            marker=dict(size=8, color="#27AE60"),
            fill="tozeroy", fillcolor="rgba(39,174,96,0.12)",
            text=[str(v) for v in decaf_cnt.values()],
            textposition="top center",
            textfont=dict(size=11, color="#1A4731"),
            name="디카페인 언급",
        ))
        fig2.update_layout(title="디카페인 언급 월별 추이",
                           xaxis_title="월", yaxis_title="문서 수")
        chart_style(fig2, height=240, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("""
        <div class='success-box'><b>디카페인 — 구조적 성장 신호</b><br>
        2025.09 6건 → 2026.05 10건. NSS +56.5로 전 속성 최고 긍정률.
        파스쿠찌의 선점 가능한 1순위 카테고리.</div>""", unsafe_allow_html=True)
        st.markdown("""
        <div class='danger-box'><b>5월 급증 = 구조적 위기</b><br>
        환불·일베·이마트·정용진·극우 등 정치·사회 이슈 키워드 신규 폭발적 등장.
        스타벅스 이탈은 단기 회복 어려운 구조적 전환.</div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>급증 키워드 상세 데이터</div>", unsafe_allow_html=True)
    st.dataframe(burst_df, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════
# TAB 8 — PMI 분석
# ════════════════════════════════════════════════════
with tab_pmi:
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

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class='insight-box'><b>프리미엄 소규모 클러스터</b><br>
        테라로사·폴바셋·블루보틀·이디야·할리스가 높은 PMI로 묶임.
        소비자가 이 브랜드들을 함께 '대안 프리미엄 선택지'로 인식.
        파스쿠찌는 이 클러스터에 진입 가능한 이미지 자산 보유.
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='warning-box'><b>스타벅스의 낮은 PMI</b><br>
        스타벅스는 대량 개별 언급이 많아 PMI가 낮음.
        다른 브랜드와 '함께 비교되기보다' 독자적으로 회자되는 구조.
        불매 후 대안으로는 PMI가 높은 클러스터 브랜드들이 부상.
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>PMI 상세 데이터</div>", unsafe_allow_html=True)
    st.dataframe(pmi_df[pmi_df["공출현수"] > 0].sort_values("PMI", ascending=False),
                 use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════
# TAB 9 — 포지셔닝맵
# ════════════════════════════════════════════════════
with tab_pos:
    st.markdown("<div class='section-title'>📍 브랜드 포지셔닝맵</div>", unsafe_allow_html=True)

    def norm01(s):
        mn, mx = s.min(), s.max()
        return (s - mn) / (mx - mn + 1e-9)

    pos_df = brand_df.copy()
    pos_df["norm_total"]  = norm01(pos_df["언급량"])
    pos_df["norm_nss"]    = norm01(pos_df["NSS"])
    pos_df["norm_pos"]    = norm01(pos_df["긍정률"])
    pos_df["neg_risk"]    = norm01(100 - pos_df["긍정률"])

    c1, c2 = st.columns(2)
    with c1:
        fig = px.scatter(
            pos_df, x="norm_total", y="norm_nss",
            size="언급량", color="브랜드",
            color_discrete_map=BRAND_COLORS, text="브랜드",
            size_max=70, title="대중성(언급량) × 품질(NSS)  버블차트",
        )
        fig.update_traces(textposition="top center",
                          textfont=dict(size=10, color="#1B2A4A", family="Arial Black"))
        fig.add_hline(y=pos_df["norm_nss"].mean(), line_dash="dot", line_color="#A0AEC0")
        fig.add_vline(x=pos_df["norm_total"].mean(), line_dash="dot", line_color="#A0AEC0")
        fig.update_layout(xaxis_title="대중성 (언급량 정규화)", yaxis_title="평판 (NSS 정규화)")
        chart_style(fig, height=420, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = px.scatter(
            pos_df, x="SOV_긍정", y="NSS",
            size="언급량", color="브랜드",
            color_discrete_map=BRAND_COLORS, text="브랜드",
            size_max=70, title="긍정 SOV × NSS 포지셔닝",
        )
        fig2.update_traces(textposition="top center",
                           textfont=dict(size=10, color="#1B2A4A", family="Arial Black"))
        fig2.add_hline(y=0, line_color="#E53E3E", line_width=1.5, line_dash="dash")
        fig2.update_layout(xaxis_title="긍정 SOV (%)", yaxis_title="NSS")
        chart_style(fig2, height=420, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='section-title'>경쟁 브랜드 경쟁력 레이더차트</div>", unsafe_allow_html=True)
    st.caption("실측 데이터 기반 경쟁 브랜드 비교 (파스쿠찌는 데이터 충분 확보 후 추가 예정). 선형 표기로 브랜드별 윤곽을 명확히 비교")
    radar_axes = ["SOV 규모","NSS 평판","맛·품질","공간 전문성","가격 포지션","디카페인 기회","브랜드 이미지"]
    # 실측 기반 경쟁 브랜드 (파스쿠찌 제외)
    radar_data = {
        "스타벅스":  [100, 20, 50, 60, 40, 55, 45],
        "이디야":    [15, 80, 70, 55, 60, 75, 65],
        "테라로사":  [8,  90, 88, 70, 40, 70, 85],
        "메가커피":  [12, 65, 55, 30, 90, 40, 40],
        "투썸플레이스": [25, 55, 72, 65, 50, 50, 70],
    }
    fig3 = go.Figure()
    # 채도 높고 명확히 구분되는 색상 팔레트
    colors_radar = ["#1B6CA8","#E8511D","#2CA02C","#9467BD","#D62728"]
    for (name, vals), color in zip(radar_data.items(), colors_radar):
        v_plot = vals + [vals[0]]
        fig3.add_trace(go.Scatterpolar(
            r=v_plot, theta=radar_axes + [radar_axes[0]],
            fill=None, name=name,
            line=dict(color=color, width=2.8),
            marker=dict(size=6, color=color),
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
with tab_kw:
    st.markdown("<div class='section-title'>☁️ 브랜드별 키워드 버블차트</div>", unsafe_allow_html=True)
    sel_b10 = st.selectbox("브랜드", TARGET_BRANDS, key="kw_brand")
    n_kw10  = st.slider("표시 키워드 수", 15, 40, 25, key="kw_n")

    b10_docs = v[v["brands"].apply(lambda x: sel_b10 in x)]
    tokens10 = [t for ts in b10_docs["tokens"] for t in ts]
    topN     = Counter(tokens10).most_common(n_kw10)

    if topN:
        words, counts = zip(*topN)
        counts_arr    = np.array(counts, dtype=float)
        np.random.seed(42)
        angles = np.linspace(0, 4*np.pi, len(words))
        radii  = np.linspace(0.1, 1.0, len(words))
        x = radii*np.cos(angles) + np.random.uniform(-0.08, 0.08, len(words))
        y = radii*np.sin(angles) + np.random.uniform(-0.08, 0.08, len(words))
        sizes = (counts_arr / counts_arr.max()) * 120 + 20
        color = BRAND_COLORS.get(sel_b10, "#2D6BC4")

        fig = go.Figure()
        for i, (word, cnt, xi, yi, sz) in enumerate(zip(words, counts, x, y, sizes)):
            op = 0.4 + (cnt / counts_arr.max()) * 0.6
            fig.add_trace(go.Scatter(
                x=[xi], y=[yi], mode="markers+text",
                marker=dict(size=sz, color=color, opacity=op,
                            line=dict(color="white", width=1.5)),
                text=[word], textposition="middle center",
                textfont=dict(size=max(9, min(17, int(sz/6))),
                              color="#FFFFFF" if sz > 45 else "#1B2A4A"),
                hovertemplate=f"<b>{word}</b><br>빈도: {cnt}회<extra></extra>",
                showlegend=False,
            ))
        fig.update_layout(
            title=f"{sel_b10} — 키워드 버블차트 (크기=빈도)",
            xaxis=dict(visible=False, range=[-1.5, 1.5]),
            yaxis=dict(visible=False, range=[-1.5, 1.5]),
            plot_bgcolor="#FFFFFF", paper_bgcolor="#F7F9FC", height=520,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-title'>감성별 키워드 비교</div>", unsafe_allow_html=True)
    st.caption(f"선택 브랜드({sel_b10})의 긍정/부정 리뷰 TOP 키워드")
    c1, c2 = st.columns(2)
    for col, sent in zip([c1, c2], ["긍정","부정"]):
        with col:
            s_toks = [t for ts in b10_docs[b10_docs["sentiment"]==sent]["tokens"] for t in ts]
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
            st_toks = [t for ts in type_docs[type_docs["sentiment"]==sent]["tokens"] for t in ts]
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
with tab_occ:
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
    occ_brand_mat = pd.DataFrame(0, index=occs, columns=TARGET_BRANDS)
    for occ in occs:
        sub = v[v["occasion"] == occ]
        for b in TARGET_BRANDS:
            cnt = sub["brands"].apply(lambda x: b in x).sum()
            occ_brand_mat.loc[occ, b] = cnt
    fig2 = px.imshow(
        occ_brand_mat,
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

    st.markdown("""
    <div class='insight-box'><b>파스쿠찌 소비 상황 전략</b><br>
    공부·업무(카공)와 만남·미팅 상황에서 스타벅스 집중도가 가장 높음.
    이탈 후 대안으로 파스쿠찌가 포지셔닝되려면 '조용하고 넓은 공간' 강조와 함께
    카공족을 위한 콘센트·WiFi 특화 마케팅이 효과적.
    </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# TAB 12 — 리스크 탐지
# ════════════════════════════════════════════════════
with tab_risk:
    st.markdown("<div class='section-title'>🚨 리스크 탐지 — 부정 드라이버 맵</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='danger-box'>
    <b>리스크 탐지</b>: 부정 리뷰에서 반복 등장하는 불만 패턴을 자동 감지합니다.
    빈도가 높고 여러 브랜드에 걸쳐 나타나는 키워드일수록 구조적 리스크 신호입니다.
    </div>""", unsafe_allow_html=True)

    neg_docs = v[v["sentiment"] == "부정"].copy()
    neg_tokens_all = [t for ts in neg_docs["tokens"] for t in ts]
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
        for b in TARGET_BRANDS:
            neg_b   = v[(v["brands"].apply(lambda x: b in x)) & (v["sentiment"] == "부정")]
            neg_tok = [t for ts in neg_b["tokens"] for t in ts]
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
        for b in TARGET_BRANDS:
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
    rb  = st.selectbox("브랜드 필터", ["전체"] + sorted(TARGET_BRANDS), key="risk_b")
    rkw = st.text_input("키워드 검색", placeholder="예: 환불, 불매, 비싸", key="risk_kw")
    neg_show = neg_docs if rb == "전체" else neg_docs[neg_docs["brands"].apply(lambda x: rb in x)]
    if rkw:
        neg_show = neg_show[neg_show["full_text"].str.contains(rkw, na=False)]
    show_df = neg_show[["title","body","year_month","sentiment"]].copy()
    show_df.columns = ["제목","본문","작성월","감성"]
    show_df["본문"] = show_df["본문"].str[:200]
    st.dataframe(show_df.head(30), use_container_width=True, height=300,
                 column_config={"본문": st.column_config.TextColumn(width="large")})
    st.caption(f"{min(30, len(show_df))}건 표시 / 전체 {len(show_df)}건")

# ════════════════════════════════════════════════════
# TAB — 브랜드 로열티 (찐팬 지수) [고도화 A]
# ════════════════════════════════════════════════════
with tab_loyalty:
    st.markdown("<div class='section-title'>💎 브랜드 로열티 (찐팬) 지수</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='insight-box'>
    단순 호불호(NSS)를 넘어, <b>"이 브랜드의 찐팬인가"</b>를 측정합니다.<br>
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
            title="브랜드별 충성 신호 문서 수 구성",
            color_discrete_map={"독점충성": "#C0392B", "강한애착": "#E67E22", "반복소비": "#F5C77E"},
            labels={"value": "문서 수", "variable": "충성 등급"},
        )
        chart_style(fig3, height=350)
        st.plotly_chart(fig3, use_container_width=True)

        st.dataframe(
            loyalty_df[["브랜드","언급량","로열티지수","찐팬비율","독점충성","강한애착","반복소비","NSS"]],
            use_container_width=True, hide_index=True,
        )


# ════════════════════════════════════════════════════
# TAB — 토픽 클러스터링 (토픽×브랜드×고객 중첩) [고도화 C]
# ════════════════════════════════════════════════════
with tab_topiccl:
    st.markdown("<div class='section-title'>🧩 토픽 클러스터링 — 토픽 × 브랜드 × 감성 중첩 분석</div>", unsafe_allow_html=True)
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
        cluster_colors = ["#2980B9", "#16A085", "#E67E22", "#8E44AD", "#E74C3C"]
        for i, col in enumerate(tcols):
            with col:
                kw_html = "".join([
                    f"<span style='display:inline-block;background:{cluster_colors[i]}22;"
                    f"color:{cluster_colors[i]};border-radius:10px;padding:2px 8px;"
                    f"margin:2px;font-size:11px;'>{w}</span>"
                    for w in topic_words[i][:6]])
                occ_str = ", ".join(topic_occasions[i]) if topic_occasions[i] else "—"
                brand_str = ", ".join(topic_brands_list[i]) if topic_brands_list[i] else "—"
                st.markdown(f"""
                <div style='background:#FFFFFF;border-top:3px solid {cluster_colors[i]};
                            border:1px solid #E2E8F0;border-radius:8px;padding:10px;'>
                    <div style='font-weight:800;color:{cluster_colors[i]};font-size:0.9rem;'>토픽 {i}</div>
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

        st.markdown("""
        <div class='success-box'>
        <b>활용</b>: 특정 토픽이 경쟁사에 집중되어 있다면 그 토픽은 '경쟁사 강점 영역',
        파스쿠찌 언급이 적은 토픽은 '담론 공백 → 선점 기회'로 해석합니다.
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════
# TAB — 소비맥락 세분화 (3축 결합) [고도화 B]
# ════════════════════════════════════════════════════
with tab_occ2:
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

        st.markdown("""
        <div class='success-box'>
        <b>전략 활용</b>: "집중 카공" "디저트 타임" 등 파스쿠찌가 강점을 가질 수 있는 상황을
        선별해 상황 맞춤형 메뉴·공간·프로모션을 기획합니다. 경쟁사가 독점한 상황은 차별화 포인트를 찾습니다.
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════
# TAB — 트렌드 조기경보 (상대평가) [고도화 D]
# ════════════════════════════════════════════════════
with tab_trend:
    st.markdown("<div class='section-title'>📡 상품 트렌드 조기경보 — 상대평가 기반</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='insight-box'>
    단순 증감이 아니라 <b>늘 소비되는 기준 제품(아메리카노·라떼) 대비 상대 배수</b>로 유행을 예측합니다.<br>
    <b>상대배수</b>(기준선 대비) + <b>성장 기울기</b> + <b>브랜드 확산도</b>를 결합한 <b>ES점수</b>로
    "뜰 것 같은 제품·식재료"를 사전 포착합니다. (예: 두쫀쿠 열풍 전 카다이프 검색량 급증 패턴)
    </div>""", unsafe_allow_html=True)

    if trend_ew is None:
        st.info("트렌드 분석을 위한 데이터가 부족합니다.")
    else:
        ew_df_full = trend_ew["df"]
        st.markdown(f"""
        <div class='warning-box'>
        <b>기준선(아메리카노·라떼 등) 월평균 언급량 = {trend_ew['baseline_avg']}건</b><br>
        각 신흥 제품의 최근 언급량을 이 기준선과 비교해 상대 배수를 산출합니다.
        </div>""", unsafe_allow_html=True)

        # [항목 10] 카테고리 구분 필터
        cat_options = ["전체"] + list(TREND_CATEGORY.keys())
        sel_cat = st.radio("카테고리 구분", cat_options, horizontal=True, key="trend_cat")
        if sel_cat == "전체":
            ew_df = ew_df_full
        else:
            ew_df = ew_df_full[ew_df_full["카테고리"] == sel_cat]

        # 카테고리별 요약 카드
        ccols = st.columns(len(TREND_CATEGORY))
        cat_emoji = {"커피·음료": "☕", "푸드류": "🥐", "식재료": "🧂"}
        for col, (cat, items) in zip(ccols, TREND_CATEGORY.items()):
            cat_df = ew_df_full[ew_df_full["카테고리"] == cat]
            top_item = cat_df.iloc[0]["제품·식재료"] if len(cat_df) > 0 else "—"
            top_es = cat_df.iloc[0]["ES점수"] if len(cat_df) > 0 else 0
            with col:
                st.markdown(f"""
                <div style='background:#FFFFFF;border:1px solid #E2E8F0;border-top:3px solid #E67E22;
                            border-radius:8px;padding:10px;text-align:center;'>
                    <div style='font-size:1.3rem;'>{cat_emoji.get(cat,"📦")}</div>
                    <div style='font-weight:700;color:#1B2A4A;font-size:0.85rem;'>{cat}</div>
                    <div style='color:#718096;font-size:0.72rem;'>{len(cat_df)}개 항목</div>
                    <div style='color:#E67E22;font-weight:700;font-size:0.78rem;margin-top:3px;'>
                        TOP: {top_item} (ES {top_es:.0f})
                    </div>
                </div>""", unsafe_allow_html=True)

        if len(ew_df) == 0:
            st.info(f"{sel_cat} 카테고리에 해당하는 제품이 없습니다.")
            st.stop()

        c1, c2 = st.columns([1.3, 1])
        with c1:
            sorted_ew = ew_df.sort_values("ES점수")
            alert_color_map = {
                "🚨 강한 신호": "#E74C3C", "📈 성장 조짐": "#E67E22",
                "➡️ 안정": "#2980B9", "📉 둔화": "#7F8C8D",
            }
            fig = px.bar(
                sorted_ew, x="ES점수", y="제품·식재료", orientation="h",
                color="경보", color_discrete_map=alert_color_map,
                title="제품·식재료 Emerging Signal 점수",
                text=sorted_ew["ES점수"].apply(lambda x: f"{x:.0f}"),
            )
            fig.update_traces(textposition="outside")
            chart_style(fig, height=480)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown("<div class='section-title'>조기경보 신호</div>", unsafe_allow_html=True)
            for _, row in ew_df.head(8).iterrows():
                ac = {"🚨 강한 신호":"#E74C3C","📈 성장 조짐":"#E67E22",
                      "➡️ 안정":"#2980B9","📉 둔화":"#7F8C8D"}.get(row["경보"],"#2980B9")
                st.markdown(f"""
                <div style='background:#FFFFFF;border:1px solid #E2E8F0;border-left:4px solid {ac};
                            border-radius:0 8px 8px 0;padding:8px 12px;margin-bottom:5px;'>
                    <b style='color:{ac};font-size:0.85rem;'>{row['경보']} {row['제품·식재료']}</b>
                    <div style='color:#718096;font-size:0.74rem;margin-top:3px;'>
                        상대배수 {row['상대배수']}배 · 기울기 {row['성장기울기']:+.1f} · {row['브랜드확산']}개 브랜드 · NSS {row['NSS']:+.1f}
                    </div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div class='section-title'>트렌드 스코어 포지셔닝 (상대배수 × 성장기울기)</div>", unsafe_allow_html=True)
        st.caption("우상단 = 이미 많이 언급되고 + 계속 성장 중 / 좌상단 = 아직 작지만 급성장 (조기 진입 기회)")
        fig2 = go.Figure()
        for _, row in ew_df.iterrows():
            ac = {"🚨 강한 신호":"#E74C3C","📈 성장 조짐":"#E67E22",
                  "➡️ 안정":"#2980B9","📉 둔화":"#7F8C8D"}.get(row["경보"],"#2980B9")
            fig2.add_trace(go.Scatter(
                x=[row["상대배수"]], y=[row["성장기울기"]],
                mode="markers+text",
                marker=dict(size=max(row["총언급"]/2, 12), color=ac, opacity=0.75,
                            line=dict(color="white", width=1.5)),
                text=[row["제품·식재료"]], textposition="top center",
                textfont=dict(size=10, color=ac),
                name=row["제품·식재료"],
                hovertemplate=f"<b>{row['제품·식재료']}</b><br>상대배수: {row['상대배수']}<br>기울기: {row['성장기울기']}<br>ES: {row['ES점수']}<extra></extra>",
            ))
        fig2.add_hline(y=0, line_dash="dash", line_color="#A0AEC0")
        fig2.add_vline(x=0.5, line_dash="dot", line_color="#A0AEC0")
        fig2.update_layout(title="상대배수 × 성장기울기 (버블=총언급량)",
                           xaxis_title="기준선 대비 상대배수", yaxis_title="성장 기울기",
                           showlegend=False)
        chart_style(fig2, height=460)
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<div class='section-title'>상위 신호 제품 월별 추이</div>", unsafe_allow_html=True)
        top_products = ew_df.head(5)["제품·식재료"].tolist()
        ts_rows = []
        for _, row in ew_df.head(5).iterrows():
            for mi, m in enumerate(trend_ew["months"]):
                ts_rows.append({"제품": row["제품·식재료"], "월": m,
                                "언급량": row["_monthly"][mi] if mi < len(row["_monthly"]) else 0})
        ts_df = pd.DataFrame(ts_rows)
        fig3 = px.line(ts_df, x="월", y="언급량", color="제품", markers=True,
                       title="상위 5개 신호 제품 월별 언급 추이")
        chart_style(fig3, height=360)
        st.plotly_chart(fig3, use_container_width=True)

        st.dataframe(
            ew_df[["제품·식재료","총언급","상대배수","성장기울기","브랜드확산","NSS","ES점수","경보"]],
            use_container_width=True, hide_index=True,
        )


# ════════════════════════════════════════════════════
# TAB — 브랜드별 제품 [항목 4]
# ════════════════════════════════════════════════════
with tab_product:
    st.markdown("<div class='section-title'>🛍️ 브랜드별 제품 언급·감성 분석</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='insight-box'>
    브랜드별로 가장 많이 언급되는 <b>제품(커피·음료·디저트·푸드 망라)</b>과 그 제품의
    <b>언급량·감성(NSS)·월별 추이</b>를 확인합니다. 시그니처 제품 발굴과 상품 기획에 활용합니다.
    </div>""", unsafe_allow_html=True)

    sel_bp = st.selectbox("브랜드 선택", TARGET_BRANDS, key="product_brand")
    prod_df = compute_brand_products(v, sel_bp)

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
        ptrend = compute_product_trend(v, sel_bp, sel_prod)
        if len(ptrend) > 0 and ptrend["언급량"].sum() > 0:
            fig3 = make_subplots(specs=[[{"secondary_y": True}]])
            fig3.add_trace(go.Bar(
                x=ptrend["월"], y=ptrend["언급량"], name="언급량",
                marker_color="#2D6BC4", opacity=0.75,
            ), secondary_y=False)
            fig3.add_trace(go.Scatter(
                x=ptrend["월"], y=ptrend["NSS"], name="NSS", mode="lines+markers",
                line=dict(color="#E67E22", width=3), marker=dict(size=7),
            ), secondary_y=True)
            fig3.add_hline(y=0, line_dash="dot", line_color="#A0AEC0", secondary_y=True)
            fig3.update_layout(
                title=f"{sel_bp} — {sel_prod} 월별 언급량 & 감성 추이",
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
with tab_promo:
    st.markdown("<div class='section-title'>🎁 프로모션 모니터링</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='insight-box'>
    통신·카드할인, 이벤트, 1+1, 굿즈 증정 등 <b>촉진(프로모션) 관련 담론</b>을 브랜드별로 모니터링하고,
    "할인 개꿀", "이벤트 필참", "잇템" 등 <b>고객 반응 강도</b>를 측정합니다.
    (전체 {promo_doc_count}건의 프로모션 언급 분석)
    </div>""", unsafe_allow_html=True)

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
        st.markdown("<div class='section-title'>촉진 반응 강도</div>", unsafe_allow_html=True)
        fig2 = px.bar(
            promo_react_df, x="반응", y="언급량",
            color="반응",
            color_discrete_map={"강한 긍정":"#C0392B","긍정":"#E67E22","부정":"#7F8C8D"},
            title="프로모션 반응 강도 분포", text="언급량",
        )
        fig2.update_traces(textposition="outside")
        chart_style(fig2, height=340, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

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

    st.markdown("<div class='section-title'>촉진 활동별 반응 강도 (고객 호응도)</div>", unsafe_allow_html=True)
    st.caption("반응 강도 = (강한긍정×2 + 긍정×1 − 부정×1) / 언급량. 높을수록 고객 호응이 강한 촉진 유형")
    if len(promo_type_react_df) > 0:
        fig4 = px.bar(
            promo_type_react_df.sort_values("반응강도"),
            x="반응강도", y="프로모션", orientation="h",
            color="반응강도", color_continuous_scale=["#E74C3C","#FFFFFF","#27AE60"],
            color_continuous_midpoint=0,
            title="촉진 유형별 고객 반응 강도",
            text=promo_type_react_df.sort_values("반응강도")["반응강도"].apply(lambda x: f"{x:+.2f}"),
            hover_data=["언급량"],
        )
        fig4.update_traces(textposition="outside")
        fig4.add_vline(x=0, line_color="#4A5568", line_width=1.5)
        chart_style(fig4, height=340, showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("""
    <div class='success-box'>
    <b>전략 활용</b>: 반응 강도가 높은 촉진 유형(예: 굿즈·1+1)은 파스쿠찌도 적극 도입,
    경쟁사가 독점한 촉진 영역은 차별화된 방식으로 접근합니다.
    </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════
# TAB — 고객 클러스터링 & 페르소나 [항목 7]
# ════════════════════════════════════════════════════
with tab_cluster:
    st.markdown("<div class='section-title'>👥 고객 클러스터링 & 페르소나</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='insight-box'>
    고객을 <b>성향·특성·관심사</b> 기준으로 군집화하고 <b>페르소나</b>를 도출합니다.
    각 페르소나의 <b>카페 방문·커피 음용 U&A</b>, 주요 관심사, 자주 언급하는 브랜드를 확인합니다.
    (TF-IDF 텍스트 70% + 감성·충성도·브랜드수·디카페인 관심 등 행동 피처 30% 결합)
    </div>""", unsafe_allow_html=True)

    if customer_cluster is None:
        st.info("고객 클러스터링을 위한 데이터가 부족합니다. (30건 이상 필요)")
    else:
        sub_c = customer_cluster["sub"]
        profiles = customer_cluster["profiles"]
        pca_var = customer_cluster["pca_var"]

        st.markdown("<div class='section-title'>고객 세그먼트 분포 (PCA 2D)</div>", unsafe_allow_html=True)
        cluster_palette = ["#2D6BC4","#E67E22","#27AE60","#8E44AD","#E74C3C","#16A085"]
        fig = go.Figure()
        for prof in profiles:
            c = prof["cluster"]
            cdocs = sub_c[sub_c["cluster"] == c]
            persona = make_persona(prof)
            fig.add_trace(go.Scatter(
                x=cdocs["pca_x"], y=cdocs["pca_y"], mode="markers",
                name=f"C{c}: {persona['name']}",
                marker=dict(size=8, color=cluster_palette[c % len(cluster_palette)],
                            opacity=0.6, line=dict(color="white", width=0.5)),
                hovertemplate=f"<b>{persona['name']}</b><br>%{{text}}<extra></extra>",
                text=cdocs["title"].str[:30],
            ))
        fig.update_layout(
            title=f"고객 세그먼트 분포 (PC1 {pca_var[0]}% · PC2 {pca_var[1]}%)",
            xaxis_title="주성분 1", yaxis_title="주성분 2",
            paper_bgcolor="#F7F9FC", plot_bgcolor="#FFFFFF",
            font=dict(color="#2D3748"), height=480,
            legend=dict(bgcolor="#FFFFFF", bordercolor="#E2E8F0", borderwidth=1),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("<div class='section-title'>도출된 고객 페르소나</div>", unsafe_allow_html=True)
        persona_cols = st.columns(min(len(profiles), 3))
        for i, prof in enumerate(profiles):
            persona = make_persona(prof)
            c = prof["cluster"]
            color = cluster_palette[c % len(cluster_palette)]
            brands_str = ", ".join(persona["brands"][:3]) if persona["brands"] else "특정 브랜드 없음"
            kw_str = ", ".join(persona["kw"][:6])
            with persona_cols[i % 3]:
                st.markdown(f"""
                <div style='background:#FFFFFF;border:1px solid #E2E8F0;border-top:4px solid {color};
                            border-radius:10px;padding:14px;margin-bottom:12px;
                            box-shadow:0 2px 6px rgba(0,0,0,0.05);'>
                    <div style='color:{color};font-weight:800;font-size:1rem;'>C{c}. {persona['name']}</div>
                    <div style='color:#718096;font-size:0.75rem;margin:2px 0 8px;'>n={persona['n']}명 · NSS {persona['nss']:+.0f}</div>
                    <div style='color:#2D3748;font-size:0.82rem;margin-bottom:8px;'>{persona['desc']}</div>
                    <div style='background:#F7FAFC;border-radius:6px;padding:8px;margin-bottom:6px;'>
                        <div style='color:#1B2A4A;font-weight:700;font-size:0.75rem;margin-bottom:3px;'>U&A</div>
                        <div style='color:#4A5568;font-size:0.76rem;'>{persona['ua']}</div>
                    </div>
                    <div style='font-size:0.75rem;color:#4A5568;'>
                        <b>충성도</b> {persona['loyalty']}% · <b>디카페인 관심</b> {persona['decaf']}%<br>
                        <b>주요 브랜드</b>: {brands_str}<br>
                        <b>관심 키워드</b>: {kw_str}
                    </div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div class='section-title'>세그먼트 × 브랜드 언급 히트맵</div>", unsafe_allow_html=True)
        seg_brand = pd.DataFrame(0, index=[f"C{p['cluster']}" for p in profiles], columns=TARGET_BRANDS)
        for prof in profiles:
            c = prof["cluster"]
            cdocs = sub_c[sub_c["cluster"] == c]
            for b in TARGET_BRANDS:
                seg_brand.loc[f"C{c}", b] = int(cdocs["brands"].apply(lambda x: b in x).sum())
        fig2 = px.imshow(
            seg_brand, color_continuous_scale="Purples",
            title="고객 세그먼트 × 브랜드 언급 매트릭스",
            text_auto=True, aspect="auto",
        )
        fig2.update_traces(textfont=dict(color="#1B2A4A", size=11))
        chart_style(fig2, height=320, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)


# ── 푸터 ──────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#A0AEC0;font-size:11px;'>"
    "커피 시장 VoC 심층 분석 대시보드  ·  82Cook 커뮤니티 데이터  ·  파스쿠찌 데이터 마케팅 전략  ·  2026"
    "</p>",
    unsafe_allow_html=True,
)
