# 必要套件 - request + beautiful soup
import requests as req
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
from time import time, sleep
from random import randint
import os
import re


def connection():
    ua = UserAgent()
    my_headers = {
        'User-Agent':ua.random
    }

    url = 'https://www.gutenberg.org/browse/languages/zh'
    print(f"爬取「古騰堡計劃」中文電子書 ({url})")
    response = req.get(url, headers = my_headers)
    soup = bs(response.text, 'lxml')
    print(f'網站狀態碼: {response.status_code}')
    print(f'網站編碼　: {response.encoding}')

    # 建立soup物件
    soup = bs(response.text, 'lxml')
    return soup


def folderCreate(soup):
    # 建立小說儲存資料夾 - 以古騰堡網站為名
    folderName = soup.select('img[alt="Project Gutenberg"]')[0]['alt']
    # print(folderName)

    illegalChar = '[@_!#$%^&*()<>?/|}{~:]'

    for char in folderName:
        if char in illegalChar:
            truncateIndex = folderName.find(char)
            folderName = folderName[0:truncateIndex]
            break

    if not os.path.exists(folderName):
        os.makedirs(folderName)
    
    return folderName


def getChapterList(soup):
    # 選取小說連結 - 直接選取連結所在標籤
    raw = soup.select('div.pgdbbylanguage > ul > li.pgdbetext > a')
    # raw = soup.select('div.page_content > div.pgdbbylanguage')

    illegalChar = '[@_!#$%^&*()<>?/|}{~:]'
    newLine = r'([\r\n])'
    chapterListRaw = []
    i = 1
    for item in raw:
        title = item.get_text()
        if re.search(newLine, title) != None:
            title = re.sub(newLine, ' ', title)
        for char in title:
            if char in illegalChar:
                title = title.replace(char, "_")

        link =  f"https://www.gutenberg.org{item['href']}"
        chapter = [title, link]
        chapterListRaw.append(chapter)
        
    chapterList = []
    [chapterList.append(chapter) for chapter in chapterListRaw if chapter not in chapterList]
    with open(f"./{folderName}/Gutenberg_zh-tw.txt", 'w', encoding='utf-8') as file:
        for item in chapterList:
            itemConcat = ' '.join(item)
            file.write(itemConcat + '\n')

    return chapterList



def saveChapter(chapterList, folderName):
    # 建立小說爬蟲用物件 - v3
    ua = UserAgent()
    my_headers = {
        'User-Agent':ua.random
    }
    
    removeTarget = r'[\x00-\xff]+$'
    i = 1

    for chapter in chapterList:
        res_chapter = req.get(chapter[1], headers = my_headers)
        soup_chapter = bs(res_chapter.text, 'lxml')
        # content = soup_chapter.select('tr[typeof="pgterms:file"] > ')
        dowloadLinks = soup_chapter.select('td[property="dcterms:format"] > a')
        for link in dowloadLinks:
            if link.get_text() == 'Plain Text UTF-8':
                # print(f"{i} title:{chapter[0]} https://www.gutenberg.org{link['href']}")
                dlLink = f"https://www.gutenberg.org{link['href']}"
                dlLinkRequest = req.get(dlLink)
                dlLinkRequest.encoding = 'UTF-8'
                # print("encoding: %s" % dlLinkRequest.encoding)
                # print(dlLinkRequest.text)
                
                with open(f"./{folderName}/{[i]}_gutenberg_{chapter[0]}.txt", 'w', encoding='utf-8') as file:
                    rawText = dlLinkRequest.text
                    listSentences = re.sub(removeTarget, '', rawText, flags=re.DOTALL | re.MULTILINE)
                    file.write(listSentences)
                    # new_file.truncate()
                break
        # sleep(randint(1, 3))
        i+=1




if __name__ == '__main__':
    soup = connection()
    folderName = folderCreate(soup)
    chapterList = getChapterList(soup)
    saveChapter(chapterList, folderName)

