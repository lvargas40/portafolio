from flask import Flask, jsonify, abort, request, make_response, url_for, render_template
import json
import sys
import traceback
import time
import requests
from datetime import datetime, timedelta


app = Flask(__name__, static_url_path = "")

var = ['Nombre_activo', 'Precios']

@app.route("/")
def start_page():

    return render_template('index.html')


@app.route('/stock', methods = ['POST'])
def stock():

    for parameter in var:
        if not parameter in request.json:
            return jsonify({'error' : 'Dato no seleccionado: {}'.format(parameter) } ), 400

    stock = request.json['Nombre_activo']
    date   = request.json['Precios']


    try:
        dt = datetime.strptime(date, ("%Y-%m-%d"))
    except:
        return jsonify({ 'Error :' : 'La fecha debe ser AAAA-MM-DD' }), 400

    result, bRet = getStockValue(stock, dt)

    if False == bRet:
        return jsonify( { 'Nombre del activo': stock, 'Fechas': date,'Precio': result } ), 400

    return jsonify( { 'Nombre del activo': stock, 'Fechas': date,'Precio': result } )


def getStockValue(stock, dt):
    to_return = ""
    bRet = True
    _size = 'compact'


    if ( datetime.now() < dt ):
        print("Datos en el futuro")
        return "La fecha aun no ha llegado", False


    delta = datetime.now() - dt


    if delta > timedelta(days=100):
        print("Delta t es {}".format(delta))
        _size = 'full'


    try:
        start_time = time.monotonic()
        r = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={}&outputsize={}&apikey=OPVSB0L3RACDA2ZO&datatype=json".format(stock, _size))
        elapsed_time = time.monotonic() - start_time
        print("get_daily took {}s".format(elapsed_time))


        json_data = json.loads(r.text)

        meta_data = json_data["Meta Data"]
        data      = json_data["Time Series (Daily)"]


        date = dt.strftime("%Y-%m-%d")

        last_data_point = sorted(data, key=lambda  kv: kv[1])[-1]


        if ( dt < datetime.strptime(last_data_point, ("%Y-%m-%d")) ):
            to_return = "Sin datos en la fecha {}".format(last_data_point)
        else:
            while date not in data:
                print("Sin datos en la fecha {}".format(date))
                dt -= timedelta(days=1)
                date = dt.strftime("%Y-%m-%d")


            fValue = float(data[date]['4. close'])
            to_return = "{:.8f}".format(fValue)

    except:
        to_return = "No hay datos"
        bRet = False
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)

    return to_return, bret


if __name__ == '__main__':
    app.run(debug = True)
