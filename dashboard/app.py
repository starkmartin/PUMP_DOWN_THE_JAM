import dash
import os
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash import html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import pandas as pd
import plotly.io as pio
from simple_dwd_weatherforecast import dwdforecast
from datetime import datetime, timedelta, timezone, date
from dotenv import load_dotenv

pio.templates.default = "plotly_white"
external_stylesheets = [dbc.themes.SKETCHY]
colors = ["#f4b92c", #light_orange
          "#ba88ee", #light_purple
          "#898976", #warm_grey
          "#f1771c", #intense_orange
          "#7e2eeb", #intense_purple
          "#1dd5b3"] #teal


####### SECRET MAPBOX KEY
load_dotenv()
MAP_BOX_KEY = os.environ["MAP_BOX_KEY"]

################################################################################
# APP INITIALIZATION
################################################################################
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                meta_tags=[{'name': "viewport", "content": "width=device-width, initial-scale=1.0"}])

# this is needed by gunicorn command in procfile
server = app.server


################################################################################
# PLOTS
################################################################################
df_ = pd.read_pickle('./pred_station_date.pkl')


#### Organise labels for drop down

def get_stations(filename):
    df = pd.read_csv(filename)
    # list_station = 

    dict_list = []
    for i in zip(df.alias,df.station):
        dict_list.append({'label': i[0], 'value': i[1]})

    return dict_list


stations = get_stations('Dauerzaehlstellen_latlon.csv')
locations = pd.read_csv('Dauerzaehlstellen_latlon.csv')

def get_map_select(stelle,locations):
    
    map_ = go.Figure((go.Scattermapbox(
                        lon = locations['long'],
                        lat = locations['lat'],
                        text = locations['alias'],
                        mode = 'markers',
                        marker={'size': 12},
                        hoverinfo='text',
                        marker_color=colors[1])
                        ))
    
    if stelle:
        select_pnt = locations[locations.station == stelle]
        map_.add_traces((go.Scattermapbox(
                            lon = select_pnt.long,
                            lat = select_pnt.lat, 
                            marker_size=20, 
                            marker_color=colors[0],
                            hoverinfo='text')))
        
    map_.update_layout(
        margin={"r":10,"t":0,"l":10,"b":0}, 
        paper_bgcolor="rgb(0,0,0,0)",
        showlegend=False,
        mapbox_style="mapbox://styles/mapbox/light-v11",
        hovermode='closest',
        mapbox=dict(
            center=go.layout.mapbox.Center(lat=53.55,lon=10),
            zoom=9.5,
            accesstoken=MAP_BOX_KEY
            )
        )

    return map_



def get_figure(traces,stelle):
       min_day = min([min(trace.x) for trace in traces])
       max_day = max([max(trace.x) for trace in traces])
       min_day = shift_time_str(min_day,-1)
       max_day = shift_time_str(max_day,1)
       figure = go.Figure(data=traces,layout=go.Layout(
                #  colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                #  colorway=[colors[1],colors[0],colors[3]]
                #   template='plotly_dark',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  margin={'b': 15,'t': 2},
                  hovermode='closest',
                  clickmode="select",
                  autosize=True,
                  xaxis={'range': [min_day,max_day]},
              ))
       
       figure.update_xaxes(dtick="D1", tickformat="%a, %d %b")
       return figure

def shift_time_str(date_str,day_shift):
    return (pd.to_datetime(date_str) + pd.Timedelta(days=day_shift)).strftime('%Y-%m-%d')

def query_data(df_,stelle,mydate):
    df = df_[stelle].copy(deep=True)
    # date_past = shift_time_str(mydate,-7)
    # date_future = shift_time_str(mydate,1)
    df = df.query(f'day_predicted == "{mydate}"')
    return df
    

def get_traces(df_,stelle,mydate):
    df = query_data(df_,stelle,mydate)
   
    traces = []

    ## Past
    plt_data = df[df.ds < mydate ]
    traces.append(go.Scatter(x=plt_data.ds,
                                 y=plt_data.y,
                                 mode='lines',
                                 opacity=0.7,
                                 line=dict(
                                    color=colors[1],
                                    width=4),
                                 name='Past actual',
                                 textposition='bottom center'))

    traces.append(go.Scatter(x=plt_data.ds,
                                 y=plt_data.yhat,
                                 mode='lines',
                                line=dict(
                                    color=colors[0],
                                    width=4),
                                 opacity=0.7,
                                 name='Past model fit',
                                 textposition='bottom center'))
    
    ## Predictions
    plt_data = df[df.ds == mydate ]

    traces.append(go.Scatter(x=plt_data.ds,
                                 y=plt_data.yhat,
                                 mode='markers',
                                  marker=dict(
                                    color=colors[3],
                                    size=20),
                                 opacity=0.7,
                                 name='Prediction',
                                 textposition='bottom center'))

 
    return traces, df


figure_empty = {'layout': go.Layout(
                #  colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                #   template='plotly_dark',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  margin={'b': 15, 't': 2},
                  hovermode='x',
                  autosize=True,
                  xaxis={'range': ['2022-01-01','2022-12-31']},
              )}


map_empty = get_map_select(stelle=None, locations=locations)

def make_card(title,id_,body,style_add,image_add=None):
    style = {}
    style.update(style_add)
    if image_add is None:
        card_ = html.Div(id=id_, children=[
            dbc.Card(class_name='card text-center',children=[
            dbc.CardHeader(html.H3(title)),
            dbc.CardBody(children=body)
            ])], style=style)
    else:
        card_ = html.Div(id=id_, children=[
            dbc.Card(class_name='card text-center', children=[
            dbc.CardHeader(html.H3(title)),
            dbc.CardBody(children=[dbc.CardImg(src=image_add, style={'width': '45%'},
                        class_name='align-self-center'),] + body)
            ])], style=style)

    return card_

def make_indicator(value=100):
    fig=go.Figure(go.Indicator(
        mode="delta",
        value=value,
        delta={"reference": 100, "relative": True}))
    if value==100:
        fig.update_traces(delta_decreasing_color=colors[2], selector=dict(type='indicator'))
        fig.update_traces(delta_increasing_color=colors[2], selector=dict(type='indicator'))
    else:
        fig.update_traces(delta_decreasing_color=colors[5], selector=dict(type='indicator'))
        fig.update_traces(delta_increasing_color=colors[3], selector=dict(type='indicator'))
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=80)


    return fig




##### GET WEATHER ######
dwd_weather = dwdforecast.Weather("10147") # Station-ID for HH-Fuhlsbüttel
time_tomorrow = datetime.now(timezone.utc)+timedelta(days=1)
temperature_tomorrow = dwd_weather.get_forecast_data(dwdforecast.WeatherDataType.TEMPERATURE, time_tomorrow)
rain_tomorrow = dwd_weather.get_forecast_data(dwdforecast.WeatherDataType.PRECIPITATION, time_tomorrow)
sun_tomorrow = dwd_weather.get_forecast_data(dwdforecast.WeatherDataType.SUN_DURATION, time_tomorrow)
wind_tomorrow = dwd_weather.get_forecast_data(dwdforecast.WeatherDataType.WIND_SPEED, time_tomorrow)


string_temp = ('Temperature: ' + str(round(temperature_tomorrow - 273.51)) + ' \u00b0' + 'C')
string_rain = ('Rainfall: ' + str(rain_tomorrow) + ' mm')
string_sun = ('Sunshine: ' + str(round(sun_tomorrow/(60*60),1)) + ' hours')
string_wind = ('Windspeed: ' + str(round(wind_tomorrow)) + ' m/s')
 

################################################################################
# LAYOUT
################################################################################

app.layout = html.Div([

        html.Div(id='title', children=[
            html.Img(src="./assets/RGB_Jam_banner.png", style={'width': '80%', 'max-width': '600px'})], 
            style={'display':'flex','flex-flow':'row wrap','justify-content': 'center'}),
        html.Hr(style={'width':'95%','margin-left': 'auto', 'margin-right': 'auto'}),
        html.Br(),
        ### FIRST TOW
        html.Div(id="first-row", children=[
    
        dbc.Row([
    
        dbc.Col([ html.H4("To drive or not to drive?",),
            html.P("Welcome to Pump Down the Jam, a proof-of-concept for traffic prediction in Hamburg. We help you decide whether to \
               leave the car at home and skip the jam, based on tomorrow's traffic prediction and the weather forecast.\
               To get started, choose the traffic node that lies on your route.",
               ),
               html.H4("Proof of concept", style={'margin-left': 'auto', 'margin-right': '0'}),
            html.P("This is a demo of traffic prediction based on traffic data from 2012-2022, for which data was available from GeoPortal Hamburg. \
                   Once an automatic download of yesterday's traffic is available, we will be able to actually predict tomorrow's traffic. \
                    For the moment, can select a day in March 2022 for the prediction:",
               ),
            html.Div(dcc.DatePickerSingle(id='date-picker',
        min_date_allowed=date(2022, 3, 1),
        max_date_allowed=date(2022, 3, 31),
        initial_visible_month=date(2022, 3, 1),
        display_format='DD MMMM Y',
        date=date(2022, 3, 30))),
               ], width={"size": 11}, lg=2),#, "offset": 1
        dbc.Col([
        ####  Drop down and MAP #####
        make_card("1. Select the traffic hub", "map-card",style_add={'min-height': '200px'},body=[
            html.Div(id='map-parent',n_clicks=0, children=[     
                    dcc.Graph(id='map', figure=map_empty)], style={'min-width': '100px'}),
            html.Br(),
            html.Div(id='dropdown-parent', n_clicks=0,children=[
                dcc.Dropdown(id='dropdown-menu',
                            options=stations,
                            multi=False, style={'width': '98%'})
                            ]) #style={'display': 'flex', 'justify-content': 'center'}
                    ])], class_name='mb-3', width=11,lg=5),
        
        dbc.Col([
        ##### Card with indicator ########
        dbc.Row(make_card("2. Check the traffic tomorrow","indic_card", style_add={'width': '100%'},
                  body=[dcc.Graph(id='indicator', figure=make_indicator()),
                        html.P(id="indic-text",children="Select a station!",
                    className="card-text")
                    ]), class_name='mb-3'),
        ##### Card with weather #####
        dbc.Row(make_card("3. Check the weather tomorrow","weath_card", image_add='./assets/rainy.png', style_add={'width': '100%'},
                  body=[html.H5(string_temp,className="text-muted",style={'margin-top': '15px'}),
                        html.H5(string_rain,className="text-muted"),
                        html.H5(string_sun,className="text-muted"),
                        html.H5(string_wind,className="text-muted")
                    ]),  class_name='mb-3')
        ], width=11,lg=3), 
        ], justify="center")
                    ]),#,style={'display':'flex','flex-flow':'row wrap','justify-content': 'center'}),
        html.Hr(style={'width':'95%','margin-left': 'auto', 'margin-right': 'auto'}),
        html.H1('For Nerds',style={'display':'flex','flex-flow':'row wrap','justify-content': 'center'}),
        ###### Time series graph ######
        html.H4(id="time-title",children="Select a station!",style={'display':'flex','flex-flow':'row wrap','justify-content': 'center'}),
        html.Div(id="second-row",
                 children=[dbc.Row([ 
                                    dbc.Col([
                                        dcc.Graph(id='timeseries', figure=figure_empty)], 
                                            width=12, lg=10)
                                    ], justify="center")
                           ]
                 ),
        #Disclaimer
        html.Hr(),
        html.Div([html.P([html.H6("Credits",className="text-muted"),"Pump Up The Jam logo by Elise Hedemann. ",
                          "Raincloud icon created by ", 
                          html.A("bqlqn - Flaticon",
                                 href="https://www.flaticon.com/free-icons/rain"), 
                          ". Weather by @FL550 ", html.A("simple_dwd_weatherforecast.",
                                 href="https://github.com/FL550/simple_dwd_weatherforecast"),
                            
                     ],className="text-center")
                   ])
                   ])

################################################################################
# INTERACTION CALLBACKS
################################################################################

@app.callback([Output('timeseries', 'figure'),
               Output('map', 'figure'),
               Output('time-title', 'children'),
               Output('indicator','figure'),
               Output('indic-text','children')],
              [Input('dropdown-menu', 'value'),
              Input('date-picker', 'date')])

def update_from_dropdown(station_num,mydate):

    if (station_num is None):
        return figure_empty, map_empty, "Select a station", make_indicator(),""
    
    else:
        traces, df_stelle = get_traces(df_,station_num,mydate)
        figure_ = get_figure(traces,stelle=station_num)
        map_ = get_map_select(stelle=station_num,locations=locations)
        name_ = locations.alias[locations.station == station_num].values[0]
        title_ = f"Traffic prediction for {name_}"

        percent_ = round(df_stelle[df_stelle.ds == mydate].y_dif_mean.values[0]*100) + 100
        if percent_ == 100:
            text_indic_ = "Tomorrow, this location looks like it will have traffic similar to other\
                equivalent weekdays in the past year."
        elif percent_ > 100:
            text_indic_ = "Tomorrow, this location looks like it will have higher than average\
                traffic compared to equivalent weekdays in the past year"
        else:
            text_indic_ = "Tomorrow, this location looks like it will have lower than average\
                traffic compared to equivalent weekdays in the past year"

        indicator_ = make_indicator(percent_)
        return figure_, map_, title_, indicator_, text_indic_


@app.callback(Output('dropdown-menu', 'value'),
              [Input('map', 'clickData'),
              Input('map-parent','n_clicks')])

def set_dropdown_from_map(clickData,n_clicks):
    if clickData is None:
        raise dash.exceptions.PreventUpdate
        
    elif clickData['points'][0].get('text') is None:
        return None
        
    else:
        station_name = clickData['points'][0]['text']
        station_num = locations.station[locations.alias == station_name].values[0]

        return station_num


# Add the server clause:
if __name__ == "__main__":
    app.run_server()
