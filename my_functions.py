from pathlib import Path

import pandas as pd
from openpyxl.reader.excel import load_workbook


def get_template_columns(template_path, number_of_columns):
    def _get_hauschr_index(new_columns):
        for idx, column in enumerate(new_columns):
            if pd.isnull(column):
                return idx


    df = pd.read_excel(template_path)

    # Cut until columns row:
    df = df[5:]
    # Cut null columns:
    df = df.iloc[:, :number_of_columns]


    columns = list(df.iloc[0])
    print("template columns: ", columns)
    # set hauschar column
    hauschar_index = _get_hauschr_index(columns)
    columns[hauschar_index] = "Hauschar"

    return columns

def write_bvh_dfs_to_excel(path, bvh_city_name, df):
    book = load_workbook(path)  # assuming that the new template is there
    writer = pd.ExcelWriter(path, engine='openpyxl')
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

    print("Log: Writing on Excel")

    sheet = book["HA_Auswertung"]
    sheet["A1"] = "All Montage: " + bvh_city_name

    df.to_excel(writer, index=False, startrow=7, startcol=0, sheet_name='HA_Auswertung', header=False)
    writer.save()


def log(message):
    print("Log: " + message)