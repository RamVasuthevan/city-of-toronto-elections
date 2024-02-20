from abc import ABC, abstractmethod
import os
import pandas as pd
from openpyxl import load_workbook
import sqlite_utils


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
    raw_data_dir = os.path.join(os.getcwd(), "raw_data/contribution_search_results/2022/")

    @classmethod
    def download(cls):
        pass

    @classmethod
    def clean(cls):
        file = os.path.join(cls.raw_data_dir,"contribution-search-results.xls")
        df = pd.read_excel(file,usecols="A:L", skiprows=range(7))
        df.columns = (
            df.columns.str.replace("\n", " ", regex=False)
            .str.replace("\s+", " ", regex=True)
            .str.replace(" */ *", "/", regex=True)
            .str.strip()
        )

        df['Amount'] = df['Amount'].astype(float)
        df['Amount Returned'] = df['Amount Returned'].astype(float)
        df['Contribution Type'] = pd.Categorical(df['Contribution Type'], categories=["Monetary", "Goods/Services"])
        df['Description of Goods/Services'] = df['Description of Goods/Services'].astype('string')
        df['Contributor Type'] = pd.Categorical(df['Contributor Type'], categories=["Candidate", "Individual", "Candidate Spouse", "Third Party Registrant"], ordered=False)
        df['Date Contribution Received'] = pd.to_datetime(df['Date Contribution Received'], format='%b %d, %Y').dt.date
        df['Registered for'] = pd.Categorical(df['Registered for'], categories=["Mayor", "Councillor", "Toronto District School Board", "Toronto Catholic District School Board", "Third Party Advertiser"], ordered=False)
        df['Ward'] = pd.Categorical(df['Ward'], categories=range(26))
        df['Registrant Type'] = pd.Categorical(df["Registrant Type"],categories=["Corporation","Individual"])

        return df

class ElectionsOfficialResults(Data):
    raw_data_dir = os.path.join(os.getcwd(), "raw_data/elections_official_results/2022/")

    @classmethod
    def download(cls):
        pass

    @staticmethod
    def clean_election_search_results_2022(file_path,mayor=False):
        # Initialize an empty list to hold DataFrames
        dfs = []

        # Load the workbook and sheet names using openpyxl
        workbook = load_workbook(filename=file_path, data_only=True)

        for sheet_name in workbook.sheetnames:
            # Access the sheet
            sheet = workbook[sheet_name]

            # Extract 'Ward Name' from cell A1
            office = "Mayor" if mayor else sheet['A1'].value

            # Read the sheet into a DataFrame, skipping the first row
            df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=1, engine="openpyxl")

            # Drop the first row (now second row in df) which contains the position, e.g., 'Mayor'
            df = df.iloc[1:]

            # Drop the last row (which may contain total values)
            df = df.iloc[:-1]

            df = df.drop(columns='Total')

            # Rename the columns and add 'Ward' and 'Ward Name' columns
            df.columns = ['Candidate'] + list(map(int, df.columns[1:]))
            df['Ward'] = int(sheet_name.split()[-1])
            df['Office'] = office

            # Melt the DataFrame to convert it from wide to long format
            df = pd.melt(df, id_vars=['Office', 'Ward', 'Candidate'], var_name='Subdivision', value_name='Vote Count')

            # Append the melted DataFrame to the list
            dfs.append(df)

        # Concatenate all DataFrames in the list into a single DataFrame
        data = pd.concat(dfs, ignore_index=True)

        # Convert data types
        data['Subdivision'] = data['Subdivision'].astype(int)
        data['Vote Count'] = data['Vote Count'].astype(pd.Int64Dtype())

        # Reorder the columns
        data = data[['Office', 'Candidate', 'Ward', 'Subdivision', 'Vote Count']]

        return data


    def clean(cls):
        mayor = cls.clean_election_search_results_2022("raw_data/elections_official_results/2022/2022_Toronto_Poll_By_Poll_Mayor.xlsx",mayor=True)
        councillor = cls.clean_election_search_results_2022("raw_data/elections_official_results/2022/2022_Toronto_Poll_By_Poll_Councillor.xlsx")
        tdsb_counselor = cls.clean_election_search_results_2022("raw_data/elections_official_results/2022/2022_Toronto_Poll_By_Poll_Toronto_District_School_Board.xlsx")
        return pd.concat([mayor,councillor,tdsb_counselor],ignore_index=True)

def build_db():
    if os.path.exists("database.db"):
        os.remove("database.db")
    ContributionSearchResults().clean().to_sql(name="contribution_search_results",con="sqlite:///database.db")
    #ElectionsOfficialResults().clean("raw_data/elections_official_results/2022/2022_Toronto_Poll_By_Poll_Mayor.xlsx").to_sql(name="elections_official_results_mayor",con="sqlite:///database.db")
    #electionsOfficialResults().clean("raw_data/elections_official_results/2022/2022_Toronto_Poll_By_Poll_Councillor.xlsx").to_sql(name="elections_official_results_councillor",con="sqlite:///database.db")
    #ElectionsOfficialResults().clean("raw_data/elections_official_results/2022/2022_Toronto_Poll_By_Poll_Toronto_District_School_Board.xlsx").to_sql(name="elections_official_results_tdsb_trustee",con="sqlite:///database.db")
    ElectionsOfficialResults().clean().to_sql(name="elections_official_results",con="sqlite:///database.db")

    db = sqlite_utils.Database("database.db")
    db.create_view("[election_winner]", """SELECT Candidate, Ward, "Vote Count" FROM ( SELECT Candidate, Ward, SUM([Vote Count]) as "Vote Count", ROW_NUMBER() OVER(PARTITION BY Ward ORDER BY SUM([Vote Count]) DESC) as rn FROM elections_official_results GROUP BY Candidate, Ward ) subquery WHERE rn = 1 ORDER BY Ward, "Vote Count" DESC""")

build_db()