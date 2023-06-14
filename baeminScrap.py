from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from time import time, sleep
import random

start = time()

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


mainUrl = "https://note.baemin.com/"
loginUrl = "https://ceo.baemin.com/web/login?returnUrl=https%3A%2F%2Fceo.baemin.com%2F"
orderHistoryUrl = "https://ceo.baemin.com/self-service/orders/history"
st_id = "id"  # 아이디
st_pw = "pw"  # 비밀번호
sorry = random.randint(3, 10)

driver.get(loginUrl)

print("배민 ceo 스크래핑 실행", sorry)
sleep(sorry)

input_id = driver.find_element(by=By.NAME, value="id")
input_pw = driver.find_element(by=By.NAME, value="password")
input_id.send_keys(st_id)
sleep(sorry)
input_pw.send_keys(st_pw)
print("id/pw 입력")
sleep(sorry)

driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div/div/form/button').click()
print("로그인 성공")
