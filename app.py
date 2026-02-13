import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date
import json
import os

# Set page config
st.set_page_config(page_title="CPA Perfect Platform 2027", layout="wide", page_icon="📚")

# Data Persistence
DATA_FILE = "cpa_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"scores": [], "logs": []}

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

# Vocabulary Data
vocab_data = {
    'Financial': [
        {'term': 'Going Concern', 'jp': '継続企業の前提', 'desc': '企業が将来にわたって事業を継続するという前提。'},
        {'term': 'Accrual Basis', 'jp': '発生主義', 'desc': '現金の収支にかかわらず、経済的事象の発生時点で収益・費用を認識する原則。'},
        {'term': 'Materiality', 'jp': '重要性', 'desc': '財務諸表利用者の意思決定に影響を与える情報の性質や金額の大きさ。'},
        {'term': 'Impairment', 'jp': '減損', 'desc': '資産の収益性が低下した結果、投資額の回収が見込めなくなった場合に帳簿価額を減額すること。'},
        {'term': 'Asset Retirement Obligation', 'jp': '資産除去債務', 'desc': '有形固定資産の取得や使用によって生じる、除去に関する将来の法的義務。'}
    ],
    'Management': [
        {'term': 'Opportunity Cost', 'jp': '機会原価', 'desc': 'ある代替案を選択したことによって犠牲となった（諦めた）最大の利益。'},
        {'term': 'Sunk Cost', 'jp': '埋没原価', 'desc': '過去の意思決定によって既に発生し、回収不能なコスト。意思決定では無視すべき。'},
        {'term': 'Break-even Point', 'jp': '損益分岐点', 'desc': '売上高と総費用が等しくなり、利益がゼロとなる点。'},
        {'term': 'Safety Margin', 'jp': '安全余裕率', 'desc': '現在の売上高が損益分岐点をどれだけ上回っているかを示す指標。高いほど安全。'},
        {'term': 'Cost Driver', 'jp': 'コスト・ドライバー', 'desc': '活動原価計算（ABC）において、コスト発生の原因となる活動量や要因。'}
    ],
    'Audit': [
        {'term': 'Professional Skepticism', 'jp': '職業的懐疑心', 'desc': '常に疑念を持ち、監査証拠を批判的に評価する姿勢。'},
        {'term': 'Audit Risk', 'jp': '監査リスク', 'desc': '財務諸表に重要な虚偽表示があるにもかかわらず、監査人が不適切な意見を表明するリスク。'},
        {'term': 'Material Misstatement', 'jp': '重要な虚偽表示', 'desc': '財務諸表利用者の判断を誤らせる可能性のある誤りや不正。'},
        {'term': 'Internal Control', 'jp': '内部統制', 'desc': '業務の有効性・効率性、財務報告の信頼性などを確保するために組織内に構築されるプロセス。'},
        {'term': 'Substantive Procedures', 'jp': '実証手続', 'desc': '重要な虚偽表示を発見するために、取引や残高の詳細を直接検証する手続。'}
    ],
    'Company': [
        {'term': 'Fiduciary Duty', 'jp': '受託者責任', 'desc': '取締役などが会社や株主のために忠実に職務を遂行する義務（善管注意義務・忠実義務）。'},
        {'term': 'Shareholder Derivative Suit', 'jp': '株主代表訴訟', 'desc': '会社が取締役の責任を追及しない場合に、株主が会社に代わって提起する訴訟。'},
        {'term': 'Business Judgment Rule', 'jp': '経営判断の原則', 'desc': '取締役の経営判断が合理的で誠実に行われた場合、結果的に損害が生じても責任を問われない原則。'},
        {'term': 'Authorized Shares', 'jp': '発行可能株式総数', 'desc': '定款で定められた、会社が発行することができる株式の上限数。'},
        {'term': 'Treasury Stock', 'jp': '自己株式', 'desc': '会社が保有する自社の株式。議決権や配当請求権はない。'}
    ]
}

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
page = st.sidebar.radio("Navigation", ["Dashboard", "Study Timer", "Mock Exams", "Scores", "Drills", "Roadmap", "Big 4 Job Hunting"])

if page == "Dashboard":
    st.header("Dashboard")
    st.subheader("Goal: 2027 May Short & Aug Essay")
    
    # Countdowns
    col1, col2, col3 = st.columns(3)
    today = date.today()
    
    with col1:
        target = date(2026, 12, 13)
        diff = (target - today).days
        st.markdown(f"""<div class="metric-card"><h4>Dec 2026 Short</h4><h1>{max(0, diff)} Days</h1></div>""", unsafe_allow_html=True)
        
    with col2:
        target = date(2027, 5, 23)
        diff = (target - today).days
        st.markdown(f"""<div class="metric-card"><h4>May 2027 Short</h4><h1>{max(0, diff)} Days</h1></div>""", unsafe_allow_html=True)
        
    with col3:
        target = date(2027, 8, 20)
        diff = (target - today).days
        st.markdown(f"""<div class="metric-card"><h4>Aug 2027 Essay</h4><h1>{max(0, diff)} Days</h1></div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Study Time & Radar Chart
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.subheader("Skill Balance")
        subjects = ['Financial', 'Management', 'Audit', 'Company', 'Tax', 'Elective']
        # Mock scores for radar chart if empty
        radar_scores = [60, 55, 40, 45, 30, 30]
        
        # Calculate from actual scores if available
        if st.session_state.data["scores"]:
            df_scores = pd.DataFrame(st.session_state.data["scores"])
            avg_scores = []
            for sub in subjects:
                sub_df = df_scores[df_scores['subject'] == sub]
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
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        st.subheader("Phase Progress: Foundation")
        st.progress(15)
        st.markdown("""
        * Focus: Financial & Management Accounting Calculation
        * Goal: Complete basic lectures by Aug 2026
        * Next Milestone: Dec 2026 Short Exam
        """)

elif page == "Study Timer":
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

elif page == "Mock Exams":
    st.header("Mock Exam Schedule")
    df_exams = pd.DataFrame(mock_exams)
    st.table(df_exams)

elif page == "Scores":
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

elif page == "Drills":
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
        
        if st.button("Start Quiz"):
            # Check for Vocabulary Mode
            if selected_level == "vocab":
                vocab_list = vocab_data.get(subject, [])
                if vocab_list:
                    # Transform vocab to question format
                    vocab_questions = []
                    for v in vocab_list:
                        vocab_questions.append({
                            'q': f"【重要語句】 「{v['term']}」 の意味として最も適切なものは？",
                            'options': [v['desc'], "（誤りの選択肢: 逆の意味）", "（誤りの選択肢: 無関係な定義）", "（誤りの選択肢: 類似用語の定義）"], # Simplified options for now
                            'correct': 0, # Always 0 for this simple implementation, ideally randomized
                            'explanation': f"**{v['term']} ({v['jp']})**\n\n{v['desc']}",
                            'type': 'vocab'
                        })
                    
                    # Better randomization for options would require more logic, 
                    # for now let's just use it as a flashcard style or simple drill
                    
                    st.session_state.quiz_state = {
                        'active': True,
                        'subject': subject,
                        'level': 'vocab',
                        'questions': vocab_questions,
                        'q_index': 0,
                        'score': 0,
                        'show_feedback': False,
                        'selected_option': None
                    }
                else:
                    st.warning(f"No vocabulary data for {subject}")
            else:
                # Filter questions
                questions = drill_questions.get(subject, [])
                filtered_q = [q for q in questions if q.get('level', 1) == selected_level]
                
                if not filtered_q:
                    # Fallback for legacy or empty
                    if selected_level == 1:
                        filtered_q = [q for q in questions if 'level' not in q or q['level'] == 1]
                
                if filtered_q:
                    st.session_state.quiz_state = {
                        'active': True,
                        'subject': subject,
                        'level': selected_level,
                        'questions': filtered_q,
                        'q_index': 0,
                        'score': 0,
                        'show_feedback': False,
                        'selected_option': None
                    }
                else:
                    st.warning(f"No questions found for {subject} - Level {selected_level}")
                
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
                
                if qs['q_index'] < total_q - 1:
                    if st.button("Next Question"):
                        qs['q_index'] += 1
                        qs['show_feedback'] = False
                        qs['selected_option'] = None
                        st.rerun()
                else:
                    st.success(f"Quiz Completed! Score: {qs['score']} / {total_q}")
                    if st.button("Finish"):
                        qs['active'] = False
                        st.rerun()
                        
            else:
                choice = st.radio("Choose Answer:", options, index=None, key=f"q_{qs['q_index']}")
                if st.button("Submit Answer"):
                    if choice:
                        selected_idx = options.index(choice)
                        qs['selected_option'] = selected_idx
                        qs['show_feedback'] = True
                        if selected_idx == current_q['correct']:
                            qs['score'] += 1
                        st.rerun()
                    else:
                        st.warning("Please select an option.")
        else:
            st.info("Select a subject and level from the sidebar to start.")

elif page == "Roadmap":
    st.header("Roadmap")
    st.markdown(roadmap_md)

elif page == "Big 4 Job Hunting":
    st.header("🏢 Big 4 CPA Job Hunting Strategy")
    st.markdown("Strategy guide and comparison for the major audit firms in Japan.")

    tab1, tab2 = st.tabs(["Strategy & Timeline", "Big 4 Comparison"])

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
        st.subheader("📊 Big 4 Audit Firms Comparison")
        
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
            }
        ]
        
        df_firms = pd.DataFrame(firms_data)
        
        # Display as a styled table or cards
        for firm in firms_data:
            with st.expander(f"{firm['Firm Name (JP)']} ({firm['Network']})", expanded=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**Strengths:** {firm['Key Strengths']}")
                    st.markdown(f"**Culture:** {firm['Culture']}")
                with col2:
                    st.link_button("Recruit Page", firm['Link'])
