import os
import pypdf

exam_dir = "EXAM"
pdf_files = [f for f in os.listdir(exam_dir) if f.endswith(".pdf")]

for pdf_file in sorted(pdf_files):
    pdf_path = os.path.join(exam_dir, pdf_file)
    try:
        reader = pypdf.PdfReader(pdf_path)
        if len(reader.pages) > 0:
            text = reader.pages[0].extract_text()
            # Clean up text a bit for display
            text_lines = [line.strip() for line in text.split('\n') if line.strip()]
            print(f"--- {pdf_file} ---")
            for i, line in enumerate(text_lines[:10]): # Print first 10 lines
                print(f"{i}: {line}")
            print("\n")
    except Exception as e:
        print(f"Error reading {pdf_file}: {e}")
