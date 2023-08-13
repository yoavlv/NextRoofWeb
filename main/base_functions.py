from django.db import connection

def lasted_deals_street(street):
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT Date, Type, Rooms, Floor, Size, Price, Build_year, Floors, Home_number , Year "
            f"FROM history_deals WHERE street = '{street}' ORDER BY Year DESC LIMIT 5"
        )
        rows = cursor.fetchall()

    items = []
    for row in rows:
        item = {
            'Date': row[0],
            'Type': row[1],
            'Rooms': int(row[2]),
            'Floor': row[3],
            'Size': row[4],
            'Price': "₪{:,}".format(row[5]) ,
            'Build_year': row[6],
            'Floors': row[7],
            'Home_number': row[8],

        }
        items.append(item)
    return items

