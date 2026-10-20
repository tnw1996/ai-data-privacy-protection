import pandas as pd
from presidio_analyzer import AnalyzerEngine
df = pd.read_csv("sample_data.csv")
analyzer = AnalyzerEngine()

for column in df.columns:
    for value in df[column].dropna():
        text = str(value)

        results = analyzer.analyze(
            text=text,
            language="en"
        )

        for result in results:
            detected_value = text[result.start:result.end]

            print(
                f"PII Type: {result.entity_type} | "
                f"Value: {detected_value} | "
                f"Confidence: {result.score:.2f}"
            )