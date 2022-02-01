import pathlib
import dash
import json
from dash import dcc
from dash import html
import pandas as pd
from dash.dependencies import Input, Output, State
import cufflinks as cf
import plotly_express as px
from app import app
from app import server
import numpy as np
from urllib.request import urlopen

# # Load data
APP_PATH = str(pathlib.Path(__file__).parent.resolve())

DEFAULT_OPACITY = 0.8

# set mapbox token and style
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"
mapbox_style = "mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz"

# read in fips shape data
file = open("data/geojson-counties-fips.json")
counties = json.load(file)

# read in climate data
dat = "data/annual_climateDS.csv"
datDF = pd.read_csv(dat, dtype={'fips': str})

# read in kestral range shift data
dat1 = "data/kestralModel.csv"
datDFKest = pd.read_csv(dat1, dtype={'Counties': str})

# read in carya ovata range shift data
dat2 = "data/Carya_ovata.csv"
datDFCar = pd.read_csv(dat2, dtype={'Counties': str})

#######################################################################################################################
# This is my app layout

app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            children=[
                html.A(
                    html.Img(id="logo", src=app.get_asset_url("logo.png")),
                    href="https://www.uvm.edu/",
                ),
                html.H4(children=" Barracuda Data Visualization Dashboard"),
                html.P(
                    id="description",
                    children="Biodiversity and Rural Response to Climate Change Using Data Analysis",
                ),
            ],
        ),
        html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="left-column",
                    children=[
                         html.Div(
                             id="slider-container",
                             children=[
                                html.P(id="data-selector", children="Select a Data Set to Plot"),
                                dcc.Dropdown(
                                    options=[
                                        {
                                            "label": "Average of Nighttime Minimum Temperature, (deg. C)",
                                            "value": "tmin",
                                        },
                                                                                {
                                            "label": "Average of Daytime High Temperature, (deg. C)",
                                            "value": "tmax",
                                        },
                                                                                {
                                            "label": "Average of Daily Mean Temperature, (deg. C)",
                                            "value": "tmean",
                                        },
                                        {
                                            "label": "Total Annual Precipitation, (mm)",
                                            "value": "prec",
                                        },
                                        {
                                            "label": "Total April Precipitation, (mm)",
                                            "value": "aprec",
                                        },
                                                                                {
                                            "label": "Length of Frost Free Period, (days)",
                                            "value": "ffp",
                                        },
                                                                                {
                                            "label": "Kestral Range Shift Modeled Abundance",
                                            "value": "Kest_Abundance",
                                        },
                                                                                {
                                            "label": "Carya ovata Range Shift Modeled Abundance",
                                            "value": "CarO_Abundance",
                                        },
                                    ],
                                    value="tmin",
                                    id="data-dropdown",
                                ),
                            ],
                        ),
                        html.Div(
                            id="heatmap-container",
                            children=[
                                html.P(
                                    "Heatmap Over Time (Select Year Below Map)",
                                    id="heatmap-title",
                                ),
                                dcc.Graph(
                                    id="county-choropleth",
                                    figure=dict(
                                        layout=dict(
                                            mapbox=dict(
                                                layers=[],
                                                accesstoken=mapbox_access_token,
                                                style=mapbox_style,
                                                center=dict(
                                                    lat=38.72490, lon=-95.61446
                                                ),
                                                pitch=0,
                                                zoom=3.5,
                                            ),
                                            autosize=True,
                                        ),
                                    ),
                                ),
                            ],
                        ),
                        html.Div(
                             id="year-container",
                             children=[
                                html.P(id="year-selector", children="Select a Year to Plot"),
                                dcc.Slider(
                                    value=1950,
                                    min=1950,
                                    max=2019,
                                    step=1,
                                    marks={
                                        1950: {'label': '1950'},
                                        1967: {'label': '1967'},
                                        1985: {'label': '1985'},
                                        2002: {'label': '2002'},
                                        2019: {'label': '2019'},
                                            },
                                    tooltip={"placement": "bottom", "always_visible": True},
                                    id="year-slider",
                                ),
                            ], style= {'display': 'block'},
                        ),

                    ],
                ),
                html.Div(
                    id="graph-container",
                    children=[
                        html.P(id="chart-selector", children="Select summary statistic to plot:"),
                        dcc.Dropdown(
                            options=[
                                {
                                    "label": "Mean Value",
                                    "value": "mean",
                                },
                                {
                                    "label": "Median Value",
                                    "value": "median",
                                },
                                                                {
                                    "label": "Min. Value",
                                    "value": "min",
                                },
                                                                {
                                    "label": "Max. Value ",
                                    "value": "max",
                                },
                            ],
                            value="mean",
                            id="chart-dropdown",
                        ),
                        dcc.Graph(
                            id="selected-data",
                            figure=dict(
                                data=[dict(x=0, y=0)],
                                layout=dict(
                                    paper_bgcolor="#F4F4F8",
                                    plot_bgcolor="#F4F4F8",
                                    autofill=True,
                                    margin=dict(t=75, r=50, b=100, l=50),
                                ),
                            ),
                        ),
                    ],
                ),
            ],
        ),
    ],
)
#######################################################################################################################




#######################################################################################################################

@app.callback(
   Output(component_id='year-container', component_property='style'),
   [Input(component_id='data-dropdown', component_property='value')])


def show_hide_element(visibility_state):

    if visibility_state == 'Kest_Abundance' or visibility_state == 'CarO_Abundance':
        return {'display': 'none'}


@app.callback(
    Output("county-choropleth", "figure"),
    [
        State("county-choropleth", "figure"),
        Input("data-dropdown", "value"),
        Input("year-slider", "value"),
    ],
)

#######################################################################################################################



#######################################################################################################################
### Here we build the main choropleth figure and populate the layout
def display_map(figure, data_dropdown, year_slider):

    # write if else statement here:
    if data_dropdown == "Kest_Abundance" or data_dropdown=='CarO_Abundance':

        if data_dropdown == "Kest_Abundance":
            AbndDat = datDFKest
        if data_dropdown=='CarO_Abundance':
            AbndDat = datDFCar

        # plot scatter box
        # find the max value
        maxVal = np.nanmax(AbndDat["Abundance"])

        fig = px.scatter_mapbox(AbndDat, lat='Latitude',
                                    lon='Longitude',
                                    color='Abundance',
                                    animation_frame="year",
                                    range_color=(0, maxVal),
                                    color_continuous_scale="Viridis",
                                    opacity=0.8,
                                )
        fig.update_layout(mapbox_style="carto-darkmatter", mapbox_zoom=4.5, mapbox_center = {"lat": 43, "lon": -74},)
        fig.update_layout(margin={"r":0,"t":0,"l":20,"b":0},
            plot_bgcolor="#252e3f",
            paper_bgcolor="#252e3f",
            font=dict(color="#7fafdf"),
            #dragmode="lasso",
            )


        fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 200
        fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 200
        fig.layout.coloraxis.showscale = True
        fig.layout.sliders[0].pad.t = 10
        fig.layout.updatemenus[0].pad.t= 10


    else:


        # plot choropleth

        # Find max value for heat map bar
        maxVal = max(datDF[data_dropdown])

        # filter by year
        datDF1 = datDF[(datDF['year'] == year_slider)]

        fig = px.choropleth_mapbox(datDF1, geojson=counties, locations='fips', color=data_dropdown,
                            color_continuous_scale="Viridis",
                            #animation_frame="year",
                            range_color=(0, maxVal),
                            mapbox_style="carto-darkmatter",
                            zoom=2.9, center = {"lat": 34.640033, "lon": -95.981758},
                            opacity=0.9,
                            labels={data_dropdown:' ', 'time':'Year', 'Counties':'County Code'}
                            )

        fig.update_layout(margin={"r":0,"t":0,"l":20,"b":0},
            geo_scope='usa',
            #dragmode="lasso", #select
            plot_bgcolor="#252e3f",       #1f2630 dark blue
            paper_bgcolor="#252e3f",      #7fafdf light blue text
            font=dict(color="#7fafdf"),
            )

    return fig
#######################################################################################################################




# human data
# climate vs range shifrt
# historical vs modeled
# 10km grid for range


# callback for selcted data on map
#######################################################################################################################
@app.callback( # call back for selected data on map for chart on right
    Output("selected-data", "figure"),
    [
        Input("county-choropleth", "selectedData"),
        Input("chart-dropdown", "value"),
        Input("data-dropdown", "value"),
        State("data-dropdown","options"),
    ],
)
#######################################################################################################################




#######################################################################################################################
# Plot the time series on the right
def display_selected_data(selectedData, chart_dropdown, data_dropdown, opts):
    if selectedData is None:
        return dict(
            data=[dict(x=0, y=0)],
            layout=dict(
                title="Click drag on the map to select counties",
                paper_bgcolor="#1f2630",
                plot_bgcolor="#1f2630",
                font=dict(color="#7fafdf"),
                margin=dict(t=75, r=50, b=100, l=75),
            ),
        )


    # find points from the selected data
    pts = selectedData["points"]

    the_label = [x['label'] for x in opts if x['value'] == data_dropdown]

    the_label = str(the_label).replace('[','').replace(']','')


    if data_dropdown == "Kest_Abundance" or data_dropdown == 'CarO_Abundance':

        yval = "Abundance"

        if data_dropdown == "Kest_Abundance":
            AbndDat = datDFKest
        if data_dropdown=='CarO_Abundance':
            AbndDat = datDFCar




        latVals = [d['lat'] for d in pts if 'lat' in d]
        lonVals = [d['lon'] for d in pts if 'lon' in d]

        vals = list(zip(latVals, lonVals))

        # find the values for all selected counties for all years
        df = AbndDat.set_index(['Latitude', 'Longitude'])

        subDF = df.loc[df.index.isin(vals)]

    else:

        yval = data_dropdown

        # get a list of all locations selected
        vals = [d['location'] for d in pts if 'location' in d]

        # find the values for all selected counties for all years
        df = datDF.set_index(['fips'])
        subDF = df.loc[df.index.isin(vals)]


    # select the data to plot
    ##########################################################################################
    if chart_dropdown == "mean":

        # summmary by time
        summDF = subDF.groupby('year').mean().reset_index()

    if chart_dropdown == "median":

        # summmary by time
        summDF = subDF.groupby('year').median().reset_index()

    if chart_dropdown == "min":

        # summmary by time
        summDF = subDF.groupby('year').min().reset_index()

    if chart_dropdown == "max":

        # summmary by time
        summDF = subDF.groupby('year').max().reset_index()



    ##########################################################################################

    # make the plot
    ##########################################################################################
    fig = summDF.iplot(
        x="year",
        kind="scatter",
        y=yval,
        colors=[
            "#7fafdf",
        ],
        asFigure=True,
    )

    fig_layout = fig["layout"]

    # See plot.ly/python/reference
    fig_layout["yaxis"]["title"] = the_label
    fig_layout["xaxis"]["title"] = "Time (years)"
    fig_layout["yaxis"]["fixedrange"] = True
    fig_layout["xaxis"]["fixedrange"] = False
    fig_layout["hovermode"] = "closest"
    fig_layout["legend"] = dict(orientation="v")
    fig_layout["autosize"] = True
    fig_layout["paper_bgcolor"] = "#1f2630"
    fig_layout["plot_bgcolor"] = "#1f2630"
    fig_layout["font"]["color"] = "#7fafdf"
    fig_layout["xaxis"]["tickfont"]["color"] = "#7fafdf"
    fig_layout["yaxis"]["tickfont"]["color"] = "#7fafdf"
    fig_layout["xaxis"]["gridcolor"] = "#5b5b5b"
    fig_layout["yaxis"]["gridcolor"] = "#5b5b5b"


    return fig
    ##########################################################################################




#######################################################################################################################
# run the server

if __name__ == "__main__":
    app.run_server(debug=True)



