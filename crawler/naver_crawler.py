import time
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

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

# 2. Selenium 크롬드라이버 세팅
options = Options()
# options.add_argument('--headless')  # 눈으로 확인 후 활성화!
driver = webdriver.Chrome(options=options)

# ——— 여기서부터 URL 직접 사용 ———
start_url = "https://map.naver.com/p/search/%EC%9D%8C%EC%8B%9D%EC%A0%90?c=10.61,0,0,0,dh"
driver.get(start_url)
time.sleep(7)  # 지도가 느리게 뜨니 넉넉히
# ————————————————————————

# 3. search iframe 진입
for iframe in driver.find_elements(By.TAG_NAME, "iframe"):
    if "search" in iframe.get_attribute("src"):
        driver.switch_to.frame(iframe)
        print("[INFO] search iframe 전환!")
        break
time.sleep(2)

# 4. 무한 스크롤 → 더 많은 결과 로드
scroll_container = driver.find_element(By.CSS_SELECTOR,
    '#_pcmap_list_scroll_container')
for _ in range(50):  # 50번 스크롤 (약 500개 로드)
    driver.execute_script(
        "arguments[0].scrollTop = arguments[0].scrollHeight",
        scroll_container
    )
    time.sleep(1)

# 5. li_list 갱신
li_list = scroll_container.find_elements(By.CSS_SELECTOR, 'ul > li')

# 6. 본격 크롤링: 최대 500개
count = 0
for li in li_list:
    try:
        # 음식점명
        name_elem = li.find_element(By.CSS_SELECTOR, 'span.TYaxT')
        name = name_elem.text.strip()
        if not name:
            continue
        print(f"{count+1}번째 음식점명:", name)

        # 상세페이지 진입
        parent_a = name_elem.find_element(By.XPATH, './ancestor::a[1]')
        driver.execute_script("arguments[0].click();", parent_a)
        time.sleep(2.5)

        # entry iframe 진입
        driver.switch_to.default_content()
        for iframe in driver.find_elements(By.TAG_NAME, "iframe"):
            if "entry" in iframe.get_attribute("src"):
                driver.switch_to.frame(iframe)
                print("[INFO] entry iframe 전환!")
                break
        time.sleep(1.5)

        # 주소 추출
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

        if news_tab:
            driver.execute_script("arguments[0].click();", news_tab)
            time.sleep(2)

            # 소식글들 중 민생 키워드 포함된 것만 저장
            notice_found = False
            news_items = driver.find_elements(By.CSS_SELECTOR, 'div.pui__dGLDWy')
            for n in news_items:
                text = n.text
                if any(kw in text for kw in [
                    "민생지원금", "민생회복", "민생 쿠폰",
                    "민생소비쿠폰", "민생소비", "소비쿠폰"
                ]):
                    print("★ 저장:", name, address, text[:30], "...")
                    cursor.execute('''
                        INSERT INTO stores (name, address, notice)
                        VALUES (?, ?, ?)
                    ''', (name, address, text))
                    conn.commit()
                    notice_found = True
                    break
            if not notice_found:
                print(f"{name}: 민생 관련 소식 없음, PASS")
        else:
            print(f"{name}: 소식탭 없음, PASS")

        # 검색 리스트로 복귀
        driver.switch_to.default_content()
        for iframe in driver.find_elements(By.TAG_NAME, "iframe"):
            if "search" in iframe.get_attribute("src"):
                driver.switch_to.frame(iframe)
                break
        time.sleep(1)

        count += 1
        if count >= 500:
            break

    except Exception as e:
        print("에러:", e)
        # 복귀 로직
        driver.switch_to.default_content()
        for iframe in driver.find_elements(By.TAG_NAME, "iframe"):
            if "search" in iframe.get_attribute("src"):
                driver.switch_to.frame(iframe)
                break
        continue

# 7. 마무리
driver.quit()
conn.close()
print(f"✅ 민생 안내 있는 음식점 최대 {count}개 저장 완료")
