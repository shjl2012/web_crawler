def weekForecast():
    from urllib import parse
    import requests as req
    from bs4 import BeautifulSoup as bs
    from fake_useragent import UserAgent
    from datetime import datetime, timedelta
    import re
    import pandas as pd


    # ===== 產生取得最新預報用網址 =====
    # 預報網站的最新資訊html每10分鐘會變，格式基於目前日期時間(到10分鐘位)
    # import datetime物件用來抓取目前時間並動態產生query string加入url
    now = datetime.now()
    nowFormatted = f"{now.year}{now.month:02}{now.day:02}{now.hour:02}-{str(now.minute)[0]}"
    url = f"https://www.cwb.gov.tw/V8/C/W/County/MOD/wf7dayNC_NCSEI/ALL_Week.html?t={nowFormatted}"
    # print(url)
    # ===== 產生取得最新預報用網址 end =====

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

    # 選取包含所有資料的最小標籤層級 (22個縣市、各有7天份的白天、晚上預報資訊)
    dataByCounty = soup.select('tbody')

    # # ===== 把一週天氣預報資料印出到console =====
    # for county in dataByCounty:
    #     # dayLabel => 預報白天時段的標籤名
    #     # nightLabel => 預報晚上時段的標籤名
    #     # cityName => 目前這筆資料的縣市名
    #     # dayTempAll => 目前縣市的全部白天溫度預報資料
    #     # nightTempAll => 目前縣市的全部晚上溫度預報資料
    #     dayLabel = county.select('tr.day td[headers] span')[0].get_text()
    #     nightLabel = county.select('tr.night td[headers] span')[0].get_text()
    #     cityName = county.select('th[headers] span')[0].get_text()
    #     dayTempAll = county.select('tr.day td[headers] span.tem-C')
    #     nightTempAll = county.select('tr.night td[headers] span.tem-C')
        
    #     # ===== 印出資料header =====
    #     print(cityName)
    #     print(f"day #     {dayLabel:8}{nightLabel:8}")
    #     # ===== 印出資料header end =====

    #     # ===== 印出資料預報溫度 =====
    #     for i in range(len(dayTempAll)):
    #         dayTemp = re.sub(r'\u2002',r'',dayTempAll[i].get_text())
    #         nightTemp = re.sub(r'\u2002',r'',nightTempAll[i].get_text())
    #         print(f"day {i+1}     {dayTemp:10}{nightTemp:10}")  
    #     # ===== 印出資料預報溫度 end =====

    # # ===== 把一週天氣預報資料印出到console end =====



    # ===== 把一週天氣預報資料寫入csv =====
    
    # 建立會使用於csv的變數
    # dayLabel => csv存放白天預報溫度的行標題
    # nightLabel => csv存放晚上預報溫度的行標題
    # followingWeek => 接下來一週的日期，從資料表頭抓取
    dateSource = soup.select('tr.table_top th:not(#County, #time)')
    dayLabel = dataByCounty[0].select('tr.day td[headers] span')[0].get_text()
    nightLabel = dataByCounty[0].select('tr.night td[headers] span')[0].get_text()
    followingWeek = []
    reDate = r'([\d]+\/[\d]{2})'
    for date in dateSource:
        followingWeek.append(re.search(reDate, date.get_text())[0])


    # 建立weatherData字典結構，為以pandas dataframe灌入csv檔用
    # weatherData['city_name'] => 建立key為city_name的串列，用來放縣市名
    # weatherData['date'] => 建立key為date的串列，用來存放一週的日期
    # weatherData[dayLabel] => 建立key為dayLabel變數值的串列，用來放白天預報溫度
    # weatherData[nightLabel] => 建立key為nightLabel變數值的串列，用來放晚上預報溫度
    weatherData = {}
    weatherData['city_name'] = []
    weatherData['date'] = []
    weatherData[dayLabel] = []
    weatherData[nightLabel] = []
    

    # ===== 把資料寫到weatherData各個key內 ===== 
    for county in dataByCounty:
        # 對於dataByCounty中的每個縣市資料先用select取得以下資料
        # dayTempAll => 目前縣市全部白天天氣預報資料
        # nightTempAll => 目前縣市全部晚上天氣預報資料
        dayTempAll = county.select('tr.day td[headers] span.tem-C')
        nightTempAll = county.select('tr.night td[headers] span.tem-C')
        cityName = county.select('th[headers] span')[0].get_text()
        
        # 個別迭代dayTempAll的各個元素，因同時需要取出對應的day_of_week，使用i in range()
        # 各縣市日間/晚間資料共有7筆，range()值也可直接指定為7
        for i in range(len(dayTempAll)):
            dayTemp = re.sub(r'\u2002',r'',dayTempAll[i].get_text()) # 動態取得一週各日
            nightTemp = re.sub(r'\u2002',r'',nightTempAll[i].get_text())
            forecastDate = followingWeek[i]

            weatherData['city_name'].append(cityName)
            weatherData['date'].append(forecastDate)
            weatherData[dayLabel].append(dayTemp)
            weatherData[nightLabel].append(nightTemp)
    # ===== 把資料寫到weatherData各個key內 end ===== 
    
    # print(weatherData)

    weatherData_df = pd.DataFrame(weatherData)
    weatherData_df.to_csv('weatherForecast.csv')
    # ===== 把一週天氣預報資料寫入csv end =====


if __name__ == '__main__':
    weekForecast()