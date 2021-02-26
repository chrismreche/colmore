from flask import Flask, render_template, session
from flask import request as flask_req
import requests
import json
from app import app

@app.route('/')
def session_key():
    return render_template('home.html', desc="API Key", name="apikey")


@app.route('/search', methods=['POST', 'GET'])
def symbolSearch():
    if flask_req.method == 'GET':
        if not session['apikey']:
            return f"The URL /data is accessed directly. Try going to '/' to submit form"
        else:
            return render_template('search.html')
    if flask_req.method == 'POST':
        apikey = flask_req.form['apikey']
        session['apikey'] = apikey
        session['symbols'] = []
        return render_template('search.html')


@app.route('/symbols_found', methods=['POST', 'GET'])
def symbolsFound():
    
    if flask_req.method == 'GET':
        index_nb = 0
        table_string = ""
        for elem in session['symbols']:
            table_string += "<tr><td>"+elem['1. symbol']+"</td>"+"<td>"+elem['2. name']+"</td>"+"<td>"+"<a href='/s"+str(index_nb)+"' class='trhova'>"+"Select</a></td></tr>\n"
            #table_string += "<tr class='trclick'><td>"+elem['1. symbol']+"</a></td>"+"<td>"+"<a href='/s"+str(index_nb)+"'>"+elem['2. name']+"</a></td>"+"</tr>\n"
            index_nb += 1
        return render_template('symbols.html', tablecontent=table_string)
    if flask_req.method == 'POST':
        symbolsearch = flask_req.form['symbol']
        results = requests.get('https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords='+symbolsearch+'&apikey='+session['apikey'])
        if results.status_code == 200:
            usable_results = json.loads(results.content)
            session['symbols'] = usable_results["bestMatches"]
            index_nb = 0
            table_string = ""
            for elem in usable_results["bestMatches"]:
                table_string += "<tr><td>"+elem['1. symbol']+"</td>"+"<td>"+elem['2. name']+"</td>"+"<td>"+"<a href='/s"+str(index_nb)+"' class='trhova'>"+"Select</a></td></tr>\n"
                #table_string += "<tr class='trclick'><td>"+"<a href='/s"+str(index_nb)+"'>"+elem['1. symbol']+"</a></td>"+"<td>"+"<a href='/s"+str(index_nb)+"'>"+elem['2. name']+"</a></td>"+"</tr>\n"
                index_nb += 1
            return render_template('symbols.html', tablecontent=table_string)
        else:
            return "Something went wrong : "+str(results.status_code)


@app.route('/s<int:symb_idx>')
def selected_symbol(symb_idx):
    name = session['symbols'][int(symb_idx)]['2. name']
    symbol_id = session['symbols'][int(symb_idx)]['1. symbol']
    session['idx'] = int(symb_idx)
    return render_template('actchoice.html', name=name, symbol_id=symbol_id)


@app.route('/details', methods=['POST', 'GET'])
def companyDetails():
    usable_results = session['symbols'][session['idx']]
    display_str = ""
    for k, val in usable_results.items():
        display_str += "<tr><td>"+k[3:].capitalize()+"</td><td>"+val+"</td></tr>\n"
    return render_template('table.html', tablecontent=display_str) #details


@app.route('/timeframes', methods=['POST', 'GET'])
def selected_timeframe():
    return render_template('timeframechoice.html')


@app.route('/timeframe_intraday', methods=['POST', 'GET'])
def timeframe_intraday():
    results = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol="+session['symbols'][session['idx']]['1. symbol'].lower()+"&interval=5min&apikey="+session['apikey'])
    if results.status_code == 200:
        table_header = "<tr><th>time</th><th>open</th><th>high</th><th>low</th><th>close</th><th>volume</th></tr>\n"
        usable_results = json.loads(results.content)
        display_str = ""
        for k, val in usable_results['Time Series (5min)'].items():
            display_str += '<tr><td>'+k+"</td>"
            for k2, v2 in val.items():
                display_str += "<td>"+v2+"</td>"
            display_str += "</tr>\n"
        display_str = table_header + display_str
        return render_template('table.html', tablecontent=display_str)
    else:
        return "Something went wrong : "+str(results.status_code)


@app.route('/timeframe_daily', methods=['POST', 'GET'])
def timeframe_daily():
    print(session['symbols'][session['idx']]['1. symbol'])
    results = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="+session['symbols'][session['idx']]['1. symbol']+"&apikey="+session['apikey'])
    if results.status_code == 200:
        table_header = "<tr><th>time</th><th>open</th><th>high</th><th>low</th><th>close</th><th>volume</th></tr>\n"
        usable_results = json.loads(results.content)
        display_str = ""
        print(usable_results)
        for k, val in usable_results["Time Series (Daily)"].items():
            display_str += "<tr><td>"+k+"</td>"
            for k2, v2 in val.items():
                display_str += "<td>"+v2+"</td>"
            display_str += "</tr>\n"
        display_str = table_header + display_str
        return render_template('table.html', tablecontent=display_str)
    else:
        return "Something went wrong : "+str(results.status_code)


@app.route('/quote', methods=['POST', 'GET'])
def currentQuote():
    results = requests.get("https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol="+session['symbols'][session['idx']]['1. symbol']+"&apikey="+session['apikey'])
    if results.status_code == 200:
        usable_results = json.loads(results.content)
        display_str = ""
        for k, val in usable_results["Global Quote"].items():
            display_str += "<tr><td>"+k[4:].capitalize()+"</td><td>"+val+"</td></tr>\n"
        return render_template('table.html', tablecontent=display_str)		#details, details
    else:
        return "Something went wrong : "+str(results.status_code)


@app.route('/indicator')
def resultTable():
    results = requests.get("https://www.alphavantage.co/query?function=SMA&symbol="+session['symbols'][session['idx']]['1. symbol']+"&interval=weekly&time_period=10&series_type=open&apikey="+session['apikey'])
    if results.status_code == 200:
        table_header = "<th>time</th><th>SMA</th>\n"
        usable_results = json.loads(results.content)
        display_str = ""
        for k, val in usable_results["Technical Analysis: SMA"].items():
            display_str += "<tr><td>"+k+"</td>"+"<td>"+val["SMA"]+"</td></tr>\n"
        display_str = table_header + display_str
        return render_template('table.html', tablecontent=display_str)
    else:
        return "Something went wrong : "+str(results.status_code)


@app.route('/logout')
def popsession():
    print(session)
    session.pop('apikey', None)
    message = "<h3>You have been successfully logged out</h3>"
    return render_template('blank.html', message=message)

@app.errorhandler(500)
def InternalServerErr(error):
    message = "<h2>KaBoom</h2>\n<p>If you see this message, it means that something broke. Please email your mechanics to have a look on what we can do to fix it : christophe.reche@yahoo.com</p>"
    return render_template('blank.html', message=message)

@app.errorhandler(400)
def pageNotFound(error):
    message = "<h2>Where are we ?</h2>\n<p>If you see this message, you are lost ... the page you are trying to access cannot be found. As your wise satnav would say : Please make a U-turn. (Yes, I hate my satnav too for telling me such things!)</p>"
    return render_template('blank.html', message=message)

@app.errorhandler(403)
def accessDenied(error):
    message = "<h2>Sorry we're closed</h2>\n<p>If you see this message, you are being denied the access to this page. Go straight to jail, do not go pass go, do not collect money</p>"
    return render_template('blank.html', message=message)

@app.errorhandler(405)
def methodNotAllowed(error):
    message = "<h2>Do not ask for the impossible<h2>\n<p>Game Over. Please insert coin and try again : Method Not Allowed error striked again :-O</p>"
    return render_template('blank.html', message=message)

