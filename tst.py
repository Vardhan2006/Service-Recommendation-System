import pandas as pd

df = pd.read_csv("armut_data.csv")
df["Service_Code"] = df["ServiceId"].astype(str) + "_" + df["CategoryId"].astype(str)
unique_codes = sorted(df["Service_Code"].unique())

print("Total unique combinations:", len(unique_codes))
print(unique_codes)
