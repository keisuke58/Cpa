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
    defaults = {"scores": [], "logs": [], "xp": 0, "level": 1, "badges": []}
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

# Vocabulary Data
vocab_data = {
    'Financial': [
        {'term': 'Going Concern', 'jp': '継続企業の前提', 'desc': '企業が将来にわたって事業を継続するという前提。'},
        {'term': 'Accrual Basis', 'jp': '発生主義', 'desc': '現金の収支にかかわらず、経済的事象の発生時点で収益・費用を認識する原則。'},
        {'term': 'Materiality', 'jp': '重要性', 'desc': '財務諸表利用者の意思決定に影響を与える情報の性質や金額の大きさ。'},
        {'term': 'Impairment', 'jp': '減損', 'desc': '資産の収益性が低下した結果、投資額の回収が見込めなくなった場合に帳簿価額を減額すること。'},
        {'term': 'Asset Retirement Obligation', 'jp': '資産除去債務', 'desc': '有形固定資産の取得や使用によって生じる、除去に関する将来の法的義務。'},
        {'term': 'Fair Value', 'jp': '公正価値', 'desc': '市場参加者間で秩序ある取引が行われた場合に成立する価格。'},
        {'term': 'Deferred Tax Asset', 'jp': '繰延税金資産', 'desc': '将来の税金を減らす効果がある一時差異。回収可能性の検討が必要。'},
        {'term': 'Equity Method', 'jp': '持分法', 'desc': '投資会社の持分に応じて、被投資会社の損益等を反映させる会計処理。関連会社等に適用。'},
        {'term': 'Goodwill', 'jp': 'のれん', 'desc': '企業買収等の際に支払った対価が、受け入れた純資産の時価を上回る超過収益力。'},
        {'term': 'Comprehensive Income', 'jp': '包括利益', 'desc': '純資産の変動額のうち、資本取引によらない部分。当期純利益＋その他の包括利益。'},
        {'term': 'Provision', 'jp': '引当金', 'desc': '将来の特定の費用や損失に備えて、当期の費用として計上される金額。'},
        {'term': 'Contingent Liability', 'jp': '偶発債務', 'desc': '将来の事象の発生・不発生によって債務が確定する潜在的な義務。'}
    ],
    'Management': [
        {'term': 'Opportunity Cost', 'jp': '機会原価', 'desc': 'ある代替案を選択したことによって犠牲となった（諦めた）最大の利益。'},
        {'term': 'Sunk Cost', 'jp': '埋没原価', 'desc': '過去の意思決定によって既に発生し、回収不能なコスト。意思決定では無視すべき。'},
        {'term': 'Break-even Point', 'jp': '損益分岐点', 'desc': '売上高と総費用が等しくなり、利益がゼロとなる点。'},
        {'term': 'Safety Margin', 'jp': '安全余裕率', 'desc': '現在の売上高が損益分岐点をどれだけ上回っているかを示す指標。高いほど安全。'},
        {'term': 'Cost Driver', 'jp': 'コスト・ドライバー', 'desc': '活動原価計算（ABC）において、コスト発生の原因となる活動量や要因。'},
        {'term': 'Standard Costing', 'jp': '標準原価計算', 'desc': '科学的・統計的調査に基づいて設定された目標原価を用いて行う原価計算。'},
        {'term': 'Variance Analysis', 'jp': '差異分析', 'desc': '標準原価と実際原価の差額（差異）を分析し、原因を特定して管理に役立てる手法。'},
        {'term': 'Direct Costing', 'jp': '直接原価計算', 'desc': '原価を変動費と固定費に分解し、変動費のみを製品原価とする計算手法（CVP分析に有用）。'},
        {'term': 'ROI (Return on Investment)', 'jp': '投下資本利益率', 'desc': '投資した資本に対してどれだけの利益を上げたかを示す収益性指標。'},
        {'term': 'Balanced Scorecard', 'jp': 'バランスト・スコアカード', 'desc': '財務、顧客、業務プロセス、学習と成長の4つの視点から業績を評価する手法。'},
        {'term': 'Just-In-Time (JIT)', 'jp': 'ジャスト・イン・タイム', 'desc': '必要なものを、必要な時に、必要な量だけ生産・供給する生産方式。'},
        {'term': 'Kaizen Costing', 'jp': '改善原価計算', 'desc': '製造段階において、継続的な改善活動を通じて原価低減を図る手法。'}
    ],
    'Audit': [
        {'term': 'Professional Skepticism', 'jp': '職業的懐疑心', 'desc': '常に疑念を持ち、監査証拠を批判的に評価する姿勢。'},
        {'term': 'Audit Risk', 'jp': '監査リスク', 'desc': '財務諸表に重要な虚偽表示があるにもかかわらず、監査人が不適切な意見を表明するリスク。'},
        {'term': 'Material Misstatement', 'jp': '重要な虚偽表示', 'desc': '財務諸表利用者の判断を誤らせる可能性のある誤りや不正。'},
        {'term': 'Internal Control', 'jp': '内部統制', 'desc': '業務の有効性・効率性、財務報告の信頼性などを確保するために組織内に構築されるプロセス。'},
        {'term': 'Substantive Procedures', 'jp': '実証手続', 'desc': '重要な虚偽表示を発見するために、取引や残高の詳細を直接検証する手続。'},
        {'term': 'Significant Deficiency', 'jp': '重要な不備', 'desc': '内部統制の不備のうち、財務諸表の信頼性に重要な影響を及ぼす可能性が高いもの。'},
        {'term': 'Key Audit Matters (KAM)', 'jp': '監査上の主要な検討事項', 'desc': '当年度の監査において、職業的専門家として特に重要であると判断した事項。'},
        {'term': 'Audit Evidence', 'jp': '監査証拠', 'desc': '監査意見の基礎となる結論を導くために監査人が入手した情報。'},
        {'term': 'Sampling Risk', 'jp': '試査リスク', 'desc': '監査人が母集団の一部（試査）に基づいて結論を出す際に、母集団全体を精査した場合と異なる結論になるリスク。'},
        {'term': 'Management Representation Letter', 'jp': '経営者確認書', 'desc': '経営者が監査人に対して、財務諸表作成責任の履行や情報の完全性などを文書で確認するもの。'},
        {'term': 'Subsequent Events', 'jp': '後発事象', 'desc': '決算日後に発生した事象で、次期以降の財政状態や経営成績に影響を及ぼすもの。'}
    ],
    'Company': [
        {'term': 'Fiduciary Duty', 'jp': '受託者責任', 'desc': '取締役などが会社や株主のために忠実に職務を遂行する義務（善管注意義務・忠実義務）。'},
        {'term': 'Shareholder Derivative Suit', 'jp': '株主代表訴訟', 'desc': '会社が取締役の責任を追及しない場合に、株主が会社に代わって提起する訴訟。'},
        {'term': 'Business Judgment Rule', 'jp': '経営判断の原則', 'desc': '取締役の経営判断が合理的で誠実に行われた場合、結果的に損害が生じても責任を問われない原則。'},
        {'term': 'Authorized Shares', 'jp': '発行可能株式総数', 'desc': '定款で定められた、会社が発行することができる株式の上限数。'},
        {'term': 'Treasury Stock', 'jp': '自己株式', 'desc': '会社が保有する自社の株式。議決権や配当請求権はない。'},
        {'term': 'Articles of Incorporation', 'jp': '定款', 'desc': '会社の目的、商号、本店所在地などの基本規則を定めた根本規則。'},
        {'term': 'Board of Directors', 'jp': '取締役会', 'desc': '業務執行の決定や取締役の職務執行の監督を行う機関。'},
        {'term': 'Statutory Auditor', 'jp': '監査役', 'desc': '取締役の職務執行や会計を監査する機関。'},
        {'term': 'General Meeting of Shareholders', 'jp': '株主総会', 'desc': '株式会社の最高意思決定機関。株主で構成される。'},
        {'term': 'Corporate Governance', 'jp': 'コーポレート・ガバナンス', 'desc': '企業経営を規律するための仕組み。企業統治。'},
        {'term': 'Stock Option', 'jp': 'ストック・オプション', 'desc': '自社株をあらかじめ決められた価格で購入できる権利。役員や従業員へのインセンティブ。'},
        {'term': 'Mergers and Acquisitions (M&A)', 'jp': 'M&A（合併・買収）', 'desc': '企業の合併や買収の総称。組織再編行為を含む。'}
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
    # Looking for 'studying' folder in parent of 'platform'
    # platform/app.py -> parent is CPA -> CPA/studying
    materials_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'studying')
    syllabus = {}
    
    if not os.path.exists(materials_dir):
        return {}
        
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
                
    return syllabus

study_materials = load_study_materials()

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
if st.sidebar.button("🔗 Studying.jp Login"):
    import webbrowser
    webbrowser.open_new_tab("https://member.studying.jp/top/")

st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation", ["Dashboard", "My Syllabus 📚", "Old Exams 📄", "Study Timer", "Mock Exams", "Scores", "Drills", "Survival Mode ⚡", "Roadmap", "Big 4 Job Hunting"])

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
    
    # Daily Tip
    st.subheader("💡 Daily CPA Tip")
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

elif page == "My Syllabus 📚":
    st.header("My Study Syllabus 📚")
    st.info("Based on your uploaded materials in 'studying' folder.")
    
    if not study_materials:
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
                            for _, row in group.iterrows():
                                title = row['title']
                                unique_key = f"{subject}|{title}"
                                is_done = unique_key in completed_items
                                
                                c_chk, c_txt, c_time = st.columns([0.5, 4, 1.5])
                                with c_chk:
                                    st.checkbox("", value=is_done, key=f"chk_{unique_key}", on_change=toggle_syllabus, kwargs={'key': unique_key})
                                
                                with c_txt:
                                    if is_done:
                                        st.markdown(f"~~{title}~~")
                                    else:
                                        st.markdown(f"**{title}**")
                                        if row['subcategory']:
                                            st.caption(f"└ {row['subcategory']}")
                                            
                                with c_time:
                                    st.caption(f"⏱️ {row['duration']}")

elif page == "Old Exams 📄":
    st.header("Old Exam Papers 📄")
    
    # Path to EXAM folder
    # platform/app.py -> CPA/platform -> CPA/EXAM
    exam_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'EXAM')
    
    if not os.path.exists(exam_dir):
        st.error(f"EXAM directory not found at: {exam_dir}")
    else:
        files = [f for f in os.listdir(exam_dir) if f.lower().endswith('.pdf')]
        
        if not files:
            st.warning("No PDF exam papers found.")
        else:
            st.write(f"Found {len(files)} exam papers.")
            
            for f in sorted(files):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"📄 **{f}**")
                with col2:
                    if st.button("Open", key=f"open_exam_{f}"):
                        try:
                            file_path = os.path.join(exam_dir, f)
                            os.startfile(file_path)
                            st.toast(f"Opening {f}...", icon="🚀")
                        except Exception as e:
                            st.error(f"Error opening file: {e}")
            
            st.markdown("---")
            st.info("💡 Tip: Use these papers to practice time management.")

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
        
        if selected_level == "vocab":
            st.info("💡 Hint: These are key English terms often found in global accounting standards (IFRS/US GAAP).")
    
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
                            'explanation': f"**{v['term']} ({v['jp']})**\n\n{v['desc']}",
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
                # Level 1 (Static questions)
                raw_questions = drill_questions.get(subject, [])
                # Filter for Level 1 or undefined (legacy)
                filtered_questions = [q for q in raw_questions if q.get('level', 1) == 1]
                
                if filtered_questions:
                    st.session_state.quiz_state['questions'] = filtered_questions
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
            'user_ans': None
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
        if st.button("🚀 Start Challenge", use_container_width=True):
            ss['active'] = True
            ss['lives'] = 3
            ss['streak'] = 0
            ss['score'] = 0
            ss['q'] = None
            ss['feedback'] = False
            st.rerun()
            
    else:
        # Metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Lives", "❤️" * ss['lives'])
        c2.metric("Streak", f"🔥 {ss['streak']}")
        c3.metric("Score", ss['score'])
        
        if ss['lives'] <= 0:
            st.error("💀 GAME OVER")
            st.markdown(f"### Final Score: {ss['score']}")
            
            # Save High Score
            if ss['score'] > 0:
                st.session_state.data["scores"].append({
                    'name': 'Survival Mode ⚡',
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
