import bcrypt
import psycopg2
from django.contrib import messages
# from ..forms.registration_form import CustomUserRegistrationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, render

from ...NextRoofWeb.settings.dev import db
from ..session import create_session, get_user_from_session, invalidate_session
from ..utils.sql_utils import get_connection
from ..utils.user_utils import get_user_details, get_user_from_db


def hash_password(plain_text_password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_text_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password.encode('utf-8'),
                          hashed_password.encode('utf-8'))


def login_view(request):
    error_message = ""
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = get_user_from_db(email)

        if user and check_password(password, user['password_hash']):
            session_token, expiration_time = create_session(user['user_id'])
            response = redirect('home')
            response.set_cookie(
                'session_token', session_token, max_age=7200
            )  # Set cookie expiration to 2 hours (7200 seconds)
            return response
        elif user:
            error_message = "Incorrect password!"
        else:
            error_message = "Email does not exist!"

    return render(request, 'login.html', {'error_message': error_message})


def logout_view(request):
    session_token = request.COOKIES.get('session_token')
    if session_token:
        invalidate_session(session_token)

    response = redirect('home')
    response.delete_cookie('session_token')  # Remove the session cookie
    return response


def register(request):
    session_token = request.COOKIES.get('session_token')
    # If the user isn't logged in, redirect to the login page
    if session_token:
        return redirect('home')
    if request.method == 'POST':
        first_name = request.POST['first_name']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        conn = get_connection()
        cursor = conn.cursor()

        # Check if passwords match
        if password1 == password2:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email, ))
            user_exists = cursor.fetchone()

            if user_exists:
                messages.error(request, 'דוא"ל זה כבר קיים במערכת.')
                cursor.close()
                conn.close()
                return redirect('register')
            else:
                hashed_password = hash_password(password1)
                cursor.execute(
                    "INSERT INTO users (first_name, email, password_hash) VALUES (%s, %s, %s)",
                    (first_name, email, hashed_password))
                conn.commit()
                messages.success(request, 'נרשמת בהצלחה!')
                cursor.close()
                conn.close()
                return redirect('login')  # Redirect to login page
        else:
            cursor.close()
            conn.close()
            messages.error(request, 'הסיסמאות אינן תואמות. נסה שוב.')
            return redirect('register')
    else:
        return render(request, 'register.html')


def get_user_properties(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT item_id FROM user_posts WHERE user_id = %s"
    cursor.execute(query, (user_id, ))
    user_item_ids = [row[0] for row in cursor.fetchall()]

    if not user_item_ids:
        return []

    item_ids_placeholder = ', '.join(['%s'] * len(user_item_ids))
    query = f"SELECT * FROM deals WHERE item_id IN ({item_ids_placeholder})"
    cursor.execute(query, tuple(user_item_ids))

    properties = cursor.fetchall()
    cursor.close()
    conn.close()

    return properties


def toggle_like(request, item_id):
    try:
        user_logged_in = request.is_user_logged_in
    except:
        user_logged_in = False

    if not user_logged_in:
        return HttpResponseForbidden('User not logged in')

    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT * FROM user_saved WHERE user_id = %s AND item_id = %s;"
        cursor.execute(query, (request.user_id, item_id))
        if cursor.fetchone():
            # Item is liked, so unlike it
            delete_query = "DELETE FROM user_saved WHERE user_id = %s AND item_id = %s;"
            cursor.execute(delete_query, (request.user_id, item_id))
            liked = False
        else:
            # Item is not liked, so like it
            insert_query = "INSERT INTO user_saved (user_id, item_id) VALUES (%s, %s);"
            cursor.execute(insert_query, (request.user_id, item_id))
            liked = True

        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        return JsonResponse({'error': str(e)})
    finally:
        cursor.close()
        conn.close()

    return JsonResponse({'liked': liked})
