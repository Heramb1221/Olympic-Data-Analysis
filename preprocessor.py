import pandas as pd

def preprocess(df, region_df):

    # Filter only Summer Olympics
    df = df[df['Season'] == 'Summer']

    # Merge with region info
    df = df.merge(region_df, on='NOC', how='left')

    # Drop duplicate rows
    df.drop_duplicates(inplace=True)

    # Drop existing columns if dummy names already exist to prevent duplication
    for col in ['Gold', 'Silver', 'Bronze']:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    # Create one-hot encoded medal columns
    medal_dummies = pd.get_dummies(df['Medal'])

    # Ensure consistency in column names
    for medal in ['Gold', 'Silver', 'Bronze']:
        if medal not in medal_dummies.columns:
            medal_dummies[medal] = 0

    # Concatenate the one-hot encoded columns
    df = pd.concat([df, medal_dummies[['Gold', 'Silver', 'Bronze']]], axis=1)

    # Remove duplicate columns, if any, as a final safety step
    df = df.loc[:, ~df.columns.duplicated()]

    return df
