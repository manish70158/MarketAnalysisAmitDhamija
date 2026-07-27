"""
NSE CSV Inspector
Analyzes the structure of NSE participant OI CSV file
to understand how to parse it correctly
"""

import pandas as pd
import sys

def inspect_csv(csv_file):
    """Inspect CSV file structure"""
    print("\n" + "="*70)
    print(f"Inspecting: {csv_file}")
    print("="*70 + "\n")

    try:
        # Try reading with default settings
        print("Attempting to read CSV...")
        df = pd.read_csv(csv_file)

        print(f"✓ Successfully loaded!")
        print(f"\n📊 Basic Info:")
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {len(df.columns)}")

        print(f"\n📋 Column Names:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i}. {col}")

        print(f"\n🔍 First 10 Rows:")
        print("-" * 70)
        print(df.head(10).to_string())

        print(f"\n📈 Data Types:")
        print("-" * 70)
        print(df.dtypes)

        print(f"\n📝 Sample Values from Each Column:")
        print("-" * 70)
        for col in df.columns:
            sample_values = df[col].dropna().head(3).tolist()
            print(f"   {col}: {sample_values}")

        # Check for specific keywords
        print(f"\n🔎 Looking for key terms...")
        key_terms = ['Client', 'DII', 'FII', 'Pro', 'Long', 'Short', 'Future', 'Option', 'Call', 'Put']
        for term in key_terms:
            found = False
            for col in df.columns:
                if term.lower() in str(col).lower():
                    print(f"   ✓ Found '{term}' in column: {col}")
                    found = True
            if not found:
                # Check in data
                for col in df.columns:
                    if df[col].astype(str).str.contains(term, case=False).any():
                        print(f"   ✓ Found '{term}' in data of column: {col}")
                        found = True
                        break

        print("\n" + "="*70)
        print("✓ Inspection complete!")
        print("="*70 + "\n")

        return df

    except Exception as e:
        print(f"✗ Error reading CSV: {e}")
        print("\nTrying alternative methods...\n")

        # Try reading first few lines as text
        try:
            with open(csv_file, 'r') as f:
                print("First 20 lines of file:")
                print("-" * 70)
                for i, line in enumerate(f, 1):
                    if i <= 20:
                        print(f"{i:3d}: {line.rstrip()}")
                    else:
                        break
        except Exception as e2:
            print(f"✗ Error reading as text: {e2}")

        return None


def main():
    if len(sys.argv) < 2:
        print("\n" + "="*70)
        print("NSE CSV Inspector")
        print("="*70)
        print("\nUsage: python inspect_nse_csv.py <path-to-csv-file>")
        print("\nExample:")
        print("  python inspect_nse_csv.py fao_participant_oi_24JUL2026.csv")
        print("\n" + "="*70 + "\n")
        return

    csv_file = sys.argv[1]
    inspect_csv(csv_file)


if __name__ == "__main__":
    main()
