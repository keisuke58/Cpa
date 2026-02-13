import os
import json
import re
import pypdf

exam_dir = "EXAM"
metadata_file = "exam_metadata.json"

def extract_info(text):
    info = {"year": "", "type": "", "subject": ""}
    
    # Year
    year_match = re.search(r'(令和\s*[0-9０-９]+\s*年)', text)
    if year_match:
        info["year"] = year_match.group(1).replace(" ", "")
    
    # Type
    if "短答式" in text:
        info["type"] = "Short-Answer (Tanto)"
        if "第 Ⅰ 回" in text or "第Ⅰ回" in text:
            info["type"] += " I"
        elif "第 Ⅱ 回" in text or "第Ⅱ回" in text:
            info["type"] += " II"
    elif "論文式" in text:
        info["type"] = "Essay (Ronbun)"
    elif "正　解" in text or "正 解" in text:
        info["type"] = "Answer Key"
    
    # Subject
    subjects = {
        "企業法": "Corporate Law",
        "管理会計論": "Management Accounting",
        "監査論": "Audit",
        "財務会計論": "Financial Accounting",
        "租税法": "Tax Law",
        "経営学": "Business Admin",
        "経済学": "Economics",
        "統計学": "Statistics"
    }
    for jp, en in subjects.items():
        if jp in text:
            info["subject"] = f"{jp} ({en})"
            break
            
    return info

metadata = {}
pdf_files = [f for f in os.listdir(exam_dir) if f.endswith(".pdf")]

for pdf_file in sorted(pdf_files):
    pdf_path = os.path.join(exam_dir, pdf_file)
    try:
        reader = pypdf.PdfReader(pdf_path)
        if len(reader.pages) > 0:
            text = reader.pages[0].extract_text()
            info = extract_info(text)
            
            # Fallback/Cleanup if extraction failed
            if not info["subject"]:
                # Try to guess from filename number
                if pdf_file.startswith("01"): info["subject"] = "企業法 (Corporate Law)"
                elif pdf_file.startswith("02"): info["subject"] = "管理会計論 (Management Accounting)"
                elif pdf_file.startswith("03"): info["subject"] = "監査論 (Audit)"
                elif pdf_file.startswith("04"): info["subject"] = "財務会計論 (Financial Accounting)"
                elif pdf_file.startswith("05"): info["subject"] = "租税法 (Tax Law)"
                elif pdf_file.startswith("06"): info["subject"] = "経営学 (Business Admin)"
                elif pdf_file.startswith("07"): info["subject"] = "経済学 (Economics)"
                elif pdf_file.startswith("09"): info["subject"] = "統計学 (Statistics)"
            
            metadata[pdf_file] = info
            print(f"Processed {pdf_file}: {info}")
            
    except Exception as e:
        print(f"Error processing {pdf_file}: {e}")

with open(metadata_file, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=4, ensure_ascii=False)

print(f"Metadata saved to {metadata_file}")
