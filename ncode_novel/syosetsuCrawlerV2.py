# 日本網路小說網站『成為小說家』爬蟲程式ver.2
# 加入選擇爬的資料筆數功能

def syosetsuCrawlerV2():

    # import必要套件
    from urllib import parse
    import requests as req
    from bs4 import BeautifulSoup as bs
    from fake_useragent import UserAgent
    from time import time, sleep
    from random import randint
    import os
    import re
    
    # 測試用fixed輸入值
    # url = 'https://ncode.syosetu.com/n9722do/'
    # howMany = 50

    url = input('請輸入小說主頁url: ')
    howMany = int(input('請輸入要爬幾章: '))


    # 隨機產生User-Agent
    ua = UserAgent()
    my_headers = {
        'User-Agent':ua.random
    }

    # 發出get request，確認連線狀況
    response = req.get(url, headers = my_headers)
    print(f'網站狀態碼: {response.status_code}')
    print(f'網站編碼　: {response.encoding}')
    print(f'回覆標頭　: {response.headers}')

    # 建立soup物件
    soup = bs(response.text, 'lxml')
    
    # 檔名標題中不能有的字元，稍後存檔時使用
    illegal_c = '[@_!#$%^&*()<>?/|}{~:]　'

    # 取得小說標題
    novel_title = soup.select('div#novel_contents p.novel_title')[0].get_text()
            

    # 小說存放資料夾名檢查用
    # 檢查小說名，判斷是否有任何不能用在檔名/資料夾名的字元，有時在非法字元處截斷資料夾名
    folderPath = ''
    for char in novel_title:
        if char in illegal_c:
            truncateIndex = novel_title.find(char)
            folderPath = novel_title[0:truncateIndex]
            break
    
    # 檢查同名資料夾是否存在，若沒有創建資料夾
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)

    
    # 取得各小說章節標題、上傳日期、更新日期、連結作為一組陣列存到chapterLink
    # chapterInfoSource = 可取得以上所有資訊的上層節點
    # regexDateTime = 擷取上傳、更新日期時只保留日期時間用的正規表達式
    chapterInfoSource = soup.select('div.index_box dl.novel_sublist2')
    chapterInfo = []
    regexDateTime = r'([\d]{4}/[\d]+/[\d]+) ([\d]{2}:[\d]{2})'

    # 從chapterInfoSource個別抓出需要資訊存入對應變數
    for i in range(howMany):
        chapterTitle = chapterInfoSource[i].a.get_text()
        uploadDateTime = re.search(regexDateTime, chapterInfoSource[i].dt.get_text())[0]
        updateDateTime = ''
        if chapterInfoSource[i].find('span') != None:
            updateDateTime = re.search(regexDateTime, chapterInfoSource[i].span['title'])[0]
        chapterLink = f"https://ncode.syosetu.com{chapterInfoSource[i].a['href']}"

        # chapterTitle = 節標題
        # uploadDateTime = 節首次上傳時間
        # updateDateTime = 節最後更新時間
        # chapterLink = 節連結
        link = [chapterTitle, uploadDateTime, updateDateTime, chapterLink]
        chapterInfo.append(link)
    

    # 確認有正常抓到資料
    # for link in chapterInfo:
    #     print(f"link:{link}")


    # 從chapterInfo資料開始取出資料寫檔案
    for link in chapterInfo:
        res_chapter = req.get(link[3], headers = my_headers)
        soup_chapter = bs(res_chapter.text, 'lxml')
        chapter_title = soup_chapter.select('p.novel_subtitle')[0].get_text()
        
        # 當節的標題含無法用在檔案以及資料夾命名的文字時砍掉
        for char in chapter_title:
            if char in illegal_c:
                chapter_title = chapter_title.replace(char, '')

        # 建立指向含小說本文標籤的soup物件
        chapter_content = soup_chapter.select('div#novel_honbun p')

        # 在folderPath中打開或創建後打開一個txt檔，命名為小說節名
        # 檔案內寫入小說節名、上傳、更新時間、內文並加入換行符號進行styling
        with open(f'{folderPath}/{chapter_title}.txt', 'w', encoding='utf-8') as novel_file:
            novel_file.write(f"タイトル：{chapter_title}\n更新日時：{link[1]}\n最終更新：{link[2]}\n\n\n")
            for text in chapter_content:
                novel_file.write(f"{text.get_text()}\n")
        
        # 爬連結間空3~7秒避免因太過頻繁被認定是爬蟲
        sleep(randint(3, 7))

if __name__ == '__main__':
    syosetsuCrawlerV2()