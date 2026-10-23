import pandas as pd
from presidio_analyzer import AnalyzerEngine

INPUT_FILE = "evaluation_dataset.csv"

df = pd.read_csv(INPUT_FILE, dtype=str).fillna("")
analyzer = AnalyzerEngine()

true_positive = 0
false_positive = 0
false_negative = 0

print("Starting privacy detection evaluation...\n")

for index, row in df.iterrows():
    text = row["text"]

    expected = {
        entity.strip()
        for entity in row["expected_entities"].split(";")
        if entity.strip() and entity.strip() != "NONE"
    }

    results = analyzer.analyze(
        text=text,
        language="en"
    )

    filtered_results = []

    for result in results:
        redundant = False

        for other in results:
            if result is other:
                continue

            overlaps = (
                result.start < other.end
                and other.start < result.end
            )

            if not overlaps:
                continue

            if (
                result.entity_type == "URL"
                and other.entity_type == "EMAIL_ADDRESS"
                and other.start <= result.start
                and other.end >= result.end
            ):
                redundant = True
                break

            if (
                result.entity_type in {
                    "US_BANK_NUMBER",
                    "US_DRIVER_LICENSE"
                }
                and other.entity_type == "CREDIT_CARD"
                and other.start <= result.start
                and other.end >= result.end
            ):
                redundant = True
                break

        if not redundant:
            filtered_results.append(result)

    detected = {
        result.entity_type
        for result in filtered_results
    }

    tp = expected & detected
    fp = detected - expected
    fn = expected - detected

    true_positive += len(tp)
    false_positive += len(fp)
    false_negative += len(fn)

    if fp or fn:
        print(f"Test case {index + 1}:")
        print(f"  Text: {text}")
        print(f"  Expected: {sorted(expected) or ['NONE']}")
        print(f"  Detected: {sorted(detected) or ['NONE']}")

        if fp:
            print(f"  Unexpected detections: {sorted(fp)}")

        if fn:
            print(f"  Missed entities: {sorted(fn)}")

        print()

precision = (
    true_positive / (true_positive + false_positive)
    if true_positive + false_positive > 0
    else 0
)

recall = (
    true_positive / (true_positive + false_negative)
    if true_positive + false_negative > 0
    else 0
)

f1_score = (
    2 * precision * recall / (precision + recall)
    if precision + recall > 0
    else 0
)

print("\n--- Evaluation Results ---")
print(f"Total test cases: {len(df)}")
print(f"True positives: {true_positive}")
print(f"False positives: {false_positive}")
print(f"False negatives: {false_negative}")
print(f"Precision: {precision:.2%}")
print(f"Recall: {recall:.2%}")
print(f"F1-score: {f1_score:.2%}")
