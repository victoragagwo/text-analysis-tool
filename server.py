from flask import Flask, abort, request
from stockAnalyze import getCompanyStockInfo
from analyze import analyzeText
from flask_cors import CORS
import json
import requests

app=Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def healthCheck():
    return 'Flask server is up and running'

@app.route('/analyze-stock/<ticker>', methods=['GET'])
def analyzeStock(ticker):
    
    if ticker == 'TEST':  # Optional: allow test data with TEST ticker
        with open('test/result.json', encoding='utf-8') as f:
            return json.load(f)
    
    if len(ticker) > 5 or not ticker.isidentifier():
        abort(400, "Invalid ticker symbol")
    try:
        analysis = getCompanyStockInfo(ticker)
    except NameError as e:
        abort(404, e)
    except:
        abort(500, "Something went wrong running the stock analysis.")
    return analysis

@app.route('/analyze-text', methods=['POST'])
def analyzeTextHandler():
    data = request.get_json()
    if "text" not in data or not data["text"]:
        abort(400, "No text provided to analyze.")
    analysis = analyzeText(data["text"])
    return analysis

@app.route('/api/quotes', methods=['GET'])
def getQuotes():
    try:
        response = requests.get('https://type.fit/api/quotes')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        abort(500, "Failed to fetch quotes from external API")

if __name__ == '__main__':
    app.run()