from flask import Flask, render_template, session
from flask import request as flask_req
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'


@app.route('/')
def session_key():
    return render_template('home.html', desc="API Key", name="apikey")


@app.route('/search', methods=['POST', 'GET'])
def symbolSearch():
    if flask_req.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if flask_req.method == 'POST':
        apikey = flask_req.form['apikey']
        session['apikey'] = apikey
        session['symbols'] = []
        return render_template('search.html')


@app.route('/symbols_found', methods=['POST', 'GET'])
def symbolsFound():
    if flask_req.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if flask_req.method == 'POST':
        symbolsearch = flask_req.form['symbol']
        results = requests.get('https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords='+symbolsearch+'&apikey='+session['apikey'])
        if results.status_code == 200:
            usable_results = json.loads(results.content)
            session['symbols'] = usable_results["bestMatches"]
            index_nb = 0
            table_string = ""
            for elem in usable_results["bestMatches"]:
                table_string += "<tr><td>"+elem['1. symbol']+"</td>"+"<td>"+elem['2. name']+"</td>"+"<td>"+"<a href='/s"+str(index_nb)+"'>"+"Select</a></td></tr>\n"
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
    display_str = ""
    display_str += "<li>symbol : " + session['symbols'][session['idx']]['1. symbol'] + "</li>\n"
    display_str += "<li>name : " + session['symbols'][session['idx']]['2. name'] + "</li>\n"
    display_str += "<li>type :" + session['symbols'][session['idx']]['3. type'] + "</li>\n"
    display_str += "<li>region :" + session['symbols'][session['idx']]['4. region'] + "</li>\n"
    display_str += "<li>marketOpen : " + session['symbols'][session['idx']]['5. marketOpen'] + "</li>\n"
    display_str += "<li>marketClose : " + session['symbols'][session['idx']]['6. marketClose'] + "</li>\n"
    display_str += "<li>timezone : " + session['symbols'][session['idx']]['7. timezone'] + "</li>\n"
    display_str += "<li>currency : " + session['symbols'][session['idx']]['8. currency'] + "</li>\n"
    display_str += "<li>matchScore " + session['symbols'][session['idx']]['9. matchScore'] + "</li>\n"
    return render_template('details.html', details=display_str)


@app.route('/timeframes', methods=['POST', 'GET'])
def selected_timeframe():
    return render_template('timeframechoice.html')


@app.route('/timeframe_intraday', methods=['POST', 'GET'])
def timeframe_intraday():
    results = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol="+session['symbols'][session['idx']]['1. symbol']+"&interval=5min&apikey="+session['apikey'])
    if results.status_code == 200:
        table_header = "<tr><th>time</th><th>open</th><th>high</th><th>low</th><th>close</th><th>volume</th></tr>\n"
        usable_results = json.loads(results.content)
        display_str = ""
        for k, val in usable_results["Time Series (5min)"].items():
            display_str += '<tr class="'+c+'"><td>'+k+"</td>"
            for k2, v2 in val.items():
                display_str += "<td>"+v2+"</td>"
            display_str += "</tr>\n"
        display_str = table_header + display_str
        return render_template('table.html', tablecontent=display_str)
    else:
        return "Something went wrong : "+str(results.status_code)


@app.route('/timeframe_daily', methods=['POST', 'GET'])
def timeframe_daily():
    results = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="+session['symbols'][session['idx']]['1. symbol']+"&apikey="+session['apikey'])
    if results.status_code == 200:
        table_header = "<tr><th>time</th><th>open</th><th>high</th><th>low</th><th>close</th><th>volume</th></tr>\n"
        usable_results = json.loads(results.content)
        display_str = ""
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
            display_str += "<li>"+k+" : "+val+"</li>\n"
        return render_template('details.html', details=display_str)
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
    session.pop('apikey', None)
    return "You have been successfully logged out"


if __name__ == '__main__':
    app.run(host='localhost', port=5000)
