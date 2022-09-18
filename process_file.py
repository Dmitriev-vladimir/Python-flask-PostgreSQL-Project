import csv
import os
import psycopg2
from openpyxl.workbook import Workbook
from psycopg2 import Error, sql
from os import path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def create_table_from_csv(file: path):
    """
    Функция считывает данные из файла "___.csv" и создает одноименную таблицу в базе данных

    :param file: path
    :return:
    """
    table_name = ''.join(file.split('.')[0]).split('/')[-1]

    if table_name.find('volume') != -1:
        sql_create_table = sql.SQL('''CREATE TABLE {name} (
            DATE DATE PRIMARY KEY,
            AREA INT NOT NULL,
            VOLUME INT NOT NULL
        );''').format(name=sql.Identifier(table_name))
    else:
        sql_create_table = sql.SQL("""CREATE TABLE {} (
            DATE DATE PRIMARY KEY,
            TYPE VARCHAR(10) NOT NULL,
            NUMBER VARCHAR(5) NOT NULL
        );""").format(sql.Identifier(table_name))

    with psycopg2.connect(host='127.0.0.1', user='postgres', password='0000', database="test_db") as connection:
        print('База данных успешно открыта')
        with connection.cursor() as cursor:
            try:
                cursor.execute(sql_create_table)
                print('Таблица {} успешно создана. Работа с базой данных завершена'.format(table_name))
            except (Exception, Error) as error:
                print('Error in work with PSQL (create table)', error)

    file_path = os.path.join(BASE_DIR, file)
    with open(file_path, encoding='utf-8', newline='') as file:
        reader = csv.reader(file)
        next(reader)
        with psycopg2.connect(host='127.0.0.1', user='postgres', password='0000', database="test_db") as connection:
            print('База данных успешно открыта для заполнения таблицы', table_name)
            with connection.cursor() as cursor:
                sql_fill_table = sql.SQL('INSERT INTO {} VALUES(%s, %s, %s)').format(sql.Identifier(table_name))
                try:
                    for line in reader:
                        print(line[0], line[1], line[2])
                        cursor.execute(sql_fill_table, line)
                        connection.commit()
                except (Exception, Error) as error:
                    print('Error in work with PSQL (fill table)', error)
                finally:
                    print('Таблица {} успешно заполнена. Работа с базой данных завершена'.format(table_name))


def download_report_to_xlsx(data: list[tuple], title: str, min_date: str, max_date: str):
    """
    Функция выгружает текущий отчет в файл <название хозяйства (или all)><начало периода><конец периода>.xlsx
    :param data:
    :param title:
    :param min_date:
    :param max_date:
    :return:
    """
    file_title = '{}_{}_{}.xlsx'.format(title, min_date, max_date)
    file = os.path.join(BASE_DIR, file_title)
    wb = Workbook()
    ws = wb.active

    ws.append(('Дата', 'Техника', 'Номер техники', 'Площадь, га', 'Объем работ, м3'))

    for row in data:
        ws.append(row)
    wb.save(file)
    print('Данные отчета успешно сохранены в файле {}'.format(file))
