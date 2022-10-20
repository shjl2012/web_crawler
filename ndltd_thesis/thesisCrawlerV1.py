# '''
# 論文爬蟲目標
# https://ndltd.ncl.edu.tw/cgi-bin/gs32/gsweb.cgi/login?o=dwebmge
# '''
# Ver.1只爬第一頁的論文

# 操作 browser 的 API
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 期待元素出現要透過什麼方式指定，通常與 EC、WebDriverWait 一起使用
from selenium.webdriver.common.by import By

# 強制等待 (執行期間休息一下)
from time import sleep

# 整理 json 使用的工具
import json

# 執行 command 的時候用的 (建立資料夾)
import os


# 啟動瀏覽器工具的選項
my_options = webdriver.ChromeOptions()
# my_options.add_argument("--headless")                # 不開啟實體瀏覽器背景執行
my_options.add_argument("--start-maximized")           # 最大化視窗
my_options.add_argument("--incognito")                 # 開啟無痕模式
my_options.add_argument("--disable-popup-blocking")    # 禁用彈出攔截
my_options.add_argument("--disable-notifications")     # 取消通知
my_options.add_argument("--lang=zh-TW")                # 設定為正體中文

# 使用 Chrome 的 WebDriver
driver = webdriver.Chrome(
    options = my_options,
    service = Service(ChromeDriverManager().install())
)

# 建立儲存圖片、影片的資料夾
folderPath = 'Thesis'
if not os.path.exists(folderPath):
    os.makedirs(folderPath)

# 暫時放置爬取的資料供後續存入JSON的檔案
listData = []


# ========== 訪問碩博士論文系統首頁 ==========
def visit():
    driver.get('https://ndltd.ncl.edu.tw/cgi-bin/gs32/gsweb.cgi/login?o=dwebmge')
# ========== 訪問碩博士論文系統首頁 end ==========


# ========== 於系統輸入關鍵字並開始搜尋 ==========
def search():
    SearchKeys = input('請輸入查詢關鍵字:' )
    txtInput = driver.find_element(By.CSS_SELECTOR, 'input.inputbox')
    txtInput.send_keys(SearchKeys)
    sleep(2)
    txtInput.submit()
    sleep(3)
# ========== 於系統輸入關鍵字並開始搜尋 end ==========


# ========== 爬取論文資料 ==========
def selectTheses():
    # 選擇內含論文連結的element
    theses = driver.find_elements(By.CSS_SELECTOR, 'td.tdfmt1-content')
    
    for thesis in theses: # 測試用先抓10篇
        # reference, resultNum => 用於取得搜尋結果編號 (確認抓到之資料用)
        # linkElement => 論文暫時連結位在標籤
        # titleTag => 論文標題位在的標籤
        # thesisTitle => 論文標題文字
        # tempLink => 論文暫時連結
        reference = thesis.find_element(By.XPATH, '..')
        resultNum = reference.find_element(By.CSS_SELECTOR, 'td.tdfmt1-second').text
        linkElement = thesis.find_element(By.CSS_SELECTOR, 'a.slink')
        titleTag = linkElement.find_element(By.CSS_SELECTOR, 'span.etd_d')
        thesisTitle = titleTag.get_attribute('innerText')
        tempLink = linkElement.get_attribute('href')
        
        # 開啟、切換顯示至新分頁，並於新分頁開啟論文連結
        driver.execute_script("window.open('');") # 開啟新tab
        driver.switch_to.window(driver.window_handles[1]) # 切換到新開的tab (原來的tab在[0])
        driver.get(tempLink) # 在新的tab打開論文暫時連結
        sleep(3)
        
        # 取得論文永久連結以及說明文
        permaLink = driver.find_elements(By.CSS_SELECTOR, 'input#fe_text1')[0].get_attribute("value") # 取得論文網址永久URL
        description = driver.find_elements(By.CSS_SELECTOR, 'meta[name="description"]')[0].get_attribute("content") # 取得論文網址摘要 (位於header中)
            
        # 關掉新分頁、切回至原來分頁
        driver.close() # 關掉剛開的新分頁
        driver.switch_to.window(driver.window_handles[0]) # 回到原本的搜尋結果頁面
        sleep(3) 

        # 把目前這筆論文資料加入至listData
        listData.append({
            'resulNum':resultNum,
            'title':thesisTitle,
            'link':permaLink,
            'description':description
        })
# ========== 爬取論文資料 end ==========


# ========== 把爬取到的資料存到JSON ==========
def saveJson():
    with open(f"{folderPath}/thesis.json", "w", encoding="utf-8" ) as file:
        file.write(json.dumps(listData, ensure_ascii=False))       
# ========== 把爬取到的資料存到JSON end ==========        


# ========== 關掉瀏覽器 ==========
def close():
    driver.quit()
# ========== 關掉瀏覽器 end ==========


# ========== 主程式 ==========
if __name__ == "__main__":
    visit()
    search()
    selectTheses()
    saveJson()
    close()
# ========== 主程式 end ==========