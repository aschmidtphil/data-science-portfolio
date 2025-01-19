# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Find the min and max payload values
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown to select the launch site
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        value='ALL',  # Default value is 'ALL'
        placeholder="Select a Launch Site",
        searchable=True
    ),
    
    # Graph for the pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    
    html.Br(),  # Add some space
    
    html.P("Payload range (Kg):"),
    
    # RangeSlider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,  # Minimum payload value
        max=10000,  # Maximum payload value
        step=1000,  # Step interval of 1000 kg
        marks={i: str(i) for i in range(0, 10001, 1000)},  # Range of marks from 0 to 10000 kg
        value=[min_payload, max_payload]  # Default value is from min to max payload
    ),
    
    # Scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Define callback function for updating the pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site-dropdown', 'value')]
)
def update_pie_chart(selected_site):
    print(f"Selected site: {selected_site}")
    
    if selected_site == 'ALL':
        # Gruppieren nach Launch Site und Success (class), um die Anzahl der erfolgreichen und gescheiterten Starts
        # für jede Launch Site zu erhalten.
        success_counts = spacex_df.groupby(['Launch Site', 'class']).size().reset_index(name='Count')
        
        # Um das Pie-Diagramm korrekt anzuzeigen, benötigen wir die Labels (Launch Site) und Werte (Count)
        fig = px.pie(
            success_counts,  # die aggregierten Daten für das Pie-Diagramm
            names='Launch Site',  # Das Label ist die Launch Site
            values='Count',  # Die Werte sind die Zählungen für jede Kombination aus Launch Site und Success
            title="Launch Success for All Sites"
        )
        
    else:
        # Wenn eine spezifische Launch Site ausgewählt wird
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        print(f"Filtered data for {selected_site}: {filtered_df.shape[0]} rows")
        
        if filtered_df.empty:
            # Falls keine Daten für die gewählte Launch Site vorhanden sind, setzen wir eine leere Zählung
            success_counts = pd.Series([0, 0], index=[0, 1])
        else:
            success_counts = filtered_df['class'].value_counts()
    
        # Erstellen des Pie-Diagramms mit Plotly
        fig = px.pie(
            names=success_counts.index,  # Die Namen sollten die Indizes (0 und 1) sein
            values=success_counts.values,  # Werte sind die Zählungen für jede Klasse (0 und 1)
            title=f"Launch Success for {selected_site}" if selected_site != 'ALL' else "Launch Success for All Sites"
        )
    
    return fig


# Define callback function for updating the scatter chart based on payload range and site selection
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    print(f"Selected site: {selected_site}, Payload range: {payload_range}")
    
    # Filter data based on the payload range
    filtered_df = spacex_df[spacex_df['Payload Mass (kg)'].between(payload_range[0], payload_range[1])]
    
    # Further filter the data based on selected launch site
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    # Create a scatter plot showing the correlation between payload and success
    fig = px.scatter(
        filtered_df, 
        x='Payload Mass (kg)', 
        y='class', 
        color='Booster Version Category', 
        title=f"Payload vs Success for {selected_site}" if selected_site != 'ALL' else "Payload vs Success for All Sites",
        labels={'class': 'Success (1) / Failure (0)', 'Payload Mass (kg)': 'Payload (kg)'}
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8052)
