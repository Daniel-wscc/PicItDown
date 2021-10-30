from selenium import webdriver
import time
import urllib
import os
import tkinter as tk
import jieba
import pandas as ps
from datetime import datetime, timedelta
from translate import Translator
from pytrends.request import TrendReq
import requests
from bs4 import BeautifulSoup


def seachimg():
    # 存圖位置
    i=download_entry.get()
    local_path = './'+i
    
    if not os.path.isdir(local_path):
        os.mkdir(local_path)
    # 爬取頁面網址 3
    if (var.get()=='google'):   
        url = 'https://www.google.com.tw/search?hl=zh-TW&tbm=isch&source=hp&biw=1920&bih=936&ei=V5CuXu_-DJGU0ASbjLbIBA&q='+i+'&oq='+i+'&gs_lcp=CgNpbWcQAzICCAAyAggAMgIIADICCAAyAggAMgIIADIFCAAQgwEyAggAMgIIADICCABQyQ1Y0SVgjSxoAHAAeACAAUaIAagCkgEBNZgBAKABAaoBC2d3cy13aXotaW1nsAEA&sclient=img&ved=0ahUKEwivhtuPspfpAhURCpQKHRuGDUkQ4dUDCAc&uact=5' 
    # 目標元素的xpath
    if (var.get()=='google'):
        xpath = '//div[@id="islrg"]/div/div/a/div/img'

    # 啟動chrome瀏覽器
    #chromeDriver = 'C:\\Users\\ogame\\Downloads\\互動專案\\chromedriver.exe' # chromedriver檔案放的位置
    driver = webdriver.Chrome('.\chromedriver.exe') 
    #driver = webdriver.Chrome(chromeDriver) 
      
    # 最大化窗口，因為每一次爬取只能看到視窗内的圖片  
    driver.maximize_window()  
      
    # 紀錄下載過的圖片網址，避免重複下載  
    img_url_dic = {}  
          
    # 瀏覽器打開爬取頁面
    driver.get(url)  
      
    # 模擬滾動視窗瀏覽更多圖片
    pos = 0  
    m = 0 # 圖片編號 
    picsum = number_entry.get()
    for i in range(100): 
        if (m < int(picsum)):
            pos += i*500 # 每次下滾500  
            js = "document.documentElement.scrollTop=%d" % pos  
            driver.execute_script(js)  
            time.sleep(0.5)
            
            for element in driver.find_elements_by_xpath(xpath):
                if (m < int(picsum)):
                    try:
                        img_url = element.get_attribute('src')
                        
                        # 保存圖片到指定路徑
                        if img_url != None and not img_url in img_url_dic:
                            img_url_dic[img_url] = ''  
                            m += 1
                           # print(img_url)
                            #ext = img_url.split('/')[-1]
                            # print(ext)       
                            filename = str(m)  +'.jpg'                     
                            print(filename)
                            # 保存圖片
                            urllib.request.urlretrieve(img_url, os.path.join(local_path , filename))
                    except OSError:
                        print('發生OSError!')
                        print(pos)
                        break;
                else :
                    break
                
    driver.close()
#--------------------------------------------------------------------------------------   
def questask():

    date = str(datetime.now().strftime('%Y/%m/%d'))
    week = str(datetime.now().strftime('%A'))
    time = str(datetime.now().strftime('%X'))
    timeflag = 0
    quesflag = 0
    '''
    weather = pd.read_csv('taiwan_cwd2020-06-08.csv')
    weather = weather[['CITY','DISTRICT','DAY','TIME','Wx']]
    TODAY = weather[weather.DAY == today]
    '''
    sentence = quest_entry.get()
    global texts
    
    print("Input：",sentence)
    words = jieba.cut(sentence, cut_all=False)
    timedic = {"今天":1,"昨天":2,"明天":3,"現在":1}
    quesdic = {"天氣":1,"日期":2,"西元":2,"幾月":2,"星期":4,"幾日":2,"時間":3,"幾點":3,"幾分":3,"熱門":5,"排行":6,"焦點":7,"位置":8,"下載":9}
    
    for word in words:
        print(word)
        if timedic.get(word)!= None :
            timeflag = timedic.get(word)
            if (timeflag==1):
                date = str(datetime.now().strftime('%Y/%m/%d'))
                week = str(datetime.now().strftime('%A'))
                time = str(datetime.now().strftime('%X'))
            if (timeflag==2):
                yesterday = datetime.today() + timedelta(-1)
                date =  str(yesterday.strftime('%Y/%m/%d'))
                week = str(yesterday.strftime('%A'))
            if (timeflag==3):
                tomorrow = datetime.today() + timedelta(+1)
                date =  str(tomorrow.strftime('%Y/%m/%d'))
                week = str(tomorrow.strftime('%A'))
        if quesdic.get(word)!= None :
            quesflag =quesdic.get(word)
    if quesflag==0:
        texts.set("你問這什麼鳥問題")
        
    elif quesflag == 1 :   
        texts.set("今天天氣晴")
            
            
    elif quesflag == 2 :    
        texts.set(date)
        
    elif quesflag == 3 :   
        texts.set(time)
        
    elif quesflag == 4 :
        translator= Translator(from_lang="english",to_lang="chinese")
        translation = translator.translate(week)
        texts.set(translation)
    elif quesflag == 5 :    
        pytrends = TrendReq(hl='zh-TW', tz=0)
        pd = pytrends.today_searches(pn='TW')
        sss=""
        i=0
        while(i<pd.size):
            sss+=pd[i]+'\n'
            i = i + 1
        texts.set(sss)
    elif quesflag == 6 :    
        pytrends = TrendReq(hl='zh-TW', tz=0)
        pd = pytrends.today_searches(pn='TW')
        keywords = [pd[0]]
        pytrends.build_payload(
             kw_list=keywords,
             cat=0, 
             timeframe='now 7-d',
             geo='TW',
             gprop='')
        df = ps.DataFrame(data=pytrends.interest_by_region(resolution='COUNTRY', inc_low_vol=True, inc_geo_code=False))
        texts.set(df.sort_values(by=pd[0],ascending=False ))
    elif quesflag == 7 :
         r = requests.get('https://tw.yahoo.com/')

         if r.status_code == requests.codes.ok:
             soup = BeautifulSoup(r.text, 'html.parser')
        
         stories = soup.find_all('a', class_='story-title')
         flag = 0
         strr=""
         for s in stories:
             flag+=1
             strr+=str(flag)+ '.' + s.text+'\n\n'
             if flag == 5:
                 break
         texts.set(strr)
    elif quesflag == 8 :
        texts.set(os.getcwd())
        
    elif quesflag == 9 :
        pytrends = TrendReq(hl='zh-TW', tz=0)
        pd = pytrends.today_searches(pn='TW')
        text2.set(pd[0])
        seachimg()
        texts.set("下載完畢")



print('------臭扒手------')
#print (os.getcwd())
window = tk.Tk()
window.title('一鍵下載')
window.geometry('650x850')
window.configure(background = 'pink')
#window.mainloop()



print('------準備素材------')
var = tk.StringVar()  
texts = tk.StringVar()
text2 = tk.StringVar()
text3 = tk.StringVar()
text3.set(3)
var.set("google")

header_label = tk.Label(window,text = '想來些甚麼? 給我名字',font = ('Arial',30),width = 28)
download_entry = tk.Entry(window,textvariable=text2, font=('Arial',30),width = 23)
number_label = tk.Label(window,text = '想要下載幾張?',font = ('Arial',30),width = 28)
number_entry = tk.Entry(window,textvariable=text3,font=('Arial',30),width = 28)
serchoption = tk.OptionMenu(window,var,'google')
calculate_btn = tk.Button(window,text = 'Click me!',font = ('Arial',30),command=seachimg)
#result_label = tk.Label(window,text = '檔案會下載到同程式的資料夾',font = ('Arial',30),width = 28,height = 1)
ques_label = tk.Label(window,text = '想問些甚麼問題',font = ('Arial',30))
quest_entry = tk.Entry(window,font=('Arial',30))
qb = tk.Button(window,text = '回答我!',font = ('Arial',30),command=questask)

ans_label = tk.Label(window,textvariable=texts,font = ('Arial',15),width = 50,height = 16)
print('------版面配置------')
header_label.grid(row = 0,column = 0,columnspan = 2)
serchoption.grid(row = 1,column = 0)
download_entry.grid(row = 1,column = 1)
number_label.grid(row = 2,column = 0,columnspan = 2)
number_entry.grid(row = 3,column = 0,columnspan = 2)
calculate_btn.grid(row = 4,column = 0,columnspan = 2)
#result_label.grid(row = 5,column = 0,columnspan = 2)
ques_label.grid(row = 5,column = 0,columnspan = 2)
quest_entry.grid(row = 6,column = 0,columnspan = 2)
ans_label.grid(row = 8,column = 0,columnspan = 2)
qb.grid(row = 7,column = 0,columnspan = 2)
window.mainloop()