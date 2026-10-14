import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)


def money(value):
    """Format revenue as £1.43M or £167K."""
    if value >= 1_000_000:
        return f"£{value / 1_000_000:.2f}M"
    return f"£{value / 1_000:.0f}K"


# ============================================================
# 1. Load the data
# ============================================================
df_raw = pd.read_csv("OnlineRetail.csv.zip", encoding="ISO-8859-1")
df_raw["InvoiceDate"] = pd.to_datetime(df_raw["InvoiceDate"])
print(f"Raw rows: {len(df_raw):,}")


# ============================================================
# 2. Data quality check (before cleaning)
# ============================================================
non_product_codes = [
    "POST", "DOT", "M", "D", "C2", "S", "B",
    "BANK CHARGES", "AMAZONFEE", "CRUK", "PADS",
]

is_cancel = df_raw["InvoiceNo"].astype(str).str.startswith("C")
is_bad_qty = df_raw["Quantity"] <= 0
is_bad_price = df_raw["UnitPrice"] <= 0
is_non_product = df_raw["StockCode"].astype(str).str.upper().isin(non_product_codes)
is_missing_cust = df_raw["CustomerID"].isna()

print(f"Cancelled invoices:      {is_cancel.sum():,}")
print(f"Zero/negative quantity:  {is_bad_qty.sum():,}")
print(f"Zero/negative price:     {is_bad_price.sum():,}")
print(f"Non-product rows:        {is_non_product.sum():,}")
print(f"Missing CustomerID:      {is_missing_cust.sum():,}")
print(f"Last invoice date:       {df_raw['InvoiceDate'].max()}")


# ============================================================
# 3. Clean
# ============================================================
df = df_raw[~is_cancel & ~is_bad_qty & ~is_bad_price & ~is_non_product].copy()

# Remove orders that were later cancelled
cancels = df_raw[is_cancel].copy()
cancels["Quantity"] = -cancels["Quantity"]
cancel_keys = cancels[["CustomerID", "StockCode", "Quantity"]].drop_duplicates()

before = len(df)
df = df.merge(cancel_keys, on=["CustomerID", "StockCode", "Quantity"],
              how="left", indicator=True)
df = df[df["_merge"] == "left_only"].drop(columns="_merge")
print(f"Orders matched to a cancellation: {before - len(df):,}")
print(f"Clean rows: {len(df):,} ({len(df) / len(df_raw):.1%} of raw)")

df["Revenue"] = df["Quantity"] * df["UnitPrice"]
df["YearMonth"] = df["InvoiceDate"].dt.to_period("M")


# ============================================================
# 4. Monthly revenue (Dec 2011 is a partial month)
# ============================================================
monthly = df.groupby("YearMonth")["Revenue"].sum()
full_months = monthly.drop(pd.Period("2011-12"))
months = monthly.index.astype(str)

plt.figure(figsize=(13, 6))
plt.plot(months, monthly.values, marker="o", color="#2E86AB")
plt.scatter(["2011-12"], [monthly[pd.Period("2011-12")]], color="gray", zorder=3,
            label="Dec 2011 (partial month)")

for x, y in zip(months, monthly.values):
    plt.text(x, y + 25_000, money(y), ha="center", va="bottom",
             fontsize=9, fontweight="bold")

plt.ylim(0, monthly.max() * 1.12)
plt.title("Monthly Revenue (Dec 2010 to Dec 2011)", fontsize=16, fontweight="bold")
plt.ylabel("Revenue (£)")
plt.xticks(rotation=45)
plt.legend(loc="upper left")
plt.tight_layout()
plt.savefig("images/monthly_revenue.png", dpi=150)
plt.close()

print(f"Total revenue:            £{monthly.sum():,.0f}")
print(f"Avg full-month revenue:   £{full_months.mean():,.0f}")
print(f"Peak month:               {full_months.idxmax()} at £{full_months.max():,.0f}")
print(f"Peak vs average:          {full_months.max() / full_months.mean():.1f}x")


# ============================================================
# 5. Top 10 products
# ============================================================
top_products = df.groupby("Description")["Revenue"].sum().nlargest(10)

plt.figure(figsize=(12, 6))
plt.barh(top_products.index, top_products.values, color="#A23B72")
for i, value in enumerate(top_products.values):
    plt.text(value + top_products.max() * 0.01, i, money(value),
             va="center", fontsize=10, fontweight="bold")

plt.xlim(0, top_products.max() * 1.12)
plt.gca().invert_yaxis()
plt.title("Top 10 Products by Revenue", fontsize=16, fontweight="bold")
plt.xlabel("Revenue (£)")
plt.tight_layout()
plt.savefig("images/top_products.png", dpi=150)
plt.close()

print(top_products.round(0))


# ============================================================
# 6. Top 10 countries
# ============================================================
country = df.groupby("Country")["Revenue"].sum().sort_values(ascending=False)
top_countries = country.head(10)

plt.figure(figsize=(12, 6))
plt.bar(top_countries.index, top_countries.values, color="#F18F01")
for i, value in enumerate(top_countries.values):
    plt.text(i, value + top_countries.max() * 0.01, money(value),
             ha="center", va="bottom", fontsize=10, fontweight="bold")

plt.ylim(0, top_countries.max() * 1.1)
plt.title("Top 10 Countries by Revenue", fontsize=16, fontweight="bold")
plt.ylabel("Revenue (£)")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("images/top_countries.png", dpi=150)
plt.close()

print(f"UK share of revenue: {country['United Kingdom'] / country.sum():.1%}")
print(country.head(4).round(0))