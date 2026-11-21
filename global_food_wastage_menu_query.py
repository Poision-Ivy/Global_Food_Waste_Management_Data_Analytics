"""
GLOBAL FOOD WASTAGE DATASET - MENU-DRIVEN CSV QUERY PROGRAM
Imports used: NumPy and Pandas only.
"""

import numpy as np
import pandas as pd
df = pd.read_csv("global_food_wastage_cleaned.csv")
def display_rows(rows):
    if len(rows) == 0:
        print("\nNo matching records found.")
    else:
        result = pd.DataFrame(rows, columns=df.columns)
        print("\nMatching dataset:")
        print(result.to_string(index=False))
        print("\nTotal records found:", len(result))
while True:
    print("\n==========================================")
    print("       GLOBAL FOOD WASTAGE DATA")
    print("==========================================")
    print("1. Display complete dataset")
    print("2. Search data by country")
    print("3. Search data by food category")
    print("4. Search data by year")
    print("5. Search by country and year")
    print("6. Find records above a waste amount")
    print("7. Exit")
    print("==========================================")

    choice = input("Enter your choice (1-7): ")

    if choice == "1":
        print("\nComplete Global Food Wastage Dataset:")
        print(df.to_string(index=False))
        print("\nTotal records:", len(df))

    elif choice == "2":
        country_name = input("Enter country name: ").strip()
        matched_rows = []

        for index, row in df.iterrows():
            if str(row["Country"]).strip().lower() == country_name.lower():
                matched_rows.append(row)

        display_rows(matched_rows)

    elif choice == "3":
        category_name = input("Enter food category: ").strip()
        matched_rows = []

        for index, row in df.iterrows():
            if str(row["Food Category"]).strip().lower() == category_name.lower():
                matched_rows.append(row)

        display_rows(matched_rows)

    elif choice == "4":
        year_input = input("Enter year (example: 2021): ").strip()
        matched_rows = []

        for index, row in df.iterrows():
            if str(int(row["Year"])) == year_input:
                matched_rows.append(row)

        display_rows(matched_rows)

    elif choice == "5":
        country_name = input("Enter country name: ").strip()
        year_input = input("Enter year: ").strip()
        matched_rows = []

        for index, row in df.iterrows():
            if str(row["Country"]).strip().lower() == country_name.lower():
                if str(int(row["Year"])) == year_input:
                    matched_rows.append(row)

        display_rows(matched_rows)

    elif choice == "6":
        amount_input = input("Enter minimum food waste in tons: ").strip()

        if amount_input.replace(".", "", 1).isdigit():
            minimum_waste = float(amount_input)
            matched_rows = []

            for index, row in df.iterrows():
                if row["Total Waste (Tons)"] > minimum_waste:
                    matched_rows.append(row)

            display_rows(matched_rows)
        else:
            print("Please enter a valid positive number.")

    elif choice == "7":
        print("Thank you for using the Global Food Wastage Data program.")
        break

    else:
        print("Invalid choice. Please select a number from 1 to 7.")
