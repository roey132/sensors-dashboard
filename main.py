# Import necessary libraries
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import requests
import json

# Initialize the Dash app
app = Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Live Sensor Data from Elasticsearch"),
    
    # Input field for the number of records to fetch
    html.Label("Number of Records to Fetch:"),
    dcc.Input(id='record-count', type='number', value=50, min=1, max=1000, step=1),
    
    # Graphs for each metric
    dcc.Graph(id='lux-graph'),
    dcc.Graph(id='hum-graph'),
    dcc.Graph(id='temp-graph'),
    dcc.Graph(id='uvs-graph'),
    dcc.Graph(id='pressure-graph'),

    # Interval component to update graphs every second
    dcc.Interval(id='interval-component', interval=1000, n_intervals=0)  # Update every second
])

# Define the callback to update all graphs
@app.callback(
    [Output('lux-graph', 'figure'),
     Output('hum-graph', 'figure'),
     Output('temp-graph', 'figure'),
     Output('uvs-graph', 'figure'),
     Output('pressure-graph', 'figure')],
    [Input('interval-component', 'n_intervals'), Input('record-count', 'value')]
)
def update_graphs(n_intervals, record_count):
    # Fetch data from Elasticsearch with the specified number of records
    es_url = 'http://localhost:9200/sensors/_search'
    query = {
        "query": {
            "match_all": {}
        },
        "sort": [{"timestamp": "desc"}],  # Assuming 'timestamp' is in your data
        "size": record_count  # Use the user-specified record count
    }
    
    # Request data from Elasticsearch
    response = requests.get(es_url, headers={"Content-Type": "application/json"}, data=json.dumps(query))
    data = response.json()

    # Initialize lists for each metric
    timestamps, lux_values, hum_values, temp_values, uvs_values, pressure_values = [], [], [], [], [], []

    # Process Elasticsearch response data
    for hit in data['hits']['hits']:
        source = hit['_source']
        timestamps.append(source['timestamp'])
        lux_values.append(source['lux'])
        hum_values.append(source['hum'])
        temp_values.append(source['temp'])
        uvs_values.append(source['uvs'])
        pressure_values.append(source['pressure'])

    # Define figures for each graph, setting Y-axis to start from 0
    lux_figure = go.Figure(
        data=[go.Scatter(x=timestamps, y=lux_values, mode='lines+markers')],
        layout=go.Layout(title='Lux Levels Over Time', xaxis=dict(title='Time'), yaxis=dict(title='Lux', range=[0, max(lux_values) * 1.1]))
    )
    
    hum_figure = go.Figure(
        data=[go.Scatter(x=timestamps, y=hum_values, mode='lines+markers')],
        layout=go.Layout(title='Humidity Levels Over Time', xaxis=dict(title='Time'), yaxis=dict(title='Humidity (%)', range=[0, max(hum_values) * 1.1]))
    )

    temp_figure = go.Figure(
        data=[go.Scatter(x=timestamps, y=temp_values, mode='lines+markers')],
        layout=go.Layout(title='Temperature Over Time', xaxis=dict(title='Time'), yaxis=dict(title='Temperature (°C)', range=[0, max(temp_values) * 1.1]))
    )

    uvs_figure = go.Figure(
        data=[go.Scatter(x=timestamps, y=uvs_values, mode='lines+markers')],
        layout=go.Layout(title='UV Levels Over Time', xaxis=dict(title='Time'), yaxis=dict(title='UV Index', range=[0, max(uvs_values) * 1.1]))
    )

    pressure_figure = go.Figure(
        data=[go.Scatter(x=timestamps, y=pressure_values, mode='lines+markers')],
        layout=go.Layout(title='Pressure Over Time', xaxis=dict(title='Time'), yaxis=dict(title='Pressure (hPa)', range=[0, max(pressure_values) * 1.1]))
    )

    return lux_figure, hum_figure, temp_figure, uvs_figure, pressure_figure

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
