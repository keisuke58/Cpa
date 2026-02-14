import pandas as pd
import os

file_path = r"C:\Users\nishioka\kaggle\CPA\studying\0-簿記入門コース.xlsx"

try:
    xl = pd.ExcelFile(file_path)
    print(f"Sheet names: {xl.sheet_names}")
    for sheet in xl.sheet_names:
        print(f"\n--- Sheet: {sheet} ---")
        df = pd.read_excel(file_path, sheet_name=sheet, nrows=5)
        print(df.to_string())
except Exception as e:
    print(f"Error reading Excel file: {e}")
