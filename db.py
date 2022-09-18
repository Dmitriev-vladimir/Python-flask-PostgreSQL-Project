from typing import List

import psycopg2
from psycopg2 import Error, sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.sql import Composed


def create_database():
    """
    Функция создает базу данных test_db
    :return:
    """
    with psycopg2.connect(host='127.0.0.1', user='postgres', password='0000') as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with connection.cursor() as cursor:
            try:
                print('Cursor is created', cursor)
                sql_create_database = 'CREATE DATABASE test_db'
                cursor.execute(sql_create_database)
                print('База данных test.db создана')
            except (Exception, Error) as error:
                print('Error in work with psql', error)


def create_sql_to_farm(farm_name: str) -> Composed:
    """
    :param farm_name: string, name of farm
    :return: Composed, request-string to database
    """
    machine = '{}_machine'.format(farm_name)
    volume = '{}_volume'.format(farm_name)
    return sql.SQL("""SELECT {machine}.date, type, number, area, volume from {machine} join {volume} on
                            {volume}.date = {machine}.date where {machine}.date between %s and %s""") \
        .format(
        volume=sql.Identifier(volume),
        machine=sql.Identifier(machine),
    )


def create_sql_all_farms(farms: List[str], min_date: str, max_date: str):
    """

    :param farms:
    :param min_date:
    :param max_date:
    :return:
    """
    with psycopg2.connect(host='127.0.0.1', user='postgres', password='0000', database="test_db") as connection:
        print('База данных подключена')
        temp_sql = create_sql_to_farm(farms[0])
        temp_dates = [min_date, max_date]

        if len(farms) > 1:
            for farm in farms[1:]:
                temp_sql = sql.SQL(' union ').join([temp_sql, create_sql_to_farm(farm)])
                temp_dates.append(min_date)
                temp_dates.append(max_date)

        with connection.cursor() as cursor:
            final_request = sql.SQL(' ').join([temp_sql, sql.SQL("ORDER BY date")])
            cursor.execute(final_request, temp_dates)
            result = cursor.fetchall()
            print('Работа с базой данных завершена. Данные успешно загружены')
            return result
