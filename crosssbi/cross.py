"""Get xxx"""
import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import urllib.parse
import json
import time
import logging
import datetime
import re

WAIT_TIME = 1


def order(user_id, login_pwd, trade_pwd):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] : %(message)s')
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    proxies = {"http": "http://127.0.0.1:8888", "https": "http:127.0.0.1:8888"}
    # proxies = {}

    # ログイン画面
    url = "https://www.sbisec.co.jp/ETGate"
    r = requests.get(
        url
        , proxies=proxies
        , verify=False
    )

    ## ログイン押下 ############
    data = {
        "JS_FLG": "0"
        , "BW_FLG": "0"
        , "_ControlID": "WPLETlgR001Control"
        , "_DataStoreID": "DSWPLETlgR001Control"
        , "_PageID": "WPLETlgR001Rlgn20"
        , "_ActionID": "login"
        , "getFlg": "on"
        , "allPrmFlg": "on"
        , "_ReturnPageInfo": "WPLEThmR001Control/DefaultPID/DefaultAID/DSWPLEThmR001Control"
        , "user_id": user_id
        , "user_password": login_pwd
    }

    headers = {
        'Content-Length': get_content_length(data)
        ,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
        , 'Cache-Control': 'max-age=0'
        , 'Sec-Fetch-Site': 'same-origin'
        , 'Sec-Fetch-Mode': 'navigate'
        , 'Sec-Fetch-User': '?1'
        , 'Sec-Fetch-Dest': 'document'
        , 'Accept-Encoding': 'gzip, deflate, br'
        , 'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8'
    }

    time.sleep(WAIT_TIME)
    r = requests.post(
        "https://www.sbisec.co.jp/ETGate/"
        , proxies=proxies
        , verify=False
        , data=data
        , headers=headers
    )

    soup = BeautifulSoup(r.content, "html.parser")
    action = soup.find("form", {"name": "formSwitch"})["action"]
    ctoken = soup.find("input", {"name": "ctoken"})["value"]
    login_date_time = soup.find("input", {"name": "LoginDateTime"})["value"]
    tengun_id = soup.find("input", {"name": "_TENGUN_ID"})["value"]

    # ログイン（フォワード先）
    data = {
        "ctoken": ctoken
        , "LoginDateTime": login_date_time
        , "_TENGUN_ID": tengun_id
        , "_ActionID": "login"
        , "_PageID": "WPLETlgR001Rlgn20"
        , "BW_FLG": "0"
        , "allPrmFlg": "on"
        , "JS_FLG": "0"
        , "_DataStoreID": "DSWPLETlgR001Control"
        , "_ControlID": "WPLETlgR001Control"
        , "getFlg": "on"
        , "_ReturnPageInfo": "WPLEThmR001Control/DefaultPID/DefaultAID/DSWPLEThmR001Control"
    }

    time.sleep(WAIT_TIME)
    ses = requests.session()
    r = ses.post(
        action
        , proxies=proxies
        , verify=False
        , headers=headers
        , data=data
    )

    soup = BeautifulSoup(r.content, "html.parser")
    # user_name = soup.find(id='MAINAREA01').find('a').string
    user_name = user_id

    # 一般信用在庫への遷移
    params = {
        'OutSide': 'on'
        , '_ControlID': 'WPLETsmR001Control'
        , '_PageID': 'WPLETsmR001Sdtl12'
        , '_DataStoreID': 'DSWPLETsmR001Control'
        , 'sw_page': 'WNS001'
        , 'sw_param1': 'domestic'
        , 'sw_param2': 'top'
        , 'sw_param3': 'cbsProductList'
        , 'cat1': 'home'
        , 'cat2': 'none'
        , 'getFlg': 'on'
        , 'OutSide': 'on'
    }

    r = ses.get(
        'https://www.sbisec.co.jp/ETGate/'
        , proxies=proxies
        , verify=False
        , params=params
    )

    # 一般信用在庫検索

    data = {
         'productCodeName': ''
        , 'paymentLimit': 'SHORT'
        , 'positionStatus': 'IN_STOCK'
        , 'positionStatus': 'LITTLE_STOCK'
        , 'vestingMonths': 'DECEMBER'
        , 'productCodeNameOrg': ''
        , 'rows': '200'
        , 'pageNum': '1'
        , 'sortKey': 'PRODUCT_CODE'
        , 'sortOrder': 'ASC'
        , 'first': 'false'
    }

    data_str = '&'.join('%s=%s' % (k, v) for k, v in data.items())

    headers['Content-Type'] = 'application/x-www-form-urlencoded'

    r = ses.post(
        'https://site0.sbisec.co.jp/marble/domestic/top/cbsProductList.do'
        , proxies=proxies
        , verify=False
        , headers=headers
        , data=data_str
    )

    soup = BeautifulSoup(r.content, "html.parser")

    stock_tags = soup.find('tbody').find_all('tr')

    for stock_tag in stock_tags:
        tds = stock_tag.find_all('td')
        # re.search(r'[0-9]*', stock_tag.find_all('td')[1].find('a').text)
        code =re.search(r'[0-9]+',tds[1].find('a').text).group()
        # 在庫　を抽出するところから。


    exit(0)

    seqNo = soup.find("input", {"name": "_SeqNo"})["value"]
    wbSessionId = soup.find("input", {"name": "_WBSessionID"})["value"]
    be_wstm4080 = soup.find("input", {"name": "BE_WSTM4080"})["value"]
    payment_limit = soup.find("input", {"name": "payment_limit"})["value"]
    limit_in = soup.find('select', {"name": "limit_in"}).find('option')['value']

    while True:

        stock_sec_code = '2702'
        # stock_sec_code = '3626'

        # 株価表示
        data = {
            '_PageID': 'WPLETstT001Mord10'
            , '_DataStoreID': 'DSWPLETstT001Control'
            , '_SeqNo': seqNo
            , '_ControlID': 'WPLETstT001Control'
            , '_WID': 'NoWID'
            , '_ORGWID': ''
            , '_WIDManager': ''
            , '_WBSessionID': wbSessionId
            , '_preProcess': ''
            , '_TimeOutControl': ''
            , '_WIDMode': '0'
            , '_WindowName': ''
            , '_ReturnPageInfo': ''
            , '_ActionID': 'order'
            , 'page_from': 'WPLETstT001Mord10'
            , 'mkt_cd': 'TKY'
            , 'iscontrol1': '1'
            , 'account_des_kbn': '1'
            , 'account_get_kbn': '2'
            , 'BE_WSTM4080': be_wstm4080
            , 'trade_kbn': '3'
            , 'stock_sec_code': stock_sec_code
            , 'input_market': '+++'
            , 'ACT_order': '%8A%94%89%BF%95%5C%8E%A6'
            , 'tyuubun_top_flg': '1'
            , 'input_quantity': ''
            , 'in_sasinari_kbn': '+'
            , 'sasine_condition': '+'
            , 'input_price': ''
            , 'nariyuki_condition': 'N'
            , 'input_trigger_price': ''
            , 'input_trigger_zone': '1'
            , 'gsn_sasinari_kbn': '+'
            , 'gsn_sasine_condition': '+'
            , 'gsn_input_price': ''
            , 'gsn_nariyuki_condition': 'N'
            , 'selected_limit_in': 'this_day'
            , 'limit_in': '20%2F12%2F23'
            , 'hitokutei_trade_kbn': '0'
            , 'payment_limit': '6'
            , 'autocomplete-off': ''
            , 'trade_pwd1': ''
            , 'trade_pwd2': ''
            , 'trade_pwd': ''
            , 'trade_pwd4': ''
        }

        data_str = '&'.join('%s=%s' % (k, v) for k, v in data.items())

        r = ses.post(
            'https://site2.sbisec.co.jp/ETGate/'
            , proxies=proxies
            , verify=False
            , headers=headers
            , data=data_str
        )

        soup = BeautifulSoup(r.content, "html.parser")

        stock = soup.find('input', id='input_quantity').parent.parent.parent.find_all('td')[2].text
        print(datetime.datetime.now())
        print(stock)
        if not '×' in stock:
            break
        time.sleep(10)

    exit(0)

    # 現物買い注文
    # headers['Referer'] = 'https://site2.sbisec.co.jp/ETGate/?_ControlID=WPLETstT001Control&_PageID=DefaultPID&_DataStoreID=DSWPLETstT001Control&_ActionID=DefaultAID&getFlg=on'

    stock_sec_code = '8593'

    data = {
        '_PageID': 'WPLETstT001Mord10'
        , '_DataStoreID': 'DSWPLETstT001Control'
        , '_SeqNo': seqNo
        , '_ControlID': 'WPLETstT001Control'
        , '_WID': 'NoWID'
        , '_ORGWID': ''
        , '_WIDManager': ''
        , '_WBSessionID': wbSessionId
        , '_preProcess': ''
        , '_TimeOutControl': ''
        , '_WIDMode': '0'
        , '_WindowName': ''
        , '_ReturnPageInfo': ''
        , '_ActionID': 'place'
        , 'page_from': 'WPLETstT001Mord10'
        , 'mkt_cd': 'TKY'
        , 'iscontrol1': '1'
        , 'account_des_kbn': '1'
        , 'account_get_kbn': '2'
        , 'BE_WSTM4080': be_wstm4080
        , 'trade_kbn': '0'
        , 'stock_sec_code': stock_sec_code
        , 'input_market': '+++'
        , 'tyuubun_top_flg': '1'
        , 'input_quantity': '100'
        , 'sasine_condition': '+'
        , 'input_price': ''
        , 'in_sasinari_kbn': 'N'
        , 'nariyuki_condition': 'N'
        , 'input_trigger_price': ''
        , 'input_trigger_zone': '0'
        , 'gsn_sasinari_kbn': '+'
        , 'gsn_sasine_condition': '+'
        , 'gsn_input_price': ''
        , 'gsn_nariyuki_condition': 'N'
        , 'selected_limit_in': 'this_day'
        , 'limit_in': '20%2F04%2F21'
        , 'hitokutei_trade_kbn': '0'
        , 'payment_limit': payment_limit
        , 'autocomplete-off': ''
        , 'trade_pwd1': ''
        , 'trade_pwd2': ''
        , 'trade_pwd': trade_pwd
        , 'trade_pwd4': ''
        , 'skip_estimate': 'on'
    }

    data_str = '&'.join('%s=%s' % (k, v) for k, v in data.items())

    r = ses.post(
        'https://site2.sbisec.co.jp/ETGate/'
        , proxies=proxies
        , verify=False
        , headers=headers
        , data=data_str
    )

    exit(0)

    params = {
        'OutSide': 'on'
        , '_ControlID': 'WPLETstT001Control'
        , '_PageID': 'DefaultPID'
        , '_DataStoreID': 'DSWPLETstT001Control'
        , '_ActionID': 'DefaultAID'
        , 'getFlg': 'on'
        , 'int_pr1': '150313_cmn_gnavi:1_dmenu_01'
    }

    params = {
        '_ControlID': 'WPLETsmR001Control'
        , '_DataStoreID': 'DSWPLETsmR001Control'
        , 'burl': 'search_domestic'
        , 'dir': 'ipo%2F'
        , 'sw_page': 'Offer'
        , 'sw_param1': '21'
        , 'sw_param2': ''
        , 'cat1': 'home'
        , 'cat2': 'none'
        , 'getFlg': 'on'
    }

    time.sleep(WAIT_TIME)
    r = ses.get(
        action
        , proxies=proxies
        , verify=False
        , params=params
    )

    # IPO申込対象の抽出とループ

    soup = BeautifulSoup(r.content, "html.parser")
    orders = soup.find_all("img", {"alt": "申込"})

    for order in orders:
        url = order.previous_element["href"]
        # p_cd = url[-4:]
        time.sleep(WAIT_TIME)
        r = ses.get(
            'https://m.sbisec.co.jp' + url
            , proxies=proxies
            , verify=False
            , params=params
        )
        soup = BeautifulSoup(r.content, "html.parser")

        p_cd = soup.find('input', {'name': 'p_cd'})['value']
        r_no = soup.find('input', {'name': 'r_no'})['value']
        type = soup.find('input', {'name': 'type'})['value']

        # IPO注文申込
        data = {
            'dummypass': ''
            , 'actualAccount': '0'
            , 'jnisaOrderAvailableFlag': '0'
            , 'type': type
            , 'p_cd': p_cd  # 銘柄コード
            , 'r_no': r_no
            , 'suryoType': '2'
            , 'kakakuType': '2'
            , 'enc_suryoTitle': '%258A%2594%2590%2594'
            , 'enc_kakakuTitle': '%2589%25BF%258Ai'
            , 'mailFlag': ''
            , 'nisaBallotDisp': '0'
            , 'nisaOrderAvailableFlag': '0'
            , 'getBuyLimit': '0'
            , 'suryo': '10000'  # 注文株数
            , 'kakaku_kbn': '1'  # ストライクプライス
            , 'kakaku': ''
            , 'useKbn': '0'  # IPOポイント使用なし
            , 'usePoint': ''
            , 'tr_pass': trade_pwd
            , 'order_kakunin': '%90%5C%8D%9E%8Am%94F%89%E6%96%CA%82%D6'
            , 'JspId': 'oeapw010'
        }

        time.sleep(WAIT_TIME)
        r = ses.post(
            'https://m.sbisec.co.jp/oeapw021'
            , proxies=proxies
            , verify=False
            , headers=headers
            , data=data
        )

        # IPO注文確定

        headers['Referer'] = 'https://m.sbisec.co.jp/oeapw021'
        headers['Upgrade-Insecure-Requests'] = '1'
        headers['Origin'] = 'https://m.sbisec.co.jp'
        headers['Content-Type'] = 'application/x-www-form-urlencoded'

        data = {
            'type': type
            , 'p_cd': p_cd
            , 'r_no': r_no
            , 'actualAccount': '0'
            , 'jnisaOrderAvailableFlag': '0'
            , 'useKbn': '0'
            , 'usePoint': ''
            , 'suryo': '10000'
            , 'kakaku': ''
            , 'suryoType': '2'
            , 'kakakuType': '2'
            , 'kakaku_kbn': '1'
            , 'mailFlag': ''
            , 'mailCheck': ''
            , 'nisaBallotDisp': '0'
            , 'nisaSuryo': '0'
            , 'nisaOrderAvailableFlag': '0'
            , 'getBuyLimit': ''
            , 'order_btn': ''
        }

        time.sleep(WAIT_TIME)
        r = ses.post(
            'https://m.sbisec.co.jp/oeapw031'
            , proxies=proxies
            , verify=False
            # , headers=headers
            , data=data
        )

    # 申込状況の確認
    params = {
        '_ControlID': 'WPLETsmR001Control'
        , '_DataStoreID': 'DSWPLETsmR001Control'
        , 'burl': 'search_domestic'
        , 'dir': 'ipo%2F'
        , 'sw_page': 'Offer'
        , 'sw_param1': '21'
        , 'sw_param2': ''
        , 'cat1': 'home'
        , 'cat2': 'none'
        , 'getFlg': 'on'
    }

    time.sleep(WAIT_TIME)
    r = ses.get(
        action
        , proxies=proxies
        , verify=False
        , params=params
    )

    soup = BeautifulSoup(r.content, "html.parser")
    tables = soup.find_all('table', border='0', cellspacing='1', cellpadding='2', width='780')

    logging.info(user_name)
    for table in tables:
        tags = table.find_all('td')
        sec_info = tags[1].text.replace('\n', '')
        bb_term = tags[5].text
        bb_info = tags[13].text
        bb_result = tags[17].text

        logging.info(sec_info + ' : ' + bb_term + ' : ' + bb_info + ' : ' + bb_result)

    # ログアウト
    params = {
        '_ControlID': 'WPLETlgR001Control'
        , '_PageID': 'WPLETlgR001Rlgn50'
        , '_DataStoreID': 'DSWPLETlgR001Control'
        , '_ActionID': 'logout'
        , 'getFlg': 'on'
    }

    time.sleep(WAIT_TIME)
    r = ses.get(
        action
        , proxies=proxies
        , verify=False
        , params=params
    )


def get_content_length(data):
    return str(len(json.dumps(data)) - len(data) * 6 - 2)  # 要素ごとに"""": ,の７文字。後で&と相殺で1要素当たり6文字で計算


if __name__ == '__main__':
    f = open(r'conf\id.txt', 'r')
    login_pwd = f.readline().rstrip('\n')
    trade_pwd = f.readline().rstrip('\n')
    for line in f:
        login_id = line.rstrip('\n')
        order(login_id, login_pwd, trade_pwd)

    f.close()
