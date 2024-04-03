import matplotlib

matplotlib.use('Agg')
import base64
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import text
from ...NextRoofWeb.settings.dev import get_db_engine


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


def city_plot(city_id, city_name, start_year=2017, end_year=2024):
    condition = {'where': 'city_id', 'value_1': city_id}
    query_params = {
        'table': 'nadlan_clean',
        'cols': 'date, price, size, city_id, street_id, year',
        'condition': condition,
    }
    df = read_from_db(query_params)  # Assuming read_from_db returns a DataFrame

    df = df[df['year'] >= start_year]
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df_grouped = df.groupby('year').apply(lambda x: pd.Series({
        'PRICE_PER_METER': (x['price'] / x['size']).mean(),
        'total_transactions': len(x)
    })).reset_index()

    df_grouped['PERCENT_CHANGE'] = df_grouped['PRICE_PER_METER'].pct_change() * 100

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_grouped['year'],
            y=df_grouped['PRICE_PER_METER'],
            mode='lines+markers',
            name='מחיר למטר',
            line=dict(color='RoyalBlue'),
            marker=dict(size=22)
        )
    )

    fig.update_layout(
        title=f'מחיר ממוצע למטר ב{city_name}',
        title_x=0.5,
        xaxis=dict(
            title='שנה / מספר עסקאות',
            tickmode='array',
            tickvals=df_grouped['year'],
            ticktext=[
                f"{year} / {transactions}" for year, transactions in zip(df_grouped['year'], df_grouped['total_transactions'].astype(int))
            ]
        ),
        yaxis_title='מחיר ממוצע למטר (₪)',
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        plot_bgcolor='rgba(211, 211, 211, 0.2)',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=20, color="black"),
        height=420,
        width=1250,
        margin=dict(l=20, r=20, t=40, b=40)
    )

    for i, row in df_grouped.iterrows():
        if i > 0:
            fig.add_annotation(
                x=row['year'],
                y=row['PRICE_PER_METER'],
                text=f"{row['PERCENT_CHANGE']:.2f}%",
                showarrow=True,
                arrowhead=3,
                yshift=10,
                font=dict(size=20, color="red" if row['PERCENT_CHANGE'] > 0 else "green")
            )

    img_bytes = fig.to_image(format="png")
    encoding = base64.b64encode(img_bytes).decode('utf-8')
    return encoding


def street_plot(city_id, city_name, street_id, street_name):
    condition = {
        'where': 'street_id',
        'value_1': int(street_id),
        'value_2': int(city_id),
    }
    query_params = {
        'table': 'nadlan_clean',
        'cols': 'date, price, size, city_id, street_id, city, street, year',
        'condition': condition,
    }
    df = read_from_db(query_params)  # Replace this with actual fetching logic

    price_per_meter_by_year = {}
    total_per_year = {}
    percentage_change_by_year = {}

    for year in range(2017, datetime.datetime.now().year + 1):
        year_data = df[(df["street_id"] == int(street_id)) & (df['year'] == year)]

        if not year_data.empty and year_data['size'].sum() > 0:
            total_transactions = year_data.shape[0]
            average_price_per_meter = year_data['price'].sum() / year_data['size'].sum()

            price_per_meter_by_year[year] = round(average_price_per_meter)
            total_per_year[year] = total_transactions

            if year > 2017:
                prev_year_price = price_per_meter_by_year[year - 1]
                change = ((average_price_per_meter - prev_year_price) / prev_year_price) * 100
                percentage_change_by_year[year] = round(change, 2)

    fig = go.Figure()

    years = list(price_per_meter_by_year.keys())
    prices_per_meter = list(price_per_meter_by_year.values())
    transactions = [total_per_year[year] for year in years]

    fig.add_trace(go.Scatter(x=years, y=prices_per_meter, mode='lines+markers',
                             name='מחיר למטר',
                             line=dict(color='RoyalBlue'),
                             marker=dict(size=22)))

    fig.update_layout(
        title=f'מחיר ממוצע למטר ב{city_name}, {street_name}',
        xaxis=dict(
            title='שנה / עסקאות',
            tickmode='array',
            tickvals=years,
            ticktext=[f"{year} / {trans}" for year, trans in zip(years, transactions)]
        ),
        yaxis_title='מחיר ממוצע למטר (₪)',
        plot_bgcolor='rgba(211, 211, 211, 0.2)',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=20, color="black"),
        height=450,
        width=1150,
        margin=dict(l=20, r=20, t=40, b=40)
    )

    for year, change in percentage_change_by_year.items():
        fig.add_annotation(
            x=year,
            y=price_per_meter_by_year[year],
            text=f"{change}%",
            showarrow=True,
            arrowhead=3,
            yshift=10,
            font=dict(size=20, color="red" if change > 0 else "green")
        )

    img_bytes = fig.to_image(format="png")
    encoding = base64.b64encode(img_bytes).decode('utf-8')
    return encoding


def lasted_deals_street(city_id, city_name, street_id, street_name):
    items = []
    street_id = int(street_id)
    city_id = int(city_id)

    engine = get_db_engine()
    with engine.connect() as conn:
        query_params = text(
            "SELECT date,type,rooms,floor,build_year,home_number, price, size, city, street, floors FROM nadlan_clean WHERE city_id = :city_id AND street_id = :street_id ORDER BY date DESC LIMIT 5"
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
            'city': row.get('city', 'N/A'),
            'street': row.get('street', 'N/A'),
            'type': row.get('type', 'N/A'),
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
