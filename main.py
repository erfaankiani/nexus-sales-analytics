import pandas as pd

df = pd.read_csv("sales.csv")

df["Total"] = df["Price"] * df["Quantity"]

total_revenue = df["Total"].sum()
total_items = df["Quantity"].sum()

best_selling = df.groupby("Product")["Quantity"].sum().idxmax()
top_revenue = df.groupby("Product")["Total"].sum().idxmax()

print("SALES ANALYSIS REPORT")
print("-" * 30)
print("Total Revenue:", total_revenue)
print("Items Sold:", total_items)
print("Best Selling Product:", best_selling)
print("Highest Revenue Product:", top_revenue)

df.to_csv("sales_report.csv", index=False)

print("\nReport saved successfully!")