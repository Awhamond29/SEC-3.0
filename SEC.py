import multiprocessing
import random
import time
# from utils import WebscraperFunctions
import json
import requests
from datetime import datetime, timedelta
import os
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
import json
import winsound
import webbrowser
import urllib.parse
import re
import pandas as pd
import praw
import cloudscraper
from finvizfinance.quote import finvizfinance

headers_list = [
    {'User-Agent': 'Quant quant@quant.com'}, {'User-Agent': 'DataCorp johndoe@datacorp.com'},
    {'User-Agent': 'FinAnalytics janesmith@finanalytics.com'}, {'User-Agent': 'MarketInsights mikeb@marketinsights.org'},
    {'User-Agent': 'EquityResearch emilyd@equityresearch.net'}, {'User-Agent': 'InvestMate chrisw@investmate.io'},
    {'User-Agent': 'StockScan karent@stockscan.co'}, {'User-Agent': 'BondBuddy robertm@bondbuddy.com'},
    {'User-Agent': 'FundTracker lisaa@fundtracker.org'}, {'User-Agent': 'TradeWatch danielt@tradewatch.net'},
    {'User-Agent': 'AlphaBeta sarahl@alphabeta.com'}, {'User-Agent': 'QuantTools davidm@quanttools.io'}, 
    {'User-Agent': 'PortfolioPlus jamesr@portfolioplus.org'}, {'User-Agent': 'CapitalFlow patricial@capitalflow.net'},
    {'User-Agent': 'WealthWave stevenw@wealthwave.com'}, {'User-Agent': 'AssetGuard barbarah@assetguard.io'},
    {'User-Agent': 'RiskRadar keviny@riskradar.co'}, {'User-Agent': 'FinancePro angelak@financepro.org'},
    {'User-Agent': 'StockEdge brianh@stockedge.net'}, {'User-Agent': 'HedgeHub laurac@hedgehub.co'}
]

earnings_list = [
    'AAPL', 'ABNB', 'ADBE', 'AFRM', 'AI', 'AMAT', 'AMD', 'AMZN', 'APP', 'ARM', 'AVGO', 'BA', 'BYND',
    'CAVA', 'CCL', 'CMG', 'COIN', 'COST', 'CRM', 'CRWD', 'CSCO', 'CVNA', 'DDOG', 'DELL', 'DIS', 'DOCU', 'DKNG',
    'ENPH', 'F', 'FDX', 'GME', 'GOOGL', 'GPS', 'GTLB', 'HIMS', 'HOOD', 'HPQ', 'HUBS', 'IBM', 'INTC',
    'LEVI', 'LULU', 'LYFT', 'MDB', 'MELI', 'META', 'MRVL', 'MSFT', 'MSTR', 'MU', 'NFLX', 'NKE', 'NVO',
    'NVAX', 'NVDA', 'NXPI', 'ON', 'ORCL', 'PANW', 'PATH', 'PDD', 'PINS', 'PLTR', 'PYPL', 'QCOM', 'RBLX',
    'RDDT', 'RH', 'RIVN', 'ROKU', 'S', 'SBUX', 'SEDG', 'SHOP', 'SMCI', 'SNAP', 'SNOW', 'SOFI', 'SQ',
    'TGT', 'TMDX', 'TSLA', 'TTD', 'U', 'UAL', 'UBER', 'ULTA', 'UPST', 'VSCO', 'WBA', 'WDAY', 'WSM',
    'XYZ', 'ZM', 'ZS', 'IREN', 'EXPE', 'SNDK', 'SPCX'
]

extra = ['MDB', 'APP', 'CRCL', 'SNDK', 'Q', 'AFRM', 'MSGM', 'PLNT', 'QCLS', 'GPCR', 'SEZL', 'SRXH', 'SIDU', 'DJT', 'FLYX', 'RVSN', 'GELS', 'ROMA', 'ROLR', 'AUID', 'CJMD', 'FUSE', 'LIMN', 'EVMN' , 'BETA', 'QNCX', 'ELAN',
         'RIME', 'GXAI', 'OLB', 'RXT', 'NAK', 'LUNR', 'EOSE','SABR', "TMDE", "TPET", "BATL", 'TURB', "UESG", 'MOBX', 'PRSO', 'CYN', 'KALA', 'DOMO' , 'CDXS', 'POLA', 'BMBL', 'TLYS', 'SLAI', 'AAOI', 'HIMX', 'LITE', 'COHR', 'LAES',
         'RIVN', 'HOOD', 'BFRG', 'OWL' , 'SKYQ', 'TMDE', 'BIRD', 'MYSE', "BYND", 'CLIK', 'FFAI', 'POET', 'NVTS', 'RUM', 'ICCM', 'CBRS']

filter_out = ['GABC', 'AHT', 'BHR', 'IBCP', 'MGEE', 'TPB', 'RM', "YORW", 'CBL', "DXPE", 'IIIN', 'STBA']

def log_error(error_log, error_message):
    timestamp = datetime.now()
    error_log.append((error_message, timestamp))

def should_terminate(error_log, threshold=15, time_frame=2):
    current_time = datetime.now()
    time_limit = current_time - timedelta(minutes=time_frame)
    error_count = sum(1 for _, ts in error_log if ts >= time_limit)
    # print(f"Current error count: {error_count}")  # Debug print
    return error_count >= threshold

CSV_FILES = [
    "S&P500.csv",
    "Russell2000.csv",
    "snp400.csv",
    "sp600_subset.csv",
    "misc_tickers.csv"
]
#print(os.getcwd())

TICKER_COL_CANDIDATES = {"ticker", "tickers", "symbol", "symbols", "Ticker", "Tickers", "Symbol", "Symbols"}

def load_tickers_from_csv(path):
    try:
        df = pd.read_csv(path, encoding="utf-8", engine="python")
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="latin-1", engine="python")

    for c in df.columns:
        if c in TICKER_COL_CANDIDATES:
            col_text = c

    # Normalize
    tickers = (
        df[col_text]
        .astype(str)
        #.str.strip()
        .str.upper()
        .replace({"": None, "NAN": None})
        .dropna()
        .tolist()
    )
    # Keep only things that look like tickers (incl. class shares like BRK.B / MOG.A)

    return tickers

#print(load_tickers_from_csv("S&P500.csv"))
#print(load_tickers_from_csv("Russell2000.csv"))
#print(load_tickers_from_csv("snp400.csv"))
#print(load_tickers_from_csv("sp600_subset.csv"))

#all_tickers = list(chain.from_iterable(load_tickers_from_csv(f) for f in CSV_FILES))
tickers = []

for file in CSV_FILES:
    file_tickers = load_tickers_from_csv(file)
    for ticker in file_tickers:
        tickers.append(ticker)

for ticker in extra:
    tickers.append(ticker)

#print(all_tickers)
all_tickers = sorted(set(tickers))
print(all_tickers)

# open json file
def open_json(main_json_path):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(main_json_path), exist_ok=True)
    # Load the main JSON file
    try:
        with open(main_json_path, 'r') as file:
            main_data = json.load(file)
            return main_data
    except (FileNotFoundError, json.JSONDecodeError):
        main_data = []
        return main_data
    
def open_txt(txt_path):
    try:
        with open(txt_path, 'r') as file:
            txt_data = file.read()
            return txt_data
    except FileNotFoundError:
        txt_data = []
        return txt_data
    
def check_new_filing(filing_urls_path, new_data, filing_urls_txt_file):
    # # Convert string to list if it's a string
    # if isinstance(filing_urls_txt_file, str):
    #     filing_urls_txt_file = filing_urls_txt_file.split('\n') if filing_urls_txt_file else []
        
    # if not any(item == new_data for item in filing_urls_txt_file):
    #     filing_urls_txt_file.append(new_data)
    #     # Write as newline-separated text file
    #     with open(filing_urls_path, 'w') as file:
    #         file.write('\n'.join(filing_urls_txt_file))
    #     return True
    # else:
    #     return False
    
    # Convert string to list if it's a string
    # if isinstance(filing_urls_txt_file, str):
    #     filing_urls_txt_file = filing_urls_txt_file.split('\n') if filing_urls_txt_file else []
        
    # if not any(item == new_data for item in filing_urls_txt_file):
    #     filing_urls_txt_file.append(new_data)
    #     # Write as newline-separated text file
    #     with open(filing_urls_path, 'w') as file:
    #         file.write('\n'.join(filing_urls_txt_file))
    #     return True
    # else:
    #     return False
    

        # Convert string to list if it's a string
    if isinstance(filing_urls_txt_file, str):
        filing_urls_txt_file = filing_urls_txt_file.split('\n') if filing_urls_txt_file else []
    
    # Remove any empty strings from the list
    filing_urls_txt_file = [url for url in filing_urls_txt_file if url]
        
    if new_data not in filing_urls_txt_file:
        # Append new URL and immediately write to file
        with open(filing_urls_path, 'a') as file:
            file.write(new_data + '\n')
        return True
    return False

# compare most recently scraped headline to most recently stored headline (in the json file)
# print new headline, update json file, and return true if headline is new (not in json file)
def update_main_json(main_json_path, new_data, main_data):
    # Check if the new data already exists in the main JSON
    new_data_dict = json.loads(new_data)
    if not any(item['title'] == new_data_dict for item in main_data):
        # print(new_data_dict['timestamp'] + '  |  ' + new_data_dict['title'] + '  |  ' + new_data_dict['source'] + '  |  ' + new_data_dict['url'])
        
        main_data.append(new_data_dict)
        
        # Overwrite the main JSON file with the updated data
        with open(main_json_path, 'w') as file:
            json.dump(main_data, file, indent=4)
        # print("New data added to the main JSON.")
        # print(' ')
        return True
    else:
        # print("Data already exists in the main JSON.")
        return False
    
def update_13f_json(json_path_13f, new_data, json_data_13f):
    new_data_dict = json.loads(new_data)
    # if dict key does not exist in any dict keys in json file, add it
    if not any(item['Company'] == new_data_dict['Company'] for item in json_data_13f):
        json_data_13f.append(new_data_dict)
        with open(json_path_13f, 'w') as file:
            json.dump(json_data_13f, file, indent=4)
        return True
    else:
        return False
    
def update_13f_json_value(json_path_13f, new_data, json_data_13f):
    new_data_dict = json.loads(new_data)
    # Check if company exists in json file
    for item in json_data_13f:
        if item['Company'] == new_data_dict['Company']:

            # Calculate difference between new and old value
            value_difference = int(new_data_dict['Value']) - int(item['Value'])
            # Update the value in json
            item['Value'] = new_data_dict['Value']
            with open(json_path_13f, 'w') as file:
                json.dump(json_data_13f, file, indent=4)
            return value_difference
            
    # If company not found, add it and return None since no difference
    json_data_13f.append(new_data_dict)
    with open(json_path_13f, 'w') as file:
        json.dump(json_data_13f, file, indent=4)
    return None
    
def ticker_search(query):
    # instantiate chrome session
    chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
    query = urllib.parse.quote_plus(query + ' stock ticker')
    # Create and open Google search URL
    url = f"https://www.google.com/search?q={query}"
    webbrowser.get(chrome_path).open(url)

def alert(path):

    if path != None:
        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)

    else:
        # play sound
        frequency = 800  # Frequency in Hertz (e.g., 440Hz is the note A4)
        duration = 200  # Duration in milliseconds (1000ms = 1 second)
        winsound.Beep(frequency, duration)

def open_link(url):
    chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
    webbrowser.get(chrome_path).open(url)

def scrape_sec():
    
    error_log = []

    while True:
        data = None  # reset each iteration so error handlers never hit a NameError
        try:
            # send http request to rss feed
            # url = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent`&`CIK=&type=8-k&company=&dateb=&owner=include&start=0&count=40&output=atom'  # 8-k url
            url = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=&company=&dateb=&owner=include&start=0&count=40&output=atom'
            response = requests.get(url, headers=random.choice(headers_list))
            # successful request

            if response.status_code == 200:
                filing_response_html = BeautifulSoup(response.content, 'xml')
                entries = filing_response_html.find_all('entry', limit=5)

                # send http request to most recent filing
                if entries:
                    for entry in entries:
                        filing_title = entry.find('title').text
                        filing_url = entry.find('link')['href']

                        # '''FOR TESTING PURPOSES'''
                        # filing_title = 'NVIDIA 0001045810 13D'
                        # filing_url = 'https://www.sec.gov/Archives/edgar/data/2055515/000121390025013082/0001213900-25-013082-index.htm'
                        # '''FOR TESTING PURPOSES'''

                        # check if filing is new
                        # __file__ is a special variable that contains the path to the current Python script file
                        script_dir = os.path.dirname(os.path.abspath(__file__))
                        filing_urls_txt_file = open_txt(os.path.join(script_dir, 'filing_urls.txt'))
                        new_filing_boolean = check_new_filing(os.path.join(script_dir, 'filing_urls.txt'), filing_url, filing_urls_txt_file)

                        if new_filing_boolean == True:

                            if '8-K' in filing_title:

                                # convert html to txt so we can do text parsing
                                # filing_txt_url = filing_url.replace("-index.htm", ".txt").replace("-index.html", ".txt")
                                filing_txt_url = re.sub(r'-index\.html?$', '.txt', filing_url)
                                filing_response_txt = requests.get(filing_txt_url, headers=random.choice(headers_list))

                                filing_response_txt_soup = BeautifulSoup(filing_response_txt.content, "lxml")
                                filing_object_txt = str(filing_response_txt_soup)

                                filing_object_txt_soup = filing_response_txt_soup.get_text()

                                # get ticker, return empty json if no ticker
                                if "dei:tradingsymbol" in filing_object_txt:
                                    ticker = filing_object_txt.split("dei:tradingsymbol")[1].split(">")[1].split("</")[0]
                                else:
                                    # go to next filing
                                    continue
                                #print(ticker)
                                #if ticker not in earnings_list:
                                #    continue

                                if any(keyword in filing_title for keyword in ["OTCQB", "Federal Home Loan Bank", "Trust", "Fund", "Capital"]):
                                    # go to next filing
                                    continue

                                #if len(ticker) > 50:
                                #    ticker = ""

                                #if ticker != "":
                                if ticker in all_tickers:
                                    #data = finviz(ticker)

                                    #if not data or len(data) < 3:
                                    #    continue

                                    #elif data[0] >= (5.0 * 1000000000):
                                    #    title = "Ticker: " + ticker + '   |   ' + filing_title
                                    #elif data[0] >= (1.0 * 1000000000) and data[2] >= 2000000:
                                    #    title = "Ticker: " + ticker + '   |   ' + filing_title
                                    #elif data[1] >= 15:
                                    #    title = "Ticker: " + ticker + '   |   ' + filing_title
                                    #elif data[1] >= 8 and data[2] >= 2000000:
                                    #    title = "Ticker: " + ticker + '   |   ' + filing_title
                                    #elif data[2] >= (4.0 * 1000000):
                                    #    title = "Ticker: " + ticker + '   |   ' + filing_title
                                    #else:
                                    #    continue

                                    dash_index = filing_title.index(' - ')
                                    parenthesis_index = filing_title.index('(')
                                    filing_title = filing_title[dash_index + 2:parenthesis_index].strip()
                                    #title = "Ticker: " + ticker + '   |   ' + filing_title
                                    title = '8-K | ' + ticker + " | " + filing_title

                                else:
                                    continue
                                # get 8k content summary from Item Informatiom section
                                filing_items = filing_response_txt_soup.text.split('ITEM INFORMATION:		')[1:]
                                filing_item_list = [item.split('FILED AS OF DATE:')[0].strip('\n') if i == len(filing_items)-1
                                            else item.strip('\n')
                                            for i, item in enumerate(filing_items)]
                                
                                #if any(phrase == "Financial Statements and Exhibits" for phrase in filing_item_list) and (ticker not in earnings_list):
                               ##     continue
                                # remove financial statements from list
                                filing_item_list = [s for s in filing_item_list if s != "Financial Statements and Exhibits"]
                                #print("item-list for 8-k: ")
                                #print(filing_item_list)
                                filing_object_txt_soup = filing_object_txt_soup.replace("\n"," ").replace("     "," ").replace("    "," ").replace("   "," ").replace("  "," ")


                                for item in filing_item_list:
                                    # skip document sections that have these titles. The title will be in the output but none of the content underneath the title
                                    skip_items = [
                                        "Submission of Matters to a Vote",
                                        "Submission of Matters to a Vote of Security Holders"
                                        "Amendments to Articles of Incorporation",
                                        "Material Modifications to Rights of Security Holders",
                                        "Creation of a Direct Financial Obligation",
                                        "Results of Operations and Financial Condition",
                                        "Financial Statements and Exhibits"

                                    ]

                                    if any(phrase in item for phrase in skip_items):
                                        continue

                                    item = item[:24]
                                    start_index = filing_object_txt_soup.find(item)
                                    second_index = filing_object_txt_soup.find(item, (start_index + len(item) + 400) + len(item))
                                    if "The information contained in Item 7.01 Regulation FD Disclosure" in filing_object_txt_soup:
                                        second_index = filing_object_txt_soup.find(item, (second_index + len(item) + 400) + len(item))
                                    end_index = filing_object_txt_soup.find("SIGNATURES", second_index)

                                    # if any(phrase in item for phrase in skip_items):
                                    #     extracted_text = ""
                                    # else:
                                    text_slice = filing_object_txt_soup[second_index:end_index] if end_index != -1 else filing_object_txt_soup[second_index:]
                                    extracted_text = text_slice.strip(".").replace("\n", "")[:300]
                                    sentences = extracted_text.split(".")
                                    four_sentence_text = ".".join(sentences[:4]).strip()  # includes header with a period after it
                                    
                                    # print('extracted text 1: ', extracted_text)
                                    # print('extracted 3 sentences: ', four_sentence_text)

                                    # Get the first sentence from the 8-K filing text to use as the section header
                                    #extracted_header = four_sentence_text.split(".")[0]
                                    # extracted_body = four_sentence_text.split(extracted_header)[1].strip(".").strip(" ")
                                    #sentences_after_header = four_sentence_text.split(extracted_header)[1].strip(".").strip(" ").split(".")
                                    #extracted_body = ".".join(sentences_after_header[:2]).strip()
                                    # print('extracted bpdy: ', extracted_body)
                                    #title += "\n" + "\033[1m" + extracted_header + "\033[1;m. " + '   |   ' + extracted_body + "\n"
                                    # title += '   |   ' + extracted_header + ': ' + extracted_text
                                    # print('title: ', title)

                                for doc_link_8k in BeautifulSoup(requests.get(filing_url, headers=random.choice(headers_list)).content,
                                                            "html.parser").find_all('a', href=True):
                                    if ".htm" in doc_link_8k.text and "htm" in doc_link_8k['href']:
                                        content_url = "https://www.sec.gov" + doc_link_8k['href']
                                        break
                                
                                if '8-K/A' in filing_title:

                                    data = {
                                        'timestamp': datetime.now().strftime("%H:%M:%S"),
                                        'title': title,
                                        'source': 'sec filing 8-k',
                                        'url': content_url,
                                    }
                                    # data = json.dumps(data)
                                    print(data['timestamp'] + ' |' + data['title'] + ' | ' + data['url'] + '\n')
                                    alert(os.path.join(os.path.dirname(script_dir), 'sound_alerts', '8ka_filing.wav'))
                                    main_8k_data = open_json(os.path.join(script_dir, 'sec.json'))
                                    update_main_json(os.path.join(script_dir, 'sec.json'), json.dumps(data), main_8k_data)
                                
                                else:

                                    data = {
                                        'timestamp': datetime.now().strftime("%H:%M:%S"),
                                        'title': title,
                                        'source': 'sec filing 8-k',
                                        'url': content_url,
                                    }
                                    # data = json.dumps(data)
                                    print(data['timestamp'] + ' | ' + data['title'] + ' | ' + data['url'] + '\n')

                                    skip_titles = [
                                        "Directors",
                                        "Submission of Matters to a Vote",
                                        "Amendments to Articles of Incorporation",
                                        "Material Modifications to Rights of Security Holders", 
                                        "Creation of a Direct Financial Obligation"
                                        #"Results of Operations and Financial Condition"
                                    ]
                                    
                                    if not any(title in data['title'] for title in skip_titles):
                                        open_link(content_url)
                                    
                                    alert(os.path.join(os.path.dirname(script_dir), 'sound_alerts', '8k_filing.wav'))
                                    main_8k_data = open_json(os.path.join(script_dir, 'sec.json'))
                                    update_main_json(os.path.join(script_dir, 'sec.json'), json.dumps(data), main_8k_data)

                            # if '6-K' in filing_title:
                            #     # convert html to txt so we can do text parsing
                            #     # filing_txt_url = filing_url.replace("-index.htm", ".txt").replace("-index.html", ".txt")
                            #     filing_txt_url = re.sub(r'-index\.html?$', '.txt', filing_url)
                            #     filing_response_txt = requests.get(filing_txt_url, headers=random.choice(headers_list))

                            #     filing_response_txt_soup = BeautifulSoup(filing_response_txt.content, "lxml")
                            #     filing_object_txt = str(filing_response_txt_soup).lower()

                            #     filing_object_txt_soup = filing_response_txt_soup.get_text()

                            #     keywords = ['providing the following updates', 'providing the following information', 'providing the following details',
                            #                 'providing an update', 'providing the following update', 'guidance', 'outlook', 'investigation', 'financail update',
                            #                 'demand', 'sales', 'revenue,' 'earnings', 'clinical', 'trial']
                                
                            #     # Find which keyword matched
                            #     matched_keyword = None
                            #     for keyword in keywords:
                            #         if keyword in filing_object_txt:
                            #             matched_keyword = keyword
                            #             break
                                
                            #     if matched_keyword:
                            #         data = {
                            #             'timestamp': datetime.now().strftime("%H:%M:%S"),
                            #             'title': filing_title + "    keyword match: " + matched_keyword,
                            #             'source': 'sec filing 6-k',
                            #             'url': filing_url,
                            #         }

                            #         print('\n' + data['timestamp'] + '  |  ' + data['title'] + '  |  ' + data['source'] + '  |  ' + data['url'] + '\n\n')
                            #         open_link(content_url)
                                
                            #         alert(os.path.join(os.path.dirname(script_dir), 'sound_alerts', '6k_filing.wav'))
                            #         main_8k_data = open_json(os.path.join(script_dir, 'sec.json'))
                            #         update_main_json(os.path.join(script_dir, 'sec.json'), json.dumps(data), main_8k_data)
                            #f (('10-Q' in filing_title) or ('10-K' in filing_title)) and ('NT 10-Q' not in filing_title) and ('NT 10-K' not in filing_title):
                            if (('10-Q' in filing_title) or ('10-K' in filing_title)) and ('NT 10-Q' not in filing_title) and ('NT 10-K' not in filing_title):
                                if ('super' in filing_title.lower() and 'micro' in filing_title.lower()) or ('smci' in filing_title.lower()) or ('0001375365' in filing_title.lower()):

                                    data_10q = {
                                        'timestamp': datetime.now().strftime("%H:%M:%S"),
                                        'title': filing_title,
                                        'source': 'SMCI 10-Q',
                                        'url': filing_url
                                    }

                                    data_10k = {
                                        'timestamp': datetime.now().strftime("%H:%M:%S"),
                                        'title': filing_title,
                                        'source': 'SMCI 10-K',
                                        'url': filing_url
                                    }

                                    # data = json.dumps(data)
                                    if "10-Q" in filing_title:
                                        print('\n' + data_10q['timestamp'] + '  |  ' + data_10q['title'] + '  |  ' + data_10q['source'] + '  |  ' + data_10q['url'] + '\n')
                                        alert(os.path.join(os.path.dirname(script_dir), 'sound_alerts', 'smci_10q.wav'))
                                        open_link(filing_url)
                                        main_data = open_json(os.path.join(script_dir, 'sec.json'))
                                        update_main_json(os.path.join(script_dir, 'sec.json'), json.dumps(data_10q), main_data)
                                    elif "10-K" in filing_title:
                                        print('\n' + data_10k['timestamp'] + '  |  ' + data_10k['title'] + '  |  ' + data_10k['source'] + '  |  ' + data_10k['url'] + '\n')
                                        alert(os.path.join(os.path.dirname(script_dir), 'sound_alerts', 'smci_10k.wav'))
                                        open_link(filing_url)
                                        main_data = open_json(os.path.join(script_dir, 'sec.json'))
                                        update_main_json(os.path.join(script_dir, 'sec.json'), json.dumps(data_10k), main_data)

                            if 'NT 10-K' in filing_title:
                                
                                data_10q = {
                                    'timestamp': datetime.now().strftime("%H:%M:%S"),
                                    'title': filing_title,
                                    'source': 'NT 10-Q',
                                    'url': filing_url
                                }

                                data_10k = {
                                    'timestamp': datetime.now().strftime("%H:%M:%S"),
                                    'title': filing_title,
                                    'source': 'NT 10-K',
                                    'url': filing_url
                                }

                                # data = json.dumps(data)
                                if "10-Q" in filing_title:
                                    print('\n' + data_10q['timestamp'] + '  |  ' + data_10q['title'] + '  |  ' + data_10q['source'] + '  |  ' + data_10q['url'] + '\n')
                                    alert(os.path.join(os.path.dirname(script_dir), 'sound_alerts', 'nt_10q.wav'))
                                    open_link(filing_url)
                                    main_data = open_json(os.path.join(script_dir, 'sec.json'))
                                    update_main_json(os.path.join(script_dir, 'sec.json'), json.dumps(data_10q), main_data)
                                elif "10-K" in filing_title:
                                    print('\n' + data_10k['timestamp'] + '  |  ' + data_10k['title'] + '  |  ' + data_10k['source'] + '  |  ' + data_10k['url'] + '\n')
                                    alert(os.path.join(os.path.dirname(script_dir), 'sound_alerts', 'nt_10k.wav'))
                                    open_link(filing_url)
                                    main_data = open_json(os.path.join(script_dir, 'sec.json'))
                                    update_main_json(os.path.join(script_dir, 'sec.json'), json.dumps(data_10k), main_data)
                            '''
                            if '13G' in filing_title:
                                if not '13G/A' in filing_title: 
                                    
                                    # convert to text to get company name
                                    filing_txt_url = re.sub(r'-index\.html?$', '.txt', filing_url)
                                    # txt_url = filing_url.replace("-index.htm", ".txt").replace("-index.html", ".txt")
                                    filing_response_txt = requests.get(filing_txt_url, headers=random.choice(headers_list))
                                    filing_response_txt_soup = BeautifulSoup(filing_response_txt.content, "lxml")
                                    filing_object_txt = str(filing_response_txt_soup)

                                    pattern = re.compile(
                                        r"(?is)"                  # (?i) = case-insensitive, (?s) = DOTALL so '.' matches newlines
                                        r"subject\s+company\s*:\s*"  # match "subject company:" ignoring case and possible spaces
                                        r".*?"                    # lazily match anything (including newlines) until we find...
                                        r"company\s+conformed\s+name\s*:\s*([^\n]+)"  # capture everything after "company conformed name:"
                                    )

                                    company_name = pattern.search(filing_object_txt)
                                    company_name = company_name.group(1).strip()
                                
                                    data = {
                                        'timestamp': datetime.now().strftime("%H:%M:%S"),
                                        'title': str(company_name) + '  |  ' + filing_title,
                                        'source': 'SEC 13G',
                                        'url': filing_url
                                    }

                                    # Keith Gill CIK
                                    if '0001871280' in filing_title:
                                        
                                        # data = json.dumps(data)
                                        print('\n' + data['timestamp'] + '  |  KEITH GILL 13G - ' + data['title'] + '  |  ' + data['source'] + '  |  ' + data['url'] + '\n')
                                        ticker_search(company_name)
                                        open_link(filing_url)
                                        alert(os.path.join(os.path.dirname(script_dir), 'sound_alerts', 'keith_gill_13g.wav'))
                                        main_data = open_json(os.path.join(script_dir, 'sec.json'))
                                        update_main_json(os.path.join(script_dir, 'sec.json'), json.dumps(data), main_data)

                                    if ('nvidia' in filing_title.lower()) and ('0001045810' in filing_title.lower()):
                                        print('\n' + data['timestamp'] + '  |  ' + data['title'] + '  |  ' + data['source'] + '  |  ' + data['url'] + '\n')
                                        open_link(filing_url)
                                        ticker_search(company_name)
                                        alert(os.path.join(os.path.dirname(script_dir), 'sound_alerts', 'nvidia_13g.wav'))
                                        main_data = open_json(os.path.join(script_dir, 'sec.json'))
                                        update_main_json(os.path.join(script_dir, 'sec.json'), json.dumps(data), main_data)
                                    
                                    # if any item from list of companies in filing_title
                                    companies = ['apple', 'amazon', 'meta', 'microsoft', 'google', 'tesla', 'palantir',
                                                 "spacex", "space-x", "starlink", "merck", "novo nordisk", "eli lilly",
                                                 "johnson", "pfizer", "abbvie", "squibb", "regeneron", "sanofi", "vertex",
                                                 "amgen", "roche", "astrazeneca", "schrodinger", "revvity", "novartis",
                                                 "gilead", "moderna", "tempus", "thermo fisher", "biogen", "trump", "uber",
                                                 "qualcomm", "broadcom", "intel", "internation business machines",
                                                 "advanced micro devices", "super micro", "marvell", "arm holdings",
                                                 "arm semiconductor", "arm semiconductors", "general electric", "general motors",
                                                 "goldman sachs", "jpmorgan", "citigroup", "wells fargo", "bank of america",
                                                 "morgan stanley", "deutsche bank", "barclays", "applovin", "walmart", 'nvidia']
                                                
                                    if any(company in filing_title.lower() for company in companies):
                                        print('\n' + data['timestamp'] + '  |  ' + data['title'] + '  |  ' + data['source'] + '  |  ' + data['url'] + '\n')
                                        open_link(filing_url)
                                        ticker_search(company_name)
                                        alert(os.path.join(os.path.dirname(script_dir), 'sound_alerts', '13g_filing.wav'))
                                        main_data = open_json(os.path.join(script_dir, 'sec.json'))
                                        update_main_json(os.path.join(script_dir, 'sec.json'), json.dumps(data), main_data)
                            '''
                            '''
                            if '13D' in filing_title:
                                if not '13D/A' in filing_title:
                                    
                                    # convert to text to get company name
                                    filing_txt_url = re.sub(r'-index\.html?$', '.txt', filing_url)
                                    # txt_url = filing_url.replace("-index.htm", ".txt").replace("-index.html", ".txt")
                                    filing_response_txt = requests.get(filing_txt_url, headers=random.choice(headers_list))
                                    filing_response_txt_soup = BeautifulSoup(filing_response_txt.content, "lxml")
                                    filing_object_txt = str(filing_response_txt_soup)

                                    pattern = re.compile(
                                        r"(?is)"                  # (?i) = case-insensitive, (?s) = DOTALL so '.' matches newlines
                                        r"subject\s+company\s*:\s*"  # match "subject company:" ignoring case and possible spaces
                                        r".*?"                    # lazily match anything (including newlines) until we find...
                                        r"company\s+conformed\s+name\s*:\s*([^\n]+)"  # capture everything after "company conformed name:"
                                    )

                                    company_name = pattern.search(filing_object_txt)
                                    company_name = company_name.group(1).strip()

                                    # look for item 4 purpose of transaction
                                    filing_txt_url = re.sub(r'-index\.html?$', '.txt', filing_url)
                                    filing_response_txt = requests.get(filing_txt_url, headers=random.choice(headers_list))

                                    filing_response_txt_soup = BeautifulSoup(filing_response_txt.content, "lxml")
                                    item4_tag = filing_response_txt_soup.find("item4")
                                    
                                    # if item4_tag:
                                    item4_text = item4_tag.text
                                    # print('item 4 purpose of transaction: ', item4_tag)
                                
                                    # search for M&A keywords in item 4
                                    # split into sentences
                                    sentence_pattern = r'(?<=[.])\s+'
                                    sentences = re.split(sentence_pattern, item4_text.strip())
                                    sentences = [s.strip() for s in sentences if s.strip()]

                                    # search for M&A keywords in sentences
                                    keywords_regex = re.compile(r'\b(acquire|bid|merger|takeover|acquisition|offer|proposal|bidder|bidder)\b', re.IGNORECASE)
                                    
                                    if keywords_regex:  # if keyword_regex has a match
                                        relevant_sentences = []
                                        for s in sentences:
                                            if keywords_regex.search(s):
                                                relevant_sentences.append(s)
                                                
                                        # Within each relevant sentence, check if there's a $ sign and extract the special substring if so.
                                        acquisition_price_regex = re.compile(r'\$[\d,]+\.\d+')

                                        # extract acquisition price
                                        # If there's no '$' sign, continue
                                        results = []
                                        for sentence in relevant_sentences:
                                            if '$' in sentence:
                                                results.append(sentence)

                                            else:
                                                continue
                                    
                                        data = {
                                            'timestamp': datetime.now().strftime("%H:%M:%S"),
                                            'title': str("\n\u001b[1m" + company_name + "\u001b[1;m") + '  |  ' + str("\u001b[1m" + filing_title + "\u001b[1;m") + '  |  ' + str('\n' + str(results)),
                                            'source': 'SEC 13D',
                                            'url': filing_url
                                        }
                                        # data = json.dumps(data)
                                        print('\n' + data['timestamp'] + '  |  ' + data['title'] + '  |  ' + data['source'] + '  |  ' + data['url'] + '\n')
                                        open_link(filing_url)
                                        ticker_search(company_name)
                                        alert(os.path.join(os.path.dirname(script_dir), 'sound_alerts', 'mna_13d_filing.wav'))
                                        main_data = open_json(os.path.join(script_dir, 'sec.json'))
                                        update_main_json(os.path.join(script_dir, 'sec.json'), json.dumps(data), main_data)

                                    # no item 4 purpose of transaction
                                    else:
                                        data = {
                                            'timestamp': datetime.now().strftime("%H:%M:%S"),
                                            'title': str(company_name) + '  |  ' + filing_title,
                                            'source': 'SEC 13D',
                                            'url': filing_url
                                        }
                                        
                                        # data = json.dumps(data)
                                        print('\n' + data['timestamp'] + '  |  ' + data['title'] + '  |  ' + data['source'] + '  |  ' + data['url'] + '\n')
                                        ticker_search(company_name)
                                        alert(os.path.join(os.path.dirname(script_dir), 'sound_alerts', '13d_filing.wav'))
                                        open_link(filing_url)
                                        main_data = open_json(os.path.join(script_dir, 'sec.json'))
                                        update_main_json(os.path.join(script_dir, 'sec.json'), json.dumps(data), main_data)
                            '''
                            if '13F-HR' in filing_title:
                                if (
                                    (('berkshire' in filing_title.lower()) and ('0001067983' in filing_title.lower())) or 
                                    (('pershing' in filing_title.lower()) and ('0001336528' in filing_title.lower())) or
                                    (('nvidia' in filing_title.lower()) and ('0001045810' in filing_title.lower()))
                                ):
                                    
                                    # get filing content
                                    berkshire_filing_response = requests.get(filing_url, headers=random.choice(headers_list))
                                    berkshire_soup_object = BeautifulSoup(berkshire_filing_response.content, "html.parser")

                                    rows = berkshire_soup_object.find_all("tr")
                                    xml_data_suburl = None

                                    for row in rows:
                                        # Collect all <td scope="row"> cell texts in this row
                                        cells = row.find_all("td", scope="row")

                                        # Check that row has both "INFORMATION TABLE FOR FORM 13F" and "INFORMATION TABLE"
                                        if "INFORMATION TABLE" in str(cells):
                                            # Now find all <a> tags within this row
                                            links = row.find_all("a", href=True)
                                            for link in links:
                                                href = link["href"].strip()
                                                link_text = link.get_text(strip=True)

                                                # Only accept if BOTH the href and link text end in ".xml"
                                                if href.lower().endswith(".xml") and link_text.lower().endswith(".xml"):
                                                    xml_data_suburl = href
                                                    break
                                            
                                            if xml_data_suburl:
                                                break  # Stop searching once found

                                    xml_data_url = "https://www.sec.gov" + xml_data_suburl
                                    berkshire_xml_data_response = requests.get(xml_data_url, headers=random.choice(headers_list))
                                    berkshire_xml_data_soup = BeautifulSoup(berkshire_xml_data_response.content, "html.parser")
                                    info_tables = berkshire_xml_data_soup.find_all("infotable")
                                        
                                    issuer_values = {}

                                    if info_tables:
                                        for idx, info_table in enumerate(info_tables):
                                            # Extract <nameOfIssuer> text
                                            issuer_tag = info_table.find("nameofissuer")
                                            issuer_name = issuer_tag.get_text(strip=True) if issuer_tag else "UNKNOWN_ISSUER"

                                            # Extract <value> text and convert to int (or float if needed)
                                            value_tag = info_table.find("value")
                                            value_amount = int(value_tag.get_text(strip=True)) if value_tag else 0

                                            holdings_data = {
                                                'Company': issuer_name,
                                                'Value': value_amount
                                            }

                                            # Accumulate the sums per issuer
                                            issuer_values[issuer_name] = issuer_values.get(issuer_name, 0) + value_amount
                                            # add commas to value_amount every 3 digits from the right
                                            value_amount = f"{value_amount:,}"
                                            if 'berkshire' in filing_title.lower():
                                                berkshire_data = open_json(os.path.join(script_dir, 'berkshire_holdings.json'))
                                                update_13f_boolean = update_13f_json(os.path.join(script_dir, 'berkshire_holdings.json'), json.dumps(holdings_data), berkshire_data)

                                                if update_13f_boolean == True:

                                                    data = {
                                                        'timestamp': datetime.now().strftime("%H:%M:%S"),
                                                        'title': ("\n\u001b[1m" + issuer_name + "\u001b[1;m") + '  |  ' + str(value_amount),
                                                        'source': 'Berkshire Hathaway SEC 13F-HR',
                                                        'url': filing_url
                                                    }

                                                    # data = json.dumps(data)
                                                    print('\n' + data['timestamp'] + '  |  ' + data['title'] + '  |  ' + data['source'] + '  |  ' + data['url'])
                                                    if idx == 0:
                                                        open_link(filing_url)
                                                    ticker_search(issuer_name)
                                                    alert(os.path.join(os.path.dirname(script_dir), 'sound_alerts', 'berkshire_13f.wav'))
                                                    main_data = open_json(os.path.join(script_dir, 'sec.json'))
                                                    update_main_json(os.path.join(script_dir, 'sec.json'), json.dumps(data), main_data)

                                            if 'pershing' in filing_title.lower():
                                                pershing_data = open_json(os.path.join(script_dir, 'pershing_square_holdings.json'))
                                                update_13f_boolean = update_13f_json(os.path.join(script_dir, 'pershing_square_holdings.json'), json.dumps(holdings_data), pershing_data)
        
                                                if update_13f_boolean == True:
                                                    
                                                    data = {
                                                        'timestamp': datetime.now().strftime("%H:%M:%S"),
                                                        'title': ("\n\u001b[1m" + issuer_name + "\u001b[1;m") + '  |  ' + str(value_amount),
                                                        'source': 'Pershing Square SEC 13F-HR',
                                                        'url': filing_url
                                                    }

                                                    # data_json = json.dumps(data)
                                                    print('\n' + data['timestamp'] + '  |  ' + data['title'] + '  |  ' + data['source'] + '  |  ' + data['url'] + '\n')
                                                    if idx == 0:
                                                        open_link(filing_url)
                                                    ticker_search(issuer_name)
                                                    alert(os.path.join(os.path.dirname(script_dir) , 'sound_alerts', 'pershing_13f.wav'))
                                                    main_data = open_json(os.path.join(script_dir, 'sec.json'))
                                                    update_main_json(os.path.join(script_dir, 'sec.json'), json.dumps(data), main_data)

                                            if 'nvidia' in filing_title.lower():
                                                nvidia_data = open_json(os.path.join(script_dir, 'nvidia_holdings.json'))
                                                update_13f_boolean = update_13f_json(os.path.join(script_dir, 'nvidia_holdings.json'), json.dumps(holdings_data), nvidia_data)
                                                value_difference_13f = update_13f_json_value(os.path.join(script_dir, 'nvidia_holdings.json'), json.dumps(holdings_data), nvidia_data)

                                                if update_13f_boolean == True:

                                                    data = {
                                                        'timestamp': datetime.now().strftime("%H:%M:%S"),
                                                        'title': ("\n\u001b[1m" + "NEW STAKE!!!" + "\u001b[1;m") + '  |  ' + ("\u001b[1m" + issuer_name + "\u001b[1;m") + '  |  ' + str(value_amount),
                                                        'source': 'NVIDIA SEC 13F-HR',
                                                        'url': filing_url
                                                    }   

                                                    # data_json = json.dumps(data)
                                                    print('\n' + data['timestamp'] + '  |  ' + data['title'] + '  |  ' + data['source'] + '  |  ' + data['url'] + '\n')
                                                    if idx == 0:
                                                        open_link(filing_url)
                                                    ticker_search(issuer_name)
                                                    alert(os.path.join(os.path.dirname(script_dir) , 'sound_alerts', 'nvidia_13f.wav'))

                                                    main_data = open_json(os.path.join(script_dir, 'sec.json'))
                                                    update_main_json(os.path.join(script_dir, 'sec.json'), json.dumps(data), main_data)

                                                if value_difference_13f != 0 and update_13f_boolean == False:
                                                    
                                                    value_difference_13f = f"{value_difference_13f:,}"

                                                    data = {
                                                        'timestamp': datetime.now().strftime("%H:%M:%S"),
                                                        'title': ("\n\u001b[1m" + "Amended Value" + "\u001b[1;m") + '  |  ' + ("\u001b[1m" + issuer_name + "\u001b[1;m") + '  |  ' + str(value_difference_13f),
                                                        'source': 'NVIDIA SEC 13F-HR',
                                                        'url': filing_url
                                                    }

                                                    print('\n' + data['timestamp'] + '  |  ' + data['title'] + '  |  ' + data['source'] + '  |  ' + data['url'] + '\n')
                                                    if idx == 0:
                                                        open_link(filing_url)
                                                    ticker_search(issuer_name)
                                                    alert(os.path.join(os.path.dirname(script_dir) , 'sound_alerts', 'nvidia_13f.wav'))
                                                    main_data = open_json(os.path.join(script_dir, 'sec.json'))
                                                    update_main_json(os.path.join(script_dir, 'sec.json'), json.dumps(data), main_data)


                            #if '424B5' in filing_title or '424B4' in filing_title:
                            #    if any(company in filing_title for company in
                            #           ['Goldman', 'J.P. Morgan', 'Bank of America', 'Verizon', 'Citi', 'Wells Fargo', 'Jeffries', 'Morgan Stanley', 'Bank of Hawaii'
                            #            'Nova Scotia', 'Bank of Canada', 'HSBC', 'Nomura', 'Valley Bank']):
                            #            #['C', 'JPM', 'BAC', 'WFC', 'GS', 'JEF', 'MS', 'BOH', 'BNS', 'RY', 'TD', 'VLY','DB','RNST', 'VRT', 'HSBC', 'NMR']
                            #        continue
                            #    else:
                            #        data = {
                            #            'timestamp': datetime.now().strftime("%H:%M:%S"),
                            #            'title': title,
                            #            'source': '424B4 filing',
                            #            'url': content_url,
                            #        }
                            #        # data = json.dumps(data)
                            #        print('\n' + data['timestamp'] + '  |  ' + data['title'] + '  |  ' + data[
                            #            'source'] + '  |  ' + data['url'] + '\n')
                            '''
                            if 's-1' in filing_title.lower():
                                data = {
                                    'timestamp': datetime.now().strftime("%H:%M:%S"),
                                    'title': title,
                                    'source': 'S-1 filing',
                                    'url': content_url,
                                }
                                print('\n' + data['timestamp'] + '  |  ' + data['title'] + '  |  ' + data[
                                    'source'] + '  |  ' + data['url'] + '\n')
                            '''
                            if 's-3' in filing_title.lower():
                                data = {
                                    'timestamp': datetime.now().strftime("%H:%M:%S"),
                                    'title': title,
                                    'source': 'S-3 filing',
                                    'url': content_url,
                                }
                                print('\n' + data['timestamp'] + '  |  ' + data['title'] + '  |  ' + data[
                                    'source'] + '  |  ' + data['url'] + '\n')
                            
            elif response.status_code != 200:
                error_message = f"Bad status code: {response.status_code}"
                log_error(error_log, error_message)
                time.sleep(1)
                
                if should_terminate(error_log):
                    print(f"\nToo many errors ({len(error_log)} in last 2 minutes). Pausing for 2 minutes...")
                    print(f"\nLast error: {error_message}")
                    print(data)

                    time.sleep(120)  # Sleep for 2 minutes
                    error_log.clear()  # Clear error log after sleep
                    continue
                
                # time.sleep(5)  # Short sleep between retries
                continue

        except requests.exceptions.RequestException as e:
            error_message = f"Request error: {str(e)}"
            log_error(error_log, error_message)
            time.sleep(1)
            
            if should_terminate(error_log):
                print(f"\nToo many errors ({len(error_log)} in last 2 minutes). Pausing for 2 minutes...\n")
                print(f"\nLast error: {error_message}\n")

                time.sleep(120)
                error_log.clear()
            
            time.sleep(5)  # Short sleep between retries
            continue

        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            log_error(error_log, error_message)
            print(f'{error_message}')
            print(data)
            time.sleep(1)
            
            if should_terminate(error_log):
                print(f"\nToo many errors ({len(error_log)} in last 2 minutes). Pausing for 2 minutes...\n")
                print(f"\nLast error: {error_message}\n")
                time.sleep(120)
                error_log.clear()
            
        # print('iteration')

        time.sleep(0.3)  # Your existing delay between successful scrapes

# ADD ERROR HANDLING AND LOGGING
# ADD FUNCTION TO CLEAN UP JSON AND TXT FILES WHEN STARTING NEW SCRAPE EXCEPT FOR THE MOST RECENT FILE
# MULTIPROCESS EACH OF THE 5 FILINGS - MAKE SURE JSON AND TXT FILES DONT GET CORRUPTED  BY OPENING AT THE SAME TIME

# 8-k, 13D buyouts and activists and big companies, 13F buyouts, activists, and from big companies, berkshire/pershing square, SMCI 10Q/10K, Keith Gill 13G, 
# 13d filings scraper / announcement of ownership Control / active stake affect stock more than passive stake

def finviz(ticker):
    try:
        tick = finvizfinance(ticker).ticker_fundament()

        avg_vol = tick['Avg Volume']
        sfp = float(tick['Short Float'][:-1])


        mc = tick['Market Cap']

        if avg_vol[-1] == 'B':
            avg_vol = float(avg_vol[:-1]) * 1000000000
        elif avg_vol[-1] == 'M':
            avg_vol = float(avg_vol[:-1]) * 1000000
        elif avg_vol[-1] == 'T':
            avg_vol = float(avg_vol[:-1]) * 10000000000000
        elif avg_vol[-1] == 'K':
            avg_vol = float(avg_vol[:-1]) * 1000

        if mc[-1] == 'B':
            mc = float(mc[:-1]) * 1000000000
        elif mc[-1] == 'M':
            mc = float(mc[:-1]) * 1000000
        elif mc[-1] == 'T':
            mc = float(mc[:-1]) * 10000000000000


        return mc, sfp, avg_vol
    except Exception as e:
        pass
        #print(f"Error in finviz: {e}")


if __name__ == "__main__":
    # while True:
    #     try:
    #         scrape_sec()
    #         # Sleep for 0.2 seconds between scrapes to avoid overwhelming the server
    #         time.sleep(0.2)
    #     except Exception as e:
    #         print(f"Error occurred: {e}")
    #         # Sleep for 30 seconds if there's an error before retrying
    #         time.sleep(1)
    #         continue
    print('Starting SEC algorithm...\n')
    try:
        scrape_sec()
    except KeyboardInterrupt:
        print('\nStopped by user.')
    except Exception:
        import traceback
        traceback.print_exc()
    input("\nStopped. Press Enter to close...")


'''

if data is None:
    continue
elif filing['ticker'] == 'UMAC' or filing['ticker'] == 'MU':
    file_print(filing)
elif data[0] >= (5.0 * 1000000000):
                                file_print(filing)
                            elif data[0] >= (1.0 * 1000000000) and data[2] >= 2000000:
                                file_print(filing)
                            elif data[1] >= 10 and data[2] >= 2000000:
                                file_print(filing)
                            elif data[2] >= (4.0 * 1000000):
                                file_print(filing)
'''
