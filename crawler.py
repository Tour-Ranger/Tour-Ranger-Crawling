# Standard Library
import csv
import json
import os
import time
from multiprocessing import Pool

# Third Party Library
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

CRAWLING_TARGET_CSV_FILE = "crawling_target.csv"
RESULT_ROOT = "result"
STR_P_NAME = "parent"
STR_C_NAME = "child"
STR_URL = "url"
PROCESSES = 5


class DanawaCrawler:
    def __init__(self):
        # 크롤링 작업에 필요한 정보를 담은 리스트. 구조는 아래 참조.
        self.crawling_category = list()
        # CRAWLING_TARGET_CSV_FILE 에서 크롤링 대상에 대한 정보를 얻어옴.
        with open(
            CRAWLING_TARGET_CSV_FILE, "r", newline="", encoding="utf8"
        ) as file:
            for crawling_values in csv.reader(file, skipinitialspace=True):
                if not crawling_values[0].startswith("//"):
                    self.crawling_category.append(
                        {
                            STR_P_NAME: crawling_values[0],
                            STR_C_NAME: crawling_values[1],
                            STR_URL: crawling_values[2],
                        }
                    )

    def start_crawling(self) -> None:
        """
        multiprocessing을 위한 매서드.
        crawling_category의 요소들을 Pool을 통해 배정한다.
        PROCESSES 변수를 이용해 한번에 몇개의 프로세스를 실행할 건지 정할 수 있다.
        """
        if __name__ == "__main__":
            pool = Pool(processes=PROCESSES)
            pool.map(self.crawling_product, self.crawling_category)
            pool.close()
            pool.join()

    def crawling_product(self, category_value: dict[str, str]) -> None:
        """
        크롤링에 사용되는 동작을 정의한 메서드
        StartCrawling에 의해 호출된다.

        Args:
            category_value (dict[str, str]): 크롤링 대상에 대한 정보를 정리한 dict.
        """
        crawling_name: str = (
            category_value[STR_P_NAME] + "_" + category_value[STR_C_NAME]
        )
        crawling_url: str = category_value[STR_URL]
        crawled_product: int = 0

        # 결과를 저장할 폴더가 없다면 생성한다.
        try:
            if not os.path.exists(RESULT_ROOT):
                os.makedirs(RESULT_ROOT)
        except OSError:
            print("Error: Failed to create the directory.")
        # data를 저장할 csv 파일 경로. result 폴더 아래에 생성한다.
        crawling_file = open(
            f"{RESULT_ROOT}/{crawling_name}.csv", "w", newline="", encoding="utf8"
        )
        crawling_csv_writer = csv.writer(crawling_file)

        print(f"{crawling_name} 크롤링 시작!")

        try:
            browser = webdriver.Chrome()
            browser.implicitly_wait(5)
            browser.get(crawling_url)

            wait = WebDriverWait(browser, 10)
            wait.until(
                EC.invisibility_of_element(
                    (By.CLASS_NAME, "list_travel_goods_cover")
                )
            )
            browser.implicitly_wait(2)

            # 검색 결과가 몇건인지 확인한다. (10,000)의 형태로 되어있다.
            crawling_size = browser.find_element_by_xpath(
                    '//*[@id="danawa-tour-TourProductList-product-tab-1"]/span'
                ).text
            # 괄호와 콤마 제거 후 int로 변환
            crawling_size = int(''.join(filter(str.isdigit, crawling_size)))
            # 몇 페이지 까지 크롤링 해야하는지를 확인한다. 한 페이지당 30건을 표시하고 있기 때문에 30으로 나눈 몫을 구한다.
            crawling_page_size: int = crawling_size // 30 + 1

            for i in range(1, crawling_page_size + 1):
                # 첫 페이지 차례가 아니라면 다음 페이지로 이동.
                if i != 1:
                    browser.find_element_by_xpath(
                        '//*[@id="tour-paging-utils-id-link-productList-%d"]'
                        % (i)
                    ).click()

                # 차단 우회도 노릴 겸. 페이지 로딩을 기다림.
                wait.until(
                    EC.invisibility_of_element(
                        (By.CLASS_NAME, "list_travel_goods_cover")
                    )
                )
                time.sleep(2)

                # 상품 목록을 불러옴
                product_list_div = browser.find_element_by_xpath(
                    '//*[@id="danawa-tour-TourProductList-product-self"]'
                )
                products = product_list_div.find_elements_by_xpath(
                    '//ul[@class="list_travel_goods"]/li'
                )

                # 상품검색이 더 이상 불가할 경우 종료. 약 300페이지를 넘었을 경우 로드를 못하는 문제가 있다.
                if product_list_div.find_elements_by_class_name(
                    "cont_no_result"
                ):
                    break

                for product in products:
                    # 해당 객체가 광고라면 skip.
                    if "prod_ad_item" in product.get_attribute("class").split(
                        " "
                    ) or product.get_attribute("id").strip().startswith("ad"):
                        continue

                    product_img = product.find_element_by_xpath(
                        "./div/div[1]/div/img"
                    ).get_attribute("src")
                    product_title = product.find_element_by_xpath(
                        "./div/div[1]/div/img"
                    ).get_attribute("alt")
                    product_company = product.find_element_by_xpath(
                        "./div/div[2]/a/div[1]/img"
                    ).get_attribute("alt")
                    product_company_img = product.find_element_by_xpath(
                        "./div/div[2]/a/div[1]/img"
                    ).get_attribute("src")
                    product_d_date = product.find_element_by_xpath(
                        "./div/div[2]/a/div[3]/span[1]"
                    ).text
                    product_a_date = product.find_element_by_xpath(
                        "./div/div[2]/a/div[3]/span[2]"
                    ).text
                    product_date = product.find_element_by_xpath(
                        './/span[@class="date"]'
                    ).text
                    porduct_airline = product.find_element_by_xpath(
                        "./div/div[2]/a/div[3]/span[4]/span"
                    ).text
                    porduct_airline_img = product.find_element_by_xpath(
                        "./div/div[2]/a/div[3]/span[4]/span/img"
                    ).get_attribute("src")
                    product_price = product.find_element_by_xpath(
                        "./div/div[3]/a/p/strong"
                    ).text

                    crawling_csv_writer.writerow(
                        [
                            product_img,
                            product_title,
                            product_company,
                            product_company_img,
                            product_d_date,
                            product_a_date,
                            product_date,
                            porduct_airline,
                            porduct_airline_img,
                            product_price,
                        ]
                    )
                    crawled_product += 1
        except Exception as e:
            # 에러 출력
            print("Error - " + crawling_name + " ->")
            print(e)

        # 작성 끝난 csv 파일 연결 종료
        crawling_file.close()
        # 탐색 끝난 브라우저 종료
        browser.quit()
        print(f"{crawling_name} 크롤링 종료! {crawled_product}/{crawling_size} 완료!")

    def merge_whole_data(self) -> None:
        """
        각 페이지에 대한 크롤링 결과를 하나의 파일로 합치는 메서드.
        """
        # 결과 csv의 칼럼 이름 정보
        col_names = [
            "product_img",
            "product_title",
            "product_company",
            "product_company_img",
            "product_Ddate",
            "product_Adate",
            "product_date",
            "porduct_airline",
            "porduct_airline_img",
            "product_price",
        ]

        # 결과를 기록할 DataFrame 생성. 칼럼 이름은 col_names을 사용하여 정한다.
        df_all = pd.DataFrame(columns=col_names)
        # result 폴더에 생성한 결과 파일 목록 확인
        files = os.listdir("result")
        
        for i in range(0, len(files)):
            if files[i].split(".")[1] == "csv":
                file = "result/" + files[i]
                print(file)
                df = pd.read_csv(file, encoding="utf-8", header=None)
                df.columns = col_names
                df_all = pd.concat([df_all, df], ignore_index=True, axis=0)
                # DataFrame의 shape 메서드는 (row개수, col개수)를 반환한다.
                # 만약 col의 수가 10이 아니라면 의도와 다르게 병합이 이루어진 것 이므로 정지한다.
                if df_all.shape[1] != 10:
                    print(files[i])
                    break
        print(f"병합이 끝났습니다! 크롤링을 통해 총 {df_all.shape[0]}개의 데이터를 수집했습니다!")
        # 결과를 csv로 저장.
        df_all.to_csv("all_result.csv", encoding="utf-8")
        # 결과를 json으로 저장.
        dict_all = df_all.to_dict(orient="records")
        json_str = json.dumps(dict_all, indent=4, ensure_ascii=False)
        with open("all_result.json", "w", encoding="utf-8") as json_file:
            json_file.write(json_str)


if __name__ == "__main__":
    crawler = DanawaCrawler()
    crawler.start_crawling()
    crawler.merge_whole_data()
