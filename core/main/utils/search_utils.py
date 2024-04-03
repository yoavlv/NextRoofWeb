from .sql_utils import get_connection


def create_apartment_item(res, liked=False):
    base_link = "https://madlan.co.il/listings/"

    price = int(res[7])
    p_price = int(res[8])
    item_id = str(res[1])

    try:
        images = res[9].split(",")
        img = images[0][1:]
        img = (
            'https://images2.madlan.co.il/t:nonce:v=2;resize:height=1280;convert:type=webp/'
            + img).replace('"', '').replace('}', '').replace('//b',
                                                             '/b').strip()
    except:
        img = None
    return {
        'Street': res[0],
        'Item_id': item_id,
        'Room': int(res[2]),
        'Neighborhood': res[3],
        'Floor': int(res[4]),
        'Size': int(res[5]),
        'City': res[6],
        'Price': f"₪{price:,.0f}",
        'Predicted': f"₪{p_price:,.0f}",
        'p_change': calculate_percentage_difference(res[7], res[8]),
        'Images': img,
        'link': base_link + item_id,
        'Liked': liked
    }


def calculate_percentage_difference(num1, num2):
    num1 = int(num1)
    num2 = int(num2)
    difference = num1 - num2
    average = (num1 + num2) / 2
    percentage_difference = ((difference / average) * 100) * -1
    return round(percentage_difference, 2)


def user_liked_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT item_id FROM user_saved WHERE user_id = %s"
    cursor.execute(query, (user_id, ))
    user_id_list = [row[0] for row in cursor.fetchall()
                    ]  # Assuming item_id is the first column
    return user_id_list
