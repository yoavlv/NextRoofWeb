from django.shortcuts import redirect, render

from ..utils.sql_utils import get_connection
from ..utils.user_utils import get_user_details


def create_post(request):
    if not hasattr(
            request,
            'user_id'):  # We're checking for user_id now, not user_name.
        return render(request, 'error.html',
                      {'message': 'Please login to view this page.'})

    user = get_user_details(request.user_id)
    #
    # neighborhoods = create_list(col = 'neighborhood' ,table='nadlan')
    # streets = create_list(col = 'street' ,table='nadlan')

    if request.method == 'POST':
        # Gather data from POST request
        city = request.POST.get('city')
        neighborhood = request.POST.get('neighborhood')
        street = request.POST.get('street')
        asset_type = request.POST.get('type')
        price = request.POST.get('price')
        floor = request.POST.get('floor')
        size = request.POST.get('size')
        rooms = request.POST.get('rooms')
        new = request.POST.get('condition')
        entry_date = request.POST.get('entry_date')
        storage = request.POST.get('storage') == 'on'  # Convert to boolean
        elevators = request.POST.get('elevators') == 'on'  # Convert to boolean
        parking = request.POST.get('parking')
        floors = request.POST.get('floors')
        # Assuming the next fields are checkboxes:
        protected = request.POST.get('protected') == 'on'  # Convert to boolean
        furniture = request.POST.get('furniture') == 'on'  # Convert to boolean
        balcony = request.POST.get('balcony') == 'on'  # Convert to boolean
        accessibility = request.POST.get(
            'accessibility') == 'on'  # Convert to boolean
        renovated_checkbox = request.POST.get(
            'renovated') == 'on'  # Convert to boolean
        text = request.POST.get('text')
        property_image = request.FILES.get('property_image', None)
        # Create new property listing

        record = (city, neighborhood, street, asset_type, price, floor, size,
                  rooms, new, entry_date, storage, elevators, parking, floors,
                  protected, furniture, balcony, accessibility,
                  renovated_checkbox, text, property_image)
        item_id = insert_into_database(record)
        if item_id:
            # Insert the user_id and item_id into the user_posts table
            associate_user_with_post(request.user_id, item_id)
        return redirect(
            'home'
        )  # replace 'success_page' with the name of your desired redirect view

    # return render(request, "post.html", {'neighborhoods':neighborhoods ,'streets':streets , 'user':user})
    return render(request, "post.html", {'user': user})


def associate_user_with_post(user_id, item_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO user_posts (user_id, item_id)
            VALUES (%s, %s)
        """

        cursor.execute(query, (user_id, item_id))
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def insert_into_database(record):
    conn = get_connection()
    cursor = conn.cursor()
    item_id = None
    try:
        cursor = conn.cursor()
        query = """
                INSERT INTO deals (city, neighborhood, street, asset_type, price, floor, size, rooms, new, entry_date,
                storage, elevators, parking, floors, protected_space, furniture, balcony,
                accessibility, renovated, description, images)
                VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING item_id
            """
        cursor.execute(query, record)
        item_id = cursor.fetchone()[
            0]  # Get the returned item_id from the database
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    return item_id  # Return the ID of the newly created post
