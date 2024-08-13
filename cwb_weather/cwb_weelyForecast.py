def weekForecast():
    from urllib import parse
    import requests as req
    from bs4 import BeautifulSoup as bs
    from fake_useragent import UserAgent
    from datetime import datetime

    now = datetime.now()
    nowFormatted = f"{now.year}{now.month:02}{now.day:02}{now.hour:02}-{str(now.minute)[0]}"
    url = f"https://www.cwb.gov.tw/V8/C/W/County/MOD/wf7dayNC_NCSEI/ALL_Week.html?t={nowFormatted}"
    # print(url)

    # 設定隨機UserAgent
    ua = UserAgent()
    my_headers = {
        'User-Agent':ua.random
    }

    # 發出get request，確認連線狀況
    response = req.get(url, headers = my_headers)
    # print(f'網站狀態碼: {response.status_code}')
    # print(f'網站編碼　: {response.encoding}')
    # print(f'回覆標頭　: {response.headers}')

    soup = bs(response.text, 'lxml')
    dataByCounty = soup.select('tr.day')

    for county in dataByCounty:
        if county.find('span', class_='heading_3') != None:
            print(f"縣市: {county.find('span', class_='heading_3').get_text()}")
        
        dayTempRange = county.find_all('span', class_='tem-C')
        for i in range(len(dayTempRange)):
            print(f"day {i+1}: {dayTempRange[i].get_text()}")
    


weekForecast()