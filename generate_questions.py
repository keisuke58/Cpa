import json
import random
import hashlib
import os

def _sig(q):
    return hashlib.md5((q.get('q','') + '|' + '|'.join(q.get('options', [])) + '|' + str(q.get('correct'))).encode('utf-8')).hexdigest()

def _tag_for_text(txt, default_tag):
    if "監査リスク" in txt:
        return ["監査リスク"]
    if "内部統制" in txt:
        return ["内部統制"]
    if "KAM" in txt or "主要な検討事項" in txt:
        return ["KAM"]
    if "継続企業" in txt or "ゴーイング" in txt:
        return ["GC"]
    if "棚卸" in txt:
        return ["棚卸"]
    if "取締役" in txt:
        return ["取締役"]
    if "株主総会" in txt:
        return ["株主総会"]
    if "合併" in txt or "株式交換" in txt:
        return ["組織再編"]
    return [default_tag]

def generate_intro_questions(count_per_subject=50):
    """
    Generates Level 0 (Intro/Basic) questions that serve as a bridge to Old Exams.
    Simple definitions, basic formulas, and key concepts.
    """
    data = {
        "Financial": [],
        "Management": [],
        "Audit": [],
        "Company": []
    }

    # --- Financial Accounting Basics ---
    for _ in range(count_per_subject):
        q_type = random.choice(["equation", "elements", "pl_items"])
        q = {}
        if q_type == "equation":
            q = {
                "q": "貸借対照表等式: 資産(Assets) = 負債(Liabilities) + 【 A 】",
                "options": ["純資産(Equity)", "収益(Revenue)", "費用(Expense)", "利益(Profit)"],
                "correct": 0,
                "explanation": "貸借対照表等式は、資産 = 負債 + 純資産 です。",
                "level": 0
            }
        elif q_type == "elements":
            item = random.choice([
                ("売掛金", "資産"), ("買掛金", "負債"), ("資本金", "純資産"), 
                ("売上高", "収益"), ("給料手当", "費用"), ("貸倒引当金", "資産のマイナス")
            ])
            opts = ["資産", "負債", "純資産", "収益", "費用"]
            if item[1] == "資産のマイナス": opts.append("資産のマイナス")
            options = [item[1]] + [o for o in opts if o != item[1]][:3]
            
            q = {
                "q": f"勘定科目「{item[0]}」の区分として正しいものはどれか？",
                "options": options,
                "correct": 0,
                "explanation": f"「{item[0]}」は{item[1]}に分類されます。",
                "level": 0
            }
        elif q_type == "pl_items":
            q = {
                "q": "損益計算書において、売上高から売上原価を差し引いた利益は何か？",
                "options": ["売上総利益", "営業利益", "経常利益", "税引前当期純利益"],
                "correct": 0,
                "explanation": "売上高 - 売上原価 = 売上総利益 (Gross Profit) です。",
                "level": 0
            }
        
        # Shuffle
        if "options" in q:
            correct_opt = q['options'][q['correct']]
            random.shuffle(q['options'])
            q['correct'] = q['options'].index(correct_opt)
        data["Financial"].append(q)

    # --- Management Accounting Basics ---
    for _ in range(count_per_subject):
        q_type = random.choice(["cost_behavior", "cvp_basic"])
        q = {}
        if q_type == "cost_behavior":
            item = random.choice([
                ("工場の家賃", "固定費"), ("材料費", "変動費"), ("社長の給料", "固定費"), ("外注加工費", "変動費")
            ])
            opts = ["固定費", "変動費", "準変動費", "機会原価"]
            options = [item[1]] + [o for o in opts if o != item[1]][:3]
            
            q = {
                "q": f"操業度（生産量）の増減に関わらず発生額が一定である「{item[0]}」は、原価態様による分類では何になるか？",
                "options": options,
                "correct": 0,
                "explanation": f"{item[0]}は操業度の変化に関わらず一定額発生するため、固定費に分類されます。",
                "level": 0
            }
        elif q_type == "cvp_basic":
            q = {
                "q": "CVP分析において、売上高から変動費を引いたものを何と呼ぶか？",
                "options": ["貢献利益 (限界利益)", "営業利益", "売上総利益", "純利益"],
                "correct": 0,
                "explanation": "売上高 - 変動費 = 貢献利益 (Contribution Margin) です。固定費を回収し、利益を生み出す源泉となります。",
                "level": 0
            }
        
        # Shuffle
        if "options" in q:
            correct_opt = q['options'][q['correct']]
            random.shuffle(q['options'])
            q['correct'] = q['options'].index(correct_opt)
        data["Management"].append(q)

    # --- Audit Basics ---
    audit_templates = [
        {
            "q": "公認会計士監査の主たる目的は何か？",
            "options": ["財務諸表の適正性に関する意見表明", "不正の摘発", "経営指導", "税務申告書の作成"],
            "correct": 0,
            "explanation": "財務諸表監査の目的は、財務諸表が適正に作成されているかどうかについて監査人が意見を表明することです（不正摘発は主目的ではありません）。",
            "level": 0
        },
        {
            "q": "監査人が守るべき「独立性」において、第三者から見て独立しているように見えることを何というか？",
            "options": ["外観的独立性", "精神的独立性", "経済的独立性", "物理的独立性"],
            "correct": 0,
            "explanation": "精神的独立性（事実上の独立性）だけでなく、第三者から疑われない外観的独立性も必要です。",
            "level": 0
        },
        {
            "q": "監査報告書において、財務諸表が適正であると認められる場合に表明される意見は？",
            "options": ["無限定適正意見", "限定付適正意見", "不適正意見", "意見不表明"],
            "correct": 0,
            "explanation": "重要な虚偽表示がなく適正である場合は「無限定適正意見」が表明されます。",
            "level": 0
        }
    ]
    for _ in range(count_per_subject):
        base = random.choice(audit_templates)
        q = base.copy()
        q['options'] = base['options'].copy()
        correct_opt = q['options'][q['correct']]
        random.shuffle(q['options'])
        q['correct'] = q['options'].index(correct_opt)
        data["Audit"].append(q)

    # --- Company Law Basics ---
    company_templates = [
        {
            "q": "株式会社の最高意思決定機関は何か？",
            "options": ["株主総会", "取締役会", "監査役会", "代表取締役"],
            "correct": 0,
            "explanation": "株主総会は、株主によって構成される株式会社の最高意思決定機関です。",
            "level": 0
        },
        {
            "q": "取締役の任期は、原則として選任後何年以内に終了する事業年度のうち最終のものに関する定時株主総会の終結の時までか？",
            "options": ["2年", "1年", "4年", "10年"],
            "correct": 0,
            "explanation": "公開会社における取締役の任期は原則として2年です（監査役は4年）。",
            "level": 0
        },
        {
            "q": "株式会社の設立に際して、出資される財産の価額の総額の2分の1を超えない額は、何として計上できるか？",
            "options": ["資本準備金", "利益準備金", "任意積立金", "資本金"],
            "correct": 0,
            "explanation": "会社法上、払込金額の1/2を超えない額は資本金に計上せず、資本準備金とすることができます。",
            "level": 0
        }
    ]
    for _ in range(count_per_subject):
        base = random.choice(company_templates)
        q = base.copy()
        q['options'] = base['options'].copy()
        correct_opt = q['options'][q['correct']]
        random.shuffle(q['options'])
        q['correct'] = q['options'].index(correct_opt)
        data["Company"].append(q)
        
    return data

def generate_financial_questions(count):
    questions = []
    seen = set()
    while len(questions) < count:
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
        s1 = _sig(q1)
        if s1 not in seen:
            q1['tags'] = ["減価償却"]
            seen.add(s1)
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
        s2 = _sig(q2)
        if s2 not in seen:
            q2['tags'] = ["キャッシュフロー"]
            seen.add(s2)
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
        s3 = _sig(q3)
        if s3 not in seen:
            q3['tags'] = ["在庫評価"]
            seen.add(s3)
            questions.append(q3)

        # Type 4: Consolidation (Goodwill) - Level 3
        parent_invest = random.randint(500, 2000) * 1000
        sub_net_assets = random.randint(300, 1500) * 1000
        ownership_rate = random.choice([0.6, 0.7, 0.8, 1.0])
        goodwill = parent_invest - (sub_net_assets * ownership_rate)
        
        # Ensure positive goodwill for simplicity
        if goodwill < 0:
             parent_invest = int(sub_net_assets * ownership_rate) + random.randint(10, 100) * 1000
             goodwill = parent_invest - (sub_net_assets * ownership_rate)
             
        q4 = {
            "q": f"P社はS社の発行済株式の{int(ownership_rate*100)}%を{parent_invest:,}円で取得し支配を獲得した。支配獲得日のS社の純資産が{sub_net_assets:,}円（すべて時価）であった場合、のれんの金額はいくらか？",
            "options": [
                f"{int(goodwill):,}円",
                f"{int(parent_invest - sub_net_assets):,}円",
                f"{int(goodwill * 1.1):,}円",
                f"{int(sub_net_assets * (1-ownership_rate)):,}円"
            ],
            "correct": 0,
            "explanation": f"のれん = 投資額 - (子会社純資産 × 持分比率) = {parent_invest:,} - ({sub_net_assets:,} × {ownership_rate}) = {int(goodwill):,}円",
            "level": 3
        }
        s4 = _sig(q4)
        if s4 not in seen:
            q4['tags'] = ["連結・のれん"]
            seen.add(s4)
            questions.append(q4)

    return questions

def generate_management_questions(count):
    questions = []
    seen = set()
    while len(questions) < count:
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
        s1 = _sig(q1)
        if s1 not in seen:
            q1['tags'] = ["CVP・BEP"]
            seen.add(s1)
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
        s2 = _sig(q2)
        if s2 not in seen:
            q2['tags'] = ["原価差異・材料"]
            seen.add(s2)
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
        s3 = _sig(q3)
        if s3 not in seen:
            q3['tags'] = ["ROI"]
            seen.add(s3)
            questions.append(q3)

    return questions

def generate_audit_questions(count):
    questions = []
    # Expanded templates for Audit Theory
    templates = [
        {
            "q": "監査リスク・モデルにおいて、監査リスク(AR)は、重大な虚偽表示リスク(RMM)と何の積として表されるか？",
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
    
    seen = set()
    while len(questions) < count:
        base = random.choice(templates)
        q = base.copy()
        q['options'] = base['options'].copy()
        correct_option = q['options'][q['correct']]
        random.shuffle(q['options'])
        q['correct'] = q['options'].index(correct_option)
        q['tags'] = _tag_for_text(q['q'], "監査")
        s = _sig(q)
        if s not in seen:
            seen.add(s)
            questions.append(q)
        
    return questions

def generate_company_law_questions(count):
    questions = []
    # Expanded templates for Company Law
    templates = [
        {
            "q": "株式会社の設立に際して、発起人が割り当てを受ける設立時発行株式の総数の下限に関する規定として適切なものはどれか？",
            "options": ["制限はない", "4分の1", "2分の1", "3分の1"],
            "correct": 0,
            "explanation": "公開会社でない場合や設立時は、発行可能株式総数の引受割合に法定の制限はない（公開会社の定款変更時とは異なる）。",
            "level": 2
        },
        {
            "q": "吸収合併において、存続会社が消滅会社の株主に対して交付する対価として認められるものは何か？",
            "options": ["金銭、株式、その他の財産すべて認められる", "株式のみ", "金銭のみ", "社債のみ"],
            "correct": 0,
            "explanation": "会社法上、合併対価の柔軟化により、株式だけでなく金銭やその他の財産（親会社株式など）も対価として認められる（交付金合併など）。",
            "level": 3
        },
        {
            "q": "株式交換において、完全子会社となる会社の株主総会決議は原則として何決議が必要か？",
            "options": ["特別決議", "普通決議", "特殊決議", "取締役会決議のみ"],
            "correct": 0,
            "explanation": "株式交換契約の承認には、原則として株主総会の特別決議（議決権の過半数出席＋2/3以上の賛成）が必要である。",
            "level": 3
        },
        {
            "q": "取締役会設置会社における取締役の任期の原則は何年か？",
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
            "q": "株主総会の普通決議の定足数の原則として適切なものはどれか？",
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
    
    seen = set()
    while len(questions) < count:
        base = random.choice(templates)
        q = base.copy()
        q['options'] = base['options'].copy()
        correct_option = q['options'][q['correct']]
        random.shuffle(q['options'])
        q['correct'] = q['options'].index(correct_option)
        q['tags'] = _tag_for_text(q['q'], "会社法")
        s = _sig(q)
        if s not in seen:
            seen.add(s)
            questions.append(q)
    return questions

def _assign_metadata(all_data, seed):
    for subject, items in all_data.items():
        for idx, q in enumerate(items):
            base = q.get('q', '') + '|' + '|'.join(q.get('options', [])) + '|' + str(q.get('correct'))
            q['id'] = hashlib.md5((str(seed) + '|' + subject + '|' + base).encode('utf-8')).hexdigest()
            q['subject'] = subject
            if 'tags' not in q:
                q['tags'] = _tag_for_text(q.get('q',''), subject)

def main(seed=None):
    if seed is not None:
        try:
            random.seed(int(seed))
        except Exception:
            random.seed(seed)
    # Generate Intro/Basic Questions (Level 0)
    intro_data = generate_intro_questions(150)

    # Generate Standard/Advanced Questions (Level 2/3)
    # Financial: 3 types * 200 = 600
    # Management: 3 types * 200 = 600
    # Audit: 10 templates * 40 = 400
    # Company: 10 templates * 40 = 400
    
    financial = generate_financial_questions(1200)
    management = generate_management_questions(1200)
    audit = generate_audit_questions(800)
    company = generate_company_law_questions(800)
    
    # Merge Intro questions
    financial.extend(intro_data["Financial"])
    management.extend(intro_data["Management"])
    audit.extend(intro_data["Audit"])
    company.extend(intro_data["Company"])
    
    all_data = {
        "Financial": financial,
        "Management": management,
        "Audit": audit,
        "Company": company
    }
    _assign_metadata(all_data, seed)
    
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

    # Additionally write sharded files by Subject x Level
    shards_dir = os.path.join(output_dir, "questions")
    os.makedirs(shards_dir, exist_ok=True)
    manifest = {"shards": []}
    for subject, items in all_data.items():
        # group by level
        buckets = {}
        for q in items:
            lvl = q.get("level")
            buckets.setdefault(lvl, []).append(q)
        for lvl, arr in buckets.items():
            # level might be None in legacy; skip shards without defined level
            if lvl is None:
                continue
            shard_name = f"{subject}_L{lvl}.json"
            shard_path = os.path.join(shards_dir, shard_name)
            with open(shard_path, "w", encoding="utf-8") as sf:
                json.dump(arr, sf, ensure_ascii=False, indent=2)
            manifest["shards"].append({"subject": subject, "level": lvl, "file": shard_name, "count": len(arr)})
    # write manifest
    with open(os.path.join(shards_dir, "manifest.json"), "w", encoding="utf-8") as mf:
        json.dump(manifest, mf, ensure_ascii=False, indent=2)
    
    print(f"Generated {len(financial)} Financial, {len(management)} Management, {len(audit)} Audit, {len(company)} Company questions.")
    print(f"Saved to {output_dir}")

if __name__ == "__main__":
    env_seed = os.environ.get("CPA_Q_SEED")
    main(seed=env_seed)
