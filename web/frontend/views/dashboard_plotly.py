from distutils.command.build import build
import dash
from dash import dcc, html

from django_plotly_dash import DjangoDash

from dash import Dash, html, dcc, Input, Output, State
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from pyadlml.dataset.plot.plotly.acts_and_devs import activities_and_devices
from pyadlml.dataset.plot.plotly.dashboard.layout import _buttons_to_use
import plotly.graph_objs as go

from frontend.util import get_server
from pyadlml.dataset import load_act_assist
from pyadlml.constants import DEVICE
from pyadlml.dataset.util import select_timespan
from hass_api.rest import HARest


def build_app():
    name = 'initial'
    app = DjangoDash('experiment', external_stylesheets=[dbc.themes.BOOTSTRAP])

    layout = dbc.Container(fluid=True,
        children=[
            dcc.Input(id='act_assist_path', type='hidden', value='not_set'),
            dcc.Input(id='subject_names', type='hidden', value='not_set'),
            html.Div(children=[
                    dcc.Graph(id='graph-acts_n_devs',
                                figure=go.Figure(),
                                config=dict(displayModeBar=True,
                                            modeBarButtonsToRemove=_buttons_to_use(
                                                'zoom2d', 'zoomIn2d', 'zoomOut2d',
                                                'pan2d', 'resetScale2d'

                                            ),
                                            edits=dict(legendPosition=True),
                                            showAxisDragHandles=True,
                                            displaylogo=False))
            ]),

            dbc.Row(children=[
                    dbc.Col('Marker type: ', width=2),
                    dbc.Col(width=10, children=dbc.RadioItems(id='and_dev-type',
                                        inline=True,
                                        options=[{'label': i, 'value': i} for i in ['event', 'state']],
                                        value='event',
                                        labelStyle={'display': 'inline-block', 'marginTop': '5px'}),

                    )
            ])

        ]
    )
    app.layout = layout

    @app.callback(
        Output('graph-acts_n_devs', 'figure'),
        Output('act_assist_path', 'value'),
        Input('and_dev-type', 'value'),
        State('act_assist_path', 'value'),
    )
    def update_acts_n_devs(dev_type_trigger, act_assist_path):
        srv = get_server()
        if act_assist_path == 'not_set':
            act_assist_path = srv.dataset.path_to_folder
        data = load_act_assist(act_assist_path)

        df_devs, df_acts = data['devices'], data['activities']

        states = (dev_type_trigger == 'state')

        # Replace long names with friendly names
        har = HARest()
        mapping = har.get_friendly_names(df_devs[DEVICE].unique())
        mapping  = {k: k if v is None else v for k, v in mapping.items()}
        df_devs[DEVICE] = df_devs[DEVICE].map(mapping)

        # Only show one day into the past
        tz_offset = pd.Timestamp.now(srv.time_zone).utcoffset()
        start_time = pd.Timestamp.now() - pd.Timedelta('1D') + tz_offset
        df_devs, df_acts = select_timespan(df_devs, df_acts, start_time=start_time)

        fig_and = activities_and_devices(df_devs, df_acts, states=states)
        return fig_and, act_assist_path

app_dashboard = build_app()