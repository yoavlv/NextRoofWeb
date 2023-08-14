from django.db import connection
import pandas as pd


def lasted_deals_street(street):
    items = []
    df_history_deals = pd.read_csv('data/Nadlan_clean.csv')
    df_filtered = df_history_deals[df_history_deals['Street'] == street].sort_values(by='Year', ascending=False)
    df_filtered = df_filtered.head(7)
    for index, row in df_filtered.iterrows():
        item = {
            'Date': row['Date'],
            'Type': row['Type'],
            'Rooms': int(row['Rooms']),
            'Floor': row['Floor'],
            'Size': row['Size'],
            'Price': "₪{:,}".format(row['Price']),
            'Build_year': row['Build_year'],
            'Floors': row['Floors'],
            'Home_number': row['Home_number'],
        }
        items.append(item)

    return items



