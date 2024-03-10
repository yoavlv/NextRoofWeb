import pandas as pd

from .sql_utils import get_connection


def get_user_saved(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Query to get item_ids from user_saved
        query = "SELECT item_id FROM user_saved WHERE user_id = %s"
        cursor.execute(query, (user_id, ))
        user_item_ids = [row[0] for row in cursor.fetchall()]

        if not user_item_ids:
            return pd.DataFrame()  # Return an empty DataFrame

        # Placeholder for item_ids in the query
        item_ids_placeholder = ', '.join(['%s'] * len(user_item_ids))

        # Modified query to join madlan_rank and madlan_predict
        query = f"""
        SELECT r.street, r.item_id, r.rooms, r.neighborhood, r.floor, r.size, r.city, r.price,
               p.predicted,r.images,p.difference
        FROM madlan_rank r
        LEFT JOIN madlan_predict p ON r.item_id = p.item_id
        WHERE r.item_id IN ({item_ids_placeholder})
        """
        cursor.execute(query, tuple(user_item_ids))

        # Fetch properties with additional columns and convert to DataFrame
        columns = [
            'street', 'item_id', 'rooms', 'neighborhood', 'floor', 'size',
            'city', 'price', 'predicted', 'images', 'difference'
        ]
        properties = pd.DataFrame(cursor.fetchall(), columns=columns)

    except Exception as e:
        print(f"Error: {e}")
        properties = pd.DataFrame()  # Return empty DataFrame in case of error

    finally:
        cursor.close()
        conn.close()

    return properties


def get_user_from_db(email):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT user_id, email, password_hash FROM users WHERE email = %s;"
        cursor.execute(query, (email, ))
        result = cursor.fetchone()
        if result:
            return {
                'user_id': result[0],
                'email': result[1],
                'password_hash': result[2]
            }
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()
    return None


def get_user_details(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT first_name, email, phone_number, city,birthday,subscribie FROM users WHERE user_id = %s;"
        cursor.execute(query, (user_id, ))
        result = cursor.fetchone()
        if result:
            return {
                'first_name': result[0],
                'email': result[1],
                'phone_number': result[2],
                'city': result[3],
                'birthday': result[4],
                'subscribie': result[5],
                # Add other fields as needed
            }
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()
    return None
