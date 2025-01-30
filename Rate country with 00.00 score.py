#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 08:43:03 2025

@author: patrickotoole
"""

import os
import json
import sys

# Define Fitch credit rating hierarchy
fitch_ratings = {
    "CCC": 1,  # Default
    "CCC+": 2,  # High risk of default
    "B-": 3,
    "B": 4,
    "B+": 5,
    "BB-": 6,
    "BB": 7,  # Lower medium grade
    "BB+": 8,  # Upper medium grade
    "BBB-": 9,  # High grade
    "BBB": 10,  # Prime
    "BBB+": 11,
    "A-": 12,
    "A": 13,
    "A+": 14,
    "AA": 15,
    "AA+": 16,
    "AAA": 17
}

# Reverse mapping: from numerical values to Fitch ratings
fitch_ratings_reverse = {value: key for key, value in fitch_ratings.items()}

def load_json(file_path):
    """Load JSON data from a file."""
    with open(file_path, 'r') as file:
        return json.load(file)

# function to check the population in a file. This is a integer type
def check_population(data):
    """Check and return the population."""
    if "People and Society" in data and "Population" in data["People and Society"]:
        population_data = data["People and Society"]["Population"]
        if "total" in population_data and "text" in population_data["total"]:
            population_str = population_data["total"]["text"].replace(",", "")
            try:
                return int(population_str)
            except ValueError:
                return None
    return None

# function to check the real GDP growth rate in 2023 in the file. the value is a float with a % and it has (Year number est.)
def check_real_GDP_growth_2023(data):
    """Check and return the Real GDP growth percentage as a float."""
    if "Economy" in data and "Real GDP growth rate" in data["Economy"]:
        gdp_2023_data = data["Economy"]["Real GDP growth rate"]
        if "Real GDP growth rate 2023" in gdp_2023_data and "text" in gdp_2023_data["Real GDP growth rate 2023"]:
            gdp_2023_str = gdp_2023_data["Real GDP growth rate 2023"]["text"].replace(",", "").split('%')[0].strip()
            try:
                return float(gdp_2023_str)  # Keep as float to preserve decimals
            except ValueError:
                return None
    return None
# function to check the real GDP growth rate in 2022 in the file. the value is a float with a % and it has (Year number est.)

def check_real_GDP_growth_2022(data):
    """Check and return the Real GDP growth percentage as a float."""
    if "Economy" in data and "Real GDP growth rate" in data["Economy"]:
        gdp_2022_data = data["Economy"]["Real GDP growth rate"]
        if "Real GDP growth rate 2022" in gdp_2022_data and "text" in gdp_2022_data["Real GDP growth rate 2022"]:
            gdp_2022_str = gdp_2022_data["Real GDP growth rate 2022"]["text"].replace(",", "").split('%')[0].strip()
            try:
                return float(gdp_2022_str)  # Keep as float to preserve decimals
            except ValueError:
                return None
    return None

# this function is to check the fitch credit rating found in a file. the credit rating is a string with (year)
def check_credit_rating_fitch(data):
    """Check and return the Fitch Credit Rating."""
    if "Economy" in data and "Credit ratings" in data["Economy"]:
        fitch_rating_data = data["Economy"]["Credit ratings"].get("Fitch rating", {}).get("text", "")
        fitch_rating = fitch_rating_data.split(" ")[0].strip()
        return fitch_ratings.get(fitch_rating.upper(), 0)
    return 0

#this function is to check the natural resources found in the files. the values are strings in a list
def check_natural_resources(data):
    """
    Extract natural resources from the Geography -> Natural resources -> text field.
    Split the text into a list of resources.
    """
    try:
        resources_text = data.get("Geography", {}).get("Natural resources", {}).get("text", "")
        # Split resources by commas and clean up whitespace
        return [resource.strip().lower() for resource in resources_text.split(",") if resource.strip()]
    except (AttributeError, KeyError):
        return []




if __name__ == "__main__":
    folder_path = "CIA Factbook"  # Path to your JSON data folder

    # Ask the user to rank the variables (1 to 5)
    variables = ["population", "real GDP growth 2023", "real GDP growth 2022", "Fitch credit rating", "natural resources"]
    print("Rank the importance of the following variables (1 = most important, 5 = least important):")
    rankings = {}
    for variable in variables:
        while True:
            try:
                rank = int(input(f"Rank for {variable}: "))
                if 1 <= rank <= 5 and rank not in rankings.values():
                    rankings[variable] = rank
                    break
                else:
                    print("Invalid rank or rank already assigned. Please enter a unique rank between 1 and 5.")
            except ValueError:
                print("Invalid input. Please enter a number between 1 and 5.")

    # Convert rankings to weights (higher rank = higher weight)
    weights = {var: 6 - rank for var, rank in rankings.items()}

    # Ask for thresholds
    thresholds = {}
    for variable in variables:
        if variable == "population":
            thresholds[variable] = int(input(f"Enter the desired threshold for {variable} (e.g., 1000000): "))
        elif "GDP" in variable:
            thresholds[variable] = float(input(f"Enter the desired threshold for {variable} (e.g., 3.5): "))
        elif variable == "Fitch credit rating":
            thresholds[variable] = input(f"Enter the desired threshold for {variable} (e.g., 'A'): ").strip().upper()
            if thresholds[variable] not in fitch_ratings:
                print("Invalid credit rating. Defaulting to 'CCC'.")
                thresholds[variable] = "CCC"
        elif variable == "natural resources":
            thresholds[variable] = {res.strip().lower() for res in input(f"Enter desired {variable} (comma-separated): ").split(",")}

    # Predefine max thresholds for normalization (you can adjust these based on your dataset)
max_thresholds = {
    "population": 1409128296,  # Example: max population expected
    "real GDP growth 2023": 5,  # Example: max GDP growth rate in %
    "real GDP growth 2022": 5,  # Example: max GDP growth rate in %
    "Fitch credit rating": 17,  # Fitch scale: 1 to 17
    "natural resources": 50  # Example: max number of resources matched
}

# Calculate the maximum possible score
max_total_score = sum(weights.values())  # Sum of all weights

# Initialize scores dictionary
country_scores = {}

country_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]


for file_name in country_files:
    file_path = os.path.join(folder_path, file_name)
    data = load_json(file_path)

    country_name = file_name.replace(".json", "")  # Assume file name is the country name

    # Calculate normalized score
    score = 0

    # Population
    population = check_population(data)
    if population and population > thresholds["population"]:
        normalized_population = min(population / max_thresholds["population"], 1)  # Cap at 1
        score += weights["population"] * normalized_population

    # GDP Growth 2023
    real_2023_GDP = check_real_GDP_growth_2023(data)
    if real_2023_GDP and real_2023_GDP > thresholds["real GDP growth 2023"]:
        normalized_gdp_2023 = min(real_2023_GDP / max_thresholds["real GDP growth 2023"], 1)  # Cap at 1
        score += weights["real GDP growth 2023"] * normalized_gdp_2023

    # GDP Growth 2022
    real_2022_GDP = check_real_GDP_growth_2022(data)
    if real_2022_GDP and real_2022_GDP > thresholds["real GDP growth 2022"]:
        normalized_gdp_2022 = min(real_2022_GDP / max_thresholds["real GDP growth 2022"], 1)  # Cap at 1
        score += weights["real GDP growth 2022"] * normalized_gdp_2022

    # Fitch Credit Rating
    credit_rating_rank = check_credit_rating_fitch(data)
    if credit_rating_rank > fitch_ratings[thresholds["Fitch credit rating"]]:
        normalized_credit_rating = min(credit_rating_rank / max_thresholds["Fitch credit rating"], 1)  # Cap at 1
        score += weights["Fitch credit rating"] * normalized_credit_rating

    # Natural Resources
    country_resources = check_natural_resources(data)
    matches = thresholds["natural resources"] & set(country_resources)
    if matches:
        normalized_resources = min(len(matches) / max_thresholds["natural resources"], 1)  # Cap at 1
        score += weights["natural resources"] * normalized_resources

    # Normalize the score to be out of 100
    final_score = (score / max_total_score) * 100

    # Add score to the country
    country_scores[country_name] = final_score

# Sort countries by scores
sorted_countries = sorted(country_scores.items(), key=lambda x: x[1], reverse=True)

# Display results
print("\nCountries ranked by score:")
for rank, (country, score) in enumerate(sorted_countries, 1):
    print(f"{rank}. {country}: Score = {score:.2f}")