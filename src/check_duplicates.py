import pandas as pd

# Load files
source2 = pd.read_csv("../data/source2_gig_workers.csv")
source3 = pd.read_csv("../data/source3_cbnexus_contacts.csv")


# ==========================================
# SOURCE 2
# ==========================================

print("\n==============================")
print("SOURCE 2 - GIG WORKERS")
print("==============================")

print("Rows:", len(source2))
print("Unique emails:", source2["normalized_email"].nunique())

duplicates_2 = source2[
    source2["normalized_email"].duplicated(keep=False)
]

print("\nDuplicate emails:")

if duplicates_2.empty:
    print("No duplicate emails found.")
else:
    print(
        duplicates_2[
            ["worker_name", "normalized_email"]
        ].to_string(index=False)
    )


# ==========================================
# SOURCE 3
# ==========================================

print("\n==============================")
print("SOURCE 3 - CB NEXUS")
print("==============================")

print("Rows:", len(source3))
print("Unique phones:", source3["normalized_phone_no"].nunique())

duplicates_3 = source3[
    source3["normalized_phone_no"].duplicated(keep=False)
]

print("\nDuplicate phones:")

if duplicates_3.empty:
    print("No duplicate phones found.")
else:
    print(
        duplicates_3[
            ["Name", "normalized_phone_no"]
        ].to_string(index=False)
    )