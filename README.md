# Automated Analysis - Overview
`autolysis.py` is a Python script designed to perform automated analysis, visualization, and narration of insights derived from a dataset. The script utilizes a large language model (LLM) to generate a structured analysis based on the dataset's contents, including summary statistics, correlation analysis, and visualizations.

By running the command `uv run autolysis.py dataset.csv` in the terminal, the script performs the following steps:

<b>Data Loading:</b> It reads the provided dataset.

<b>Data Cleaning:</b> The dataset is cleaned by converting non-numeric values to NaN where appropriate.

<b>Basic Analysis:</b> It generates summary statistics, including the mean, median, and standard deviation, for all numeric columns.

<b>Correlation Analysis:</b> It computes and visualizes the correlation between numeric columns in the dataset.

<b>Visualization:</b> It creates visual representations of the correlation matrix and missing data.

<b>Narrative Generation:</b> The script generates a written analysis of the dataset, which includes key insights, correlations, and missing data summaries.

# Output Files
Upon successful execution of the script, the following files will be generated in the current directory:

<b>README.md:</b> This file will contain the automated analysis results, structured as a comprehensive story.

<b>correlation_matrix.png:</b> This file will contain a heatmap visualization of the correlation matrix, showing relationships between numeric columns in the dataset.

<b>missing_data.png:</b> This file will display a bar chart indicating the proportion of missing data for each column in the dataset.

Note: Replace dataset.csv with the name of your CSV file.
 
 
