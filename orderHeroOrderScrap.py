from bs4 import BeautifulSoup as bs
from time import time, sleep
import datetime as dt
import pandas as pd
import requests
import time
import re


def orderScraping():
    start = time()

    loginUrl = "https://orderherodl.cafe24.com/php/api/login.php"
    orderUrl = "https://orderherodl.cafe24.com/order-tracking.php"

    id_list = ["id"]  # 아이디
    pw_list = ["pw"]  # 패스워드

    today = dt.datetime.now().strftime("%m/%d")
    tomorrow = dt.datetime.strptime(today, "%m/%d") + dt.timedelta(days=1)
    tomorrowday = tomorrow.strftime("%m/%d")
    isTime = dt.datetime.now().strftime("%H")
    if int(isTime) < 10:
        scrapDay = today
    else:
        scrapDay = tomorrowday
    fileDate = "23" + re.sub("[^0-9]", "", scrapDay).strip()

    print("오더히어로 스크래핑 실행", today)
    sleep(1)

    session = requests.Session()

    for store_id in id_list:
        index = int(id_list.index(store_id)) + 1

        res = session.post(
            loginUrl,
            data={
                "cust_id": store_id,
                "password": pw_list[int(id_list.index(store_id))],
            },
        )
        res.raise_for_status()
        result = session.get(orderUrl)
        soup = bs(result.text, "html.parser")
        soup_string = str(soup)

        with open(f"./orderHeroRow{fileDate}_{store_id}.json", "w") as f:
            f.write(soup_string)
            print("row data 저장")

        print(f"{index}번째 {store_id} soup.parser", soup.find("title"))
        sleep(1)

        order_tracking_list = []
        order_date_list = []
        order_id_list = []
        product_name_list = []
        delivery_status_list = []
        product_title_list = []
        product_info_list = []
        storage_list = []
        weight_list = []
        price_list = []
        unit_price_list = []
        amount_list = []
        unit_list = []
        unit_amount_list = []

        # 날짜 단위로 리스트
        orderList = soup.find_all(
            "li",
            {
                "class": "li_ordr_tracking link_block_cancel_return w-inline-block w-clearfix"
            },
        )

        for list in orderList:
            order_tracking = list.find("div", {"class": "orderDate"}).text
            product_detailproductname = list.find(
                "div", {"class": "text_detailproductname"}
            )

            # []로 저장
            product_detail_info = list.select("div.text_detailproductname")

            # 상품 단위로 리스트
            for product in product_detail_info:
                # 주문날짜:
                order_date = order_tracking.split("(")[0].split(" ")[0]
                order_id = order_tracking.split("(")[1].split(")")[0]
                # 주문번호:
                order_date_list.append(order_date)
                order_id_list.append(order_id)
                # 주문날짜 + 주문번호:
                order_tracking_list.append(order_tracking)
                # 주문상품:
                product_name = product.find("span", {"class": "prod_name"}).text
                product_name_list.append(product_name)
                # 상품정보:
                product_info = product.find("span", {"class": "prod_info"}).text
                product_info_list.append(product_info)
                storage = product_info[-2:]
                storage_list.append(storage)

                weight = product_info.split("/")[1]
                weight_list.append(weight)

                unit_list.append(re.sub("[^a-zA-Z]", " ", weight).strip())
                unit_amount_str = re.sub("[^0-9,.]", " ", weight).strip()

                if unit_amount_str == "":
                    unit_amount_list.append(int(1))
                elif "." in unit_amount_str:
                    unit_amount_list.append(float(unit_amount_str))
                else:
                    unit_amount_list.append(
                        int(
                            unit_amount_str.split(" ")[
                                len(unit_amount_str.split(" ")) - 1
                            ]
                        )
                    )

                # 가격
                product_price_a = product.get_text()
                product_price_b = product_price_a[-50:].replace("\n", "")
                product_price_result = product_price_b.replace(" ", "")
                price_list.append(product_price_result)

                if "개" in product_price_result:
                    product_amount = (
                        product_price_result.split("=")[0].split("X")[1].split("개")[0]
                    )
                    amount_list.append(int(product_amount))
                else:
                    amount_list.append(int(0))

                if "원" in product_price_result:
                    unit_price = (
                        product_price_result.split("=")[0].split("X")[0].split("원")[0]
                    )
                    unit_price_list.append(
                        int(re.sub("[^0-9]", "", unit_price).strip())
                    )
                else:
                    unit_price_list.append(int(0))  # 가격이 없으면 0

        print("총 상품 개수: ", len(product_name_list))
        sleep(1)

        # 주문상태값
        move_list = []
        ongoing_list = []
        title_list = []
        day_list = []

        textli_ordr = soup.find_all("div", {"class": "area_textli_ordr"})

        for list in textli_ordr:
            llist = list.find_all("div", {"class": "block_detailproduct"})
            for row in llist:
                title = row.find_all("span", {"class": "prod_name"})
                title_list.append(title)
                n = 0
                span = row.find_all("span", {"class": "prod_move_title"})
                ongoing = row.find("div", {"class": "text_detailproduct ongoing"})

                if len(span) == 1:
                    move_list.append(span)
                    ongoing_list.append(ongoing)
                else:
                    move_list_copy = move_list[n - 1]
                    move_list.append(move_list_copy)
                    ongoing_list_copy = ongoing_list[n - 1]
                    ongoing_list.append(ongoing_list_copy)
                n = n + 1

        pd.set_option("display.max_rows", None)
        df_sample = pd.DataFrame(move_list, columns=["업체"])
        df_sample["title"] = title_list
        df_sample["ongoing"] = ongoing_list

        for idx, row in df_sample.iterrows():
            if len(row.title) > 0:
                dayText = re.sub("[^0-9가-힣/()]", "", row["ongoing"].text).strip()
                day_list.append(dayText)

        print("출고 상태 개수: ", len(day_list))
        sleep(1)

        # 테이블 저장
        df = pd.DataFrame(product_name_list, columns=["name"])
        df["unit"] = unit_list
        df["delivery"] = day_list
        df["order_id"] = order_id_list
        df["order_date"] = order_date_list
        df["unit_price"] = unit_price_list
        df["unit_amount"] = unit_amount_list
        df["unit_weight"] = weight_list
        df["unit_quantity"] = amount_list

        filter_df = df[~df["delivery"].astype(str).str.contains("배송완료")]
        print("입고 예정 물품 수: ", len(filter_df))
        sleep(1)

        filter_df.to_json(
            f"./orderHeroList{fileDate}_{store_id}.json",
            orient="records",
            force_ascii=False,
        )

        print(f"{scrapDay} 파일 저장 ( {index}/{int(len(id_list))} )")

        sleep(1)

    end = time()
    print("총 소요시간:", end - start)
    print("== 완료 ===================================================================")
