import pandas as pd

def mask_email(email):
    if pd.isna(email) or "@" not in str(email):
        return email

    name, domain = str(email).split("@", 1)
    return name[0] + "***@" + domain

def mask_phone(phone):
    if pd.isna(phone):
        return phone

    phone = str(phone)

    if len(phone) <= 4:
        return "*" * len(phone)

    return "*" * (len(phone) - 4) + phone[-4:]

df = pd.read_csv("sample_data.csv")

if "Email" in df.columns:
    df["Email"] = df["Email"].apply(mask_email)

if "Phone" in df.columns:
    df["Phone"] = df["Phone"].apply(mask_phone)

df.to_csv("masked_data.csv", index=False)

print("Masked dataset:")
print(df.to_string(index=False))

print("\nMasked data saved to masked_data.csv")
