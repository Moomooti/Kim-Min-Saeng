import time
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1. DB 연결 및 테이블 준비
conn = sqlite3.connect('DB/raw_results.sqlite')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS stores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        address TEXT,
        notice TEXT,
        crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

# 2. Selenium 드라이버 세팅
options = Options()
# options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)

keyword = '서울시 음식점'
start_url = f"https://map.naver.com/v5/search/{keyword}?c=10.61,0,0,0,dh"
driver.get(start_url)
print("[DEBUG] 현재 페이지 URL:", driver.current_url)
time.sleep(4)

# === 반드시 src에 search가 포함된 iframe으로 전환 ===
def switch_to_search_iframe():
    driver.switch_to.default_content()
    for _ in range(5):
        try:
            search_iframe = WebDriverWait(driver, 7).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='search']"))
            )
            driver.switch_to.frame(search_iframe)
            print("[INFO] search iframe 전환!")
            return True
        except:
            time.sleep(1)
    print("[ERROR] search iframe 못 찾음!")
    return False

switch_to_search_iframe()

count = 0
page = 1

while count < 500:
    # 1페이지씩 (탭 닫는 구조 말고, 리스트에서 바로 클릭)
    scroll = driver.find_element(By.CSS_SELECTOR, '#_pcmap_list_scroll_container')
    li_list = scroll.find_elements(By.CSS_SELECTOR, 'ul > li')
    for li in li_list:
        if count >= 500:
            break
        try:
            name_elem = li.find_element(By.CSS_SELECTOR, 'span.TYaxT')
            name = name_elem.text.strip()
            if not name:
                continue
            parent_a = name_elem.find_element(By.XPATH, './ancestor::a[1]')
            driver.execute_script("arguments[0].click();", parent_a)
            time.sleep(1.5)

            # entry iframe 전환
            driver.switch_to.default_content()
            entry_iframe = WebDriverWait(driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='entry']"))
            )
            driver.switch_to.frame(entry_iframe)
            time.sleep(1)

            # 주소
            try:
                address = driver.find_element(By.CSS_SELECTOR, 'span.LDgIH').text
            except:
                address = ""

            # 소식탭 클릭
            news_tab = None
            for tab in driver.find_elements(By.CSS_SELECTOR, 'span.veBoZ'):
                if "소식" in tab.text:
                    news_tab = tab
                    break
            if not news_tab:
                print(f"{name}: 소식탭 없음, PASS")
            else:
                driver.execute_script("arguments[0].click();", news_tab)
                time.sleep(1)
                notice_found = False
                for news in driver.find_elements(By.CSS_SELECTOR, 'div.pui__dGLDWy'):
                    text = news.text
                    if any(kw in text for kw in [
                        "민생지원금", "민생회복", "민생 쿠폰",
                        "민생소비쿠폰", "민생소비", "소비쿠폰"
                    ]):
                        print(f"   ★ 저장: {name}, {address}, {text[:30]}")
                        cursor.execute(
                            'INSERT INTO stores(name,address,notice) VALUES(?,?,?)',
                            (name, address, text)
                        )
                        conn.commit()
                        notice_found = True
                        break
                if not notice_found:
                    print(f"{name}: 민생 키워드 소식 없음, PASS")

            # 다시 검색 리스트 iframe으로 복귀
            switch_to_search_iframe()
            time.sleep(0.8)

            count += 1
        except Exception as e:
            print("에러:", e)
            switch_to_search_iframe()
            time.sleep(0.8)
            continue

    # 다음 페이지 이동 (페이지 버튼이 안 뜨면 종료)
    page += 1
    try:
        next_btn = driver.find_element(
            By.XPATH, f"//a[contains(@class,'mBN2s') and normalize-space(text())='{page}']"
        )
        driver.execute_script("arguments[0].click();", next_btn)
        print(f"[INFO] {page}페이지로 이동")
        time.sleep(2)
        switch_to_search_iframe()
    except:
        print("[INFO] 다음 페이지가 없습니다.")
        break

driver.quit()
conn.close()
print(f"✅ 총 {count}개 저장 완료")
