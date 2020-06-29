from flask import Flask, render_template, request, redirect
import json
import requests
import pandas as pd
from bokeh.plotting import figure, show
from bokeh.io import output_file
from bokeh.resources import CDN
from bokeh.models import ColumnDataSource, Range1d
from bokeh.embed import file_html, components
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/graph', methods=["POST", "GET"])
def plotmaker():
    sym = request.form['sym']
    start = request.form['start']
    fromDate=datetime.strptime(start, '%Y-%m-%d')
    today = datetime.today()
    diff =  today - fromDate
    ndays=diff.days*5//7
    params = {
        'apikey': '{R4T5DKYNBGNXP596}',
        'symbol':sym,
        'outputsize' : 'full'
      }
    r = requests.get(
          'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED',params=params)
    d=r.json()['Time Series (Daily)']
    ds=pd.DataFrame.from_dict(d,orient='index')
    ds.iloc[:]=ds[:].astype(float)


    source = ColumnDataSource(ds.head(ndays))
    time0 = source.data['index'].tolist()
    date=pd.to_datetime(time0)
    x=date
    y1=source.data['1. open'].tolist()
    y2=source.data['4. close'].tolist()
    y3=source.data['5. adjusted close'].tolist()
    y4=source.data['3. low'].tolist()
    y5=source.data['2. high'].tolist()
    ymin=ds['3. low'][0:ndays].min()
    ymax=ds['2. high'][0:ndays].max()
    p = figure(x_axis_type="datetime", plot_width=800)
    p.title.text = '*Click legend to mute/unmute lines.'
    p.y_range = Range1d(ymin-5,ymax+25)
    p.line(x, y1, color='blue', legend_label='Opening Price', alpha=0.8,
               muted_color='blue', muted_alpha=0.07)
    p.line(x, y2, color='red', legend_label='Closing Price', alpha=0.8,
               muted_color='red', muted_alpha=0.07)
    p.line(x, y3, color='green', legend_label='Adjusted Closing Price', alpha=0.8,
               muted_color='green', muted_alpha=0.07)
    p.line(x, y4, color='orange', legend_label='Lowest Daily Price', alpha=0.8,
               muted_color='orange', muted_alpha=0.07)
    p.line(x, y5, color='black', legend_label='Highest Daily Price', alpha=0.8,
               muted_color='black', muted_alpha=0.07)
    p.legend.location = "top_left"
    p.legend.click_policy="mute"

    p.xaxis.axis_label = "Date"
    p.xaxis.axis_label_text_font_size = "20pt"

    p.yaxis.axis_label = "Stock Price in USD"
    p.yaxis.axis_label_text_font_size = "20pt"

    script, div = components(p)
    cdn_js=CDN.js_files[0]
    cdn_css=CDN.css_files
    return render_template("graph.html", script=script, div=div,cdn_js=cdn_js,cdn_css=cdn_css)





@app.route('/about')
def about():
  return render_template('about.html')

if __name__ == '__main__':
  app.run(port=33507)
