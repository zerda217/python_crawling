from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import chromedriver_autoinstaller
from selenium import webdriver
from time import time, sleep
import datetime as dt
import pandas as pd
import os.path
import random
import re
import os


def cobaroScraping():
    chrome_ver = chromedriver_autoinstaller.get_chrome_version().split(".")[0]
    print("현재 크롬 버전 : ", chrome_ver)
    driver_path = f"../{chrome_ver}/chromedriver"  # 크롬드라이버 설치 주소
    if os.path.exists(driver_path):
        print(f"크롬 드라이버 버전 확인: {driver_path}")
    else:
        print(f"크롬 드라이버 자동 설치(ver: {chrome_ver})")
        chromedriver_autoinstaller.install(True)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    print("옵션 추가")
    driver = webdriver.Chrome(
        executable_path=driver_path, chrome_options=chrome_options
    )
    print("성공")
    start = time()

    baseUrl = "http://www.cobaro.co.kr/shop/main/index.php"
    loginUrl = "http://www.cobaro.co.kr/shop/member/login.php?returnUrl=/shop/mypage/mypage_orderlist.php"
    orderUrl = "http://www.cobaro.co.kr/shop/mypage/mypage_orderlist.php?&&"

    st_id = "id"  # 아이디
    st_pw = "pw"  # 패스워드

    sorry = random.randint(3, 10)

    today = dt.datetime.now().strftime("%m/%d")
    tomorrow = dt.datetime.strptime(today, "%m/%d") + dt.timedelta(days=1)
    tomorrowday = tomorrow.strftime("%m/%d")
    isTime = dt.datetime.now().strftime("%H")
    if int(isTime) < 12:
        scrapDay = today
    else:
        scrapDay = tomorrowday
    fileDate = "23" + re.sub("[^0-9]", "", scrapDay).strip()

    print("코바로 스크래핑 실행", today)
    driver.get(loginUrl)
    sleep(sorry)

    input_id = driver.find_element(by=By.NAME, value="m_id")
    input_pw = driver.find_element(by=By.NAME, value="password")
    input_id.send_keys(st_id)
    sleep(sorry)
    input_pw.send_keys(st_pw)
    print("id/pw 입력")
    sleep(sorry)

    driver.find_element(
        By.XPATH, '//*[@id="form"]/table/tbody/tr[1]/td[3]/input'
    ).click()

    sleep(sorry)
    print("로그인 성공")

    sourceJson = driver.page_source
    soup_json = bs(sourceJson, "html.parser")
    order_list = soup_json.find("form", {"name": "frmOrderList"})
    sleep(sorry)

    print("주문 내역", soup_json.find("title"))

    # 주문리스트 만들기
    cleanr = re.compile("<.*?>")

    header_list = []
    number_list = []
    order_rnqns_list = []
    order_date_list = []
    order_number_list = []
    order_payment_list = []
    order_price_list = []
    order_status_list = []

    tbody = order_list.tbody.find_all("tr")
    fileDate = "23" + re.sub("[^0-9]", "", scrapDay).strip()

    for tr in tbody:
        if tr.find("th", {"style": "background:#5d584e;color:#fff;"}):
            for th_i in tr:
                cleantext = re.sub(cleanr, "", str(th_i))
                if cleantext != "\n":
                    header_list.append(cleantext)
        else:
            if tr.find("td", {"class": "stxt"}) is not None and (
                tr.find("td", {"class": "stxt"}).get_text() == "배송중"
                or tr.find("td", {"class": "stxt"}).get_text() == "결제완료"
                or tr.find("td", {"class": "stxt"}).get_text() == "배송준비중"
            ):
                print("배송중...")
                tds = tr.find_all("td", {"align": "center"})
                for td in tds:
                    index = int(tds.index(td))
                    if index == 0:
                        number_list.append(tds[index].text)
                    elif index == 1:
                        order_rnqns_list.append(tds[index].text)
                    elif index == 2:
                        order_date_list.append(tds[index].text)
                    elif index == 3:
                        order_number_list.append(tds[index].text)
                    elif index == 4:
                        order_payment_list.append(tds[index].text)
                    elif index == 5:
                        order_price_list.append(tds[index].text)
                    elif index == 6:
                        order_status_list.append(tds[index].text)
                        if tds[index].text == "배송중" or tds[index].text == "입금확인":
                            driver.get(
                                f"http://www.cobaro.co.kr/shop/mypage/mypage_orderview.php?&ordno={tds[3].text}"
                            )
                            detail = driver.page_source
                            df1 = pd.read_html(detail)
                            df_filter = df1[9].loc[:, ["상품정보.1", "판매가", "수량"]]
                            df_new = df_filter.rename(columns={"상품정보.1": "name"})
                            df_result = df_new.dropna()
                            df_result["unit_price"] = df_result["판매가"].apply(
                                lambda x: int(re.sub("[^0-9]", "", x.strip()))
                            )
                            df_result["unit_amount"] = df_result["수량"].apply(
                                lambda x: int(re.sub("[^0-9]", "", x.strip()))
                            )
                            df_result = df_result.loc[
                                :, ["name", "unit_price", "unit_amount"]
                            ]

                            df_new = df_filter.rename(columns={"상품정보.1": "name"})
                            df_dropna = df_new.dropna()
                            df_dropna["name"]
                            df_result["unit_string"] = df_dropna["name"].apply(
                                lambda x: re.search(
                                    "[0-9]+\s*[A-Z]+\s*[x|X]+\s*([0-9])", x
                                ).group()
                            )
                            df_result["unit_weight"] = df_result["unit_string"].apply(
                                lambda x: (
                                    int(re.sub("[^0-9]", "", x.split("X")[0]))
                                    * int(x.split("X")[1])
                                )
                            )
                            df_result["unit"] = df_result["unit_string"].apply(
                                lambda x: re.sub("[^a-zA-Z,.]", "", x.split("X")[0])
                            )
                            df_result["unit_quantity"] = df_result["unit_string"].apply(
                                lambda x: int(x.split("X")[1])
                            )
                            df_result = df_result.loc[
                                :,
                                [
                                    "name",
                                    "unit",
                                    "unit_price",
                                    "unit_amount",
                                    "unit_weight",
                                    "unit_quantity",
                                ],
                            ]

                            # 테이블 저장
                            df = pd.DataFrame(order_date_list, columns=["order_date"])
                            df["order_id"] = order_number_list
                            df["order_status"] = order_status_list
                            df_filter2 = df.loc[
                                :, ["order_date", "order_id", "order_status"]
                            ]
                            df_filter2 = df_filter2.astype({"order_id": "string"})
                            df = df_result.join(df_filter2)
                            df_today = df.fillna(method="ffill")
                            print(f"입고 예정 물품 수: ", len(df_today))

                            df_today.to_json(
                                f"cobaro{fileDate}_{st_id}.json",
                                orient="records",
                                force_ascii=False,
                            )
                            end = time()
                            print(f"{scrapDay} 파일 저장 // 배송 상품 있음")
                            break
                break
            else:
                f = open(f"./cobaro{fileDate}_{st_id}.json", "w")
                data = "[]"
                f.write(data)
                f.close()
                print(f"{scrapDay} 파일 저장 // 배송 상품 없음")
                break

    driver.quit()

    end = time()
    print("총 소요시간:", end - start)
    print("== 완료 ===================================================================")
