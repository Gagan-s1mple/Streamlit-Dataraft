import pandas as pd

def clean_data(file_path):
    df = pd.read_csv(file_path)

    for col in df.columns:
        if df[col].dtype == float:
            mean_value = df[col].mean()
            df[col].fillna(mean_value, inplace=True)
        elif df[col].dtype == object:
            mode_value = df[col].mode()[0] if len(df[col].mode()) > 0 else ''
            df[col].fillna(mode_value, inplace=True)
    df.to_csv(file_path, index=False)
    
    date_columns = []
    for col in df.columns:
        try:
            pd.to_datetime(df[col])
            date_columns.append(col)
        except ValueError:
            pass
    for col in date_columns:
        if df[col].isnull().any():
            earliest_date = df[col].min()
            df[col].fillna(earliest_date, inplace=True)

#cleaned_data = clean_data(r"C:\Users\gagan\Downloads\Global+Electronics+Retailer\Exchange_Rates.csv")
