import datetime
import uuid

import psycopg2

from ..NextRoofWeb.settings.dev import db
from .utils.sql_utils import get_connection


def create_session(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        session_token = str(uuid.uuid4())  # Generate a unique session token
        # Calculate expiration timestamp 2 hours from now
        expiration = datetime.datetime.now() + datetime.timedelta(hours=5)

        query = """
        INSERT INTO custom_sessions (user_id, session_token, expiration)
        VALUES (%s, %s, %s)
        """

        cursor.execute(query, (user_id, session_token, expiration))
        conn.commit()

        return session_token, expiration

    except Exception as e:
        print(f"Error: {e}")
        return None, None

    finally:
        cursor.close()
        conn.close()


def invalidate_session(token):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            DELETE FROM custom_sessions WHERE session_token = %s
            """, (token, ))
        conn.commit()
    except Exception as e:
        print(f"Error during session invalidation: {e}")
    finally:
        cursor.close()
        conn.close()


def get_user_from_session(token):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT users.user_id, users.first_name , users.email ,users.phone_number
            FROM custom_sessions
            JOIN users ON custom_sessions.user_id = users.user_id
            WHERE custom_sessions.session_token = %s AND custom_sessions.expiration > CURRENT_TIMESTAMP
            """, (token, ))
        result = cursor.fetchone()
        if result:
            cursor.execute(
                "UPDATE custom_sessions SET last_accessed = CURRENT_TIMESTAMP WHERE session_token = %s",
                (token, ))
            conn.commit()
            return {
                "user_id": result[0],
                "first_name": result[1],
                "email": result[2],
                "phone_number": result[3]
            }
        else:
            return None
    finally:
        cursor.close()
        conn.close()


def session_middleware(get_response):
    def middleware(request):
        session_token = request.COOKIES.get('session_token')
        if session_token:
            user_data = get_user_from_session(session_token)
            if user_data:
                request.is_user_logged_in = True
                request.user_id = user_data['user_id']
                request.user_name = user_data['first_name']
                request.email = user_data['email']
                request.phone_number = user_data['phone_number']
            else:
                request.is_user_logged_in = False
        return get_response(request)

    return middleware
