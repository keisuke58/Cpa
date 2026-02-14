import os
import json
import pypdf
from janome.tokenizer import Tokenizer
from collections import Counter

exam_dir = "EXAM"
vocab_file = "exam_vocab.json"
metadata_file = "exam_metadata.json"

# Known unimportant words or stopwords
STOPWORDS = set([
    "の", "に", "は", "を", "た", "が", "で", "て", "と", "し", "れ", "さ", "ある", "いる", "する", "ない", 
    "よう", "もの", "こと", "ため", "なり", "これ", "それ", "あり", "よっ", "等", "及び", "又は", 
    "並び", "その", "この", "から", "また", "へ", "ば", "より", "など", "ます", "まで", "お", 
    "問題", "正解", "番号", "試験", "解答", "用紙", "注意事項", "受験", "令和", "年度", "ページ",
    "次", "記述", "うち", "最も", "適切", "選べ", "マーク", "場合", "第", "問", "年"
])

def extract_vocab_from_pdf(pdf_path, subject_name):
    text = ""
    try:
        reader = pypdf.PdfReader(pdf_path)
        for page in reader.pages:
            text += page.extract_text()
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return []

    t = Tokenizer()
    words = []
    
    # Extract nouns (名詞)
    for token in t.tokenize(text):
        pos = token.part_of_speech.split(',')[0]
        word = token.surface
        
        # Filter: Nouns only, length > 1, not in stopwords, not a number
        if pos == '名詞' and len(word) > 1 and word not in STOPWORDS and not word.isdigit():
            # Filter out simple numbers/dates
            if not any(char.isdigit() for char in word):
                 words.append(word)
    
    return words

def main():
    # Load metadata to map file -> subject
    file_to_subject = {}
    if os.path.exists(metadata_file):
        with open(metadata_file, "r", encoding="utf-8") as f:
            meta = json.load(f)
            for k, v in meta.items():
                if v.get('subject'):
                    # Simplify subject name (remove English part)
                    # "企業法 (Corporate Law)" -> "企業法"
                    simple_subject = v['subject'].split(' ')[0]
                    file_to_subject[k] = simple_subject

    # Process files
    subject_vocab = {} # {subject: Counter}
    
    pdf_files = [f for f in os.listdir(exam_dir) if f.endswith(".pdf")]
    
    for pdf_file in pdf_files:
        print(f"Processing {pdf_file}...")
        subject = file_to_subject.get(pdf_file, "Uncategorized")
        
        if subject not in subject_vocab:
            subject_vocab[subject] = Counter()
            
        words = extract_vocab_from_pdf(os.path.join(exam_dir, pdf_file), subject)
        subject_vocab[subject].update(words)

    # Convert to JSON structure (Top 50 words per subject)
    final_output = {}
    for subject, counter in subject_vocab.items():
        top_words = counter.most_common(50)
        final_output[subject] = [{"word": w, "count": c} for w, c in top_words]

    with open(vocab_file, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=4, ensure_ascii=False)
    
    print(f"Vocabulary saved to {vocab_file}")

if __name__ == "__main__":
    main()
