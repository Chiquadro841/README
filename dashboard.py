import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.graph_objects as go
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Carica i dati dal file CSV
data = pd.read_csv('sp500_monthly_data.csv')

# Converti la colonna 'Date' in formato datetime e impostala come indice
data['Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d')
data.set_index('Date', inplace=True)

# Inizializza l'app Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("SARIMAX Prediction Dashboard"),

    # Box colorato per il form di inserimento
    html.Div([
        html.Label("Lunghezza della previsione (mesi):"),
        dcc.Input(id='periods', type='number', value=12, min=1),

        html.Br(),  # Linea vuota per spaziatura

        html.Label("Valore EPS (costante o lista separata da virgola):"),
        dcc.Input(id='eps', type='text', value='185'),

        html.Br(),

        html.Label("Valore FedFundsRate (costante o lista separata da virgola):"),
        dcc.Input(id='fedfunds', type='text', value='4.3'),

        html.Br(), html.Br(),

        # Bottone per aggiungere una previsione
        html.Button('Aggiungi Previsione', id='submit', n_clicks=0)
    ], style={
        'backgroundColor': '#333333',
        'padding': '20px',
        'borderRadius': '10px',
        'color': 'white',
        'width': '400px',
        'margin': '20px auto'
    }),

    # Grafico per visualizzare le previsioni
    html.Div([
        dcc.Graph(id='forecast-graph', config={'scrollZoom': True})  # Assicurati che scrollZoom sia abilitato
    ], style={
        'width': '100%',
        'height': '80vh'  # Adatta l'altezza in base alle tue esigenze
    }),

    # Slider per comprimere/estendere la scala dell'asse Y
    html.Label("Scala Asse Y:"),
    dcc.Slider(
        id='y-scale-slider',
        min=0.5,
        max=2,
        step=0.1,
        value=1,
        marks={i: str(i) for i in range(1, 3)},
        tooltip={"placement": "bottom", "always_visible": True},
    ),

    # Memorizzare i dati delle previsioni per generare più scenari
    dcc.Store(id='stored-data', data=[]),
    dcc.Store(id='xaxis-range', data=None)
])

@app.callback(
    Output('stored-data', 'data'),
    Output('forecast-graph', 'figure'),
    Output('xaxis-range', 'data'),
    Input('submit', 'n_clicks'),
    Input('y-scale-slider', 'value'),
    State('periods', 'value'),
    State('eps', 'value'),
    State('fedfunds', 'value'),
    State('stored-data', 'data'),
    State('xaxis-range', 'data'),
    State('forecast-graph', 'relayoutData')
)
def update_forecast(n_clicks, y_scale, periods, eps, fedfunds, stored_data, xaxis_range, relayout_data):
    trigger = dash.callback_context.triggered[0]['prop_id'].split('.')[0]

    # Verifica se l'asse X è stato modificato dallo zoom/pan
    if relayout_data and 'xaxis.range[0]' in relayout_data:
        xaxis_range = [relayout_data['xaxis.range[0]'], relayout_data['xaxis.range[1]']]

    if trigger == 'submit' and n_clicks > 0:
        # Prepara le future date per la previsione
        future_dates = pd.date_range(start=data.index[-1] + pd.DateOffset(months=1), periods=periods, freq='M')

        # Gestisce i valori di EPS
        try:
            eps_values = [float(e) for e in eps.split(',')]
        except:
            eps_values = [float(eps)] * periods

        # Gestisce i valori di FedFundsRate
        try:
            fedfunds_values = [float(f) for f in fedfunds.split(',')]
        except:
            fedfunds_values = [float(fedfunds)] * periods

        # Crea il DataFrame per i dati esogeni futuri
        future_exog = pd.DataFrame({'Eps': eps_values, 'FedFundsRate': fedfunds_values}, index=future_dates)

        # Modello SARIMAX
        order = (1, 1, 1)
        seasonal_order = (1, 1, 1, 12)

        model = SARIMAX(data['Close'], exog=data[['Eps', 'FedFundsRate']], order=order, seasonal_order=seasonal_order)
        results = model.fit()

        # Previsione
        forecast = results.get_forecast(steps=periods, exog=future_exog)
        forecast_mean = forecast.predicted_mean
        forecast_ci = forecast.conf_int()

        # Memorizza i risultati della previsione
        new_forecast = {
            'dates': future_dates,
            'mean': forecast_mean,
            'ci_lower': forecast_ci.iloc[:, 0],
            'ci_upper': forecast_ci.iloc[:, 1]
        }
        stored_data.append(new_forecast)

    # Crea il grafico con Plotly
    fig = go.Figure()

    # Aggiungi i dati storici
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines+markers', name='Storico'))

    # Aggiungi ogni scenario di previsione
    for i, scenario in enumerate(stored_data):
        fig.add_trace(go.Scatter(x=scenario['dates'], y=scenario['mean'], mode='lines+markers', name=f'Previsione {i+1}'))
        fig.add_trace(go.Scatter(
            x=scenario['dates'],
            y=scenario['ci_lower'],
            mode='lines',
            line=dict(color='lightpink', width=0),
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=scenario['dates'],
            y=scenario['ci_upper'],
            mode='lines',
            fill='tonexty',
            fillcolor='rgba(255, 182, 193, 0.4)',
            line=dict(color='lightpink', width=0),
            name=f'Intervallo di Confidenza {i+1}'
        ))

    # Configura il layout del grafico
    y_min = data['Close'].min() * y_scale
    y_max = data['Close'].max() * y_scale

    fig.update_layout(
        title='Previsione Close con SARIMAX',
        xaxis_title='Date',
        yaxis_title='Close',
        hovermode='x unified',
        dragmode='zoom',  # Permette il zoom con il mouse
        autosize=True,
        xaxis=dict(
            rangeslider=dict(visible=False),  # Disabilita lo slider se non necessario
            showline=True,
            range=xaxis_range  # Usa il range attuale dell'asse X
        ),
        yaxis=dict(
            showline=True,
            range=[y_min, y_max]  # Aggiorna il range dell'asse Y in base al valore dello slider
        )
    )

    return stored_data, fig, xaxis_range

if __name__ == '__main__':
    app.run_server(debug=True)
