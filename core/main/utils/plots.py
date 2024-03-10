import matplotlib
import matplotlib.pyplot as plt  # noqa: E402

matplotlib.use('Agg')
import base64
import io

import numpy as np
import pandas as pd

from ...NextRoofWeb.settings.dev import db, get_db_engine


def read_cities_and_streets_nadlan(table_name='nadlan_clean', city_id=False):
    engine = get_db_engine()
    if city_id:
        query = text(
            f"SELECT DISTINCT(street) , street_id FROM {table_name} WHERE city_id = :city_id and street_id is not null;"
        )
        with engine.connect() as conn:
            df = pd.read_sql_query(query, conn, params={"city_id": city_id})

            return dict(zip(df['street_id'], df['street']))
    else:
        query = text(
            f"SELECT DISTINCT(city), city_id FROM {table_name} where city_id is not null;"
        )
        with engine.connect() as conn:
            df = pd.read_sql_query(query, conn)
            city_dict = dict(zip(df['city_id'], df['city']))

            return city_dict


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
            f"SELECT {cols} FROM {table} WHERE {condition_column} = :value1 AND city_id = :value2"
        )
        params = {
            "value1": f"{condition_value_1}",
            "value2": f"{condition_value_2}"
        }
    else:
        # SQL query with one condition using LIKE
        query = text(
            f"SELECT {cols} FROM {table} WHERE {(condition_column)} = :value1")
        params = {"value1": f"{condition_value_1}"}

    with engine.connect() as conn:
        df = pd.read_sql_query(query, conn, params=params)
    return df


from sqlalchemy import text


def city_plot(city_id, city_name, start_year=2017, end_year=2024):

    condition = {
        'where': 'city_id',
        'value_1': city_id,
    }
    query_params = {
        'table': 'nadlan_clean',
        'cols': 'date,price,size,city_id,street_id',
        'condition': condition,
    }
    df = read_from_db(query_params)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year.astype(np.int32)
    last_year = df['year'].max()
    years = range(2017, int(last_year) + 1)
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
    text = f' מחיר ממוצע למטר ב-{city_name}'
    plt.title(text[::-1], fontsize=12)

    plt.plot(df_grouped.index,
             df_grouped['PRICE_PER_METER'],
             '-o',
             label='Price per meter')
    text = 'מחיר ממוצע למטר ב-₪'
    plt.ylabel(text[::-1])
    # Prepare custom x-axis labels with years and total deals
    custom_xticks_labels = [
        f"{year}\n({total_per_year.get(year, 0)})" for year in years
    ]
    plt.xticks(df_grouped.index, custom_xticks_labels, rotation=0)
    text = 'שנה \ סה"כ עסקאות'  # noqa: W605

    plt.xlabel(text[::-1])

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


def lasted_deals_street(city_id, city_name, street_id, street_name):
    items = []
    street_id = int(street_id)
    city_id = int(city_id)

    engine = get_db_engine()
    with engine.connect() as conn:
        query_params = text(
            "SELECT date,type,rooms,floor,build_year,home_number, price, size, city, street FROM nadlan_clean WHERE city_id = :city_id AND street_id = :street_id ORDER BY date DESC LIMIT 5"
        )
        df = pd.read_sql_query(query_params,
                               conn,
                               params={
                                   'city_id': city_id,
                                   'street_id': street_id
                               })

    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year.astype(np.int32)

    df_history_deals = df.sort_values(by='date', ascending=False)

    df_filtered = df_history_deals.head(5)
    for index, row in df_filtered.iterrows():
        formatted_date = row['date'].strftime('%Y-%m-%d')
        item = {
            'date': formatted_date,
            'type': row.get('type', 'N/A'),  # Default to 'N/A' if missing
            'rooms': row.get('rooms', 'N/A'),
            'floor': row.get('floor', 'N/A'),
            'size': row.get('size', 'N/A'),
            'price':
            f"₪{row['price']:,}" if row.get('price') is not None else 'N/A',
            'build_year': row.get('build_year', 'N/A'),
            'floors': row.get('floors', 'N/A'),
            'home_number': int(float(row.get('home_number', 'N/A'))),
        }
        items.append(item)

    return items


def street_plot(city_id, city_name, street_id, street_name):
    condition = {
        'where': 'street_id',
        'value_1': int(street_id),
        'value_2': int(city_id),
    }
    query_params = {
        'table': 'nadlan_clean',
        'cols': 'date, price, size, city_id, street_id , city, street',
        'condition': condition,
    }
    df = read_from_db(query_params)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year.astype(np.int32)

    price_per_meter_by_year = {}
    total_per_year = {}
    for year in range(2017, 2024):
        year_data = df[(df["street_id"] == int(street_id))
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
    text = f' מחיר ממוצע למטר בעיר- {city_name} ברחוב - {street_name}'
    plt.title(text[::-1], fontsize=15)
    text = 'שנה \ סה"כ עסקאות'  # noqa: W605
    plt.xlabel(text[::-1])
    text = 'מחיר למטר ₪'
    plt.ylabel(text[::-1])
    plt.subplots_adjust(bottom=0.2)

    # Save the plot as an image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    plot_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

    plt.close()
    return plot_image
