import base64
import io
import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px
from dash.dependencies import Input, Output, State

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return None
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")
        return None
    return df

external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1("Dashboard de Dados Quantitativos", className='m-4'),

    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Arraste e solte ou ',
            html.A('selecione um arquivo')
        ]),
        style={
            'width': '60%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '25px',
            'cursor': 'pointer'
        },
        multiple=False
    ),

    html.Div(id='graphs-container', style={'margin': '10px'})
])

@app.callback(
    Output('graphs-container', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_graphs(contents, filename):
    if contents is None:
        print("Nenhum conteúdo carregado.")
        return []

    df = parse_contents(contents, filename)

    if df is None:
        print("Erro ao parsear o conteúdo.")
        return []
    else:
        print("DataFrame carregado com sucesso.")
        print(df.head())

    print("Colunas do DataFrame:", df.columns)

    required_columns = ['Data do Fechamento', 'Serviço/Produto', 'Valor do Contrato', 'Taxa PJ - 6%', 'Lucro Líquido']
    if not all(col in df.columns for col in required_columns):
        print("As colunas necessárias não estão presentes no DataFrame.")
        return []

    df['Data do Fechamento'] = pd.to_datetime(df['Data do Fechamento']).dt.strftime('%d/%m/%Y')

    fig_bar = px.bar(
        df,
        x='Data do Fechamento',
        y='Valor do Contrato',
        color='Cliente',
        text='Valor do Contrato',
        title='Valor do Contrato',
        labels={'Data do Fechamento': 'Data do Fechamento (dia/mês/ano)', 'Valor do Contrato': 'Valor do Contrato (R$)'},
        text_auto=True
    )
    
    fig_bar.update_traces(texttemplate='%{text:.2f}', textposition='outside')

    fig_line = px.line(
        df,
        x='Data do Fechamento',
        y='Valor do Contrato',
        color='Cliente',
        markers=True,
        title='Valor do Contrato',
        labels={'Data do Fechamento': 'Data do Fechamento (dia/mês/ano)', 'Valor do Contrato': 'Valor do Contrato (R$)'}
    )

    fig_line.update_traces(mode='lines+markers')

    fig_tax_pj = px.line(
        df,
        x='Data do Fechamento',
        y='Taxa PJ - 6%',
        color='Cliente',
        markers=True,
        title='Taxa PJ - 6%',
        labels={'Data do Fechamento': 'Data do Fechamento (dia/mês/ano)', 'Taxa PJ - 6%': 'Taxa PJ - 6%'}
    )

    fig_tax_pj.update_traces(mode='lines+markers')

    fig_profit = px.line(
        df,
        x='Data do Fechamento',
        y='Lucro Líquido',
        color='Cliente',
        markers=True,
        title='Lucro Líquido',
        labels={'Data do Fechamento': 'Data do Fechamento (dia/mês/ano)', 'Lucro Líquido': 'Lucro Líquido (R$)'}
    )

    fig_profit.update_traces(mode='lines+markers')

    return [
        html.Div([
            dcc.Graph(figure=fig_bar)
        ], style={'width': '49%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        html.Div([
            dcc.Graph(figure=fig_line)
        ], style={'width': '49%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        html.Div([
            dcc.Graph(figure=fig_tax_pj)
        ], style={'width': '49%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        html.Div([
            dcc.Graph(figure=fig_profit)
        ], style={'width': '49%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ]

if __name__ == '__main__':
    print("Iniciando o servidor Dash...")
    app.run_server(debug=True)
    print("Servidor Dash está em execução.")
