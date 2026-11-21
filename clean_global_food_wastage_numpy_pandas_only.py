import numpy as np
import pandas as pd

INPUT_FILE = "global_food_wastage_messy.csv"
OUTPUT_FILE = "global_food_wastage_cleaned.csv"
REPORT_FILE = "cleaning_report.txt"

EXPECTED_COLUMNS = [
    "Country",
    "Year",
    "Food Category",
    "Total Waste (Tons)",
    "Economic Loss (Million $)",
    "Avg Waste per Capita (Kg)",
    "Population (Million)",
    "Household Waste (%)"
]

NUMERIC_COLUMNS = [
    "Year",
    "Total Waste (Tons)",
    "Economic Loss (Million $)",
    "Avg Waste per Capita (Kg)",
    "Population (Million)",
    "Household Waste (%)"
]

NON_NEGATIVE_COLUMNS = [
    "Total Waste (Tons)",
    "Economic Loss (Million $)",
    "Avg Waste per Capita (Kg)",
    "Population (Million)"
]


def clean_text(series):
    return (
        series.astype("string")
        .str.strip()
        .str.replace(r"[_-]+", " ", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
        .replace({"": pd.NA, "Nan": pd.NA, "None": pd.NA})
    )


def detect_outliers_iqr(series):
    values = pd.to_numeric(series, errors="coerce")
    valid = values.dropna()

    if len(valid) < 4 or valid.nunique() < 2:
        return 0, np.nan, np.nan

    q1 = valid.quantile(0.25)
    q3 = valid.quantile(0.75)
    iqr = q3 - q1

    if iqr == 0:
        return 0, np.nan, np.nan

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    count = int(((valid < lower) | (valid > upper)).sum())

    return count, lower, upper


def clean_dataset():
    try:
        df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print("\nERROR: Input file was not found.")
        print("Place '" + INPUT_FILE + "' in the same folder as this Python file.")
        return None

    rows_before = len(df)
    columns_before = len(df.columns)
    report = []

    #Standardize and validate column names.
    df.columns = [str(column).strip() for column in df.columns]

    missing_columns = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing_columns:
        print("\nERROR: Required columns are missing:")
        for col in missing_columns:
            print(" -", col)
        return None

    # Only the required columns and in Consistent Order
    df = df[EXPECTED_COLUMNS].copy()

    # Clean text columns.
    for column in ["Country", "Food Category"]:
        df[column] = clean_text(df[column])

    # Convert numeric columns.
    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Replacing impossible negative measurements with missing values.
    negative_counts = {}
    for column in NON_NEGATIVE_COLUMNS:
        invalid = df[column] < 0
        negative_counts[column] = int(invalid.sum())
        df.loc[invalid, column] = np.nan

    # Validating percentage values.
    invalid_percent = ~df["Household Waste (%)"].between(0, 100)
    invalid_percent_count = int(invalid_percent.sum())
    df.loc[invalid_percent, "Household Waste (%)"] = np.nan

    # Validating years.
    invalid_year = ~df["Year"].between(2000, 2100)
    invalid_year_count = int(invalid_year.sum())
    df.loc[invalid_year, "Year"] = np.nan

    # Remove exact duplicate records only.
    duplicate_count = int(df.duplicated().sum())
    df = df.drop_duplicates(keep="first").copy()

    # Missing text values with "Unknown".
    text_missing_counts = {}
    for column in ["Country", "Food Category"]:
        text_missing_counts[column] = int(df[column].isna().sum())
        df[column] = df[column].fillna("Unknown")

    # Detect possible outliers, but do not automatically change them.
    outlier_columns = [
        "Total Waste (Tons)",
        "Economic Loss (Million $)",
        "Avg Waste per Capita (Kg)",
        "Population (Million)"
    ]

    outlier_results = {}
    for column in outlier_columns:
        outlier_results[column] = detect_outliers_iqr(df[column])

    # Fill remaining numeric missing values with the median.
    numeric_missing_counts = {}
    for column in NUMERIC_COLUMNS:
        numeric_missing_counts[column] = int(df[column].isna().sum())
        median_value = df[column].median()

        if pd.isna(median_value):
            # No valid value exists in this column.
            median_value = 0

        df[column] = df[column].fillna(median_value)

    df["Year"] = df["Year"].round().astype("int64")

    # Sorting records for easier reading.
    df = df.sort_values(
        ["Country", "Year", "Food Category"],
        kind="stable"
    ).reset_index(drop=True)

    # Saving the cleaned dataset.
    df.to_csv(OUTPUT_FILE, index=False)

    report.append("GLOBAL FOOD WASTAGE - DATA CLEANING REPORT")
    report.append("=" * 58)
    report.append("")
    report.append("DATASET OVERVIEW")
    report.append("-" * 58)
    report.append("Rows before cleaning       : " + str(rows_before))
    report.append("Columns before cleaning    : " + str(columns_before))
    report.append("Rows after cleaning        : " + str(len(df)))
    report.append("Exact duplicate rows removed: " + str(duplicate_count))
    report.append("Rows removed overall       : " + str(rows_before - len(df)))
    report.append("")

    report.append("DATA VALIDATION")
    report.append("-" * 58)
    for column, count in negative_counts.items():
        report.append("Negative values in " + column + ": " + str(count))
    report.append("Invalid household percentages: " + str(invalid_percent_count))
    report.append("Invalid year values           : " + str(invalid_year_count))
    report.append("")

    report.append("MISSING VALUE HANDLING")
    report.append("-" * 58)
    for column, count in text_missing_counts.items():
        report.append(column + " values filled as 'Unknown': " + str(count))
    for column, count in numeric_missing_counts.items():
        report.append(column + " values filled with median: " + str(count))
    report.append("")

    report.append("POSSIBLE OUTLIERS (IQR METHOD)")
    report.append("-" * 58)
    report.append("Outliers are reported for review; original values are retained.")
    for column, result in outlier_results.items():
        count, lower, upper = result
        if np.isnan(lower):
            report.append(column + ": Not enough variation/data to calculate IQR limits.")
        else:
            report.append(
                column + ": " + str(count)
                + " possible outlier(s); expected range approximately "
                + str(round(lower, 2)) + " to " + str(round(upper, 2))
            )
    report.append("")
    report.append("OUTPUT")
    report.append("-" * 58)
    report.append("Cleaned CSV : " + OUTPUT_FILE)
    report.append("This report: " + REPORT_FILE)

    report_text = "\n".join(report)

    with open(REPORT_FILE, "w", encoding="utf-8") as report_file:
        report_file.write(report_text)

    print("\n" + "=" * 58)
    print("       GLOBAL FOOD WASTAGE - DATA CLEANING")
    print("=" * 58)
    print("Status                  : COMPLETED")
    print("Rows before cleaning    :", rows_before)
    print("Rows after cleaning     :", len(df))
    print("Duplicate rows removed :", duplicate_count)
    print("Invalid years           :", invalid_year_count)
    print("Invalid percentages     :", invalid_percent_count)
    print("-" * 58)
    print("POSSIBLE OUTLIERS (not modified)")
    for column, result in outlier_results.items():
        print(" -", column + ":", result[0], "possible outlier(s)")
    print("-" * 58)
    print("FILES CREATED")
    print("  1.", OUTPUT_FILE)
    print("  2.", REPORT_FILE)
    print("=" * 58)
    print("\nCLEANED DATA PREVIEW")
    print(df.head(10).to_string(index=False))
    print("\nCleaning completed successfully.")

    return df


if __name__ == "__main__":
    cleaned_data = clean_dataset()
