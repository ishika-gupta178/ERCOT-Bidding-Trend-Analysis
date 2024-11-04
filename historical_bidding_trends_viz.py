import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load the data
df = pd.read_csv("bidding_ng_load.csv")

price_cols = []
supply_cols = []
for i in range(1,11):
    price_cols.append(f'QSE submitted Curve-Price{i}')
    supply_cols.append(f'QSE submitted Curve-MW{i}')

# Create the first graph (Graph 1)
def create_graph1(selected_date, selected_unit, selected_resource_type):
    if selected_date is None or selected_unit is None or selected_resource_type is None:
        return go.Figure()

    # Filter the dataframe based on selections
    filtered_df = df[(df['Delivery Date'] == selected_date) & (df['Resource Name'] == selected_unit) & 
                     (df['Resource Type'] == selected_resource_type)]
    
    supplier = filtered_df['QSE'].unique()

    # Create a 4x6 subplot grid (24 hours)
    fig = make_subplots(rows=4, cols=6, subplot_titles=[f'Hour {i+1}' for i in range(24)],
                        horizontal_spacing=0.05, vertical_spacing=0.1)
    
    # Plot each hour's data
    for hour, hour_df in filtered_df.groupby('Hour Ending'):
        row = (hour - 1) // 6 + 1
        col = (hour - 1) % 6 + 1

        supply_values = hour_df[supply_cols].values[0]
        price_values = hour_df[price_cols].values[0]
        
        # Add scatter plot for the hour
        fig.add_trace(
            go.Scatter(
                x=supply_values, 
                y=price_values,
                mode='markers',
                marker=dict(size=8),
                name=f'Hour {hour}'
            ), row=row, col=col
        )
    
    # Set the same x and y axis ranges for all subplots
    fig.update_xaxes(title_text='Offer MW', row=4, col=1)
    fig.update_yaxes(title_text='Offer Price in $/MW', row=1, col=1)


    # Update layout
    fig.update_layout(
        height=800, width=1200,
        showlegend=False,
        title_text=f'Offer MW & Offer Price Curve on {selected_date}, for Unit {selected_unit}, QSE {supplier}, Resource Type {selected_resource_type}'
    )
    
    return fig

# Create the second graph (Graph 2)
def create_graph2(selected_date, selected_unit, selected_resource_type):
    if selected_date is None or selected_unit is None or selected_resource_type is None:
        return go.Figure()

    # Filter the dataframe based on selections
    filtered_df = df[(df['Delivery Date'] == selected_date) & (df['Resource Name'] == selected_unit) & 
                     (df['Resource Type'] == selected_resource_type)]
    
    supplier = filtered_df['QSE'].unique()
    
    fig = go.Figure()

    # Plotting for each hour
    for hour in filtered_df['Hour Ending'].unique():
        hour_df = filtered_df[filtered_df['Hour Ending'] == hour]
        supply_values = hour_df[supply_cols].values[0]
        price_values = hour_df[price_cols].values[0]
        fig.add_trace(go.Scatter(
            x=supply_values,
            y=price_values,
            mode='markers+lines',
            name=f'Hour {hour}'
        ))
    
        # Set the same x and y axis ranges for all subplots
    fig.update_xaxes(title_text='Offer MW')
    fig.update_yaxes(title_text='Offer Price in $/MW')

    # Update layout
    fig.update_layout(
        title=f'Offer MW & Offer Price Curve on {selected_date}, for Unit {selected_unit}, QSE {supplier}, Resource Type {selected_resource_type}',
        xaxis_title='Offer MW',
        yaxis_title='Offer Price in $/MW',
        showlegend=True
    )

    return fig

# Initialize the main Dash app
app = dash.Dash(__name__)
server = app.server

# Layout with dropdowns for filtering
app.layout = html.Div([
    html.H1("Supply Price Bid Analysis"),
    
    # Dropdown for Resource Type
    dcc.Dropdown(id='resource_type_dropdown', options=[
        {'label': rt, 'value': rt} for rt in df['Resource Type'].unique()
    ], placeholder="Select Resource Type"),
    
    # Dropdown for Unit
    dcc.Dropdown(id='unit_dropdown', placeholder="Select Unit"),
    
    # Dropdown for Date
    dcc.Dropdown(id='date_dropdown', placeholder="Select Date"),

    # Graph 1 and Graph 2 buttons in a horizontal line
    html.Div([
        html.Button('Show Graph 1 (Separate plot for each hour)', id='btn-graph1', n_clicks=0, style={'margin-right': '20px'}),
        html.Button('Show Graph 2 (All hours on one plot)', id='btn-graph2', n_clicks=0),
    ]),

    # Wrapper Div for Graph and Next/Previous buttons
    html.Div([
        # Previous and Next buttons
        html.Div([
            html.Button('Previous Date', id='prev-date-btn', n_clicks=0, style={'margin-right': '20px'}),
            html.Button('Next Date', id='next-date-btn', n_clicks=0),
        ], style={'display': 'flex', 'align-items': 'center', 'margin-right': '20px'}),
        
        # Graph for plotting
        dcc.Graph(id='graph-placeholder'),
    ], style={'display': 'flex', 'align-items': 'center'}),

    # Store for saving the selected graph type
    dcc.Store(id='selected-graph', data=None)
])

# Callback to update Unit dropdown based on Resource Type
@app.callback(
    Output('unit_dropdown', 'options'),
    [Input('resource_type_dropdown', 'value')]
)
def update_unit_dropdown(selected_resource_type):
    if selected_resource_type is None:
        return []
    
    filtered_df = df[df['Resource Type'] == selected_resource_type]
    units = filtered_df['Resource Name'].unique()
    return [{'label': unit, 'value': unit} for unit in units]

# Callback to update Date dropdown based on Unit and Resource Type
@app.callback(
    Output('date_dropdown', 'options'),
    [Input('unit_dropdown', 'value'), Input('resource_type_dropdown', 'value')]
)
def update_date_dropdown(selected_unit, selected_resource_type):
    if selected_unit is None:
        return []
    
    filtered_df = df[(df['Resource Name'] == selected_unit) & (df['Resource Type'] == selected_resource_type)]
    dates = filtered_df['Delivery Date'].unique()
    return [{'label': date, 'value': date} for date in dates]

# Function to find next or previous date
def find_adjacent_date(selected_date, dates, direction):
    if selected_date in dates:
        idx = list(dates).index(selected_date)
        if direction == 'next' and idx < len(dates) - 1:
            return dates[idx + 1]
        elif direction == 'prev' and idx > 0:
            return dates[idx - 1]
    return selected_date

# Callback for Next and Previous Date buttons
@app.callback(
    Output('date_dropdown', 'value'),
    [Input('next-date-btn', 'n_clicks'), Input('prev-date-btn', 'n_clicks')],
    [State('date_dropdown', 'value'), State('unit_dropdown', 'value'), State('resource_type_dropdown', 'value')]
)
def update_date(next_clicks, prev_clicks, selected_date, selected_unit, selected_resource_type):
    # Get available dates for the selected unit and resource type
    filtered_df = df[(df['Resource Name'] == selected_unit) & (df['Resource Type'] == selected_resource_type)]
    available_dates = filtered_df['Delivery Date'].unique()
    
    # Determine which button was pressed (Next or Previous)
    ctx = dash.callback_context
    if not ctx.triggered or selected_date is None:
        return selected_date  # No change

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Update the date based on the button clicked
    if button_id == 'next-date-btn':
        new_date = find_adjacent_date(selected_date, available_dates, 'next')
        return new_date
    elif button_id == 'prev-date-btn':
        new_date = find_adjacent_date(selected_date, available_dates, 'prev')
        return new_date
    
    return selected_date

# Callback to update the selected graph type and render the appropriate graph
@app.callback(
    Output('selected-graph', 'data'),
    Output('graph-placeholder', 'figure'),
    Input('btn-graph1', 'n_clicks'),
    Input('btn-graph2', 'n_clicks'),
    Input('date_dropdown', 'value'),  # Add this input
    Input('unit_dropdown', 'value'),
    Input('resource_type_dropdown', 'value'),
    State('selected-graph', 'data')  # Access the current graph type
)
def update_graph_type(btn1, btn2, selected_date, selected_unit, selected_resource_type, current_graph_type):

    selected_graph = current_graph_type if current_graph_type else 'Graph 1'  # Default to 'Graph 1' if no previous selection

    # Check which button was clicked and update the graph type accordingly
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, go.Figure()  # No change

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]  # Get the ID of the button that triggered the callback
    
    # Update the graph based on the selected date
    figure = dash.no_update  # Default to no update
    if selected_date and selected_unit and selected_resource_type:
        if button_id == 'btn-graph1' and btn1 > 0:
            selected_graph = 'Graph 1'
            figure = create_graph1(selected_date, selected_unit, selected_resource_type)
        elif button_id == 'btn-graph2' and btn2 > 0:
            selected_graph = 'Graph 2'
            figure = create_graph2(selected_date, selected_unit, selected_resource_type)
        else:
            selected_graph = current_graph_type  # If no button was pressed, keep the current graph type
            if current_graph_type == 'Graph 1':
                figure = create_graph1(selected_date, selected_unit, selected_resource_type)
            elif current_graph_type == 'Graph 2':
                figure = create_graph2(selected_date, selected_unit, selected_resource_type)
    
    return selected_graph, figure

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
