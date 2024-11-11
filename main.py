# Import necessary libraries
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import requests
import json
import dash
# Initialize the Dash app
app = Dash(__name__)

# Define the layout of the app with a subtle grayish dark theme
# Initialize the Dash app with meta tags for mobile responsiveness
app = Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])

# Initialize the Dash app
app = Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])

# Define the layout of the app with a subtle grayish dark theme and page-wide background styling
app.layout = html.Div(
    style={'backgroundColor': '#1e1e1e', 'color': '#b0e0e6', 'fontFamily': 'Arial', 'height': '100vh'},
    children=[
        # Custom CSS for setting the full page background color
        dcc.Markdown('''<style>body { background-color: #1e1e1e; margin: 0; }</style>''', dangerously_allow_html=True),
        
        html.H1("Live Sensor Data from Elasticsearch", style={'textAlign': 'center'}),
        
        # Input field for the number of records to fetch
        html.Div([
            html.Label("Number of Records to Fetch:", style={'marginRight': '10px'}),
            dcc.Input(id='record-count', type='number', value=50, min=1, max=1000, step=1),
        ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'padding': '10px'}),

        # Toggle switch for live data reading on/off
        html.Div([
            html.Label("Live Data:", style={'marginRight': '10px'}),
            dcc.Checklist(
                id='live-toggle',
                options=[{'label': 'On/Off', 'value': 'on'}],
                value=['on'],  # Default to live data on
                inline=True,
                style={'color': '#b0e0e6'}
            ),
        ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'padding': '10px'}),
        
        # Graphs in a 3x1 grid on the top row and 2x1 grid on the bottom row
        html.Div([
            # Top row (3x1 grid)
            html.Div([
                dcc.Graph(id='lux-graph', style={'height': '30vh'}),
                dcc.Graph(id='hum-graph', style={'height': '30vh'}),
                dcc.Graph(id='temp-graph', style={'height': '30vh'}),
            ], style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr 1fr', 'gap': '10px'}),

            # Bottom row (2x1 grid)
            html.Div([
                dcc.Graph(id='uvs-graph', style={'height': '30vh'}),
                dcc.Graph(id='pressure-graph', style={'height': '30vh'}),
            ], style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '10px'}),
        ], style={'padding': '10px'}),

        # Interval component to update graphs every second
        dcc.Interval(id='interval-component', interval=1000, n_intervals=0)  # Update every second
    ]
)

# Define the callback to update all graphs
@app.callback(
    [Output('lux-graph', 'figure'),
     Output('hum-graph', 'figure'),
     Output('temp-graph', 'figure'),
     Output('uvs-graph', 'figure'),
     Output('pressure-graph', 'figure'),
     Output('interval-component', 'disabled')],
    [Input('interval-component', 'n_intervals'), 
     Input('record-count', 'value'),
     Input('live-toggle', 'value')]
)
def update_graphs(n_intervals, record_count, live_toggle):
    # Disable interval component if live data toggle is off
    interval_disabled = 'on' not in live_toggle

    # Fetch data only if live data is on
    if interval_disabled:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, interval_disabled

    # Fetch data from Elasticsearch with the specified number of records
    es_url = 'http://localhost:9200/sensors/_search'
    query = {
        "query": {
            "match_all": {}
        },
        "sort": [{"timestamp": "desc"}],
        "size": record_count
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

    # Define figures for each graph with grayish dark theme and cyan accents
    # Define figures for each graph with grayish dark theme and neon colors
    lux_figure = go.Figure(
        data=[go.Scatter(x=timestamps, y=lux_values, mode='lines+markers', marker=dict(color='#00ffff'))],
        layout=go.Layout(
            title='Lux Levels Over Time', xaxis=dict(title='Time', color='#00ffff'), yaxis=dict(title='Lux', color='#00ffff'),
            plot_bgcolor='#2b2b2b', paper_bgcolor='#1e1e1e', font=dict(color='#00ffff')
        )
    )

    hum_figure = go.Figure(
        data=[go.Scatter(x=timestamps, y=hum_values, mode='lines+markers', marker=dict(color='#ff00ff'))],
        layout=go.Layout(
            title='Humidity Levels Over Time', xaxis=dict(title='Time', color='#ff00ff'), yaxis=dict(title='Humidity (%)', color='#ff00ff'),
            plot_bgcolor='#2b2b2b', paper_bgcolor='#1e1e1e', font=dict(color='#ff00ff')
        )
    )

    temp_figure = go.Figure(
        data=[go.Scatter(x=timestamps, y=temp_values, mode='lines+markers', marker=dict(color='#00ff00'))],
        layout=go.Layout(
            title='Temperature Over Time', xaxis=dict(title='Time', color='#00ff00'), yaxis=dict(title='Temperature (°C)', color='#00ff00'),
            plot_bgcolor='#2b2b2b', paper_bgcolor='#1e1e1e', font=dict(color='#00ff00')
        )
    )

    uvs_figure = go.Figure(
        data=[go.Scatter(x=timestamps, y=uvs_values, mode='lines+markers', marker=dict(color='#ffbf00'))],
        layout=go.Layout(
            title='UV Levels Over Time', xaxis=dict(title='Time', color='#ffbf00'), yaxis=dict(title='UV Index', color='#ffbf00'),
            plot_bgcolor='#2b2b2b', paper_bgcolor='#1e1e1e', font=dict(color='#ffbf00')
        )
    )

    pressure_figure = go.Figure(
        data=[go.Scatter(x=timestamps, y=pressure_values, mode='lines+markers', marker=dict(color='#ff4500'))],
        layout=go.Layout(
            title='Pressure Over Time', xaxis=dict(title='Time', color='#ff4500'), yaxis=dict(title='Pressure (hPa)', color='#ff4500'),
            plot_bgcolor='#2b2b2b', paper_bgcolor='#1e1e1e', font=dict(color='#ff4500')
        )
    )


    return lux_figure, hum_figure, temp_figure, uvs_figure, pressure_figure, interval_disabled

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
