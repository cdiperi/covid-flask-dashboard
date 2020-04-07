from flask import Flask, render_template, request
from bokeh.embed import components
from myplots import live_summary_data, live_top_10_hbar, live_map_chart, fetch_data

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def chart():

    global_df, us_state_df = fetch_data()

    selected_class = request.form.get('dropdown-select')
    
    if selected_class == 0 or selected_class == None:
        summary_list, map_chart, hbar_chart = redraw(global_df, us_state_df, 'US')
        scope = 'US'
        selected_class = 'US'
    else:
        summary_list, map_chart, hbar_chart = redraw(global_df, us_state_df, selected_class)
        scope = selected_class

    summary_list = live_summary_data(global_df, scope)

    total_confirmed = f"{summary_list[0]:,}"
    total_deaths = f"{summary_list[2]:,}"
    total_recovered = f"{summary_list[4]:,}"

    script_map_chart, div_map_chart = components(map_chart)
    script_hbar_chart, div_hbar_chart = components(hbar_chart)

    return render_template(
        'index.html',
        div_map_chart=div_map_chart,
        script_map_chart=script_map_chart,
        div_hbar_chart=div_hbar_chart,
        script_hbar_chart=script_hbar_chart,
        total_confirmed=total_confirmed,
        total_deaths=total_deaths,
        total_recovered=total_recovered,
        selected_class=selected_class,
        scope=scope
    )


def redraw(global_df, us_state_df, scope):
    summary_list = live_summary_data(global_df, scope)
    if scope == 'US':
        us_state_df = us_state_df.fillna(0) #
        gmap = live_map_chart(us_state_df, scope)
        hbar = live_top_10_hbar(us_state_df, scope)
    else:
        global_df = global_df.fillna(0) #
        gmap = live_map_chart(global_df, scope)
        hbar = live_top_10_hbar(global_df, scope)

    return (
        summary_list,
        gmap,
        hbar
    )


