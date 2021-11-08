import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output
from functools import reduce

tabs_styles = {
    'height': '44px',
    'align-items': 'center'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold',
    'border-radius': '15px',
    'background-color': '#F2F2F2',
    'box-shadow': '4px 4px 4px 4px lightgrey',

}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px',
    'border-radius': '15px',
}

chunksize = 10000

corona = pd.read_csv('owid-covid-data.csv', chunksize=chunksize, iterator=True)

# corona = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv')
# corona = pd.read_csv('owid-covid-data.csv')

########################################################################################################################
#Filtering World Data

columns_2 = ['location', 'date','total_cases', 'new_cases', 'new_deaths', 'total_deaths']
df3 = corona.filter(items=columns_2)
world= df3[df3.location =='World']
world_= df3[df3.location =='World'].set_index('date')
########################################################################################################################
#Filtering Sri Lankan Data

sri_lanka = df3[df3.location=='Sri Lanka']
dummy = pd.DataFrame({'date': pd.date_range('2020-01-22', '2020-01-26', )}).astype(str)
sri_lanka = pd.concat([dummy, sri_lanka]).replace(np.nan, 0).set_index('date')
sri_lanka = sri_lanka.drop('location', axis=1)
sri_lanka.insert(0, 'location', ['Sri Lanka']*len(sri_lanka))

########################################################################################################################
#Filtering Rest of the World

Rest_of_the_World = world_.iloc[:, 1:] - sri_lanka.iloc[:, 1:]
Rest_of_the_World.insert(0, 'location', ['Rest_of_the_World']*len(Rest_of_the_World))

########################################################################################################################
#Filtering SAARK Data
saark_countries = ['Afghanistan', 'Bangladesh','Bhutan', 'India', 'Maldives', 'Nepal', 'Pakistan', 'Sri Lanka']
saark = df3[df3.location.isin(saark_countries)].groupby('date').sum()
saark.insert(0, 'location', ['SAARK']*len(saark))

########################################################################################################################
#Filtering ASIA Data

asia = corona[corona.location =='Asia'].loc[:, columns_2].set_index('date')

########################################################################################################################
#Concat R0W, SAAK, ASIA Data
concat_ = pd.concat([sri_lanka, Rest_of_the_World, saark, asia]).reset_index()
concat_.date = pd.to_datetime(concat_.date)
########################################################################################################################
#Test_to_detection

column_3 = ['date', 'location', 'new_tests', 'new_cases', 'total_tests']
t_D = corona.filter(items=column_3)
t_D['test_to_detection'] = t_D['new_tests']/t_D['new_cases']
t_D

########################################################################################################################
#Mapping the Spread of Coronavirus COVID-19

df_confirmed = pd.read_csv('C:/Users/MSI-Gaming/Desktop/HND/Data Visualization/IP/time_series_covid19_confirmed_global.csv')
df_deaths = pd.read_csv('C:/Users/MSI-Gaming/Desktop/HND/Data Visualization/IP/time_series_covid19_deaths_global.csv')
df_recovered = pd.read_csv('C:/Users/MSI-Gaming/Desktop/HND/Data Visualization/IP/time_series_covid19_recovered_global.csv')

id_list = df_confirmed.columns.to_list()[:4]
vars_list = df_confirmed.columns.to_list()[4:]

confirmed_tidy = pd.melt(df_confirmed, id_vars=id_list, value_vars=vars_list, var_name='Date', value_name='Confirmed')

deaths_tidy = pd.melt(df_deaths, id_vars=id_list, value_vars=vars_list, var_name='Date', value_name='Deaths')

recovered_tidy = pd.melt(df_recovered, id_vars=id_list, value_vars=vars_list, var_name='Date', value_name='recovered')

# 1.3 Merging the three dataframes into one
data_frames = [confirmed_tidy, deaths_tidy, recovered_tidy]
df_corona = reduce(lambda left, right: pd.merge(left, right, on = id_list+['Date'], how='outer'), data_frames)

# 1.4 Each row should only represent one observation
id_vars = df_corona.columns[:5]
data_type = ['Confirmed', 'Deaths', 'recovered']
df_corona = pd.melt(df_corona, id_vars=id_vars, value_vars=data_type, var_name='type', value_name='Count')
df_corona['Date'] = pd.to_datetime(df_corona['Date'],format='%m/%d/%y', errors='raise')
corona_sums = df_corona.groupby(['type', 'Date'], as_index=False).agg({'Count':'sum'})

tsmap_corona = df_corona[df_corona['type']=='Confirmed']
tsmap_corona['Date'] = tsmap_corona['Date'].astype(str)
to_Category = pd.cut(tsmap_corona['Count'], [-1,0,105, 361, 760,\
            1350, 6280, 200000], labels=[0, 1, 8, 25, 40, 60, 100])
tsmap_corona = tsmap_corona.assign(size=to_Category)
tsmap_corona['size'] = tsmap_corona['size'].fillna(0)

fig_time= px.scatter_mapbox(data_frame=tsmap_corona,lat='Lat',lon='Long',
                            hover_name= 'Country/Region', hover_data=['Province/State',
                                                                      'Count'], size='size', animation_frame='Date',
                            mapbox_style='stamen-toner', template='plotly_dark', zoom=1,
                            size_max=70)
#######################################################################################################################
columns_4 = ['location', 'date','total_cases', 'new_cases', 'new_deaths', 'total_deaths', 'people_fully_vaccinated', 'population',
             'hosp_patients', 'total_deaths_per_million', 'positive_rate']
col_5 = ['date', 'total_cases', 'new_cases','total_deaths_per_million', 'positive_rate']

df_5 = corona.filter(items=columns_4)
df_5 = df_5[df_5.location=='Sri Lanka']

########################################################################################################################

app = dash.Dash(__name__)

app.config['suppress_callback_exceptions'] = True

app.layout = html.Div([

    html.Div([
        html.Div([
            html.Div([
                html.H1('Covid-19(Coronavirus) Situation Dashboard'),
                html.H3('Date update as of : ' +df3.date.max())
            ],style={'margin-bottom': '12px', 'color': 'black', "border":"2px black solid"})
        ], className="create_container1 four columns", id="title"),

    ], id="header", className="row flex-display", style={"margin-bottom": "25px"}),

    html.Div([

        html.Div([
            html.Div([
                dcc.Tabs(id="tabs-styled-with-inline", value='tab-1', children=[
                    dcc.Tab(label='Current Status', value='tab-1', style=tab_style, selected_style=tab_selected_style),
                    dcc.Tab(label='Sri Lanka Covid(19)  Status', value='tab-2', style=tab_style, selected_style=tab_selected_style),
                ], style=tabs_styles),
                html.Div(id='tabs-content-inline')
            ], className="create_container3 eight columns", ),
        ], className="row flex-display"),

        html.Br()])])


@app.callback(Output('tabs-content-inline', 'children'),
              Input('tabs-styled-with-inline', 'value'))

def update_tab(tab):

    if tab == 'tab-1':
        return html.Div([
            html.Div([
                dcc.Graph(id='map', figure=fig_time)
            ]),
            html.Br(),
            html.Div([
                html.Div([
                    dcc.Dropdown(id='q2-variable-dropdown',
                                 options=[{'label': i.replace('_', ' '), 'value': i} for i in columns_2[2:]],
                                 value='total_cases')], style={'width': '40%', 'display': 'inline-block'}),

                html.Div([
                    dcc.Dropdown(id='q2-aggregate-dropdown',
                                 options=[{'label': i, 'value': i} for i in
                                          ['Daily', 'Weekly Average', 'Monthly Average', '7-day average', '14-day average']],
                                 value='Daily')], style={'width': '40%', 'display': 'inline-block'}),

                html.Div([
                    dcc.DatePickerRange(id='q2-datepickerrange',
                                        start_date=df3.date.min(),
                                        end_date=df3.date.max())],style={'width': '48%', 'display': 'block'}),

                html.Br(),
                html.Div([
                    dcc.Checklist(id='q2-checklist',
                                  options=[{'label': i, 'value': i} for i in ['Rest_of_the_World', 'Asia', 'SAARK']],
                                  value=['Rest_of_the_World'],labelStyle={'display': 'block'})]),

                dcc.Graph(id='q2-graph', figure={})], style={ 'display': 'block'}),

        # question 2
            html.Div([
                html.Div([
                    html.Div([
                        html.H2("Worldwide Changes with Covid(19) Cases"),
                        dcc.Dropdown(id='q1-dropdown',
                                     options=[{'label': i.replace('_', ' '), 'value': i} for i in columns_2[2:]],
                                     value='total_cases')], style={'width': '65%', 'display': 'block'}),


                    html.Div([
                    dcc.DatePickerRange(id='q1-datepickerrange',
                                        start_date=world.date.min(),
                                        end_date=world.date.max())],style={'width': '49%', 'display': 'block'}),

                    dcc.Graph(id='q1-graph', figure={})], style={'width': '48%', 'display': 'inline-block'}),



    # question 3
                html.Div([
                        html.H2("Daily Test Detection Ratio"),
                        html.Div([
                            dcc.Dropdown(id='location',
                                         options=[{'label': i, 'value': i} for i in t_D.location.unique()],
                                         value='Sri Lanka')],style={'width': '65%', 'display': 'inline-block'}),
                        html.Div([
                            dcc.DatePickerRange(id='q3-datepickerrange',
                                                start_date=t_D.date.min(),
                                                end_date=t_D.date.max())],style={'width': '48%', 'display': 'block'}),
                        dcc.Graph(id='q3-graph', figure={})], style={'width': '48%', 'display': 'inline-block'})]),


            html.Div([
                html.H2("Relationship Between Tests and New cases in Sri Lanka"),
                html.Div([
                    dcc.DatePickerRange(id='q4-datepickerrange',
                                        start_date=t_D.date.min(),
                                        end_date=t_D.date.max())], style={'width': '48%', 'display': 'block'}),
                dcc.Graph(id= 'q4-graph', figure={})
            ])

        ])
    elif tab == 'tab-2':
        return html.Div([
                html.Div([
                    dcc.Dropdown(id='q5-variable-dropdown',
                                 options=[{'label': i.replace('_', ' '), 'value': i} for i in col_5[1:]],
                                 value='total_cases')], style={'width': '40%', 'display': 'inline-block'}),
                    dcc.Graph(id='q5-graph',
                              figure={})
            ])


@app.callback(Output('q2-graph', 'figure'),
              Input('q2-variable-dropdown', 'value'),
              Input('q2-datepickerrange', 'start_date'),
              Input('q2-datepickerrange', 'end_date'),
              Input('q2-checklist', 'value'),
              Input('q2-aggregate-dropdown', 'value'))
def update_q2_fig(variable, start_date, end_date, checklist, frequency):
    #print(variable, start_date, end_date, checklist, frequency)
    dates_filtered = concat_[(concat_.date >= start_date) & (concat_.date <= end_date)]
    checklist.append('Sri Lanka')
    location_filtered = dates_filtered[dates_filtered.location.isin(checklist)]

    if frequency == 'Daily':
        title = f"<b>{frequency} changes in {variable.replace('_', ' ')}</b>"
        df = location_filtered
    elif frequency == 'Weekly Average':
        title = f"<b>{frequency} changes in {variable.replace('_', ' ')}</b>"
        df = location_filtered.groupby([pd.Grouper(key='date', freq='W'), 'location'], ).mean().reset_index()
    elif frequency == 'Monthly Average':
        title = f"<b>{frequency} changes in {variable.replace('_', ' ')}</b>"
        df = location_filtered.groupby([pd.Grouper(key='date', freq='M'), 'location'], ).mean().reset_index()
    elif frequency == '7-day average':
        title = f"<b>{frequency} changes in {variable.replace('_', ' ')}</b>"
        df = location_filtered.groupby('location').rolling(7, on='date').mean().reset_index()
    elif frequency == '14-day average':
        title = f"<b>{frequency} changes in {variable.replace('_', ' ')}</b>"
        df = location_filtered.groupby('location').rolling(14, on='date').mean().reset_index()

    fig = px.line(data_frame=df,
                  x='date',
                  y=variable,  # filter by vraible of interest,
                  color='location',
                  title=title)
    fig.layout.title.x = 0.5
    fig.update_layout(xaxis_title='<b>Date</b>',
                     yaxis_title=f'<b>{variable.replace("_", " ")}</b>')
    return fig

@app.callback(Output('q1-graph', 'figure'),
              Input('q1-dropdown', 'value'),
              Input('q1-datepickerrange', 'start_date'),
              Input('q1-datepickerrange', 'end_date'))
def update_q1_fig(variable, start, end):
    fig = px.line(data_frame=world[(world.date >= start) & (world.date <= end)],
                  x='date',
                  y=variable)
    fig.update_xaxes(title='Date')
    fig.update_yaxes(title=variable)
    fig.update_layout(height=370, margin={'l': 20, 'b': 30, 'r': 10, 't': 10})

    return fig


@app.callback(Output('q3-graph', 'figure'),
             Input('location', 'value'),
             Input('q3-datepickerrange', 'start_date'),
             Input('q3-datepickerrange', 'end_date'))
def update_q3_fig(location, start, end):
    df = t_D[(t_D.location == location) & (t_D.date >= start) & (t_D.date <= end)]
    fig = px.line(df,
                  x='date',
                  y='test_to_detection')
    fig.update_xaxes(title='Date')
    fig.update_yaxes(title='Test to Detection')
    fig.update_layout(height=370, margin={'l': 20, 'b': 30, 'r': 10, 't': 10})

    return fig

@app.callback(Output('q4-graph', 'figure'),
             Input('q4-datepickerrange', 'start_date'),
             Input('q4-datepickerrange', 'end_date'))
def update_q3_fig(start, end):
    df = t_D[(t_D.location == 'Sri Lanka') & (t_D.date >= start) & (t_D.date <= end)]
    cor = round(df[['new_tests', 'new_cases']].corr()['new_cases'][0], 2)
    fig = px.scatter(df,
                  x='total_tests',
                  y='new_cases')
    fig.update_layout(height=370, margin={'l': 20, 'b': 30, 'r': 10, 't': 10})

    fig.add_annotation(x=0, y=max(df['new_cases']),
            text= "Correlation: {}".format(cor),
            font=dict(
            family="Courier New, monospace",
            size=25,
            color="#ff7f0e"
            ),
            showarrow=False,
            arrowhead=1)
    return fig

@app.callback(Output('q5-graph', 'figure'),
              Input('q5-variable-dropdown', 'value'))
def update_q1_fig(variable):
    fig = px.line(data_frame=df_5,
                  x='date',
                  y=variable)
    fig.update_xaxes(title='Date')
    fig.update_yaxes(title=variable)
    fig.update_layout(height=350, margin={'l': 20, 'b': 30, 'r': 0, 't': 10})

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)