# 日本網路小說網站『成為小說家』爬蟲程式ver.3
# 加入選擇爬的資料筆數功能
# 加入根據章節建立資料夾功能

def syosetsuCrawlerV3():

    # import必要套件
    from urllib import parse
    import requests as req
    from bs4 import BeautifulSoup as bs
    from fake_useragent import UserAgent
    from time import time, sleep
    from random import randint
    import os
    import re
    
    
    # 指定爬的URL、要爬資料的筆數
    # url = 'https://ncode.syosetu.com/n1881dn/'
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
    
    # illegal_c = 不該出現在小說資料夾名的字元、符號集合
    illegal_c_title = '[@_!#$%^&*()<>?/|}{~:]　'

    # 取得小說標題
    novel_title = soup.select('div#novel_contents p.novel_title')[0].get_text()
            

    # 建立存放小說的資料夾，判斷其中是否有任何
    folderPath = ''
    for char in novel_title:
        if char in illegal_c_title:
            truncateIndex = novel_title.find(char)
            folderPath = novel_title[0:truncateIndex]
            break

    if not os.path.exists(folderPath):
        os.makedirs(folderPath)

    # 把每個小說的所屬章、節標題、上傳時間、更新時間、連結資料抓出存成一個list
    # chapterInfoSource = 個別小說標題、上傳時間、更新時間、連結資料來源
    # novel_content = 章資料來源
    chapterInfoSource = soup.select('div.index_box dl.novel_sublist2')
    novel_content = soup.select('div.index_box')
    regexChapterTitle = r'<div class=\"chapter_title\">([一-龯ぁ-んァ-ン　\w]+)<\/div>'
    chapterInfo = []
    regexDateTime = r'([\d]{4}/[\d]+/[\d]+) ([\d]{2}:[\d]{2})'



    # 取得小說章、節標題、上傳日期、更新日期、連結作為一組陣列存到chapterLink
    for i in range(howMany):
        sectionSliceIndex = str(novel_content).find(chapterInfoSource[i].a.get_text())
        sectionString = str(novel_content)[0:sectionSliceIndex]
        section = re.findall(regexChapterTitle, sectionString)
        latest_section = section[len(section)-1]
        chapterTitle = chapterInfoSource[i].a.get_text()
        uploadDateTime = re.search(regexDateTime, chapterInfoSource[i].dt.get_text())[0]
        updateDateTime = ''
        if chapterInfoSource[i].find('span') != None:
            updateDateTime = re.search(regexDateTime, chapterInfoSource[i].span['title'])[0]
        chapterLink = f"https://ncode.syosetu.com{chapterInfoSource[i].a['href']}"


        link = [latest_section, chapterTitle, uploadDateTime, updateDateTime, chapterLink]
        chapterInfo.append(link)

    
    # 確認有正常抓到資料
    # for item in chapterInfo:
    #     print(item)

    # illegal_c_section = 不該出現在章資料夾名的文字集合
    illegal_c_section = '[@_!#$%^&*()<>?/|}{~:]'
    
    # for迴圈跑過chapterInfo中的每個元素
    for item in chapterInfo:
        
        # ===== 在小說資料夾內建立章子資料夾 =====
        chapterPath = ''
        for char in item[0]:

            # 確保章資料夾名不會有不能使用的特殊字元
            if char in illegal_c_section:
                truncateIndex = item[0].find(char)
                chapterPath = item[0][0:truncateIndex]
                break
            else:
                chapterPath = item[0]

        # 判斷章資料夾是否存在，沒有的話建立資料夾
        if not os.path.exists(f"{folderPath}/{chapterPath}"):
            os.makedirs(f"{folderPath}/{chapterPath}")
        # ===== 區塊結束 =====
        

        # ===== 建立爬文章本文需要的呼叫、soup物件，以及檔名 =====
        res_chapter = req.get(item[4], headers = my_headers)
        soup_chapter = bs(res_chapter.text, 'lxml')
        chapter_content = soup_chapter.select('div#novel_honbun p')
        chapter_title = item[1]
        
        for char in chapter_title:
            if char in illegal_c_section:
                chapter_title = chapter_title.replace(char, '')
        # ===== 區塊結束 =====
        

        # ===== 開啟檔案並寫入 =====
        with open(f'{folderPath}/{chapterPath}/{chapter_title}.txt', 'w', encoding='utf-8') as novel_file:
            novel_file.write(f"タイトル：{item[1]}\n更新日時：{item[2]}\n最終更新：{item[3]}\n\n\n")
            for text in chapter_content:
                novel_file.write(f"{text.get_text()}\n")

        # 爬連結間空3~7秒避免因太過頻繁被認定是爬蟲
        sleep(randint(3, 7))
        # ===== 區塊結束 =====



if __name__ == '__main__':
    syosetsuCrawlerV3()