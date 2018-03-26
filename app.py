import os
import quandl
import pandas as pd
from flask import Flask, render_template, flash, request
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from boto.s3.connection import S3Connection

app = Flask(__name__)
s3 = S3Connection(os.environ['APIKEY_DATA'])
def create_figure(stock_ticker,s1):
    dates=[]
    for i in range(1,29):
        dates.append('2018-02-'+str(i))
    dates=','.join(dates)
    quandl.ApiConfig.api_key = s3
    aa=quandl.get_table('WIKI/PRICES', ticker=stock_ticker, date=dates)
    days=aa.date.dt.day
    # create a new plot with a title and axis labels
    p = figure(title="Quandl Wiki EOD Stock Price - Feb 2017",
        x_axis_label='date', y_axis_label='Price (Dollars)')
    l_color = ['blue','red','green','orange']

    ydata = ['open','adj_open','close','adj_close'];
    # add a line renderer with legend and line thickness
    for i in range(4):
        if s1[i] == '1':
            p.line(days, aa.loc[:,ydata[i]], legend=stock_ticker+':'+ydata[i],
                    line_color=l_color[i], line_width=2)
    return p

@app.route('/')
def inputdata():
    return render_template('stock_input.html')

@app.route("/result",methods = ['GET','POST'])
def resultpage():
    # Create the plot
    select = request.form.get('ticker')
    s1 = list(map(request.form.get,('C_P','AC_P','O_P','AO_P')))
    p = create_figure(select,s1)
    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    script, div = components(p)
    return render_template(
        'result.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
    )

if __name__ == "__main__":
	port = int(os.environ.get("PORT",5000))
	app.run(host='0.0.0.0',port=port,debug=True)
