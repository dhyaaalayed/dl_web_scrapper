import pandas as pd



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

    # set hauschar column
    hauschar_index = _get_hauschr_index(columns)
    columns[hauschar_index] = "Hauschar"

    return columns



def log(message):
    print("Log: " + message)