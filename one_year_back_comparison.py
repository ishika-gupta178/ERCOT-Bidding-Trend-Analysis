import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load the data
df = pd.read_csv("bidding_ng_load.csv")

# get subset of data
df_subset = df[(df['Resource Type'] == 'CCGT90') & (df['Resource Name'] == 'FRNYPP_CC1_4')]

# getting the relevant columns:
supply_cols = []
price_cols = []
rel_columns = ['Delivery Date', 'Hour Ending']

for i in range(1,11):
    supply_cols.append(f'QSE submitted Curve-MW{i}')
    price_cols.append(f'QSE submitted Curve-Price{i}')

rel_columns.extend(supply_cols)
rel_columns.extend(price_cols)

df_subset = df_subset[rel_columns]

# change the datatype of time
df_subset['Delivery Date'] = pd.to_datetime(df['Delivery Date'])

# getting the valid dates - date and the corresponding date 2 months before

# setting the dates as index
df_subset = df_subset.set_index('Delivery Date')
# Find unique delivery dates in the dataset
unique_dates = df_subset.index.unique()

valid_dates = []
one_year_before_dates = []
for date in unique_dates:
    one_year_before_date = date - pd.DateOffset(months=12)
    if one_year_before_date in unique_dates:
        valid_dates.append(date)
        one_year_before_dates.append(one_year_before_date)

dates_df = pd.DataFrame({'Date':valid_dates, 'One Year Back':one_year_before_dates})
dates_df['Date'] = dates_df['Date'].astype('str')
dates_df['One Year Back'] = dates_df['One Year Back'].astype('str')
valid_dates = list(dates_df['Date'].values)
one_year_before_dates = list(dates_df['One Year Back'].values)


def plot_bids(selected_date):

    present_date_df = df_subset.loc[selected_date]
    present_date_index = valid_dates.index(selected_date)

    one_year_back_date = one_year_before_dates[present_date_index]
    one_year_back_df = df_subset.loc[one_year_back_date]

    # Set up a 4x6 grid for subplots (24 plots)
    fig = make_subplots(rows=4, cols=6, shared_xaxes=True, shared_yaxes=True,
                        subplot_titles=[f'Hour {i+1}' for i in range(24)])
    
    for hour in range(1, 25):
        row = (hour - 1) // 6 + 1
        col = (hour - 1) % 6 + 1

        # Data for the present day and two months back for the specific hour
        present_hour_data = present_date_df[present_date_df['Hour Ending'] == hour]
        one_year_back_hour_data = one_year_back_df[one_year_back_df['Hour Ending'] == hour]

        # Extract supply and price bids for the present day
        present_supply_bids = present_hour_data[supply_cols].values.flatten()
        present_price_bids = present_hour_data[price_cols].values.flatten()

        # Extract supply and price bids for two months back
        back_supply_bids = one_year_back_hour_data[supply_cols].values.flatten()
        back_price_bids = one_year_back_hour_data[price_cols].values.flatten()

        # Add line for present day
        fig.add_trace(go.Scatter(x=present_supply_bids,
                                 y=present_price_bids,
                                 mode='lines+markers',
                                 name=f'Selected Date',
                                 marker=dict(symbol='circle', color='blue'),
                                 line=dict(color='blue'),
                                 showlegend=(hour == 1)),
                                 row= row, 
                                 col=col)

        # Add line for two months back
        fig.add_trace(go.Scatter(x=back_supply_bids, 
                                 y=back_price_bids,
                                 mode='lines+markers',
                                 name=f'1 Year Back',
                                 marker=dict(symbol='x', color='red'),
                                 line=dict(dash='dash'),
                                 showlegend=(hour == 1)),
                                 row=row, 
                                 col=col)

    # Update layout with shared labels and title
    fig.update_layout(height=800, width=1200, title_text=f'Bids on {selected_date} and 1 Year Back {one_year_back_date}',
                      showlegend=True)
    
    fig.update_xaxes(title_text="Supply Bids (1 to 10) in MW", row=4, col=3)  # Common x-axis title
    fig.update_yaxes(title_text="Price Bids (1 to 10) in $/MW", row=2, col=1)  # Common y-axis title

    return fig

# Initialize the main Dash app
app = dash.Dash(__name__)

# Layout with dropdowns for filtering
app.layout = html.Div([
    html.H1("Bidding Curves for Unit FRNYPP_CC1_4, Resource Type CCGT90"),

    # Dropdown for Date
    dcc.Dropdown(id='date_dropdown', options=[
        {'label': date, 'value': date} for date in valid_dates
    ], placeholder="Select Date"),
    

    # Wrapper Div for Graph and Next/Previous buttons
    html.Div([
        # Previous and Next buttons
        html.Div([
            html.Button('Previous Date', id='prev-date-btn', n_clicks=0, style={'margin-right': '20px'}),
            html.Button('Next Date', id='next-date-btn', n_clicks=0),
        ], style={'display': 'flex', 'align-items': 'center', 'margin-right': '20px'}),
        
        # Graph for plotting
        dcc.Graph(id='graph-placeholder'),
    ], style={'display': 'flex', 'align-items': 'center'})
])


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
    [State('date_dropdown', 'value')]
)
def update_date(next_clicks, prev_clicks, selected_date):    
    # Determine which button was pressed (Next or Previous)
    ctx = dash.callback_context
    if not ctx.triggered or selected_date is None:
        return selected_date  # No change

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Update the date based on the button clicked
    if button_id == 'next-date-btn':
        new_date = find_adjacent_date(selected_date, valid_dates, 'next')
        return new_date
    elif button_id == 'prev-date-btn':
        new_date = find_adjacent_date(selected_date, valid_dates, 'prev')
        return new_date
    
    return selected_date

# Callback to update the selected graph type and render the appropriate graph
@app.callback(
    Output('graph-placeholder', 'figure'),
    Input('next-date-btn', 'n_clicks'),
    Input('prev-date-btn', 'n_clicks'),
    Input('date_dropdown', 'value')  # Add this input
)
def update_graph(btn1, btn2, selected_date):

    # If no date is selected yet, default to the first date in unique_dates
    if selected_date is None:
        selected_date = valid_dates[0]  # Use the first available date

    # Call the plot_forecasts function to create the graph for the selected date
    fig = plot_bids(selected_date)
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
