#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 11 14:25:08 2025

@author: patrickotoole
"""

# The purpose of this file is to try and return the countries that are above my entered thresholds and their values

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

    # Population threshold
    try:
        population_threshold = int(input("Enter the population threshold: "))
    except ValueError:
        print("Invalid population threshold.")
        sys.exit()

    # Real GDP 2023 growth threshold
    try:
        real_GDP_growth_2023_threshold = float(input("Enter the 2023 real GDP growth rate threshold: "))
    except ValueError:
        print("Invalid 2023 GDP threshold.")
        sys.exit()
        
        # Real GDP 2022 growth threshold

    try:
        real_GDP_growth_2022_threshold = float(input("Enter the 2022 real GDP growth rate threshold: "))
    except ValueError:
        print("Invalid 2022 GDP threshold.")
        sys.exit()

    # Fitch credit rating threshold
    credit_rating_threshold = input("Enter the Fitch credit rating threshold (e.g., 'A'): ").strip().upper()
    if credit_rating_threshold not in fitch_ratings:
        print("Invalid credit rating threshold.")
        sys.exit()
    credit_rating_threshold_rank = fitch_ratings[credit_rating_threshold]
    
    #natural resources threshold
    enter_natural_resources = input("Enter the natural resources you are looking for (comma-separated): ")
    desired_resources = {resource.strip().lower() for resource in enter_natural_resources.split(",")}
    

    # Process each JSON file
    countries_over_population_threshold = []
    countries_over_real_GDP_growth_2023_threshold = []
    countries_over_credit_rating_threshold = []
    countries_over_real_GDP_growth_2022_threshold = []
    countries_with_natural_resources = []

    

    country_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]

    for file_name in country_files:
        file_path = os.path.join(folder_path, file_name)
        data = load_json(file_path)

        country_name = file_name.replace(".json", "")  # Assume file name is the country name
        
#dive deeper into 133 to the end specifically why there are two variables in the portions below
        # Check population
        population = check_population(data)
        if population and population > population_threshold:
            countries_over_population_threshold.append((country_name, population))

        # Check 2023 GDP growth
        real_2023_GDP = check_real_GDP_growth_2023(data)
        if real_2023_GDP and real_2023_GDP > real_GDP_growth_2023_threshold:
            countries_over_real_GDP_growth_2023_threshold.append((country_name, real_2023_GDP))
            
        # check 2022 GDP growth
        real_2022_GDP = check_real_GDP_growth_2022(data)
        if real_2022_GDP and real_2022_GDP > real_GDP_growth_2022_threshold:
            countries_over_real_GDP_growth_2022_threshold.append((country_name, real_2022_GDP))

        # Check Fitch credit rating
        credit_rating_rank = check_credit_rating_fitch(data)
        if credit_rating_rank > credit_rating_threshold_rank:
            countries_over_credit_rating_threshold.append((country_name, credit_rating_rank))
            
         # Check for matches between desired resources and the country's resources
        country_resources = check_natural_resources(data)
        matches = desired_resources & set(country_resources)
        if matches:
             countries_with_natural_resources.append((country_name, matches))
            
# Extract country names from the results
population_countries = {country for country, _ in countries_over_population_threshold}
gdp_2023_countries = {country for country, _ in countries_over_real_GDP_growth_2023_threshold}
gdp_2022_countries = {country for country, _ in countries_over_real_GDP_growth_2022_threshold}
credit_rating_countries = {country for country, _ in countries_over_credit_rating_threshold}
countries_natural_resources = {country for country, _ in countries_with_natural_resources}

# Find common countries across all criteria
common_countries = population_countries & gdp_2023_countries & gdp_2022_countries & credit_rating_countries & countries_natural_resources

# Print final results with field values
if common_countries:
    print(f"\nCountries meeting all criteria (Population > {population_threshold}, "
          f"2023 GDP growth > {real_GDP_growth_2023_threshold}%, 2022 GDP growth > {real_GDP_growth_2022_threshold}%, "
          f" Fitch rating > {credit_rating_threshold}"
          f"and Natural Resources > {enter_natural_resources}):")
    for country in common_countries:
        # Extract field values for each country
        population = next(value for name, value in countries_over_population_threshold if name == country)
        real_2023_GDP = next(value for name, value in countries_over_real_GDP_growth_2023_threshold if name == country)
        real_2022_GDP = next(value for name, value in countries_over_real_GDP_growth_2022_threshold if name == country)
        credit_rating_rank = next(value for name, value in countries_over_credit_rating_threshold if name == country)
        country_resources = next(value for name, value in countries_with_natural_resources if name == country)
        print(f"{country}: Population = {population}, 2023 GDP Growth = {real_2023_GDP}%, 2022 GDP Growth = {real_2022_GDP}%, \
              Fitch Credit rating = {credit_rating_rank} Natural Resources = {country_resources}")
else:
    print("\nNo countries meet all the criteria.")
            
  
# if countries_over_population_threshold and countries_over_real_GDP_growth_2023_threshold and countries_over_credit_rating_threshold and countries_over_real_GDP_growth_2022_threshold:
#     # Find common countries across all criteria
#     common_countries = set(countries_over_population_threshold) & \
#                        set(countries_over_real_GDP_growth_2023_threshold) & \
#                        set(countries_over_credit_rating_threshold) & \
#                        set(countries_over_real_GDP_growth_2022_threshold)
#     # field_values = set(population) \
#     #                set(real_2023_GDP) \
#     #                set(real_2022_GDP) \
#     #                set(credit_rating_rank)
                   
                       
#     if common_countries:
#         print(f"\nCountries with population over {population_threshold}, 2023 GDP growth > {real_GDP_growth_2023_threshold}%, "
#               f"2022 GDP growth > {real_GDP_growth_2022_threshold}%, and Fitch credit rating > {credit_rating_threshold}:")
#         for country in common_countries:
#             print(country)
#     else:
#         print("\nNo countries meet all the criteria.")
# else:
#     print("\nNo countries meet all the criteria.")


