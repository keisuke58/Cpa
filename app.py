import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date, timedelta
import json
import os

# Set page config
st.set_page_config(page_title="CPA Perfect Platform 2027", layout="wide", page_icon="📚")

# Data Persistence
DATA_FILE = "cpa_data.json"

def load_data():
    defaults = {"scores": [], "logs": [], "xp": 0, "level": 1, "badges": [], "wrong_answers": [], "retry": []}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                # Merge defaults for backward compatibility
                for k, v in defaults.items():
                    if k not in data:
                        data[k] = v
                return data
            except:
                return defaults
    return defaults

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Initialize Session State
if 'data' not in st.session_state:
    st.session_state.data = load_data()

if 'quiz_state' not in st.session_state:
    st.session_state.quiz_state = {
        'active': False,
        'subject': None,
        'level': None,
        'q_index': 0,
        'score': 0,
        'show_feedback': False,
        'selected_option': None
    }

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4e8cff;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
    .correct-answer {
        background-color: #d1fae5;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #10b981;
        color: #065f46;
    }
    .incorrect-answer {
        background-color: #fee2e2;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ef4444;
        color: #991b1b;
    }
</style>
""", unsafe_allow_html=True)

# Mock Data
mock_exams = [
    {'date': '2026-11-15', 'type': 'Short', 'name': 'Dec Short Mock (TAC/Ohara)', 'provider': 'TAC/Ohara', 'status': 'Practice'},
    {'date': '2026-12-13', 'type': 'Short', 'name': 'Official Dec Short Exam', 'provider': 'CPAAOB', 'status': 'Target'},
    {'date': '2027-04-25', 'type': 'Short', 'name': 'May Short Mock (TAC/Ohara)', 'provider': 'TAC/Ohara', 'status': 'Practice'},
    {'date': '2027-05-23', 'type': 'Short', 'name': 'Official May Short Exam', 'provider': 'CPAAOB', 'status': 'Target'},
    {'date': '2027-07-10', 'type': 'Essay', 'name': 'Essay Mock (TAC/Ohara)', 'provider': 'TAC/Ohara', 'status': 'Practice'},
    {'date': '2027-08-20', 'type': 'Essay', 'name': 'Official Aug Essay Exam', 'provider': 'CPAAOB', 'status': 'Target'}
]

default_official_schedule = [
    # Short I (Dec) 2026
    {'date': '2026-12-13', 'category': 'Exam', 'event': '短答式 第I回（12月） 試験', 'notes': '企業法/管理/監査/財務（500点満点）'},
    {'date': '2027-01-20', 'category': 'Result', 'event': '短答式 第I回 合格発表（目安）', 'notes': '公式発表時刻に従う・目安日付'},
    # Short II (May) 2027
    {'date': '2027-05-23', 'category': 'Exam', 'event': '短答式 第II回（5月） 試験', 'notes': '目標：同年の論文へ'},
    {'date': '2027-06-20', 'category': 'Result', 'event': '短答式 第II回 合格発表（目安）', 'notes': '公式発表時刻に従う・目安日付'},
    # Essay 2027
    {'date': '2027-08-20', 'category': 'Exam', 'event': '論文式 試験', 'notes': '2日間科目・配点に注意'},
    {'date': '2027-11-15', 'category': 'Result', 'event': '論文式 合格発表（目安）', 'notes': '例年11月頃発表・目安日付'}
]

official_schedule = st.session_state.data.get('official_schedule', default_official_schedule)
# Vocabulary Data
def load_vocab_data():
    vocab_path = "assets/vocab.json"
    if os.path.exists(vocab_path):
        with open(vocab_path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

vocab_data = load_vocab_data()

def load_formulas_data():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "formulas.json")
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

formulas_data = load_formulas_data()

def save_formulas_data(data):
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "formulas.json")
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def seed_top10_examples():
    top10 = {
        "Future Value (Single Sum)": {
            "example_ja": "例: PV=1,000、r=5%、n=3年 ⇒ FV = 1,000×(1.05)^3 ≈ 1,157.63",
            "example_en": "Example: PV=1,000, r=5%, n=3 ⇒ FV = 1,000×(1.05)^3 ≈ 1,157.63",
            "problem_ja": "問題: PV=200、r=8%、n=4年 の将来価値FVは？",
            "problem_en": "Problem: Find FV for PV=200, r=8%, n=4.",
            "solution_ja": "解答: FV = 200×(1.08)^4 ≈ 272.1",
            "solution_en": "Solution: FV = 200×(1.08)^4 ≈ 272.1"
        },
        "Present Value (Single Sum)": {
            "example_ja": "例: FV=1,000、r=6%、n=2年 ⇒ PV = 1,000 ÷ (1.06)^2 ≈ 890.0",
            "example_en": "Example: FV=1,000, r=6%, n=2 ⇒ PV = 1,000/(1.06)^2 ≈ 890.0",
            "problem_ja": "問題: FV=500、r=10%、n=3年 の現在価値PVは？",
            "problem_en": "Problem: Find PV for FV=500, r=10%, n=3.",
            "solution_ja": "解答: PV ≈ 500 ÷ 1.331 ≈ 375.7",
            "solution_en": "Solution: PV ≈ 500/1.331 ≈ 375.7"
        },
        "Present Value of Annuity": {
            "example_ja": "例: P=100、r=5%、n=4 ⇒ PVA = 100×[1 − (1.05)^(−4)] ÷ 0.05 ≈ 354.6",
            "example_en": "Example: P=100, r=5%, n=4 ⇒ PVA ≈ 354.6",
            "problem_ja": "問題: P=50、r=6%、n=3 の年金現在価値PVAは？",
            "problem_en": "Problem: Find PVA for P=50, r=6%, n=3.",
            "solution_ja": "解答: PVA ≈ 50×[1 − (1.06)^(−3)] ÷ 0.06 ≈ 133.7",
            "solution_en": "Solution: PVA ≈ 50×[1 − 1.06^(−3)]/0.06 ≈ 133.7"
        },
        "Contribution Margin": {
            "example_ja": "例: 売上1,000、変動費600 ⇒ 限界利益CM = 400",
            "example_en": "Example: Sales=1,000, Variable=600 ⇒ CM=400",
            "problem_ja": "問題: 単価20、変動費/単位12、数量200 ⇒ 限界利益は？",
            "problem_en": "Problem: Price=20, Var/unit=12, Units=200 ⇒ CM?",
            "solution_ja": "解答: 単位CM=8、合計CM=8×200=1,600",
            "solution_en": "Solution: Unit CM=8; Total CM=8×200=1,600"
        },
        "Break-even Units": {
            "example_ja": "例: 固定費1,200、単価20、変動費12 ⇒ BEQ=1,200÷(20−12)=150単位",
            "example_en": "Example: Fixed=1,200, Price=20, Var=12 ⇒ BEQ=150 units",
            "problem_ja": "問題: 固定費5,000、単価50、変動費30 ⇒ BEQは？",
            "problem_en": "Problem: Fixed=5,000, Price=50, Var=30 ⇒ BEQ?",
            "solution_ja": "解答: BEQ=5,000 ÷ (50−30)=250単位",
            "solution_en": "Solution: BEQ=5,000/(50−30)=250 units"
        },
        "Net Present Value": {
            "example_ja": "例: CF0=-1,000、CF1-3=400、r=8% ⇒ NPV ≈ 30.8（正、採用）",
            "example_en": "Example: CF0=-1,000, CF1-3=400, r=8% ⇒ NPV ≈ 30.8",
            "problem_ja": "問題: CF0=-2,000、CF1-4=600、r=10% ⇒ NPVは？",
            "problem_en": "Problem: CF0=-2,000, CF1-4=600, r=10% ⇒ NPV?",
            "solution_ja": "解答: 600×[(1−1.1^(−4))/0.1]−2,000 ≈ -98.1",
            "solution_en": "Solution: 600×[(1−1.1^(−4))/0.1]−2,000 ≈ -98.1"
        },
        "WACC": {
            "example_ja": "例: w_e=0.6, w_d=0.4, k_e=10%, k_d=5%, T=30% ⇒ WACC=7.4%",
            "example_en": "Example: we=0.6, wd=0.4, ke=10%, kd=5%, T=30% ⇒ WACC=7.4%",
            "problem_ja": "問題: w_e=0.7, w_d=0.3, k_e=12%, k_d=4%, T=25% ⇒ WACCは？",
            "problem_en": "Problem: we=0.7, wd=0.3, ke=12%, kd=4%, T=25% ⇒ WACC?",
            "solution_ja": "解答: 0.7×0.12 + 0.3×0.04×(1−0.25)=9.3%",
            "solution_en": "Solution: 0.7×0.12 + 0.3×0.04×(1−0.25)=9.3%"
        },
        "CAPM Cost of Equity": {
            "example_ja": "例: Rf=2%、β=1.2、(Rm−Rf)=5% ⇒ k_e=8%",
            "example_en": "Example: Rf=2%, β=1.2, (Rm−Rf)=5% ⇒ ke=8%",
            "problem_ja": "問題: Rf=1%、β=0.8、Rm=6% ⇒ k_eは？",
            "problem_en": "Problem: Rf=1%, β=0.8, Rm=6% ⇒ ke?",
            "solution_ja": "解答: MRP=5%、k_e=1%+0.8×5%=5%",
            "solution_en": "Solution: MRP=5%, ke=1%+0.8×5%=5%"
        },
        "ROE": {
            "example_ja": "例: 当期純利益120、平均自己資本1,000 ⇒ ROE=12%",
            "example_en": "Example: NI=120, Avg Equity=1,000 ⇒ ROE=12%",
            "problem_ja": "問題: 当期純利益80、平均自己資本400 ⇒ ROEは？",
            "problem_en": "Problem: NI=80, Avg Equity=400 ⇒ ROE?",
            "solution_ja": "解答: 80 ÷ 400 = 20%",
            "solution_en": "Solution: 80/400 = 20%"
        },
        "DuPont ROE": {
            "example_ja": "例: NPM=10%、TAT=1.5、EM=2 ⇒ ROE=30%",
            "example_en": "Example: NPM=10%, TAT=1.5, EM=2 ⇒ ROE=30%",
            "problem_ja": "問題: NPM=8%、TAT=1.2、EM=1.8 ⇒ ROEは？",
            "problem_en": "Problem: NPM=8%, TAT=1.2, EM=1.8 ⇒ ROE?",
            "solution_ja": "解答: 0.08×1.2×1.8=0.1728 ⇒ 17.28%",
            "solution_en": "Solution: 0.08×1.2×1.8=0.1728 ⇒ 17.28%"
        }
    }
    # Also seed for Annuity Due PV/FV if present
    top10.update({
        "Annuity Due PV": {
            "example_ja": "例: P=100、r=5%、n=3 ⇒ PVA_due = 100×[(1−1.05^(−3))/0.05]×(1.05) ≈ 286.98",
            "example_en": "Example: P=100, r=5%, n=3 ⇒ PVA_due ≈ 286.98",
            "problem_ja": "問題: P=50、r=6%、n=4 の年金現価（期首払い）は？",
            "problem_en": "Problem: Find annuity-due present value for P=50, r=6%, n=4.",
            "solution_ja": "解答: PVA_due = 50×[(1−1.06^(−4))/0.06]×1.06 ≈ 183.6",
            "solution_en": "Solution: PVA_due = 50×[(1−1.06^(−4))/0.06]×1.06 ≈ 183.6"
        },
        "Annuity Due FV": {
            "example_ja": "例: P=100、r=5%、n=3 ⇒ FVA_due = 100×[(1.05^3−1)/0.05]×(1.05) ≈ 331.0",
            "example_en": "Example: P=100, r=5%, n=3 ⇒ FVA_due ≈ 331.0",
            "problem_ja": "問題: P=80、r=4%、n=5 の年金将来価値（期首払い）は？",
            "problem_en": "Problem: Find annuity-due future value for P=80, r=4%, n=5.",
            "solution_ja": "解答: FVA_due = 80×[(1.04^5−1)/0.04]×1.04 ≈ 433.0",
            "solution_en": "Solution: FVA_due = 80×[(1.04^5−1)/0.04]×1.04 ≈ 433.0"
        }
    })
    changed = False
    for i, item in enumerate(formulas_data):
        name = item.get("name", "")
        if name in top10:
            for k, v in top10[name].items():
                if formulas_data[i].get(k) in (None, "", []):
                    formulas_data[i][k] = v
                    changed = True
    if changed:
        save_formulas_data(formulas_data)

def _sanitize_text(v):
    try:
        if v is None:
            return ""
        # Handle numpy/pandas NaN
        try:
            import pandas as _pd
            if _pd.isna(v):
                return ""
        except Exception:
            pass
        if isinstance(v, str) and v.strip().lower() == "nan":
            return ""
        return v
    except Exception:
        return ""

def seed_all_formulas():
    changed = False
    for i, item in enumerate(formulas_data):
        name = str(item.get("name", "")).strip()
        cat = str(item.get("category", "")).strip()
        ex_ja = _sanitize_text(item.get("example_ja", ""))
        ex_en = _sanitize_text(item.get("example_en", ""))
        pb_ja = _sanitize_text(item.get("problem_ja", ""))
        pb_en = _sanitize_text(item.get("problem_en", ""))
        so_ja = _sanitize_text(item.get("solution_ja", ""))
        so_en = _sanitize_text(item.get("solution_en", ""))
        if not ex_ja and not ex_en and not pb_ja and not pb_en and not so_ja and not so_en:
            nl = name.lower()
            if "eoq" in nl or "economic order quantity" in nl:
                ex_ja = "例: 年需要D=12,000、発注費S=100、在庫費H=2 ⇒ EOQ=√(2×12,000×100/2)≈1,095"
                ex_en = "Example: D=12,000/yr, S=100/order, H=2/unit/yr ⇒ EOQ≈1,095"
                pb_ja = "問題: D=36,000、S=80、H=4 のEOQは？"
                pb_en = "Problem: Find EOQ for D=36,000, S=80, H=4."
                so_ja = "解答: EOQ=√(2×36,000×80/4)=√1,440,000≈1,200"
                so_en = "Solution: EOQ=√(2×36,000×80/4)=√1,440,000≈1,200"
            elif "reorder point" in nl or "rop" in nl:
                ex_ja = "例: 需要日量d=50、リードタイムL=6、 安全在庫SS=100 ⇒ ROP=50×6+100=400"
                ex_en = "Example: d=50/day, L=6 days, SS=100 ⇒ ROP=400"
                pb_ja = "問題: d=80、L=5、SS=60 のROPは？"
                pb_en = "Problem: Find ROP for d=80, L=5, SS=60."
                so_ja = "解答: ROP=80×5+60=460"
                so_en = "Solution: ROP=80×5+60=460"
            elif "safety stock" in nl:
                ex_ja = "例: σL=40、Z=1.65 ⇒ SS=1.65×40=66"
                ex_en = "Example: σL=40, Z=1.65 ⇒ SS=66"
                pb_ja = "問題: σL=30、Z=1.96 の安全在庫は？"
                pb_en = "Problem: Find SS for σL=30, Z=1.96."
                so_ja = "解答: SS=1.96×30=58.8≈59"
                so_en = "Solution: SS=1.96×30=58.8≈59"
            elif "material price variance" in nl or "mpv" in nl:
                ex_ja = "例: AQ=1,000kg、AP=¥6、SP=¥5 ⇒ MPV=1,000×(6−5)=1,000不利"
                ex_en = "Example: AQ=1,000kg, AP=6, SP=5 ⇒ MPV=1,000 U"
                pb_ja = "問題: AQ=800、AP=¥4.8、SP=¥5.0 のMPVは？"
                pb_en = "Problem: Find MPV for AQ=800, AP=4.8, SP=5.0."
                so_ja = "解答: 800×(4.8−5.0)=−160 有利"
                so_en = "Solution: 800×(4.8−5.0)=−160 F"
            elif "material quantity variance" in nl or "mqv" in nl or "usage variance" in nl:
                ex_ja = "例: SP=¥5、AQ=1,100kg、SQ=1,000kg ⇒ MQV=5×(1,100−1,000)=500不利"
                ex_en = "Example: SP=5, AQ=1,100, SQ=1,000 ⇒ MQV=500 U"
                pb_ja = "問題: SP=¥4、AQ=950、SQ=1,000 のMQVは？"
                pb_en = "Problem: Find MQV for SP=4, AQ=950, SQ=1,000."
                so_ja = "解答: 4×(950−1,000)=−200 有利"
                so_en = "Solution: 4×(950−1,000)=−200 F"
            elif "labor rate variance" in nl or "lrv" in nl:
                ex_ja = "例: AH=1,200h、AR=¥12、SR=¥10 ⇒ LRV=1,200×(12−10)=2,400不利"
                ex_en = "Example: AH=1,200h, AR=12, SR=10 ⇒ LRV=2,400 U"
                pb_ja = "問題: AH=900、AR=¥9.5、SR=¥10 のLRVは？"
                pb_en = "Problem: Find LRV for AH=900, AR=9.5, SR=10."
                so_ja = "解答: 900×(9.5−10)=−450 有利"
                so_en = "Solution: 900×(9.5−10)=−450 F"
            elif "labor efficiency variance" in nl or "lev" in nl:
                ex_ja = "例: SR=¥10、AH=1,200h、SH=1,000h ⇒ LEV=10×(1,200−1,000)=2,000不利"
                ex_en = "Example: SR=10, AH=1,200, SH=1,000 ⇒ LEV=2,000 U"
                pb_ja = "問題: SR=¥12、AH=800、SH=850 のLEVは？"
                pb_en = "Problem: Find LEV for SR=12, AH=800, SH=850."
                so_ja = "解答: 12×(800−850)=−600 有利"
                so_en = "Solution: 12×(800−850)=−600 F"
            elif "straight-line" in nl or "定額" in nl:
                ex_ja = "例: 原価1,000、残存100、耐用年数5 ⇒ 年額=(1,000−100)/5=180"
                ex_en = "Example: Cost=1,000, Salvage=100, Life=5 ⇒ Annual=180"
                pb_ja = "問題: 原価800、残存0、耐用年数4 の年額は？"
                pb_en = "Problem: Find annual SL depreciation for Cost=800, Salvage=0, Life=4."
                so_ja = "解答: 800/4=200"
                so_en = "Solution: 800/4=200"
            elif "declining" in nl or "double-declining" in nl or "定率" in nl:
                ex_ja = "例: 原価1,000、耐用年数5、率=40% ⇒ 1年目=400、2年目=(1,000−400)×0.4=240"
                ex_en = "Example: Cost=1,000, Life=5, Rate=40% ⇒ Y1=400, Y2=240"
                pb_ja = "問題: 原価900、寿命3、率=2/3 の1年目減価は？"
                pb_en = "Problem: Cost=900, Life=3, Rate=2/3: Year 1 depreciation?"
                so_ja = "解答: 900×(2/3)=600"
                so_en = "Solution: 900×(2/3)=600"
            elif "sum-of-the-years" in nl or "syd" in nl:
                ex_ja = "例: 原価1,000、残存100、寿命5、合計=15 ⇒ 1年目=(5/15)×900=300"
                ex_en = "Example: Cost=1,000, Salvage=100, Life=5, Sum=15 ⇒ Y1=300"
                pb_ja = "問題: 原価600、残存60、寿命4、合計=10 の2年目は？"
                pb_en = "Problem: Cost=600, Salvage=60, Life=4, Sum=10: Year 2?"
                so_ja = "解答: (3/10)×540=162"
                so_en = "Solution: (3/10)×540=162"
            elif "units of production" in nl or "production-output" in nl:
                ex_ja = "例: 原価1,000、残存100、総見積50,000u ⇒ 率=(900/50,000)=0.018/u"
                ex_en = "Example: Cost=1,000, Salvage=100, Total 50,000u ⇒ Rate=0.018/u"
                pb_ja = "問題: 当期生産4,000u の減価は？"
                pb_en = "Problem: Find depreciation for 4,000 units."
                so_ja = "解答: 0.018×4,000=72"
                so_en = "Solution: 0.018×4,000=72"
            elif "profitability index" in nl or " pi " in nl or nl.endswith(" pi"):
                ex_ja = "例: 流入PV=1,200、初期投資=1,000 ⇒ PI=1.2（採用）"
                ex_en = "Example: PV inflows=1,200, Initial=1,000 ⇒ PI=1.2 (accept)"
                pb_ja = "問題: PV流入=900、投資=1,000 のPIは？採否は？"
                pb_en = "Problem: PV inflows=900, investment=1,000 ⇒ PI? Accept?"
                so_ja = "解答: 0.9、1未満のため不採用"
                so_en = "Solution: 0.9; below 1, reject"
            elif "payback" in nl:
                ex_ja = "例: 初期投資1,000、毎年CF=250 ⇒ 回収期間=4年"
                ex_en = "Example: Initial 1,000, annual CF=250 ⇒ Payback=4 years"
                pb_ja = "問題: 初期投資1,200、年CF=300 ⇒ 回収期間は？"
                pb_en = "Problem: Initial 1,200, annual CF=300 ⇒ Payback?"
                so_ja = "解答: 1,200/300=4年"
                so_en = "Solution: 1,200/300=4 years"
            elif "perpetuity" in nl and "growing" not in nl:
                ex_ja = "例: C=100、r=5% ⇒ PV=100/0.05=2,000"
                ex_en = "Example: C=100, r=5% ⇒ PV=100/0.05=2,000"
                pb_ja = "問題: C=60、r=4% の永久年金PVは？"
                pb_en = "Problem: C=60, r=4% ⇒ PV?"
                so_ja = "解答: 60/0.04=1,500"
                so_en = "Solution: 60/0.04=1,500"
            elif ("growing perpetuity" in nl) or ("gordon" in nl) or ("ddm" in nl) or ("dividend discount" in nl):
                ex_ja = "例: D1=2、k=8%、g=3% ⇒ P0=2/(0.08−0.03)=40"
                ex_en = "Example: D1=2, k=8%, g=3% ⇒ P0=2/(0.08−0.03)=40"
                pb_ja = "問題: D1=3、k=10%、g=4% のP0は？"
                pb_en = "Problem: D1=3, k=10%, g=4% ⇒ P0?"
                so_ja = "解答: 3/(0.10−0.04)=50"
                so_en = "Solution: 3/(0.10−0.04)=50"
            elif "current ratio" in nl:
                ex_ja = "例: 流動資産=500、流動負債=250 ⇒ 2.0倍"
                ex_en = "Example: CA=500, CL=250 ⇒ 2.0x"
                pb_ja = "問題: CA=360、CL=300 の流動比率は？"
                pb_en = "Problem: CA=360, CL=300 ⇒ current ratio?"
                so_ja = "解答: 360/300=1.2倍"
                so_en = "Solution: 360/300=1.2x"
            elif "quick ratio" in nl or "acid-test" in nl:
                ex_ja = "例: 当座資産=300、流動負債=200 ⇒ 1.5倍"
                ex_en = "Example: Quick assets=300, CL=200 ⇒ 1.5x"
                pb_ja = "問題: QA=180、CL=240 の当座比率は？"
                pb_en = "Problem: QA=180, CL=240 ⇒ quick ratio?"
                so_ja = "解答: 180/240=0.75倍"
                so_en = "Solution: 180/240=0.75x"
            elif "debt-to-equity" in nl or "debt to equity" in nl or "d/e" in nl:
                ex_ja = "例: 負債=600、自己資本=400 ⇒ D/E=1.5"
                ex_en = "Example: Debt=600, Equity=400 ⇒ D/E=1.5"
                pb_ja = "問題: 負債=750、自己資本=500 のD/Eは？"
                pb_en = "Problem: Debt=750, Equity=500 ⇒ D/E?"
                so_ja = "解答: 750/500=1.5"
                so_en = "Solution: 750/500=1.5"
            elif "times interest earned" in nl or "interest coverage" in nl:
                ex_ja = "例: EBIT=300、利息=60 ⇒ TIE=5倍"
                ex_en = "Example: EBIT=300, Interest=60 ⇒ TIE=5x"
                pb_ja = "問題: EBIT=240、利息=80 のTIEは？"
                pb_en = "Problem: EBIT=240, Interest=80 ⇒ TIE?"
                so_ja = "解答: 240/80=3倍"
                so_en = "Solution: 240/80=3x"
            elif "inventory turnover" in nl:
                ex_ja = "例: 売上原価=1,200、平均在庫=300 ⇒ 回転=4.0"
                ex_en = "Example: COGS=1,200, Avg Inv=300 ⇒ Turnover=4.0"
                pb_ja = "問題: COGS=900、平均在庫=225 ⇒ 回転は？"
                pb_en = "Problem: COGS=900, Avg Inv=225 ⇒ turnover?"
                so_ja = "解答: 900/225=4.0"
                so_en = "Solution: 900/225=4.0"
            elif "days sales outstanding" in nl or "dso" in nl or "receivables turnover" in nl:
                ex_ja = "例: 売掛回転=12 ⇒ DSO≈365/12≈30.4日"
                ex_en = "Example: AR turnover=12 ⇒ DSO≈365/12≈30.4 days"
                pb_ja = "問題: AR回転=10 のDSOは？"
                pb_en = "Problem: AR turnover=10 ⇒ DSO?"
                so_ja = "解答: 365/10=36.5日"
                so_en = "Solution: 365/10=36.5 days"
            elif "days inventory outstanding" in nl or "dio" in nl:
                ex_ja = "例: 在庫回転=8 ⇒ DIO≈365/8≈45.6日"
                ex_en = "Example: Inventory turnover=8 ⇒ DIO≈365/8≈45.6 days"
                pb_ja = "問題: 在庫回転=5 のDIOは？"
                pb_en = "Problem: Inventory turnover=5 ⇒ DIO?"
                so_ja = "解答: 365/5=73日"
                so_en = "Solution: 365/5=73 days"
            elif "cash conversion cycle" in nl or "ccc" in nl:
                ex_ja = "例: DIO=50、DSO=35、DPO=40 ⇒ CCC=45日"
                ex_en = "Example: DIO=50, DSO=35, DPO=40 ⇒ CCC=45 days"
                pb_ja = "問題: DIO=60、DSO=30、DPO=50 のCCCは？"
                pb_en = "Problem: DIO=60, DSO=30, DPO=50 ⇒ CCC?"
                so_ja = "解答: 60+30−50=40日"
                so_en = "Solution: 60+30−50=40 days"
            elif "gross margin" in nl or "operating margin" in nl or "net profit margin" in nl:
                ex_ja = "例: 利益=120、売上=1,000 ⇒ マージン=12%"
                ex_en = "Example: Profit=120, Sales=1,000 ⇒ margin=12%"
                pb_ja = "問題: 利益=90、売上=750 のマージンは？"
                pb_en = "Problem: Profit=90, Sales=750 ⇒ margin?"
                so_ja = "解答: 90/750=12%"
                so_en = "Solution: 90/750=12%"
            elif "present value" in name.lower() or "future value" in name.lower() or "annuity" in name.lower():
                ex_ja = f"例: 仮に r=5%、期間 n=3、適切な金額を代入して計算してください。"
                ex_en = f"Example: Assume r=5%, n=3; plug suitable amounts and compute."
                pb_ja = f"問題: {name} を用いて金額を求めよ。"
                pb_en = f"Problem: Use {name} to find the requested amount."
                so_ja = f"解答: 数式に代入し、四捨五入して数値を示す。"
                so_en = f"Solution: Substitute into the formula and present the rounded value."
            elif "wacc" in name.lower() or "capm" in name.lower() or "npv" in name.lower() or "irr" in name.lower():
                ex_ja = "例: Rf, β, MRP または キャッシュフロー列 と 割引率 を仮定して計算。"
                ex_en = "Example: Assume Rf, β, MRP or CF series and a discount rate to compute."
                pb_ja = f"問題: {name} を計算し、採否を判断せよ（該当する場合）。"
                pb_en = f"Problem: Compute {name} and decide accept/reject if applicable."
                so_ja = "解答: 与えられた数値を代入し、式に従って算出。"
                so_en = "Solution: Substitute the provided values and evaluate per the formula."
            elif "roe" in name.lower() or "roa" in name.lower() or "ratio" in name.lower():
                ex_ja = "例: 分子と分母の数値を仮定し、比率を算出。"
                ex_en = "Example: Assume numerator and denominator values and compute the ratio."
                pb_ja = f"問題: {name} を計算し、解釈を述べよ。"
                pb_en = f"Problem: Calculate {name} and interpret the result."
                so_ja = "解答: 代入してパーセンテージで表示。"
                so_en = "Solution: Substitute values and present as a percentage."
            elif "break-even" in name.lower() or "contribution" in name.lower() or "variance" in name.lower():
                ex_ja = "例: 単価・変動費・固定費（または実績と標準）を仮定して指標を計算。"
                ex_en = "Example: Assume price, variable, fixed costs (or actual vs. standard) and compute."
                pb_ja = f"問題: {name} を算出し、意思決定を示せ。"
                pb_en = f"Problem: Compute {name} and state the decision implication."
                so_ja = "解答: 指定式に代入し、単位数または差額を導出。"
                so_en = "Solution: Substitute into the specified formula and derive units or variance."
            else:
                ex_ja = f"例: 「{name}」の簡単な数値例を記入。"
                ex_en = f"Example: Provide a simple numeric example for \"{name}\"."
                pb_ja = "問題: 数値を設定し、未知数を求めよ。"
                pb_en = "Problem: Set numbers and solve for the unknown."
                so_ja = "解答: 式へ代入し計算結果を提示。"
                so_en = "Solution: Substitute into the formula and show the result."
            formulas_data[i]["example_ja"] = ex_ja
            formulas_data[i]["example_en"] = ex_en
            formulas_data[i]["problem_ja"] = pb_ja
            formulas_data[i]["problem_en"] = pb_en
            formulas_data[i]["solution_ja"] = so_ja
            formulas_data[i]["solution_en"] = so_en
            changed = True
        else:
            if not ex_ja:
                formulas_data[i]["example_ja"] = ex_ja
            if not ex_en:
                formulas_data[i]["example_en"] = ex_en
            if not pb_ja:
                formulas_data[i]["problem_ja"] = pb_ja
            if not pb_en:
                formulas_data[i]["problem_en"] = pb_en
            if not so_ja:
                formulas_data[i]["solution_ja"] = so_ja
            if not so_en:
                formulas_data[i]["solution_en"] = so_en
    if changed:
        save_formulas_data(formulas_data)

def _is_missing_text(v):
    try:
        if v is None:
            return True
        try:
            import pandas as _pd
            if _pd.isna(v):
                return True
        except Exception:
            pass
        if isinstance(v, str) and v.strip().lower() == "nan":
            return True
        if isinstance(v, str) and v.strip() == "":
            return True
        return False
    except Exception:
        return True

def seed_latex_formulas():
    mapping = {
        "future value (single sum)": r"FV = PV\\times(1+r)^{n}",
        "present value (single sum)": r"PV = \\dfrac{FV}{(1+r)^{n}}",
        "present value of annuity": r"PVA = P\\times\\dfrac{1-(1+r)^{-n}}{r}",
        "future value of annuity": r"FVA = P\\times\\dfrac{(1+r)^{n}-1}{r}",
        "fv of annuity": r"FVA = P\\times\\dfrac{(1+r)^{n}-1}{r}",
        "pv of annuity": r"PVA = P\\times\\dfrac{1-(1+r)^{-n}}{r}",
        "present value (annuity due)": r"PVA_{\\text{due}} = P\\times\\dfrac{1-(1+r)^{-n}}{r}\\times(1+r)",
        "future value (annuity due)": r"FVA_{\\text{due}} = P\\times\\dfrac{(1+r)^{n}-1}{r}\\times(1+r)",
        "annuity due pv": r"PVA_{\\text{due}} = P\\times\\dfrac{1-(1+r)^{-n}}{r}\\times(1+r)",
        "annuity due fv": r"FVA_{\\text{due}} = P\\times\\dfrac{(1+r)^{n}-1}{r}\\times(1+r)",
        "pv of growing annuity": r"PV = P\\times\\dfrac{1 - \\left(\\dfrac{1+g}{1+r}\\right)^{n}}{r-g}",
        "pv of growing perpetuity": r"PV = \\dfrac{C_1}{r-g}",
        "present value of growing perpetuity": r"PV = \\dfrac{C_1}{r-g}",
        "growing annuity": r"PV = P\\times\\dfrac{1 - \\left(\\dfrac{1+g}{1+r}\\right)^{n}}{r-g}",
        "continuous compounding fv": r"FV = PV\\,e^{rt}",
        "continuous compounding pv": r"PV = FV\\,e^{-rt}",
        "contribution margin": r"CM = \\text{Sales} - \\text{Variable Costs}",
        "break-even units": r"Q_{BE} = \\dfrac{\\text{Fixed Costs}}{\\text{Price} - \\text{Variable Cost per Unit}}",
        "net present value": r"NPV = \\sum_{t=0}^{n} \\dfrac{CF_{t}}{(1+r)^{t}}",
        "wacc": r"WACC = w_e k_e + w_d k_d (1-T) + w_p k_p",
        "capm cost of equity": r"k_e = R_f + \\beta\\,(R_m - R_f)",
        "roe": r"ROE = \\dfrac{\\text{Net Income}}{\\text{Average Equity}}",
        "dupont roe": r"ROE = \\text{NPM}\\times\\text{TAT}\\times\\text{EM}",
        "irr": r"0 = \\sum_{t=0}^{n} \\dfrac{CF_{t}}{(1+IRR)^{t}}",
        "profitability index": r"PI = \\dfrac{\\text{PV of Inflows}}{\\text{Initial Investment}}",
        "payback period": r"\\text{Payback} = \\dfrac{\\text{Initial Investment}}{\\text{Annual Cash Flow}}",
        "present value of perpetuity": r"PV = \\dfrac{C}{r}",
        "gordon growth (ddm)": r"P_0 = \\dfrac{D_1}{k-g}",
        "pv of growing ddm": r"P_0 = \\dfrac{D_1}{k-g}",
        "current ratio": r"CR = \\dfrac{CA}{CL}",
        "quick ratio": r"QR = \\dfrac{\\text{Quick Assets}}{CL}",
        "debt-to-equity": r"\\dfrac{\\text{Debt}}{\\text{Equity}}",
        "times interest earned": r"TIE = \\dfrac{EBIT}{\\text{Interest}}",
        "inventory turnover": r"\\text{Turnover} = \\dfrac{COGS}{\\text{Average Inventory}}",
        "days sales outstanding": r"DSO = \\dfrac{365}{\\text{Receivables Turnover}}",
        "days inventory outstanding": r"DIO = \\dfrac{365}{\\text{Inventory Turnover}}",
        "cash conversion cycle": r"CCC = DIO + DSO - DPO",
        "gross profit margin": r"GPM = \\dfrac{\\text{Gross Profit}}{\\text{Sales}}",
        "operating margin": r"OM = \\dfrac{\\text{Operating Income}}{\\text{Sales}}",
        "net profit margin": r"NPM = \\dfrac{\\text{Net Income}}{\\text{Sales}}",
        "economic order quantity (eoq)": r"EOQ = \\sqrt{\\dfrac{2DS}{H}}",
        "reorder point": r"ROP = d\\times L + SS",
        "safety stock": r"SS = Z\\times\\sigma_{L}",
        "capm": r"k_e = R_f + \\beta\\,(R_m - R_f)",
        "effective annual rate": r"EAR = (1 + i/m)^{m} - 1",
        "future value of annuity (ordinary)": r"FVA = P\\times\\dfrac{(1+r)^{n}-1}{r}",
        "future value (annuity)": r"FVA = P\\times\\dfrac{(1+r)^{n}-1}{r}",
        "black–scholes d1": r"d_1 = \\dfrac{\\ln(S/K) + (r + \\tfrac{\\sigma^2}{2})T}{\\sigma\\sqrt{T}}",
        "black–scholes d2": r"d_2 = d_1 - \\sigma\\sqrt{T}",
        "black–scholes call price": r"C = S\\,N(d_1) - K e^{-rT} N(d_2)",
        "black–scholes put price": r"P = K e^{-rT} N(-d_2) - S\\,N(-d_1)",
        "call delta (bsm)": r"\\Delta_{call} = N(d_1)",
        "vega (bsm)": r"\\text{Vega} = S\\,\\phi(d_1)\\sqrt{T}",
        "receivables turnover": r"\\dfrac{\\text{Sales}}{\\overline{AR}}",
        "payables turnover": r"\\dfrac{COGS}{\\overline{AP}}"
    }
    changed = False
    for i, item in enumerate(formulas_data):
        nm = str(item.get("name", "")).strip().lower()
        cur = item.get("latex", "")
        if _is_missing_text(cur):
            # exact match
            if nm in mapping:
                formulas_data[i]["latex"] = mapping[nm]
                changed = True
            else:
                # substring fallback
                for key, tex in mapping.items():
                    if key in nm or nm in key:
                        formulas_data[i]["latex"] = tex
                        changed = True
                        break
    if changed:
        save_formulas_data(formulas_data)

seed_top10_examples()
seed_all_formulas()
seed_latex_formulas()

drill_questions = {
    'Financial': [
        {
            'level': 1,
            'q': "現金預金: 貸借対照表の「現金」に含まれないものはどれですか？",
            'options': ["紙幣 (Bank notes)", "硬貨 (Coins)", "郵便切手 (Postage stamps)", "当座預金 (Demand deposits)"],
            'correct': 2,
            'explanation': "郵便切手は「貯蔵品」または「通信費」として処理され、現金には含まれません。現金には通貨、小切手、当座預金などが含まれます。"
        },
        {
            'level': 1,
            'q': "減価償却: 資産の利用量に基づいて減価償却費を計算する方法はどれですか？",
            'options': ["定額法 (Straight-line)", "定率法 (Declining-balance)", "生産高比例法 (Production-output)", "級数法 (Sum-of-the-years'-digits)"],
            'correct': 2,
            'explanation': "生産高比例法は、総見積生産量に対する当期の実際生産量の割合に基づいて費用を配分する方法です。"
        },
        {
            'level': 1,
            'q': "棚卸資産: 物価上昇局面において、当期純利益が最も大きくなる評価方法はどれですか？",
            'options': ["先入先出法 (FIFO)", "後入先出法 (LIFO)", "移動平均法 (Weighted Average)", "個別法 (Specific Identification)"],
            'correct': 0,
            'explanation': "先入先出法(FIFO)では、過去の（安い）在庫が先に売上原価となり、期末在庫に直近の（高い）単価が残るため、売上原価が小さくなり利益が大きくなります。"
        },
        {
            'level': 1,
            'q': "資産除去債務: 資産除去債務は当初何をもって測定されますか？",
            'options': ["除去費用の将来価値", "除去費用の割引現在価値", "資産の取得原価", "資産の公正価値"],
            'correct': 1,
            'explanation': "資産除去債務は、将来発生すると見込まれる除去費用の「割引現在価値」で算定されます。"
        },
        {
            'level': 1,
            'q': "一般原則: 企業会計原則の「真実性の原則」における「真実」の意味として正しいものはどれですか？",
            'options': ["絶対的真実", "相対的真実", "形式的真実", "法的真実"],
            'correct': 1,
            'explanation': "企業会計は複数の会計処理の原則・手続の選択適用を認めているため、求められるのは「相対的真実」であると解されます。"
        },
        {
            'level': 1,
            'q': "減損会計: 固定資産の「回収可能価額」とは、どのように算定されますか？",
            'options': ["正味売却価額と使用価値のいずれか高い金額", "正味売却価額と使用価値のいずれか低い金額", "正味売却価額のみ", "使用価値のみ"],
            'correct': 0,
            'explanation': "回収可能価額は、資産の「正味売却価額」と「使用価値」のいずれか高い方の金額とされます。"
        },
        {
            'level': 1,
            'q': "リース会計: ファイナンス・リース取引において、借手が計上する資産の額は原則としていくらですか？",
            'options': ["リース料総額", "リース料総額の割引現在価値と貸手の購入価額等のいずれか低い額", "貸手の購入価額", "リース料総額の割引現在価値"],
            'correct': 1,
            'explanation': "通常のファイナンス・リースでは、リース料総額の現在価値と、貸手の購入価額（現金購入価額）のいずれか低い額で資産計上します。"
        },
        {
            'level': 2,
            'q': "キャッシュ・フロー計算書: 間接法において、税引前当期純利益からスタートする際、減価償却費はどう調整しますか？",
            'options': ["加算する", "減算する", "調整しない", "営業外収益として扱う"],
            'correct': 0,
            'explanation': "減価償却費は現金支出を伴わない費用（非資金損益）であるため、利益からスタートしてキャッシュフローを求める際は「加算」して戻します。"
        },
        {
            'level': 3,
            'q': "税効果会計: 繰延税金資産の回収可能性を判断する際、会社分類が「分類2」の企業において、スケジューリング可能な一時差異はいつまで計上可能ですか？",
            'options': ["1年以内", "5年以内", "スケジューリング可能な全期間", "計上できない"],
            'correct': 2,
            'explanation': "「分類2（業績が安定している企業）」の場合、スケジューリング可能な将来減算一時差異については、期間制限なく（全期間）回収可能性があると判断されます。"
        }
    ],
    'Management': [
        {
            'level': 1,
            'q': "CVP分析: 損益分岐点売上高を求める計算式はどれですか？",
            'options': ["固定費 ÷ 貢献利益率", "固定費 ÷ 変動費率", "変動費 ÷ 売上高", "利益 ÷ 売上高"],
            'correct': 0,
            'explanation': "損益分岐点売上高 ＝ 固定費 ÷ (1 － 変動費率) ＝ 固定費 ÷ 貢献利益率 です。"
        },
        {
            'level': 1,
            'q': "原価の分類: 「素価 (Prime Cost)」を構成するものはどれですか？",
            'options': ["直接材料費 ＋ 直接労務費", "直接労務費 ＋ 製造間接費", "直接材料費 ＋ 製造間接費", "販売費及び一般管理費"],
            'correct': 0,
            'explanation': "素価（Prime Cost）は、直接材料費と直接労務費の合計です。（加工費 ＝ 直接労務費 ＋ 製造間接費）"
        },
        {
            'level': 1,
            'q': "標準原価計算: 実際消費量が標準消費量を上回った場合に発生する差異はどれですか？",
            'options': ["有利数量差異", "不利数量差異", "有利価格差異", "不利価格差異"],
            'correct': 1,
            'explanation': "標準よりも多くの数量を消費してしまった場合は、コスト増となるため「不利差異（Unfavorable）」となります。"
        },
        {
            'level': 1,
            'q': "直接原価計算: 固定製造間接費はどのように処理されますか？",
            'options': ["製品原価として処理", "期間原価として処理", "資産として計上", "負債として計上"],
            'correct': 1,
            'explanation': "直接原価計算では、固定製造間接費は発生時に「期間原価」として全額費用処理されます（CVP分析に有用）。"
        },
        {
            'level': 1,
            'q': "原価計算基準: 原価計算基準において、原価計算の目的として挙げられていないものはどれですか？",
            'options': ["財務諸表の作成", "原価管理", "予算統制", "従業員給与の計算"],
            'correct': 3,
            'explanation': "原価計算基準には、財務諸表作成、価格計算、原価管理、予算管理、基本計画策定の5つの目的が挙げられていますが、給与計算は含まれません。"
        },
        {
            'level': 1,
            'q': "ABC (活動基準原価計算): 製造間接費を製品に配賦するために使用される基準は何ですか？",
            'options': ["操業度", "コスト・ドライバー (活動原価要因)", "直接作業時間", "機械稼働時間"],
            'correct': 1,
            'explanation': "ABCでは、製造間接費を活動ごとに把握し、それぞれの活動の発生要因である「コスト・ドライバー」に基づいて製品に配賦します。"
        },
        {
            'level': 1,
            'q': "投資の経済性計算: ROI (投下資本利益率) を求める計算式はどれですか？",
            'options': ["利益 ÷ 売上高", "売上高 ÷ 投下資本", "利益 ÷ 投下資本", "投下資本 ÷ 利益"],
            'correct': 2,
            'explanation': "ROI (Return On Investment) は、利益を投下資本で割って算出します（ROI = 売上高利益率 × 資本回転率）。"
        },
        {
            'level': 2,
            'q': "CVP分析: 固定費1,000、変動費率0.6、目標利益200の場合、目標売上高はいくらですか？",
            'options': ["2,000", "3,000", "2,500", "1,200"],
            'correct': 1,
            'explanation': "目標売上高 ＝ (固定費 ＋ 目標利益) ÷ (1 － 変動費率) ＝ (1000 + 200) ÷ 0.4 ＝ 3000 です。"
        }
    ],
    'Audit': [
        {
            'level': 1,
            'q': "監査リスク: 監査リスク・モデルの構成要素として正しいものはどれですか？",
            'options': ["固有リスク × 統制リスク × 発見リスク", "ビジネスリスク × 監査リスク", "重要性 × リスク", "抽出リスク × 非抽出リスク"],
            'correct': 0,
            'explanation': "監査リスク ＝ 重要な虚偽表示リスク（固有リスク×統制リスク） × 発見リスク です。"
        },
        {
            'level': 1,
            'q': "独立性: 「外観的独立性」を損なう要因となるものはどれですか？",
            'options': ["被監査会社の株式保有", "誠実であること", "専門能力を有すること", "倫理規定の遵守"],
            'correct': 0,
            'explanation': "被監査会社の株式や重要な経済的利害関係を有することは、外観的独立性（第三者から見て独立していると見えること）を損ないます。"
        },
        {
            'level': 1,
            'q': "監査意見: 財務諸表全体に重要な虚偽表示があり、かつその影響が広範である場合に表明される意見はどれですか？",
            'options': ["無限定適正意見", "限定付適正意見", "不適正意見", "意見不表明"],
            'correct': 2,
            'explanation': "重要かつ広範（Pervasive）な虚偽表示がある場合は、「不適正意見（Adverse Opinion）」が表明されます。"
        },
        {
            'level': 1,
            'q': "内部統制: 内部統制の整備・運用責任は誰にありますか？",
            'options': ["監査人", "経営者", "株主", "政府"],
            'correct': 1,
            'explanation': "内部統制を整備し運用する責任は「経営者」にあります。監査人はその有効性を評価・報告する立場です。"
        },
        {
            'level': 1,
            'q': "監査証拠: 一般的に最も証明力が高いとされる監査証拠はどれですか？",
            'options': ["経営者への質問", "観察", "外部確認", "社内文書"],
            'correct': 2,
            'explanation': "外部の第三者から直接入手する「確認（External Confirmation）」は、一般に社内証拠よりも証明力が高いとされます。"
        },
        {
            'level': 1,
            'q': "不正対応: 「不正のトライアングル」の3要素に含まれないものはどれですか？",
            'options': ["動機・プレッシャー", "機会", "姿勢・正当化", "罰則"],
            'correct': 3,
            'explanation': "不正のトライアングルは、「動機・プレッシャー」「機会」「姿勢・正当化」の3要素から構成されます。"
        },
        {
            'level': 1,
            'q': "監査報告書: 監査報告書日はいつであるべきですか？",
            'options': ["決算日", "監査人が監査意見を形成するのに十分かつ適切な監査証拠を入手した日", "株主総会開催日", "有価証券報告書提出日"],
            'correct': 1,
            'explanation': "監査報告書日は、監査人が意見表明の基礎となる十分かつ適切な監査証拠を入手した日（監査終了日）とする必要があります。"
        }
    ],
    'Company': [
        {
            'level': 1,
            'q': "設立: 株式会社の設立における最低資本金の額はいくらですか？",
            'options': ["1,000万円", "300万円", "1円", "0円"],
            'correct': 2,
            'explanation': "現在の会社法では、最低資本金制度は撤廃されており、資本金1円から設立が可能です。"
        },
        {
            'level': 1,
            'q': "自己株式: 株式会社は自己株式を取得することができますか？",
            'options': ["完全に禁止されている", "財源規制等の下で認められる", "自由に認められる", "解散時のみ認められる"],
            'correct': 1,
            'explanation': "自己株式の取得は、分配可能額の範囲内であることや株主総会決議などの規制の下で認められています。"
        },
        {
            'level': 1,
            'q': "機関設計: 取締役会設置会社における取締役の最低人数は何人ですか？",
            'options': ["1人", "2人", "3人", "5人"],
            'correct': 2,
            'explanation': "取締役会を設置する場合、取締役は3人以上必要です。"
        },
        {
            'level': 1,
            'q': "株主総会: 特別決議の定足数は原則としてどのくらいですか？",
            'options': ["議決権の過半数", "議決権の3分の1", "議決権の3分の2", "全株主"],
            'correct': 0,
            'explanation': "特別決議の定足数は原則として「議決権の過半数」です（定款で3分の1まで緩和可）。決議要件は出席株主の議決権の3分の2以上です。"
        },
        {
            'level': 1,
            'q': "監査役: 監査役の任期は原則として何年ですか？",
            'options': ["1年", "2年", "4年", "10年"],
            'correct': 2,
            'explanation': "監査役の任期は原則として4年です。定款によっても短縮することはできません。"
        },
        {
            'level': 1,
            'q': "株主の権利: 単独株主権（1株でも保有していれば行使できる権利）はどれですか？",
            'options': ["株主総会招集請求権", "帳簿閲覧請求権", "剰余金配当請求権", "取締役解任請求権"],
            'correct': 2,
            'explanation': "剰余金配当請求権や議決権は、1株から認められる単独株主権です。帳簿閲覧権などは一定の株式数・期間が必要な少数株主権です。"
        },
        {
            'level': 1,
            'q': "事業譲渡: 株主総会の特別決議が必要となる事業譲渡はどれですか？",
            'options': ["事業の全部または重要な一部の譲渡", "重要な資産の処分", "多額の借財", "支配人の選任"],
            'correct': 0,
            'explanation': "事業の全部の譲渡、または事業の重要な一部の譲渡（譲渡資産が総資産の1/5超など）には、株主総会の特別決議が必要です。"
        }
    ]
}

# Load generated questions
json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'questions.json')
if os.path.exists(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            generated_questions = json.load(f)
            for subject, questions in generated_questions.items():
                if subject in drill_questions:
                    drill_questions[subject].extend(questions)
                else:
                    drill_questions[subject] = questions
    except Exception as e:
        st.error(f"Failed to load generated questions: {e}")

# Load Study Materials (Syllabus)
def load_study_materials():
    # Looking for 'studying' folder in 'platform' directory (moved inside)
    materials_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'studying')
    syllabus = {}
    extra_pdfs = []
    
    if not os.path.exists(materials_dir):
        return {}, []
        
    for filename in os.listdir(materials_dir):
        if filename.endswith('.xlsx') and not filename.startswith('~$'): # Ignore temp files
            try:
                # Extract subject from filename (e.g., "1-財務会計論コース.xlsx" -> "財務会計論")
                parts = filename.split('-')
                if len(parts) > 1:
                    subject_name = parts[1].replace('コース.xlsx', '')
                else:
                    subject_name = filename.replace('.xlsx', '')
                
                # Read Excel
                file_path = os.path.join(materials_dir, filename)
                df = pd.read_excel(file_path, header=1)
                
                # Fill merged cells (NaN) with previous value
                if 'カテゴリ' in df.columns:
                    df['カテゴリ'] = df['カテゴリ'].ffill()
                if 'サブカテゴリ' in df.columns:
                    df['サブカテゴリ'] = df['サブカテゴリ'].ffill()
                
                # Filter relevant columns
                if '講座名' in df.columns:
                    items = []
                    for _, row in df.iterrows():
                        if pd.notna(row['講座名']):
                            items.append({
                                'category': row.get('カテゴリ', ''),
                                'subcategory': row.get('サブカテゴリ', ''),
                                'title': row['講座名'],
                                'duration': row.get('再生時間/標準時間', '')
                            })
                    
                    # Find corresponding PDF
                    pdf_path = os.path.join(materials_dir, filename.replace('.xlsx', '.pdf'))
                    has_pdf = os.path.exists(pdf_path)
                    
                    syllabus[subject_name] = {
                        'items': items,
                        'pdf_path': pdf_path if has_pdf else None,
                        'excel_path': file_path
                    }
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    # Load extra PDFs from 'PDF' subdirectory
    pdf_dir = os.path.join(materials_dir, 'PDF')
    if os.path.exists(pdf_dir):
        for f in os.listdir(pdf_dir):
            if f.lower().endswith('.pdf'):
                extra_pdfs.append({
                    'name': f,
                    'path': os.path.join(pdf_dir, f)
                })
                
    # Also load standalone PDFs in the root of 'studying' that are not paired with an Excel file
    # Get list of PDF paths already associated with courses
    paired_pdfs = set()
    for subject_data in syllabus.values():
        if subject_data['pdf_path']:
            paired_pdfs.add(os.path.normpath(subject_data['pdf_path']))
            
    for filename in os.listdir(materials_dir):
        if filename.lower().endswith('.pdf'):
            full_path = os.path.join(materials_dir, filename)
            if os.path.normpath(full_path) not in paired_pdfs:
                extra_pdfs.append({
                    'name': filename,
                    'path': full_path
                })
                
    return syllabus, extra_pdfs

study_materials, extra_pdfs = load_study_materials()

roadmap_md = """
# CPA 1.5 Year Strategy Roadmap

## Phase 0: Foundation (2026)
* **Feb - Mar**: Build study habits. Focus on Fin/Mgmt Accounting basics.
* **Apr - Jun**: Start Applied theory. Begin Audit & Company Law.
* **Jul - Sep**: **CRITICAL** Start Tax Law & Electives.
* **Oct - Dec**: **Dec Short Exam Challenge**. Aim to pass!

## Phase 1: Short Exam Mastery (Jan - May 2027)
* **Jan - Mar**: Solidify basics. 75%+ in drills.
* **Apr - May**: Peak conditioning. Rote memorization.

## Phase 2: Essay Sprint (Jun - Aug 2027)
* **Jun**: Revive Tax/Elective knowledge.
* **Jul**: Output training (Writing).
* **Aug**: Final adjustments.
"""

# Navigation
st.sidebar.title("CPA Platform 2027")

# User Profile in Sidebar
with st.sidebar.container():
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### 🎓")
    with col2:
        curr_level = st.session_state.data.get('level', 1)
        st.write(f"**Level {curr_level}**")
    
    curr_xp = st.session_state.data.get('xp', 0)
    next_level_xp = curr_level * 100
    progress = min(curr_xp / next_level_xp, 1.0)
    st.progress(progress)
    st.caption(f"XP: {curr_xp} / {next_level_xp}")

st.sidebar.markdown("---")

# Quick Links
st.sidebar.markdown("""
    <style>
    .big-rocket-button {
        display: inline-block;
        width: 100%;
        padding: 12px;
        background: linear-gradient(135deg, #FF4B4B 0%, #FF0000 100%);
        color: white !important;
        text-align: center;
        font-size: 18px;
        font-weight: 900;
        border-radius: 12px;
        text-decoration: none !important;
        box-shadow: 0 4px 15px rgba(255, 0, 0, 0.4);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        border: 2px solid rgba(255, 255, 255, 0.2);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .big-rocket-button:hover {
        background: linear-gradient(135deg, #FF0000 0%, #D00000 100%);
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 6px 20px rgba(255, 0, 0, 0.6);
        border-color: rgba(255, 255, 255, 0.5);
    }
    .big-rocket-button:active {
        transform: translateY(1px);
        box-shadow: 0 2px 10px rgba(255, 0, 0, 0.3);
    }
    </style>
    <a href="https://member.studying.jp/top/" target="_blank" class="big-rocket-button">
        🚀 STUDYING
    </a>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
with st.sidebar.expander("📅 Official Schedule (Edit)"):
    if 'schedule_edit' not in st.session_state:
        st.session_state.schedule_edit = [dict(item) for item in official_schedule]
    edit_rows = []
    for idx, item in enumerate(st.session_state.schedule_edit):
        d = st.date_input(f"Date {idx+1}", value=pd.to_datetime(item.get('date')).date(), key=f"sch_d_{idx}")
        c = st.selectbox(f"Category {idx+1}", options=["Exam", "Result"], index=0 if item.get('category','Exam')=='Exam' else 1, key=f"sch_c_{idx}")
        e = st.text_input(f"Event {idx+1}", value=item.get('event',''), key=f"sch_e_{idx}")
        n = st.text_input(f"Notes {idx+1}", value=item.get('notes',''), key=f"sch_n_{idx}")
        edit_rows.append({'date': d.strftime("%Y-%m-%d"), 'category': c, 'event': e, 'notes': n})
        st.markdown("---")
    if st.button("Add Row"):
        st.session_state.schedule_edit.append({'date': date.today().strftime("%Y-%m-%d"), 'category': 'Exam', 'event': '', 'notes': ''})
        st.rerun()
    if st.button("Save Schedule", type="primary"):
        st.session_state.data['official_schedule'] = edit_rows
        save_data(st.session_state.data)
        st.toast("Official schedule saved", icon="✅")
        official_schedule = edit_rows
page = st.sidebar.radio("Navigation", ["Dashboard 📊", "My Syllabus 📚", "Vocabulary 📖", "Formulas 📐", "Old Exams 📄", "Study Timer ⏱️", "Mock Exams 📝", "Scores 📈", "Wrong Answers 📕", "Drills 🔧", "Exam Mode ⏲️", "Survival Mode ⚡", "Analytics 📊", "Roadmap 🗺️", "Big 4 Job Hunting 💼", "Company Directory 🏢", "Future 🚀"])

if page == "Dashboard 📊":
    st.header("Dashboard 🚀")
    
    # --- Top Metrics Row ---
    st.subheader("📊 At a Glance")
    today = date.today()
    
    # Calculate Metrics
    # 1. Study Time Today
    logs_df = pd.DataFrame(st.session_state.data.get("logs", []))
    minutes_today = 0
    if not logs_df.empty:
        today_str = today.strftime("%Y-%m-%d")
        today_logs = logs_df[logs_df['date'] == today_str]
        minutes_today = today_logs['duration'].sum()
    
    # 2. Quizzes Today
    scores_df = pd.DataFrame(st.session_state.data.get("scores", []))
    quizzes_today = 0
    avg_score_today = 0
    if not scores_df.empty:
        today_str = today.strftime("%Y-%m-%d")
        today_scores = scores_df[scores_df['date'] == today_str]
        quizzes_today = len(today_scores)
        if quizzes_today > 0:
            avg_score_today = today_scores['val'].mean()

    # 3. Total XP
    total_xp = st.session_state.data.get('xp', 0)

    # Streak (consecutive study days up to today)
    streak = 0
    if not logs_df.empty:
        try:
            logs_df_dates = pd.to_datetime(logs_df['date']).dt.date
            logged = set(logs_df_dates[logs_df['duration'] > 0].unique())
            d = today
            while d in logged:
                streak += 1
                d = d - timedelta(days=1)
        except Exception:
            pass

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Study Time (Today)", f"{minutes_today} min", delta=f"{minutes_today/60:.1f} hrs")
    m2.metric("Quizzes Completed", f"{quizzes_today}", delta=f"Avg: {avg_score_today:.0f}%" if quizzes_today > 0 else None)
    m3.metric("Total XP", f"{total_xp}", delta="Level Up Soon?" if total_xp % 100 > 80 else None)
    
    # 4. Nearest Deadline
    target_short = date(2026, 12, 13)
    days_short = (target_short - today).days
    m4.metric("Next Exam (Dec Short)", f"{days_short} Days", delta="-1 Day", delta_color="inverse")
    
    st.caption(f"🔥 Study Streak: {streak} days")
    
    st.markdown("---")

    # --- Main Content Grid ---
    c_main_1, c_main_2 = st.columns([2, 1])
    
    with c_main_1:
        st.subheader("🗓️ Exam Countdown")
        
        # Enhanced Countdown Cards
        cd1, cd2, cd3 = st.columns(3)
        
        with cd1:
            target = date(2026, 12, 13)
            diff = (target - today).days
            st.info(f"**Dec 2026 Short**\n\n# {max(0, diff)} Days\n\n*Target: 60%*")
            
        with cd2:
            target = date(2027, 5, 23)
            diff = (target - today).days
            st.warning(f"**May 2027 Short**\n\n# {max(0, diff)} Days\n\n*Target: PASS*")
            
        with cd3:
            target = date(2027, 8, 20)
            diff = (target - today).days
            st.error(f"**Aug 2027 Essay**\n\n# {max(0, diff)} Days\n\n*Target: PASS*")

        se = None
        try:
            sched_df = pd.DataFrame(official_schedule)
            if not sched_df.empty:
                sched_df['d'] = pd.to_datetime(sched_df['date']).dt.date
                future = sched_df[sched_df['d'] >= today]
                if not future.empty:
                    se = future.sort_values('d').iloc[0]
        except Exception:
            pass
        if se is not None:
            dd = (se['d'] - today).days
            st.info(f"**Next Official Event**: {se['event']} ({se['category']})\n\n# {dd} Days\n\n{se.get('notes','')}")

        # Weakness Analysis
        st.subheader("🧠 Weak Areas Analysis")
        if not scores_df.empty:
            # Group by subject and calculate mean
            subject_perf = scores_df.groupby('subject')['val'].mean().sort_values()
            weakest_subject = subject_perf.index[0]
            weakest_score = subject_perf.iloc[0]
            
            st.markdown(f"""
            <div style="padding: 15px; border-radius: 10px; background-color: #fff3cd; border: 1px solid #ffeeba; color: #856404;">
                <h4>⚠️ Focus Area: {weakest_subject} ({weakest_score:.1f}%)</h4>
                <p>Your performance in <b>{weakest_subject}</b> is lower than other subjects. Consider doing a targeted drill.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🔥 Start {weakest_subject} Drill Now"):
                # Redirect logic (simulated by setting session state)
                # Note: Direct page switching in Streamlit is tricky without rerun, 
                # but we can set the quiz state to active for this subject
                # Ideally, user goes to Drills tab, but we can hint them.
                st.toast(f"Go to 'Drills' tab and select {weakest_subject}!", icon="👉")
        else:
            st.info("Complete some drills to identify your weak areas.")

        # Recent Activity Chart (Last 7 Days)
        st.subheader("📈 Study Consistency (Last 7 Days)")
        if not logs_df.empty:
            # Filter last 7 days
            logs_df['date'] = pd.to_datetime(logs_df['date']).dt.date
            last_7_days = [today - pd.Timedelta(days=i) for i in range(6, -1, -1)]
            
            daily_minutes = []
            for d in last_7_days:
                day_logs = logs_df[logs_df['date'] == d]
                daily_minutes.append(day_logs['duration'].sum())
            
            chart_data = pd.DataFrame({
                "Date": last_7_days,
                "Minutes": daily_minutes
            })
            
            fig_activity = px.bar(chart_data, x="Date", y="Minutes", title="Daily Study Time")
            st.plotly_chart(fig_activity, use_container_width=True)
        else:
            st.info("Log your study sessions to see your consistency chart.")


    with c_main_2:
        # Skill Radar
        st.subheader("Skills")
        subjects = ['Financial', 'Management', 'Audit', 'Company', 'Tax', 'Elective']
        radar_scores = [30] * 6 # Default
        
        if not scores_df.empty:
            avg_scores = []
            for sub in subjects:
                sub_df = scores_df[scores_df['subject'] == sub]
                if not sub_df.empty:
                    avg_scores.append(sub_df['val'].mean())
                else:
                    avg_scores.append(30) # Default baseline
            radar_scores = avg_scores
            
        fig = go.Figure(data=go.Scatterpolar(
            r=radar_scores,
            theta=subjects,
            fill='toself',
            name='Current Skill'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])), 
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Daily Tip Card
        st.subheader("💡 Daily Tip")
        tips = [
            "Consistency is key. 30 minutes every day is better than 5 hours once a week.",
            "Focus on 'why', not just 'how'. Understanding the logic helps in applied questions.",
            "Don't ignore the theory. It's 40-50% of the exam.",
            "Review your mistakes. The 'incorrect' options are learning opportunities.",
            "Sleep is part of studying. Memory consolidation happens during sleep.",
            "Use the 'Survival Mode' to build speed and accuracy under pressure!",
            "Audit isn't just memorization; imagine you are the auditor in that situation."
        ]
        import random
        st.info(random.choice(tips))
        
        # Progress
        st.subheader("Phase 0 Progress")
        st.progress(15)
        st.caption("Goal: Foundation Mastery")

elif page == "My Syllabus 📚":
    st.header("My Study Syllabus 📚")
    st.info("Based on your uploaded materials in 'studying' folder.")
    
    if not study_materials and not extra_pdfs:
        st.warning("No study materials found in 'studying' folder.")
    else:
        # Progress Tracking
        if 'syllabus_progress' not in st.session_state.data:
            st.session_state.data['syllabus_progress'] = []
            
        completed_items = set(st.session_state.data['syllabus_progress'])
        
        # Callback for checkbox
        def toggle_syllabus(key):
            if key in st.session_state.data['syllabus_progress']:
                st.session_state.data['syllabus_progress'].remove(key)
            else:
                st.session_state.data['syllabus_progress'].append(key)
                # Add XP for completing a lecture!
                st.session_state.data['xp'] = st.session_state.data.get('xp', 0) + 50
                st.toast("Lecture Completed! +50 XP", icon="🎓")
            save_data(st.session_state.data)

        # Tabs for subjects
        if study_materials:
            subjects = list(study_materials.keys())
            tabs = st.tabs(subjects)
            
            for i, subject in enumerate(subjects):
                with tabs[i]:
                    data = study_materials[subject]
                    items = data['items']
                    pdf_path = data['pdf_path']
                    excel_path = data['excel_path']
                    
                    # Header Actions
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.subheader(f"{subject} ({len(items)} Lectures)")
                    with c2:
                        if pdf_path:
                            if st.button(f"📄 Open PDF", key=f"pdf_{subject}"):
                                try:
                                    os.startfile(pdf_path)
                                    st.toast(f"Opening {subject} PDF...", icon="🚀")
                                except Exception as e:
                                    st.error(f"Cannot open PDF: {e}")
                        
                        if st.button(f"📊 Open Excel", key=f"excel_{subject}"):
                            try:
                                os.startfile(excel_path)
                                st.toast(f"Opening {subject} Excel...", icon="📊")
                            except Exception as e:
                                st.error(f"Cannot open Excel: {e}")

                    
                    # Progress Bar for Subject
                    subject_completed = [item['title'] for item in items if f"{subject}|{item['title']}" in completed_items]
                    prog = len(subject_completed) / len(items) if items else 0
                    st.progress(prog)
                    st.caption(f"Progress: {len(subject_completed)} / {len(items)} ({prog:.1%})")
                    
                    # Group by Category/Subcategory
                    df = pd.DataFrame(items)
                    if not df.empty and 'category' in df.columns:
                        for cat, group in df.groupby('category'):
                            with st.expander(f"📂 {cat}", expanded=True):
                                for idx, row in group.iterrows():
                                    title = row['title']
                                    unique_key = f"{subject}|{title}"
                                    is_done = unique_key in completed_items
                                    
                                    c_chk, c_txt, c_time = st.columns([0.5, 4, 1.5])
                                    with c_chk:
                                        # Use subject and index to ensure widget key uniqueness
                                        st.checkbox("", value=is_done, key=f"chk_{subject}_{idx}", on_change=toggle_syllabus, kwargs={'key': unique_key})
                                    
                                    with c_txt:
                                        if is_done:
                                            st.markdown(f"~~{title}~~")
                                        else:
                                            st.markdown(f"**{title}**")
                                            if row['subcategory']:
                                                st.caption(f"└ {row['subcategory']}")
                                                
                                    with c_time:
                                        st.caption(f"⏱️ {row['duration']}")

        # Supplemental Resources (Extra PDFs)
        if extra_pdfs:
            st.markdown("---")
            st.subheader("📚 Supplemental Resources")
            for i, pdf in enumerate(extra_pdfs):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f"📄 **{pdf['name']}**")
                with c2:
                    if st.button("Open", key=f"extra_pdf_{i}_{pdf['name']}"):
                        try:
                            os.startfile(pdf['path'])
                            st.toast(f"Opening {pdf['name']}...", icon="🚀")
                        except Exception as e:
                            st.error(f"Cannot open PDF: {e}")

elif page == "Vocabulary 📖":
    st.header("Vocabulary Mastery 📖")
    st.info("Master the essential accounting terminology in Japanese and English.")

    # Create Tabs
    tab1, tab2 = st.tabs(["📚 Word List", "⚡ Tap & Study (Flashcards)"])

    # --- TAB 1: Word List ---
    with tab1:
        st.subheader("Bilingual Terminology List")
        
        # Subject Selection
        subjects = list(vocab_data.keys())
        selected_subject = st.selectbox("Select Subject", subjects, key="vocab_list_subject")
        
        if selected_subject:
            terms = vocab_data[selected_subject]
            st.write(f"Found {len(terms)} terms for **{selected_subject}**.")
            
            for term in terms:
                with st.expander(f"**{term['term']}** ({term['jp']})"):
                    st.markdown(f"**🇯🇵 Definition:** {term['desc']}")
                    st.markdown(f"**🇺🇸 Definition:** {term.get('desc_en', 'No English definition available.')}")

    # --- TAB 2: Flashcards ---
    with tab2:
        st.subheader("⚡ Flashcard Mode")
        st.markdown("Tap to flip the card, swipe (click next) to move to the next word.")
        
        # Initialize Session State for Flashcards
        if 'flashcard_active' not in st.session_state:
            st.session_state.flashcard_active = False
            st.session_state.flashcard_subject = subjects[0]
            st.session_state.flashcard_index = 0
            st.session_state.flashcard_flipped = False

        # Subject Selection for Flashcards
        fc_subject = st.selectbox("Select Subject for Study", subjects, key="fc_subject_selector")
        
        # Start/Reset Button
        if st.button("Start / Restart Session", type="primary"):
            st.session_state.flashcard_active = True
            st.session_state.flashcard_subject = fc_subject
            st.session_state.flashcard_index = 0
            st.session_state.flashcard_flipped = False
            st.rerun()

        if st.session_state.flashcard_active:
            current_terms = vocab_data.get(st.session_state.flashcard_subject, [])
            total_cards = len(current_terms)
            
            if total_cards == 0:
                st.warning("No words available for this subject.")
            else:
                current_idx = st.session_state.flashcard_index
                
                # Check if session is finished
                if current_idx >= total_cards:
                    st.balloons()
                    st.success(f"🎉 You've completed all {total_cards} words for {st.session_state.flashcard_subject}!")
                    if st.button("Start Over"):
                        st.session_state.flashcard_index = 0
                        st.session_state.flashcard_flipped = False
                        st.rerun()
                else:
                    word_data = current_terms[current_idx]
                    
                    # Progress Bar
                    progress = (current_idx + 1) / total_cards
                    st.progress(progress)
                    st.caption(f"Card {current_idx + 1} of {total_cards}")

                    # Card Container
                    card_container = st.container()
                    
                    # Card Logic
                    with card_container:
                        # Styling
                        st.markdown("""
                        <style>
                        .flashcard {
                            border: 2px solid #e0e0e0;
                            border-radius: 15px;
                            padding: 40px;
                            text-align: center;
                            background-color: white;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                            min-height: 200px;
                            display: flex;
                            flex-direction: column;
                            justify-content: center;
                            align-items: center;
                            margin-bottom: 20px;
                        }
                        .flashcard-term { font-size: 28px; font-weight: bold; color: #1e88e5; }
                        .flashcard-jp { font-size: 24px; font-weight: bold; color: #d32f2f; margin-top: 10px;}
                        .flashcard-desc { font-size: 16px; color: #424242; margin-top: 15px; }
                        </style>
                        """, unsafe_allow_html=True)

                        if not st.session_state.flashcard_flipped:
                            # FRONT SIDE
                            st.markdown(f"""
                            <div class="flashcard">
                                <div class="flashcard-term">{word_data['term']}</div>
                                <div style="color: #9e9e9e; margin-top: 20px;">(Tap 'Flip' to see meaning)</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if st.button("🔄 Flip Card", use_container_width=True):
                                st.session_state.flashcard_flipped = True
                                st.rerun()
                                
                        else:
                            # BACK SIDE
                            st.markdown(f"""
                            <div class="flashcard">
                                <div class="flashcard-term">{word_data['term']}</div>
                                <div class="flashcard-jp">{word_data['jp']}</div>
                                <div class="flashcard-desc">🇯🇵 {word_data['desc']}</div>
                                <div class="flashcard-desc">🇺🇸 {word_data.get('desc_en', '')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            col_prev, col_next = st.columns(2)
                            with col_prev:
                                if st.button("⬅️ Previous", use_container_width=True):
                                    if st.session_state.flashcard_index > 0:
                                        st.session_state.flashcard_index -= 1
                                        st.session_state.flashcard_flipped = False
                                        st.rerun()
                            
                            with col_next:
                                if st.button("Next ➡️", use_container_width=True):
                                    st.session_state.flashcard_index += 1
                                    st.session_state.flashcard_flipped = False
                                    st.rerun()

elif page == "Formulas 📐":
    st.header("Formulas 📐")
    if not formulas_data:
        st.warning("No formulas found.")
    else:
        df_all_formulas = pd.DataFrame(formulas_data)
        st.subheader("Top Picks")
        show_picks = st.checkbox("Show Top Picks", value=True)
        if show_picks:
            cats_all = sorted({str(f.get("category", "General")) for f in formulas_data})
            size = st.radio("Size", [10, 30], horizontal=True)
            top10_names = [
                "Future Value (Single Sum)",
                "Present Value (Single Sum)",
                "Present Value of Annuity",
                "Contribution Margin",
                "Break-even Units",
                "Net Present Value",
                "WACC",
                "CAPM Cost of Equity",
                "ROE",
                "DuPont ROE"
            ]
            top30_names = top10_names + [
                "IRR",
                "Profitability Index",
                "Payback Period",
                "Present Value of Perpetuity",
                "Gordon Growth (DDM)",
                "Current Ratio",
                "Quick Ratio",
                "Debt-to-Equity",
                "Times Interest Earned",
                "Inventory Turnover",
                "Days Sales Outstanding",
                "Days Inventory Outstanding",
                "Cash Conversion Cycle",
                "Gross Profit Margin",
                "Operating Margin",
                "Net Profit Margin",
                "Economic Order Quantity (EOQ)",
                "Reorder Point",
                "Safety Stock",
                "Annuity Due PV",
                "Annuity Due FV",
                "Present Value (Annuity Due)",
                "Future Value (Annuity Due)"
            ]
            pick_names = top10_names if size == 10 else top30_names
            top_df = df_all_formulas[df_all_formulas["name"].isin(pick_names)].copy()
            if top_df.empty and not df_all_formulas.empty:
                top_df = df_all_formulas.head(size).copy()
                pick_names = list(top_df["name"])
            if len(top_df) < size and not df_all_formulas.empty:
                missing = size - len(top_df)
                fallback = df_all_formulas[~df_all_formulas["name"].isin(pick_names)].head(missing)
                top_df = pd.concat([top_df, fallback], ignore_index=True)
                pick_names = list(top_df["name"])
            order_map = {name: i for i, name in enumerate(pick_names)}
            top_cat = st.selectbox("Category Focus", ["All"] + cats_all)
            if top_cat != "All":
                top_df = top_df[top_df["category"] == top_cat]
            if not top_df.empty:
                top_df["rank"] = top_df["name"].map(order_map)
                top_df = top_df.sort_values("rank")
                tab1, tab2, tab3 = st.tabs(["Cards", "Table", "Category Chart"])
                with tab1:
                    cols = st.columns(2)
                    for idx, (_, r) in enumerate(top_df.iterrows()):
                        with cols[idx % 2]:
                            st.markdown(f"**{r.get('name','')}**")
                            st.caption(str(r.get('category', '')))
                            if r.get("latex", ""):
                                st.latex(r.get("latex", ""))
                            elif r.get("formula", ""):
                                st.code(str(r.get("formula", "")))
                with tab2:
                    st.table(top_df[["name", "category", "formula"]].rename(columns={"name": "Name", "category": "Category", "formula": "Formula"}))
                with tab3:
                    try:
                        import plotly.express as px
                        dfc = top_df.groupby("category").size().reset_index(name="count")
                        if not dfc.empty:
                            fig = px.bar(dfc, x="category", y="count", title=f"Top {size} by Category", color="category")
                            fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Count")
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No data to chart for the selected filter.")
                    except Exception as e:
                        st.info("Plotly is unavailable for charting.")
            else:
                st.info("No formulas matched the current top selection.")
        st.divider()
        cats = sorted({str(f.get("category", "General")) for f in formulas_data})
        cat_sel = st.multiselect("Category", options=cats, default=[])
        q = st.text_input("Search")
        df_f = pd.DataFrame(formulas_data)
        if not df_f.empty:
            if cat_sel:
                df_f = df_f[df_f["category"].isin(cat_sel)]
            if q:
                ql = q.lower()
                def _has(r):
                    return (ql in str(r.get("name", "")).lower() or
                            ql in str(r.get("formula", "")).lower() or
                            ql in str(r.get("explanation", "")).lower() or
                            ql in str(r.get("variables", "")).lower())
                df_f = df_f[df_f.apply(_has, axis=1)]
        st.write(f"Found {len(df_f)} formulas.")
        for _, row in df_f.iterrows():
            title = row.get("name", "")
            cat = row.get("category", "")
            if cat:
                title = f"{title} [{cat}]"
            with st.expander(title):
                ftxt = row.get("formula", "")
                ltx = row.get("latex", "")
                if ltx:
                    st.latex(ltx)
                elif ftxt:
                    st.markdown(f"**Formula:** {ftxt}")
                vtxt = row.get("variables", "")
                if vtxt:
                    st.markdown(f"**Variables:** {vtxt}")
                etxt = row.get("explanation", "")
                if etxt:
                    st.markdown(etxt)
                ex_ja = _sanitize_text(row.get("example_ja", ""))
                ex_en = _sanitize_text(row.get("example_en", ""))
                if ex_ja or ex_en:
                    st.markdown("**Examples**")
                    if ex_ja:
                        st.markdown(f"🇯🇵 {ex_ja}")
                    if ex_en:
                        st.markdown(f"🇺🇸 {ex_en}")
                prob_ja = _sanitize_text(row.get("problem_ja", ""))
                prob_en = _sanitize_text(row.get("problem_en", ""))
                sol_ja = _sanitize_text(row.get("solution_ja", ""))
                sol_en = _sanitize_text(row.get("solution_en", ""))
                if prob_ja or prob_en:
                    st.markdown("**Practice Problem**")
                    if prob_ja:
                        st.markdown(f"🇯🇵 {prob_ja}")
                    if prob_en:
                        st.markdown(f"🇺🇸 {prob_en}")
                    if sol_ja or sol_en:
                        with st.expander("Show Solution"):
                            if sol_ja:
                                st.markdown(f"🇯🇵 {sol_ja}")
                            if sol_en:
                                st.markdown(f"🇺🇸 {sol_en}")
                with st.expander("Edit Examples / Problem"):
                    with st.form(f"form_edit_{row.get('name','')}"):
                        i_ex_ja = st.text_area("Example (JP)", value=_sanitize_text(ex_ja), height=100)
                        i_ex_en = st.text_area("Example (EN)", value=_sanitize_text(ex_en), height=100)
                        i_pb_ja = st.text_area("Problem (JP)", value=_sanitize_text(prob_ja), height=120)
                        i_pb_en = st.text_area("Problem (EN)", value=_sanitize_text(prob_en), height=120)
                        i_sol_ja = st.text_area("Solution (JP)", value=_sanitize_text(sol_ja), height=120)
                        i_sol_en = st.text_area("Solution (EN)", value=_sanitize_text(sol_en), height=120)
                        submitted = st.form_submit_button("Save")
                        if submitted:
                            key_name = row.get("name", "")
                            updated = False
                            for idx, item in enumerate(formulas_data):
                                if item.get("name", "") == key_name:
                                    formulas_data[idx]["example_ja"] = i_ex_ja
                                    formulas_data[idx]["example_en"] = i_ex_en
                                    formulas_data[idx]["problem_ja"] = i_pb_ja
                                    formulas_data[idx]["problem_en"] = i_pb_en
                                    formulas_data[idx]["solution_ja"] = i_sol_ja
                                    formulas_data[idx]["solution_en"] = i_sol_en
                                    updated = True
                                    break
                            if updated and save_formulas_data(formulas_data):
                                st.toast("Saved examples and problem.", icon="✅")
                                st.rerun()
                            else:
                                st.error("Failed to save. Please try again.")
elif page == "Old Exams 📄":
    st.header("Old Exam Papers 📄")
    
    # Path to EXAM folder
    # platform/app.py -> platform/EXAM
    base_dir = os.path.dirname(os.path.abspath(__file__))
    exam_dir = os.path.join(base_dir, 'EXAM')
    metadata_file = os.path.join(base_dir, 'exam_metadata.json')
    
    metadata = {}
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except Exception as e:
            st.error(f"Error loading metadata: {e}")

    with st.expander("📝 Exam Info（合格ボーダー R4〜R8）", expanded=True):
        st.markdown("""
        ### 短答式（相対評価）
        - 合格基準: 総点数の70％を基準として、審査会が相当と認めた得点比率
        - 足切り: 1科目でも満点の40％未満がある場合、不合格の可能性あり
        
        参考：近年のボーダー（予備校・メディア集計／一部参考値）
        
        | 実施年 | 第I回（12月） | 第II回（5月） | 備考 |
        |---|---:|---:|---|
        | 令和8年 (2026) | 72.0% | ― | 最新（第I回、結果1月公表） |
        | 令和7年 (2025) | 70.4% | 74.0% | 標準化の動き |
        | 令和6年 (2024) | 68.0% | 78.0% | 易化で高水準 |
        | 令和5年 (2023) | 71.0% | 70.2% | 70%前後 |
        | 令和4年 (2022) | 68.0% | 73.0% | 変動大 |
        
        - 出典（参考値・解説記事）:
          - マイナビ会計士「第Ⅱ回短答式試験 結果速報」: https://cpa.mynavi.jp/column_mt/2024/06/967.html
          - 短答式の合格基準（公式）: https://www.fsa.go.jp/cpaaob/kouninkaikeishi-shiken/kijuntou/05.html
        
        ---
        例: 500点 × 0.72 = 360点
        
        ---
        ### 論文式（偏差値方式）
        - 合格基準: 総点数の60％を基準として、審査会が相当と認めた得点比率
        - 足切り: 1科目でも得点比率（偏差値）が40％未満のものがある場合は不合格
        - 得点比率（偏差値）の一般式: 50 + 10 × (個人の得点 − 平均点) / 標準偏差
        
        近年の合格点（公表資料/報道ベース）
        - 令和6年 (2024): 約52.0前後（毎年微調整）
        - 令和5年 (2023): 約51.8前後（微調整）
        - 令和4年 (2022): 約52.0前後（基準に近い）
        - 令和7年 (2025): 公表ページ参照（偏差値法の説明あり）
        - 令和8年 (2026): 公表予定
        
        - 出典（公式）:
          - 合格基準について（短答式/論文式の公式基準）: https://www.fsa.go.jp/cpaaob/kouninkaikeishi-shiken/kijuntou/05.html
          - 令和7年 論文式 合格点の公表例（PDF、偏差値法の説明含む）: https://www.fsa.go.jp/cpaaob/kouninkaikeishi-shiken/r7shiken/ronbungoukaku_r07/02.pdf
        """)
        # R4-R8 short-answer border mini chart
        try:
            df_borders = pd.DataFrame([
                {"Year": "R4 (2022)", "Session": "I (Dec)", "Border": 68.0},
                {"Year": "R4 (2022)", "Session": "II (May)", "Border": 73.0},
                {"Year": "R5 (2023)", "Session": "I (Dec)", "Border": 71.0},
                {"Year": "R5 (2023)", "Session": "II (May)", "Border": 70.2},
                {"Year": "R6 (2024)", "Session": "I (Dec)", "Border": 68.0},
                {"Year": "R6 (2024)", "Session": "II (May)", "Border": 78.0},
                {"Year": "R7 (2025)", "Session": "I (Dec)", "Border": 70.4},
                {"Year": "R7 (2025)", "Session": "II (May)", "Border": 74.0},
                {"Year": "R8 (2026)", "Session": "I (Dec)", "Border": 72.0},
            ])
            fig_border = px.bar(
                df_borders, x="Year", y="Border", color="Session", barmode="group",
                title="短答式 合格ボーダー（参考値）R4〜R8", range_y=[60, 80],
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_border.update_layout(legend_title_text="Session", yaxis_title="Border (%)")
            st.plotly_chart(fig_border, use_container_width=True)
            st.caption("注: 参考値（予備校・メディア集計ベース）。公式の相対基準はリンク参照。")
        except Exception:
            pass
    
    with st.expander("🆕 令和7・令和8 情報（リンク/予定）", expanded=True):
        st.markdown("""
        - 令和7年 (2025)  
          - 短答式: 公式日程・合格基準は CPAAOB 公表ページを参照  
          - 論文式: 上記リンク（偏差値方式の説明付き）参照
        - 令和8年 (2026)  
          - 短答式/論文式: 順次公表予定（例年どおり）
        
        公式ポータル  
        - 公認会計士・監査審査会（CPAAOB）試験情報: https://www.fsa.go.jp/cpaaob/kouninkaikeishi-shiken/index.html
        """)
    
    with st.expander("🎯 短答 必要得点計算機", expanded=False):
        # Target presets
        p1, p2, p3 = st.columns(3)
        with p1:
            if st.button("Target 70%"):
                st.session_state["tanto_target_pct"] = 70
                st.rerun()
        with p2:
            if st.button("Target 72%"):
                st.session_state["tanto_target_pct"] = 72
                st.rerun()
        with p3:
            if st.button("Target 78%"):
                st.session_state["tanto_target_pct"] = 78
                st.rerun()

        # Target slider
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            default_target = st.session_state.get("tanto_target_pct", 72)
            target_pct = st.slider("目標得点率(%)", min_value=60, max_value=85, value=default_target, step=1, key="tanto_target_slider")
            target_points = int(500 * target_pct / 100)
            st.metric("必要合計点(500点満点)", f"{target_points} 点", f"{target_pct}%")
        with col_t2:
            st.caption("配点: 企業法100・管理100・監査100・財務200")
        
        # Preset buttons for subject shares
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("Preset: Balanced 70/70/70/70"):
                st.session_state["tanto_corp_pct"] = 70
                st.session_state["tanto_mgmt_pct"] = 70
                st.session_state["tanto_audit_pct"] = 70
                st.session_state["tanto_fin_pct"] = 70
                st.rerun()
        with b2:
            if st.button("Preset: Fin-Heavy 65/65/65/78"):
                st.session_state["tanto_corp_pct"] = 65
                st.session_state["tanto_mgmt_pct"] = 65
                st.session_state["tanto_audit_pct"] = 65
                st.session_state["tanto_fin_pct"] = 78
                st.rerun()
        with b3:
            if st.button("Preset: Safety 75/70/70/75"):
                st.session_state["tanto_corp_pct"] = 75
                st.session_state["tanto_mgmt_pct"] = 70
                st.session_state["tanto_audit_pct"] = 70
                st.session_state["tanto_fin_pct"] = 75
                st.rerun()

        # Inputs with keys to allow presets
        if "tanto_corp_pct" not in st.session_state:
            st.session_state["tanto_corp_pct"] = 70
        if "tanto_mgmt_pct" not in st.session_state:
            st.session_state["tanto_mgmt_pct"] = 70
        if "tanto_audit_pct" not in st.session_state:
            st.session_state["tanto_audit_pct"] = 70
        if "tanto_fin_pct" not in st.session_state:
            st.session_state["tanto_fin_pct"] = 70

        c1, c2 = st.columns(2)
        with c1:
            corp_pct = st.number_input("企業法(%)", min_value=0, max_value=100, value=st.session_state["tanto_corp_pct"], step=1, key="tanto_corp_pct")
            mgmt_pct = st.number_input("管理会計論(%)", min_value=0, max_value=100, value=st.session_state["tanto_mgmt_pct"], step=1, key="tanto_mgmt_pct")
        with c2:
            audit_pct = st.number_input("監査論(%)", min_value=0, max_value=100, value=st.session_state["tanto_audit_pct"], step=1, key="tanto_audit_pct")
            fin_pct = st.number_input("財務会計論(%)", min_value=0, max_value=100, value=st.session_state["tanto_fin_pct"], step=1, key="tanto_fin_pct")
        total_points = int(corp_pct/100*100 + mgmt_pct/100*100 + audit_pct/100*100 + fin_pct/100*200)
        total_pct = round(total_points / 500 * 100, 1)
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.metric("合計得点率", f"{total_pct}%")
        with col_r2:
            st.metric("合計点", f"{total_points} 点")
        with col_r3:
            ok = (corp_pct >= 40) and (mgmt_pct >= 40) and (audit_pct >= 40) and (fin_pct >= 40)
            status = "OK" if (total_pct >= target_pct and ok) else "要改善"
            st.metric("達成状況", status)
        if not ok:
            st.warning("足切り注意: いずれかの科目が40%未満です。")
        elif total_pct < target_pct:
            st.info("合計が目標に届いていません。強化科目を見直してください。")
        else:
            st.success("目標達成ラインです。")
    
    with st.expander("🧮 論文 偏差値計算機", expanded=False):
        col_e1, col_e2, col_e3 = st.columns(3)
        with col_e1:
            personal = st.number_input("個人の得点", min_value=0.0, value=60.0, step=0.1)
        with col_e2:
            mean = st.number_input("平均点", min_value=0.0, value=55.0, step=0.1)
        with col_e3:
            std = st.number_input("標準偏差", min_value=0.1, value=7.0, step=0.1)
        deviation = round(50 + 10 * (personal - mean) / std, 2)
        st.metric("得点比率（偏差値）", f"{deviation}")
        if deviation < 40:
            st.warning("足切りラインに注意（40未満）。")
        elif deviation < 52:
            st.info("基準目安 52 に未達。学習強化が必要です。")
        else:
            st.success("合格基準目安を超えています。")
    
    with st.expander("📐 基本式 / Basic Formulas", expanded=False):
        st.markdown("""
        - 短答 合計点: 合計点 = 100×企業法% + 100×管理% + 100×監査% + 200×財務%
        - 短答 合計得点率: 合計得点率(%) = 合計点 ÷ 500 × 100
        - 短答 合格条件(目安): 全科目40%以上 かつ 合計得点率 ≥ 目標%
        - 逆算（必要な財務%）: 財務% = { (目標%×500/100) − [100×(企業法%+管理%+監査%)] } ÷ 200 × 100
        - 論文 偏差値: D = 50 + 10 × (x − μ)/σ
        - 論文 必要得点: x = μ + σ × (D − 50)/10
        """)
        col_rev1, col_rev2 = st.columns(2)
        with col_rev1:
            st.subheader("短答 逆算（必要財務%）")
            t_pct = st.number_input("目標得点率(%)", min_value=60, max_value=85, value=72, step=1, key="rev_target")
            rc = st.number_input("企業法(%)", min_value=0, max_value=100, value=70, step=1, key="rev_corp")
            rm = st.number_input("管理会計論(%)", min_value=0, max_value=100, value=70, step=1, key="rev_mgmt")
            ra = st.number_input("監査論(%)", min_value=0, max_value=100, value=70, step=1, key="rev_audit")
            need_fin = ((t_pct/100*500) - (100*(rc+rm+ra))) / 200 * 100
            need_fin_disp = round(need_fin, 1)
            feas = 0 <= need_fin <= 100
            st.metric("必要 財務会計論(%)", f"{need_fin_disp}%")
            if not feas:
                st.warning("この条件では達成不可能です（0〜100%の範囲外）。")
        with col_rev2:
            st.subheader("論文 必要得点（逆算）")
            d_target = st.number_input("目標偏差値 D", min_value=35.0, max_value=70.0, value=52.0, step=0.1, key="rev_d")
            mu = st.number_input("平均点 μ", min_value=0.0, value=55.0, step=0.1, key="rev_mu")
            sigma = st.number_input("標準偏差 σ", min_value=0.1, value=7.0, step=0.1, key="rev_sigma")
            need_x = mu + sigma * (d_target - 50) / 10
            st.metric("必要得点 x", f"{round(need_x, 2)}")

    if not os.path.exists(exam_dir):
        st.error(f"EXAM directory not found at: {exam_dir}")
    else:
        # --- Vocab Analysis Section ---
        vocab_file = os.path.join(base_dir, 'exam_vocab.json')
        if os.path.exists(vocab_file):
            with st.expander("📊 Exam Vocabulary Analysis (Tangocho)", expanded=False):
                st.info("Top frequent words extracted from actual exam papers. Master these!")
                
                try:
                    with open(vocab_file, "r", encoding="utf-8") as f:
                        exam_vocab = json.load(f)
                    
                    # Subject selector
                    subjects = list(exam_vocab.keys())
                    if subjects:
                        selected_subject = st.selectbox("Select Subject for Vocabulary", subjects)
                        
                        if selected_subject:
                            words = exam_vocab[selected_subject]
                            
                            # Display as a dataframe or cloud
                            # Create a nice dataframe
                            df_vocab = pd.DataFrame(words)
                            df_vocab.columns = ["Word", "Frequency"]
                            
                            col1, col2 = st.columns([1, 2])
                            
                            with col1:
                                st.dataframe(df_vocab, use_container_width=True, height=400)
                                
                            with col2:
                                if not df_vocab.empty:
                                    st.markdown("### Top Keywords")
                                    # Create a bar chart
                                    fig = px.bar(
                                        df_vocab.head(20), 
                                        x='Frequency', 
                                        y='Word', 
                                        orientation='h',
                                        title=f"Top 20 Words in {selected_subject}",
                                        color='Frequency',
                                        color_continuous_scale='Viridis'
                                    )
                                    fig.update_layout(yaxis={'categoryorder':'total ascending'})
                                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Error loading vocabulary: {e}")
        
        st.divider()

        files = [f for f in os.listdir(exam_dir) if f.lower().endswith('.pdf')]
        
        if not files:
            st.warning("No PDF exam papers found.")
        else:
            st.write(f"Found {len(files)} exam papers.")
            
            # Sort by filename to keep subjects grouped (01, 02, ...)
            for f in sorted(files):
                info = metadata.get(f, {})
                display_title = f"**{f}**"
                sub_info = ""
                
                if info:
                    # Construct nice title
                    # e.g. R7 Short-Answer (Tanto) I - Corporate Law (企業法)
                    year = info.get('year', '')
                    exam_type = info.get('type', '')
                    subject = info.get('subject', '')
                    
                    # Create a clean badge-like string
                    display_title = f"**{subject}** - {year} {exam_type}"
                    sub_info = f"Filename: {f}"
                
                with st.container():
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"📄 {display_title}")
                        if sub_info:
                            st.caption(sub_info)
                    with col2:
                        if st.button("Open", key=f"open_exam_{f}"):
                            try:
                                file_path = os.path.join(exam_dir, f)
                                if os.name == 'nt':
                                    os.startfile(file_path)
                                    st.toast(f"Opening {f}...", icon="🚀")
                                else:
                                    st.warning("File opening is only supported on Windows locally.")
                            except Exception as e:
                                st.error(f"Error opening file: {e}")
                    st.divider()
            
            st.info("💡 Tip: Use these papers to practice time management.")

elif page == "Study Timer ⏱️":
    st.header("Study Timer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Log Study Session")
        with st.form("timer_form"):
            subject = st.selectbox("Subject", ["Financial", "Management", "Audit", "Company", "Tax", "Elective"])
            duration = st.number_input("Duration (minutes)", min_value=1, value=60)
            date_val = st.date_input("Date", value=date.today())
            submitted = st.form_submit_button("Log Session")
            
            if submitted:
                new_log = {
                    'date': date_val.strftime("%Y-%m-%d"),
                    'subject': subject,
                    'duration': duration
                }
                st.session_state.data["logs"].append(new_log)
                save_data(st.session_state.data)
                st.success("Session logged!")
                
    with col2:
        st.subheader("Recent Logs")
        if st.session_state.data["logs"]:
            df_logs = pd.DataFrame(st.session_state.data["logs"])
            st.dataframe(df_logs.sort_values('date', ascending=False))
            
            total_mins = df_logs['duration'].sum()
            hours = total_mins // 60
            mins = total_mins % 60
            st.metric("Total Study Time", f"{hours}h {mins}m")
        else:
            st.info("No logs yet.")

elif page == "Mock Exams 📝":
    st.header("Exam Schedule")
    t1, t2 = st.tabs(["📅 Official Schedule", "📝 Mock Schedule"])
    with t1:
        df_off = pd.DataFrame(official_schedule)
        if not df_off.empty:
            df_off = df_off.sort_values('date')
            st.table(df_off)
            st.caption("注: 合格発表日は目安。正式な日程・時刻はCPAAOBの公表に従ってください。")
        else:
            st.info("No official schedule available.")
    with t2:
        df_exams = pd.DataFrame(mock_exams)
        if not df_exams.empty:
            st.table(df_exams)
        else:
            st.info("No mock exams scheduled.")

elif page == "Scores 📈":
    st.header("Score Tracker")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        with st.form("score_form"):
            name = st.text_input("Exam/Drill Name")
            date_val = st.date_input("Date", value=date.today())
            subject = st.selectbox("Subject", ["Financial", "Management", "Audit", "Company", "Tax", "Elective", "Total"])
            val = st.number_input("Score (%)", min_value=0, max_value=100, value=70)
            submitted = st.form_submit_button("Save Score")
            
            if submitted:
                new_score = {
                    'name': name,
                    'date': date_val.strftime("%Y-%m-%d"),
                    'subject': subject,
                    'val': val
                }
                st.session_state.data["scores"].append(new_score)
                save_data(st.session_state.data)
                st.success("Score saved!")
                
    with col2:
        if st.session_state.data["scores"]:
            df = pd.DataFrame(st.session_state.data["scores"])
            st.subheader("History")
            st.dataframe(df.sort_values('date', ascending=False))
            st.download_button("Download Scores CSV", data=df.to_csv(index=False).encode('utf-8'), file_name="scores.csv", mime="text/csv")
            
            # Line Chart
            st.subheader("Trend")
            fig = go.Figure()
            for sub in df['subject'].unique():
                sub_df = df[df['subject'] == sub].sort_values('date')
                fig.add_trace(go.Scatter(x=sub_df['date'], y=sub_df['val'], mode='lines+markers', name=sub))
            fig.update_layout(yaxis_range=[0, 100])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No scores recorded yet.")

elif page == "Drills 🔧":
    st.header("Drills ✏️")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Select Topic")
        subject = st.radio("Subject", ["Financial", "Management", "Audit", "Company"])
        
        st.subheader("Select Level")
        level = st.radio("Level", ["Level 1 (Basic)", "Level 2 (Standard)", "Level 3 (Advanced)", "Vocabulary (Important Words)"])
        level_map = {
            "Level 1 (Basic)": 1, 
            "Level 2 (Standard)": 2, 
            "Level 3 (Advanced)": 3,
            "Vocabulary (Important Words)": "vocab"
        }
        selected_level = level_map[level]
        
        if selected_level == "vocab":
            st.info("💡 Hint: These are key English terms often found in global accounting standards (IFRS/US GAAP).")
            
            # Add Tangocyo List View
            with st.expander("📖 View Vocabulary List (Tangocyo)"):
                vocab_list_view = vocab_data.get(subject, [])
                if vocab_list_view:
                    for v in vocab_list_view:
                        st.markdown(f"**{v['term']}** ({v['jp']})")
                        st.markdown(f"- 🇯🇵 {v['desc']}")
                        st.markdown(f"- 🇺🇸 {v.get('desc_en', '')}")
                        st.divider()
                else:
                    st.warning("No vocabulary data available.")
    
        # Load generated questions if available and not already loaded
        if 'generated_questions' not in st.session_state:
            try:
                with open('questions.json', 'r', encoding='utf-8') as f:
                    st.session_state.generated_questions = json.load(f)
            except FileNotFoundError:
                st.session_state.generated_questions = {}

        if st.button("Start / Restart Quiz"):
            import random
            st.session_state.quiz_state['active'] = True
            st.session_state.quiz_state['subject'] = subject
            st.session_state.quiz_state['level'] = selected_level
            st.session_state.quiz_state['q_index'] = 0
            st.session_state.quiz_state['score'] = 0
            st.session_state.quiz_state['show_feedback'] = False
            st.session_state.quiz_state['selected_option'] = None
            
            # Select questions based on level
            if selected_level == "vocab":
                vocab_list = vocab_data.get(subject, [])
                if vocab_list:
                    vocab_questions = []
                    for v in vocab_list:
                        vocab_questions.append({
                            'q': f"【重要語句】 「{v['term']}」 の意味として最も適切なものは？",
                            'options': [v['desc'], "（誤りの選択肢: 逆の意味）", "（誤りの選択肢: 無関係な定義）", "（誤りの選択肢: 類似用語の定義）"],
                            'correct': 0,
                            'explanation': f"**{v['term']} ({v['jp']})**\n\n**🇯🇵 日本語:** {v['desc']}\n\n**🇺🇸 English:** {v.get('desc_en', 'No English description available.')}",
                            'type': 'vocab'
                        })
                    # Shuffle options for each question
                    for q in vocab_questions:
                        correct_opt = q['options'][0]
                        random.shuffle(q['options'])
                        q['correct'] = q['options'].index(correct_opt)
                    
                    st.session_state.quiz_state['questions'] = vocab_questions
                else:
                    st.warning(f"No vocabulary data for {subject} yet.")
                    st.session_state.quiz_state['active'] = False
            
            elif selected_level == 2 or selected_level == 3:
                # Use generated questions for Level 2/3
                gen_qs = st.session_state.generated_questions.get(subject, [])
                level_gen_qs = [q for q in gen_qs if q.get('level') == selected_level]
                
                if level_gen_qs:
                     # Pick 10 random questions
                    if len(level_gen_qs) > 10:
                        st.session_state.quiz_state['questions'] = random.sample(level_gen_qs, 10)
                    else:
                        st.session_state.quiz_state['questions'] = level_gen_qs
                else:
                    st.warning(f"No generated questions for {subject} Level {selected_level} yet.")
                    st.session_state.quiz_state['active'] = False

            else:
                # Level 1 (Static questions + Generated Level 0)
                raw_questions = drill_questions.get(subject, [])
                # Filter for Level 1 or undefined (legacy)
                static_level1 = [q for q in raw_questions if q.get('level', 1) == 1]
                
                # Fetch Level 0 from generated questions
                gen_qs = st.session_state.generated_questions.get(subject, [])
                level0_gen_qs = [q for q in gen_qs if q.get('level') == 0]
                
                # Merge
                all_level1_questions = static_level1 + level0_gen_qs
                
                if all_level1_questions:
                    # Random sample if too many
                    if len(all_level1_questions) > 10:
                        st.session_state.quiz_state['questions'] = random.sample(all_level1_questions, 10)
                    else:
                        st.session_state.quiz_state['questions'] = all_level1_questions
                else:
                    st.warning(f"No questions found for {subject} Level 1.")
                    st.session_state.quiz_state['active'] = False
                
    with col2:
        qs = st.session_state.quiz_state
        if qs['active']:
            current_q = qs['questions'][qs['q_index']]
            total_q = len(qs['questions'])
            
            st.subheader(f"Question {qs['q_index'] + 1} / {total_q}")
            st.markdown(f"**{current_q['q']}**")
            
            # Options
            options = current_q['options']
            
            # If feedback is shown, disable interaction or show result
            if qs['show_feedback']:
                for idx, opt in enumerate(options):
                    if idx == current_q['correct']:
                        st.markdown(f"<div class='correct-answer'>{opt} (Correct)</div>", unsafe_allow_html=True)
                    elif idx == qs['selected_option']:
                        st.markdown(f"<div class='incorrect-answer'>{opt} (Your Answer)</div>", unsafe_allow_html=True)
                    else:
                        st.text(opt)
                
                st.markdown("### Explanation")
                st.info(current_q['explanation'])
                if qs['selected_option'] is not None and qs['selected_option'] != current_q['correct']:
                    err = st.radio("Tag your error", ["careless", "concept", "guess", "time"], horizontal=True, key=f"err_{qs['q_index']}")
                    if st.button("Save Tag", key=f"save_err_{qs['q_index']}"):
                        idx = getattr(st.session_state, 'last_wrong_idx', None)
                        try:
                            if idx is not None and idx < len(st.session_state.data.get('wrong_answers', [])):
                                st.session_state.data['wrong_answers'][idx]['error_type'] = err
                                save_data(st.session_state.data)
                                st.toast("Tag saved", icon="✅")
                            else:
                                st.warning("No recent wrong answer to tag.")
                        except Exception:
                            pass
                
                if qs['q_index'] < total_q - 1:
                    if st.button("Next Question"):
                        qs['q_index'] += 1
                        qs['show_feedback'] = False
                        qs['selected_option'] = None
                        st.rerun()
                else:
                    score = qs['score']
                    st.success(f"Quiz Completed! Score: {score} / {total_q}")
                    
                    if st.button("Finish & Claim XP"):
                        # XP Logic
                        earned_xp = score * 10
                        current_xp = st.session_state.data.get('xp', 0)
                        current_level = st.session_state.data.get('level', 1)
                        
                        new_xp = current_xp + earned_xp
                        required_xp = current_level * 100
                        
                        leveled_up = False
                        while new_xp >= required_xp:
                            new_xp -= required_xp
                            current_level += 1
                            required_xp = current_level * 100
                            leveled_up = True
                        
                        st.session_state.data['xp'] = new_xp
                        st.session_state.data['level'] = current_level
                        
                        # Save score history
                        st.session_state.data["scores"].append({
                            'name': f"Drill: {qs.get('subject', 'General')} Lv{qs.get('level', '?')}",
                            'date': date.today().strftime("%Y-%m-%d"),
                            'subject': qs.get('subject', 'General'),
                            'val': (score / total_q) * 100 if total_q > 0 else 0
                        })
                        save_data(st.session_state.data)
                        
                        if leveled_up:
                            st.balloons()
                            st.success(f"LEVEL UP! You are now Level {current_level}!")
                        else:
                            st.success(f"Earned {earned_xp} XP!")
                            
                        qs['active'] = False
                        st.rerun()
                        
            else:
                choice = st.radio("Choose Answer:", options, index=None, key=f"q_{qs['q_index']}")
                conf = st.select_slider("Confidence (1-5)", options=[1,2,3,4,5], value=3, key=f"conf_{qs['q_index']}")
                if st.button("Submit Answer"):
                    if choice:
                        selected_idx = options.index(choice)
                        qs['selected_option'] = selected_idx
                        qs['show_feedback'] = True
                        if selected_idx != current_q['correct']:
                            wrong_entry = {
                                'date': date.today().strftime("%Y-%m-%d"),
                                'subject': qs.get('subject', 'General'),
                                'level': qs.get('level', None),
                                'q': current_q.get('q', ''),
                                'options': current_q.get('options', []),
                                'correct_idx': current_q.get('correct', None),
                                'selected_idx': selected_idx,
                                'explanation': current_q.get('explanation', ''),
                                'confidence': int(conf)
                            }
                            st.session_state.data.setdefault('wrong_answers', []).append(wrong_entry)
                            st.session_state.last_wrong_idx = len(st.session_state.data['wrong_answers']) - 1
                            save_data(st.session_state.data)
                        if selected_idx == current_q['correct']:
                            qs['score'] += 1
                        st.rerun()
                    else:
                        st.warning("Please select an option.")
        else:
            st.info("Select a subject and level from the sidebar to start.")

elif page == "Wrong Answers 📕":
    st.header("Wrong Answers")
    wa = st.session_state.data.get('wrong_answers', [])
    if not wa:
        st.info("No wrong answers recorded yet.")
    else:
        df = pd.DataFrame(wa)
        subjects = sorted([s for s in df['subject'].dropna().unique()])
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            sub = st.selectbox("Subject", ["All"] + subjects)
        with c2:
            n = st.number_input("Retry count", min_value=5, max_value=50, value=20)
        with c3:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", data=csv, file_name="wrong_answers.csv", mime="text/csv")
        cc1, cc2 = st.columns([1,1])
        with cc1:
            if st.button("Clear All", type="secondary"):
                st.session_state.data['wrong_answers'] = []
                save_data(st.session_state.data)
                st.rerun()
        if sub != "All":
            df = df[df['subject'] == sub]
        st.dataframe(df[['date','subject','level','q']].sort_values('date', ascending=False), use_container_width=True)
        if not df.empty:
            if st.button("Retry 20"):
                import random
                sample = df.sample(min(len(df), n)).to_dict(orient='records')
                qs = []
                for r in sample:
                    opts = r.get('options', [])
                    correct_idx = r.get('correct_idx', None)
                    if opts and correct_idx is not None:
                        qs.append({
                            'q': r.get('q',''),
                            'options': opts,
                            'correct': correct_idx,
                            'explanation': r.get('explanation','')
                        })
                if qs:
                    st.session_state.quiz_state['active'] = True
                    st.session_state.quiz_state['subject'] = sub if sub != "All" else "Mixed"
                    st.session_state.quiz_state['level'] = "Retry"
                    st.session_state.quiz_state['q_index'] = 0
                    st.session_state.quiz_state['score'] = 0
                    st.session_state.quiz_state['show_feedback'] = False
                    st.session_state.quiz_state['selected_option'] = None
                    st.session_state.quiz_state['questions'] = qs
                    st.toast("Retry started", icon="✅")
                    st.rerun()

elif page == "Exam Mode ⏲️":
    st.header("Exam Mode")
    if 'exam' not in st.session_state:
        st.session_state.exam = {'active': False, 'start_ts': None, 'duration_min': 30, 'q_index': 0, 'questions': [], 'answers': [], 'finished': False, 'subject': 'Mixed'}
    ex = st.session_state.exam
    if not ex['active'] and not ex['finished']:
        subject = st.selectbox("Subject", ["Mixed", "Financial", "Management", "Audit", "Company"])
        qcount = st.number_input("Number of Questions", min_value=10, max_value=60, value=20, step=5)
        duration = st.number_input("Time Limit (minutes)", min_value=10, max_value=180, value=60, step=5)
        if st.button("Start Exam", type="primary", use_container_width=True):
            import time, random
            ex['active'] = True
            ex['finished'] = False
            ex['start_ts'] = int(time.time())
            ex['duration_min'] = int(duration)
            ex['q_index'] = 0
            pool = []
            if subject == "Mixed":
                for sub, qs in drill_questions.items():
                    for q in qs:
                        qx = q.copy()
                        qx['subject'] = sub
                        pool.append(qx)
            else:
                for q in drill_questions.get(subject, []):
                    qx = q.copy()
                    qx['subject'] = subject
                    pool.append(qx)
            random.shuffle(pool)
            ex['questions'] = pool[:int(qcount)]
            ex['answers'] = [None] * len(ex['questions'])
            ex['subject'] = subject
            st.rerun()
    elif ex['active'] and not ex['finished']:
        import time
        now = int(time.time())
        elapsed = now - int(ex['start_ts'])
        remain = max(0, ex['duration_min'] * 60 - elapsed)
        mm = remain // 60
        ss = remain % 60
        st.metric("Time Remaining", f"{mm:02d}:{ss:02d}")
        if remain == 0:
            ex['finished'] = True
            ex['active'] = False
            st.rerun()
        q = ex['questions'][ex['q_index']]
        st.markdown(f"**[{q.get('subject','')}] Q{ex['q_index']+1}/{len(ex['questions'])}**")
        st.write(q['q'])
        key = f"exam_{ex['q_index']}"
        sel = st.radio("Select answer", q['options'], index=ex['answers'][ex['q_index']] if ex['answers'][ex['q_index']] is not None else None, key=key)
        if st.button("Save Answer"):
            ex['answers'][ex['q_index']] = q['options'].index(sel) if sel else None
            st.rerun()
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Prev") and ex['q_index'] > 0:
                ex['q_index'] -= 1
                st.rerun()
        with c2:
            if st.button("Next") and ex['q_index'] < len(ex['questions']) - 1:
                ex['q_index'] += 1
                st.rerun()
        with c3:
            if st.button("Finish Now", type="primary"):
                ex['finished'] = True
                ex['active'] = False
                st.rerun()
    else:
        corrects = 0
        for i, q in enumerate(st.session_state.exam['questions']):
            a = st.session_state.exam['answers'][i]
            if a is not None and a == q.get('correct'):
                corrects += 1
        total = max(1, len(st.session_state.exam['questions']))
        percent = round(corrects / total * 100, 1)
        st.success(f"Finished. Score: {corrects}/{total} ({percent}%)")
        earned_xp = corrects * 10
        curr_xp = st.session_state.data.get('xp', 0)
        curr_level = st.session_state.data.get('level', 1)
        new_xp = curr_xp + earned_xp
        req = curr_level * 100
        leveled = False
        while new_xp >= req:
            new_xp -= req
            curr_level += 1
            req = curr_level * 100
            leveled = True
        st.session_state.data['xp'] = new_xp
        st.session_state.data['level'] = curr_level
        st.session_state.data["scores"].append({
            'name': f"Exam Mode ({st.session_state.exam.get('subject','Mixed')})",
            'date': date.today().strftime("%Y-%m-%d"),
            'subject': st.session_state.exam.get('subject','Mixed'),
            'val': percent
        })
        save_data(st.session_state.data)
        if earned_xp > 0:
            if leveled:
                st.balloons()
                st.success(f"+{earned_xp} XP, Level {curr_level}")
            else:
                st.info(f"+{earned_xp} XP added")
        with st.expander("Review"):
            for i, q in enumerate(st.session_state.exam['questions']):
                st.markdown(f"**Q{i+1}.** {q['q']}")
                a = st.session_state.exam['answers'][i]
                for idx, opt in enumerate(q['options']):
                    if idx == q.get('correct'):
                        st.markdown(f"- ✅ {opt}")
                    elif a is not None and idx == a:
                        st.markdown(f"- ❌ {opt}")
                    else:
                        st.markdown(f"- {opt}")
                st.caption(q.get('explanation',''))
                st.divider()
        if st.button("Reset Exam"):
            st.session_state.exam = {'active': False, 'start_ts': None, 'duration_min': 30, 'q_index': 0, 'questions': [], 'answers': [], 'finished': False, 'subject': 'Mixed'}
            st.rerun()

elif page == "Survival Mode ⚡":
    st.header("⚡ Survival Mode")
    st.markdown("### Challenge your limits! 3 Strikes and you're out.")
    
    # Initialize State
    if 'survival' not in st.session_state:
        st.session_state.survival = {
            'active': False,
            'lives': 3,
            'streak': 0,
            'score': 0,
            'q': None,
            'feedback': False,
            'user_ans': None,
            'target_streak': "Unlimited"
        }
    
    ss = st.session_state.survival
    
    # Load Questions Logic
    if 'all_questions' not in st.session_state:
        all_qs = []
        # Static
        for sub, qs in drill_questions.items():
            for q in qs:
                # Create a copy to avoid modifying original
                q_copy = q.copy()
                q_copy['subject'] = sub
                all_qs.append(q_copy)
        # Generated
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'questions.json')
        if os.path.exists(json_path):
             try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    gen_qs = json.load(f)
                    for sub, qs in gen_qs.items():
                        for q in qs:
                            q_copy = q.copy()
                            q_copy['subject'] = sub
                            all_qs.append(q_copy)
             except:
                 pass
        st.session_state.all_questions = all_qs
    
    if not ss['active']:
        st.subheader("Select Challenge Mode")
        streak_target = st.radio("Target Streak", ["Unlimited", 1, 5, 10], horizontal=True, format_func=lambda x: "∞ Unlimited" if x == "Unlimited" else f"Target: {x} 🔥")

        if st.button("🚀 Start Challenge", use_container_width=True):
            ss['active'] = True
            ss['lives'] = 3
            ss['streak'] = 0
            ss['score'] = 0
            ss['q'] = None
            ss['feedback'] = False
            ss['target_streak'] = streak_target
            st.rerun()
            
    else:
        # Metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Lives", "❤️" * ss['lives'])
        target_display = "∞" if ss.get('target_streak', "Unlimited") == "Unlimited" else ss['target_streak']
        c2.metric("Streak", f"🔥 {ss['streak']} / {target_display}")
        c3.metric("Score", ss['score'])
        
        target = ss.get('target_streak', "Unlimited")
        is_win = target != "Unlimited" and ss['streak'] >= target

        if ss['lives'] <= 0 or is_win:
            if is_win:
                st.balloons()
                st.success(f"🎉 MISSION ACCOMPLISHED! You reached a {ss['streak']} streak!")
            else:
                st.error("💀 GAME OVER")
            
            st.markdown(f"### Final Score: {ss['score']}")
            
            # Save High Score
            if ss['score'] > 0:
                st.session_state.data["scores"].append({
                    'name': f"Survival Mode ⚡ (Target {target})",
                    'date': date.today().strftime("%Y-%m-%d"),
                    'subject': 'Survival',
                    'val': ss['score'] # Just storing score
                })
                save_data(st.session_state.data)
            
            if st.button("Try Again", use_container_width=True):
                ss['active'] = False
                st.rerun()
        else:
            # Get Question
            if ss['q'] is None:
                import random
                if st.session_state.all_questions:
                    q_data = random.choice(st.session_state.all_questions)
                    # Shuffle options
                    opts = q_data['options'].copy()
                    correct_text = q_data['options'][q_data['correct']]
                    random.shuffle(opts)
                    
                    ss['q'] = {
                        'q': q_data['q'],
                        'options': opts,
                        'correct_idx': opts.index(correct_text),
                        'explanation': q_data['explanation'],
                        'subject': q_data.get('subject', 'General')
                    }
                else:
                    st.error("No questions found!")
                    st.stop()
            
            q = ss['q']
            
            st.markdown(f"**[{q['subject']}]** {q['q']}")
            
            if not ss['feedback']:
                # Use a form to prevent reload on radio selection
                with st.form(key=f"surv_form_{ss['score']}_{ss['lives']}"):
                    ans = st.radio("Select Answer:", q['options'])
                    submit = st.form_submit_button("Submit Answer")
                    
                    if submit:
                        ss['user_ans'] = q['options'].index(ans)
                        ss['feedback'] = True
                        
                        if ss['user_ans'] == q['correct_idx']:
                            # Bonus XP for streak
                            bonus = ss['streak'] * 2
                            points = 10 + bonus
                            ss['score'] += points
                            ss['streak'] += 1
                            st.session_state.data['xp'] = st.session_state.data.get('xp', 0) + points
                            st.toast(f"Correct! +{points} XP", icon="✅")
                            
                            # Check Win
                            target = ss.get('target_streak', "Unlimited")
                            if target != "Unlimited" and ss['streak'] >= target:
                                st.rerun()
                        else:
                            ss['lives'] -= 1
                            ss['streak'] = 0
                            st.toast("Wrong Answer!", icon="❌")
                        
                        st.rerun()
            else:
                # Show Feedback
                if ss['user_ans'] == q['correct_idx']:
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Wrong! Correct: {q['options'][q['correct_idx']]}")
                
                st.info(f"**Explanation:**\n\n{q['explanation']}")
                
                if st.button("Next Question ➡", use_container_width=True):
                    ss['q'] = None
                    ss['feedback'] = False
                    st.rerun()

elif page == "Analytics 📊":
    st.header("Analytics")
    scores_df = pd.DataFrame(st.session_state.data.get("scores", []))
    logs_df = pd.DataFrame(st.session_state.data.get("logs", []))
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Skill Radar")
        subjects = ['Financial', 'Management', 'Audit', 'Company', 'Tax', 'Elective']
        radar_scores = [30] * 6
        if not scores_df.empty:
            vals = []
            for sub in subjects:
                sub_df = scores_df[scores_df['subject'] == sub]
                if not sub_df.empty:
                    vals.append(sub_df['val'].mean())
                else:
                    vals.append(30)
            radar_scores = vals
        fig = go.Figure(data=go.Scatterpolar(r=radar_scores, theta=subjects, fill='toself', name='Avg'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Pacing Histogram")
        if not logs_df.empty:
            logs_df['date'] = pd.to_datetime(logs_df['date'])
            logs_df['minutes'] = logs_df['duration']
            st.plotly_chart(px.histogram(logs_df, x='minutes', nbins=20, title="Study Session Lengths"), use_container_width=True)
        else:
            st.info("No study logs")
    st.subheader("Weekly Heatmap")
    if not logs_df.empty:
        logs_df['date'] = pd.to_datetime(logs_df['date']).dt.date
        df = logs_df.groupby('date')['duration'].sum().reset_index()
        df['dow'] = pd.to_datetime(df['date']).dt.dayofweek
        df['week'] = pd.to_datetime(df['date']).dt.isocalendar().week
        pivot = df.pivot_table(index='dow', columns='week', values='duration', fill_value=0)
        st.dataframe(pivot)
    else:
        st.info("No data for heatmap")
elif page == "Roadmap 🗺️":
    st.header("🗺️ CPA Exam Strategy Roadmap (2026-2027)")
    
    # 1. Countdown Section
    today = date.today()
    tanto_date = date(2027, 5, 23) # Estimated
    ronbun_date = date(2027, 8, 20) # Estimated
    
    days_tanto = (tanto_date - today).days
    days_ronbun = (ronbun_date - today).days
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Days to May Short Exam", f"{days_tanto} Days", "Target: Pass")
    col2.metric("Days to Aug Essay Exam", f"{days_ronbun} Days", "Final Goal")
    col3.metric("Current Phase", "Foundation (2026)", "Build Habits")
    
    st.divider()

    # 2. Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Visual Schedule (Gantt)", "🗓️ Monthly Strategy", "⏰ Daily Routine"])
    
    with tab1:
        st.subheader("Strategic Timeline")
        # Gantt Chart Data
        df_gantt = pd.DataFrame([
            dict(Task="Foundation (Fin/Mgmt)", Start='2026-02-01', Finish='2026-06-30', Phase='Phase 0: Foundation'),
            dict(Task="Audit & Company Law", Start='2026-04-01', Finish='2026-09-30', Phase='Phase 0: Foundation'),
            dict(Task="Tax Law & Electives", Start='2026-07-01', Finish='2026-12-31', Phase='Phase 0: Foundation'),
            dict(Task="Dec Short (Practice)", Start='2026-10-01', Finish='2026-12-13', Phase='Phase 0: Foundation'),
            dict(Task="Short Exam Mastery", Start='2027-01-01', Finish='2027-05-23', Phase='Phase 1: Short Exam'),
            dict(Task="Essay Sprint", Start='2027-05-24', Finish='2027-08-20', Phase='Phase 2: Essay Sprint'),
        ])
        
        # Create Gantt
        fig = px.timeline(df_gantt, x_start="Start", x_end="Finish", y="Task", color="Phase", 
                          title="CPA Exam 1.5 Year Plan",
                          color_discrete_sequence=px.colors.qualitative.Prism)
        fig.update_yaxes(autorange="reversed") # Task order top-to-bottom
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("💡 **Golden Route**: Pass May Short -> Pass August Essay in one go.")
        
        with st.expander("📅 Official Dates & Announcements"):
            try:
                df_off2 = pd.DataFrame(official_schedule).sort_values('date')
                st.table(df_off2)
                st.caption("注: 合格発表日は目安。正式な公表に従って随時更新。")
            except Exception as e:
                st.error(f"Failed to load official schedule: {e}")

    with tab2:
        st.subheader("Detailed Monthly Strategy")
        
        with st.expander("Phase 0: Foundation (2026)", expanded=True):
            st.markdown("""
            *   **Feb - Mar**: Build study habits. Focus on Fin/Mgmt Accounting basics (Calculations).
            *   **Apr - Jun**: Start Applied theory. Begin Audit & Company Law.
            *   **Jul - Sep**: **CRITICAL** Start Tax Law & Electives (Management/Statistics).
            *   **Oct - Dec**: **Dec Short Exam Challenge**. Aim for 60%+ even if you fail.
            """)
            
        with st.expander("Phase 1: Short Exam Mastery (Jan - May 2027)"):
            st.markdown("""
            *   **Jan - Mar**: Solidify basics. Aim for 75%+ in drills. Focus on weak areas.
            *   **Apr**: Mock Exams (TAC/Ohara). Analyze errors thoroughly.
            *   **May**: Peak conditioning. Rote memorization of text (Audit/Company Law). **PASS EXAM**.
            """)
            
        with st.expander("Phase 2: Essay Sprint (Jun - Aug 2027)"):
            st.markdown("""
            *   **Jun**: Revive Tax/Elective knowledge (often forgotten during Short prep).
            *   **Jul**: Output training (Writing). Learn "Key Phrases" for theory questions.
            *   **Aug**: Final adjustments. Health management is key. **PASS EXAM**.
            """)

    with tab3:
        st.subheader("⏰ Ideal Daily Routine (Student/Full-time Study)")
        
        schedule_data = [
            {"Time": "07:00 - 08:00", "Activity": "Wake up / Light Breakfast / Review Vocab"},
            {"Time": "08:00 - 11:00", "Activity": "🧠 **Deep Work 1**: Financial Accounting (Calc) - 3h"},
            {"Time": "11:00 - 12:00", "Activity": "Lunch / Nap (20m)"},
            {"Time": "12:00 - 15:00", "Activity": "🧠 **Deep Work 2**: Management Accounting / Theory - 3h"},
            {"Time": "15:00 - 16:00", "Activity": "Gym / Walk / Break"},
            {"Time": "16:00 - 19:00", "Activity": "🧠 **Deep Work 3**: Corporate Law / Audit - 3h"},
            {"Time": "19:00 - 20:00", "Activity": "Dinner / Relax"},
            {"Time": "20:00 - 22:00", "Activity": "📖 **Review**: Weak areas / Next day planning - 2h"},
            {"Time": "22:00 - 23:00", "Activity": "Wind down / Sleep"},
        ]
        st.table(pd.DataFrame(schedule_data))
        st.success("Target: **10+ Hours/Day** of high-quality study.")

elif page == "Big 4 Job Hunting 💼":
    st.header("🏢 Big 4 CPA Job Hunting Strategy")
    st.markdown("Strategy guide and comparison for the major audit firms in Japan.")

    tab1, tab2, tab_depts, tab3, tab4, tab5 = st.tabs(["Strategy & Timeline", "Big 4 Comparison", "Departments (FAS/Tax/...) 🏢", "Tech & Data Science Advantage 🤖", "Boston Career Forum 🇺🇸", "Interview & Case Prep 📝"])

    with tab1:
        st.subheader("📅 Job Hunting Timeline (Typical)")
        st.info("The job hunting season for CPA candidates peaks immediately after the August Essay Exam.")
        
        timeline_data = [
            {"Period": "August (Late)", "Activity": "Essay Exam Ends", "Details": "Rest for a few days, then prepare for briefings."},
            {"Period": "September", "Activity": "Firm Briefings (Setsumeikai)", "Details": "Attend online/offline sessions. Key for networking."},
            {"Period": "October", "Activity": "Entry Sheet (ES) Submission", "Details": "Prepare resumes. Focus on 'Why this firm?'"},
            {"Period": "November (Mid)", "Activity": "Results Announcement", "Details": "Official passing results released."},
            {"Period": "November (Late)", "Activity": "Interviews & Offers", "Details": "Intensive interview period (1-2 weeks). Offers issued quickly."}
        ]
        st.table(pd.DataFrame(timeline_data))

        st.subheader("💡 Key Strategies")
        st.markdown("""
        *   **Start Early**: Don't wait for the results. Attend briefings in September.
        *   **Differentiate**: All Big 4 do audit. Focus on culture, specific clients (e.g., Tech, Auto), or non-audit opportunities (IPO, Advisory).
        *   **Networking**: Use alumni connections (OB/OG Visits) if possible.
        """)

    with tab2:
        st.subheader("📊 Big 4 Audit Firms vs. Tech Giants Comparison")
        
        # Personalized Ranking Section
        st.markdown("### 🏆 Personalized Ranking for You (ML/DS Master's Student)")
        st.info("""
        Based on your **CPA Goal** + **ML/Data Science Strength**, here is your recommended priority:
        
        1.  🥇 **PwC Aarata / EY ShinNihon**: Best balance of **Digital Audit** innovation and **CPA License** support. Both have dedicated "Digital" tracks for auditors.
        2.  🥈 **Deloitte Tohmatsu**: Massive scale and data access. Great for "Audit Analytics" but slightly more traditional hierarchy.
        3.  🥉 **Accenture / IBM**: **Top Tier for Tech**, but ⚠️ **WARNING**: You likely **cannot** complete the CPA practical experience (Jitsumu Hoshu) requirement here. Great for *after* getting your CPA, or if you pivot to Consulting.
        """)

        # Radar Chart
        st.subheader("Visual Comparison (Illustrative)")
        categories = ['Tech/AI Focus', 'Global Network', 'Domestic Scale', 'IPO/Venture', 'Work-Life Balance']

        fig = go.Figure()

        # Tohmatsu (Deloitte)
        fig.add_trace(go.Scatterpolar(
            r=[4, 5, 5, 5, 3],
            theta=categories,
            fill='toself',
            name='Tohmatsu (Deloitte)'
        ))
        # AZSA (KPMG)
        fig.add_trace(go.Scatterpolar(
            r=[3, 4, 5, 3, 4],
            theta=categories,
            fill='toself',
            name='AZSA (KPMG)'
        ))
        # EY ShinNihon
        fig.add_trace(go.Scatterpolar(
            r=[5, 4, 4, 3, 3],
            theta=categories,
            fill='toself',
            name='EY ShinNihon'
        ))
        # PwC Aarata
        fig.add_trace(go.Scatterpolar(
            r=[5, 5, 3, 2, 4],
            theta=categories,
            fill='toself',
            name='PwC Aarata'
        ))
        # Accenture (Comparison)
        fig.add_trace(go.Scatterpolar(
            r=[5, 5, 5, 2, 2],
            theta=categories,
            fill='toself',
            name='Accenture (Ref)'
        ))
        # IBM (Comparison)
        fig.add_trace(go.Scatterpolar(
            r=[5, 5, 4, 1, 4],
            theta=categories,
            fill='toself',
            name='IBM (Ref)'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5]
                )),
            showlegend=True,
            height=500,
            margin=dict(l=40, r=40, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("🏢 Firm Details")
        firms_data = [
            {
                "Firm Name (JP)": "有限責任監査法人トーマツ (Tohmatsu)",
                "Network": "Deloitte",
                "Key Strengths": "Largest scale, aggressive growth, strong in IPOs and Venture support.",
                "Culture": "Meritocratic, Sports-oriented, High energy.",
                "Link": "https://www2.deloitte.com/jp/ja/pages/audit/topics/recruit-index.html"
            },
            {
                "Firm Name (JP)": "有限責任 あずさ監査法人 (AZSA)",
                "Network": "KPMG",
                "Key Strengths": "Balanced portfolio, strong domestic manufacturing clients.",
                "Culture": "Conservative, Collaborative, 'Gentlemanly'.",
                "Link": "https://home.kpmg/jp/ja/home/careers.html"
            },
            {
                "Firm Name (JP)": "EY新日本有限責任監査法人 (EY ShinNihon)",
                "Network": "EY",
                "Key Strengths": "Long history, large number of listed clients, strong Digital Audit focus.",
                "Culture": "Traditional yet transforming, Diversity focus.",
                "Link": "https://www.ey.com/ja_jp/careers/audit"
            },
            {
                "Firm Name (JP)": "PwCあらた有限責任監査法人 (PwC Aarata)",
                "Network": "PwC",
                "Key Strengths": "Global integration, strong advisory connection, newer organizational style.",
                "Culture": "Global, Flat hierarchy, Innovative.",
                "Link": "https://www.pwc.com/jp/ja/careers/audit.html"
            },
            {
                "Firm Name (JP)": "アクセンチュア (Accenture)",
                "Network": "Accenture",
                "Key Strengths": "Absolute leader in DX/IT Consulting. High salary.",
                "Culture": "Up or Out (Evolving), High performance, Tech-first.",
                "Link": "https://www.accenture.com/jp-ja/careers"
            },
            {
                "Firm Name (JP)": "日本IBM (IBM Japan)",
                "Network": "IBM",
                "Key Strengths": "Deep research (Watson), Hybrid Cloud, Legacy stability.",
                "Culture": "Engineering-driven, Mature, Good work-life balance.",
                "Link": "https://www.ibm.com/jp-ja/employment"
            }
        ]
        
        # Display as a styled table or cards
        for firm in firms_data:
            with st.expander(f"{firm['Firm Name (JP)']} ({firm['Network']})", expanded=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**Strengths:** {firm['Key Strengths']}")
                    st.markdown(f"**Culture:** {firm['Culture']}")
                with col2:
                    st.link_button("Recruit Page", firm['Link'])

    with tab_depts:
        st.subheader("🏢 Service Lines & Business Units")
        st.markdown("Beyond Audit: Understanding the different career paths within Big 4.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔍 Audit & Assurance (監査・保証)")
            st.info("""
            **The Core Business.**
            *   **Role:** Examining financial statements to ensure accuracy and compliance.
            *   **Pros:** Stability, clear career path, high demand for CPAs.
            *   **Cons:** Can be repetitive, busy season is intense.
            *   **For You:** "Digital Audit" roles are growing fast here.
            """)
            
            st.markdown("### 💰 Financial Advisory (FAS)")
            st.warning("""
            **The "Deal" Makers.**
            *   **Role:** M&A support, Valuations, Due Diligence, Forensic investigations.
            *   **Pros:** High compensation, dynamic work, exposure to high-level strategy.
            *   **Cons:** Very high pressure, long hours, up-or-out culture.
            *   **For You:** **Forensic Technology** (Fraud Detection) is a perfect fit for Data Science skills.
            """)

        with col2:
            st.markdown("### ⚖️ Tax (税務)")
            st.info("""
            **The Specialists.**
            *   **Role:** Corporate tax compliance, Transfer Pricing, International Tax.
            *   **Pros:** Deep expertise, high autonomy, stable.
            *   **Cons:** Highly specialized (niche), constant regulatory changes.
            *   **For You:** "Tax Technology" is emerging, but less common for new grads than Audit.
            """)
            
            st.markdown("### 🚀 Consulting (コンサルティング)")
            st.success("""
            **The Problem Solvers.**
            *   **Role:** Strategy, IT Implementation, Operations improvement.
            *   **Note:** Usually a separate entity (e.g., Deloitte Tohmatsu Consulting vs. Deloitte Tohmatsu Audit).
            *   **Pros:** Variety of projects, high pay.
            *   **Cons:** Travel, unstable workload, "Jack of all trades" risk.
            """)

    with tab3:
        st.subheader("🤖 Leveraging Data Science & ML in CPA Job Hunting")
        st.markdown("""
        **Profile:** Double Degree Master's Student (Keio 🇯🇵 & Leibniz Hannover 🇩🇪) | **Major:** Mechanical Engineering
        
        **Your Technical Arsenal:**
        *   **Advanced ML:** Graph Neural Networks (GNNs), PyTorch, Bayesian Inference (MCMC/TMCMC).
        *   **Engineering:** Finite Element Analysis (FEA), Structural Health Monitoring.
        *   **Languages:** Python, MATLAB, TypeScript.
        
        Your background is a **massive differentiator** in the modern audit industry. All Big 4 firms are heavily investing in "Audit Transformation" and "Digital Audit".
        """)

        st.markdown("---")
        st.markdown("### 📚 Recommended Reading")
        st.markdown("""
        > **[The State of Generative AI in the Enterprise (Deloitte)](https://www.deloitte.com/global/en/issues/generative-ai/state-of-ai-in-enterprise.html)**  
        > *This report highlights how enterprises are adopting GenAI. Essential reading for interviews to show commercial awareness.*
        """)
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 Target Roles")
            st.success("**1. Digital Audit Specialist**")
            st.markdown("Work at the intersection of Audit and Tech. Use Python/SQL to analyze full population data instead of sampling.")
            
            st.success("**2. AI Governance / Algorithm Assurance**")
            st.markdown("Audit AI models! With your GNN/Bayesian background, you can audit complex *algorithms* themselves, not just the financial numbers.")
            
            st.success("**3. Financial Advisory (FAS) - Forensics**")
            st.markdown("Your experience in 'Defect Localization' translates perfectly to **Fraud Detection** (finding anomalies in massive datasets).")

        with col2:
            st.markdown("### 💡 Strategic Actions")
            st.info("**Resume / Entry Sheet (ES)**")
            st.markdown("*   **Highlight Research**: Explicitly mention your GNN work for Aerospace/CFRP. It shows you can handle *complex, unstructured data*.")
            st.markdown("*   **Keywords**: `PyTorch`, `Bayesian Inference`, `Uncertainty Quantification`, `End-to-End Pipelines`.")
            
            st.info("**Interview Questions to Ask**")
            st.markdown("*   *\"How can I apply Bayesian methods to audit risk assessment?\"*\n*   *\"Does your firm analyze unstructured data (like contracts/images) using GNNs or NLP?\"*")
            
            st.info("**Firm-Specific Tech Vibes**")
            st.markdown("""
            *   **EY**: Very strong brand in "Digital Audit". Has "EY Digital" specific recruiting tracks.
            *   **PwC**: Strong on "Tech-enablement". "Digital Upskilling" for all staff is a key slogan.
            *   **Deloitte**: "Audit Analytics" is a core part of their massive scale.
            *   **KPMG**: "Digital Innovation" focus, often collaborative with their consulting arm.
            """)

    with tab4:
        st.subheader("🇺🇸 Boston Career Forum (BCF)")
        st.markdown("The world's largest job fair for Japanese-English bilinguals. **Crucial for Master's students.**")
        
        st.info("💡 **Why BCF for You?**\n*   **Speed**: Offers (Naitei) often given in 3 days (Fri-Sun).\n*   **Positions**: Big 4 hires for **Advisory/Consulting** heavily here, not just Audit.\n*   **Timing**: Held in November, aligning perfectly with post-essay exam period.")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📅 Timeline")
            st.markdown("""
            *   **Aug-Sep**: Registration & Resume Upload.
            *   **Sep-Oct**: Online Applications & Skype Interviews (Pre-event).
            *   **Nov (Event)**: Walk-ins (Risky) vs. Scheduled Interviews (Safe).
            """)
        with col2:
            st.markdown("### 🎯 Strategy")
            st.markdown("""
            *   **Pre-Event is King**: Secure interviews *before* flying to Boston.
            *   **Target**: Big 4 (US & Japan offices), Consulting (MBB/Accenture), Tech.
            *   **Dinner Invitations**: If you do well, you get invited to dinner. This is effectively the final interview.
            """)
        st.link_button("BCF Official Site", "https://careerforum.net/en/event/bos/")

    with tab5:
        st.subheader("📝 Interview & Case Prep: The 'Master' Level")
        
        st.info("💡 **Goal**: Move beyond 'prepared answers'. Show **Intellectual Curiosity** and **Professional Maturity**.")

        # --- Interactive Mock Interview ---
        st.markdown("### 🤖 Mock Interview Simulator")
        mock_mode = st.radio("Select Mode:", ["Behavioral (HR/Partner)", "Technical (Audit/Accounting)", "Case/Logic (Consulting)", "Buy-Side (Investment)"], horizontal=True)
        
        if st.button("🎲 Generate Question"):
            import random
            
            if "Behavioral" in mock_mode:
                q_bank = [
                    {"q": "Why do you want to be a CPA instead of an Engineer?", "hint": "Connect 'Reliability' in Engineering to 'Assurance' in Audit."},
                    {"q": "Why our firm specifically? (Why not others?)", "hint": "Mention specific culture, clients (Tech/Auto), or digital initiatives."},
                    {"q": "Tell me about a time you failed.", "hint": "Focus on the **Lesson Learned** and **Improvement**, not the failure itself."},
                    {"q": "How do you handle disagreement with a team member?", "hint": "Emphasize **Listening**, **Data-driven discussion**, and **Shared Goals**."},
                    {"q": "What is your career plan for the next 5-10 years?", "hint": "Be ambitious but realistic. 'Digital Audit Specialist' -> 'Project Manager'."},
                    {"q": "Describe your research in simple terms to a 10-year-old.", "hint": "Tests communication skills. Avoid jargon. Use analogies."}
                ]
            elif "Technical" in mock_mode:
                q_bank = [
                    {"q": "What is the difference between 'Audit' and 'Advisory'?", "hint": "Audit = Assurance (Past/Present). Advisory = Consulting (Future/Improvement)."},
                    {"q": "Explain 'Materiality' in Audit.", "hint": "The threshold above which a misstatement would influence decision making."},
                    {"q": "How would you audit a company with massive data volumes?", "hint": "ITAC (IT Application Controls) + Data Analytics (Full population testing)."},
                    {"q": "What are the risks of using AI in financial reporting?", "hint": "Black box logic, Bias, Hallucinations, Lack of audit trail."},
                    {"q": "Explain the concept of 'Going Concern'.", "hint": "The assumption that a company will continue operating in the foreseeable future."}
                ]
            elif "Case/Logic" in mock_mode: # Case
                q_bank = [
                    {"q": "Estimate the number of smartphones sold in Japan annually.", "hint": "Pop (125M) x Penetration (80%) / Replacement Cycle (3 years)."},
                    {"q": "A client's profit is down 20%. How do you analyze it?", "hint": "Revenue vs Cost. Price x Vol. Fixed vs Variable. External vs Internal."},
                    {"q": "Should a Japanese auto-maker enter the EV market in India?", "hint": "Market Size, Competition, Regulation, Infrastructure, Capabilities."},
                    {"q": "How would you use AI to improve audit efficiency?", "hint": "Automated document review, Anomaly detection in journals, Chatbot for inquiries."}
                ]
            else: # Buy-Side
                q_bank = [
                    {"q": "Pitch a stock you would buy today (Japan-listed).", "hint": "Thesis, Catalysts, Valuation (PE/EV/EBITDA/DCF), Risks."},
                    {"q": "Walk me through an LBO model at a high level.", "hint": "Sources & Uses, Leverage, Operating Case, Exit Multiple, IRR/MOIC."},
                    {"q": "How would you diligence a mid-cap manufacturing target?", "hint": "Unit economics, customers, order backlog, capex, working capital seasonality."},
                    {"q": "What is your investment edge as a CPA + Engineer?", "hint": "Accounting quality + Technical moat assessment + Data skills."}
                ]
            
            selected = random.choice(q_bank)
            st.session_state['mock_q'] = selected
            st.session_state['show_hint'] = False
        
        if 'mock_q' in st.session_state:
            st.markdown(f"#### ❓ Q: {st.session_state['mock_q']['q']}")
            
            if st.button("Show Hint / Direction"):
                st.session_state['show_hint'] = not st.session_state.get('show_hint', False)
                
            if st.session_state.get('show_hint', False):
                st.success(f"💡 **Direction**: {st.session_state['mock_q']['hint']}")
        
        st.divider()

        # --- Case Interview Prep ---
        st.markdown("### 🧮 Case Interview Prep")
        with st.expander("Framework Cheatsheet（フレームワーク早見）", expanded=False):
            st.markdown("""
            - Profitability: Profit = Price×Volume − Fixed − Variable
            - Market Sizing: Top-down (Population→Penetration→Frequency) / Bottom-up (Units×Price)
            - Growth: New customers / ARPU / Retention / New products / Geographies
            - Cost Cut: COGS（材料/歩留/物流）× 稼働率、SG&A（人件費/広告/IT）
            - Pricing: Value-based / Cost-plus / Competitive parity / Segmentation
            - Investment: Thesis / Catalysts / Moat / Valuation / Risks
            """)
        with st.expander("Quick Calculators（即席計算）", expanded=False):
            col_q1, col_q2 = st.columns(2)
            with col_q1:
                st.caption("Break-even Units")
                be_f = st.number_input("Fixed Costs", min_value=0.0, value=1000.0, step=10.0, key="case_be_f")
                be_p = st.number_input("Price per Unit", min_value=0.0, value=20.0, step=1.0, key="case_be_p")
                be_v = st.number_input("Variable per Unit", min_value=0.0, value=12.0, step=1.0, key="case_be_v")
                be_units = (be_f / (be_p - be_v)) if (be_p - be_v) > 0 else None
                st.metric("Q_BE", f"{be_units:.1f}" if be_units else "N/A")
            with col_q2:
                st.caption("Simple DCF (Perpetual)")
                cf1 = st.number_input("FCF Year 1", min_value=0.0, value=100.0, step=5.0, key="case_dcf_cf1")
                g = st.number_input("Growth g (%)", min_value=0.0, max_value=10.0, value=2.0, step=0.5, key="case_dcf_g")
                k = st.number_input("Discount k (%)", min_value=1.0, max_value=20.0, value=8.0, step=0.5, key="case_dcf_k")
                pv = (cf1 * (1 + g/100)) / ((k/100) - (g/100)) if k > g else None
                st.metric("PV (Gordon)", f"{pv:.1f}" if pv else "N/A")
        with st.expander("Issue Tree Builder（MECE）", expanded=False):
            case_type = st.selectbox("Case Type", ["Profitability", "Market Entry", "Growth"], key="issue_type")
            seed = {
                "Profitability": ["Revenue", "Costs"],
                "Market Entry": ["Market", "Competition", "Capabilities", "Regulation"],
                "Growth": ["New Customers", "ARPU", "Retention", "Geographies", "Products"]
            }[case_type]
            st.write(", ".join(seed))
            note = st.text_area("Add branches (one per line)", value="")
            if st.button("Export Outline", key="issue_export"):
                txt = f"{case_type} Case\n" + "\n".join([f"- {x}" for x in seed]) + ("\n" + "\n".join([f"- {x}" for x in note.splitlines() if x.strip()]) if note else "")
                st.code(txt, language="markdown")
        with st.expander("Market Sizing Generator", expanded=False):
            if st.button("Generate Scenario", key="ms_gen"):
                import random
                pop = random.choice([50, 80, 100, 125])
                pen = random.choice([40, 60, 75, 80])
                freq = random.choice([1, 2, 4, 12])
                price = random.choice([1000, 2000, 5000])
                st.session_state['ms_scn'] = {"pop": pop, "pen": pen, "freq": freq, "price": price}
            scn = st.session_state.get('ms_scn')
            if scn:
                st.markdown(f"Population={scn['pop']}M, Penetration={scn['pen']}%, Frequency={scn['freq']}/yr, Price=¥{scn['price']}")
                ans_units = scn['pop']*1e6 * (scn['pen']/100) * scn['freq']
                ans_revenue = ans_units * scn['price']
                guess = st.number_input("Your revenue estimate (JPY)", min_value=0.0, value=0.0, step=1000.0)
                if st.button("Check", key="ms_check"):
                    tol = 0.1
                    low = ans_revenue*(1-tol)
                    high = ans_revenue*(1+tol)
                    correct = (guess >= low and guess <= high)
                    if correct:
                        st.success("Close enough. Good job.")
                    else:
                        st.error("Outside tolerance.")
                    st.caption(f"Answer≈ ¥{int(ans_revenue):,}")
        with st.expander("Math Speed Drills", expanded=False):
            if st.button("New Set", key="math_new"):
                import random
                qs = []
                for _ in range(5):
                    a = random.randint(50, 500)
                    b = random.randint(5, 50)
                    qs.append({"q": f"{a} × {b}", "a": a*b})
                st.session_state['math_set'] = qs
            ms = st.session_state.get('math_set', [])
            if ms:
                answers = []
                for i, item in enumerate(ms):
                    u = st.number_input(item["q"], min_value=0.0, step=1.0, key=f"math_{i}")
                    answers.append(u)
                if st.button("Grade", key="math_grade"):
                    correct = 0
                    for i, item in enumerate(ms):
                        if int(answers[i]) == item["a"]:
                            correct += 1
                    st.metric("Score", f"{correct}/5")
        with st.expander("Chart Reading Drill", expanded=False):
            import pandas as _pd
            import plotly.express as _px
            dfc = _pd.DataFrame({"Cat": ["A","B","C","D"], "Y1": [100, 140, 90, 110], "Y2": [120, 130, 150, 100]})
            figc = _px.bar(dfc, x="Cat", y=["Y1","Y2"], barmode="group", title="Category Values")
            st.plotly_chart(figc, use_container_width=True)
            st.caption("Q: Which category has the largest increase from Y1 to Y2?")
            inp = st.selectbox("Your answer", ["A","B","C","D"], key="chart_ans")
            inc = (dfc["Y2"]-dfc["Y1"]).tolist()
            idx = inc.index(max(inc))
            if st.button("Check", key="chart_check"):
                if inp == dfc.iloc[idx]["Cat"]:
                    st.success("Correct.")
                else:
                    st.error(f"Incorrect. Answer: {dfc.iloc[idx]['Cat']}")

        st.divider()

        # --- Detailed Guide ---
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🗣️ Core Competency Questions (STAR Method)")
            with st.expander("1. Self-Introduction & Why CPA?", expanded=True):
                st.markdown("""
                **The 'Engineer to Auditor' Narrative**:
                *   "I research **Defect Localization** in aerospace structures using **AI**. My job is to find 'hidden cracks' before they cause failure."
                *   "I realized **Audit** is the same concept but for **Business Structures**. I want to use my tech skills to find 'financial cracks' and ensure stability."
                *   **Why**: "Engineering is precise. Accounting is the language of business. I want to combine **Precision + Business Logic**."
                """)
            
            with st.expander("2. Handling Conflict / Teamwork"):
                st.markdown("""
                *   **Situation**: "In a joint research project with 3 others..."
                *   **Task**: "We disagreed on the simulation method (Speed vs Accuracy)."
                *   **Action**: "I didn't argue opinion. I proposed a **small-scale benchmark test** to compare data."
                *   **Result**: "Data showed my method was 2x faster with 99% accuracy. Team agreed based on evidence."
                *   **Key**: You are **Data-Driven** and **Collaborative**.
                """)

        with col2:
            st.markdown("### 🙋‍♂️ Reverse Questions (Gyakushitsumon)")
            st.info("Asking good questions is more important than giving good answers.")
            
            with st.expander("Level 1: The 'Safe' Questions"):
                st.markdown("""
                *   "What does a typical day look like for a first-year associate?"
                *   "How is the team structure for a typical audit engagement?"
                *   "What kind of training support is available for CPA exam (Jitsumu Hoshu)?"
                """)
                
            with st.expander("Level 2: The 'Interest' Questions"):
                st.markdown("""
                *   "I am interested in the Digital Audit sector. How early can I get involved in data analytics projects?"
                *   "What differentiates a 'High Performer' from an average one in your firm?"
                *   "Can you tell me about the most challenging project you've worked on recently?"
                """)
                
            with st.expander("Level 3: The 'Killer' Questions (Partner Level)"):
                st.markdown("""
                *   "With the rise of AI, how do you see the **business model of Audit** changing in 5 years? Will it shift from 'Time-Charge' to 'Value-Based'?"
                *   "How is the firm preparing for the auditing of **Non-Financial Information** (ESG/Sustainability)? I believe my engineering background could be useful there."
                *   "I want to be a bridge between the Tech team and the Audit team. Is there a career path for a 'Hybrid' professional?"
                """)
        st.divider()
        st.markdown("### 🧑‍💻 Programming Test")
        prob = st.selectbox("Select Problem", ["FizzBuzz", "Two Sum", "Valid Parentheses", "Fibonacci", "Anagram Grouping"], key="code_prob")
        starter = {
            "FizzBuzz": "def fizzbuzz(n):\n    res = []\n    for i in range(1, n+1):\n        out = ''\n        if i % 3 == 0:\n            out += 'Fizz'\n        if i % 5 == 0:\n            out += 'Buzz'\n        res.append(out or str(i))\n    return res\n",
            "Two Sum": "def two_sum(nums, target):\n    idx = {}\n    for i, x in enumerate(nums):\n        y = target - x\n        if y in idx:\n            return [idx[y], i]\n        idx[x] = i\n    return []\n",
            "Valid Parentheses": "def valid_parentheses(s):\n    stack = []\n    m = {')':'(', ']':'[', '}':'{'}\n    for ch in s:\n        if ch in '([{':\n            stack.append(ch)\n        elif ch in ')]}':\n            if not stack or stack[-1] != m[ch]:\n                return False\n            stack.pop()\n    return not stack\n",
            "Fibonacci": "def fib(n):\n    if n <= 1:\n        return n\n    a, b = 0, 1\n    for _ in range(n-1):\n        a, b = b, a+b\n    return b\n",
            "Anagram Grouping": "def group_anagrams(words):\n    buckets = {}\n    for w in words:\n        k = ''.join(sorted(w))\n        buckets.setdefault(k, []).append(w)\n    return list(buckets.values())\n"
        }[prob]
        code = st.text_area("Write your function", value=starter, height=260, key="code_area")
        if st.button("Run Tests", key="run_tests"):
            safe_builtins = {'range': range, 'len': len, 'abs': abs, 'min': min, 'max': max, 'sum': sum, 'sorted': sorted, 'enumerate': enumerate, 'zip': zip, 'map': map, 'filter': filter, 'all': all, 'any': any, 'list': list, 'dict': dict, 'set': set, 'tuple': tuple}
            g = {"__builtins__": safe_builtins}
            l = {}
            ok = False
            try:
                exec(code, g, l)
                ok = True
            except Exception as e:
                st.error(f"Compile error: {e}")
            if ok:
                res_lines = []
                def run_case(fn, args, exp):
                    try:
                        out = fn(*args)
                        return out == exp, out, exp
                    except Exception as err:
                        return False, str(err), exp
                tests = []
                if prob == "FizzBuzz":
                    tests = [([15], [str(i) if (i%3 and i%5) else ('Fizz'*(i%3==0)+'Buzz'*(i%5==0)) or str(i) for i in range(1,16)])]
                    fn = l.get("fizzbuzz")
                elif prob == "Two Sum":
                    tests = [([[2,7,11,15], 9], [0,1]), ([[3,2,4], 6], [1,2])]
                    fn = l.get("two_sum")
                elif prob == "Valid Parentheses":
                    tests = [(["()[]{}"], True), (["(]"], False), (["({[]})"], True)]
                    fn = l.get("valid_parentheses")
                elif prob == "Fibonacci":
                    tests = [([0],0),([1],1),([10],55)]
                    fn = l.get("fib")
                else:
                    tests = [([["eat","tea","tan","ate","nat","bat"]], [['eat','tea','ate'], ['tan','nat'], ['bat']])]
                    fn = l.get("group_anagrams")
                if not fn:
                    st.error("Function not found with required name.")
                else:
                    passed = 0
                    for args, exp in tests:
                        ok, out, ex = run_case(fn, args, exp)
                        if ok:
                            passed += 1
                        res_lines.append(f"Input={args} | Output={out} | Expected={ex} | {'OK' if ok else 'NG'}")
                    st.code("\n".join(res_lines), language="text")
                    st.metric("Passed", f"{passed}/{len(tests)}")
        with st.expander("Solution Outline (Steps)", expanded=False):
            if prob == "FizzBuzz":
                st.write("Loop 1..n; if %3 append 'Fizz'; if %5 append 'Buzz'; else str(i).")
            elif prob == "Two Sum":
                st.write("Use hashmap: store value→index; for x find target−x.")
            elif prob == "Valid Parentheses":
                st.write("Use stack; push opens; on close check top and pop; stack empty at end.")
            elif prob == "Fibonacci":
                st.write("Iterate a,b; next=b,a+b; repeat n−1 times.")
            else:
                st.write("Key = sorted letters of word; group by key.")

    # --- Buy-Side Path Tab ---
    tab_bs = st.tabs(["Buy-Side Path 💹"])[0]
    with tab_bs:
        st.subheader("💹 Buy-Side（AM / PE / VC）への道：CPA×Engineer")
        st.markdown("""
        **Roles**
        - AM（アセットマネジメント）: Equity/Fixed Income Analyst → PM  
        - PE: Deal Sourcing, DD（商流/財務/業界）, モデル（LBO）, バリューアップ  
        - VC: Sourcing, Tech DD, Term Sheet, ポートフォリオ支援
        
        **必須スキル**
        - Accounting/Valuation: 財務3表、DCF/Multiples、Quality of Earnings
        - Modeling: 3-statement, LBO, Sensitivity（Excel/Sheets; Python可）
        - Domain/Tech: 事業理解（製造/Tech）、データ処理（Python, SQL）
        - Edge（差別化）: CPAの会計品質×Engineerの技術理解/自動化
        
        **典型ルート**
        1) 監査（上場/製造/Tech）→ FAS（DD/Valuation）→ PE  
        2) 監査 → 事業会社（Corp Dev/IR/FP&A）→ PE/AM  
        3) Data/ML（Fin）→ Quant/AM  
        
        **実装アクション（ToDo）**
        - モデルポートフォリオ作成：3表・DCF・LBO（テンプレ整備）
        - 投資メモ（1-2ページ）: Thesis/Catalysts/Valuation/Risks（月1本）
        - 認定: CFA（推奨）＋CPA、Pythonプロジェクト（バックテスト/スクレイピング）
        - ネットワーキング: ミートアップ、OB訪問、LinkedIn最適化
        """)
        with st.expander("📎 ダウンロード（テンプレ）", expanded=False):
            st.markdown("- DCF テンプレ（準備中）\n- LBO テンプレ（準備中）\n- One-Pager 投資メモ（準備中）")

        st.markdown("### What is Buy-Side?")
        st.markdown("""
        - Investors that allocate capital to generate returns.  
        - 代表: アセットマネジメント（公募/機関）、プライベートエクイティ、ベンチャーキャピタル、ヘッジファンド。  
        - 主な成果物: 投資リターン、投資メモ、DDレポート、ポートフォリオ管理。
        """)
        st.markdown("### Buy-Side vs Sell-Side")
        st.markdown("""
        | 観点 | Buy-Side | Sell-Side |
        |---|---|---|
        | 顧客 | 自社/投資家 | 外部クライアント |
        | 成果 | リターン/損益 | フィー/アドバイス |
        | 仕事 | 投資選定/DD/運用 | リサーチ/仲介/アドバイス |
        | 時間軸 | 中長期（戦略/実行） | 短中期（案件/レポート） |
        """)

        if "buyside_plan" not in st.session_state:
            try:
                _data = load_data()
                st.session_state["buyside_plan"] = _data.get("buyside_plan", {})
            except Exception:
                st.session_state["buyside_plan"] = {}

        st.markdown("### Readiness Self-Assessment")
        c1, c2, c3 = st.columns(3)
        with c1:
            r_acc = st.slider("Accounting/Valuation", 0, 10, 6, key="ready_acc")
            r_mod = st.slider("Modeling (3表/DCF/LBO)", 0, 10, 5, key="ready_mod")
        with c2:
            r_dom = st.slider("Domain (製造/Tech理解)", 0, 10, 6, key="ready_dom")
            r_data = st.slider("Data (Python/SQL)", 0, 10, 6, key="ready_data")
        with c3:
            r_eng = st.slider("English/Global", 0, 10, 5, key="ready_eng")
            r_net = st.slider("Networking", 0, 10, 4, key="ready_net")
        score = int((r_acc*0.2 + r_mod*0.2 + r_dom*0.15 + r_data*0.15 + r_eng*0.15 + r_net*0.15) * 10)
        st.metric("Readiness Score", f"{score}/100")
        st.progress(score)
        if score < 60:
            st.info("Focus: Modeling と English を引き上げる。DCF/LBO と英語ピッチの反復。")
        elif score < 80:
            st.success("Good 基盤。案件型アウトプット（投資メモ/月）を習慣化。")
        else:
            st.success("Ready 水準。応募＋面接練習を本格化。")

        st.markdown("### 12-Week Plan")
        plan_items = [
            "Week1: 3表リンク再復習（運転資本/設備/税効果）",
            "Week2: DCF（WACC/Terminal）を自作テンプレで2社",
            "Week3: 上場製造業でQofE視点の調整を考える",
            "Week4: LBO簡易モデル（5年・簡易金利・Exit倍数）",
            "Week5: Stock Pitch #1（1-2ページ）",
            "Week6: セクター研究（自動車/サプライチェーン）",
            "Week7: DDフレーム（商流/財務/法務/オペレーション）",
            "Week8: Stock Pitch #2（異業種）",
            "Week9: Pythonでスクレイピング/財務データ取り込み",
            "Week10: バリュエーション比較（Multiples × DCF）",
            "Week11: 英語ピッチ練習（5分）を録音/改善",
            "Week12: 面接総仕上げ（Buy-Side想定質疑）"
        ]
        current_plan = st.session_state.get("buyside_plan", {})
        new_plan = {}
        for item in plan_items:
            checked = st.checkbox(item, value=bool(current_plan.get(item)), key=f"pl_{item}")
            new_plan[item] = checked
        csa1, csa2 = st.columns([1,1])
        with csa1:
            if st.button("Save Progress", key="save_buyside_plan"):
                st.session_state["buyside_plan"] = new_plan
                try:
                    blob = load_data()
                    blob["buyside_plan"] = new_plan
                    save_data(blob)
                    st.success("Saved progress.")
                except Exception as e:
                    st.error(f"Save failed: {e}")
        with csa2:
            if st.button("Reset Plan", key="reset_buyside_plan"):
                for item in plan_items:
                    st.session_state[f"pl_{item}"] = False
                st.session_state["buyside_plan"] = {}
                try:
                    blob = load_data()
                    blob["buyside_plan"] = {}
                    save_data(blob)
                except Exception:
                    pass
                st.info("Plan reset.")

        st.markdown("### Stock Pitch Builder")
        p1, p2 = st.columns([2,1])
        with p1:
            sp_name = st.text_input("Company", value="Example Corp")
            sp_thesis = st.text_area("Thesis (3 bullets, one per line)", value="1) Structural growth\n2) Operating leverage\n3) Cash returns policy")
            sp_catalysts = st.text_area("Catalysts", value="New product launch; Cost restructuring; Regulatory approval")
        with p2:
            sp_val = st.selectbox("Valuation Method", ["PE", "EV/EBITDA", "DCF"], index=1)
            sp_risks = st.text_area("Risks", value="FX; Raw materials; Execution")
        if st.button("Build One-Pager", key="build_pitch"):
            text = f"""Company: {sp_name}
Thesis:
{sp_thesis}
Valuation: {sp_val}
Catalysts: {sp_catalysts}
Risks: {sp_risks}
"""
            st.code(text, language="markdown")

        st.markdown("### Quick LBO Estimator")
        l1, l2, l3 = st.columns(3)
        with l1:
            ebitda = st.number_input("EBITDA (Year 1)", min_value=0.0, value=1000.0, step=50.0, key="lbo_ebitda")
            entry_mult = st.number_input("Entry EV/EBITDA", min_value=1.0, value=8.0, step=0.5, key="lbo_entry_mult")
        with l2:
            debt_mult = st.number_input("Debt / EBITDA", min_value=0.0, value=4.0, step=0.5, key="lbo_debt_mult")
            exit_mult = st.number_input("Exit EV/EBITDA", min_value=1.0, value=8.0, step=0.5, key="lbo_exit_mult")
        with l3:
            years = st.number_input("Hold Years", min_value=1, value=5, step=1, key="lbo_years")
            growth = st.number_input("EBITDA CAGR (%)", min_value=0.0, value=5.0, step=0.5, key="lbo_cagr")
        entry_ev = ebitda * entry_mult
        debt = ebitda * debt_mult
        equity = max(entry_ev - debt, 0.0)
        ebitda_exit = ebitda * ((1 + growth/100) ** years)
        exit_ev = ebitda_exit * exit_mult
        equity_exit = max(exit_ev - debt, 0.0)
        moic = (equity_exit / equity) if equity > 0 else None
        irr = ((moic ** (1/years)) - 1) * 100 if moic and moic > 0 else None
        st.metric("MOIC (approx)", f"{moic:.2f}x" if moic else "N/A")
        st.metric("IRR (approx)", f"{irr:.1f}%" if irr else "N/A")


elif page == "Company Directory 🏢":
    st.header("🏢 Company Directory for CPA Candidates")
    st.markdown("A curated list of potential employers in Japan for CPA holders, ranging from Audit to Tech.")

    st.subheader("Preferences")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        target_city = st.selectbox("Target City", ["Tokyo", "Osaka", "Nagoya", "Any"], index=0)
    with c2:
        w_cpa = st.slider("Weight: CPA Track", 0, 50, 20)
    with c3:
        w_ds = st.slider("Weight: Data Science/Tech", 0, 50, 15)
    with c4:
        w_global = st.slider("Weight: Global Brand", 0, 30, 5)
    min_score = st.slider("Show companies with score ≥", 0, 100, 0, 5)

    def _score_company(attrs, locs):
        score = 50
        try:
            if target_city != "Any":
                if isinstance(locs, list) and target_city in locs:
                    score += 30
                else:
                    score -= 10
            cpa_v = attrs.get("CPA", False)
            if isinstance(cpa_v, bool):
                score += w_cpa if cpa_v else 0
            elif isinstance(cpa_v, str):
                m = {"High": 1.0, "Medium": 0.6, "Low": 0.2}.get(cpa_v, 0.0)
                score += int(w_cpa * m)
            ds_v = attrs.get("DS", False)
            if isinstance(ds_v, bool):
                score += w_ds if ds_v else 0
            elif isinstance(ds_v, str):
                m = {"High": 1.0, "Medium": 0.6, "Low": 0.2}.get(ds_v, 0.0)
                score += int(w_ds * m)
            global_v = attrs.get("Global", False)
            if global_v:
                score += w_global
        except Exception:
            pass
        if score < 0:
            score = 0
        if score > 100:
            score = 100
        return int(score)

    tab1, tab2, tab3 = st.tabs(["Audit (Big 4 & Mid)", "Consulting & FAS", "Tech & Enterprise"])

    with tab1:
        st.subheader("Big 4 Audit Firms (The Standard Path)")
        big4 = [
            {"name": "Deloitte Touche Tohmatsu", "desc": "Largest scale, aggressive growth. Strong in IPO support.", "link": "https://www2.deloitte.com/jp/ja/pages/audit/topics/recruit-index.html", "locs": ["Tokyo", "Osaka", "Nagoya"], "attrs": {"CPA": True, "DS": True, "Global": True}},
            {"name": "KPMG AZSA", "desc": "Balanced portfolio, strong manufacturing clients. 'Gentleman' culture.", "link": "https://home.kpmg/jp/ja/home/careers.html", "locs": ["Tokyo", "Osaka", "Nagoya"], "attrs": {"CPA": True, "DS": True, "Global": True}},
            {"name": "EY ShinNihon", "desc": "Longest history, most listed clients. Strong Digital Audit focus.", "link": "https://www.ey.com/ja_jp/careers/audit", "locs": ["Tokyo", "Osaka", "Nagoya"], "attrs": {"CPA": True, "DS": True, "Global": True}},
            {"name": "PwC Aarata / Kyoto", "desc": "Global integration, innovative. PwC Kyoto is famous for high profitability.", "link": "https://www.pwc.com/jp/ja/careers/audit.html", "locs": ["Tokyo", "Osaka"], "attrs": {"CPA": True, "DS": True, "Global": True}}
        ]
        for c in big4:
            sc = _score_company(c.get("attrs", {}), c.get("locs", []))
            if sc < min_score:
                continue
            with st.expander(f"🦁 {c['name']}  |  Score: {sc}/100"):
                st.write(c['desc'])
                st.progress(sc)
                st.caption(f"Locations: {', '.join(c.get('locs', []))}")
                st.link_button("Recruit Page", c['link'])

        st.divider()
        st.subheader("Mid-Tier Audit Firms (准大手)")
        st.info("💡 **Why Mid-Tier?** Faster promotion, broader experience (you do everything), better work-life balance.")
        mid_tier = [
            {"name": "Grant Thornton Taiyo (太陽)", "desc": "Largest mid-tier. Very growing. Good alternative to Big 4.", "link": "https://www.grantthornton.jp/recruit/", "locs": ["Tokyo", "Osaka"], "attrs": {"CPA": True, "DS": "Medium", "Global": True}},
            {"name": "Crowe Toyo (東陽)", "desc": "Strong in domestic IPOs. Traditional but stable.", "link": "https://www.toyo-audit.or.jp/recruit/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Low", "Global": True}},
            {"name": "BDO Sanyu (三優)", "desc": "Friendly culture. Good international network via BDO.", "link": "https://www.bdo.or.jp/sanyu/recruit/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Low", "Global": True}},
            {"name": "RSM Seiwa (清和)", "desc": "Mid-sized, focus on healthcare and mid-cap clients.", "link": "https://www.seiwa-audit.or.jp/recruit/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Low", "Global": True}}
        ]
        for c in mid_tier:
            sc = _score_company(c.get("attrs", {}), c.get("locs", []))
            if sc < min_score:
                continue
            with st.expander(f"🐯 {c['name']}  |  Score: {sc}/100"):
                st.write(c['desc'])
                st.progress(sc)
                st.caption(f"Locations: {', '.join(c.get('locs', []))}")
                st.link_button("Recruit Page", c['link'])

    with tab2:
        st.subheader("FAS (Financial Advisory Services)")
        st.info("💡 **High Expertise**: M&A, Valuation, Forensics. Often requires CPA + English/Tech.")
        fas = [
            {"name": "Deloitte Tohmatsu Financial Advisory (DTFA)", "link": "https://www2.deloitte.com/jp/ja/pages/about-deloitte/articles/dtfa/dtfa-recruit.html", "locs": ["Tokyo", "Osaka"], "attrs": {"CPA": True, "DS": "Medium", "Global": True}},
            {"name": "KPMG FAS", "link": "https://home.kpmg/jp/ja/home/careers/fas.html", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Medium", "Global": True}},
            {"name": "PwC Advisory", "link": "https://www.pwc.com/jp/ja/careers/advisory.html", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Medium", "Global": True}},
            {"name": "EY Strategy and Transactions", "link": "https://www.ey.com/ja_jp/careers/strategy-and-transactions", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Medium", "Global": True}}
        ]
        for c in fas:
            sc = _score_company(c.get("attrs", {}), c.get("locs", []))
            if sc < min_score:
                continue
            with st.expander(f"💼 {c['name']}  |  Score: {sc}/100"):
                st.progress(sc)
                st.caption(f"Locations: {', '.join(c.get('locs', []))}")
                st.link_button("Recruit Page", c['link'])

        st.divider()
        st.subheader("Consulting Firms")
        st.markdown("Finance transformation, ERP implementation, Strategy.")
        consulting = [
            {"name": "Accenture (Strategy & Consulting)", "desc": "Top tier for DX/IT. High salary, hard work.", "link": "https://www.accenture.com/jp-ja/careers", "locs": ["Tokyo"], "attrs": {"CPA": False, "DS": True, "Global": True}},
            {"name": "BayCurrent Consulting", "desc": "Rapidly growing Japanese firm. High salary.", "link": "https://www.baycurrent.co.jp/recruit/", "locs": ["Tokyo"], "attrs": {"CPA": "Low", "DS": "Medium", "Global": False}},
            {"name": "Nomura Research Institute (NRI)", "desc": "Stable, high salary, strong domestic presence.", "link": "https://www.nri.com/jp/career", "locs": ["Tokyo"], "attrs": {"CPA": "Low", "DS": "Medium", "Global": True}},
            {"name": "ABeam Consulting", "desc": "Strong in SAP/ERP. Good for CPAs liking systems.", "link": "https://www.abeam.com/jp/ja/careers", "locs": ["Tokyo", "Osaka"], "attrs": {"CPA": "Low", "DS": "Medium", "Global": True}}
        ]
        for c in consulting:
            sc = _score_company(c.get("attrs", {}), c.get("locs", []))
            if sc < min_score:
                continue
            with st.expander(f"🧠 {c['name']}  |  Score: {sc}/100"):
                st.write(c['desc'])
                st.progress(sc)
                st.caption(f"Locations: {', '.join(c.get('locs', []))}")
                st.link_button("Recruit Page", c['link'])

    with tab3:
        st.subheader("Tech & Enterprise (CFO Track)")
        st.info("💡 **Business Side**: FP&A, Accounting Manager, IPO Prep.")
        fc1, fc2 = st.columns([1, 2])
        with fc1:
            te_firm_type = st.selectbox("Firm Type", ["All", "Foreign", "Japanese"], index=0, key="te_firm_type")
        with fc2:
            te_standards = st.multiselect("Accounting Standard Experience", ["IFRS", "US GAAP", "JGAAP"], default=[], key="te_standards")
        use_leftnav = st.checkbox("Left Navigation View (recommended)", value=True, key="te_leftnav")
        if use_leftnav:
            col_nav, col_view = st.columns([1, 3])
            with col_nav:
                subsec = st.radio(
                    "Section",
                    [
                        "Tech / Global",
                        "Holdings / Conglomerates",
                        "Securities",
                        "Makers",
                        "Utilities & Energy",
                        "Megabanks",
                        "Consulting (MBB)",
                        "Trading Companies",
                        "Buy-Side (AM / PE / VC)",
                        "User Catalog",
                        "Bulk Add"
                    ],
                    index=0,
                    key="te_nav"
                )
                cat_meta = {
                    "Tech / Global": {"salary": "6–12M JPY", "diff": "High"},
                    "Holdings / Conglomerates": {"salary": "7–12M JPY", "diff": "High"},
                    "Securities": {"salary": "6–12M JPY", "diff": "High"},
                    "Makers": {"salary": "5–9M JPY", "diff": "Medium"},
                    "Utilities & Energy": {"salary": "5–8M JPY", "diff": "Low–Medium"},
                    "Megabanks": {"salary": "6–10M JPY", "diff": "Medium"},
                    "Consulting (MBB)": {"salary": "8–14M JPY", "diff": "Ultra"},
                    "Trading Companies": {"salary": "8–14M JPY", "diff": "Ultra"},
                    "Buy-Side (AM / PE / VC)": {"salary": "8–20M JPY", "diff": "Ultra"},
                    "User Catalog": {"salary": "Varies", "diff": "Varies"},
                    "Bulk Add": {"salary": "", "diff": ""}
                }
                meta = cat_meta.get(subsec, {})
                if meta:
                    st.metric("Salary (cat)", meta.get("salary", "—"))
                    st.metric("Difficulty", meta.get("diff", "—"))
            with col_view:
                def _render_items(items, cat_name):
                    for c in items:
                        if te_firm_type != "All":
                            ctype = c.get("type")
                            if ctype and ctype != te_firm_type:
                                continue
                        if te_standards:
                            cstd = c.get("standards", [])
                            if cstd and not any(s in cstd for s in te_standards):
                                continue
                        sc = _score_company(c.get("attrs", {}), c.get("locs", []))
                        if sc < min_score:
                            continue
                        st.markdown(f"**{c['name']}** — Score: {sc}/100  \n{c.get('desc','')} [Link]({c.get('link','')})")
                        st.progress(sc)
                        st.caption(f"Locations: {', '.join(c.get('locs', []))}")
                        cm = cat_meta.get(cat_name, {})
                        sal = c.get("salary") or cm.get("salary", "—")
                        dif = c.get("difficulty") or cm.get("diff", "—")
                        st.caption(f"Salary: {sal} | Difficulty: {dif}")
                if subsec == "Tech / Global":
                    items = [
                        {"name": "Google / Amazon / MS (Japan)", "desc": "FP&A roles. Very high English requirement. Competitive.", "link": "https://careers.google.com/", "locs": ["Tokyo"], "attrs": {"CPA": False, "DS": True, "Global": True}, "type": "Foreign", "standards": ["US GAAP", "IFRS"], "salary": "10–14M+ JPY", "difficulty": "Ultra"},
                        {"name": "Rakuten Group", "desc": "English official language. Massive FinTech ecosystem.", "link": "https://corp.rakuten.co.jp/careers/", "locs": ["Tokyo"], "attrs": {"CPA": "Medium", "DS": True, "Global": True}, "type": "Japanese", "standards": ["IFRS"], "salary": "6–10M JPY"},
                        {"name": "Line Yahoo", "desc": "Major domestic tech player. Strong benefits.", "link": "https://www.lycorp.co.jp/ja/recruit/", "locs": ["Tokyo"], "attrs": {"CPA": "Medium", "DS": True, "Global": True}, "type": "Japanese", "standards": ["IFRS"]},
                        {"name": "Mercari", "desc": "Modern tech culture. Good for ambitious finance pros.", "link": "https://careers.mercari.com/", "locs": ["Tokyo"], "attrs": {"CPA": "Medium", "DS": True, "Global": True}, "type": "Japanese", "standards": ["IFRS"]}
                    ]
                    _render_items(items, "Tech / Global")
                elif subsec == "Holdings / Conglomerates":
                    items = [
                        {"name": "SoftBank Group", "desc": "Investment conglomerate. Complex consolidations and valuation analytics.", "link": "https://group.softbank/en/corp/recruit", "locs": ["Tokyo"], "attrs": {"CPA": "Medium", "DS": True, "Global": True}, "type": "Japanese", "standards": ["IFRS"]},
                        {"name": "Recruit Holdings", "desc": "HR Tech conglomerate. Data-driven culture; FP&A and IR strong.", "link": "https://recruit-holdings.com/careers/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": True, "Global": True}, "type": "Japanese", "standards": ["IFRS"]},
                        {"name": "Fast Retailing (UNIQLO)", "desc": "Globally integrated retail. Inventory/FX/IFRS exposure.", "link": "https://www.fastretailing.com/employment/ja/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Medium", "Global": True}, "type": "Japanese", "standards": ["IFRS"]},
                        {"name": "Takeda Pharmaceutical", "desc": "Global pharma. R&D capitalization, global IFRS, treasury.", "link": "https://www.takeda.com/jp/ja-us/careers/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Low", "Global": True}, "type": "Japanese", "standards": ["IFRS"]}
                    ]
                    _render_items(items, "Holdings / Conglomerates")
                elif subsec == "Securities":
                    items = [
                        {"name": "Nomura Securities (野村證券)", "desc": "Top-tier securities. IB, Markets, Corporate planning/Finance roles.", "link": "https://www.nomura.com/jpn/careers/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Medium", "Global": True}, "type": "Japanese", "standards": ["US GAAP", "IFRS"]},
                        {"name": "Daiwa Securities (大和証券)", "desc": "Major securities group. IB/markets, group finance & IR.", "link": "https://www.daiwa-grp.jp/recruit/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Low", "Global": True}, "type": "Japanese", "standards": ["IFRS"]}
                    ]
                    _render_items(items, "Securities")
                elif subsec == "Makers":
                    items = [
                        {"name": "Toyota", "desc": "Global auto leader. Robust finance org; strong FP&A/treasury.", "link": "https://global.toyota/en/company/", "locs": ["Tokyo", "Aichi"], "attrs": {"CPA": True, "DS": "Medium", "Global": True}, "type": "Japanese", "standards": ["IFRS"]},
                        {"name": "Keyence", "desc": "High-margin factory automation. Lean org, high productivity.", "link": "https://www.keyence.co.jp/jobs/", "locs": ["Tokyo", "Osaka"], "attrs": {"CPA": "Medium", "DS": "Medium", "Global": True}, "type": "Japanese", "standards": ["IFRS"]},
                        {"name": "Fujifilm", "desc": "Diversified: healthcare, imaging, materials. Global operations.", "link": "https://recruit.fujifilm.com/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Medium", "Global": True}, "type": "Japanese", "standards": ["IFRS"]},
                        {"name": "Sony", "desc": "Entertainment + Electronics. Complex consolidation; great for CPAs.", "link": "https://www.sony.com/en/SonyInfo/Careers/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": True, "Global": True}, "type": "Japanese", "standards": ["IFRS"]},
                        {"name": "Panasonic", "desc": "Devices to solutions. Large-scale finance transformation roles.", "link": "https://holdings.panasonic/jp/corporate/jobs/", "locs": ["Tokyo", "Osaka"], "attrs": {"CPA": True, "DS": "Medium", "Global": True}, "type": "Japanese", "standards": ["IFRS"]},
                        {"name": "Hitachi", "desc": "OT×IT leader. Project accounting, global IFRS exposure.", "link": "https://www.hitachi.co.jp/recruit/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": True, "Global": True}, "type": "Japanese", "standards": ["IFRS"]}
                    ]
                    _render_items(items, "Makers")
                elif subsec == "Utilities & Energy":
                    items = [
                        {"name": "Tokyo Gas", "desc": "Stable utility. Long-term planning, project finance, IFRS.", "link": "https://www.tokyo-gas-recruit.com/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Low", "Global": False}, "type": "Japanese", "standards": ["IFRS"]},
                        {"name": "TEPCO", "desc": "Large-scale regulated utility. Risk management heavy.", "link": "https://www.tepco.co.jp/recruit/index-j.html", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Low", "Global": False}, "type": "Japanese", "standards": ["IFRS"]}
                    ]
                    _render_items(items, "Utilities & Energy")
                elif subsec == "Megabanks":
                    items = [
                        {"name": "MUFG", "desc": "Japan’s largest financial group. Treasury, ALM, IFRS9/CECL skills.", "link": "https://www.mufg.jp/csr/recruit/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Medium", "Global": True}, "type": "Japanese", "standards": ["IFRS"]},
                        {"name": "SMBC", "desc": "Corporate banking powerhouse. Debt/FX exposure for CFO track.", "link": "https://www.smbc.co.jp/recruit/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Medium", "Global": True}, "type": "Japanese", "standards": ["IFRS"]},
                        {"name": "Mizuho", "desc": "Universal bank. Group finance/controls; transformation programs.", "link": "https://www.mizuho-fg.co.jp/recruit/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Medium", "Global": True}, "type": "Japanese", "standards": ["IFRS"]}
                    ]
                    _render_items(items, "Megabanks")
                elif subsec == "Consulting (MBB)":
                    items = [
                        {"name": "McKinsey & Company", "desc": "Top strategy firm. CFO transformation, value creation.", "link": "https://www.mckinsey.com/careers", "locs": ["Tokyo"], "attrs": {"CPA": "Low", "DS": "Medium", "Global": True}, "type": "Foreign"},
                        {"name": "Boston Consulting Group", "desc": "Deep corporate finance practice.", "link": "https://careers.bcg.com/", "locs": ["Tokyo"], "attrs": {"CPA": "Low", "DS": "Medium", "Global": True}, "type": "Foreign"},
                        {"name": "Bain & Company", "desc": "Private equity, performance improvement.", "link": "https://www.bain.com/careers/", "locs": ["Tokyo"], "attrs": {"CPA": "Low", "DS": "Medium", "Global": True}, "type": "Foreign"}
                    ]
                    _render_items(items, "Consulting (MBB)")
                elif subsec == "Trading Companies":
                    st.markdown("Mitsubishi Corp, Mitsui & Co, Itochu, Sumitomo Corp, Marubeni")
                    st.caption("Salary: 8–14M JPY | Difficulty: Ultra")
                    st.caption("Extremely competitive. High salary. Global rotations.")
                elif subsec == "Buy-Side (AM / PE / VC)":
                    items = [
                        {"name": "Nomura Asset Management", "desc": "Japan’s leading AM. Equity/Fixed Income/Quant.", "link": "https://www.nomura-am.co.jp/company/recruit/", "locs": ["Tokyo"], "attrs": {"CPA": "Medium", "DS": "Medium", "Global": True}, "type": "Japanese", "standards": ["IFRS"]},
                        {"name": "Daiwa Asset Management", "desc": "Major AM house. Public equities and funds.", "link": "https://www.daiwa-am.co.jp/company/recruit/", "locs": ["Tokyo"], "attrs": {"CPA": "Medium", "DS": "Low", "Global": True}, "type": "Japanese", "standards": ["IFRS"]},
                        {"name": "BlackRock Japan", "desc": "Global leader. iShares/Institutional mandates.", "link": "https://careers.blackrock.com/early-careers", "locs": ["Tokyo"], "attrs": {"CPA": "Low", "DS": True, "Global": True}, "type": "Foreign", "standards": ["US GAAP", "IFRS"]},
                        {"name": "Fidelity Investments Japan", "desc": "Active management, research focus.", "link": "https://www.fidelity.co.jp/corporate/recruit/", "locs": ["Tokyo"], "attrs": {"CPA": "Medium", "DS": "Low", "Global": True}, "type": "Foreign", "standards": ["US GAAP", "IFRS"]},
                        {"name": "Advantage Partners", "desc": "Japan’s top PE pioneer. Mid-market focus.", "link": "https://www.advantagepartners.com/jp/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Low", "Global": True}, "type": "Japanese"},
                        {"name": "Carlyle Japan", "desc": "Global PE. Large-cap to mid-cap.", "link": "https://www.carlyle.com/careers", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Low", "Global": True}, "type": "Foreign"},
                        {"name": "Bain Capital Japan", "desc": "Global PE. Strong operating improvement.", "link": "https://www.baincapital.com/careers", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Low", "Global": True}, "type": "Foreign"},
                        {"name": "Japan Industrial Partners (JIP)", "desc": "Carve-outs/turnarounds.", "link": "https://www.jipinc.com/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Low", "Global": False}, "type": "Japanese"},
                        {"name": "JAFCO", "desc": "Japan’s classic VC. Early to growth.", "link": "https://www.jafco.co.jp/english/recruit/", "locs": ["Tokyo"], "attrs": {"CPA": "Low", "DS": "Medium", "Global": True}, "type": "Japanese"},
                        {"name": "Globis Capital Partners", "desc": "Top-tier domestic VC. SaaS/tech focus.", "link": "https://www.globis-capital.co.jp/en/", "locs": ["Tokyo"], "attrs": {"CPA": "Low", "DS": "Medium", "Global": True}, "type": "Japanese"},
                        {"name": "Incubate Fund", "desc": "Early-stage specialist.", "link": "https://incubatefund.com/en/", "locs": ["Tokyo"], "attrs": {"CPA": "Low", "DS": "Medium", "Global": True}, "type": "Japanese"},
                        {"name": "DNX Ventures", "desc": "B2B tech-focused VC (JP/US).", "link": "https://www.dnx.vc/", "locs": ["Tokyo"], "attrs": {"CPA": "Low", "DS": True, "Global": True}, "type": "Foreign"}
                    ]
                    _render_items(items, "Buy-Side (AM / PE / VC)")
                elif subsec == "User Catalog":
                    catalog = st.session_state.get("company_catalog", [])
                    if catalog:
                        for c in catalog:
                            sc = _score_company(c.get("attrs", {}), c.get("locs", []))
                            if sc < min_score:
                                continue
                            st.markdown(f"**{c.get('name','')}** — Score: {sc}/100  \n{c.get('desc','')} [Link]({c.get('link','')})")
                            st.progress(sc)
                            st.caption(f"Locations: {', '.join(c.get('locs', []))}")
                            st.caption("Salary: Varies | Difficulty: Varies")
                    else:
                        st.info("No entries. Use 'Bulk Add' to import.")
                else:
                    st.markdown("#### Bulk Add Companies (CSV/JSON)")
                    with st.expander("Import / Manage", expanded=True):
                        st.caption("Schema: name, desc, link, locs(list or comma-separated), attrs.CPA(bool/str), attrs.DS(bool/str), attrs.Global(bool)")
                        uploaded = st.file_uploader("Upload CSV or JSON", type=["csv", "json"], accept_multiple_files=False, key="company_catalog_uploader_left")
                        if uploaded is not None:
                            try:
                                import json as _json
                                import pandas as _pd
                                if uploaded.name.lower().endswith(".json"):
                                    entries = _json.loads(uploaded.read().decode("utf-8"))
                                else:
                                    dfu = _pd.read_csv(uploaded)
                                    entries = dfu.to_dict(orient="records")
                                if not isinstance(entries, list):
                                    entries = [entries]
                                catalog = st.session_state.get("company_catalog", [])
                                for e in entries:
                                    name = e.get("name") or e.get("Name")
                                    if not name:
                                        continue
                                    desc = e.get("desc") or e.get("Desc") or ""
                                    link = e.get("link") or e.get("Link") or ""
                                    locs = e.get("locs") or e.get("Locs") or e.get("locations") or e.get("Locations") or []
                                    if isinstance(locs, str):
                                        locs = [s.strip() for s in locs.split(",") if s.strip()]
                                    attrs = e.get("attrs") or {}
                                    if not attrs:
                                        attrs = {
                                            "CPA": e.get("CPA") if e.get("CPA") is not None else False,
                                            "DS": e.get("DS") if e.get("DS") is not None else False,
                                            "Global": e.get("Global") if e.get("Global") is not None else False
                                        }
                                    item = {"name": name, "desc": desc, "link": link, "locs": locs, "attrs": attrs}
                                    exists = False
                                    for old in catalog:
                                        if old.get("name") == name:
                                            old.update(item)
                                            exists = True
                                            break
                                    if not exists:
                                        catalog.append(item)
                                st.session_state["company_catalog"] = catalog
                                try:
                                    data_blob = load_data()
                                    data_blob["company_catalog"] = catalog
                                    save_data(data_blob)
                                except Exception:
                                    pass
                                st.success(f"Imported {len(entries)} entries.")
                            except Exception as e:
                                st.error(f"Failed to import: {e}")
                        col_i1, col_i2 = st.columns([1,1])
                        with col_i1:
                            if st.button("Clear Catalog", key="clear_catalog_left"):
                                st.session_state["company_catalog"] = []
                                try:
                                    data_blob = load_data()
                                    data_blob["company_catalog"] = []
                                    save_data(data_blob)
                                except Exception:
                                    pass
                                st.info("Catalog cleared.")
                        with col_i2:
                            if st.button("Load Catalog from Storage", key="load_catalog_left"):
                                try:
                                    data_blob = load_data()
                                    st.session_state["company_catalog"] = data_blob.get("company_catalog", [])
                                    st.success("Loaded from storage.")
                                except Exception as e:
                                    st.error(f"Failed to load: {e}")
            st.stop()
        
        tech = [
            {"name": "Google / Amazon / MS (Japan)", "desc": "FP&A roles. Very high English requirement. Competitive.", "link": "https://careers.google.com/", "locs": ["Tokyo"], "attrs": {"CPA": False, "DS": True, "Global": True}},
            {"name": "Rakuten Group", "desc": "English official language. Massive FinTech ecosystem.", "link": "https://corp.rakuten.co.jp/careers/", "locs": ["Tokyo"], "attrs": {"CPA": "Medium", "DS": True, "Global": True}},
            {"name": "Line Yahoo", "desc": "Major domestic tech player. Strong benefits.", "link": "https://www.lycorp.co.jp/ja/recruit/", "locs": ["Tokyo"], "attrs": {"CPA": "Medium", "DS": True, "Global": True}},
            {"name": "Mercari", "desc": "Modern tech culture. Good for ambitious finance pros.", "link": "https://careers.mercari.com/", "locs": ["Tokyo"], "attrs": {"CPA": "Medium", "DS": True, "Global": True}}
        ]
        st.markdown("#### Tech / Global")
        for c in tech:
            sc = _score_company(c.get("attrs", {}), c.get("locs", []))
            if sc < min_score:
                continue
            st.markdown(f"**{c['name']}** — Score: {sc}/100  \n{c['desc']} [Link]({c['link']})")
            st.progress(sc)
            st.caption(f"Locations: {', '.join(c.get('locs', []))}")

        st.divider()
        st.markdown("#### Trading Companies (Sogo Shosha)")
        shosha = ["Mitsubishi Corp", "Mitsui & Co", "Itochu", "Sumitomo Corp", "Marubeni"]
        st.write(", ".join(shosha))
        st.caption("Extremely competitive. High salary. Global rotations.")

        st.divider()
        st.markdown("#### Top-Tier Holdings / Conglomerates")
        holdings = [
            {"name": "SoftBank Group", "desc": "Investment conglomerate. Complex consolidations and valuation analytics.", "link": "https://group.softbank/en/corp/recruit", "locs": ["Tokyo"], "attrs": {"CPA": "Medium", "DS": True, "Global": True}},
            {"name": "Recruit Holdings", "desc": "HR Tech conglomerate. Data-driven culture; FP&A and IR strong.", "link": "https://recruit-holdings.com/careers/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": True, "Global": True}},
            {"name": "Fast Retailing (UNIQLO)", "desc": "Globally integrated retail. Inventory/FX/IFRS exposure.", "link": "https://www.fastretailing.com/employment/ja/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Medium", "Global": True}},
            {"name": "Takeda Pharmaceutical", "desc": "Global pharma. R&D capitalization, global IFRS, treasury.", "link": "https://www.takeda.com/jp/ja-us/careers/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Low", "Global": True}}
        ]
        for c in holdings:
            sc = _score_company(c.get("attrs", {}), c.get("locs", []))
            if sc < min_score:
                continue
            st.markdown(f"**{c['name']}** — Score: {sc}/100  \n{c['desc']} [Link]({c['link']})")
            st.progress(sc)
            st.caption(f"Locations: {', '.join(c.get('locs', []))}")

        st.divider()
        st.markdown("#### Securities (証券)")
        securities = [
            {"name": "Nomura Securities (野村證券)", "desc": "Top-tier securities. IB, Markets, Corporate planning/Finance roles.", "link": "https://www.nomura.com/jpn/careers/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Medium", "Global": True}},
            {"name": "Daiwa Securities (大和証券)", "desc": "Major securities group. IB/markets, group finance & IR.", "link": "https://www.daiwa-grp.jp/recruit/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Low", "Global": True}}
        ]
        for c in securities:
            sc = _score_company(c.get("attrs", {}), c.get("locs", []))
            if sc < min_score:
                continue
            st.markdown(f"**{c['name']}** — Score: {sc}/100  \n{c['desc']} [Link]({c['link']})")
            st.progress(sc)
            st.caption(f"Locations: {', '.join(c.get('locs', []))}")

        st.divider()
        st.markdown("#### Bulk Add Companies (CSV/JSON)")
        with st.expander("Import / Manage", expanded=False):
            st.caption("Schema: name, desc, link, locs(list or comma-separated), attrs.CPA(bool/str), attrs.DS(bool/str), attrs.Global(bool)")
            uploaded = st.file_uploader("Upload CSV or JSON", type=["csv", "json"], accept_multiple_files=False, key="company_catalog_uploader")
            if uploaded is not None:
                try:
                    import json as _json
                    import pandas as _pd
                    if uploaded.name.lower().endswith(".json"):
                        entries = _json.loads(uploaded.read().decode("utf-8"))
                    else:
                        dfu = _pd.read_csv(uploaded)
                        entries = dfu.to_dict(orient="records")
                    if not isinstance(entries, list):
                        entries = [entries]
                    catalog = st.session_state.get("company_catalog", [])
                    for e in entries:
                        name = e.get("name") or e.get("Name")
                        if not name:
                            continue
                        desc = e.get("desc") or e.get("Desc") or ""
                        link = e.get("link") or e.get("Link") or ""
                        locs = e.get("locs") or e.get("Locs") or e.get("locations") or e.get("Locations") or []
                        if isinstance(locs, str):
                            locs = [s.strip() for s in locs.split(",") if s.strip()]
                        attrs = e.get("attrs") or {}
                        if not attrs:
                            attrs = {
                                "CPA": e.get("CPA") if e.get("CPA") is not None else False,
                                "DS": e.get("DS") if e.get("DS") is not None else False,
                                "Global": e.get("Global") if e.get("Global") is not None else False
                            }
                        item = {"name": name, "desc": desc, "link": link, "locs": locs, "attrs": attrs}
                        exists = False
                        for old in catalog:
                            if old.get("name") == name:
                                old.update(item)
                                exists = True
                                break
                        if not exists:
                            catalog.append(item)
                    st.session_state["company_catalog"] = catalog
                    try:
                        data_blob = load_data()
                        data_blob["company_catalog"] = catalog
                        save_data(data_blob)
                    except Exception:
                        pass
                    st.success(f"Imported {len(entries)} entries.")
                except Exception as e:
                    st.error(f"Failed to import: {e}")
            col_i1, col_i2 = st.columns([1,1])
            with col_i1:
                if st.button("Clear Catalog"):
                    st.session_state["company_catalog"] = []
                    try:
                        data_blob = load_data()
                        data_blob["company_catalog"] = []
                        save_data(data_blob)
                    except Exception:
                        pass
                    st.info("Catalog cleared.")
            with col_i2:
                if st.button("Load Catalog from Storage"):
                    try:
                        data_blob = load_data()
                        st.session_state["company_catalog"] = data_blob.get("company_catalog", [])
                        st.success("Loaded from storage.")
                    except Exception as e:
                        st.error(f"Failed to load: {e}")
        user_catalog = st.session_state.get("company_catalog", [])
        if user_catalog:
            st.markdown("#### User Catalog")
            for c in user_catalog:
                sc = _score_company(c.get("attrs", {}), c.get("locs", []))
                if sc < min_score:
                    continue
                st.markdown(f"**{c.get('name','')}** — Score: {sc}/100  \n{c.get('desc','')} [Link]({c.get('link','')})")
                st.progress(sc)
                st.caption(f"Locations: {', '.join(c.get('locs', []))}")

        st.divider()
        st.markdown("#### Makers (Tier 1)")
        makers = [
            {"name": "Toyota", "desc": "Global auto leader. Robust finance org; strong FP&A/treasury.", "link": "https://global.toyota/en/company/", "locs": ["Tokyo", "Aichi"], "attrs": {"CPA": True, "DS": "Medium", "Global": True}},
            {"name": "Keyence", "desc": "High-margin factory automation. Lean org, high productivity.", "link": "https://www.keyence.co.jp/jobs/", "locs": ["Tokyo", "Osaka"], "attrs": {"CPA": "Medium", "DS": "Medium", "Global": True}},
            {"name": "Fujifilm", "desc": "Diversified: healthcare, imaging, materials. Global operations.", "link": "https://recruit.fujifilm.com/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Medium", "Global": True}},
            {"name": "Sony", "desc": "Entertainment + Electronics. Complex consolidation; great for CPAs.", "link": "https://www.sony.com/en/SonyInfo/Careers/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": True, "Global": True}},
            {"name": "Panasonic", "desc": "Devices to solutions. Large-scale finance transformation roles.", "link": "https://holdings.panasonic/jp/corporate/jobs/", "locs": ["Tokyo", "Osaka"], "attrs": {"CPA": True, "DS": "Medium", "Global": True}},
            {"name": "Hitachi", "desc": "OT×IT leader. Project accounting, global IFRS exposure.", "link": "https://www.hitachi.co.jp/recruit/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": True, "Global": True}}
        ]
        for c in makers:
            sc = _score_company(c.get("attrs", {}), c.get("locs", []))
            if sc < min_score:
                continue
            st.markdown(f"**{c['name']}** — Score: {sc}/100  \n{c['desc']} [Link]({c['link']})")
            st.progress(sc)
            st.caption(f"Locations: {', '.join(c.get('locs', []))}")

        st.divider()
        st.markdown("#### Utilities & Energy")
        utilities = [
            {"name": "Tokyo Gas", "desc": "Stable utility. Long-term planning, project finance, IFRS.", "link": "https://www.tokyo-gas-recruit.com/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Low", "Global": False}},
            {"name": "TEPCO", "desc": "Large-scale regulated utility. Risk management heavy.", "link": "https://www.tepco.co.jp/recruit/index-j.html", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Low", "Global": False}}
        ]
        for c in utilities:
            sc = _score_company(c.get("attrs", {}), c.get("locs", []))
            if sc < min_score:
                continue
            st.markdown(f"**{c['name']}** — Score: {sc}/100  \n{c['desc']} [Link]({c['link']})")
            st.progress(sc)
            st.caption(f"Locations: {', '.join(c.get('locs', []))}")

        st.divider()
        st.markdown("#### Megabanks")
        megabanks = [
            {"name": "MUFG", "desc": "Japan’s largest financial group. Treasury, ALM, IFRS9/CECL skills.", "link": "https://www.mufg.jp/csr/recruit/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Medium", "Global": True}},
            {"name": "SMBC", "desc": "Corporate banking powerhouse. Debt/FX exposure for CFO track.", "link": "https://www.smbc.co.jp/recruit/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Medium", "Global": True}},
            {"name": "Mizuho", "desc": "Universal bank. Group finance/controls; transformation programs.", "link": "https://www.mizuho-fg.co.jp/recruit/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Medium", "Global": True}}
        ]
        for c in megabanks:
            sc = _score_company(c.get("attrs", {}), c.get("locs", []))
            if sc < min_score:
                continue
            st.markdown(f"**{c['name']}** — Score: {sc}/100  \n{c['desc']} [Link]({c['link']})")
            st.progress(sc)
            st.caption(f"Locations: {', '.join(c.get('locs', []))}")

        st.divider()
        st.markdown("#### Strategy Consulting (MBB)")
        mbb = [
            {"name": "McKinsey & Company", "desc": "Top strategy firm. CFO transformation, value creation.", "link": "https://www.mckinsey.com/careers", "locs": ["Tokyo"], "attrs": {"CPA": "Low", "DS": "Medium", "Global": True}},
            {"name": "Boston Consulting Group", "desc": "Deep corporate finance practice.", "link": "https://careers.bcg.com/", "locs": ["Tokyo"], "attrs": {"CPA": "Low", "DS": "Medium", "Global": True}},
            {"name": "Bain & Company", "desc": "Private equity, performance improvement.", "link": "https://www.bain.com/careers/", "locs": ["Tokyo"], "attrs": {"CPA": "Low", "DS": "Medium", "Global": True}}
        ]
        for c in mbb:
            sc = _score_company(c.get("attrs", {}), c.get("locs", []))
            if sc < min_score:
                continue
            st.markdown(f"**{c['name']}** — Score: {sc}/100  \n{c['desc']} [Link]({c['link']})")
            st.progress(sc)
            st.caption(f"Locations: {', '.join(c.get('locs', []))}")

        st.divider()
        st.markdown("#### Buy-Side (AM / PE / VC)")
        buyside = [
            # Asset Management
            {"name": "Nomura Asset Management", "desc": "Japan’s leading AM. Equity/Fixed Income/Quant.", "link": "https://www.nomura-am.co.jp/company/recruit/", "locs": ["Tokyo"], "attrs": {"CPA": "Medium", "DS": "Medium", "Global": True}},
            {"name": "Daiwa Asset Management", "desc": "Major AM house. Public equities and funds.", "link": "https://www.daiwa-am.co.jp/company/recruit/", "locs": ["Tokyo"], "attrs": {"CPA": "Medium", "DS": "Low", "Global": True}},
            {"name": "BlackRock Japan", "desc": "Global leader. iShares/Institutional mandates.", "link": "https://careers.blackrock.com/early-careers", "locs": ["Tokyo"], "attrs": {"CPA": "Low", "DS": True, "Global": True}},
            {"name": "Fidelity Investments Japan", "desc": "Active management, research focus.", "link": "https://www.fidelity.co.jp/corporate/recruit/", "locs": ["Tokyo"], "attrs": {"CPA": "Medium", "DS": "Low", "Global": True}},
            # Private Equity
            {"name": "Advantage Partners", "desc": "Japan’s top PE pioneer. Mid-market focus.", "link": "https://www.advantagepartners.com/jp/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Low", "Global": True}},
            {"name": "Carlyle Japan", "desc": "Global PE. Large-cap to mid-cap.", "link": "https://www.carlyle.com/careers", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Low", "Global": True}},
            {"name": "Bain Capital Japan", "desc": "Global PE. Strong operating improvement.", "link": "https://www.baincapital.com/careers", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Low", "Global": True}},
            {"name": "Japan Industrial Partners (JIP)", "desc": "Carve-outs/turnarounds.", "link": "https://www.jipinc.com/", "locs": ["Tokyo"], "attrs": {"CPA": True, "DS": "Low", "Global": False}},
            # Venture Capital
            {"name": "JAFCO", "desc": "Japan’s classic VC. Early to growth.", "link": "https://www.jafco.co.jp/english/recruit/", "locs": ["Tokyo"], "attrs": {"CPA": "Low", "DS": "Medium", "Global": True}},
            {"name": "Globis Capital Partners", "desc": "Top-tier domestic VC. SaaS/tech focus.", "link": "https://www.globis-capital.co.jp/en/", "locs": ["Tokyo"], "attrs": {"CPA": "Low", "DS": "Medium", "Global": True}},
            {"name": "Incubate Fund", "desc": "Early-stage specialist.", "link": "https://incubatefund.com/en/", "locs": ["Tokyo"], "attrs": {"CPA": "Low", "DS": "Medium", "Global": True}},
            {"name": "DNX Ventures", "desc": "B2B tech-focused VC (JP/US).", "link": "https://www.dnx.vc/", "locs": ["Tokyo"], "attrs": {"CPA": "Low", "DS": True, "Global": True}}
        ]
        for c in buyside:
            sc = _score_company(c.get("attrs", {}), c.get("locs", []))
            if sc < min_score:
                continue
            st.markdown(f"**{c['name']}** — Score: {sc}/100  \n{c['desc']} [Link]({c['link']})")
            st.progress(sc)
            st.caption(f"Locations: {', '.join(c.get('locs', []))}")


elif page == "Future 🚀":
    st.header("🚀 100-Year Life & Career Plan: The 'Founder' Trajectory")
    st.markdown("Your roadmap from **Master's Student** to **Tech CEO**. A comprehensive simulation of career, wealth, and life milestones.")

    # Top Status Board
    st.subheader("📍 Current Status")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current Age", "24", "Phase: Foundation")
    c2.metric("Next Big Milestone", "CPA Exam Pass", "2027 (Age 25)")
    c3.metric("Career Goal", "Audit Tech Founder", "Launch @ Age 35")
    c4.metric("Financial Freedom", "Target: Age 45", "Asset Goal: 500M JPY")
    
    st.divider()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["⏳ 100-Year Timeline", "🧠 Skill Evolution", "💰 Wealth (Monte Carlo)", "🦄 Entrepreneurship Blueprint", "💍 Life & Family"])

    with tab1:
        st.subheader("The Century Plan (Age 24 - 100)")
        
        timeline_events = [
            {"Age": 24, "Year": 2026, "Phase": "Foundation", "Event": "Master's (Germany/Japan) + CPA Study Start", "Status": "Current", "Importance": 3},
            {"Age": 25, "Year": 2027, "Phase": "Foundation", "Event": "Pass CPA Exam (May/Aug) 🏆", "Status": "Goal", "Importance": 5},
            {"Age": 26, "Year": 2028, "Phase": "Foundation", "Event": "Graduation & Join Big 4 (Digital Audit/FAS)", "Status": "Planned", "Importance": 4},
            {"Age": 29, "Year": 2031, "Phase": "Growth", "Event": "Promoted to Senior Associate. Lead ML Projects.", "Status": "Planned", "Importance": 3},
            {"Age": 30, "Year": 2032, "Phase": "Life", "Event": "Marriage 💍 (Target)", "Status": "Life", "Importance": 5},
            {"Age": 32, "Year": 2034, "Phase": "Growth", "Event": "Manager Promotion. Deep expertise in AI Governance.", "Status": "Planned", "Importance": 3},
            {"Age": 35, "Year": 2037, "Phase": "Launch", "Event": "🚀 FOUND YOUR COMPANY (AI Audit Firm). Disruption.", "Status": "Dream", "Importance": 5},
            {"Age": 40, "Year": 2042, "Phase": "Scale", "Event": "Global Expansion. AI-First Assurance.", "Status": "Dream", "Importance": 4},
            {"Age": 45, "Year": 2047, "Phase": "Exit", "Event": "IPO or Strategic Partnership. Financial Freedom.", "Status": "Dream", "Importance": 5},
            {"Age": 50, "Year": 2052, "Phase": "Invest", "Event": "Angel Investor for Deep Tech. University Lecturer.", "Status": "Vision", "Importance": 3},
            {"Age": 60, "Year": 2062, "Phase": "Legacy", "Event": "Establish Scholarship Foundation.", "Status": "Vision", "Importance": 3},
            {"Age": 80, "Year": 2082, "Phase": "Wisdom", "Event": "Write Memoirs. Mentor next gen.", "Status": "Vision", "Importance": 2},
            {"Age": 100, "Year": 2102, "Phase": "Complete", "Event": "Die Empty. No regrets.", "Status": "Final", "Importance": 5}
        ]
        
        df_timeline = pd.DataFrame(timeline_events)
        
        # Visual Timeline - Improved
        fig_timeline = px.scatter(
            df_timeline, 
            x="Year", 
            y="Age", 
            color="Phase", 
            size="Importance",
            hover_name="Event",
            text="Event", 
            title="Life Trajectory Map", 
            size_max=40,
            template="plotly_white"
        )
        fig_timeline.update_traces(textposition='top center', marker=dict(line=dict(width=2, color='DarkSlateGrey')))
        fig_timeline.update_layout(
            height=600,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, title="Age"),
            showlegend=True
        )
        # Add connecting line
        fig_timeline.add_trace(go.Scatter(
            x=df_timeline["Year"], 
            y=df_timeline["Age"], 
            mode='lines', 
            line=dict(color='lightgrey', width=1, dash='dot'),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        with st.expander("Show Data Table"):
            st.dataframe(df_timeline, use_container_width=True)

    with tab2:
        st.subheader("🧠 Skill Evolution: The 'T-Shaped' Professional")
        st.markdown("Visualizing your growth from a CPA specialist to a Tech CEO.")
        
        categories = ['Accounting/Audit', 'Coding/AI', 'English/Global', 'Leadership', 'Risk Taking']
        
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=[4, 2, 3, 2, 2],
            theta=categories,
            fill='toself',
            name='Current (Age 24)'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=[5, 4, 4, 4, 3],
            theta=categories,
            fill='toself',
            name='Manager (Age 32)'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=[5, 5, 5, 5, 5],
            theta=categories,
            fill='toself',
            name='Founder/CEO (Age 40)'
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                visible=True,
                range=[0, 5]
                )),
            showlegend=True,
            title="Skill Radar Chart"
        )
        
        col_r1, col_r2 = st.columns([2, 1])
        with col_r1:
            st.plotly_chart(fig_radar, use_container_width=True)
        with col_r2:
            st.info("💡 **Key Insight**")
            st.markdown("""
            *   **Accounting**: Must be perfect early on (CPA).
            *   **Coding/AI**: Your differentiator. Grow this during your Associate years.
            *   **Risk Taking**: The biggest shift required to become a Founder.
            """)

    with tab3:
        st.subheader("💰 Financial Simulation: Monte Carlo Analysis")
        st.markdown("A Quant-style simulation of your future wealth. **Life is probabilistic, not deterministic.**")
        
        # --- Interactive Sliders ---
        col_ctrl1, col_ctrl2 = st.columns(2)
        with col_ctrl1:
            st.markdown("**Income & Savings**")
            initial_salary = st.slider("Starting Salary (Million JPY)", 4.0, 10.0, 6.0, 0.5)
            savings_rate = st.slider("Savings Rate (%)", 10, 70, 30, 5) / 100.0
            investment_return_mean = st.slider("Expected Return (%)", 1.0, 15.0, 5.0, 0.5) / 100.0
            investment_volatility = st.slider("Volatility (Risk) (%)", 5.0, 30.0, 15.0, 1.0) / 100.0
            
        with col_ctrl2:
            st.markdown("**Startup Variables**")
            launch_age = st.slider("Launch Age", 28, 45, 35)
            exit_age = st.slider("Exit Age", launch_age + 3, 60, 45)
            exit_valuation = st.slider("Exit Valuation (Million JPY)", 100, 10000, 500, 100)
            exit_prob = st.slider("Exit Success Probability (%)", 10, 90, 30, 5) / 100.0
            
        st.divider()

        if st.button("Run Monte Carlo Simulation (100 Scenarios)"):
            with st.spinner("Running 100 simulations..."):
                # Simulation Data
                years = list(range(2026, 2060))
                ages = list(range(24, 58))
                n_sims = 100
                
                # Store all paths
                all_paths = []
                
                for i in range(n_sims):
                    path = []
                    current_asset = 1.0
                    
                    # Startup outcome for this simulation
                    is_successful_exit = np.random.random() < exit_prob
                    
                    for age in ages:
                        # Salary Logic
                        if age < launch_age:
                            # Corporate Phase
                            if age < 26: sal = 0
                            elif age < 30: sal = initial_salary
                            elif age < 35: sal = initial_salary * 1.5
                            elif age < 40: sal = initial_salary * 2.0
                            else: sal = initial_salary * 2.5
                            
                            current_asset += (sal * savings_rate)
                            
                        elif age == launch_age:
                            # Launch Cost
                            current_asset -= 5.0
                            if current_asset < 0: current_asset = 0
                            
                        elif age < exit_age:
                            # Founder Phase (Lean)
                            sal = 4.0
                            current_asset += (sal * 0.1)
                            
                        elif age == exit_age:
                            # Exit Event
                            if is_successful_exit:
                                current_asset += exit_valuation
                            else:
                                current_asset += 0 # Failed exit
                                
                        else:
                            # Post-Exit / Investor
                            pass

                        # Investment Return (Stochastic)
                        # Geometric Brownian Motion component: exp((mu - 0.5*sigma^2) + sigma*Z)
                        # Simplified: return ~ N(mean, vol)
                        r = np.random.normal(investment_return_mean, investment_volatility)
                        current_asset *= (1 + r)
                        
                        path.append(current_asset)
                    
                    all_paths.append(path)
                
                # Calculate Percentiles
                all_paths_np = np.array(all_paths) # shape (n_sims, n_years)
                p10 = np.percentile(all_paths_np, 10, axis=0)
                p50 = np.percentile(all_paths_np, 50, axis=0)
                p90 = np.percentile(all_paths_np, 90, axis=0)
                
                # Plot
                df_mc = pd.DataFrame({
                    "Age": ages,
                    "P10 (Pessimistic)": p10,
                    "P50 (Median)": p50,
                    "P90 (Optimistic)": p90
                })
                
                fig_mc = go.Figure()
                fig_mc.add_trace(go.Scatter(x=ages, y=p90, mode='lines', name='90th Percentile (Lucky)', line=dict(width=0), showlegend=False))
                fig_mc.add_trace(go.Scatter(x=ages, y=p10, mode='lines', name='10th Percentile (Unlucky)', line=dict(width=0), fill='tonexty', fillcolor='rgba(0,100,80,0.2)', showlegend=False))
                fig_mc.add_trace(go.Scatter(x=ages, y=p50, mode='lines', name='Median Outcome', line=dict(color='rgb(0,100,80)')))
                
                fig_mc.update_layout(title="Monte Carlo Wealth Projection (90% Confidence Interval)", yaxis_title="Net Assets (Million JPY)", hovermode="x")
                st.plotly_chart(fig_mc, use_container_width=True)
                
                st.success(f"Simulation Complete. Median Asset at Age {ages[-1]}: **{p50[-1]:.1f}M JPY**")
                if p90[-1] > 1000:
                    st.balloons()
        else:
            st.info("Click the button above to run the Monte Carlo simulation.")

    with tab4:
        st.subheader("🦄 Entrepreneurship Blueprint: 'Next-Gen AI Audit Firm'")
        
        # Business Stats
        m1, m2, m3 = st.columns(3)
        m1.metric("TAM (Total Addressable Market)", "¥500 Billion", "Audit Market in Japan")
        m2.metric("Target Market", "¥50 Billion", "Mid-Cap Listed Companies")
        m3.metric("Your Edge", "Tech + License", "Unbeatable Combo")
        
        st.markdown("---")
        
        st.info("💡 **Why AI Audit Firm > SaaS?**")
        st.markdown("""
        *   **SaaS Weakness**: High churn, low barrier to entry, "race to the bottom" pricing. Anyone can build a tool.
        *   **Audit Strength**: **Regulatory Moat**. Only licensed firms can sign off on financial statements. High switching costs.
        *   **The Opportunity**: Build a **Tech-Enabled Audit Firm** (Service + Tech) that operates at 10x efficiency of Big 4, undercutting their fees while maintaining higher margins.
        """)

        st.markdown("""
        **Vision**: Replace the "Army of Associates" with **Autonomous AI Agents**. Focus on high-level judgement and client relationships.
        
        **Phase 1: The "Insider" (Age 26-34)**
        *   **Goal**: Become a domain expert (CPA License is the Key). Understand *exactly* where the inefficiencies are in Big 4.
        *   **Action**: Lead "Digital Transformation" projects. Learn the *regulatory constraints* inside out.
        
        **Phase 2: The "Prototype" (Age 34-35)**
        *   **Goal**: Build the "AI Auditor" (Internal Tool).
        *   **Tech**: RAG (Retrieval Augmented Generation) for accounting standards, GNNs for transaction anomaly detection.
        *   **Team**: You (CTO/CEO) + Experienced Audit Partner (for credibility/signing).
        
        **Phase 3: The "Disruption" (Age 35+)**
        *   **Target**: Mid-cap public companies (tired of high Big 4 fees).
        *   **Product**: **"AI-First Statutory Audit"**. 
        *   **Value Prop**: "Faster audit, lower fees, deeper insights." Not just a software tool, but the *full service*.
        """)

    with tab5:
        st.subheader("💍 Life, Family & Happiness")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 👨‍👩‍👧 Family Goals")
            st.write("*   **Age 30**: Marriage (Partner who understands the startup grind).")
            st.write("*   **Age 32**: First Child.")
            st.write("*   **Age 35**: Second Child (Coincides with Startup Launch - Tough!).")
            st.write("*   **Policy**: Weekends are for family. No work on Sundays.")
            
        with col2:
            st.markdown("### ✈️ Experiences")
            st.write("*   **20s**: Backpacking Europe/Asia (Cheap travel).")
            st.write("*   **30s**: Family trips to Hawaii/Okinawa.")
            st.write("*   **40s**: World Cruise (Post-Exit).")
            st.write("*   **Hobbies**: Hiking, Coding, Wine Tasting.")

