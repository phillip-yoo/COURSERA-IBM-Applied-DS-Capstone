# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from operator import itemgetter
from dash.dependencies import Input, Output
import plotly.express as px


# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

unique_launch_sites = spacex_df['Launch Site'].unique().tolist()
launch_sites = []
launch_sites.append({'label': 'All Sites', 'value': 'ALL'})
for lsite in unique_launch_sites:
    launch_sites.append({'label': lsite, 'value': lsite})
launch_sites = sorted(launch_sites, key=itemgetter('label'))

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                #dcc.Dropdown(id='site-dropdown',
                                    #options=[
                                        #{'label': 'All Sites', 'value': 'ALL'},
                                        #{'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                        #{'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                        #{'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                        #{'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
                                    #],
                                    #value= 'ALL',
                                    #placeholder='Select a Launch Site here',
                                    #searchable=True),
                                dcc.Dropdown(id='site-dropdown', 
                                    options= launch_sites, 
                                    value='ALL',
                                    placeholder='Select a Launch Site here', 
                                    searchable=True,
                                    style={'width':'80%', 'padding':'3px', 'font-size':'20px', 'text-align-last':'center'}),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),
                                
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                html.P("Payload range (Kg):"),
                                
                                dcc.RangeSlider(id='payload-slider',
                                    min=0, max=10000, step=1000,
                                    marks={0: '0 kg', 2500: '2500 kg', 5000: '5000 kg', 7500: '7500 kg', 10000: '10000 kg'},
                                    value=[min_payload, max_payload]),
                                
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(site):
    filtered_df = spacex_df
    if site == 'ALL':
        pie_chart = px.pie(filtered_df, values='class', names='Launch Site', title='Total Successful Launches By Site')
        return pie_chart
    else:
        # return the outcomes piechart for a selected site
        filtered_df = filtered_df[filtered_df['Launch Site'] == site].groupby(['Launch Site', 'class']).size().reset_index(name='class count')
        filtered_df.rename(columns={0:'class count'}, inplace=True)
        pie_chart = px.pie(filtered_df, values='class count', names='class', title=f'Total Successful Launches for Site {site}')    
        return pie_chart

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), 
              Input(component_id='payload-slider', component_property='value')])
def get_scatter(site,payload):
    low, high = payload #As oppose to using payload[0], payload[1]
    filtered_df2 = spacex_df[(spacex_df['Payload Mass (kg)'] > low) & (spacex_df['Payload Mass (kg)'] < high)] #Or spacex_df[spacex_df['Payload Mass (kg)'].between(low, high)] 
    if site == 'ALL':
        scatter_chart = px.scatter(filtered_df2,x="Payload Mass (kg)", y="class", color="Booster Version Category",\
        title="Correlation Between Payload & Success for All Sites")
        return scatter_chart
    else :
        filtered_df2 = filtered_df2[filtered_df2['Launch Site'] == site]
        scatter_chart = px.scatter(filtered_df2, x="Payload Mass (kg)", y="class", color="Booster Version Category",\
        title=f"Correlation Between Payload & Success for Site {site}")
        return scatter_chart

# Run the app
if __name__ == '__main__':
    app.run_server()