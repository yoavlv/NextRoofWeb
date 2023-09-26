from django.contrib import messages
from django.shortcuts import redirect, render

from ..session import get_user_from_session
from ..utils.search_utils import create_apartment_item
from ..utils.sql_utils import get_connection
from ..utils.user_utils import get_user_details, get_user_saved


def edit_profile(request):
    session_token = request.COOKIES.get('session_token')
    # If the user isn't logged in, redirect to the login page
    if not session_token:
        return redirect('login')

    user_data = get_user_from_session(session_token)

    if not user_data:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('login')

    if request.method == 'POST':
        city = request.POST.get('city', None)
        phone_number = request.POST.get('phone_number', None)
        birthday = request.POST.get('birthday', None)
        if not birthday:  # Check for empty string and set to None
            birthday = None
        subscribie = request.POST.get('subscribie', False)

        conn = get_connection()
        cursor = conn.cursor()

        try:
            query = """
                UPDATE users
                SET city = %s, phone_number = %s, birthday = %s, subscribie = %s
                WHERE user_id = %s
            """
            cursor.execute(query, (city, phone_number, birthday, subscribie,
                                   user_data['user_id']))
            conn.commit()

            messages.success(request, 'Profile updated successfully!')
            return redirect('home')

        except Exception as e:
            messages.error(request,
                           'Error updating profile. Please try again.')
            print(f"Error: {e}")

        finally:
            cursor.close()
            conn.close()

    # For GET request, fetch user details to populate the form
    user_details = get_user_details(user_data['user_id'])

    return render(request, 'edit_profile.html', {'user': user_details})


def profile_view(request):
    if not hasattr(
            request,
            'user_id'):  # We're checking for user_id now, not user_name.
        return render(request, 'error.html',
                      {'message': 'Please login to view this page.'})

    conn = get_connection()
    cursor = conn.cursor()

    try:
        user = get_user_details(request.user_id)
        liked_properties = get_user_saved(request.user_id)
        apartments = [
            create_apartment_item(row)
            for index, row in liked_properties.iterrows()
        ]

    except Exception as e:
        print(f"Error: {e}")
        apartments = []
        user = None
    finally:
        cursor.close()
        conn.close()

    context = {
        'user': user,
        'user_logged_in': True,
        'liked_properties': apartments,
    }

    return render(request, 'profile.html', context)
