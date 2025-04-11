import pandas as pd
import numpy as np

# Basic DataFrame creation
data = {
  "points": [100, 120, 114],
  "total": [350, 340, 402],
  "category": ["A", "B", "C"]
}

df = pd.DataFrame(data)

# Case 1: Single column access with string literal - should return Series
s1 = df["total"]

# Case 2: Multiple columns access with list of strings - should return DataFrame
df1 = df[["points", "total"]]

# Case 3: Column access using a variable
col_name = "category"
s2 = df[col_name]

# Case 4: Boolean mask filtering - should return DataFrame
mask = df["points"] > 110
filtered_df = df[mask]

# Case 5: Series extraction after mask filtering - should return Series
filtered_s = df[mask]["total"]

# Case 6: Complex boolean condition filtering - should return DataFrame
complex_filtered_df = df[(df["points"] > 110) & (df["total"] < 400)]

# Case 7: Series extraction after complex filtering - should return Series
s3 = df[(df["points"] > 110) & (df["total"] < 400)]["category"]

# Case 8: Negated boolean condition
s4 = df[~(df["points"] < 115)]["total"]

# Case 9: iloc indexer - should return various types based on indexing
s5 = df.iloc[0]  # Returns Series for a single row

# Case 10: loc indexer with column access - should return Series
s6 = df.loc[0, "points"]

# Case 11: Boolean indexing with numpy array
bool_array = np.array([True, False, True])
numpy_filtered_df = df[bool_array]

# Case 12: Series extraction from numpy array filtered DataFrame
numpy_filtered_s = df[bool_array]["points"]

# Case 13: Combined conditions with OR operator
or_filtered_s = df[(df["points"] > 110) | (df["total"] > 350)]["category"]

# Case 14: Double boolean filtering and then column selection
double_filtered_s = df[df["points"] > 100][df["total"] > 350]["category"]

# Case 15: More complex nested subscription with multiple boolean operations
nested_complex_s = df[(df["points"] > 100) & ~(df["total"] < 350) | (df["category"] == "C")]["points"]

# Case 16: Direct boolean condition on the DataFrame
direct_bool_df = df[df > 110]  # Returns DataFrame with values satisfying condition

# FINAL:  bool_array -> BoolArray; col_name -> String; complex_filtered_df -> DataFrame; data -> Dict; df -> DataFrame; df1 -> DataFrame; direct_bool_df -> DataFrame; double_filtered_s -> Series; filtered_df -> Top; filtered_s -> Top; mask -> Top; nested_complex_s -> Series; numpy_filtered_df -> DataFrame; numpy_filtered_s -> Series; or_filtered_s -> Series; s1 -> Series; s2 -> Series; s3 -> Series; s4 -> Series; s5 -> Series; s6 -> Scalar