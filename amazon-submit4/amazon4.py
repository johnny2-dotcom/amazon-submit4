from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import pandas as pd
from datetime import datetime
import re


def product_search():
    driver = webdriver.Chrome(ChromeDriverManager().install())

    url = 'https://www.amazon.co.jp/gp/bestsellers/kitchen/ref=zg_bs_kitchen_home_all?pf_rd_p=234a2e41-c662-4f1c-987f-e3b33cc421ff&pf_rd_s=center-1&pf_rd_t=2101&pf_rd_i=home&pf_rd_m=AN1VRQENFRJN5&pf_rd_r=69W2MBGRT6S8E3WYBSCH&pf_rd_r=69W2MBGRT6S8E3WYBSCH&pf_rd_p=234a2e41-c662-4f1c-987f-e3b33cc421ff'

    driver.get(url)
    sleep(2)

    p_names = []
    link_urls = []
    while True:
        for i in range(1,52):
            if i < 5:
                p_name = driver.find_element_by_css_selector('#zg-ordered-list > li:nth-child({}) > span > div > span > a > div'.format(i)).text
                link_url = driver.find_element_by_css_selector('#zg-ordered-list > li:nth-child({}) > span > div > span > a'.format(i)).get_attribute('href')
                p_names.append(p_name)
                link_urls.append(link_url)
            elif i == 5:
                pass
            else:
                p_name = driver.find_element_by_css_selector('#zg-ordered-list > li:nth-child({}) > span > div > span > a > div'.format(i)).text
                link_url = driver.find_element_by_css_selector('#zg-ordered-list > li:nth-child({}) > span > div > span > a'.format(i)).get_attribute('href')
                p_names.append(p_name)
                link_urls.append(link_url)

        if len(driver.find_elements_by_css_selector('#zg-center-div > div.a-row.a-spacing-top-mini > div > ul > li.a-last > a')) > 0:
            next_page = driver.find_element_by_css_selector('#zg-center-div > div.a-row.a-spacing-top-mini > div > ul > li.a-last > a').get_attribute('href')
            driver.get(next_page)
            sleep(2)
        else:
            break

    names = []
    prices = []
    deliveries = []
    asins = []
    for item_url in link_urls:
        driver.get(item_url)
        sleep(4)

        name = driver.find_element_by_id('productTitle')
        names.append(name.text)

        if len(driver.find_elements_by_css_selector('#priceblock_ourprice')) > 0:
            _price = driver.find_element_by_css_selector('#priceblock_ourprice')
            price = int(_price.text.replace('￥','').replace(',',''))
            prices.append(price)
        elif len(driver.find_elements_by_css_selector('#priceblock_dealprice')) > 0:
            _price = driver.find_element_by_css_selector('#priceblock_dealprice')
            price = int(_price.text.replace('￥','').replace(',',''))
            prices.append(price)
        elif len(driver.find_elements_by_css_selector('#olp_feature_div > div.a-section.a-spacing-small.a-spacing-top-small > span > a > span.a-size-base.a-color-price')) > 0:
            _price = driver.find_element_by_css_selector('#olp_feature_div > div.a-section.a-spacing-small.a-spacing-top-small > span > a > span.a-size-base.a-color-price')
            price = int(_price.text.replace('￥','').replace(',',''))
            prices.append(price)
        else:
            price = ''
            prices.append(price)
    
        if len(driver.find_elements_by_css_selector('#mir-layout-DELIVERY_BLOCK-slot-DELIVERY_MESSAGE > b')) > 0:
            if len(driver.find_elements_by_css_selector('#oneTimePurchaseDefaultDeliveryDate > span')) > 0:
                delivery = driver.find_element_by_css_selector('#oneTimePurchaseDefaultDeliveryDate > span').text
                deliveries.append(delivery)
            else:
                delivery = driver.find_element_by_css_selector('#mir-layout-DELIVERY_BLOCK-slot-DELIVERY_MESSAGE > b').text
                deliveries.append(delivery)       
        elif len(driver.find_elements_by_css_selector('#mir-layout-DELIVERY_BLOCK-slot-UPSELL > b')) > 0:
            delivery = driver.find_element_by_css_selector('#mir-layout-DELIVERY_BLOCK-slot-UPSELL > b').text
            deliveries.append(delivery)
        elif len(driver.find_elements_by_css_selector('#ddmDeliveryMessage > b')) > 0:
            delivery = driver.find_element_by_css_selector('#ddmDeliveryMessage > b').text
            deliveries.append(delivery)
        # 次の配達日が取得できなかったが、上記の一番目のセレクタの配達日テキストがページ画面上は見えないが、HTMLには存在しており、それが干渉して要素のテキスト取得が出来ていなかったため、一番上のifの中に入子構造で入れることによって解決した。
        # elif len(driver.find_elements_by_css_selector('#oneTimePurchaseDefaultDeliveryDate > span')) > 0:
        #     delivery = driver.find_element_by_css_selector('#oneTimePurchaseDefaultDeliveryDate > span').text
        #     deliveries.append(delivery)
        elif len(driver.find_elements_by_css_selector('#availability > span.a-size-medium.a-color-state')) > 0:
            delivery = driver.find_element_by_css_selector('#availability > span.a-size-medium.a-color-state').text
            deliveries.append(delivery)
        else:
            delivery = ''
            deliveries.append(delivery)

        if len(driver.find_elements_by_css_selector('#detailBullets_feature_div > ul > li')) > 0:
            texts = driver.find_elements_by_css_selector('#detailBullets_feature_div > ul > li')
            for _text in texts:
                pattern = r'^ASIN : B.*'
                result = re.search(pattern,_text.text)
                if result == None:
                    pass
                else:
                    asin = result.group().split(':')[1].replace(' ','')
                    asins.append(asin)
        elif len(driver.find_elements_by_css_selector('#productDetails_detailBullets_sections1 > tbody > tr:nth-child(1) > td')) > 0:
            asin = driver.find_element_by_css_selector('#productDetails_detailBullets_sections1 > tbody > tr:nth-child(1) > td').text
            asins.append(asin)
        else:
            asin = ''
            asins.append(asin)

    # driver.close()

    df = pd.DataFrame()
    df['商品名'] = p_names
    df['商品ページへのURL'] = link_urls
    df['商品名（詳細）'] = names
    df['価格（円）'] = prices
    df['発送リードタイム（納期）'] = deliveries
    df['ASIN'] = asins

    time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    df.to_csv('売れ筋ランキング一覧:{}.csv'.format(time),index=False)

if __name__ == "__main__":
    product_search()