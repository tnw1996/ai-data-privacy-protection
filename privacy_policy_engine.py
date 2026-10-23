
import pandas as pd
from pathlib import Path
from presidio_analyzer import AnalyzerEngine

INPUT_FILE = Path("sample_data.csv")
OUTPUT_FILE = Path("policy_protected_data.csv")

analyzer = AnalyzerEngine()

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


def mask_value(value, entity_type):
    value = str(value)

    if entity_type == "PHONE_NUMBER":
        digit_count = sum(char.isdigit() for char in value)

        if digit_count <= 4:
            return "".join(
                "*" if char.isdigit() else char
                for char in value
            )

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

    return "[MASKED]"


def apply_policy(value):
    if pd.isna(value) or not isinstance(value, str):
        return value, [], False

    results = analyzer.analyze(
        text=value,
        language="en"
    )

    results = [
        result for result in results
        if result.score >= MIN_CONFIDENCE
        or result.entity_type == "PHONE_NUMBER"
    ]

    if not results:
        return value, [], False

    actions = [
        (
            result.entity_type,
            PRIVACY_POLICIES.get(
                result.entity_type, "REVIEW"
            ),
            round(result.score, 2)
        )
        for result in results
    ]

    for result in results:
        action = PRIVACY_POLICIES.get(
            result.entity_type, "REVIEW"
        )

        if action == "BLOCK":
            return None, actions, True

        if action == "REVIEW":
            return None, actions, True

    protected_value = value

    for result in sorted(
        results,
        key=lambda item: item.start,
        reverse=True
    ):
        entity = result.entity_type
        action = PRIVACY_POLICIES[entity]

        original = value[result.start:result.end]

        if action == "ANONYMIZE":
            replacement = f"[{entity}]"
        elif action == "MASK":
            replacement = mask_value(original, entity)
        else:
            return None, actions, True

        protected_value = (
            protected_value[:result.start]
            + replacement
            + protected_value[result.end:]
        )

    return protected_value, actions, False


def main():
    if not INPUT_FILE.exists():
        print(f"ERROR: Input file not found: {INPUT_FILE}")
        return

    try:
        df = pd.read_csv(INPUT_FILE, dtype=str)
    except Exception as error:
        print(f"ERROR reading CSV: {error}")
        return

    protected_df = df.copy()
    all_actions = []
    blocked_items = []

    for column in df.columns:
        for index, value in df[column].items():
            protected, actions, blocked = apply_policy(value)

            all_actions.extend(
                (entity, action, score)
                for entity, action, score in actions
            )

            if blocked:
                blocked_items.append(
                    (column, index + 2, actions)
                )
            else:
                protected_df.at[index, column] = protected

    print("\n--- Privacy Policy Report ---")

    if all_actions:
        for entity, action in sorted(
            set(
                (entity, action)
                for entity, action, score in all_actions
            )
        ):
            print(f"{entity}: {action}")
    else:
        print("No PII detected above the confidence threshold.")

    if blocked_items:
        if OUTPUT_FILE.exists():
            OUTPUT_FILE.unlink()

        print("\nFile BLOCKED.")

        for column, row, actions in blocked_items:
            print(f"Column '{column}', row {row}:")

            for entity, action, score in actions:
                print(
                    f"  Entity: {entity}; "
                    f"Policy: {action}; "
                    f"Confidence: {score}"
                )

        print("No protected output was approved.")
        return

    try:
        protected_df.to_csv(OUTPUT_FILE, index=False)
    except OSError as error:
        print(f"ERROR saving output: {error}")
        return

    print("\nFile approved by the configured rules.")
    print(f"Protected file saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
