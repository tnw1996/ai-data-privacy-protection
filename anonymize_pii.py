
import pandas as pd
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

df = pd.read_csv("sample_data.csv")

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

anonymized_df = df.copy()

for column in df.columns:
    for index, value in df[column].items():
        if pd.isna(value):
            continue

        text = str(value)

        results = analyzer.analyze(
            text=text,
            language="en"
        )

        if results:
            anonymized_result = anonymizer.anonymize(
                text=text,
                analyzer_results=results
            )

            anonymized_df.at[index, column] = (
                anonymized_result.text
            )

anonymized_df.to_csv(
    "anonymized_data.csv",
    index=False
)

print("Original data:")
print(df.to_string(index=False))

print("\nAnonymized data:")
print(anonymized_df.to_string(index=False))

print("\nSaved anonymized data to anonymized_data.csv")
