import json
import random

def generate_financial_questions(count):
    questions = []
    for _ in range(count):
        # Type 1: Depreciation (Straight-line)
        cost = random.randint(100, 1000) * 1000
        years = random.choice([3, 4, 5, 8, 10])
        salvage_rate = random.choice([0, 0.1])
        salvage_value = int(cost * salvage_rate)
        depreciation = int((cost - salvage_value) / years)
        
        q1 = {
            "q": f"取得原価{cost:,}円、耐用年数{years}年、残存価額{salvage_value:,}円の固定資産について、定額法による1年間の減価償却費はいくらか？",
            "options": [
                f"{depreciation:,}円",
                f"{int(depreciation * 1.1):,}円",
                f"{int(depreciation * 0.9):,}円",
                f"{int(cost / years):,}円"
            ],
            "correct": 0,
            "explanation": f"定額法: (取得原価 - 残存価額) ÷ 耐用年数 = ({cost:,} - {salvage_value:,}) ÷ {years} = {depreciation:,}円",
            "level": 2
        }
        questions.append(q1)

        # Type 2: Cash Flow (Direct Method)
        sales = random.randint(500, 2000) * 1000
        ar_start = random.randint(50, 200) * 1000
        ar_end = ar_start + random.randint(-20, 50) * 1000
        cash_in = sales + ar_start - ar_end
        
        q2 = {
            "q": f"当期の売上高は{sales:,}円、期首売掛金は{ar_start:,}円、期末売掛金は{ar_end:,}円であった。直接法による営業キャッシュ・フロー（顧客からの収入）はいくらか？",
            "options": [
                f"{cash_in:,}円",
                f"{sales:,}円",
                f"{sales - ar_start + ar_end:,}円",
                f"{cash_in + 10000:,}円"
            ],
            "correct": 0,
            "explanation": f"顧客からの収入 = 売上高 + 期首売掛金 - 期末売掛金 = {sales:,} + {ar_start:,} - {ar_end:,} = {cash_in:,}円",
            "level": 3
        }
        questions.append(q2)
        
        # Type 3: Inventory Valuation (Moving Average)
        # Added new type for variety
        qty1 = random.randint(10, 50)
        price1 = random.randint(100, 200)
        qty2 = random.randint(10, 50)
        price2 = price1 + random.randint(10, 50)
        total_qty = qty1 + qty2
        avg_price = (qty1 * price1 + qty2 * price2) / total_qty
        avg_price_int = int(avg_price)
        
        q3 = {
            "q": f"期首在庫{qty1}個（単価{price1}円）、当期仕入{qty2}個（単価{price2}円）の場合、移動平均法による払出単価はいくらか？（円未満切り捨て）",
            "options": [
                f"{avg_price_int}円",
                f"{int((price1 + price2)/2)}円",
                f"{price2}円",
                f"{price1}円"
            ],
            "correct": 0,
            "explanation": f"移動平均単価 = (在庫金額合計) ÷ (在庫数量合計) = ({qty1*price1} + {qty2*price2}) ÷ {total_qty} = {avg_price:.2f} ≒ {avg_price_int}円",
            "level": 2
        }
        questions.append(q3)

    return questions

def generate_management_questions(count):
    questions = []
    for _ in range(count):
        # Type 1: CVP Analysis (Break-even Point)
        bep_units = random.randint(100, 1000)
        price = random.randint(10, 50) * 100
        variable_cost = int(price * random.uniform(0.4, 0.7))
        contribution_margin = price - variable_cost
        fixed_cost = bep_units * contribution_margin
        
        q1 = {
            "q": f"製品単価{price:,}円、単位当たり変動費{variable_cost:,}円、固定費{fixed_cost:,}円の場合、損益分岐点販売数量は何個か？",
            "options": [
                f"{bep_units:,}個",
                f"{bep_units + 50:,}個",
                f"{int(fixed_cost / price):,}個",
                f"{int(fixed_cost / variable_cost):,}個"
            ],
            "correct": 0,
            "explanation": f"損益分岐点販売数量 = 固定費 ÷ (単価 - 単位当たり変動費) = {fixed_cost:,} ÷ ({price:,} - {variable_cost:,}) = {bep_units:,}個",
            "level": 2
        }
        questions.append(q1)
        
        # Type 2: Variance Analysis (Direct Material)
        standard_price = random.randint(100, 500)
        standard_qty = random.randint(1000, 5000)
        actual_price = standard_price + random.randint(-20, 30)
        actual_qty = standard_qty + random.randint(-200, 300)
        
        price_variance = (actual_price - standard_price) * actual_qty
        qty_variance = (actual_qty - standard_qty) * standard_price
        
        # Question: Price Variance
        q2 = {
            "q": f"標準価格{standard_price:,}円、実際価格{actual_price:,}円、実際消費量{actual_qty:,}kgの場合、価格差異はいくらか？（プラスは不利、マイナスは有利とする）",
            "options": [
                f"{price_variance:,}円",
                f"{qty_variance:,}円",
                f"{price_variance * -1:,}円",
                f"0円"
            ],
            "correct": 0,
            "explanation": f"価格差異 = (実際価格 - 標準価格) × 実際消費量 = ({actual_price:,} - {standard_price:,}) × {actual_qty:,} = {price_variance:,}円",
            "level": 3
        }
        questions.append(q2)
        
        # Type 3: ROI Calculation
        invested_capital = random.randint(100, 500) * 1000000
        profit = int(invested_capital * random.uniform(0.05, 0.20))
        roi = (profit / invested_capital) * 100
        
        q3 = {
            "q": f"投資資本{invested_capital//10000}万円、事業利益{profit//10000}万円の場合、ROI（投下資本利益率）は何％か？",
            "options": [
                f"{roi:.1f}%",
                f"{roi*1.2:.1f}%",
                f"{roi*0.8:.1f}%",
                f"{(profit/invested_capital):.1f}%"
            ],
            "correct": 0,
            "explanation": f"ROI = 利益 ÷ 投資資本 × 100 = {profit} ÷ {invested_capital} × 100 = {roi:.1f}%",
            "level": 2
        }
        questions.append(q3)

    return questions

def generate_audit_questions(count):
    questions = []
    # Expanded templates for Audit Theory
    templates = [
        {
            "q": "監査リスク・モデルにおいて、監査リスク(AR)は、重大な虚偽表示リスク(RMM)と{item}の積として表される。",
            "options": ["発見リスク(DR)", "統制リスク(CR)", "固有リスク(IR)", "ビジネスリスク(BR)"],
            "correct": 0,
            "explanation": "監査リスク・モデル: AR = RMM × DR (発見リスク)。",
            "level": 1
        },
        {
            "q": "内部統制の不備が識別された場合、監査人が最初に行うべきことは何か？",
            "options": ["不備の深刻度の評価", "経営者への報告", "監査意見の変更", "監査計画の修正"],
            "correct": 0,
            "explanation": "不備を識別した場合、まずはその不備が重要な不備や重要な欠陥に該当するかどうか、深刻度を評価する必要がある。",
            "level": 2
        },
        {
            "q": "実証手続の実施時期について、期中実施が許容される条件として適切でないものはどれか？",
            "options": ["統制リスクが高いと評価されている場合", "統制環境が良好である場合", "残余期間の予測可能性が高い場合", "取引の性質が経常的である場合"],
            "correct": 0,
            "explanation": "統制リスクが高い（内部統制が信頼できない）場合、期中実施のリスクが高まるため、期末実施が原則となる。",
            "level": 3
        },
        {
            "q": "監査人の独立性において、「精神的独立性」と対になる概念は何か？",
            "options": ["外観的独立性", "経済的独立性", "組織的独立性", "法規的独立性"],
            "correct": 0,
            "explanation": "独立性は「精神的独立性（事実上の独立性）」と「外観的独立性（第三者から見て独立していると見えること）」の両方が必要である。",
            "level": 1
        },
        {
            "q": "財務諸表全体に重要な虚偽表示が存在し、その影響が広範である場合に表明される監査意見はどれか？",
            "options": ["不適正意見", "限定付適正意見", "無限定適正意見", "意見不表明"],
            "correct": 0,
            "explanation": "重要かつ広範(Pervasive)な虚偽表示がある場合は「不適正意見」となる。重要だが広範でない場合は「限定付適正意見」。",
            "level": 2
        },
        {
            "q": "監査証拠の十分かつ適切性において、「適切性」は何を意味するか？",
            "options": ["証拠の質（関連性と信頼性）", "証拠の量", "証拠の入手時期", "証拠の入手コスト"],
            "correct": 0,
            "explanation": "十分性は「量」、適切性は「質（関連性と信頼性）」を指す。",
            "level": 1
        },
        {
            "q": "不正のトライアングルを構成する3要素に含まれないものはどれか？",
            "options": ["監視", "動機・プレッシャー", "機会", "正当化"],
            "correct": 0,
            "explanation": "不正のトライアングルは「動機・プレッシャー」「機会」「正当化」の3要素である。「監視」はこれらを抑制する要因。",
            "level": 2
        },
        {
            "q": "継続企業の前提（ゴーイング・コンサーン）に重要な疑義があり、財務諸表に適切な注記が行われている場合の監査意見は？",
            "options": ["無限定適正意見＋追記情報", "限定付適正意見", "不適正意見", "意見不表明"],
            "correct": 0,
            "explanation": "GC注記が適切に行われていれば、財務諸表自体は適正であるため「無限定適正意見」となり、「継続企業の前提に関する重要な不確実性」として追記情報で記載する。",
            "level": 3
        },
        {
            "q": "監査上の主要な検討事項（KAM）は、誰とのコミュニケーションから選定されるか？",
            "options": ["監査役等", "経営者", "株主", "従業員"],
            "correct": 0,
            "explanation": "KAMは、監査役等とコミュニケーションを行った事項の中から、職業的専門家として特に重要と判断した事項を選定する。",
            "level": 2
        },
        {
            "q": "棚卸立会は、主にどのアサーション（経営者の主張）を検証するための手続か？",
            "options": ["実在性", "網羅性", "評価の妥当性", "権利と義務"],
            "correct": 0,
            "explanation": "棚卸立会は、現物がそこに存在することを確認するため、主に「実在性」を検証する。",
            "level": 2
        }
    ]
    
    for _ in range(count):
        base = random.choice(templates)
        q = base.copy()
        q['options'] = base['options'].copy()
        correct_option = q['options'][q['correct']]
        random.shuffle(q['options'])
        q['correct'] = q['options'].index(correct_option)
        questions.append(q)
        
    return questions

def generate_company_law_questions(count):
    questions = []
    # Expanded templates for Company Law
    templates = [
        {
            "q": "株式会社の設立に際して、発起人が割り当てを受ける設立時発行株式の総数は、発行可能株式総数の{item}を下回ってはならない。",
            "options": ["制限はない", "4分の1", "2分の1", "3分の1"],
            "correct": 0,
            "explanation": "公開会社でない場合や設立時は、発行可能株式総数の引受割合に法定の制限はない（公開会社の定款変更時とは異なる）。",
            "level": 2
        },
        {
            "q": "取締役会設置会社において、取締役の任期は原則として選任後{item}年以内に終了する事業年度のうち最終のものに関する定時株主総会の終結の時までである。",
            "options": ["2", "1", "4", "10"],
            "correct": 0,
            "explanation": "会社法332条1項。原則は2年。定款や株主総会決議で短縮可能。非公開会社は10年まで伸長可能。",
            "level": 1
        },
        {
            "q": "公開会社における取締役会の決議要件として、原則的なものはどれか？",
            "options": ["議決権を行使できる取締役の過半数が出席し、その過半数", "取締役の過半数が出席し、その3分の2以上", "取締役全員の同意", "出席取締役の3分の2以上"],
            "correct": 0,
            "explanation": "取締役会の決議は、議決権を行使することができる取締役の過半数（定款でこれを上回る割合を定めることができる）が出席し、その過半数（定款でこれを上回る割合を定めることができる）をもって行う。",
            "level": 2
        },
        {
            "q": "株主総会の普通決議の定足数は、原則として議決権を行使することができる株主の議決権の{item}を有する株主の出席が必要である。",
            "options": ["過半数", "3分の1以上", "3分の2以上", "4分の1以上"],
            "correct": 0,
            "explanation": "普通決議の定足数は原則として過半数であるが、定款で排除・軽減が可能（取締役選任などを除く）。",
            "level": 2
        },
        {
            "q": "監査役会設置会社において、監査役は最低何人必要か？",
            "options": ["3人", "1人", "2人", "4人"],
            "correct": 0,
            "explanation": "監査役会設置会社では、監査役は3人以上で、かつ、その半数以上は社外監査役でなければならない。",
            "level": 1
        },
        {
            "q": "剰余金の配当において、配当財産が金銭以外の財産である場合（現物配当）、原則としてどの機関の決議が必要か？",
            "options": ["株主総会の特別決議", "株主総会の普通決議", "取締役会決議", "株主全員の同意"],
            "correct": 0,
            "explanation": "金銭以外の財産を配当する場合、株主の不平等を招く恐れがあるため、原則として株主総会の特別決議が必要となる。",
            "level": 3
        },
        {
            "q": "株式会社が自己株式を取得できる場合として、誤っているものはどれか？",
            "options": ["取締役会の決定のみでいつでも自由に取得できる", "株主総会決議に基づいて株主との合意により取得する場合", "合併等の組織再編により取得する場合", "単元未満株主の買取請求に応じる場合"],
            "correct": 0,
            "explanation": "自己株式の取得は財源規制等があるため、取締役会の決定のみで自由に取得できるわけではない（市場取引等の特定ケースを除く原則論）。",
            "level": 2
        },
        {
            "q": "指名委員会等設置会社において、設置が義務付けられていない委員会はどれか？",
            "options": ["コンプライアンス委員会", "指名委員会", "監査委員会", "報酬委員会"],
            "correct": 0,
            "explanation": "指名委員会等設置会社には、指名委員会、監査委員会、報酬委員会の3つの委員会を置くことが義務付けられている。",
            "level": 1
        },
        {
            "q": "株主代表訴訟を提起するために、原則として必要な株式保有期間は？（公開会社の場合）",
            "options": ["6ヶ月", "3ヶ月", "1年", "保有期間の要件はない"],
            "correct": 0,
            "explanation": "公開会社では、6ヶ月（定款で短縮可）前から引き続き株式を保有している株主が代表訴訟を提起できる。",
            "level": 3
        },
        {
            "q": "吸収合併において、反対株主が会社に対して公正な価格での株式買取を請求できる権利を何というか？",
            "options": ["株式買取請求権", "新株予約権", "株式引受権", "配当請求権"],
            "correct": 0,
            "explanation": "組織再編に反対する株主を保護するため、株式買取請求権が認められている。",
            "level": 1
        }
    ]
    
    for _ in range(count):
        base = random.choice(templates)
        q = base.copy()
        q['options'] = base['options'].copy()
        correct_option = q['options'][q['correct']]
        random.shuffle(q['options'])
        q['correct'] = q['options'].index(correct_option)
        questions.append(q)
    return questions

import os

def main():
    # Generate ~2000 questions total
    # Financial: 3 types * 200 = 600
    # Management: 3 types * 200 = 600
    # Audit: 10 templates * 40 = 400
    # Company: 10 templates * 40 = 400
    
    financial = generate_financial_questions(600)
    management = generate_management_questions(600)
    audit = generate_audit_questions(400)
    company = generate_company_law_questions(400)
    
    all_data = {
        "Financial": financial,
        "Management": management,
        "Audit": audit,
        "Company": company
    }
    
    # Determine output directory (same as script directory)
    output_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Save as JSON for Python
    json_path = os.path.join(output_dir, "questions.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
        
    # Save as JS for HTML
    js_path = os.path.join(output_dir, "questions.js")
    js_content = f"const generatedQuestions = {json.dumps(all_data, ensure_ascii=False, indent=2)};"
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js_content)
    
    print(f"Generated {len(financial)} Financial, {len(management)} Management, {len(audit)} Audit, {len(company)} Company questions.")
    print(f"Saved to {output_dir}")

if __name__ == "__main__":
    main()
