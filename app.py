import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
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
page = st.sidebar.radio("Navigation", ["Dashboard 📊", "My Syllabus 📚", "Vocabulary 📖", "Formulas 📐", "Old Exams 📄", "Study Timer ⏱️", "Mock Exams 📝", "Scores 📈", "Drills 🔧", "Survival Mode ⚡", "Roadmap 🗺️", "Big 4 Job Hunting 💼", "Company Directory 🏢", "Future 🚀"])

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

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Study Time (Today)", f"{minutes_today} min", delta=f"{minutes_today/60:.1f} hrs")
    m2.metric("Quizzes Completed", f"{quizzes_today}", delta=f"Avg: {avg_score_today:.0f}%" if quizzes_today > 0 else None)
    m3.metric("Total XP", f"{total_xp}", delta="Level Up Soon?" if total_xp % 100 > 80 else None)
    
    # 4. Nearest Deadline
    target_short = date(2026, 12, 13)
    days_short = (target_short - today).days
    m4.metric("Next Exam (Dec Short)", f"{days_short} Days", delta="-1 Day", delta_color="inverse")
    
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
                if ftxt:
                    st.markdown(f"**Formula:** {ftxt}")
                vtxt = row.get("variables", "")
                if vtxt:
                    st.markdown(f"**Variables:** {vtxt}")
                etxt = row.get("explanation", "")
                if etxt:
                    st.markdown(etxt)
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

    with st.expander("📝 Exam Info（合格ボーダー R4〜R6）", expanded=True):
        st.markdown("""
        ### 短答式（相対評価）
        - 合格基準: 総点数の70％を基準として、審査会が相当と認めた得点比率
        - 足切り: 1科目でも満点の40％未満がある場合、不合格の可能性あり
        
        参考：近年のボーダー（予備校・メディア集計）
        
        | 実施年 | 第I回（12月） | 第II回（5月） | 備考 |
        |---|---:|---:|---|
        | 令和6年 (2024) | 68.0% | 78.0% | 易化で高水準 |
        | 令和5年 (2023) | 71.0% | 70.2% | 70%前後 |
        | 令和4年 (2022) | 68.0% | 73.0% | 変動大 |
        
        - 出典（参考値・解説記事）:
          - マイナビ会計士「第Ⅱ回短答式試験 結果速報」: https://cpa.mynavi.jp/column_mt/2024/06/967.html
          - 短答式の合格基準（公式）: https://www.fsa.go.jp/cpaaob/kouninkaikeishi-shiken/kijuntou/05.html
        
        ---
        ### 論文式（偏差値方式）
        - 合格基準: 総点数の60％を基準として、審査会が相当と認めた得点比率
        - 足切り: 1科目でも得点比率（偏差値）が40％未満のものがある場合は不合格
        - 得点比率（偏差値）の一般式: 50 + 10 × (個人の得点 − 平均点) / 標準偏差
        
        近年の合格点（公表資料/報道ベース）
        - 令和6年 (2024): 約52.0前後（毎年微調整）
        - 令和5年 (2023): 約51.8前後（微調整）
        - 令和4年 (2022): 約52.0前後（基準に近い）
        
        - 出典（公式）:
          - 合格基準について（短答式/論文式の公式基準）: https://www.fsa.go.jp/cpaaob/kouninkaikeishi-shiken/kijuntou/05.html
          - 令和7年 論文式 合格点の公表例（PDF、偏差値法の説明含む）: https://www.fsa.go.jp/cpaaob/kouninkaikeishi-shiken/r7shiken/ronbungoukaku_r07/02.pdf
        """)
        # R4-R6 short-answer border mini chart
        try:
            df_borders = pd.DataFrame([
                {"Year": "R4 (2022)", "Session": "I (Dec)", "Border": 68.0},
                {"Year": "R4 (2022)", "Session": "II (May)", "Border": 73.0},
                {"Year": "R5 (2023)", "Session": "I (Dec)", "Border": 71.0},
                {"Year": "R5 (2023)", "Session": "II (May)", "Border": 70.2},
                {"Year": "R6 (2024)", "Session": "I (Dec)", "Border": 68.0},
                {"Year": "R6 (2024)", "Session": "II (May)", "Border": 78.0},
            ])
            fig_border = px.bar(
                df_borders, x="Year", y="Border", color="Session", barmode="group",
                title="短答式 合格ボーダー（参考値）R4〜R6", range_y=[60, 80],
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_border.update_layout(legend_title_text="Session", yaxis_title="Border (%)")
            st.plotly_chart(fig_border, use_container_width=True)
            st.caption("注: 参考値（予備校・メディア集計ベース）。公式の相対基準はリンク参照。")
        except Exception:
            pass
    
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
    st.header("Mock Exam Schedule")
    df_exams = pd.DataFrame(mock_exams)
    st.table(df_exams)

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
        mock_mode = st.radio("Select Mode:", ["Behavioral (HR/Partner)", "Technical (Audit/Accounting)", "Case/Logic (Consulting)"], horizontal=True)
        
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
            else: # Case
                q_bank = [
                    {"q": "Estimate the number of smartphones sold in Japan annually.", "hint": "Pop (125M) x Penetration (80%) / Replacement Cycle (3 years)."},
                    {"q": "A client's profit is down 20%. How do you analyze it?", "hint": "Revenue vs Cost. Price x Vol. Fixed vs Variable. External vs Internal."},
                    {"q": "Should a Japanese auto-maker enter the EV market in India?", "hint": "Market Size, Competition, Regulation, Infrastructure, Capabilities."},
                    {"q": "How would you use AI to improve audit efficiency?", "hint": "Automated document review, Anomaly detection in journals, Chatbot for inquiries."}
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


elif page == "Company Directory 🏢":
    st.header("🏢 Company Directory for CPA Candidates")
    st.markdown("A curated list of potential employers in Japan for CPA holders, ranging from Audit to Tech.")

    tab1, tab2, tab3 = st.tabs(["Audit (Big 4 & Mid)", "Consulting & FAS", "Tech & Enterprise"])

    with tab1:
        st.subheader("Big 4 Audit Firms (The Standard Path)")
        big4 = [
            {"name": "Deloitte Touche Tohmatsu", "desc": "Largest scale, aggressive growth. Strong in IPO support.", "link": "https://www2.deloitte.com/jp/ja/pages/audit/topics/recruit-index.html"},
            {"name": "KPMG AZSA", "desc": "Balanced portfolio, strong manufacturing clients. 'Gentleman' culture.", "link": "https://home.kpmg/jp/ja/home/careers.html"},
            {"name": "EY ShinNihon", "desc": "Longest history, most listed clients. Strong Digital Audit focus.", "link": "https://www.ey.com/ja_jp/careers/audit"},
            {"name": "PwC Aarata / Kyoto", "desc": "Global integration, innovative. PwC Kyoto is famous for high profitability.", "link": "https://www.pwc.com/jp/ja/careers/audit.html"}
        ]
        for c in big4:
            with st.expander(f"🦁 {c['name']}"):
                st.write(c['desc'])
                st.link_button("Recruit Page", c['link'])

        st.divider()
        st.subheader("Mid-Tier Audit Firms (准大手)")
        st.info("💡 **Why Mid-Tier?** Faster promotion, broader experience (you do everything), better work-life balance.")
        mid_tier = [
            {"name": "Grant Thornton Taiyo (太陽)", "desc": "Largest mid-tier. Very growing. Good alternative to Big 4.", "link": "https://www.grantthornton.jp/recruit/"},
            {"name": "Crowe Toyo (東陽)", "desc": "Strong in domestic IPOs. Traditional but stable.", "link": "https://www.toyo-audit.or.jp/recruit/"},
            {"name": "BDO Sanyu (三優)", "desc": "Friendly culture. Good international network via BDO.", "link": "https://www.bdo.or.jp/sanyu/recruit/"},
            {"name": "RSM Seiwa (清和)", "desc": "Mid-sized, focus on healthcare and mid-cap clients.", "link": "https://www.seiwa-audit.or.jp/recruit/"}
        ]
        for c in mid_tier:
            with st.expander(f"🐯 {c['name']}"):
                st.write(c['desc'])
                st.link_button("Recruit Page", c['link'])

    with tab2:
        st.subheader("FAS (Financial Advisory Services)")
        st.info("💡 **High Expertise**: M&A, Valuation, Forensics. Often requires CPA + English/Tech.")
        fas = [
            {"name": "Deloitte Tohmatsu Financial Advisory (DTFA)", "link": "https://www2.deloitte.com/jp/ja/pages/about-deloitte/articles/dtfa/dtfa-recruit.html"},
            {"name": "KPMG FAS", "link": "https://home.kpmg/jp/ja/home/careers/fas.html"},
            {"name": "PwC Advisory", "link": "https://www.pwc.com/jp/ja/careers/advisory.html"},
            {"name": "EY Strategy and Transactions", "link": "https://www.ey.com/ja_jp/careers/strategy-and-transactions"}
        ]
        for c in fas:
            st.link_button(f"💼 {c['name']}", c['link'])

        st.divider()
        st.subheader("Consulting Firms")
        st.markdown("Finance transformation, ERP implementation, Strategy.")
        consulting = [
            {"name": "Accenture (Strategy & Consulting)", "desc": "Top tier for DX/IT. High salary, hard work.", "link": "https://www.accenture.com/jp-ja/careers"},
            {"name": "BayCurrent Consulting", "desc": "Rapidly growing Japanese firm. High salary.", "link": "https://www.baycurrent.co.jp/recruit/"},
            {"name": "Nomura Research Institute (NRI)", "desc": "Stable, high salary, strong domestic presence.", "link": "https://www.nri.com/jp/career"},
            {"name": "ABeam Consulting", "desc": "Strong in SAP/ERP. Good for CPAs liking systems.", "link": "https://www.abeam.com/jp/ja/careers"}
        ]
        for c in consulting:
            with st.expander(f"🧠 {c['name']}"):
                st.write(c['desc'])
                st.link_button("Recruit Page", c['link'])

    with tab3:
        st.subheader("Tech & Enterprise (CFO Track)")
        st.info("💡 **Business Side**: FP&A, Accounting Manager, IPO Prep.")
        
        tech = [
            {"name": "Google / Amazon / MS (Japan)", "desc": "FP&A roles. Very high English requirement. Competitive.", "link": "https://careers.google.com/"},
            {"name": "Rakuten Group", "desc": "English official language. Massive FinTech ecosystem.", "link": "https://corp.rakuten.co.jp/careers/"},
            {"name": "Line Yahoo", "desc": "Major domestic tech player. Strong benefits.", "link": "https://www.lycorp.co.jp/ja/recruit/"},
            {"name": "Mercari", "desc": "Modern tech culture. Good for ambitious finance pros.", "link": "https://careers.mercari.com/"}
        ]
        st.markdown("#### Tech / Global")
        for c in tech:
            st.markdown(f"**{c['name']}**: {c['desc']} [Link]({c['link']})")

        st.divider()
        st.markdown("#### Trading Companies (Sogo Shosha)")
        shosha = ["Mitsubishi Corp", "Mitsui & Co", "Itochu", "Sumitomo Corp", "Marubeni"]
        st.write(", ".join(shosha))
        st.caption("Extremely competitive. High salary. Global rotations.")


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

