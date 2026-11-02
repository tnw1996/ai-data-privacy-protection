import pandas as pd
import ollama
from pathlib import Path

INPUT_FILE = Path("policy_protected_data.csv")
OUTPUT_FILE = Path("llm_analysis.txt")
MODEL_NAME = "llama3.2:3b"

def load_protected_data():
    """Load the privacy-protected dataset."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            "Protected dataset not found."
        )

    df = pd.read_csv(INPUT_FILE, dtype=str).fillna("")

    protected_markers = (
        "[PERSON]",
        "[EMAIL_ADDRESS]",
        "[URL]",
        "[MASKED]",
        "*"
    )

    has_protected_values = any(
        any(marker in str(value) for marker in protected_markers)
        for value in df.values.flatten()
    )

    if not has_protected_values:
        raise ValueError(
            "No privacy-protection markers found. "
            "LLM processing stopped."
        )

    return df


def analyse_with_llm(df):
    """Send protected records to the local LLM."""

    protected_data = df.to_csv(index=False)

    prompt = f"""
You are a data analysis assistant.

Analyse the following privacy-protected customer dataset.

The data has already undergone privacy processing.
Do not attempt to identify individuals or reconstruct
their original personal information.

Please provide:
1. A short dataset summary.
2. Main customer enquiry categories.
3. Important observations.
4. Suggestions for improving customer support.

Protected dataset:

{protected_data}
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


def main():
    try:
        print("Loading protected dataset...")

        df = load_protected_data()

        print("Protected dataset loaded.")
        print("Connecting to local Ollama model...")

        result = analyse_with_llm(df)

        print("\n========== LLM ANALYSIS ==========")
        print(result)
        print("==================================")

        OUTPUT_FILE.write_text(
            result,
            encoding="utf-8"
        )

        print("\nAnalysis saved to:", OUTPUT_FILE)

    except Exception as error:
        print("\nLLM processing failed:", error)

if __name__ == "__main__":
    main()
