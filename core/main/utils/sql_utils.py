import psycopg2
from django.http import JsonResponse
from sqlalchemy import text

from ...NextRoofWeb.settings.dev import db, get_db_engine


def get_streets_for_neighborhood(request):
    neighborhood = request.GET.get('neighborhood')
    engine = get_db_engine()
    query = text(
        "SELECT DISTINCT(street) FROM madlan_rank WHERE neighborhood = :neighborhood order by street"
    )
    with engine.connect() as connection:
        result = connection.execute(query, {'neighborhood': neighborhood})  #
        streets = [row[0] for row in result]
    streets.insert(0, 'בחר רחוב')

    return JsonResponse({'streets': streets})


def get_neighborhoods_for_city(request):
    city = request.GET.get('city')
    engine = get_db_engine()

    query = text(
        "SELECT DISTINCT(neighborhood) FROM madlan_rank WHERE city = :city order by neighborhood"
    )
    with engine.connect() as connection:
        result = connection.execute(query, {'city': city})
        neighborhoods = [row[0] for row in result]
    neighborhoods.insert(0, 'בחר שכונה')

    return JsonResponse({'neighborhoods': neighborhoods})


def get_streets_for_city(request):
    city = request.GET.get('city_calc')
    print(city)

    engine = get_db_engine()
    query = text(
        "SELECT DISTINCT(street) FROM nadlan_rank WHERE city = :city order by street"
    )
    with engine.connect() as connection:
        result = connection.execute(query, {'city': city})
        streets = [row[0] for row in result]
    return JsonResponse({'streets': streets})


def cities_list_query(table_name='madlan_rank'):
    engine = get_db_engine()
    query = text(f"SELECT DISTINCT(city) FROM {table_name} order by city")
    with engine.connect() as connection:
        result = connection.execute(query)
        cities = [row[0] for row in result]
    cities.insert(0, 'בחר עיר')
    return cities


def get_connection():
    return psycopg2.connect(host=db['default']['HOST'],
                            dbname=db['default']['NAME'],
                            user=db['default']['USER'],
                            password=db['default']['PASSWORD'],
                            port=db['default']['PORT'])


def find_item_id(item_id):
    conn = get_connection()
    cursor = conn.cursor()
    record_dict = {}

    try:
        query = "SELECT * FROM deals WHERE item_id = %s"
        cursor.execute(query, (item_id, ))
        record = cursor.fetchone()

        if record:
            columns = [col[0] for col in cursor.description]
            record_dict = dict(zip(columns, record))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

    return record_dict
