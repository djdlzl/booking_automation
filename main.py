import subprocess
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert



def start_browser():
    PROFILE = r'C:\\Users\\User'  # Profile path
    PORT = 9222 # Remote debugging port number

    # Chrome이 설치되어 있는 path
    cmd = r'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
    cmd += f' --user-data-dir="{PROFILE}"'	# user-data-dir 지정
    cmd += f' --remote-debugging-port={PORT}'	# remote debugging port 지정
    # 옵션 설정
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('debuggerAddress', f'127.0.0.1:{PORT}')
    # Chrome 실행 및 대기
    process = subprocess.Popen(cmd)


    # 드라이버 실행
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://tickets.interpark.com/")

    return driver

    # 페이지 완전히 로드될 때까지 잠시 대기
    WebDriverWait(driver, 10).until(lambda driver: driver.execute_script("return document.readyState") == "complete")

def login_process(wait):
    print("로그인 프로세스 실행")

    # 로그인 버튼 클릭
    login = "/html/body/header/div[2]/div/div/div[4]/a[1]"
    element = wait.until(EC.element_to_be_clickable((By.XPATH, login)))
    element.click()

    # 아이디 입력
    login_id = "/html/body/div/div/div/div[2]/form/div[1]/div/div[1]/label/input"
    element = wait.until(EC.element_to_be_clickable((By.XPATH, login_id)))
    element.send_keys('your_id')

    # 비밀번호 입력
    login_pass = "/html/body/div/div/div/div[2]/form/div[1]/div/div[2]/label/input"
    element = wait.until(EC.element_to_be_clickable((By.XPATH, login_pass)))
    element.send_keys('your_password')
    element.send_keys(Keys.ENTER)
    
    # 로그인 후 예매 버튼 다시 클릭
    booking_button = '/html/body/div[1]/div[2]/div[1]/div[3]/div/div[2]/a[1]'
    element = wait.until(EC.element_to_be_clickable((By.XPATH, booking_button)))
    element.click()

def select_show(driver, wait):
    # 검색
    search_input = "/html/body/div[1]/div/header/div[2]/div[1]/div/div[3]/div/input"
    element = wait.until(EC.element_to_be_clickable((By.XPATH, search_input)))
    element.send_keys('웃는 남자')
    driver.implicitly_wait(2)
    element.send_keys(Keys.ENTER)

    # 첫번째 공연 클릭
    first_stuff = "/html/body/div[1]/div/main/div/div/div[1]/div[2]/a/div"
    element = wait.until(EC.element_to_be_clickable((By.XPATH, first_stuff)))
    element.click()

    # 새 탭으로 전환
    windows = driver.window_handles
    driver.switch_to.window(windows[-1])  # 가장 최근에 열린 탭으로 전환
   
def select_time_and_booking(wait):
    day = '/html/body/div[1]/div[2]/div[1]/div[3]/div/div[1]/div[1]/div[2]/div/div/div/div/ul[3]/li[12]'
    element = wait.until(EC.element_to_be_clickable((By.XPATH, day)))
    element.click()

    time_button = '/html/body/div[1]/div[2]/div[1]/div[3]/div/div[1]/div[2]/div[2]/div[1]/ul/li/a'
    element = wait.until(EC.element_to_be_clickable((By.XPATH, time_button)))
    element.click()
    time.sleep(0.2)
    
    booking_button = '/html/body/div[1]/div[2]/div[1]/div[3]/div/div[2]/a[1]'
    element = wait.until(EC.element_to_be_clickable((By.XPATH, booking_button)))
    element.click()


def booking_process(driver, wait):
    print("예매 프로세스 실행")
    # wait_for_page_load(wait, '/html/body/table/tbody/tr/td/img[66]')
    try:
        driver.switch_to.frame("ifrmSeat")
        driver.switch_to.frame("ifrmSeatDetail")
        time.sleep(3)
        while True:
            try:
                driver.execute_script("document.querySelector('[title=\"[S석] 1층-C블록 23열-6\"]').click();")
                driver.switch_to.parent_frame()
                driver.execute_script("document.evaluate('//form[1]//div[3]//div[4]//img', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click();")
                driver.switch_to.frame("ifrmBookStep")
                driver.execute_script("document.evaluate('/html/body/div/div[1]/div/table[1]/tbody/tr/td/table/tbody/tr/td[3]/select/option[2]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click();")
                break
            except:
                print("except 실행")
                driver.execute_script("window.alert = function() {};")
                continue

        
        
    except:
        print("실패")

def execute_booking_in_all_frames(driver, wait):
    """
    모든 iframe에서 booking_process를 실행하는 함수
    """
    # 메인 프레임에서 실행
    try:
        print("메인 프레임에서 시도")
        booking_process(driver, wait)
    except Exception as e:
        print(f"메인 프레임 실행 중 오류: {e}")

    # 모든 iframe 찾기
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    print(f"총 {len(iframes)}개의 iframe을 발견했습니다.")

    # 각 iframe에서 실행
    for i in range(len(iframes)):
        try:
            # iframe으로 전환
            driver.switch_to.frame(i)
            print(f"iframe {i}로 전환")
            
            # booking_process 실행
            booking_process(driver, wait)
            
        except Exception as e:
            print(f"iframe {i}에서 오류 발생: {e}")
        
        finally:
            # 항상 기본 컨텍스트로 돌아가기
            driver.switch_to.default_content()

def wait_for_page_load(wait, element):
    try:
        # DOM이 완전히 로드될 때까지 대기
        wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        
        # 특정 요소가 보일 때까지 추가로 대기
        key_element = wait.until(EC.presence_of_element_located((By.XPATH, element)))
        
        return True
    except Exception as e:
        print("페이지 로딩 시간 초과")
        return False


# 메인 로직
def main_booking():
    
    driver = start_browser()
    # wait until someid is clickable
    wait = WebDriverWait(driver, 15)
    
    # 공연 고르기
    select_show(driver, wait)    


    try:
        
        # 창 개수 저장
        current_handles = len(driver.window_handles)

        # 회차 고르기
        select_time_and_booking(wait)

        # 새 창이 열릴 때까지 3초 대기
        WebDriverWait(driver, 3).until(
            lambda driver: len(driver.window_handles) > current_handles
        )
        # 새 창이 열린 경우 (로그인 되어있는 상태)
        print("로그인 되어있음 - 예매 진행")
        
        time.sleep(5)
        new_window = driver.window_handles[-1]
        driver.switch_to.window(new_window)
    except Exception as e:
        # 새 창이 열리지 않은 경우 (로그인 필요)
        print("로그인 필요")
        login_process(wait)

        # 회차 고르기
        select_time_and_booking(wait)
         
        # 로그인 후 새 창 감지
        WebDriverWait(driver, 3).until(
            lambda driver: len(driver.window_handles) > current_handles
        )
        time.sleep(5)
        new_window = driver.window_handles[-1]
        driver.switch_to.window(new_window)
    try:
        booking_process(driver, wait)
        # execute_booking_in_all_frames(driver, wait)
    except Exception as e:
        print("예매 창이 열리지 않았습니다.")

# 실행
main_booking()