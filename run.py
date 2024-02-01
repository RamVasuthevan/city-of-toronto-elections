import pandas as pd


def clean_contribution_search_results_2022():
    file_path = (
        "raw_data/contribution-search-results/2022/contribution-search-results.xls"
    )

    df = pd.read_excel(file_path, usecols="A:L", skiprows=range(7), engine="xlrd")

    df.columns = (
        df.columns.str.replace("\n", " ", regex=False)
        .str.replace("\s+", " ", regex=True)
        .str.replace(" */ *", "/", regex=True)
        .str.strip()
    )
    return df

def clean_mayor_election_search_results_2022():
    file_path = "raw_data/elections_official_results/2022/2022_Toronto_Poll_By_Poll_Mayor.xlsx"

    # Initialize an empty list to hold DataFrames
    dfs = []

    for sheet_name in pd.ExcelFile(file_path).sheet_names:
        # Read the sheet directly into a DataFrame, skipping the first row
        df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=1, engine="openpyxl")

        # Extract 'Ward Name' from cell A1 of the sheet (after skipping header)
        ward_name = df.columns[0]

        # Drop the first row (which contains the position, e.g., 'Mayor')
        df = df.iloc[1:]

        # Drop the last row (which may contain total values)
        df = df.iloc[:-1]

        df = df.drop(columns='Total')

        # Rename the columns and add 'Ward' and 'Ward Name' columns
        df.columns = ['Candidate'] + list(map(int, df.columns[1:]))
        df['Ward'] = int(sheet_name.split()[-1])
        df['Ward Name'] = ward_name

        # Melt the DataFrame to convert it from wide to long format
        df = pd.melt(df, id_vars=['Ward', 'Ward Name', 'Candidate'], var_name='Subdivision', value_name='Vote Count')

        # Append the melted DataFrame to the list
        dfs.append(df)

    # Concatenate all DataFrames in the list into a single DataFrame
    data = pd.concat(dfs, ignore_index=True)

    # Convert data types to integers
    data['Subdivision'] = data['Subdivision'].astype(int)
    data['Vote Count'] = data['Vote Count'].astype(pd.Int64Dtype())

    # Add 'Office' column with constant value 'Mayor'
    data['Office'] = 'Mayor'

    # Reorder the columns
    data = data[['Office', 'Candidate', 'Ward', 'Ward Name', 'Subdivision', 'Vote Count']]

    return data

def clean_cuncillor_election_search_results_2022():
    file_path = "raw_data/elections_official_results/2022/2022_Toronto_Poll_By_Poll_Councillor.xlsx"

    # Initialize an empty list to hold DataFrames
    dfs = []

    for sheet_name in pd.ExcelFile(file_path).sheet_names:
        # Read the sheet directly into a DataFrame, skipping the first row
        df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=1, engine="openpyxl")

        # Extract 'Ward Name' from cell A1 of the sheet (after skipping header)
        ward_name = df.columns[0]

        # Drop the first row (which contains the position, e.g., 'Mayor')
        df = df.iloc[1:]

        # Drop the last row (which may contain total values)
        df = df.iloc[:-1]

        df = df.drop(columns='Total')

        # Rename the columns and add 'Ward' and 'Ward Name' columns
        df.columns = ['Candidate'] + list(map(int, df.columns[1:]))
        df['Ward'] = int(sheet_name.split()[-1])
        df['Ward Name'] = ward_name
        df['Office'] = f"Councillor Ward {sheet_name.split()[-1]}"

        # Melt the DataFrame to convert it from wide to long format
        df = pd.melt(df, id_vars=['Office','Ward', 'Ward Name', 'Candidate'], var_name='Subdivision', value_name='Vote Count')

        # Append the melted DataFrame to the list
        dfs.append(df)

    # Concatenate all DataFrames in the list into a single DataFrame
    data = pd.concat(dfs, ignore_index=True)

    # Convert data types to integers
    data['Subdivision'] = data['Subdivision'].astype(int)
    data['Vote Count'] = data['Vote Count'].astype(pd.Int64Dtype())

    # Reorder the columns
    data = data[['Office', 'Candidate', 'Ward', 'Ward Name', 'Subdivision', 'Vote Count']]

    return data


import pandas as pd
from pyppeteer import launch
from syncer import sync
from abc import ABC, abstractmethod
import asyncio


class Data(ABC):
    def __init__(self):
        super().__init__()

    @staticmethod
    @abstractmethod
    def download():
        """Abstract static download method. Subclasses should implement this."""
        pass

    @staticmethod
    @abstractmethod
    def clean():
        """Abstract static clean method. Subclasses should implement this."""
        pass

class ContributionSearchResults(Data):
    @staticmethod
    async def download():
        browser = await launch(headless=True, autoClose=True)
        page = await browser.newPage()
        await page.goto('http://app.toronto.ca/EFD/jsf/main/main.xhtml?campaign=17')
        await page.click('button:has-text("Search Contributions")')
        await page.waitForSelector('button:has-text("Submit")', {'visible': True})
        await page.click('button:has-text("Submit")')
        await page.waitForSelector('button:has-text("Export")', {'visible': True})
        await page.click('button:has-text("Export")')
        # Implement logic here to handle the file download
        # ...
        await browser.close()

    @staticmethod
    def clean():
        file_path = "raw_data/contribution-search-results/2022/contribution-search-results.xls"
        df = pd.read_excel(file_path, usecols="A:L", skiprows=range(7), engine="xlrd")
        df.columns = (
            df.columns.str.replace("\n", " ", regex=False)
            .str.replace("\s+", " ", regex=True)
            .str.replace(" */ *", "/", regex=True)
            .str.strip()
        )
        return df

# Async wrapper to call the download and clean methods
async def main():
    await ContributionSearchResults.download()
    cleaned_data = ContributionSearchResults.clean()
    # Do something with cleaned_data

# Run the main function
asyncio.run(main())