from datetime import datetime
import json
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import analyze

def extractBasicInfo(data):
    keysToExtract = ['longName', 'website', 'sector', 'fullTimeEmployees', 'marketCap', 'totalRevenue', 'trailingEps']
    basicInfo = {}
    for key in keysToExtract:
        if key in data:
            basicInfo[key] = data[key]
        else:
            basicInfo[key] = ''
    return basicInfo

def getPriceHistory(company):
    historyDF = company.history(period='2mo')
    prices = historyDF['Open'].tolist()
    dates = historyDF.index.strftime('%Y-%m-%d').tolist()
    return {
        'price': prices,
        'date': dates
    }

def getEarningDates(company):
    earningsDatesDF = company.earnings_dates
    allDates = earningsDatesDF.index.strftime('%Y-%m-%d').tolist()
    dateObjects = [datetime.strptime(date, '%Y-%m-%d') for date in allDates]
    currentDate = datetime.now()
    futureDates = [date.strftime('%Y-%m-%d') for date in dateObjects if date > currentDate]
    return futureDates

def getCompanyNews(company):
    newsList = company.news
    allNewsArticles = []
    for newsDict in newsList:
        try:
            title = newsDict['content']['title']
            link = newsDict['content']['canonicalUrl']['url']
            newsDictToAdd = {
                'title': title,
                'link': link,
            }
            allNewsArticles.append(newsDictToAdd)
        except KeyError:
            continue
    return allNewsArticles

def extractNewsArticleTextFromHtml(soup):
    allText = ''
    paragraphs = soup.find_all('p')
    for p in paragraphs:
        allText += p.get_text() + ' '
    return allText

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
def extractCompanyNewsArticles(newsArticles):
    allArticlesText = ''
    for newsArticle in newsArticles:
        url = newsArticle['link']
        try:
            page = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(page.text, 'html.parser')
            if not soup.find_all(string="Continue reading"):
                allArticlesText += extractNewsArticleTextFromHtml(soup)
        except Exception:
            pass
    return allArticlesText

def getCompanyStockInfo(tickerSymbol):
    # Get data from Yahoo Finance API
    company = yf.Ticker(tickerSymbol)

    # Get basic info on company
    basicInfo = extractBasicInfo(company.info)
    priceHistory = getPriceHistory(company)
    futureEarningDates = getEarningDates(company)
    newsArticles = getCompanyNews(company)
    newsArticlesAllText = extractCompanyNewsArticles(newsArticles)
    newsTextAnalysis = analyze.analyzeText(newsArticlesAllText)
    
    finalStockAnalysis = {
        'basicInfo': basicInfo,
        'priceHistory': priceHistory,
        'futureEarningDates': futureEarningDates,
        'newsArticles': newsArticles,
        'newsTextAnalysis': newsTextAnalysis
    }
    return finalStockAnalysis

# companyStockAnalysis = getCompanyStockInfo('MSFT')
# print(json.dumps(companyStockAnalysis, indent=4))