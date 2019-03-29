import json
from botocore.vendored import requests
from datetime import datetime, timedelta

var = ['Nombre_activo', 'Precios']


API_TOKEN = "OPVSB0L3RACDA2ZO"
FUNCTION = "TIME_SERIES_DAILY_ADJUSTED"

def lambda_handler(event, context):
    print("Evento recibido: " + json.dumps(event, indent=2))

    for parameter in var:
        if not parameter in event:
            return 'Dato no seleccionado: {}'.format(parameter)

    stock  = event['Nombre_activo']
    date   = event['Precios']

    try:
        dt = datetime.strptime(date, ("%Y-%m-%d"))
    except:
        return { 'Error:' : 'La estructura de fecha es AAAA-MM-DD' }

    resultado, bret = getStockValue(stock, dt)

    return { 'Nombre del activo': stock, 'Fecha': date, 'Precio': resultado }


def getStockValue(stock, dt):
    to_return = ""
    bret = True
    _size = 'compact'


    if ( datetime.now() < dt ):
        return "La fecha aun no ha llegado", False


    deltat = datetime.now() - dt

    if deltat > timedelta(days=100):
        _size = 'full'


    try:
        r = requests.get("https://www.alphavantage.co/query?function={}&symbol={}&outputsize={}&apikey={}&datatype=json".format(FUNCTION, stock, _size, API_TOKEN))

        json_data = json.loads(r.text)

        meta_data = json_data["Meta Data"]
        data      = json_data["Time Series (Daily)"]

        date = dt.strftime("%Y-%m-%d")

        last_data_point = sorted(data, key=lambda  kv: kv[1])[-1]


        if ( dt < datetime.strptime(last_data_point, ("%Y-%m-%d")) ):
            to_return = "Sin datos en la fecha{}".format(last_data_point)
        else:
            while date not in data:
                dt -= timedelta(days=1)
                date = dt.strftime("%Y-%m-%d")


            fValue = float(data[date]['4. close'])
            to_return = "{:.8f}".format(fValue)

    except:
        to_return = "No existen datos del activo"
        bret = False

    return to_return, bret
