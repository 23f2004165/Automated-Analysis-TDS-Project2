# /// script
# requires-python = ">=3.8"  # Declare the required Python version
# dependencies = [
#   "numpy",
#   "pandas",
#   "matplotlib",
#   "requests",
#   "seaborn",
#   "logging",
#   "openai",
# ]  # List all necessary dependencies
# ///
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import openai
import numpy as np
import sys
import json
import requests
from dotenv import load_dotenv
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables from the .env file
load_dotenv()

AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")
if not AIPROXY_TOKEN:
    logging.error("AIPROXY_TOKEN not set.")
    sys.exit(1)

# Initialize OpenAI client with the provided API key
openai.api_key = AIPROXY_TOKEN

# Function to read the CSV file with error handling for encoding issues
def read_csv(file_path, encoding='ISO-8859-1'):
    try:
        logging.info(f"Reading file {file_path} with encoding {encoding}.")
        df = pd.read_csv(file_path, encoding=encoding)
        logging.info(f"File {file_path} successfully loaded.")
        return df
    except Exception as e:
        logging.error(f"Error reading {file_path}: {e}")
        sys.exit(1)

# Function to clean data by converting non-numeric columns to NaN where conversion fails
def clean_data(df):
    try:
        logging.info("Cleaning data by converting non-numeric columns to NaN.")
        df_cleaned = df.apply(pd.to_numeric, errors='coerce')
        logging.info("Data cleaning completed.")
        return df_cleaned
    except Exception as e:
        logging.error(f"Error during data cleaning: {e}")
        sys.exit(1)

# Function to get basic stats and check for missing data
def basic_analysis(df):
    try:
        logging.info("Performing basic analysis on dataset.")
        summary = {
            "columns": list(df.columns),
            "types": df.dtypes.astype(str).to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "num_rows": len(df),
            "example_values": df.head(3).to_dict(orient="records"),
            "correlation": df.corr().to_dict() if df.select_dtypes(include="number").shape[1] > 1 else None,
        }
        logging.info("Basic analysis completed.")
        return summary
    except Exception as e:
        logging.error(f"Error during basic analysis: {e}")
        sys.exit(1)

# Function to detect correlations and outliers (excluding non-numeric columns)
def correlation_analysis(df):
    try:
        logging.info("Performing correlation analysis on numeric columns.")
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.shape[1] > 1:
            corr_matrix = numeric_df.corr()
            logging.info("Correlation analysis completed.")
            return corr_matrix
        else:
            logging.warning("No numeric columns available for correlation.")
            return None
    except Exception as e:
        logging.error(f"Error during correlation analysis: {e}")
        sys.exit(1)

# Function to visualize the correlation matrix
def plot_correlation_matrix(corr_matrix, filename="correlation_matrix.png"):
    try:
        if corr_matrix is not None:
            logging.info("Plotting correlation matrix.")
            plt.figure(figsize=(10, 8))
            sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt='.2f', linewidths=0.5)
            plt.title("Correlation Matrix")
            plt.tight_layout()
            plt.savefig(filename)
            plt.close()
            logging.info(f"Correlation matrix saved to {filename}.")
        else:
            logging.warning("No correlation matrix to plot.")
    except Exception as e:
        logging.error(f"Error while plotting correlation matrix: {e}")

# Function to visualize missing data
def plot_missing_data(df, filename="missing_data.png"):
    try:
        missing_data = df.isnull().mean().sort_values(ascending=False)
        logging.info("Plotting missing data proportions.")
        plt.figure(figsize=(10, 6))
        missing_data.plot(kind='bar', color='orange')
        plt.title('Missing Data Proportions')
        plt.ylabel('Percentage')
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
        logging.info(f"Missing data plot saved to {filename}.")
    except Exception as e:
        logging.error(f"Error while plotting missing data: {e}")

# Function to interact with GPT-4o-Mini via OpenAI API
def analyze_with_gpt(prompt):
    try:
        logging.info("Generating analysis with GPT-4o-Mini.")
        headers = {
            "Authorization": f"Bearer {openai.api_key}",
            "Content-Type": "application/json"
        }
        
        # Define the payload (data)
        data = {
            "model": "gpt-4o-mini",  # Ensure to use the correct model
            "messages": [{"role": "user", "content": prompt}]
        }
        
        # Make the POST request to the OpenAI API
        response = requests.post(
            "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions",  # The correct endpoint
            headers=headers,
            data=json.dumps(data)
        )
        
        # Check if the response is successful
        if response.status_code == 200:
            response_data = response.json()
            return response_data['choices'][0]['message']['content'].strip()
        else:
            logging.error(f"Error with GPT-4o-Mini API: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logging.error(f"Error with the GPT-4o-Mini request: {e}")
        return None

# Function to generate the narrative story
def generate_narrative(df, missing_values, corr_matrix):
    try:
        # Identify columns with missing data
        missing_columns = [col for col, val in missing_values.items() if val > 0]
        prompt = f"""
        I have a dataset with the following columns:
        {', '.join(df.columns)}

        The following columns have missing data:
        {', '.join(missing_columns)}

        Here's a basic overview of the dataset:
        - Summary statistics (mean, median, etc.): {df.describe().to_string(index=False)}
        - Correlation matrix between numerical variables: {corr_matrix.to_string()}

        Based on this information, please write a structured analysis with the following sections:
        1. **Brief Description of the Data**: Provide an overview of the dataset, mentioning key columns and types.
        2. **The Analysis You Carried Out**: Describe the types of analysis you performed (summary statistics, missing data, correlations, etc.).
        3. **Insights Discovered**: Highlight any significant findings from the analysis. For example, trends in publication years, correlation between rating count and average rating, etc.
        4. **Key Findings**: Provide any interesting trends or outliers that you observed in the data.
        5. **Implications of the Findings**: Discuss what the findings mean and what actions could be taken based on these insights. For example, recommendations about pricing, targeting specific genres, or improving missing data.
        """
        narrative = analyze_with_gpt(prompt)
        logging.info("Narrative generation completed.")
        return narrative
    except Exception as e:
        logging.error(f"Error during narrative generation: {e}")
        return None

# Function to save the narrative to a README.md file
def save_narrative_to_readme(narrative, charts_filenames):
    try:
        if narrative is None or len(narrative.strip()) == 0:
            logging.error("No valid narrative to write to README.")
            return
        
        with open("README.md", "w") as f:
            f.write("# Automated Data Analysis\n\n")
            f.write(f"## Data Analysis Report\n\n{narrative}\n\n")
            f.write("## Visualizations\n\n")
            for chart in charts_filenames:
                f.write(f"![{chart}]({chart})\n")
        
        logging.info("Narrative and charts saved to README.md.")
    except Exception as e:
        logging.error(f"Error while saving to README.md: {e}")

# Main function to run the analysis
def main(csv_file):
    try:
        # Read the dataset
        df = read_csv(csv_file)

        # Clean the data by converting non-numeric columns to NaN
        df = clean_data(df)

        # Perform basic analysis
        summary = basic_analysis(df)
        
        # Generate correlation matrix and detect outliers
        corr_matrix = correlation_analysis(df)

        # Create visualizations
        plot_correlation_matrix(corr_matrix)
        plot_missing_data(df)

        # Generate the narrative story with GPT-4o-Mini
        narrative = generate_narrative(df, summary["missing_values"], corr_matrix)

        # Save the charts and narrative
        save_narrative_to_readme(narrative, ["correlation_matrix.png", "missing_data.png"])

        logging.info("Analysis complete. Results saved to README.md and charts.")
    except Exception as e:
        logging.error(f"Error in main analysis process: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logging.error("Usage: python autolysis.py <dataset.csv>")
        sys.exit(1)
    else:
        main(sys.argv[1])
