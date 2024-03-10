import datetime
import uuid

from .utils.sql_utils import get_connection


def create_session(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        session_token = str(uuid.uuid4())  # Generate a unique session token
        # Calculate expiration timestamp t hours from now
        expiration = datetime.datetime.now() + datetime.timedelta(hours=1000)

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
            SELECT users.user_id, users.first_name , users.email ,users.phone_number ,users.super_user
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
                "phone_number": result[3],
                'super_user': result[4]
            }
        else:
            return None
    finally:
        cursor.close()
        conn.close()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[
            0]  # In case of multiple IPs, take the first one
    else:
        ip = request.META.get(
            'REMOTE_ADDR', ''
        )  # Fallback to REMOTE_ADDR if HTTP_X_FORWARDED_FOR is not available
    return ip


def entrance_count_middleware(session_id, page, user_agent, ip_address):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO entrance (session_id, page, time, user_agent, ip_address) VALUES (%s, %s, CURRENT_TIMESTAMP, %s, %s)",
            (session_id, page, user_agent, ip_address))
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()


def session_middleware(get_response):
    def middleware(request):
        session_token = request.COOKIES.get('session_token')

        page = request.path
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        if len(page) < 2:
            entrance_count_middleware(session_token, page, user_agent,
                                      ip_address)

        if session_token:
            user_data = get_user_from_session(session_token)
            if user_data:
                request.is_user_logged_in = True
                request.user_id = user_data.get('user_id')
                request.user_name = user_data.get('first_name')
                request.email = user_data.get('email')
                request.phone_number = user_data.get('phone_number')
                # Safely accessing super_user with a default value of False
                request.super_user = user_data.get('super_user', False)
            else:
                request.is_user_logged_in = False
                request.super_user = False
        else:
            request.is_user_logged_in = False
            request.super_user = False

        return get_response(request)

    return middleware
