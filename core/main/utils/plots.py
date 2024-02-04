import matplotlib
import matplotlib.pyplot as plt  # noqa: E402

matplotlib.use('Agg')
import base64
import io

import numpy as np
import pandas as pd
from sqlalchemy import text

from ...NextRoofWeb.settings.dev import db, get_db_engine


def read_from_db(query_params):
    engine = get_db_engine()
    table = query_params['table']
    cols = query_params['cols']
    condition = query_params['condition']

    condition_column = condition['where']
    condition_value_1 = condition['value_1']

    # Check if there's a second condition value
    if 'value_2' in condition:
        condition_value_2 = condition['value_2']
        # SQL query with two conditions using LIKE
        query = text(
            f"SELECT {cols} FROM {table} WHERE {condition_column} LIKE :value1 AND city LIKE :value2"
        )
        params = {
            "value1": f"%{condition_value_1}%",
            "value2": f"%{condition_value_2}%"
        }
    else:
        # SQL query with one condition using LIKE
        query = text(
            f"SELECT {cols} FROM {table} WHERE {condition_column} LIKE :value1"
        )
        params = {"value1": f"%{condition_value_1}%"}

    with engine.connect() as conn:
        df = pd.read_sql_query(query, conn, params=params)
    return df


def neighborhood_plot(city, neighborhood):
    condtion = {
        'where': 'neighborhood',
        'value_1': neighborhood,
        'value_2': city,
    }
    query_params = {
        'table': 'nadlan_clean',
        'cols': 'date,price,size,city,neighborhood,city,street',
        'condition': condtion,
        'city': city,
    }
    df = read_from_db(query_params)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year.astype(np.int32)
    years = range(2017, 2024)
    price_per_meter_by_year = {}
    for year in years:
        year_data = df[(df["neighborhood"].str.contains(neighborhood))
                       & (df['year'] == year)]
        if year_data.shape[0] >= 1:
            average_price_per_meter = year_data['price'].sum(
            ) / year_data['size'].sum()
            price_per_meter_by_year[year] = round(average_price_per_meter)

    plt.figure(figsize=(7, 3))
    bars = tuple(price_per_meter_by_year.keys())
    x_pos = np.arange(len(bars))
    plt.bar(x_pos, price_per_meter_by_year.values(), color='gray', width=0.5)
    plt.xticks(x_pos, bars, rotation=10)
    text = f"מחיר למטר לפני שנים - {neighborhood} - {city} "
    plt.title(text[::-1], fontsize=15)
    plt.xlabel("Year", color='k', fontsize=3)
    plt.ylabel("Price per meter")
    # Save the plot as an image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    plot_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

    plt.close()
    return plot_image


def city_plot(city, start_year=2017, end_year=2024):
    condition = {
        'where': 'city',
        'value_1': city,
    }
    query_params = {
        'table': 'nadlan_clean',
        'cols': 'date,price,size,city,neighborhood,street',
        'condition': condition,
    }
    df = read_from_db(query_params)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year.astype(np.int32)
    years = range(2017, 2024)
    price_per_meter_by_year = {}
    total_per_year = {}
    for year in years:
        year_data = df[df['year'] == year]
        if not year_data.empty and year_data['size'].sum() > 0:
            year_data_shape = year_data.shape[0]
            total_per_year[year] = int(year_data_shape)
            average_price_per_meter = year_data['price'].sum(
            ) / year_data['size'].sum()
            price_per_meter_by_year[year] = round(average_price_per_meter)

    df_grouped = pd.DataFrame.from_dict(price_per_meter_by_year,
                                        orient='index',
                                        columns=['PRICE_PER_METER'])

    plt.figure(figsize=(7, 3))
    plt.title(f'AVG Price per Meter in {city[::-1]}', fontsize=12)

    plt.plot(df_grouped.index,
             df_grouped['PRICE_PER_METER'],
             '-o',
             label='Price per meter')
    plt.ylabel('Average Price per Meter (NIS ₪)')
    # Prepare custom x-axis labels with years and total deals
    custom_xticks_labels = [
        f"{year}\n({total_per_year.get(year, 0)})" for year in years
    ]
    plt.xticks(df_grouped.index, custom_xticks_labels, rotation=0)

    plt.xlabel('Year / Total Deals')

    # Calculate the percentage change
    price_change = (df_grouped['PRICE_PER_METER'].diff() /
                    df_grouped['PRICE_PER_METER'].shift(1)) * 100
    price_change.dropna(inplace=True)

    for i, change in enumerate(price_change):
        x = price_change.index[i]
        y = df_grouped.loc[x, 'PRICE_PER_METER']
        plt.annotate("{:.1f}%".format(change), (x, y),
                     textcoords="offset points",
                     xytext=(-5, 5),
                     ha='center',
                     fontsize=9)

    plt.legend()
    plt.subplots_adjust(bottom=0.3)
    # Save the plot as an image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    plot_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

    plt.close()
    return plot_image


def lasted_deals_street(city, street):
    items = []

    condition = {'where': 'street', 'value_1': street, 'value_2': city}

    query_params = {
        'table': 'nadlan_clean',
        'cols':
        'date,type,rooms,floor,size,build_year,floors,home_number,street,price,city,neighborhood',
        'condition': condition,
    }
    df = read_from_db(query_params)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year.astype(np.int32)

    # Filter for the specified city if needed
    df = df[df['city'] == city]

    df_history_deals = df.sort_values(by='date', ascending=False)

    df_filtered = df_history_deals.head(5)
    for index, row in df_filtered.iterrows():
        formatted_date = row['date'].strftime('%Y-%m-%d')
        item = {
            'Date': formatted_date,
            'Type': row.get('type', 'N/A'),  # Default to 'N/A' if missing
            'Rooms': row.get('rooms', 'N/A'),
            'Floor': row.get('floor', 'N/A'),
            'Size': row.get('size', 'N/A'),
            'Price':
            f"₪{row['price']:,}" if row.get('price') is not None else 'N/A',
            'Build_year': row.get('build_year', 'N/A'),
            'Floors': row.get('floors', 'N/A'),
            'Home_number': row.get('home_number', 'N/A'),
        }
        items.append(item)

    return items


def street_plot(city, street):
    # Assuming read_from_db is a function that fetches data based on query_params
    condition = {
        'where': 'street',
        'value_1': street,
        'value_2': city,
    }
    query_params = {
        'table': 'nadlan_clean',
        'cols': 'date, price, size, city, street',
        'condition': condition,
    }
    df = read_from_db(query_params)

    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year.astype(np.int32)

    price_per_meter_by_year = {}
    total_per_year = {}
    for year in range(2017, 2024):
        year_data = df[df["street"].str.contains(street)
                       & (df['year'] == year)]

        if not year_data.empty and year_data['size'].sum() > 0:
            year_data_shape = year_data.shape[0]
            total_per_year[year] = int(year_data_shape)
            average_price_per_meter = year_data['price'].sum(
            ) / year_data['size'].sum()
            price_per_meter_by_year[year] = round(average_price_per_meter)

    plt.figure(figsize=(7, 3.5))
    # Only include years with data in the plot
    years_with_data = sorted(price_per_meter_by_year.keys())
    x_pos = np.arange(len(years_with_data))

    values = [price_per_meter_by_year[year] for year in years_with_data]
    plt.bar(x_pos, values, color='blue', width=0.5)

    custom_xticks_labels = [
        f"{year}\n({total_per_year.get(year, 0)})" for year in years_with_data
    ]
    plt.xticks(x_pos, custom_xticks_labels, rotation=0)

    plt.title(f"מחיר למטר ברחוב {street} בעיר {city}"[::-1], fontsize=15)
    plt.xlabel('Year / Total Deals')
    plt.ylabel("Price per meter")
    plt.subplots_adjust(bottom=0.2)

    # Save the plot as an image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    plot_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

    plt.close()
    return plot_image
