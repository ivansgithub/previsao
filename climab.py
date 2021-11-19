import dash
from dash.dependencies import Input, Output,State
import dash_core_components as dcc
import dash_html_components as html
import requests
import json
import datetime, pytz
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px
from flask import request



#ip_address = request.headers['X-Real-IP']


FONT_AWESOME = "https://use.fontawesome.com/releases/v5.7.2/css/all.css"
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.LUX,FONT_AWESOME],meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],)



temperatura =    ['Temp. atual (°C)','Temp. máx (°C)', 'Temp. mín (°C)','Chuva(%)','Umidade(%)','Vento(m/s)']

horas=['3h', '6h', '9h','12h','24h','48h']




app.layout = html.Div([

    html.Div(className='mb-4'),

    html.Div(
    dbc.Row(dbc.Col(
    dcc.Dropdown(
        id='countries-dropdown',

        options=[{'label': k, 'value': k} for k in horas],
        value='24h',
        clearable=False,style={
                    'color': '#565555',
                    'borderStyle':'solid',
                    # 'width': '50%',
                    'font-size': '15px',
                    'textAlign': 'center'}),
    width=6,md={'size':4,'offset':4},xs={'size':8,'offset':2}),className='mb-4',),),



    html.Div(
    dbc.Row(dbc.Col(
    dcc.Dropdown(
        id='cities-dropdown',clearable=False, style={
                    'color': '#565555',
                    'borderStyle':'solid',
                    # 'width': '50%',
                    'font-size': '15px',
                    'textAlign': 'center'}  ),
    width=6,md={'size':4,'offset':4},xs={'size':8,'offset':2}),className='mb-4',),),



    dbc.Row(dbc.Col(html.Div(id='display-selected-values', className="text-center",style={
                    'color': '#565555',
                    'font-size': '30px',
                    'font': 'sans-serif',
                    'font-weight': 'bolder',
                    } ),),),

    dcc.Store(id='display-selected-values2'),

    dcc.Store(id='storage2'),

    dcc.Store(id='storage3'),



]
)



@app.callback(Output('display-selected-values2', 'data'), [Input('countries-dropdown', 'value')])
def get_ip(value):
    return dcc.Store(request.headers['X-Forwarded-For'])


@app.callback(Output('storage2','data'),[Input('display-selected-values2','data')])
def llamada_api(value2):

    ip_addresss=value2['props']['id']


    GEO_IP_API_URL  = 'http://ip-api.com/json/'


    IP_TO_SEARCH    = ip_addresss


    req             = requests.get(GEO_IP_API_URL+IP_TO_SEARCH)

    json_response   = json.loads(req.text)


    lat=(json_response['lat'])
    lon=(json_response['lon'])

    r=requests.get('https://api.openweathermap.org/data/2.5/onecall?lat='+str(lat)+'&lon='+str(lon)+'&lang=pt_br'+'&appid=029e4d13d05bab8a91e8fbe876e20239&units=metric')

    weather_data = r.json()


    tz = pytz.timezone('America/Sao_Paulo')

    dates=[]
    temp=[]
    rain=[]
    wind_speed=[]
    humidity=[]

    for i in weather_data['hourly']:
        local_time = datetime.datetime.fromtimestamp(i['dt'],tz=tz)
        str_time = local_time.strftime( '%H:%M %m-%d' )
        dates.append(str_time)
        temp.append(i['temp'])
        try:
            rain.append(i['rain'])
        except:
            rain.append(0)
        wind_speed.append(i['wind_speed'])
        humidity.append(i['humidity'])


    dates_d=[]
    max_d=[]
    min_d=[]
    temp_d=[]
    rain_d=[]
    wind_speed_d=[]
    humidity_d=[]
    for i in weather_data['daily']:
        local_time = datetime.datetime.fromtimestamp(i['dt'],tz=tz)
        str_time = local_time.strftime( '%H:%M %m-%d' )
        dates_d.append(str_time)
        max_d.append(i['temp']['max'])
        min_d.append(i['temp']['min'])
        temp_d.append(i['temp']['day'])
        try:
            rain_d.append(i['rain'])
        except:
            rain_d.append(0)
        wind_speed_d.append(i['wind_speed'])
        humidity_d.append(i['humidity'])


    L = [list(row) for row in zip(dates, temp, rain,wind_speed,humidity,dates_d,max_d,min_d,temp_d,rain_d,wind_speed_d,humidity_d)]

    dfv = pd.DataFrame(L, columns=['dates', 'temp', 'rain','wind_speed','humidity','dates_d','max_d','min_d','temp_d','rain_d','wind_speed_d','humidity_d'])


    #{'hour_dates': dates,
     #'temp': temp,
     #'rain': rain,
     #'wind+speed':wind_speed,
     #'humidity':humidity,
     #'dates_d':dates_d,
     #'max_d':max_d,
     #'min-d':min_d,
     #'temp_d':temp_d,
     #'rain_d':rain_d,
     #'wind_speed_d':wind_speed_d,
     #'humidity_d':humidity_d

    #},orient='index').T


    return dfv.to_json(date_format='iso', orient='split')





@app.callback(
    dash.dependencies.Output('cities-dropdown', 'options'),
    [dash.dependencies.Input('countries-dropdown', 'value')])
def set_cities_options(selected_country):
    return [{'label': i, 'value': i} for i in temperatura]

@app.callback(
    dash.dependencies.Output('cities-dropdown', 'value'),
    [dash.dependencies.Input('cities-dropdown', 'options')])
def set_cities_value(available_options):
    return available_options[0]['value']

@app.callback(
    dash.dependencies.Output('display-selected-values', 'children'),
    [dash.dependencies.Input('countries-dropdown', 'value'),
     dash.dependencies.Input('cities-dropdown', 'value'),
     Input('storage2','data')])
def set_display_children(selected_country, selected_city,df_del_json):

    data=json.loads(df_del_json)


    columns = data['columns']
    data_dentro=data['data']


    df = pd.DataFrame(data_dentro, columns = columns)

    if selected_country == '3h' and selected_city=='Temp. atual (°C)' :
        final=str(df['temp'].iloc[2])+'°C'
    elif selected_country=='6h' and selected_city=='Temp. atual (°C)':
        final=str(df['temp'].iloc[5])+'°C'
    elif selected_country=='9h' and selected_city=='Temp. atual (°C)':
        final=str(df['temp'].iloc[8])+'°C'
    elif selected_country=='12h' and selected_city=='Temp. atual (°C)':
        final=str(df['temp'].iloc[11])+'°C'
    elif selected_country=='24h' and selected_city=='Temp. atual (°C)':
        final=str(df['temp_d'].iloc[0])+'°C'
    elif selected_country=='48h' and selected_city=='Temp. atual (°C)':
        final=str(df['temp'].iloc[1])+'°C'
    elif selected_country=='3h' and selected_city=='Chuva(%)':
        final=str(df['rain'].iloc[2])+'%'
    elif selected_country=='6h' and selected_city=='Chuva(%)':
        final=str(df['rain'].iloc[5])+'%'
    elif selected_country=='9h' and selected_city=='Chuva(%)':
        final=str(df['rain'].iloc[8])+'%'
    elif selected_country=='12h' and selected_city=='Chuva(%)':
        final=str(df['rain'].iloc[11])+'%'
    elif selected_country=='24h' and selected_city=='Chuva(%)':
        final=str(df['rain_d'].iloc[0])+'%'
    elif selected_country=='48h' and selected_city=='Chuva(%)':
        final=str(df['rain_d'].iloc[1])+'%'
    elif selected_country=='3h' and selected_city=='Umidade(%)':
        final=str(df['humidity'].iloc[2])+'%'
    elif selected_country=='6h' and selected_city=='Umidade(%)':
        final=str(df['humidity'].iloc[5])+'%'
    elif selected_country=='9h' and selected_city=='Umidade(%)':
        final=str(df['humidity'].iloc[8])+'%'
    elif selected_country=='12h' and selected_city=='Umidade(%)':
        final=str(df['humidity'].iloc[11])+'%'
    elif selected_country=='24h' and selected_city=='Umidade(%)':
        final=str(df['humidity_d'].iloc[0])+'%'
    elif selected_country=='48h' and selected_city=='Umidade(%)':
        final=str(df['humidity_d'].iloc[1])+'%'
    elif selected_country=='3h' and selected_city=='Vento(m/s)':
        final=str(df['wind_speed'].iloc[2])+'m/s'
    elif selected_country=='6h' and selected_city=='Vento(m/s)':
        final=str(df['wind_speed'].iloc[5])+'m/s'
    elif selected_country=='9h' and selected_city=='Vento(m/s)':
        final=str(df['wind_speed'].iloc[8])+'m/s'
    elif selected_country=='12h' and selected_city=='Vento(m/s)':
        final=str(df['wind_speed'].iloc[11])+'m/s'
    elif selected_country=='24h' and selected_city=='Vento(m/s)':
        final=str(df['wind_speed_d'].iloc[0])+'m/s'
    elif selected_country=='48h' and selected_city=='Vento(m/s)':
        final=str(df['wind_speed_d'].iloc[1])+'m/s'
    elif selected_country=='3h' and selected_city=='Temp. máx (°C)':
        final='no data'
    elif selected_country=='6h' and selected_city=='Temp. máx (°C)':
        final='no data'
    elif selected_country=='9h' and selected_city=='Temp. máx (°C)':
        final='no data'
    elif selected_country=='12h' and selected_city=='Temp. máx (°C)':
        final='no data'
    elif selected_country=='24h' and selected_city=='Temp. máx (°C)':
        final=str(df['max_d'].iloc[0])+'°C'
    elif selected_country=='48h' and selected_city=='Temp. máx (°C)':
        final=str(df['max_d'].iloc[1])+'°C'
    elif selected_country=='3h' and selected_city=='Temp. mín (°C)':
        final='no data'
    elif selected_country=='6h' and selected_city=='Temp. mín (°C)':
        final='no data'
    elif selected_country=='9h' and selected_city=='Temp. mín (°C)':
        final='no data'
    elif selected_country=='12h' and selected_city=='Temp. mín (°C)':
        final='no data'
    elif selected_country=='24h' and selected_city=='Temp. mín (°C)':
        final=str(df['min_d'].iloc[0])+'°C'
    elif selected_country=='48h' and selected_city=='Temp. mín (°C)':
        final=str(df['min_d'].iloc[1])+'°C'





    return final



if __name__ == '__main__':
    app.run_server(debug=False)