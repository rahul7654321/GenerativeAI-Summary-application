import google.generativeai as genai
import textwrap
import pandas as pd
import os
import sys

def check_file(file_path):
    if file_path.lower().endswith((".csv")):
        return "csv"
    elif file_path.lower().endswith(".xls"):
        return "xls"
    elif file_path.lower().endswith(".xlsx"):
        return "xlsx"
    else:
        return "none"


def get_user_input(prompt_message):
    while True:
        try:
            user_input = input(prompt_message).strip()

            if not user_input:
                raise NoPromptProvidedError(
                    "Not 'enter_the_prompt' provided. Please enter a valid prompt."
                )

            return user_input

        except NoPromptProvidedError as e:
            print(e)


def get_valid_file_path():
    while True:
        try:
            file_path = input("Enter the file path: ").strip()

            if not file_path:
                raise ValueError("Error No file path provided")

            file_type = check_file(file_path)


            if file_type == "none":
                raise ValueError("Given file is not a CSV, XLS, or XLSX")

            # print("File is valid, proceed with processing.....")
            return file_path

        except ValueError as e:
            print(f"Error: {e}")


def get_valid_row_names(df):
    while True:
        try:

            row_names = [
                name.strip().lower()
                for name in input("Enter the row names separated by commas: ").split(
                    ","
                )
            ]
            col_mapping = {col.lower(): col for col in df.columns}

            missing_columns = [name for name in row_names if name not in col_mapping]

            if missing_columns:
                raise ValueError(
                    f"Error No column found: {', '.join(missing_columns)}. Please enter the columns that are found!"
                )

            print("All columns are valid.")
            return row_names

        except ValueError as e:
            print(f"Error: {e}")


def get_last_row_name(col_mapping2):
    while True:
        try:
            last_row_name = input("Last row name: ").strip().lower()

            if not last_row_name:
                raise ValueError("Last row name is required.")
            if last_row_name in col_mapping2:
                raise ValueError("Enter another column name; this one already exists.")

            last_row_name = col_mapping2.get(last_row_name, last_row_name)

            print(f"Last row name entered: {last_row_name}")
            return last_row_name

        except ValueError as e:
            print(f"Error: {e}")

def read_file(file_path, file_type):
    try:
        if file_type == "csv":
            df = pd.read_csv(os.path.expanduser(file_path), delimiter=",")
        elif file_type == "xls":
            df = pd.read_excel(os.path.expanduser(file_path), engine="xlrd")
        elif file_type == "xlsx":
            df = pd.read_excel(os.path.expanduser(file_path), engine="openpyxl")
        else:
            raise ValueError("Unsupported file type")
        return df
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def process_summary_column(df,Last_row_name,No_data):
    condition = df[Last_row_name].str.contains(No_data, na=False) & (df.drop(columns=[Last_row_name]).isna().all(axis=1))
    df.loc[condition, Last_row_name] = ""    
    return df


class NoPromptProvidedError(Exception):
    """exception for no prompt provided."""

    pass


class MissingColumnsError(Exception):
    """exception for missing columns."""

    pass


def to_markdown(text, width=30):
    return textwrap.fill(text, width=width)


def main():


    #file_path = "~/Downloads/username.csv"
   

    ############################################################################################################################################################
    df = None
    while df is None:
        
        file_path = get_valid_file_path()
        file_type = check_file(file_path)
        df = read_file(file_path, file_type)
        if df is None:
            print("Please try again.")
    
    try:

        if file_type == "none":
            raise ValueError("Given file is not a CSV, XLS, or XLSX")

    except ValueError as e:
        print(f"Error: {e}")

    # print(df)

    

    GOOGLE_API_KEY = "AIzaSyBkWNnmo7o4VmCfChcFBoSEEJwRUV1S8pM"

    genai.configure(api_key=GOOGLE_API_KEY)

    row_names = get_valid_row_names(df)

    number_of_rows = len(row_names)

    col_mapping2 = {col.lower(): col for col in df.columns}

    enter_the_prompt = get_user_input("Enter the enter_the_prompt: ")

    Last_row_name = get_last_row_name(col_mapping2)

    df[Last_row_name] = ""

    print("Summarizing data...")

    No_data = "No data Found to Compare !!"

    model = None
    try:
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                print(m.name)
                model = genai.GenerativeModel(m.name)
                break
    except Exception as e:
        sys.exit(f"API error Please Check the Api !!")
            

    if model is not None:
        for index, row in df.iterrows():
            rowsToCompare = " ".join([str(row[col_mapping2[r]]) for r in row_names])
            # print(rowsToCompare)

            nan_count = rowsToCompare.count("nan")
            if nan_count == number_of_rows:
                df.at[index, Last_row_name] = No_data
                continue
            else:
                combined_text = rowsToCompare + " " + enter_the_prompt
                while True:
                    try:
                        response = model.generate_content(combined_text)
                        formatted_text = to_markdown(response.text, width=60)
                        df.at[index, Last_row_name] = formatted_text
                        break  
                    except ValueError as e:
                        print(f"API error for row {index}, retrying...")


    else:
        print("No suitable model found.")

    df = process_summary_column(df,Last_row_name,No_data)


    try:
        if file_type == "csv":
            df.to_csv(
                os.path.expanduser("~/Documents/updated_sports.csv"),
                index=False,
                sep=",",
            )
            print("Summary Downloaded Successfully")
        elif file_type == "xls":
            df.to_excel(
                os.path.expanduser("~/Documents/updated_sports.xls"),
                index=False,
                engine="openpyxl",
            )
            print("Summary Downloaded Successfully")
        elif file_type == "xlsx":
            df.to_excel(
                os.path.expanduser("~/Documents/updated_sports.xlsx"),
                index=False,
                engine="openpyxl",
            )
            print("Summary Downloaded Successfully")
    except Exception as e:
        print(f"Error saving file: {e}")

    # print("You Summary was Successfully Downlaods")
    


######################################################################################################################################################


if __name__ == "__main__":
    main()
