# -*- coding: utf-8 -*-
"""
Created on Wed Aug  3 14:44:53 2022

@author: jason
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import time
import os.path
import pandas as pd
import threading
from concurrent.futures import ThreadPoolExecutor

# switch the handle window from main page to question page
# click the question url to dive into question
def Into_QA(handle, page_index, parent_handle):
    '''
    switch the handle window from main page to question page
    click the question url to dive into question
    page_index: index of page desire to look into
    '''
    if handle.current_window_handle != parent_handle:
        handle.switch_to.window(handle.window_handles[0])
    
    page_url = "//*[@id='mainContent']/div[2]/div[2]/div[" +str(page_index)+"]"+"/div/div/div/div/div/div/div/div/div/div[1]/div/span/span/a/div/div/div/div/span/span"
    element = handle.find_element(By.XPATH, page_url )
    print('entering page ',page_index)
    element.click()
    time.sleep(2)  
    # window_handles[1] is a second window
    handle.switch_to.window(handle.window_handles[1])

# 将handle从子页面切换回主页面,删掉handler释放内存
def out_QA(handle ,parent_handle):
    '''
    close question page and move to parent page
    '''
    handle.close()
    handle.switch_to.window(parent_handle)


def transText(eList):
    '''
    change element list get from selenium into text list
    all the element should include the answer paragraph
    '''
    tmp = []
    for i in eList:
        tmp.append(i.text)
    return tmp

PAUSE_TIME =1.2
def data_acquire( wd):
    '''
    acquire data from answer page.
    question: the string of question
    authorId : the webelement stores authorID
    upvote : the webelement stores upvote
    answer : the webelement stores answer
    answerb : for different html versions, 
                some answers are stored in different structure of Quora html. 
                this would retrieve answer data if the answer didn't work. 
    '''
    time.sleep(PAUSE_TIME)
    question = wd.find_element(By.XPATH,"//*[@id='mainContent']/div/div[1]/div/div/div/div[1]/span/span/div/div/div/span/span").text
    authorID = wd.find_elements(By.XPATH,'//*[@id="mainContent"]/div/div[2]/div[*]/div/div/div/div/div/div/div/div/div[1]/div[1]/div/div/div/div/div[2]/div[1]/span/span')
    answer = wd.find_elements(By.XPATH,'//*[@id="mainContent"]/div/div[2]/div[*]/div/div/div/div/div/div/div/div/div[1]/div[2]/div/div[1]')
    upvote = wd.find_elements(By.XPATH,'//*[@id="mainContent"]/div/div[2]/div[*]/div/div/div/div/div/div/div/div/div[2]/div/div/div[1]/div/div[1]/div/button/div[2]/span[2]')
    answerb = wd.find_elements(By.XPATH,'//*[@id="mainContent"]/div/div[2]/div[*]/div/div/div/div/div/div/div/div/div[1]/div[3]/div/div[1]')
    return question,authorID,answer,upvote,answerb
    
def writeData(dataframe, index, space):
    '''
    record the data into local drive, chaning the location before running progress.
    index: the index of this Q-A among this space
    space: Quora space name
    
    '''
    
    path = os.path.join('d:\\Quora_scraper\\new\\', space) 
    os.path.isdir(path)
    if os.path.isdir(path) ==False :
        os.mkdir(path)
    location = 'd:\\Quora_scraper\\new\\'+ space+'\\'+str(index)+'.txt'
    dataframe.to_csv(location, index=None, sep=',', mode='a')
    
    
# sort question dispaly in recent order
def switch_sorting(page_index ,wd):
    '''
    select the recent sort method
    don't need page_index only when to report bug
    '''

    try:
        sorts = wd.find_elements(By.XPATH,"//*[@id='mainContent']/div/div[2]/div[1]/div/div[2]/div/div[2]/div/div/button/div")
        if len(sorts)==0:
            sort = wd.find_element(By.XPATH,"//*[@id='mainContent']/div/div[2]/div[1]/div/div[2]/div/div/div/button/div/div[2]/div")
            sort.click()
            sort_recent = wd.find_element(By.XPATH,"//*[@id='mainContent']/div/div[2]/div[1]/div/div[2]/div/div/div[2]/div/div[1]/div/div/div[3]/div/div")
            sort_recent.click()
        else:
            sorts[0].click()
            sort_recent = wd.find_element(By.XPATH,"//*[@id='mainContent']/div/div[2]/div[1]/div/div[2]/div/div[2]/div/div[2]/div/div[1]/div/div/div[3]/div[1]")
            sort_recent.click()
    except:
        print('no answer',page_index)
        pass
        
def hasAnswered(page_index, wd, parent_handle):
    '''
    Determine if the question has an answer
    '''
    if wd.current_window_handle != parent_handle:
        wd.switch_to.window(wd.window_handles[0])
    
    AnswerIndex = "//*[@id='mainContent']/div[2]/div[2]/div[" +str(page_index)+"]"+"/div/div/div/div/div/div/div/div/div/div[2]/span[1]/a"
    elements = wd.find_elements(By.XPATH, AnswerIndex )
#     print(elements)
    if len(elements)==0:
        return True
    elif elements[0].text != 'No answer yet':
        return True
    else:
        return False


def ScrolltoCertain(page_index , wd ,parent_handle):
    '''
    to avoid start from zero, scroll down to desire part
    page_index: which answer you want start, like if I want to start from 50th question, page_index=50,
                the progress would scroll down until the 50th question shows on screen.
    '''
    if wd.current_window_handle != parent_handle:
        wd.switch_to.window(wd.window_handles[0])
    findFlag = True
    while (findFlag):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(PAUSE_TIME)
        page_url = "//*[@id='mainContent']/div[2]/div[2]/div[" +str(page_index)+"]"+"/div/div/div/div/div/div/div/div/div/div[1]/div/span/span/a/div/div/div/div"
        targetPage = wd.find_elements(By.XPATH, page_url )
        if len(targetPage) !=0:
            findFlag =False
            
            

PAUSE_TIME =1.0
def data_to_df( wd):
    '''
    this is a substitude function of data_acquire and to_dataframe
    Here I combine the two steps into one
    Notice: the xpath links don't looks the same among spaces, so add new one in the following list.
    Returns
    -------
    df : TYPE dataframe
        DESCRIPTION.

    '''
    
    time.sleep(PAUSE_TIME)
    #get question
    question = wd.find_element(By.XPATH,"//*[@id='mainContent']/div/div[1]/div/div/div/div[1]/span/span/div/div/div/span/span").text

    # first get blocks
    blocks = wd.find_elements(By.XPATH,'//*[@id="mainContent"]/div/div[2]/div[*]')
    column_names = ["Question", "authorID", "content","upvote"]
    df = pd.DataFrame(columns = column_names)
    # from each block get answer, author and upvote
    for b in blocks[1:]:
        authorID = b.find_elements(By.XPATH,'.//div/div/div/div/div/div/div/div/div[1]/div[1]/div/div/div/div/div[2]/div[1]/span[1]/span')
        print(len(authorID))
        if len(authorID)==0:
            authorID = b.find_elements(By.XPATH,'.//div/div/div/div/div/div[1]/div/div/div[1]/div/div/div/div/div[2]/div[1]/span[1]/span/div/div/div/div/div/a/div/span/span')
        print(len(authorID))
        
        answer = ''    
        answer_list = ['.//div/div/div/div/div/div/div/div/div[1]/div[2]/div/div',
                       './/div/div/div/div/div/div/div/div/div[2]/div/div[1]',
                       './/div/div/div/div/div/div[1]/div/div/div[2]/div/div/div',
                       './/div/div/div/div/div/div/div/div/div[2]/div/div/div[1]']   
        answer_lenth = 0
        for a in answer_list:
            option = b.find_elements(By.XPATH,a)
            if len(option)!=0 and len(transText(option)[0])>answer_lenth:
                answer_lenth = len(transText(option)[0])
                answer = transText(option)[0]
            
        # print(answer)
        upvote = b.find_elements(By.XPATH,'.//div/div/div/div/div/div/div/div/div[*]/div/div/div[1]/div/div[1]/div/button/div[2]/span[2]')
        authorID = transText(authorID)
        answer = [answer]
        upvote = transText(upvote)
        if len(upvote) ==0:
            upvote =['0']

        df.loc[len(df.index)] = [question, authorID, answer,upvote] 
        print(df)
    # df = df.drop(0,axis=0)
    df['rank'] = range(1,len(df)+1)
    df['authorID'] = df['authorID'].apply(lambda x: x[0])
    df['content'] = df['content'].apply(lambda x: x[0])
    df['upvote'] = df['upvote'].apply(lambda x: x[0])
    df[['Question','content']] = df[['Question','content']].apply(lambda x: x.str.replace(',',' '))
    df['content'] = df['content'].apply(lambda x: x.replace('\n',''))
    return df

def main(url,driver):

    wd = driver
    # Select three Quora space to get all the answers and questions
    
    wd.get(url)
    space_name = url.split(sep='.')[0].split('//')[1]
    
    wd.implicitly_wait(3)
    parent_handle = wd.current_window_handle
    
    page_index = 1
    # if certain webpage doesn't work, could set certain page in stop_page to move forward
    # stop_page = [79,122]
    stop_page = []
    
    # if you want to start from certain page, use this function to scroll down to desire page
    # ScrolltoCertain(page_index,wd,parent_handle)
    
    flag = True
    while (flag):
        if hasAnswered(page_index,wd,parent_handle) == False or page_index in stop_page:
            page_index +=1
            print('leave one unanswered question ',page_index)
            continue
        else:
            try:
    
                Into_QA(wd, page_index,parent_handle)
            except:
                print("Error in entering into %d",page_index)
                # ScrolltoCertain(page_index,wd,parent_handle)
    #             flag = False
                page_index +=1
                continue
            switch_sorting(page_index,wd)
            # if there is hidden content, show all 
            fullContent = wd.find_elements(By.XPATH,'//*[@id="mainContent"]/div/div[2]/div[*]/div/div/div/div/div/div/div/div/div[1]/div[*]/div/div/div[2]/div[1]/div/div/div/span/div/div/div/button/div/div/div')

            fullContent.extend(wd.find_elements(By.XPATH,'//*[@id="mainContent"]/div/div[2]/div[*]/div/div/div/div/div/div/div/div/div[2]/div/div/div[2]/div[1]/div/div/div/span/div/div/div/button/div/div/div'))

            for i in fullContent:
                i.click()
    
            try:
                result = data_to_df(wd)
    #         ques,author,answer,upvote,answerb = data_acquire()  # retrieve data
    #         result = to_dataframe(ques,author,answer,upvote,answerb) #make a dataframe
            except:
                print("Error in retrieve a piece of data",page_index)
                page_index +=1
                out_QA(wd,parent_handle)
                continue
            print(result)
            writeData(result,page_index,space_name) #store
            out_QA(wd,parent_handle)
    
            page_index = page_index+1
    return 


if __name__ == "__main__":
    url = 'https://cryptocurrency.quora.com/questions'
    url2 = 'https://softskillsandautism.quora.com/questions'
    url3 = 'https://softwareengineeringexperiences.quora.com/questions'
    url4 = 'https://thedoctorsroom.quora.com/questions'
   
    wd1 = webdriver.Chrome(service=Service(r'D:\chromedriver_win32\chromedriver.exe'))
    wd2 = webdriver.Chrome(service=Service(r'D:\chromedriver_win32\chromedriver.exe'))
    wd3 = webdriver.Chrome(service=Service(r'D:\chromedriver_win32\chromedriver.exe'))
    wd4 = webdriver.Chrome(service=Service(r'D:\chromedriver_win32\chromedriver.exe'))
    # main(url=url)    
       
    threads = []
    # use multi thread to process, save time
    t1 = threading.Thread(target=main,args=(url,wd1))
    threads.append(t1)
    t1.start()
    t2 = threading.Thread(target=main,args=(url2,wd2))
    threads.append(t2)
    t2.start()
    t3 = threading.Thread(target=main,args=(url3,wd3))
    threads.append(t3)
    t3.start()
    t4 = threading.Thread(target=main,args=(url4,wd4))
    threads.append(t4)
    t4.start()
    
    #haved realized Threadpool
    # with ThreadPoolExecutor(max_workers=3) as executor:
    #     executor.map(get_handles, files, drivers)
    print('Better call saul is awesome!')
    #testing
    # main(url2,wd2)