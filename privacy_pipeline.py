import pandas as pd
from pathlib import Path
from presidio_analyzer import AnalyzerEngine

INPUT_FILE = Path("sample_data.csv")
OUTPUT_FILE = Path("pipeline_protected_data.csv")

PRIVACY_POLICIES = {
    "PERSON": "ANONYMIZE",
    "EMAIL_ADDRESS": "ANONYMIZE",
    "PHONE_NUMBER": "MASK",
    "URL": "ANONYMIZE",
    "CREDIT_CARD": "BLOCK",
    "US_SSN": "BLOCK",
    "DATE_TIME": "ANONYMIZE",
    "US_BANK_NUMBER": "REVIEW",
    "US_DRIVER_LICENSE": "REVIEW",
}

MIN_CONFIDENCE = 0.5

analyzer = AnalyzerEngine()


def mask_phone(value):
    remaining = 4
    masked = []

    for char in reversed(value):
        if char.isdigit():
            if remaining > 0:
                masked.append(char)
                remaining -= 1
            else:
                masked.append("*")
        else:
            masked.append(char)

    return "".join(reversed(masked))


def protect_value(value):
    if pd.isna(value) or not isinstance(value, str):
        return value, [], False

    detections = analyzer.analyze(
        text=value,
        language="en"
    )

    detections = [
        item for item in detections
        if item.score >= MIN_CONFIDENCE
        or item.entity_type == "PHONE_NUMBER"
    ]

    actions = [
        (
            item.entity_type,
            PRIVACY_POLICIES.get(item.entity_type, "REVIEW")
        )
        for item in detections
    ]

    for item in detections:
        action = PRIVACY_POLICIES.get(
            item.entity_type, "REVIEW"
        )

        if action in ("BLOCK", "REVIEW"):
            return None, actions, True

    protected = value

    for item in sorted(
        detections,
        key=lambda result: result.start,
        reverse=True
    ):
        entity = item.entity_type
        action = PRIVACY_POLICIES[entity]
        original = value[item.start:item.end]

        if action == "ANONYMIZE":
            replacement = f"[{entity}]"
        elif action == "MASK":
            replacement = mask_phone(original)
        else:
            return None, actions, True

        protected = (
            protected[:item.start]
            + replacement
            + protected[item.end:]
        )

    return protected, actions, False


def main():
    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        return

    try:
        data = pd.read_csv(INPUT_FILE, dtype=str)
    except Exception as error:
        print(f"Could not read CSV: {error}")
        return

    protected_data = data.copy()
    blocked = []

    for column in data.columns:
        for index, value in data[column].items():
            protected, actions, is_blocked = protect_value(value)

            if is_blocked:
                blocked.append((column, index + 2, actions))
            else:
                protected_data.at[index, column] = protected

    if blocked:
        if OUTPUT_FILE.exists():
            OUTPUT_FILE.unlink()

        print("File BLOCKED by the privacy policy.")

        for column, row, actions in blocked:
            print(f"Column: {column}, row: {row}")
            for entity, action in actions:
                print(f"  {entity}: {action}")

        print("No protected output was approved.")
        return

    try:
        protected_data.to_csv(OUTPUT_FILE, index=False)
    except OSError as error:
        print(f"Could not save output: {error}")
        return

    print("Privacy pipeline completed successfully.")
    print(f"Protected file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
