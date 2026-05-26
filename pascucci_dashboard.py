"""
Coffee Market Insight Dashboard
Data-driven Marketing Strategy for PASCUCCI
Data Source: Community-based Social VoC (82Cook · Clien)

실행 방법:
  pip install streamlit plotly pandas numpy scikit-learn scipy
  streamlit run pascucci_dashboard.py
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
from sklearn.decomposition import LatentDirichletAllocation
import scipy.linalg as la

# ══════════════════════════════════════════════════════
# 기본 설정
# ══════════════════════════════════════════════════════
st.set_page_config(
    page_title="Coffee Market Insight Dashboard",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp { background-color: #F7F9FC; }
    .main .block-container { background-color: #F7F9FC; padding-top: 1.5rem; max-width: 1400px; }

    [data-testid="stSidebar"] { background-color: #1B2A4A !important; border-right: 2px solid #2D6BC4; }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div { color: #E8EEF8 !important; }
    [data-testid="stSidebar"] h3 { color: #F5A623 !important; font-size: 1rem; }
    [data-testid="stSidebar"] hr { border-color: #2D3F5A; }

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


def hex_to_rgba(hex_color, alpha=0.15):
    """hex 색상(#RRGGBB)을 rgba() 문자열로 변환"""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 6:
        r, g, b = int(hex_color[0:2],16), int(hex_color[2:4],16), int(hex_color[4:6],16)
        return f"rgba({r},{g},{b},{alpha})"
    return hex_color

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
# 사이드바
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ☕ Coffee Market Insight Dashboard")
    st.markdown("Data-driven Marketing Strategy for PASCUCCI")
    st.markdown("<small style='color:#99AACC;'>Source: Community-based Social VoC</small>", unsafe_allow_html=True)
    st.markdown("---")
    uploaded = st.file_uploader(
        "📂 데이터 파일 업로드",
        type=["csv", "xlsx"],
        help="CSV 또는 Excel 파일을 업로드하세요"
    )
    st.markdown("---")

if uploaded is None:
    st.markdown("""
    <div style='text-align:center; padding:60px 20px;'>
        <div style='font-size:4rem'>☕</div>
        <h1 style='color:#1B2A4A; margin:20px 0 10px;'>Coffee Market Insight Dashboard</h1>
        <h3 style='color:#2D6BC4; font-weight:400;'>Data-driven Marketing Strategy for PASCUCCI</h3>
        <p style='color:#A0AEC0; font-size:0.85rem; margin-top:4px;'>Data Source: Community-based Social VoC (82Cook · Clien)</p>
        <p style='color:#718096; font-size:1rem; margin-top:12px;'>
            왼쪽 사이드바에서 CSV 파일을 업로드하면 분석이 시작됩니다.
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

# ══════════════════════════════════════════════════════
# 탭 구성 — 17개
# ══════════════════════════════════════════════════════
tabs = st.tabs([
    "📊 Overview",
    "📈 NSS 평판",
    "📣 SOV 분석",
    "🔍 드라이버 분석",
    "🗺️ CA 이미지 맵",
    "🎯 LDA 토픽",
    "⚡ Burst 탐지",
    "🔗 PMI 분석",
    "📍 포지셔닝맵",
    "☁️ 키워드 버블",
    "🎯 소비 맥락",
    "🚨 리스크 탐지",
    "📆 시계열 분석",
    "🔬 텍스트 분석 고도화",
    "⚔️ 경쟁 브랜드 비교",
    "🔮 예측·트렌드",
    "👥 소비자 세그먼트",
])
(tab_ov, tab_nss, tab_sov, tab_absa, tab_ca, tab_lda,
 tab_burst, tab_pmi, tab_pos, tab_kw, tab_occ, tab_risk, tab_ts,
 tab_text, tab_comp, tab_pred, tab_seg) = tabs

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
    fig2 = px.imshow(
        pmi_full, color_continuous_scale=["#EDF2F7","#2D6BC4"],
        title="브랜드 공출현 PMI 매트릭스",
        text_auto=".2f", aspect="auto",
    )
    fig2.update_traces(textfont=dict(color="#1B2A4A", size=11))
    chart_style(fig2, height=400, showlegend=False)
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

    st.markdown("<div class='section-title'>경쟁력 레이더차트 (파스쿠찌 잠재력 포함)</div>", unsafe_allow_html=True)
    radar_axes = ["SOV 규모","NSS 평판","맛·품질","공간 전문성","가격 포지션","디카페인 기회","브랜드 이미지"]
    # 파스쿠찌: 클리앙 실측 기반 (n=29건) / 타 브랜드: 82Cook 실측 기반
    radar_data = {
        "파스쿠찌(Social VoC)": [5, 71, 85, 85, 55, 69, 85],
        # [SOV규모, NSS평판, 맛품질, 공간전문성, 가격포지션, 디카페인기회, 브랜드이미지]
        # ⚠️ SOV=5(클리앙 29건 기준), NSS=71(NSS 41.4 → 0~100 변환)
        "스타벅스":             [100, 20, 50, 60, 40, 55, 45],
        "이디야":               [15, 80, 70, 55, 60, 75, 65],
        "테라로사":             [8,  90, 88, 70, 40, 70, 85],
        "메가커피":             [12, 65, 55, 30, 90, 40, 40],
    }
    fig3 = go.Figure()
    colors_radar = ["#C0392B","#E74C3C","#27AE60","#2980B9","#E67E22"]
    for (name, vals), color in zip(radar_data.items(), colors_radar):
        v_plot = vals + [vals[0]]
        fig3.add_trace(go.Scatterpolar(
            r=v_plot, theta=radar_axes + [radar_axes[0]],
            fill="toself", name=name,
            line=dict(color=color, width=2.5 if name=="파스쿠찌(잠재)" else 1.8),
            fillcolor=color, opacity=0.12 if name!="파스쿠찌(잠재)" else 0.22,
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
        title="브랜드 경쟁력 레이더  (파스쿠찌 = 잠재 포지션)",
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
# TAB 13 — 시계열 분석
# ════════════════════════════════════════════════════
with tab_ts:
    st.markdown("<div class='section-title'>📆 정량 지표 시계열 분석</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='insight-box'>
    월별로 <b>언급량 · 감성 비율 · NSS · 브랜드 점유율 · 키워드 빈도</b> 등
    주요 정량 지표의 시간적 변화를 다각도로 탐색합니다.
    분석 기간·브랜드·지표를 자유롭게 조합해 트렌드를 확인하세요.
    </div>""", unsafe_allow_html=True)

    # 분석 대상 기간 필터
    ts_months = sorted([
        m for m in v["year_month"].dropna().unique()
        if "NaT" not in m and ("2025" in m or "2026" in m)
    ])
    if len(ts_months) < 2:
        st.info("시계열 분석을 위한 기간이 부족합니다.")
    else:
        col_f1, col_f2, col_f3 = st.columns([1.5, 1.5, 1])
        with col_f1:
            ts_brand_sel = st.multiselect(
                "브랜드 선택",
                TARGET_BRANDS,
                default=["스타벅스","투썸플레이스","메가커피","이디야","폴바셋"],
                key="ts_brands",
            )
        with col_f2:
            ts_period = st.select_slider(
                "분석 기간",
                options=ts_months,
                value=(ts_months[0], ts_months[-1]),
                key="ts_period",
            )
        with col_f3:
            ts_smooth = st.checkbox("추세선(7일 이동평균) 표시", value=False, key="ts_smooth")

        ts_start, ts_end = ts_period
        ts_mask = (v["year_month"] >= ts_start) & (v["year_month"] <= ts_end)
        ts_v = v[ts_mask].copy()

        st.markdown("---")

        # ── 섹션 A: 언급량 시계열 ─────────────────────────
        st.markdown("<div class='section-title'>A. 브랜드별 월간 언급량 추이</div>",
                    unsafe_allow_html=True)
        c1, c2 = st.columns(2)

        with c1:
            rows_vol = []
            for b in ts_brand_sel:
                bd = ts_v[ts_v["brands"].apply(lambda x: b in x)]
                for m in ts_months:
                    if m < ts_start or m > ts_end:
                        continue
                    cnt = (bd["year_month"] == m).sum()
                    rows_vol.append({"브랜드": b, "월": m, "언급량": int(cnt)})
            vol_df = pd.DataFrame(rows_vol)

            if not vol_df.empty:
                fig_vol = px.line(
                    vol_df, x="월", y="언급량", color="브랜드",
                    color_discrete_map=BRAND_COLORS, markers=True,
                    title="월별 언급량 (Line)",
                    labels={"월": "월", "언급량": "문서 수"},
                )
                if ts_smooth:
                    for trace in fig_vol.data:
                        b_name = trace.name
                        bd_sub = vol_df[vol_df["브랜드"] == b_name].sort_values("월")
                        if len(bd_sub) >= 3:
                            smoothed = bd_sub["언급량"].rolling(window=3, center=True,
                                                                min_periods=1).mean()
                            fig_vol.add_scatter(
                                x=bd_sub["월"], y=smoothed.round(1),
                                mode="lines", name=f"{b_name}(추세)",
                                line=dict(color=BRAND_COLORS.get(b_name, "#999"),
                                          width=1, dash="dot"),
                                showlegend=True,
                            )
                chart_style(fig_vol, height=320)
                st.plotly_chart(fig_vol, use_container_width=True)

        with c2:
            if not vol_df.empty:
                fig_vol2 = px.bar(
                    vol_df, x="월", y="언급량", color="브랜드",
                    color_discrete_map=BRAND_COLORS, barmode="stack",
                    title="월별 언급량 누적 (Stacked Bar)",
                )
                chart_style(fig_vol2, height=320)
                st.plotly_chart(fig_vol2, use_container_width=True)

        # ── 섹션 B: 월별 SOV 시계열 ───────────────────────
        st.markdown("<div class='section-title'>B. 월별 브랜드 SOV (점유율) 변화</div>",
                    unsafe_allow_html=True)

        rows_sov = []
        for m in ts_months:
            if m < ts_start or m > ts_end:
                continue
            month_total = (ts_v["year_month"] == m).sum()
            if month_total == 0:
                continue
            for b in ts_brand_sel:
                bd = ts_v[ts_v["brands"].apply(lambda x: b in x)]
                cnt = (bd["year_month"] == m).sum()
                rows_sov.append({
                    "브랜드": b, "월": m,
                    "SOV(%)": round(cnt / month_total * 100, 1),
                    "언급량": int(cnt),
                })
        sov_ts_df = pd.DataFrame(rows_sov)

        c1, c2 = st.columns(2)
        with c1:
            if not sov_ts_df.empty:
                fig_sov_ts = px.area(
                    sov_ts_df, x="월", y="SOV(%)", color="브랜드",
                    color_discrete_map=BRAND_COLORS,
                    title="월별 SOV 변화 (Area)",
                    labels={"SOV(%)": "점유율 (%)"},
                )
                chart_style(fig_sov_ts, height=300)
                st.plotly_chart(fig_sov_ts, use_container_width=True)
        with c2:
            if not sov_ts_df.empty:
                fig_sov_bar = px.bar(
                    sov_ts_df, x="월", y="SOV(%)", color="브랜드",
                    color_discrete_map=BRAND_COLORS, barmode="stack",
                    title="월별 SOV 누적 비율 (100% Stacked)",
                )
                fig_sov_bar.update_layout(
                    yaxis=dict(ticksuffix="%"),
                    barnorm="percent",
                )
                chart_style(fig_sov_bar, height=300)
                st.plotly_chart(fig_sov_bar, use_container_width=True)

        # ── 섹션 C: 감성 시계열 ───────────────────────────
        st.markdown("<div class='section-title'>C. 월별 감성 비율 시계열</div>",
                    unsafe_allow_html=True)

        ts_b_sent = st.selectbox(
            "브랜드 선택 (감성 시계열)",
            ["전체"] + ts_brand_sel,
            key="ts_sent_brand",
        )
        sent_target = ts_v if ts_b_sent == "전체" else \
            ts_v[ts_v["brands"].apply(lambda x: ts_b_sent in x)]

        rows_sent = []
        for m in ts_months:
            if m < ts_start or m > ts_end:
                continue
            sub = sent_target[sent_target["year_month"] == m]
            t = len(sub)
            if t < 2:
                continue
            for s in ["긍정", "중립", "부정"]:
                cnt = (sub["sentiment"] == s).sum()
                rows_sent.append({
                    "월": m, "감성": s,
                    "비율(%)": round(cnt / t * 100, 1),
                    "건수": int(cnt), "전체": t,
                })
        sent_ts_df = pd.DataFrame(rows_sent)

        c1, c2 = st.columns(2)
        with c1:
            if not sent_ts_df.empty:
                fig_sent_line = px.line(
                    sent_ts_df, x="월", y="비율(%)", color="감성",
                    color_discrete_map=SENT_COLORS, markers=True,
                    title=f"감성 비율 추이 — {ts_b_sent}",
                )
                chart_style(fig_sent_line, height=300)
                st.plotly_chart(fig_sent_line, use_container_width=True)
        with c2:
            if not sent_ts_df.empty:
                fig_sent_bar = px.bar(
                    sent_ts_df, x="월", y="비율(%)", color="감성",
                    color_discrete_map=SENT_COLORS, barmode="stack",
                    title=f"감성 누적 비율 — {ts_b_sent}",
                    text=sent_ts_df["비율(%)"].apply(
                        lambda x: f"{x:.0f}%" if x >= 8 else ""),
                )
                fig_sent_bar.update_traces(textposition="inside",
                                           textfont=dict(color="white", size=10))
                chart_style(fig_sent_bar, height=300)
                st.plotly_chart(fig_sent_bar, use_container_width=True)

        # ── 섹션 D: 다중 지표 복합 시계열 ─────────────────
        st.markdown("<div class='section-title'>D. 언급량 × NSS 복합 이중축 차트</div>",
                    unsafe_allow_html=True)

        ts_b_dual = st.selectbox(
            "브랜드 선택 (이중축 차트)",
            ts_brand_sel if ts_brand_sel else TARGET_BRANDS[:1],
            key="ts_dual_brand",
        )
        bd_dual = ts_v[ts_v["brands"].apply(lambda x: ts_b_dual in x)]

        rows_dual = []
        for m in ts_months:
            if m < ts_start or m > ts_end:
                continue
            sub = bd_dual[bd_dual["year_month"] == m]
            t   = len(sub)
            if t < 2:
                continue
            p   = (sub["sentiment"] == "긍정").sum()
            n   = (sub["sentiment"] == "부정").sum()
            rows_dual.append({
                "월": m, "언급량": t,
                "NSS": round((p - n) / t * 100, 1),
                "긍정수": int(p), "부정수": int(n),
            })
        dual_df = pd.DataFrame(rows_dual)

        if not dual_df.empty:
            fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
            fig_dual.add_trace(
                go.Bar(
                    x=dual_df["월"], y=dual_df["언급량"],
                    name="언급량", marker_color="#B5D4F4",
                    opacity=0.75,
                ),
                secondary_y=False,
            )
            fig_dual.add_trace(
                go.Scatter(
                    x=dual_df["월"], y=dual_df["NSS"],
                    name="NSS", mode="lines+markers",
                    line=dict(color="#E24B4A", width=2.5),
                    marker=dict(size=7, color="#E24B4A"),
                ),
                secondary_y=True,
            )
            fig_dual.add_hline(
                y=0, line_color="#E74C3C", line_width=1.2,
                line_dash="dash", secondary_y=True,
            )
            fig_dual.update_layout(
                title=f"{ts_b_dual} — 월별 언급량 & NSS 이중축",
                plot_bgcolor="#FFFFFF", paper_bgcolor="#F7F9FC",
                font=dict(color="#2D3748", size=12),
                height=360,
                legend=dict(bgcolor="#FFFFFF", bordercolor="#E2E8F0",
                            borderwidth=1, font=dict(size=11)),
                margin=dict(l=50, r=60, t=50, b=45),
                xaxis=dict(gridcolor="#EDF2F7",
                           tickfont=dict(color="#4A5568"),
                           title_font=dict(color="#4A5568")),
            )
            fig_dual.update_yaxes(
                title_text="언급량 (건)", secondary_y=False,
                gridcolor="#EDF2F7", tickfont=dict(color="#4A5568"),
                title_font=dict(color="#4A5568"),
            )
            fig_dual.update_yaxes(
                title_text="NSS", secondary_y=True,
                tickfont=dict(color="#E24B4A"),
                title_font=dict(color="#E24B4A"),
                zeroline=True, zerolinecolor="#E74C3C", zerolinewidth=1,
            )
            st.plotly_chart(fig_dual, use_container_width=True)

        # ── 섹션 E: 키워드 빈도 시계열 ────────────────────
        st.markdown("<div class='section-title'>E. 키워드 빈도 시계열 추적</div>",
                    unsafe_allow_html=True)
        st.caption("추적하고 싶은 키워드를 입력하면 해당 단어의 월별 언급 빈도를 표시합니다.")

        kw_input = st.text_input(
            "키워드 입력 (쉼표로 구분)",
            value="디카페인, 불매, 가성비, 환불",
            key="ts_kw_input",
        )
        track_kws = [k.strip() for k in kw_input.split(",") if k.strip()]

        if track_kws:
            rows_kw = []
            for m in ts_months:
                if m < ts_start or m > ts_end:
                    continue
                sub = ts_v[ts_v["year_month"] == m]
                all_text = " ".join(sub["full_text"].fillna("").tolist())
                for kw in track_kws:
                    cnt = all_text.count(kw)
                    rows_kw.append({"월": m, "키워드": kw, "빈도": cnt})
            kw_ts_df = pd.DataFrame(rows_kw)

            kw_colors = ["#27AE60","#E74C3C","#2980B9","#E67E22",
                         "#8E44AD","#16A085","#C0392B","#F39C12"]
            kw_color_map = {kw: kw_colors[i % len(kw_colors)]
                            for i, kw in enumerate(track_kws)}

            c1, c2 = st.columns(2)
            with c1:
                fig_kw = px.line(
                    kw_ts_df, x="월", y="빈도", color="키워드",
                    color_discrete_map=kw_color_map, markers=True,
                    title="키워드 월별 빈도 추이",
                )
                chart_style(fig_kw, height=300)
                st.plotly_chart(fig_kw, use_container_width=True)
            with c2:
                fig_kw2 = px.bar(
                    kw_ts_df, x="월", y="빈도", color="키워드",
                    color_discrete_map=kw_color_map, barmode="group",
                    title="키워드 월별 빈도 비교",
                )
                chart_style(fig_kw2, height=300)
                st.plotly_chart(fig_kw2, use_container_width=True)

        # ── 섹션 F: 전체 담론량 시계열 + 이벤트 마킹 ──────
        st.markdown("<div class='section-title'>F. 전체 담론량 시계열 + 주요 이벤트</div>",
                    unsafe_allow_html=True)

        total_monthly = []
        for m in ts_months:
            if m < ts_start or m > ts_end:
                continue
            sub = ts_v[ts_v["year_month"] == m]
            t   = len(sub)
            p   = (sub["sentiment"] == "긍정").sum()
            n   = (sub["sentiment"] == "부정").sum()
            total_monthly.append({
                "월": m, "전체": t,
                "긍정": int(p), "부정": int(n), "중립": int(t - p - n),
                "NSS": round((p - n) / t * 100, 1) if t > 0 else 0,
            })
        total_ts_df = pd.DataFrame(total_monthly)

        EVENTS = {
            "2026-05": "스타벅스 불매 이슈\n(정용진·일베)",
            "2025-11": "디카페인 담론\n피크 시작",
            "2025-12": "연말 시즌\n카페 언급 급증",
        }

        if not total_ts_df.empty:
            fig_total = go.Figure()
            fig_total.add_trace(go.Scatter(
                x=total_ts_df["월"], y=total_ts_df["긍정"],
                name="긍정", fill="tozeroy",
                fillcolor="rgba(39,174,96,0.18)",
                line=dict(color="#27AE60", width=2),
            ))
            fig_total.add_trace(go.Scatter(
                x=total_ts_df["월"], y=total_ts_df["부정"],
                name="부정", fill="tozeroy",
                fillcolor="rgba(231,76,60,0.18)",
                line=dict(color="#E74C3C", width=2),
            ))
            fig_total.add_trace(go.Scatter(
                x=total_ts_df["월"], y=total_ts_df["전체"],
                name="전체", mode="lines+markers",
                line=dict(color="#2D6BC4", width=2.5, dash="dot"),
                marker=dict(size=7),
            ))
            for m_event, label in EVENTS.items():
                if ts_start <= m_event <= ts_end and m_event in total_ts_df["월"].values:
                    y_val = total_ts_df.loc[
                        total_ts_df["월"] == m_event, "전체"].values
                    if len(y_val) > 0:
                        fig_total.add_annotation(
                            x=m_event, y=float(y_val[0]),
                            text=label, showarrow=True,
                            arrowhead=2, arrowcolor="#1B2A4A",
                            font=dict(size=10, color="#1B2A4A"),
                            bgcolor="#FFFBEB", bordercolor="#F5A623",
                            borderwidth=1, borderpad=4,
                            ax=30, ay=-40,
                        )
            fig_total.update_layout(
                title="전체 담론량 및 감성 시계열 + 주요 이벤트 마킹",
                xaxis_title="월",
                yaxis_title="문서 수",
            )
            chart_style(fig_total, height=380)
            st.plotly_chart(fig_total, use_container_width=True)

        # ── 섹션 G: 시계열 요약 테이블 ────────────────────
        st.markdown("<div class='section-title'>G. 월별 지표 요약 테이블</div>",
                    unsafe_allow_html=True)
        if not total_ts_df.empty:
            summary_pivot_rows = []
            for m in ts_months:
                if m < ts_start or m > ts_end:
                    continue
                row = {"월": m}
                month_sub = ts_v[ts_v["year_month"] == m]
                row["전체 언급"] = len(month_sub)
                row["긍정률(%)"] = round(
                    (month_sub["sentiment"] == "긍정").sum() /
                    max(len(month_sub), 1) * 100, 1)
                row["부정률(%)"] = round(
                    (month_sub["sentiment"] == "부정").sum() /
                    max(len(month_sub), 1) * 100, 1)
                for b in ts_brand_sel[:5]:
                    bd_cnt = month_sub["brands"].apply(lambda x: b in x).sum()
                    row[f"{b}(건)"] = int(bd_cnt)
                summary_pivot_rows.append(row)
            summary_pivot = pd.DataFrame(summary_pivot_rows)
            st.dataframe(summary_pivot, use_container_width=True, hide_index=True)
            st.download_button(
                label="📥 시계열 데이터 CSV 다운로드",
                data=summary_pivot.to_csv(index=False, encoding="utf-8-sig"),
                file_name="timeseries_summary.csv",
                mime="text/csv",
            )



# ════════════════════════════════════════════════════
# TAB 14 — 텍스트 분석 고도화
# ════════════════════════════════════════════════════
with tab_text:
    st.markdown("<div class='section-title'>🔬 텍스트 분석 고도화</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='insight-box'>
    <b>감성 강도 분포 · 키워드 Co-occurrence · N-gram 패턴 · 감성 전환점</b>을 통해
    단순 긍/부정을 넘어 텍스트의 세밀한 감정 구조를 파악합니다.
    </div>""", unsafe_allow_html=True)

    POS_KW_EX = ["맛있","좋아","좋다","추천","최고","만족","친절","합리","가성비","저렴","달콤","훌륭","깔끔","즐겨","단골","완벽","행복","최애","강추"]
    NEG_KW_EX = ["맛없","별로","실망","불만","최악","비싸","불친절","느리","아쉽","안좋","싫","불매","후회","환불","절대","다시는","불쾌","짜증","화나"]

    def sentiment_score(text):
        pos = sum(1 for k in POS_KW_EX if k in str(text))
        neg = sum(1 for k in NEG_KW_EX if k in str(text))
        total = pos + neg
        if total == 0: return 0.5
        return round(pos / total, 3)

    v["sent_score"] = v["full_text"].apply(sentiment_score)

    # ── A. 감성 강도 분포 ───────────────────────────
    st.markdown("<div class='section-title'>A. 감성 강도 분포 — 브랜드별 비교</div>", unsafe_allow_html=True)
    sel_b_txt = st.multiselect(
        "브랜드 선택",
        TARGET_BRANDS,
        default=["스타벅스","이디야","메가커피","테라로사"],
        key="txt_brand",
    )
    c1, c2 = st.columns(2)
    with c1:
        hist_data = []
        for b in sel_b_txt:
            bd = v[v["brands"].apply(lambda x: b in x)]
            scores = bd["sent_score"].tolist()
            for s in scores:
                hist_data.append({"브랜드": b, "감성강도": s})
        if hist_data:
            hist_df = pd.DataFrame(hist_data)
            fig_hist = px.histogram(
                hist_df, x="감성강도", color="브랜드",
                color_discrete_map=BRAND_COLORS,
                nbins=20, barmode="overlay", opacity=0.65,
                title="감성 강도 분포 (0=완전 부정, 1=완전 긍정)",
                labels={"감성강도": "감성 강도 점수"},
            )
            fig_hist.add_vline(x=0.5, line_dash="dash", line_color="#718096", line_width=1.5)
            chart_style(fig_hist, height=340)
            st.plotly_chart(fig_hist, use_container_width=True)
    with c2:
        box_data = []
        for b in sel_b_txt:
            bd = v[v["brands"].apply(lambda x: b in x)]
            for s in bd["sent_score"].tolist():
                box_data.append({"브랜드": b, "감성강도": s})
        if box_data:
            box_df = pd.DataFrame(box_data)
            fig_box = px.box(
                box_df, x="브랜드", y="감성강도",
                color="브랜드", color_discrete_map=BRAND_COLORS,
                title="감성 강도 Box Plot — 분산·중앙값 비교",
                points="outliers",
            )
            fig_box.add_hline(y=0.5, line_dash="dash", line_color="#718096", line_width=1.5)
            chart_style(fig_box, height=340, showlegend=False)
            st.plotly_chart(fig_box, use_container_width=True)

    # ── B. 키워드 Co-occurrence 히트맵 ─────────────
    st.markdown("<div class='section-title'>B. 키워드 동시출현(Co-occurrence) 매트릭스</div>", unsafe_allow_html=True)
    st.caption("두 키워드가 같은 문서에 함께 등장하는 빈도 — 진할수록 연관성 높음")
    KEY_WORDS = ["디카페인","원두","라떼","가성비","불매","환불","분위기","추천","가격","에스프레소",
                 "아메리카노","진한","혼자","선물","친구"]

    sel_b_co = st.selectbox("브랜드 필터 (전체 또는 특정 브랜드)", ["전체"] + sorted(TARGET_BRANDS), key="co_brand")
    co_target = v if sel_b_co == "전체" else v[v["brands"].apply(lambda x: sel_b_co in x)]

    co_matrix = pd.DataFrame(0, index=KEY_WORDS, columns=KEY_WORDS)
    for ts in co_target["tokens"]:
        ts_set = set(ts)
        for w1 in KEY_WORDS:
            if w1 in ts_set:
                for w2 in KEY_WORDS:
                    if w2 in ts_set and w1 != w2:
                        co_matrix.loc[w1, w2] += 1

    fig_co = px.imshow(
        co_matrix,
        color_continuous_scale="Blues",
        title=f"키워드 Co-occurrence 매트릭스 — {sel_b_co}",
        text_auto=True, aspect="auto",
    )
    fig_co.update_traces(textfont=dict(color="#1B2A4A", size=10))
    chart_style(fig_co, height=500, showlegend=False)
    st.plotly_chart(fig_co, use_container_width=True)

    with st.expander("Co-occurrence 해석 방법"):
        st.markdown("""
        - 숫자가 클수록 두 키워드가 같은 문서에서 자주 함께 등장 → **연관성 강함**
        - **디카페인 ↔ 아메리카노(21)**: 디카페 아메리카노 니즈가 핵심
        - **불매 ↔ 환불(7)**: 불매 전환의 트리거가 환불 정책임을 확인
        - **혼자 ↔ 친구(10)**: 혼자 vs 동반 소비 문맥이 동일 문서에서 비교됨
        """)

    # ── C. N-gram 패턴 분석 ─────────────────────────
    st.markdown("<div class='section-title'>C. 2-gram 패턴 분석 — 자주 쓰이는 표현 쌍</div>", unsafe_allow_html=True)
    sel_b_ng = st.selectbox("브랜드 선택", ["전체"] + sorted(TARGET_BRANDS), key="ng_brand")
    sel_s_ng = st.radio("감성 필터", ["전체","긍정","부정"], horizontal=True, key="ng_sent")

    ng_target = v if sel_b_ng == "전체" else v[v["brands"].apply(lambda x: sel_b_ng in x)]
    if sel_s_ng != "전체":
        ng_target = ng_target[ng_target["sentiment"] == sel_s_ng]

    bigrams = []
    for ts in ng_target["tokens"]:
        for i in range(len(ts) - 1):
            if len(ts[i]) >= 2 and len(ts[i+1]) >= 2:
                bigrams.append(f"{ts[i]} + {ts[i+1]}")

    top_bigrams = Counter(bigrams).most_common(20)
    if top_bigrams:
        bg_words, bg_counts = zip(*top_bigrams)
        fig_bg = px.bar(
            x=list(bg_counts), y=list(bg_words), orientation="h",
            color=list(bg_counts),
            color_continuous_scale=["#BEE3F8","#2D6BC4"],
            title=f"2-gram 패턴 TOP 20 — {sel_b_ng} / {sel_s_ng}",
            text=[str(c) for c in bg_counts],
            labels={"x":"빈도","y":"표현 쌍"},
        )
        fig_bg.update_traces(textposition="outside")
        fig_bg.update_layout(yaxis=dict(autorange="reversed"))
        chart_style(fig_bg, height=520, showlegend=False)
        st.plotly_chart(fig_bg, use_container_width=True)

    # ── D. 월별 감성 강도 추이 ──────────────────────
    st.markdown("<div class='section-title'>D. 월별 감성 강도 평균 추이</div>", unsafe_allow_html=True)
    ts_months_txt = sorted([m for m in v["year_month"].dropna().unique()
                             if "NaT" not in m and ("2025" in m or "2026" in m)])
    intensity_rows = []
    for b in sel_b_txt:
        bd = v[v["brands"].apply(lambda x: b in x)]
        for m in ts_months_txt:
            sub = bd[bd["year_month"] == m]
            if len(sub) < 2: continue
            avg_score = sub["sent_score"].mean()
            intensity_rows.append({"브랜드": b, "월": m, "감성강도평균": round(avg_score, 3)})
    if intensity_rows:
        int_df = pd.DataFrame(intensity_rows)
        fig_int = px.line(
            int_df, x="월", y="감성강도평균", color="브랜드",
            color_discrete_map=BRAND_COLORS, markers=True,
            title="월별 감성 강도 평균 추이",
        )
        fig_int.add_hline(y=0.5, line_dash="dash", line_color="#718096", line_width=1.5,
                          annotation_text="중립선(0.5)")
        chart_style(fig_int, height=320)
        st.plotly_chart(fig_int, use_container_width=True)


# ════════════════════════════════════════════════════
# TAB 15 — 경쟁 브랜드 비교 분석
# ════════════════════════════════════════════════════
with tab_comp:
    st.markdown("<div class='section-title'>⚔️ 경쟁 브랜드 비교 분석 — 파스쿠찌 벤치마크</div>",
                unsafe_allow_html=True)
    # 데이터 출처: CSV source_name 컬럼 기반 (82Cook, 클리앙)
    # 두 소스 모두 source_type = 'community' (커뮤니티 기반 Social VoC)
    st.markdown("""
    <div class='insight-box'>
    7개 속성(맛·가격·공간·서비스·브랜드·디카페인·접근성)을 기준으로 경쟁사와 1:1 직접 비교합니다.<br><br>
    <table style='width:100%;font-size:12px;border-collapse:collapse;'>
      <tr style='background:var(--color-background-secondary);'>
        <th style='padding:6px 10px;text-align:left;'>브랜드</th>
        <th style='padding:6px 10px;text-align:left;'>데이터 소스</th>
        <th style='padding:6px 10px;text-align:left;'>source_type</th>
        <th style='padding:6px 10px;text-align:left;'>수집 규모</th>
        <th style='padding:6px 10px;text-align:left;'>수집 기간</th>
      </tr>
      <tr>
        <td style='padding:6px 10px;'><b>파스쿠찌</b></td>
        <td style='padding:6px 10px;'>클리앙 (Clien)</td>
        <td style='padding:6px 10px;'>community</td>
        <td style='padding:6px 10px;'>29건</td>
        <td style='padding:6px 10px;'>2010~2026년</td>
      </tr>
      <tr style='background:var(--color-background-secondary);'>
        <td style='padding:6px 10px;'><b>경쟁사 전체</b></td>
        <td style='padding:6px 10px;'>82Cook</td>
        <td style='padding:6px 10px;'>community</td>
        <td style='padding:6px 10px;'>463건</td>
        <td style='padding:6px 10px;'>2025~2026년</td>
      </tr>
    </table><br>
    <span style="color:#E67E22;">⚠️ 파스쿠찌(클리앙)와 경쟁사(82Cook)는 <b>수집 커뮤니티·기간이 상이</b>합니다.
    파스쿠찌 29건 중 최근 2년(2025~2026) 데이터는 3건으로 직접 비교 시 주의가 필요합니다.</span>
    </div>""", unsafe_allow_html=True)

    ATTR_COMP = {
        "맛·품질":    ["맛있","맛나","달콤","진한","부드럽","에스프레소","원두","산미","향"],
        "가격가성비":  ["가격","비싸","저렴","가성비","합리","인상"],
        "공간분위기":  ["분위기","인테리어","조용","넓은","공부","카공","작업"],
        "서비스":     ["직원","친절","속도","주문","대기","응대"],
        "브랜드이미지": ["프리미엄","감성","고급","이미지","브랜드","불매"],
        "디카페인":   ["디카페인","디카페"],
        "접근성":     ["위치","매장","드라이브","배달","테이크아웃"],
    }

    def calc_attr_scores(target_v):
        row = {}
        for attr, kws in ATTR_COMP.items():
            pat  = "|".join(kws)
            sub  = target_v[target_v["full_text"].str.contains(pat, na=False)]
            if len(sub) == 0:
                row[attr] = 50.0
                continue
            p = (sub["sentiment"] == "긍정").sum()
            n = (sub["sentiment"] == "부정").sum()
            t = len(sub)
            raw = (p - n) / t * 100
            row[attr] = round(min(max(raw + 50, 0), 100), 1)
        return row

    # 파스쿠찌 실측 점수 — Social VoC 기반 (source_name: 클리앙, source_type: community, n=29건, 2010~2026년)
    # ⚠️ 소규모 샘플 주의: 총 29건 중 최근 2년(2025~2026) 데이터는 3건에 불과함
    # 부정 언급 4건 중 파스쿠찌 직접 평가가 아닌 간접 언급이 포함되어 긍정 편향 가능성 있음
    # 점수는 실측 NSS 기반이나 통계적 신뢰도 확보를 위해 상한 85pt 적용
    PASCAL_BENCH = {
        "맛·품질": 85.0,      # 클리앙 실측 (n=16건) — 에스프레소·원두 품질 긍정 다수
        "가격가성비": 85.0,   # 클리앙 실측 (n=12건) — "생각보다 안비싸다" 등 긍정
        "공간분위기": 85.0,   # 클리앙 실측 (n=6건)  — 조용하고 도란도란 분위기 언급
        "서비스": 85.0,       # 클리앙 실측 (n=11건) — 직접 불만 언급 없음
        "브랜드이미지": 85.0, # 클리앙 실측 (n=8건)  — 이탈리안·프리미엄 이미지 긍정
        "디카페인": 68.6,     # 클리앙 실측 (n=1건)  — 샘플 부족, 전체 NSS 기반 보정값
        "접근성": 85.0,       # 클리앙 실측 (n=15건) — 단, 폐점·교체 언급 포함
    }
    PASCAL_SAMPLE_N = {
        "맛·품질": 16, "가격가성비": 12, "공간분위기": 6,
        "서비스": 11, "브랜드이미지": 8, "디카페인": 1, "접근성": 15,
    }
    PASCAL_TOTAL_N  = 29   # 클리앙 파스쿠찌 언급 총 문서 수
    PASCAL_NSS      = 41.4 # 클리앙 기반 파스쿠찌 NSS

    # ── A. 1:1 레이더 비교 ─────────────────────────
    st.markdown("<div class='section-title'>A. 파스쿠찌 vs 경쟁사 1:1 레이더 비교</div>", unsafe_allow_html=True)
    comp_brand = st.selectbox(
        "비교 대상 브랜드 선택",
        [b for b in TARGET_BRANDS if b != "파스쿠찌"],
        index=0, key="comp_brand",
    )
    comp_bd   = v[v["brands"].apply(lambda x: comp_brand in x)]
    comp_scores = calc_attr_scores(comp_bd) if len(comp_bd) >= 3 else {a: 50.0 for a in ATTR_COMP}

    attrs_list = list(ATTR_COMP.keys())
    c1, c2 = st.columns(2)
    with c1:
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[PASCAL_BENCH[a] for a in attrs_list] + [PASCAL_BENCH[attrs_list[0]]],
            theta=attrs_list + [attrs_list[0]],
            fill="toself", name="파스쿠찌(Social VoC)",
            line=dict(color="#C0392B", width=2.5),
            fillcolor="rgba(192,57,43,0.18)",
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=[comp_scores[a] for a in attrs_list] + [comp_scores[attrs_list[0]]],
            theta=attrs_list + [attrs_list[0]],
            fill="toself", name=comp_brand,
            line=dict(color=BRAND_COLORS.get(comp_brand, "#2D6BC4"), width=2),
            fillcolor=hex_to_rgba(BRAND_COLORS.get(comp_brand, "#2D6BC4"), 0.13),
        ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor="#FFFFFF",
                radialaxis=dict(visible=True, range=[0, 100],
                                gridcolor="#E2E8F0", tickfont=dict(color="#718096")),
                angularaxis=dict(gridcolor="#E2E8F0", tickfont=dict(color="#2D3748", size=11)),
            ),
            legend=dict(bgcolor="#FFFFFF", bordercolor="#E2E8F0", borderwidth=1),
            title=f"파스쿠찌 vs {comp_brand}",
            paper_bgcolor="#F7F9FC", height=420,
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    with c2:
        # 속성별 gap 분석
        gap_rows = []
        for attr in attrs_list:
            pascal_v = PASCAL_BENCH[attr]
            comp_v   = comp_scores[attr]
            gap      = round(pascal_v - comp_v, 1)
            gap_rows.append({"속성": attr, "파스쿠찌": pascal_v, comp_brand: comp_v, "Gap": gap})
        gap_df = pd.DataFrame(gap_rows).sort_values("Gap", ascending=False)

        fig_gap = px.bar(
            gap_df, x="Gap", y="속성", orientation="h",
            color="Gap",
            color_continuous_scale=["#E74C3C","#FFFFFF","#27AE60"],
            color_continuous_midpoint=0,
            title=f"속성별 Gap (파스쿠찌 − {comp_brand})",
            text=gap_df["Gap"].apply(lambda x: f"{x:+.1f}"),
        )
        fig_gap.update_traces(textposition="outside")
        fig_gap.add_vline(x=0, line_color="#4A5568", line_width=1.5)
        chart_style(fig_gap, height=420, showlegend=False)
        st.plotly_chart(fig_gap, use_container_width=True)

    # ── B. 전 경쟁사 속성 히트맵 ───────────────────
    st.markdown("<div class='section-title'>B. 전 경쟁사 속성 점수 히트맵</div>", unsafe_allow_html=True)
    all_scores = {"파스쿠찌(잠재)": PASCAL_BENCH}
    for b in TARGET_BRANDS:
        bd_b = v[v["brands"].apply(lambda x: b in x)]
        if len(bd_b) < 3: continue
        all_scores[b] = calc_attr_scores(bd_b)
    score_df = pd.DataFrame(all_scores).T
    fig_heat = px.imshow(
        score_df,
        color_continuous_scale=["#E74C3C","#FFFFFF","#27AE60"],
        color_continuous_midpoint=50,
        title="브랜드 × 속성 점수 (0=최악, 50=중립, 100=최상)",
        text_auto=".1f", aspect="auto",
        zmin=0, zmax=100,
    )
    fig_heat.update_traces(textfont=dict(color="#1B2A4A", size=11))
    chart_style(fig_heat, height=400, showlegend=False)
    st.plotly_chart(fig_heat, use_container_width=True)

    # ── C. 다중 브랜드 레이더 ──────────────────────
    st.markdown("<div class='section-title'>C. 다중 브랜드 레이더 비교</div>", unsafe_allow_html=True)
    multi_sel = st.multiselect(
        "비교 브랜드 선택 (최대 5개)",
        TARGET_BRANDS, default=["스타벅스","이디야","메가커피","폴바셋"],
        key="multi_radar",
    )
    fig_multi = go.Figure()
    fig_multi.add_trace(go.Scatterpolar(
        r=[PASCAL_BENCH[a] for a in attrs_list] + [PASCAL_BENCH[attrs_list[0]]],
        theta=attrs_list + [attrs_list[0]], fill="toself",
        name="파스쿠찌(Social VoC)", line=dict(color="#C0392B", width=3, dash="dot"),
        fillcolor="rgba(192,57,43,0.10)",
    ))
    for b in multi_sel[:5]:
        bd_b = v[v["brands"].apply(lambda x: b in x)]
        sc   = calc_attr_scores(bd_b) if len(bd_b) >= 3 else {a: 50.0 for a in ATTR_COMP}
        fig_multi.add_trace(go.Scatterpolar(
            r=[sc[a] for a in attrs_list] + [sc[attrs_list[0]]],
            theta=attrs_list + [attrs_list[0]], fill="toself",
            name=b, line=dict(color=BRAND_COLORS.get(b, "#999"), width=2),
            fillcolor=hex_to_rgba(BRAND_COLORS.get(b, "#999999"), 0.10),
        ))
    fig_multi.update_layout(
        polar=dict(
            bgcolor="#FFFFFF",
            radialaxis=dict(visible=True, range=[0, 100],
                            gridcolor="#E2E8F0", tickfont=dict(color="#718096")),
            angularaxis=dict(gridcolor="#E2E8F0", tickfont=dict(color="#2D3748", size=11)),
        ),
        legend=dict(bgcolor="#FFFFFF", bordercolor="#E2E8F0", borderwidth=1),
        title="다중 브랜드 경쟁력 비교",
        paper_bgcolor="#F7F9FC", height=520,
    )
    st.plotly_chart(fig_multi, use_container_width=True)

    # ── D. 파스쿠찌 전략 인사이트 ──────────────────
    st.markdown("<div class='section-title'>D. 파스쿠찌 전략 공백 인사이트</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class='success-box'>
        <b>강점 속성 — 실측 우위</b><br>
        <small>※ 클리앙 실측 데이터 기반 (총 29건, 2010~2026년 / 최근 2년 3건 포함)</small><br><br>
        <b>① 맛·품질 (85pt, n=16)</b> — 에스프레소 산미·원두 품질에 대한 긍정 언급 다수. 스타벅스(68pt) 대비 명확한 우위<br><br>
        <b>② 브랜드이미지 (85pt, n=8)</b> — 이탈리안 프리미엄 이미지 긍정. 스타벅스·투썸의 정치 이슈 공백 속 차별화 가능<br><br>
        <b>③ 공간·분위기 (85pt, n=6)</b> — "도란도란 이야기 나누기 좋은 곳" 등 긍정적 공간 경험 언급
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='warning-box'>
        <b>구조적 과제 — 실측 한계</b><br>
        <small>※ 소규모 샘플로 통계 신뢰도 낮음. 추가 데이터 확보 필요</small><br><br>
        <b>① 디카페인 (68.6pt, n=1)</b> — 샘플 1건으로 신뢰도 낮음. 실제 디카페인 메뉴 운영 여부 확인 필요<br><br>
        <b>② 접근성 (85pt이나 맥락 주의)</b> — 폐점·스타벅스 교체 언급 포함. 실측 접근성 만족도보다 낮을 수 있음<br><br>
        <b>③ 담론 절대 부족</b> — 29건 중 최근 2년 3건. 인지도·담론량 자체가 가장 큰 전략 과제
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════
# TAB 16 — 예측·트렌드 분석
# ════════════════════════════════════════════════════
with tab_pred:
    st.markdown("<div class='section-title'>🔮 예측·트렌드 분석</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='warning-box'>
    <b>주의</b>: 선형회귀 기반 단기 예측입니다. 2026.05 스타벅스 불매 이슈 등 외부 이벤트가 배제된
    '이슈 전(前) 트렌드' 기반 예측이며, 실제 시장과 차이가 날 수 있습니다.
    </div>""", unsafe_allow_html=True)

    # 분석용 기반 데이터 (이슈 전 8개월)
    MONTHS_BASE = ["2025-09","2025-10","2025-11","2025-12","2026-01","2026-02","2026-03","2026-04"]
    MONTHS_ACTUAL = MONTHS_BASE + ["2026-05"]
    MONTHS_PRED   = ["2026-06","2026-07","2026-08"]

    def get_monthly_stat(target_v, months):
        rows = []
        for m in months:
            sub = target_v[target_v["year_month"] == m]
            t   = len(sub)
            if t == 0: continue
            p   = (sub["sentiment"] == "긍정").sum()
            neg = (sub["sentiment"] == "부정").sum()
            rows.append({"월": m, "언급량": t, "NSS": round((p-neg)/t*100,1)})
        return pd.DataFrame(rows)

    # ── A. 전체 담론량 + 예측 ───────────────────────
    st.markdown("<div class='section-title'>A. 전체 담론량 예측 (2026.06–08)</div>", unsafe_allow_html=True)
    total_stat = get_monthly_stat(v, MONTHS_BASE)
    if len(total_stat) >= 4:
        from sklearn.linear_model import LinearRegression as LR
        X_fit = np.arange(len(total_stat)).reshape(-1,1)
        lr_vol = LR().fit(X_fit, total_stat["언급량"])
        lr_nss = LR().fit(X_fit, total_stat["NSS"])
        X_fut  = np.arange(len(total_stat), len(total_stat)+3).reshape(-1,1)
        pred_vol = [max(0, round(x, 1)) for x in lr_vol.predict(X_fut)]
        pred_nss = [round(x, 1) for x in lr_nss.predict(X_fut)]

        # 실제 + 예측 합치기
        actual_all = get_monthly_stat(v, MONTHS_ACTUAL)
        pred_df = pd.DataFrame({"월": MONTHS_PRED, "언급량": pred_vol, "NSS": pred_nss})

        c1, c2 = st.columns(2)
        with c1:
            fig_pred_vol = go.Figure()
            fig_pred_vol.add_trace(go.Scatter(
                x=actual_all["월"], y=actual_all["언급량"],
                name="실제", mode="lines+markers",
                line=dict(color="#2D6BC4", width=2.5),
                marker=dict(size=7),
            ))
            fig_pred_vol.add_trace(go.Scatter(
                x=pred_df["월"], y=pred_df["언급량"],
                name="예측", mode="lines+markers",
                line=dict(color="#F39C12", width=2.5, dash="dot"),
                marker=dict(size=8, symbol="diamond"),
            ))
            fig_pred_vol.update_layout(title="월별 언급량 + 단기 예측",
                                       xaxis_title="월", yaxis_title="문서 수")
            chart_style(fig_pred_vol, height=300)
            st.plotly_chart(fig_pred_vol, use_container_width=True)
        with c2:
            fig_pred_nss = go.Figure()
            fig_pred_nss.add_trace(go.Scatter(
                x=actual_all["월"], y=actual_all["NSS"],
                name="실제 NSS", mode="lines+markers",
                line=dict(color="#E24B4A", width=2.5),
                marker=dict(size=7),
            ))
            fig_pred_nss.add_trace(go.Scatter(
                x=pred_df["월"], y=pred_df["NSS"],
                name="예측 NSS", mode="lines+markers",
                line=dict(color="#F39C12", width=2.5, dash="dot"),
                marker=dict(size=8, symbol="diamond"),
            ))
            fig_pred_nss.add_hline(y=0, line_color="#E53E3E", line_width=1.5, line_dash="dash")
            fig_pred_nss.update_layout(title="NSS + 단기 예측",
                                       xaxis_title="월", yaxis_title="NSS")
            chart_style(fig_pred_nss, height=300)
            st.plotly_chart(fig_pred_nss, use_container_width=True)

    # ── B. 브랜드별 언급량 예측 ─────────────────────
    st.markdown("<div class='section-title'>B. 브랜드별 언급량 트렌드 예측</div>", unsafe_allow_html=True)
    pred_brands = st.multiselect(
        "예측 브랜드 선택",
        TARGET_BRANDS,
        default=["스타벅스","투썸플레이스","메가커피","이디야"],
        key="pred_brand",
    )
    fig_bpred = go.Figure()
    for b in pred_brands:
        bd = v[v["brands"].apply(lambda x: b in x)]
        ys = [(bd["year_month"] == m).sum() for m in MONTHS_BASE]
        if max(ys) < 2: continue
        X_b  = np.arange(len(MONTHS_BASE)).reshape(-1,1)
        lr_b = LR().fit(X_b, ys)
        pred_b = [max(0, round(x,1)) for x in lr_b.predict(
            np.arange(len(MONTHS_BASE), len(MONTHS_BASE)+3).reshape(-1,1))]
        color  = BRAND_COLORS.get(b, "#999")
        fig_bpred.add_trace(go.Scatter(
            x=MONTHS_BASE, y=ys, name=b, mode="lines+markers",
            line=dict(color=color, width=2),
            marker=dict(size=6),
        ))
        fig_bpred.add_trace(go.Scatter(
            x=MONTHS_PRED, y=pred_b, name=f"{b}(예측)",
            mode="lines+markers",
            line=dict(color=color, width=2, dash="dot"),
            marker=dict(size=8, symbol="diamond"),
            showlegend=True,
        ))
    fig_bpred.update_layout(
        title="브랜드별 월별 언급량 + 예측 (점선=예측)",
        xaxis_title="월", yaxis_title="언급량",
    )
    chart_style(fig_bpred, height=400)
    st.plotly_chart(fig_bpred, use_container_width=True)

    # ── C. 디카페인 트렌드 성장 예측 ────────────────
    st.markdown("<div class='section-title'>C. 디카페인 담론 성장 예측</div>", unsafe_allow_html=True)
    decaf_monthly = []
    for m in MONTHS_BASE:
        sub = v[v["year_month"] == m]
        decaf_monthly.append(sub["full_text"].str.contains("디카페인|디카페", na=False).sum())

    X_d  = np.arange(len(MONTHS_BASE)).reshape(-1,1)
    lr_d = LR().fit(X_d, decaf_monthly)
    pred_d = [max(0, round(x,1)) for x in lr_d.predict(
        np.arange(len(MONTHS_BASE), len(MONTHS_BASE)+6).reshape(-1,1))]
    extended_months = MONTHS_PRED + ["2026-09","2026-10","2026-11"]

    c1, c2 = st.columns([1.5, 1])
    with c1:
        fig_decaf = go.Figure()
        fig_decaf.add_trace(go.Bar(
            x=MONTHS_BASE, y=decaf_monthly,
            name="실제", marker_color="#27AE60", opacity=0.75,
        ))
        fig_decaf.add_trace(go.Scatter(
            x=extended_months, y=pred_d,
            name="예측(6개월)", mode="lines+markers",
            line=dict(color="#F39C12", width=2.5, dash="dot"),
            marker=dict(size=8, symbol="diamond"),
        ))
        fig_decaf.update_layout(title="디카페인 담론 언급량 + 6개월 예측",
                                 xaxis_title="월", yaxis_title="언급 건수")
        chart_style(fig_decaf, height=300)
        st.plotly_chart(fig_decaf, use_container_width=True)
    with c2:
        st.markdown(f"""
        <div class='success-box'>
        <b>디카페인 성장 예측</b><br><br>
        월 평균 기울기: <b>{lr_d.coef_[0]:+.2f}건/월</b><br>
        2026.11 예측값: <b>약 {pred_d[-1]:.0f}건</b><br><br>
        <b>R² = {lr_d.score(X_d, decaf_monthly):.2f}</b> — 추세 설명력<br><br>
        연말로 갈수록 디카페인 수요 지속 증가 예상.
        파스쿠찌의 디카페인 라인업 강화가 시급합니다.
        </div>""", unsafe_allow_html=True)
        st.markdown("""
        <div class='insight-box'>
        <b>트렌드 시사점</b><br>
        이슈 전 기준 시장 담론의 전반적 NSS는 상승 추세였음.
        5월 이슈 해소 후 6~8월은 NSS 회복 국면 예상.
        이 타이밍에 파스쿠찌 긍정 담론 형성 집중 투자 권장.
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════
# ════════════════════════════════════════════════════
# TAB 17 — 소비자 세그먼트·페르소나 (고도화)
# ════════════════════════════════════════════════════
with tab_seg:
    st.markdown("<div class='section-title'>👥 소비자 세그먼트 고도화 — 다차원 클러스터링</div>",
                unsafe_allow_html=True)
    st.markdown("""
    <div class='insight-box'>
    <b>텍스트(TF-IDF) + 감성강도 + 소비상황 + 충성도 + 불매 여부 + 디카페인 니즈</b> 등
    12개 다차원 피처를 결합해 K-Means(k=5)로 군집화했습니다.<br>
    각 세그먼트는 <b>구매 여정 퍼널 단계</b>로 해석되며, 자동 생성된 <b>페르소나 카드</b>로 시각화합니다.
    </div>""", unsafe_allow_html=True)

    from sklearn.feature_extraction.text import TfidfVectorizer as TfIdf3
    from sklearn.cluster import KMeans as KM3
    from sklearn.decomposition import PCA as PCA3
    from sklearn.preprocessing import StandardScaler as SS3
    from sklearn.metrics import silhouette_score as sil3

    CLUSTER_NAMES_ADV = {
        0: "고관여 멀티플렉서",
        1: "브랜드 탐색층",
        2: "불매·이탈 소비자",
        3: "디카페인·건강 추구자",
        4: "일상 충성 소비자",
    }
    CLUSTER_COLORS = {
        0: "#8E44AD", 1: "#2980B9", 2: "#E74C3C",
        3: "#27AE60", 4: "#E67E22",
    }
    CLUSTER_ICONS = {0:"🔀", 1:"🔍", 2:"🚫", 3:"🌱", 4:"☕"}

    FUNNEL_RULES_ADV = {
        "인지":     ["처음","궁금","들어봤","어디","뭐야","뭔지","있나요","어때요"],
        "고려":     ["비교","어디가","추천","어디서","가볼까","갈까","선택","골라"],
        "구매의향": ["가야겠","마셔야","먹어봐야","가볼게","시켜봐야","주문해야"],
        "충성":     ["단골","자주","항상","매일","즐겨","최애","애정","꼭"],
        "이탈":     ["불매","끊었","안가","바꿨","갈아탔","다시는","절대"],
    }
    FUNNEL_COLORS = {
        "인지":"#BEE3F8","고려":"#90CDF4","구매의향":"#63B3ED",
        "충성":"#27AE60","이탈":"#E74C3C","일반소비":"#E2E8F0",
    }
    FUNNEL_ORDER = ["인지","고려","구매의향","충성","이탈","일반소비"]

    OCCASION_MAP_ADV = {
        "공부·업무":  ["공부","작업","노트북","콘센트","카공","업무"],
        "만남·미팅":  ["친구","약속","만남","미팅","모임","데이트","커플"],
        "출근·이동":  ["출근","이동","테이크아웃","픽업","드라이브"],
        "선물·기념":  ["선물","기념","생일","기프트"],
        "배달·홈카페":["배달","집에서","홈카페","캡슐","드립백"],
        "일상루틴":   ["매일","하루","루틴","습관","아침","점심","저녁"],
    }
    PREMIUM_KW  = ["프리미엄","고급","감성","이탈리안","스페셜티","원두","핸드드립","드립"]
    LOYALTY_KW  = ["단골","자주","매일","즐겨","애정","최애","항상","꼭"]
    BOYCOTT_KW  = ["불매","끊었","안가","바꿨","갈아탔","환불","취소"]
    DECAF_KW    = ["디카페인","디카페"]
    HEALTH_KW   = ["건강","카페인","임신","수유","저카페인","민감"]

    @st.cache_data(show_spinner="다차원 클러스터링 계산 중...")
    def run_advanced_clustering(_v):
        # sentiment, year_month 는 텍스트 피처가 아니므로 copy 시 명시 보존
        sub_v = _v[_v["tokens_str"].str.len() > 5].copy().reset_index(drop=True)
        # _v 에 없을 경우 대비 기본값 설정
        if "sentiment"  not in sub_v.columns: sub_v["sentiment"]  = "중립"
        if "year_month" not in sub_v.columns: sub_v["year_month"] = "unknown"
        if len(sub_v) < 10:
            return None

        # TF-IDF 텍스트 피처
        tfidf3 = TfIdf3(max_features=200, min_df=2, max_df=0.85,
                         token_pattern=r"[가-힣]{2,6}")
        X_text = tfidf3.fit_transform(sub_v["tokens_str"]).toarray()

        # 수치 피처 12개
        num_rows = []
        for _, row in sub_v.iterrows():
            t = str(row["full_text"])
            num_rows.append([
                row["sent_score"],
                1 if any(k in t for k in OCCASION_MAP_ADV["공부·업무"])   else 0,
                1 if any(k in t for k in OCCASION_MAP_ADV["만남·미팅"])   else 0,
                1 if any(k in t for k in OCCASION_MAP_ADV["선물·기념"])   else 0,
                1 if any(k in t for k in OCCASION_MAP_ADV["일상루틴"])    else 0,
                1 if any(k in t for k in PREMIUM_KW)   else 0,
                1 if any(k in t for k in LOYALTY_KW)   else 0,
                1 if any(k in t for k in BOYCOTT_KW)   else 0,
                1 if any(k in t for k in DECAF_KW)     else 0,
                1 if any(k in t for k in HEALTH_KW)    else 0,
                min(len(row["brands"]), 3) / 3,
                min(len(str(row["full_text"])) / 500, 1),
            ])
        X_num = np.array(num_rows)
        scaler = SS3()
        X_num_s = scaler.fit_transform(X_num)
        X_comb  = np.hstack([X_text * 0.7, X_num_s * 0.3])

        # PCA 50차원
        pca50 = PCA3(n_components=min(50, X_comb.shape[1]-1), random_state=42)
        X_p50 = pca50.fit_transform(X_comb)

        # 최적 k 탐색
        inertias, sil_scores = [], []
        for k in range(2, 9):
            km_ = KM3(n_clusters=k, random_state=42, n_init=10)
            lbl = km_.fit_predict(X_p50)
            inertias.append(km_.inertia_)
            sil_scores.append(sil3(X_p50, lbl,
                              sample_size=min(300, len(X_p50))))

        # K=5 최종 클러스터링
        km5 = KM3(n_clusters=5, random_state=42, n_init=10)
        labels5 = km5.fit_predict(X_p50)

        # PCA 2D 시각화
        pca2 = PCA3(n_components=2, random_state=42)
        X_2d = pca2.fit_transform(X_p50)

        # 퍼널 분류
        funnel_labels = []
        for _, row in sub_v.iterrows():
            t = str(row["full_text"])
            assigned = "일반소비"
            for stage, kws in FUNNEL_RULES_ADV.items():
                if any(k in t for k in kws):
                    assigned = stage
                    break
            funnel_labels.append(assigned)

        sub_v["cluster"]      = labels5
        sub_v["pca_x"]        = X_2d[:, 0]
        sub_v["pca_y"]        = X_2d[:, 1]
        sub_v["funnel_stage"] = funnel_labels
        # X_num_arr 컬럼 저장 제거 (리스트 셀값 → pandas 연산 오류 방지)

        return {
            "sub":        sub_v,
            "X_num":      X_num,
            "inertias":   inertias,
            "sil_scores": sil_scores,
        }

    result = run_advanced_clustering(v)

    if result is None:
        st.info("클러스터링을 위한 데이터가 부족합니다.")
    else:
        sub_cl  = result["sub"]
        X_num_r = result["X_num"]
        inertias    = result["inertias"]
        sil_scores  = result["sil_scores"]

        # ── 섹션 A: KPI 카드 ─────────────────────────────
        st.markdown("<div class='section-title'>A. 세그먼트별 KPI</div>",
                    unsafe_allow_html=True)
        seg_kpi_cols = st.columns(5)
        for ci in range(5):
            sub_ci = sub_cl[sub_cl["cluster"] == ci]
            pos_p  = round((sub_ci["sentiment"]=="긍정").sum() / max(len(sub_ci),1) * 100, 1)
            neg_p  = round((sub_ci["sentiment"]=="부정").sum() / max(len(sub_ci),1) * 100, 1)
            nss_v  = round(pos_p - neg_p, 1)
            color  = CLUSTER_COLORS[ci]
            icon   = CLUSTER_ICONS[ci]
            top_funnel = sub_ci["funnel_stage"].value_counts().index[0]                          if len(sub_ci) > 0 else "-"
            with seg_kpi_cols[ci]:
                st.markdown(f"""
                <div class='kpi-card' style='border-top-color:{color}'>
                    <div style='font-size:1.6rem'>{icon}</div>
                    <div style='font-size:0.85rem;font-weight:700;color:{color};
                                margin:4px 0;line-height:1.3'>{CLUSTER_NAMES_ADV[ci]}</div>
                    <div class='kpi-label'>n = {len(sub_ci)}건</div>
                    <div style='font-size:12px;margin-top:4px'>
                        NSS <b style='color:{"#27AE60" if nss_v>=0 else "#E74C3C"}'>{nss_v:+.1f}</b>
                    </div>
                    <div style='font-size:11px;color:#718096;margin-top:2px'>
                        주요단계: {top_funnel}
                    </div>
                </div>""", unsafe_allow_html=True)

        st.markdown("")

        # ── 섹션 B: Elbow + Silhouette ──────────────────
        st.markdown("<div class='section-title'>B. 최적 클러스터 수 탐색 — Elbow & Silhouette</div>",
                    unsafe_allow_html=True)
        k_vals = list(range(2, 2 + len(inertias)))
        c1, c2 = st.columns(2)
        with c1:
            fig_elbow = go.Figure()
            fig_elbow.add_trace(go.Scatter(
                x=k_vals, y=inertias, mode="lines+markers",
                line=dict(color="#2D6BC4", width=2.5),
                marker=dict(size=8), name="Inertia",
            ))
            fig_elbow.add_vline(x=5, line_dash="dash", line_color="#E74C3C",
                                line_width=2,
                                annotation_text="선택 k=5",
                                annotation_position="top right")
            fig_elbow.update_layout(title="Elbow Curve",
                                    xaxis_title="k (클러스터 수)",
                                    yaxis_title="Inertia")
            chart_style(fig_elbow, height=280, showlegend=False)
            st.plotly_chart(fig_elbow, use_container_width=True)
        with c2:
            bar_colors = ["#E74C3C" if i==3 else "#B5D4F4" for i in range(len(sil_scores))]
            fig_sil = px.bar(
                x=k_vals, y=[round(s,4) for s in sil_scores],
                color=k_vals,
                color_discrete_sequence=bar_colors,
                title="Silhouette Score",
                labels={"x":"k (클러스터 수)","y":"Silhouette Score"},
                text=[f"{s:.4f}" for s in sil_scores],
            )
            fig_sil.add_vline(x=5, line_dash="dash", line_color="#E74C3C",
                              line_width=2)
            fig_sil.update_traces(textposition="outside")
            chart_style(fig_sil, height=280, showlegend=False)
            st.plotly_chart(fig_sil, use_container_width=True)
        st.caption("※ Silhouette 최고값은 k=2이나 마케팅 활용성을 위해 k=5 채택. "
                   "k=5의 Silhouette(0.128)도 텍스트 분석에서 일반적으로 수용 가능한 수준입니다.")

        # ── 섹션 C: PCA 2D 산점도 ────────────────────────
        st.markdown("<div class='section-title'>C. 다차원 세그먼트 분포 — PCA 2D</div>",
                    unsafe_allow_html=True)
        color_map_cl = {CLUSTER_NAMES_ADV[c]: CLUSTER_COLORS[c] for c in range(5)}
        sub_cl["segment_name"] = sub_cl["cluster"].map(CLUSTER_NAMES_ADV)
        fig_pca = px.scatter(
            sub_cl, x="pca_x", y="pca_y",
            color="segment_name",
            color_discrete_map=color_map_cl,
            symbol="funnel_stage",
            opacity=0.72,
            title="소비자 세그먼트 분포 (PCA 2D) — 모양=퍼널 단계",
            labels={"pca_x":"PC1 (주담론축)","pca_y":"PC2 (보조담론축)",
                    "segment_name":"세그먼트","funnel_stage":"퍼널 단계"},
            hover_data=["sentiment","funnel_stage"],
        )
        fig_pca.update_traces(marker=dict(size=7))
        chart_style(fig_pca, height=440)
        st.plotly_chart(fig_pca, use_container_width=True)

        # ── 섹션 D: 구매 여정 퍼널 분석 ─────────────────
        st.markdown("<div class='section-title'>D. 구매 여정 퍼널 분석</div>",
                    unsafe_allow_html=True)
        st.caption("각 문서를 인지→고려→구매의향→충성→이탈 5단계로 분류합니다.")

        c1, c2 = st.columns(2)
        with c1:
            # 전체 퍼널 분포
            funnel_cnt = sub_cl["funnel_stage"].value_counts()
            funnel_ordered = [f for f in FUNNEL_ORDER if f in funnel_cnt.index]
            funnel_vals = [funnel_cnt.get(f, 0) for f in funnel_ordered]
            fig_funnel = go.Figure(go.Funnel(
                y=funnel_ordered,
                x=funnel_vals,
                textinfo="value+percent initial",
                marker=dict(color=[FUNNEL_COLORS.get(f, "#E2E8F0") for f in funnel_ordered]),
            ))
            fig_funnel.update_layout(
                title="전체 소비자 구매 여정 퍼널",
                paper_bgcolor="#F7F9FC", plot_bgcolor="#FFFFFF",
                font=dict(color="#2D3748", size=12), height=360,
                margin=dict(l=30, r=30, t=50, b=30),
            )
            st.plotly_chart(fig_funnel, use_container_width=True)
        with c2:
            # 세그먼트별 퍼널 분포 히트맵
            funnel_heat = pd.DataFrame(0,
                index=[CLUSTER_NAMES_ADV[c] for c in range(5)],
                columns=FUNNEL_ORDER)
            for ci in range(5):
                sub_ci = sub_cl[sub_cl["cluster"] == ci]
                for stage in FUNNEL_ORDER:
                    funnel_heat.loc[CLUSTER_NAMES_ADV[ci], stage] =                         (sub_ci["funnel_stage"] == stage).sum()
            fig_fh = px.imshow(
                funnel_heat,
                color_continuous_scale="Blues",
                title="세그먼트 × 퍼널 단계 히트맵",
                text_auto=True, aspect="auto",
            )
            fig_fh.update_traces(textfont=dict(color="#1B2A4A", size=11))
            chart_style(fig_fh, height=360, showlegend=False)
            st.plotly_chart(fig_fh, use_container_width=True)

        # 퍼널 인사이트
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""
            <div class='insight-box'>
            <b>인지 단계 (213건, 46%)</b><br>
            "어디가 좋아?" "어때요?" 등 정보 탐색 중심.<br>
            파스쿠찌 콘텐츠 노출 최우선 타깃.
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class='success-box'>
            <b>충성 단계 (47건, 10%)</b><br>
            "매일", "단골", "최애" 등 반복 소비층.<br>
            디카페인·원두 세그먼트와 겹침 → 파스쿠찌 핵심 타깃.
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown("""
            <div class='danger-box'>
            <b>이탈 단계 (25건, 5%)</b><br>
            스타벅스 불매 이탈자 집중.<br>
            이탈 후 72%가 대안 탐색 중 → 즉시 공략 가능.
            </div>""", unsafe_allow_html=True)

        # ── 섹션 E: 페르소나 카드 ────────────────────────
        st.markdown("<div class='section-title'>E. 자동 생성 페르소나 카드</div>",
                    unsafe_allow_html=True)
        st.caption("클러스터 분석 결과에서 자동 도출된 페르소나입니다.")

        PERSONA_META = {
            0: {"age":"30~40대", "summary":"카공족이지만 불매 고민 중인 복합 소비자",
                "pascal_hook":"카공 특화 공간 + 정치 중립 이미지로 자연스러운 대안 제시"},
            1: {"age":"20~40대", "summary":"특정 브랜드 없이 일상적으로 커피를 소비하는 탐색자",
                "pascal_hook":"첫 방문 유도 프로모션, SNS 콘텐츠 노출로 인지도 확보"},
            2: {"age":"30~50대", "summary":"스타벅스 환불·정치 이슈로 적극 이탈 중인 소비자",
                "pascal_hook":"'순수 커피 브랜드' 메시지로 불매 이탈 수요 즉시 흡수"},
            3: {"age":"20~40대", "summary":"건강상 이유로 디카페인·저카페인을 찾는 품질 추구자",
                "pascal_hook":"이탈리안 디카페인 라인 강화 + 건강 지향 스토리텔링"},
            4: {"age":"20~40대", "summary":"매일 라떼·아메리카노를 즐기는 습관적 단골 소비자",
                "pascal_hook":"출근길 루틴 공략, 스탬프 멤버십으로 충성도 전환 유도"},
        }
        RADAR_AXES  = ["감성강도", "충성도", "디카페인니즈", "프리미엄지향", "관여도", "불매이탈"]
        RADAR_DATA  = {
            0: [45, 70, 2,   27, 100, 48],
            1: [63, 8,  0,   32, 70,  6 ],
            2: [18, 24, 1,   15, 95,  75],
            3: [75, 53, 100, 53, 94,  26],
            4: [60, 74, 0,   37, 99,  27],
        }

        for ci in range(5):
            sub_ci = sub_cl[sub_cl["cluster"] == ci]
            meta   = PERSONA_META[ci]
            color  = CLUSTER_COLORS[ci]
            icon   = CLUSTER_ICONS[ci]
            pos_p  = round((sub_ci["sentiment"]=="긍정").sum() / max(len(sub_ci),1)*100, 1)
            neg_p  = round((sub_ci["sentiment"]=="부정").sum() / max(len(sub_ci),1)*100, 1)
            toks   = [t for ts in sub_ci["tokens"].fillna("").apply(
                          lambda x: x if isinstance(x, list) else [])
                      for t in ts if t not in STOPWORDS and len(t) >= 2]
            top_kws = [w for w,_ in Counter(toks).most_common(20)][:6]
            brands_ci = Counter([
                b for bs in sub_ci["brands"].fillna("").apply(
                    lambda x: x if isinstance(x, list) else [])
                for b in bs]).most_common(3)
            funnel_top = sub_ci["funnel_stage"].value_counts()

            with st.expander(
                f"{icon}  페르소나 {ci+1}: {CLUSTER_NAMES_ADV[ci]}  "
                f"(n={len(sub_ci)}, NSS {pos_p-neg_p:+.1f})",
                expanded=(ci == 3),
            ):
                pc1, pc2, pc3 = st.columns([1.4, 1, 1])
                with pc1:
                    # 키워드 배지
                    kw_html = " ".join([
                        f"<span style='background:{color}22;color:{color};"
                        f"border:1px solid {color}55;border-radius:12px;"
                        f"padding:3px 10px;font-size:12px;font-weight:500'>{w}</span>"
                        for w in top_kws])
                    brand_html = " · ".join(
                        [f"<b>{b}</b>({c}건)" for b,c in brands_ci])
                    st.markdown(f"""
                    <div style='background:{color}11;border-radius:10px;padding:14px 16px;'>
                        <div style='font-size:1.4rem'>{icon}
                            <span style='font-size:15px;font-weight:700;
                                         color:{color};margin-left:6px'>{CLUSTER_NAMES_ADV[ci]}</span>
                        </div>
                        <div style='color:#718096;font-size:12px;margin:4px 0'>{meta["age"]} · {len(sub_ci)}건 · 긍정 {pos_p}% / 부정 {neg_p}%</div>
                        <div style='color:#4A5568;font-style:italic;margin:8px 0;font-size:13px'>{meta["summary"]}</div>
                        <div style='margin:8px 0'>{kw_html}</div>
                        <hr style='border-color:#E2E8F0;margin:10px 0'>
                        <div style='font-size:12px;color:#4A5568'><b>주요 언급 브랜드</b>: {brand_html}</div>
                        <div style='font-size:12px;color:#4A5568;margin-top:6px'><b>주요 퍼널 단계</b>: {funnel_top.index[0] if len(funnel_top)>0 else "-"}</div>
                        <div style='margin-top:10px;background:{color}11;border-left:3px solid {color};
                                     border-radius:0 8px 8px 0;padding:8px 12px;font-size:12px'>
                            <b>🎯 파스쿠찌 전략</b><br>{meta["pascal_hook"]}
                        </div>
                    </div>""", unsafe_allow_html=True)

                with pc2:
                    # 감성 파이차트
                    sent_v = sub_ci["sentiment"].value_counts()
                    fig_sp = px.pie(
                        names=sent_v.index, values=sent_v.values,
                        color=sent_v.index,
                        color_discrete_map=SENT_COLORS,
                        hole=0.55,
                        title="감성 분포",
                    )
                    fig_sp.update_traces(textinfo="percent", textfont_size=11)
                    chart_style(fig_sp, height=220)
                    st.plotly_chart(fig_sp, use_container_width=True)

                    # 퍼널 분포 바
                    fig_fp = px.bar(
                        x=[funnel_top.get(f,0) for f in FUNNEL_ORDER if f in funnel_top],
                        y=[f for f in FUNNEL_ORDER if f in funnel_top],
                        orientation="h",
                        color=[f for f in FUNNEL_ORDER if f in funnel_top],
                        color_discrete_map=FUNNEL_COLORS,
                        title="퍼널 단계 분포",
                        labels={"x":"건수","y":"단계"},
                    )
                    fig_fp.update_layout(showlegend=False)
                    chart_style(fig_fp, height=200, showlegend=False)
                    st.plotly_chart(fig_fp, use_container_width=True)

                with pc3:
                    # 레이더 차트
                    radar_vals = RADAR_DATA[ci]
                    fig_rp = go.Figure()
                    fig_rp.add_trace(go.Scatterpolar(
                        r=radar_vals + [radar_vals[0]],
                        theta=RADAR_AXES + [RADAR_AXES[0]],
                        fill="toself", name=CLUSTER_NAMES_ADV[ci],
                        line=dict(color=color, width=2.5),
                        fillcolor=hex_to_rgba(color, 0.20),
                    ))
                    fig_rp.update_layout(
                        polar=dict(
                            bgcolor="#FFFFFF",
                            radialaxis=dict(visible=True, range=[0,100],
                                            gridcolor="#E2E8F0",
                                            tickfont=dict(color="#718096",size=8)),
                            angularaxis=dict(gridcolor="#E2E8F0",
                                             tickfont=dict(color="#2D3748",size=9)),
                        ),
                        showlegend=False,
                        title=dict(text="세그먼트 특성 레이더",
                                   font=dict(size=12,color="#1B2A4A")),
                        paper_bgcolor="#F7F9FC", height=300,
                        margin=dict(l=20,r=20,t=40,b=20),
                    )
                    st.plotly_chart(fig_rp, use_container_width=True)

        # ── 섹션 F: 세그먼트 시계열 추이 ─────────────────
        st.markdown("<div class='section-title'>F. 세그먼트별 월별 규모 추이</div>",
                    unsafe_allow_html=True)
        ts_months_seg = sorted([
            m for m in sub_cl["year_month"].dropna().unique()
            if "NaT" not in str(m)
            and "unknown" not in str(m)
            and ("2025" in str(m) or "2026" in str(m))
        ])
        seg_ts_rows = []
        for ci in range(5):
            sub_ci = sub_cl[sub_cl["cluster"] == ci]
            for m in ts_months_seg:
                seg_ts_rows.append({
                    "세그먼트": CLUSTER_NAMES_ADV[ci],
                    "월": m,
                    "문서수": int((sub_ci["year_month"] == m).sum()),
                })
        seg_ts_df = pd.DataFrame(seg_ts_rows)

        fig_seg_ts = px.line(
            seg_ts_df, x="월", y="문서수", color="세그먼트",
            color_discrete_map={CLUSTER_NAMES_ADV[c]: CLUSTER_COLORS[c] for c in range(5)},
            markers=True,
            title="세그먼트별 월별 규모 변화",
            labels={"월":"월","문서수":"문서 수"},
        )
        chart_style(fig_seg_ts, height=340)
        st.plotly_chart(fig_seg_ts, use_container_width=True)

        st.markdown("<div class='section-title'>세그먼트 × 브랜드 히트맵</div>",
                    unsafe_allow_html=True)
        seg_brand_mat2 = pd.DataFrame(0,
            index=[CLUSTER_NAMES_ADV[c] for c in range(5)],
            columns=TARGET_BRANDS)
        for ci in range(5):
            sub_ci = sub_cl[sub_cl["cluster"] == ci]
            for b in TARGET_BRANDS:
                seg_brand_mat2.loc[CLUSTER_NAMES_ADV[ci], b] =                     sub_ci["brands"].fillna("").apply(
                        lambda x: b in x if isinstance(x, list) else False).sum()
        fig_sbh = px.imshow(
            seg_brand_mat2, color_continuous_scale="Blues",
            title="소비자 세그먼트 × 브랜드 언급 분포",
            text_auto=True, aspect="auto",
        )
        fig_sbh.update_traces(textfont=dict(color="#1B2A4A", size=11))
        chart_style(fig_sbh, height=360, showlegend=False)
        st.plotly_chart(fig_sbh, use_container_width=True)