from bokeh.plotting import figure, gmap
from bokeh.models import ColumnDataSource, HoverTool, LinearInterpolator, GMapOptions, WheelZoomTool, NumeralTickFormatter, NumberFormatter, Range1d
import pandas as pd
import json
import requests

def fetch_data():
    url = "https://corona.lmao.ninja/states"
    response = requests.get(url).json()
    us_state_df = pd.read_json(json.dumps(response))
    state_df = pd.read_csv('/home/cbdiperi/covid/data/novel_state_list.csv')
    us_state_df = us_state_df.merge(state_df, left_on='state', right_on='state', how='left')
    us_state_df.sort_values(by='cases', ascending=False)
    us_state_df['todayDeathsPct'] = (us_state_df['todayDeaths'] / us_state_df['deaths'])
    us_state_df['todayCasesPct'] = (us_state_df['todayCases'] / us_state_df['cases'])
    us_state_df['casesPer100k'] = (us_state_df['cases'] / us_state_df['population']) * 100000
    us_state_df['deathsPer100k'] = (us_state_df['deaths'] / us_state_df['population']) * 100000
    us_state_df = us_state_df[us_state_df['state'] != 'USA Total']

    url = "https://corona.lmao.ninja/countries"
    response = requests.get(url).json()
    global_df = pd.read_json(json.dumps(response))
    global_df.sort_values(by='cases', ascending=False)
    global_df = global_df.drop(columns=['countryInfo', 'updated'])
    country_df = pd.read_csv('/home/cbdiperi/covid/data/novel_country_list.csv')
    country_df['lat'] = country_df['lat'].astype(float)
    global_df = global_df.merge(country_df, left_on='country', right_on='country', how='left')

    global_df = global_df.fillna(0)
    global_df[['casesPerOneMillion', 'deathsPerOneMillion']] = global_df[['casesPerOneMillion',
                                                                          'deathsPerOneMillion']].astype(int)
    global_df['todayDeathsPct'] = (global_df['todayDeaths'] / global_df['deaths'])
    global_df['todayCasesPct'] = (global_df['todayCases'] / global_df['cases'])

    return global_df, us_state_df


def live_summary_data(df, scope):
    # uses global_df for all scopes
    if scope == 'Global':
        df = df[['cases', 'todayCases', 'deaths', 'todayDeaths', 'recovered', 'active']]
        summary_list = df.sum()
        summary_list = summary_list.astype('Int64').tolist()
    elif scope == 'US':
        filter_df = df[df['country'] == 'USA'][['cases', 'todayCases', 'deaths', 'todayDeaths', 'recovered', 'active']]
        summary_list = []
        for index, row in filter_df.iterrows():
            summary_list = [int(row.cases), int(row.todayCases), int(row.deaths), int(row.todayDeaths),
                            int(row.recovered), int(row.active)]
    else:
        filter_df = df[df['region'] == scope]

        filter_df = filter_df[['cases', 'todayCases', 'deaths', 'todayDeaths', 'recovered', 'active']]
        summary_list = filter_df.sum()
        summary_list = summary_list.astype('Int64').tolist()

    return summary_list


def live_top_10_hbar(df, scope):

    if scope == 'Global':
        df = df.sort_values(by='cases', ascending=False)
        top_10_df = df.head(50)
    elif scope == 'US':
        df = df.sort_values(by='cases', ascending=False)
        top_10_df = df.head(52)
    else:
        df = df[df['region'] == scope]
        df = df.sort_values(by='cases', ascending=False)
        top_10_df = df

    top_10_df['mortality'] = top_10_df['deaths'] / top_10_df['cases']
    top_10_df['hbarcases'] = top_10_df['cases'] - top_10_df['deaths']
    source = ColumnDataSource(top_10_df)

    categories = top_10_df[top_10_df.columns[0]].tolist()
    categories.reverse()

    p = figure(#plot_width=500,
               #plot_height=450,
               y_range=categories,
               toolbar_location='above',
               sizing_mode='stretch_both',
            #   x_axis_label='Total Confirmed Cases',
               #title='Top 10',
               tools='save, reset, box_zoom'
               )

    if scope == 'US':
        stacks = ['deaths', 'hbarcases']
        colors = ['#e15759', '#4e79a7']
        p.hbar_stack(stacks, y="state", height=.75, color=colors, source=source)

        hbar_tooltips = """
        <div>
            <div>
                <span style="font-size:15px;font-weight:bold;text-decoration:underline;">@state</span>
            </div>
            <div>
                <span style="font-size:11px;color:#4e79a7;font-weight:bold;"><b>Confirmed: @cases{0,000}</b> (@todayCases{0,000} today)<br></span>
                <span style="font-size:11px;color:#4e79a7;font-weight:bold;"><b>Cases per 100K: @casesPer100k{0,0.0}</b><br></span>
                <span style="font-size:11px;color:#731d1d;font-weight:bold;"><b>Active: @active{0,000}</b><br></span>
                <span style="font-size:11px;color:#dc3545;font-weight:bold;"><b>Deaths: @deaths{0,000}</b> (@todayDeaths{0,000} today)<br></span>
                <span style="font-size:11px;color:#dc3545;font-weight:bold;"><b>Deaths per 100K: @deathsPer100k{0,0.0}</b><br></span>
                <span style="font-size:11px;color:#808C8E;font-weight:bold;"><b>Mortality: @mortality{0.00%}</b><br></span>
            </div>
        </div>"""

    else:
        stacks = ['deaths', 'hbarcases']
        colors = ['#e15759', '#4e79a7']
        p.hbar_stack(stacks, y="country", height=.75, color=colors, source=source)

        hbar_tooltips = """
        <div>
            <div>
                <span style="font-size:15px;font-weight:bold;text-decoration:underline;">@country</span>
            </div>
            <div>
                <span style="font-size:11px;color:#4e79a7;font-weight:bold;"><b>Confirmed: @cases{0,000}</b> (@todayCases{0,000} today)<br></span>
                <span style="font-size:11px;color:#4e79a7;font-weight:bold;"><b>Cases per 1M: @casesPerOneMillion{0,000}</b><br></span>
                <span style="font-size:11px;color:#731d1d;font-weight:bold;"><b>Active: @active{0,000}</b><br></span>
                <span style="font-size:11px;color:#dc3545;font-weight:bold;"><b>Deaths: @deaths{0,000}</b> (@todayDeaths{0,000} today)<br></span>
                <span style="font-size:11px;color:#dc3545;font-weight:bold;"><b>Deaths per 1M: @deathsPerOneMillion{0,000}</b><br></span>
                <span style="font-size:11px;color:#28a745;font-weight:bold;"><b>Recovered: @recovered{0,000}</b><br></span>
                <span style="font-size:11px;color:#808C8E;font-weight:bold;"><b>Mortality: @mortality{0.00%}</b><br></span>
            </div>
        </div>"""

    p.xaxis[0].ticker.desired_num_ticks=4
    p.add_tools(HoverTool(tooltips=hbar_tooltips))
    p.toolbar.active_drag=None
    p.xaxis[0].formatter = NumeralTickFormatter(format="0,000")
    p.title.align = 'center'
    p.ygrid.visible = False
    # p.background_fill_color = "#eef1f5"

    return p


def live_map_chart(df, scope):
    if scope == 'Global':
        geo_data = df.dropna(subset=['lat', 'lon', 'cases'])
        lat = 22.785000
        lng = 5.522778
        zoom = 2
    elif scope == 'US':
        geo_data = df.dropna(subset=['lat', 'lon', 'cases'])
        geo_data = geo_data.loc[(geo_data[['cases']] != 0).all(axis=1)]
        lat = 39.8283
        lng = -98.5795
        zoom = 4
    else:
        geo_data = df[df['region'] == scope]
        geo_data = geo_data.dropna(subset=['lat', 'lon', 'cases'])
        if scope == 'Oceania':
            lat = -26.7
            lng = 146.75136
        elif scope == 'Americas':
            lat = 25.025885
            lng = -78.035889
        else:
            lat = geo_data['lat'].mean()
            lng = geo_data['lon'].mean()
        if scope == 'Europe' or scope == 'Oceania':
            zoom = 4
        else:
            zoom = 3

    styles = """[    {        "featureType": "administrative.locality",        "elementType": "all",        "stylers": [            {                "hue": "#2c2e33"            },            {                "saturation": 7            },            {                "lightness": 19            },            {                "visibility": "on"            }        ]    },    {        "featureType": "landscape",        "elementType": "all",        "stylers": [            {                "hue": "#ffffff"            },            {                "saturation": -100            },            {                "lightness": 100            },            {                "visibility": "simplified"            }        ]    },    {        "featureType": "poi",        "elementType": "all",        "stylers": [            {                "hue": "#ffffff"            },            {                "saturation": -100            },            {                "lightness": 100            },            {                "visibility": "off"            }        ]    },    {        "featureType": "road",        "elementType": "geometry",        "stylers": [            {                "hue": "#bbc0c4"            },            {                "saturation": -93            },            {                "lightness": 31            },            {                "visibility": "simplified"            }        ]    },    {        "featureType": "road",        "elementType": "labels",        "stylers": [            {                "hue": "#bbc0c4"            },            {                "saturation": -93            },            {                "lightness": 31            },            {                "visibility": "on"            }        ]    },    {        "featureType": "road.arterial",        "elementType": "labels",        "stylers": [            {                "hue": "#bbc0c4"            },            {                "saturation": -93            },            {                "lightness": -2            },            {                "visibility": "simplified"            }        ]    },    {        "featureType": "road.local",        "elementType": "geometry",        "stylers": [            {                "hue": "#e9ebed"            },            {                "saturation": -90            },            {                "lightness": -8            },            {                "visibility": "simplified"            }        ]    },    {        "featureType": "transit",        "elementType": "all",        "stylers": [            {                "hue": "#e9ebed"            },            {                "saturation": 10            },            {                "lightness": 69            },            {                "visibility": "on"            }        ]    },    {        "featureType": "water",        "elementType": "all",        "stylers": [            {                "hue": "#e9ebed"            },            {                "saturation": -78            },            {                "lightness": 67            },            {                "visibility": "simplified"            }        ]    }]"""
    map_options = GMapOptions(lat=lat, lng=lng, map_type="roadmap", zoom=zoom, styles=styles)

    p = gmap("AIzaSyDpPxqrRI5F2h_5HC7IkEnrn1ttHHL8SNQ", map_options, title="", #height=450,
             toolbar_location='above', margin=0, sizing_mode='stretch_both',
             tools='pan, wheel_zoom, reset')

    geo_data['mortality'] = geo_data['deaths'] / geo_data['cases']
    source = ColumnDataSource(geo_data)

    if scope == 'US':
        size_mapper = LinearInterpolator(
            x = [geo_data.cases.min(), geo_data.cases.max()],
            y = [5, 50])
    elif scope == 'Global':
        size_mapper = LinearInterpolator(
            x = [geo_data.cases.min(), geo_data.cases.max()],
            y = [3, 50])
    else:
        size_mapper = LinearInterpolator(
            x = [geo_data.cases.min(), geo_data.cases.max()],
            y = [5, 50])

    if scope == 'US':
        p.circle(x="lon", y="lat", size={'field': 'cases', 'transform': size_mapper},
                    fill_color="#4e79a7", fill_alpha=0.8, source=source, line_color=None) # #eb5454
        map_tooltips = """
        <div>
            <div>
                <span style="font-size:15px;font-weight:bold;text-decoration:underline;">@state</span>
            </div>
            <div>
                <span style="font-size:11px;color:#4e79a7;font-weight:bold;"><b>Confirmed: @cases{0,000}</b> (@todayCases{0,000} today)<br></span>
                <span style="font-size:11px;color:#4e79a7;font-weight:bold;"><b>Cases per 100K: @casesPer100k{0,0.0}</b><br></span>
                <span style="font-size:11px;color:#731d1d;font-weight:bold;"><b>Active: @active{0,000}</b><br></span>
                <span style="font-size:11px;color:#dc3545;font-weight:bold;"><b>Deaths: @deaths{0,000}</b> (@todayDeaths{0,000} today)<br></span>
                <span style="font-size:11px;color:#dc3545;font-weight:bold;"><b>Deaths per 100K: @deathsPer100k{0,0.0}</b><br></span>
                <span style="font-size:11px;color:#808C8E;font-weight:bold;"><b>Mortality: @mortality{0.00%}</b><br></span>
            </div>
        </div>"""
    else:
        p.circle(x="lon", y="lat", size={'field': 'cases', 'transform': size_mapper},
                    fill_color="#4e79a7", fill_alpha=0.8, source=source, line_color=None)
        map_tooltips = """
        <div>
            <div>
                <span style="font-size:15px;font-weight:bold;text-decoration:underline;">@country</span>
            </div>
            <div>
                <span style="font-size:11px;color:#4e79a7;font-weight:bold;"><b>Confirmed: @cases{0,000}</b> (@todayCases{0,000} today)<br></span>
                <span style="font-size:11px;color:#4e79a7;font-weight:bold;"><b>Cases per 1M: @casesPerOneMillion{0,000}</b><br></span>
                <span style="font-size:11px;color:#731d1d;font-weight:bold;"><b>Active: @active{0,000}</b><br></span>
                <span style="font-size:11px;color:#dc3545;font-weight:bold;"><b>Deaths: @deaths{0,000}</b> (@todayDeaths{0,000} today)<br></span>
                <span style="font-size:11px;color:#dc3545;font-weight:bold;"><b>Deaths per 1M: @deathsPerOneMillion{0,000}</b><br></span>
                <span style="font-size:11px;color:#28a745;font-weight:bold;"><b>Recovered: @recovered{0,000}</b><br></span>
                <span style="font-size:11px;color:#808C8E;font-weight:bold;"><b>Mortality: @mortality{0.00%}</b><br></span>
            </div>
        </div>"""

    p.y_range=Range1d(-90, 90)
    p.x_range=Range1d(-170, 170)
    # p.xaxis.visible = False
    # p.yaxis.visible = False
    p.add_tools(HoverTool(tooltips=map_tooltips))
    p.toolbar.active_scroll = p.select_one(WheelZoomTool)
    return p
