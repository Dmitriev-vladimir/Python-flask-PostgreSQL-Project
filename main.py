from flask import Flask, render_template, url_for, redirect, request
import db
import process_file
from config import files, farms, min_date_start, max_date_start

app = Flask(__name__)

IS_LOAD = True
"параметр, определяющий необходимость создания базы данных и таблиц в ней"


@app.route('/index')
@app.route('/')
def index():
    if len(farm_list) > 1:
        _farm = 'all'
    else:
        _farm = farm_list[0]

    global app_data
    app_data = [x for x in db.create_sql_all_farms(farm_list, min_date, max_date)]
    return render_template('index.html', data=app_data, min=min_date, max=max_date, farm=_farm)


@app.route('/get_view', methods=['POST'])
def get_view():
    global min_date, max_date, farm_list
    min_date = request.form.get('min_date')
    max_date = request.form.get('max_date')
    request_farm = request.form.get('farm')
    if request_farm == 'all':
        farm_list = farms
    else:
        farm_list = [request_farm]
    return redirect(url_for('.index'))


@app.route('/download_report')
def download_report():
    global app_data, min_date, max_date
    print('Download report', app_data)
    if len(farm_list) > 1:
        title = 'all'
    else:
        title = farm_list[0]
    process_file.download_report_to_xlsx(app_data, title, min_date, max_date)
    return redirect(url_for('.index'))


def load_data():
    """
    Функция итерирования списка файлов для перевода данных из них в таблицы базы данных
    """
    for file in files:
        process_file.create_table_from_csv(file)


if __name__ == '__main__':
    if IS_LOAD:
        db.create_database()
        load_data()
    min_date = min_date_start
    max_date = max_date_start
    farm_list = farms
    app_data = []
    app.run('localhost', 5000, debug=True)
