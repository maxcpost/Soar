#!/usr/bin/env python
import os
import pandas as pd
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("data_processor")

def create_cork_folder():
    """
    Create the cork folder in the database directory if it doesn't exist.
    Uses Path for cross-platform compatibility.
    
    Returns:
        str: The path to the cork folder
    """
    cork_path = Path("database") / "cork"
    if not cork_path.exists():
        try:
            cork_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {cork_path}")
        except Exception as e:
            logger.error(f"Failed to create directory {cork_path}: {e}")
            raise
    else:
        logger.info(f"Directory already exists: {cork_path}")
    
    return str(cork_path)

def get_stock_number():
    """
    Ask user for the stock number to process.
    
    Returns:
        str: The selected stock number
    """
    try:
        master_csv_path = Path("database") / "master.csv"
        
        if not master_csv_path.exists():
            logger.error(f"Master CSV file not found at {master_csv_path}")
            raise FileNotFoundError(f"Master CSV file not found at {master_csv_path}")
        
        master_df = pd.read_csv(master_csv_path)
        
        if 'StockNumber' not in master_df.columns:
            logger.error("StockNumber column not found in master CSV")
            raise KeyError("StockNumber column not found in master CSV")
        
        available_stocks = master_df['StockNumber'].tolist()
        
        if not available_stocks:
            logger.error("No stock numbers found in master CSV")
            raise ValueError("No stock numbers found in master CSV")
        
        print("\nAvailable Stock Numbers:")
        for i, stock in enumerate(available_stocks):
            print(f"{i+1}. {stock}")
        
        while True:
            try:
                choice = input("\nPlease select a stock number (enter the number or the actual stock ID): ")
                
                # Handle input as index
                if choice.isdigit() and 1 <= int(choice) <= len(available_stocks):
                    selected_stock = available_stocks[int(choice) - 1]
                    break
                # Handle input as actual stock ID
                elif choice in available_stocks:
                    selected_stock = choice
                    break
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a valid number or stock ID.")
        
        logger.info(f"Selected stock number: {selected_stock}")
        return selected_stock
        
    except Exception as e:
        logger.error(f"Error selecting stock number: {e}")
        raise

def validate_data(df, required_columns, csv_name):
    """
    Validate that a DataFrame contains the required columns.
    
    Args:
        df (pandas.DataFrame): The DataFrame to validate
        required_columns (list): List of required column names
        csv_name (str): Name of the CSV for error messages
        
    Returns:
        bool: True if validation passes
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        logger.warning(f"Missing columns in {csv_name}: {missing_columns}")
        print(f"Warning: The following columns are missing in {csv_name}: {missing_columns}")
        print("Processing will continue with available columns.")
    
    return len(missing_columns) < len(required_columns)  # At least one column should be present

def process_master_csv(stock_number, cork_path):
    """
    Process the master.csv file to create separate CSVs for each agent.
    
    Args:
        stock_number (str): The stock number to process
        cork_path (str): Path to the cork folder
        
    Returns:
        dict: Inputs for the crew or None if processing fails
    """
    try:
        # Read the master CSV
        master_csv_path = Path("database") / "master.csv"
        logger.info(f"Reading master CSV from {master_csv_path}")
        master_df = pd.read_csv(master_csv_path)
        
        # Filter for the specific stock number
        stock_data = master_df[master_df['StockNumber'] == stock_number]
        
        if stock_data.empty:
            logger.error(f"No data found for stock number {stock_number}")
            return None
        
        # Create property.csv
        property_cols = ['Property Address', 'City', 'State', 'Zip']
        if validate_data(stock_data, property_cols, "property.csv"):
            existing_property_cols = [col for col in property_cols if col in stock_data.columns]
            property_df = stock_data[existing_property_cols]
            property_path = Path(cork_path) / "property.csv"
            property_df.to_csv(property_path, index=False)
            logger.info(f"Created property.csv with columns: {existing_property_cols}")
        
        # Create environmental.csv
        environmental_cols = ['In SFHA', 'Fema Flood Zone', 'FEMA Map Date', 'Floodplain Area']
        if validate_data(stock_data, environmental_cols, "enviornmental.csv"):
            existing_environmental_cols = [col for col in environmental_cols if col in stock_data.columns]
            environmental_df = stock_data[existing_environmental_cols]
            environmental_path = Path(cork_path) / "enviornmental.csv"
            environmental_df.to_csv(environmental_path, index=False)
            logger.info(f"Created enviornmental.csv with columns: {existing_environmental_cols}")
        
        # Create growthTrends.csv
        growth_cols = ['% Pop Grwth 2020-2024(5m)', '% Pop Grwth 2024-2029(5m)', 
                      '% Pop Grwth 2020-2024(10m)', '% Pop Grwth 2024-2029(10m)', 
                      '% HU Grwth 2020-2024(5m)', '% HU Grwth 2020-2024(10m)']
        if validate_data(stock_data, growth_cols, "growthTrends.csv"):
            existing_growth_cols = [col for col in growth_cols if col in stock_data.columns]
            growth_df = stock_data[existing_growth_cols]
            growth_path = Path(cork_path) / "growthTrends.csv"
            growth_df.to_csv(growth_path, index=False)
            logger.info(f"Created growthTrends.csv with columns: {existing_growth_cols}")
        
        # Create housingUnitsAndOccupancy.csv
        housing_cols = ['TotHUs_5', 'OccHUs_5', 'OwnerOcc_5', 'RenterOcc_5', 
                      'AvgOwnerHHSize_5', 'AvgRenterHHSize_5', 'VacHUs_5', 
                      'VacantForSale_5', 'VacantForRent_5', 'VacantSeasonal_5', 
                      'MobileHomes_5', 'MobileHomesPerK_5', 'TotHUs_10', 'OccHUs_10', 
                      'OwnerOcc_10', 'RenterOcc_10', 'AvgOwnerHHSize_10', 
                      'AvgRenterHHSize_10', 'VacHUs_10', 'VacantForSale_10', 
                      'VacantForRent_10', 'VacantSeasonal_10', 'MobileHomes_10', 
                      'MobileHomesPerK_10']
        if validate_data(stock_data, housing_cols, "housingUnitsAndOccupancy.csv"):
            existing_housing_cols = [col for col in housing_cols if col in stock_data.columns]
            housing_df = stock_data[existing_housing_cols]
            housing_path = Path(cork_path) / "housingUnitsAndOccupancy.csv"
            housing_df.to_csv(housing_path, index=False)
            logger.info(f"Created housingUnitsAndOccupancy.csv with columns: {existing_housing_cols}")
        
        # Create demographics.csv - includes both Demographics and Affordability data points
        demographics_cols = ['TotPop_5', 'Age0_4_5', 'Age5_9_5', 'Age10_14_5', 
                           'Age15_19_5', 'Age20_24_5', 'Age25_34_5', 'Age35_44_5', 
                           'Age45_54_5', 'Age55_59_5', 'Age60_64_5', 'Age65_74_5', 
                           'Age75_84_5', 'Over85_5', 'TotHHs_5', 'MedianHHInc_5', 
                           'AvgHHInc_5', 'InKindergarten_5', 'InElementary_5', 
                           'InHighSchool_5', 'InCollege_5', 'Disabled_5', 
                           'DisabledUnder18_5', 'NonInst18_64_5', 'Disabled18_64_5', 
                           'NonInstOver65_5', 'DisabledElder_5', 'TotPop_10', 
                           'Age0_4_10', 'Age5_9_10', 'Age10_14_10', 'Age15_19_10', 
                           'Age20_24_10', 'Age25_34_10', 'Age35_44_10', 'Age45_54_10', 
                           'Age55_59_10', 'Age60_64_10', 'Age65_74_10', 'Age75_84_10', 
                           'Over85_10', 'TotHHs_10', 'MedianHHInc_10', 'AvgHHInc_10', 
                           'InKindergarten_10', 'InElementary_10', 'InHighSchool_10', 
                           'InCollege_10', 'Disabled_10', 'DisabledUnder18_10', 
                           'NonInst18_64_10', 'Disabled18_64_10', 'NonInstOver65_10', 
                           'DisabledElder_10', 'HvalUnder50_5', 'Hval50_5', 'Hval100_5', 
                           'Hval150_5', 'Hval200_5', 'Hval300_5', 'Hval500_5', 
                           'HvalOverMillion_5', 'HvalOver2Million_5', 'MedianHValue_5', 
                           'MedianGrossRent_5', 'AvgGrossRent_5', 'HvalUnder50_10', 
                           'Hval50_10', 'Hval100_10', 'Hval150_10', 'Hval200_10', 
                           'Hval300_10', 'Hval500_10', 'HvalOverMillion_10', 
                           'HvalOver2Million_10', 'MedianHValue_10', 'MedianGrossRent_10', 
                           'AvgGrossRent_10']
        
        if validate_data(stock_data, demographics_cols, "demographics.csv"):
            # Filter for columns that actually exist in the dataframe
            existing_demographics_cols = [col for col in demographics_cols if col in stock_data.columns]
            
            demographics_df = stock_data[existing_demographics_cols]
            demographics_path = Path(cork_path) / "demographics.csv" 
            demographics_df.to_csv(demographics_path, index=False)
            logger.info(f"Created demographics.csv with {len(existing_demographics_cols)} columns")
        
        # Return the city and state for later use
        city = stock_data['City'].iloc[0] if 'City' in stock_data.columns else 'Unknown'
        state = stock_data['State'].iloc[0] if 'State' in stock_data.columns else 'Unknown'
        property_address = stock_data['Property Address'].iloc[0] if 'Property Address' in stock_data.columns else 'Unknown'
        
        return {
            'City': city,
            'State': state,
            'Property Address': property_address,
            'listing_id': stock_number,
            'property_csv_path': str(Path("database") / "cork" / "property.csv"),
            'environmental_csv_path': str(Path("database") / "cork" / "enviornmental.csv"),
            'growth_trends_csv_path': str(Path("database") / "cork" / "growthTrends.csv"),
            'occupancy_csv_path': str(Path("database") / "cork" / "housingUnitsAndOccupancy.csv"),
            'demographics_csv_path': str(Path("database") / "cork" / "demographics.csv")
        }
    
    except Exception as e:
        logger.error(f"Error processing master CSV: {e}")
        return None

def main():
    """
    Main function to run the data processing script.
    """
    try:
        logger.info("Starting land listing evaluation data processor...")
        
        # Create cork folder
        cork_path = create_cork_folder()
        
        # Get stock number from user
        stock_number = get_stock_number()
        
        # Process master CSV
        result = process_master_csv(stock_number, cork_path)
        
        if result:
            logger.info("Data processing complete!")
            print("\nData processing complete! Here are your inputs for the crew:")
            for key, value in result.items():
                print(f"{key}: {value}")
            return result
        else:
            logger.error("Data processing failed.")
            print("Data processing failed. See log for details.")
            return None
            
    except Exception as e:
        logger.error(f"Error in main processing: {e}")
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    main() 