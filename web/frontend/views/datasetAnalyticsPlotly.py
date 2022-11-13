import dash
from dash import dcc, html

from django_plotly_dash import DjangoDash

from dash import Dash, html, dcc, Input, Output, State
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from pyadlml.dataset.plotly.acts_and_devs import activities_and_devices
from pyadlml.dataset.plotly.dashboard.layout import _buttons_to_use
from pyadlml.dataset.plotly.dashboard.dashboard import dashboard
import plotly.graph_objs as go

from pyadlml.dataset import load_act_assist



def build_app(df_acts, df_devs, name=''):
    app = DjangoDash('dashboard', external_stylesheets=[dbc.themes.BOOTSTRAP])

    dashboard(app, name, True, df_acts, df_devs, None, None)


