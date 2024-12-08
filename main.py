import customtkinter as ctk
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
from cryptography.fernet import Fernet
from threading import Thread
import json
import os

class TicketBookingApp:
    def __init__(self):
        # Set theme and color
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Create main window with larger height
        self.app = ctk.CTk()
        self.app.geometry("500x800")  # 세로 길이 증가
        self.app.title("Ticket Booking System")

        # Create main frame
        self.frame = ctk.CTkFrame(master=self.app)
        self.frame.pack(pady=20, padx=40, fill='both', expand=True)

        # 창을 화면 중앙에 위치시키는 코드
        screen_width = self.app.winfo_screenwidth()
        screen_height = self.app.winfo_screenheight()
        window_width = 500
        window_height = 800
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.app.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Title label
        self.label = ctk.CTkLabel(master=self.frame, text='Ticket Booking System')
        self.label.pack(pady=12, padx=10)

        # UserID 입력 프레임
        id_frame = ctk.CTkFrame(master=self.frame)
        id_frame.pack(fill='x', pady=5, padx=10)
        id_label = ctk.CTkLabel(master=id_frame, text='계정', width=100)
        id_label.pack(side='left', padx=5)
        self.user_entry = ctk.CTkEntry(master=id_frame)
        self.user_entry.pack(side='left', expand=True, fill='x', padx=5)

        # Password 입력 프레임
        pass_frame = ctk.CTkFrame(master=self.frame)
        pass_frame.pack(fill='x', pady=5, padx=10)
        pass_label = ctk.CTkLabel(master=pass_frame, text='비밀번호', width=100)
        pass_label.pack(side='left', padx=5)
        self.pass_entry = ctk.CTkEntry(master=pass_frame, show="*")
        self.pass_entry.pack(side='left', expand=True, fill='x', padx=5)


        # 자격증명 관리를 위한 변수 초기화
        self.key_file = 'credentials.key'
        self.cred_file = 'credentials.enc'
        self.credentials = {}
        self.fernet = self.setup_encryption()
        
        # 자격증명 저장/불러오기 프레임
        self.cred_frame = ctk.CTkFrame(master=self.frame)
        self.cred_frame.pack(pady=12, padx=10)
        
        # 저장 버튼
        self.save_cred_button = ctk.CTkButton(
            master=self.cred_frame, 
            text='현재 계정 저장', 
            command=self.save_credentials
        )
        self.save_cred_button.pack(side='left', padx=5)
        
        # 불러오기 콤보박스
        self.load_combo = ctk.CTkComboBox(
            master=self.cred_frame,
            values=['계정 선택'] + self.load_credential_list(),
            command=self.load_credentials
        )
        self.load_combo.pack(side='left', padx=5)

        # Show title 입력 프레임
        show_frame = ctk.CTkFrame(master=self.frame)
        show_frame.pack(fill='x', pady=5, padx=10)
        show_label = ctk.CTkLabel(master=show_frame, text='공연 검색어', width=100)
        show_label.pack(side='left', padx=5)
        self.show_entry = ctk.CTkEntry(master=show_frame)
        self.show_entry.pack(side='left', expand=True, fill='x', padx=5)

        # 날짜 입력 프레임
        date_frame = ctk.CTkFrame(master=self.frame)
        date_frame.pack(fill='x', pady=5, padx=10)
        date_label = ctk.CTkLabel(master=date_frame, text='날짜', width=100)
        date_label.pack(side='left', padx=5)
        self.date_entry = ctk.CTkEntry(master=date_frame)
        self.date_entry.pack(side='left', expand=True, fill='x', padx=5)

        # 회차 입력 프레임
        time_frame = ctk.CTkFrame(master=self.frame)
        time_frame.pack(fill='x', pady=5, padx=10)
        time_label = ctk.CTkLabel(master=time_frame, text='회차', width=100)
        time_label.pack(side='left', padx=5)
        self.time_entry = ctk.CTkEntry(master=time_frame)
        self.time_entry.pack(side='left', expand=True, fill='x', padx=5)
        
        # 열 범위 입력 프레임
        self.row_frame = ctk.CTkFrame(master=self.frame)
        self.row_frame.pack(fill='x', pady=5, padx=10)
        
        self.row_label = ctk.CTkLabel(master=self.row_frame, text="열 범위", width=100)
        self.row_label.pack(side='left', padx=5)
        
        self.row_start = ctk.CTkEntry(master=self.row_frame, placeholder_text="시작", width=60)
        self.row_start.pack(side='left', padx=5)
        
        self.row_end = ctk.CTkEntry(master=self.row_frame, placeholder_text="끝", width=60)
        self.row_end.pack(side='left', padx=5)
        
        # 좌석 번호 범위 입력 프레임
        self.seat_num_frame = ctk.CTkFrame(master=self.frame)
        self.seat_num_frame.pack(fill='x', pady=5, padx=10)
        
        self.seat_label = ctk.CTkLabel(master=self.seat_num_frame, text="좌석 번호", width=100)
        self.seat_label.pack(side='left', padx=5)
        
        self.seat_start = ctk.CTkEntry(master=self.seat_num_frame, placeholder_text="시작", width=60)
        self.seat_start.pack(side='left', padx=5)
        
        self.seat_end = ctk.CTkEntry(master=self.seat_num_frame, placeholder_text="끝", width=60)
        self.seat_end.pack(side='left', padx=5)
        
        # 층 선택 설명 레이블
        self.floor_desc = ctk.CTkLabel(
            master=self.frame, 
            text="* 1~3지망 층을 선택하세요 (선택안함 가능)", 
            font=("", 12)
        )
        self.floor_desc.pack(pady=(12,0), padx=10)

        # 층 선택 프레임
        self.floor_frame = ctk.CTkFrame(master=self.frame)
        self.floor_frame.pack(pady=(5,12), padx=10)

        # 1지망
        self.floor_1 = ctk.CTkComboBox(
            master=self.floor_frame, 
            values=["선택안함", "1층", "2층", "3층"],
            width=100
        )
        self.floor_1.pack(side='left', padx=5)

        # 2지망
        self.floor_2 = ctk.CTkComboBox(
            master=self.floor_frame,
            values=["선택안함", "1층", "2층", "3층"],
            width=100
        )
        self.floor_2.set("선택안함")
        self.floor_2.pack(side='left', padx=5)

        # 3지망
        self.floor_3 = ctk.CTkComboBox(
            master=self.floor_frame,
            values=["선택안함", "1층", "2층", "3층"],
            width=100
        )
        self.floor_3.set("선택안함")
        self.floor_3.pack(side='left', padx=5)

        # 블록 선택 설명 레이블
        self.block_desc = ctk.CTkLabel(
            master=self.frame, 
            text="* 1~3지망 블록을 선택하세요 (선택안함 가능)", 
            font=("", 12)
        )
        self.block_desc.pack(pady=(12,0), padx=10)

        # 블록 선택 프레임
        self.block_frame = ctk.CTkFrame(master=self.frame)
        self.block_frame.pack(pady=(5,12), padx=10)

        # 블록 1지망
        self.block_1 = ctk.CTkComboBox(
            master=self.block_frame,
            values=["선택안함", "A블록", "B블록", "C블록"],
            width=100
        )
        self.block_1.pack(side='left', padx=5)

        # 블록 2지망
        self.block_2 = ctk.CTkComboBox(
            master=self.block_frame,
            values=["선택안함", "A블록", "B블록", "C블록"],
            width=100
        )
        self.block_2.set("선택안함")
        self.block_2.pack(side='left', padx=5)

        # 블록 3지망
        self.block_3 = ctk.CTkComboBox(
            master=self.block_frame,
            values=["선택안함", "A블록", "B블록", "C블록"],
            width=100
        )
        self.block_3.set("선택안함")
        self.block_3.pack(side='left', padx=5)

        # Start booking button
        self.button = ctk.CTkButton(master=self.frame, text='예매 시작', command=self.start_booking)
        self.button.pack(pady=12, padx=10)


        
        # Status label
        self.status_label = ctk.CTkLabel(master=self.frame, text='')
        self.status_label.pack(pady=12, padx=10)

    def setup_encryption(self):
        if not os.path.exists(self.key_file):
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
        else:
            with open(self.key_file, 'rb') as f:
                key = f.read()
        return Fernet(key)

    def save_credentials(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()
        
        if not username or not password:
            self.status_label.configure(text="아이디와 비밀번호를 입력하세요")
            return
            
        # 기존 자격증명 불러오기
        self.load_encrypted_credentials()
        
        # 새 자격증명 추가
        self.credentials[username] = password
        
        # 암호화하여 저장
        encrypted_data = self.fernet.encrypt(
            json.dumps(self.credentials).encode()
        )
        with open(self.cred_file, 'wb') as f:
            f.write(encrypted_data)
            
        # 콤보박스 업데이트
        self.load_combo.configure(values=self.load_credential_list())
        self.status_label.configure(text="자격증명이 저장되었습니다")

    def load_encrypted_credentials(self):
        if os.path.exists(self.cred_file):
            with open(self.cred_file, 'rb') as f:
                encrypted_data = f.read()
                decrypted_data = self.fernet.decrypt(encrypted_data)
                self.credentials = json.loads(decrypted_data)
        return {}

    def load_credential_list(self):
        try:
            self.load_encrypted_credentials()
            return list(self.credentials.keys())
        except:
            return []

    def load_credentials(self, username):
        if username in self.credentials:
            self.user_entry.delete(0, 'end')
            self.pass_entry.delete(0, 'end')
            self.user_entry.insert(0, username)
            self.pass_entry.insert(0, self.credentials[username])
            self.status_label.configure(text="자격증명을 불러왔습니다")


    def start_booking(self):
        # Get values from entries
        username = self.user_entry.get()
        password = self.pass_entry.get()
        show_title = self.show_entry.get()
        target_date = self.date_entry.get()
        target_time = self.time_entry.get()


        if not all([username, password, show_title, target_date]):
            self.status_label.configure(text="모든 필드를 입력해주세요")
            return

        self.status_label.configure(text="Booking in progress...")
        
        try:
            target_date = int(target_date)
            if not 1 <= target_date <= 31:
                self.status_label.configure(text="날짜는 1-31 사이의 숫자여야 합니다")
                return
            target_time = int(target_time)
            if target_time < 1:
                self.status_label.configure(text="올바른 회차를 입력하세요")
                return
        except ValueError:
            self.status_label.configure(text="올바른 날짜를 입력하세요")
            return


        self.status_label.configure(text="예매를 시작합니다...")
        
        
        try:
            driver = self.start_browser()
            wait = WebDriverWait(driver, 5)
            
            
            current_handles = len(driver.window_handles)

            # 공연 선택
            self.select_show(driver, wait, show_title)
            
            # 닫기 버튼 처리 (에러 무시)
            try:
                button = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[2]/div/div[3]/button')
                button.click()
            except:
                pass
            
            # 로그인 상태 확인 및 처리
            self.check_login_status(driver, wait, username, password)
            print('이까지 완료')


            self.select_date(wait, target_date)
            self.select_time(wait, target_time)
            self.click_booking_button(wait)
            self.seat_selection_process(driver, current_handles)
            
            # # 예매 대기 무한 클릭
            # if self.rapid_booking_attempt(driver, wait, target_date, target_time):
            #     self.seat_selection_process(driver, current_handles)
                        
            self.status_label.configure(text="Booking completed!")
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}")

    def start_browser(self):
        PROFILE = r'C:\\Users\\User'  # Profile path
        PORT = 9222 # Remote debugging port number

        # Chrome이 설치되어 있는 path
        cmd = r'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
        cmd += f' --user-data-dir="{PROFILE}"'	# user-data-dir 지정
        cmd += f' --remote-debugging-port={PORT}'	# remote debugging port 지정

        # 옵션 설정
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option('debuggerAddress', f'127.0.0.1:{PORT}')
        
        # # 이미지와 쿠키 차단 설정 추가
        # prefs = {
        #     "profile.managed_default_content_settings.images": 2
        # }
        # chrome_options.add_experimental_option("prefs", prefs)
        
        # Chrome 실행 및 대기
        process = subprocess.Popen(cmd)


        # 드라이버 실행
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://tickets.interpark.com/")

        return driver

        # 페이지 완전히 로드될 때까지 잠시 대기
        WebDriverWait(driver, 10).until(lambda driver: driver.execute_script("return document.readyState") == "complete")

    def login_process(self, wait, user_id, user_pass):
        print("로그인 프로세스 실행")

        # 로그인 버튼 클릭
        login = "/html/body/header/div[2]/div/div/div[4]/a[1]"
        element = wait.until(EC.element_to_be_clickable((By.XPATH, login)))
        element.click()

        # 아이디 입력
        login_id = "/html/body/div/div/div/div[2]/form/div[1]/div/div[1]/label/input"
        element = wait.until(EC.element_to_be_clickable((By.XPATH, login_id)))
        element.send_keys(user_id)

        # 비밀번호 입력
        login_pass = "/html/body/div/div/div/div[2]/form/div[1]/div/div[2]/label/input"
        element = wait.until(EC.element_to_be_clickable((By.XPATH, login_pass)))
        element.send_keys(user_pass)
        element.send_keys(Keys.ENTER)


    def check_login_status(self, driver, wait, username, password):
        try:
            
            # 닫기 버튼 처리 (에러 무시)
            try:
                button = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[2]/div/div[3]/button')
                button.click()
            except:
                pass
            
            # 로그인/로그아웃 버튼 요소 찾기
            login_element = wait.until(
                EC.presence_of_element_located((By.XPATH, '/html/body/header/div[2]/div[1]/div/div[4]/a[1]'))
            )
            
            # 버튼의 텍스트 확인
            button_text = login_element.text.strip()
            
            if button_text == '로그아웃':
                print("이미 로그인되어 있습니다.")
                return True
            elif button_text == '로그인':
                print("로그인이 필요합니다.")
                self.login_process(wait, username, password)
                return True
            return False
        except Exception as e:
            print(f"로그인 상태 확인 중 오류 발생: {str(e)}")
            return False

    def select_show(self, driver, wait, show_title):
        while True:
            try:
                # 검색
                search_input = "/html/body/div[1]/div/header/div[2]/div[1]/div/div[3]/div/input"
                element = wait.until(EC.element_to_be_clickable((By.XPATH, search_input)))
                element.send_keys(show_title)
                driver.implicitly_wait(2)
                element.send_keys(Keys.ENTER)

                # 여러 공연일 경우의 경로 먼저 시도
                try:
                    first_stuff = "/html/body/div[1]/div/main/div/div/div/div[2]/a[1]/ul/li[1]"
                    element = wait.until(EC.element_to_be_clickable((By.XPATH, first_stuff)))
                    element.click()
                except:
                    # 단일 공연일 경우의 경로 시도
                    first_stuff = "/html/body/div[1]/div/main/div/div/div[2]/div[2]/a/ul/li[1]"
                    element = wait.until(EC.element_to_be_clickable((By.XPATH, first_stuff)))
                    element.click()

                # 새 탭으로 전환
                windows = driver.window_handles
                driver.switch_to.window(windows[-1])
                break
            except Exception as e:
                print("공연 검색/선택 실패:", e)
                time.sleep(0.01)
                continue
    

    def select_date(self, wait, target_date):
        print(f"날짜 선택 시작: {target_date}")
        
        # 날짜 요소들의 기본 XPath
        base_xpath = "/html/body/div[1]/div[2]/div[1]/div[3]/div/div[1]/div[1]/div[2]/div/div/div/div/ul[3]/li"
        while True:
            print("예매 시도 중...")
            # 닫기 버튼 클릭
            try:
                button = wait.until(EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[1]/div[2]/div[2]/div/div[3]/button')))
                if button:
                    button.click()
                    print("닫기 버튼 클릭 완료")
            except:
                pass
            # 1부터 31까지 순회하면서 원하는 날짜 찾기
            for i in range(1, 32):
                try:    
                    # 현재 인덱스의 날짜 요소 찾기
                    date_element = wait.until(EC.presence_of_element_located(
                        (By.XPATH, f"{base_xpath}[{i}]")))
                    
                    # 날짜 텍스트 가져오기
                    date_text = date_element.text.strip()
                    
                    # 목표 날짜와 일치하는지 확인
                    if date_text == str(target_date):
                        print(f"날짜 찾음: {date_text}")
                        date_element.click()
                        return True
                        
                except Exception as e:
                    print(f"날짜 {i} 확인 중 오류: {str(e)}")
                    continue
        print("원하는 날짜를 찾지 못했습니다.")
        return False
        
            

    def select_time(self, wait, target_time):
        print(f"회차 선택 시작: {target_time}회")
        
        # 회차 선택 기본 XPath
        base_xpath = "/html/body/div[1]/div[2]/div[1]/div[3]/div/div[1]/div[2]/div[2]/div[1]/ul/li"
        
        try:

            # 단일 회차인 경우 먼저 시도
            single_time = wait.until(EC.presence_of_element_located(
                (By.XPATH, f"{base_xpath}/a")))
            time_text = single_time.text.strip()
            if f"{target_time}회" in time_text:
                print(f"단일 회차 선택: {time_text}")
                single_time.click()
                return True

            # 여러 회차가 있는 경우
            for i in range(1, 10):  # 적절한 범위 설정
                time_element = wait.until(EC.presence_of_element_located(
                    (By.XPATH, f"{base_xpath}[{i}]/a")))
                time_text = time_element.text.strip()
                print('회차:',target_time,'time_text:',time_text)
                if f"{target_time}회" in time_text:
                    print(f"회차 찾음: {time_text}")
                    time_element.click()
                    return True

        except Exception as e:
            print(f"회차 검색 중 종료: {str(e)}")
        
        print("원하는 회차를 찾지 못했습니다.")
        return False


    def click_booking_button(self, wait):
        while True:
            try:
                booking_button = None
                print("c지점")
                print('booking_button:--',booking_button)
                booking_button = '/html/body/div[1]/div[2]/div[1]/div[3]/div/div[2]/a[1]/span'
                element = wait.until(EC.element_to_be_clickable((By.XPATH, booking_button)))
                element.click()
                break
            except Exception as e:
                print('실패. 다시.', e)
                continue

    # def rapid_booking_attempt(self, driver, wait, target_date, target_time):
    #     """날짜, 회차, 예매 버튼을 빠르게 시도"""
    #     base_date_xpath = "/html/body/div[1]/div[2]/div[1]/div[3]/div/div[1]/div[1]/div[2]/div/div/div/div/ul[3]/li"
    #     base_time_xpath = "/html/body/div[1]/div[2]/div[1]/div[3]/div/div[1]/div[2]/div[2]/div[1]/ul/li"
    #     booking_xpath = '/html/body/div[1]/div[2]/div[1]/div[3]/div/div[2]/a[1]/span'
        
    #     while True:
    #         print("예매 시도 중...")
    #         try:
    #             # 닫기 버튼 처리 (에러 무시)
    #             try:
    #                 button = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[2]/div/div[3]/button')
    #                 button.click()
    #             except:
    #                 pass

    #             # 날짜 선택 시도
    #             date_selected = False
    #             for i in range(1, 32):
    #                 try:
    #                     date_element = driver.find_element(By.XPATH, f"{base_date_xpath}[{i}]")
    #                     if date_element.text.strip() == str(target_date):
    #                         date_element.click()
    #                         date_selected = True
    #                         break
    #                 except:
    #                     time.sleep(0.01)
    #                     continue
                
    #             if not date_selected:
    #                 time.sleep(0.01)
    #                 continue

    #             # 회차 선택 시도
    #             try:
    #                 # 단일 회차 시도
    #                 single_time = driver.find_element(By.XPATH, f"{base_time_xpath}/a")
    #                 if f"{target_time}회" in single_time.text.strip():
    #                     single_time.click()
    #                 else:
    #                     # 다중 회차 시도
    #                     time_selected = False
    #                     for j in range(1, 10):
    #                         try:
    #                             time_element = driver.find_element(By.XPATH, f"{base_time_xpath}[{j}]/a")
    #                             if f"{target_time}회" in time_element.text.strip():
    #                                 time_element.click()
    #                                 time_selected = True
    #                                 break
    #                         except:
    #                             time.sleep(0.01)
    #                             continue
                        
    #                     if not time_selected:
    #                         time.sleep(0.01)
    #                         continue
    #             except:
    #                 time.sleep(0.01)
    #                 continue

    #             # 예매 버튼 클릭 시도
    #             try:
    #                 book_button = driver.find_element(By.XPATH, booking_xpath)
    #                 book_button.click()
    #                 return True
    #             except:
    #                 time.sleep(0.01)
    #                 continue

    #         except Exception as e:
    #             time.sleep(0.01)
    #             continue
            
            

    def seat_selection_process(self, driver, current_handles):
        print("예매 프로세스 실행")
        try:
            while True:
                try:
                    WebDriverWait(driver, 3).until(
                        lambda driver: len(driver.window_handles) > current_handles
                    )
                    new_window = driver.window_handles[-1]
                    driver.switch_to.window(new_window)

                    # 팝업 확인 스레드 시작
                    popup_thread = Thread(target=self.check_and_close_popup, args=(driver,))
                    popup_thread.start()
                    
                    # iframe이 로드될 때까지 대기
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "ifrmSeat"))
                    )
                    
                    # iframe 전환
                    driver.switch_to.frame("ifrmSeat")
                    driver.switch_to.frame("ifrmSeatDetail")
                    
                    if self.find_and_select_seat(driver):
                        print("좌석 선택 완료")
                        break
                        
                except Exception as e:
                    print("예외 발생:", e)
                    continue
                    
        except Exception as e:
            print("예매 프로세스 실패:", e)

    def check_and_close_popup(self, driver):
        """팝업창 확인 및 닫기 - 3초간 시도"""
        start_time = time.time()
        
        while time.time() - start_time < 3:  # 3초 동안 실행
            try:
                popup_close = driver.find_element(By.XPATH, '/html/body/div[5]/div[2]/div[1]/a')
                if popup_close:
                    popup_close.click()
                    print("팝업창 닫기 완료")
                    return
            except:
                time.sleep(0.1)  # 0.1초 대기 후 재시도
                continue
        
        print("팝업창이 없거나 닫기 실패")

    def get_seat_range(self):
        """사용자가 입력한 좌석 범위 가져오기"""
        try:
            row_start = int(self.row_start.get())
            row_end = int(self.row_end.get())
            seat_start = int(self.seat_start.get())
            seat_end = int(self.seat_end.get())
            
            # 범위 유효성 검사
            if not all([row_start, row_end, seat_start, seat_end]):
                self.status_label.configure(text="모든 좌석 범위를 입력하세요")
                return None
                
            if row_start > row_end or seat_start > seat_end:
                self.status_label.configure(text="잘못된 범위입니다")
                return None
                
            return (row_start, row_end, seat_start, seat_end)
            
        except ValueError:
            self.status_label.configure(text="좌석 범위는 숫자여야 합니다")
            return None

    def get_floor_priorities(self):
        """층 우선순위 가져오기"""
        floors = []
        floor1 = self.floor_1.get()
        floor2 = self.floor_2.get()
        floor3 = self.floor_3.get()
        
        if floor1 != "선택안함":
            floors.append(floor1)
        if floor2 != "선택안함":
            floors.append(floor2)
        if floor3 != "선택안함":
            floors.append(floor3)
            
        # 아무것도 선택하지 않았다면 1층 기본값
        if not floors:
            floors = ["1층"]
            
        return floors

    def get_block_priorities(self):
        """블록 우선순위 가져오기"""
        blocks = []
        block1 = self.block_1.get()
        block2 = self.block_2.get()
        block3 = self.block_3.get()
        
        if block1 != "선택안함":
            blocks.append(block1)
        if block2 != "선택안함":
            blocks.append(block2)
        if block3 != "선택안함":
            blocks.append(block3)
            
        return blocks

    def cache_seats(self, driver):
        """좌석 정보 캐싱"""
        seats_cache = {}
        seats = driver.find_elements(By.CSS_SELECTOR, "table tbody tr td img")
        
        for seat in seats:
            try:
                title = seat.get_attribute('title')
                if title:
                    seats_cache[title] = seat
            except:
                continue
        return seats_cache

    def find_and_select_seat(self, driver):
        seat_range = self.get_seat_range()
        if not seat_range:
            return False
            
        row_start, row_end, seat_start, seat_end = seat_range
        floors = self.get_floor_priorities()
        blocks = self.get_block_priorities()
        
        try:
            driver.switch_to.frame("ifrmSeat")
            driver.switch_to.frame("ifrmSeatDetail")
            
            seats_cache = self.cache_seats(driver)
            available_seats = []
            
            for floor in floors:
                floor_seats = []
                
                if blocks:
                    for block in blocks:
                        block_seats = []
                        
                        for title, seat in seats_cache.items():
                            try:
                                # 층과 블록 확인
                                if floor not in title or block not in title:
                                    continue
                                
                                # 열 번호 추출 (수정된 부분)
                                if '열-' not in title:
                                    continue
                                    
                                # 전체 문자열을 '-'로 분리
                                parts = title.split('-')
                                # 열 번호가 포함된 부분 찾기
                                for part in parts:
                                    if '열' in part:
                                        row_part = part.replace('열', '').strip()
                                        if row_part.isdigit():
                                            row_num = int(row_part)
                                            break
                                else:
                                    continue
                                    
                                if not (row_start <= row_num <= row_end):
                                    continue
                                
                                # 좌석 번호 추출
                                seat_num = int(parts[-1].strip())  # 마지막 부분이 좌석 번호
                                
                                if not (seat_start <= seat_num <= seat_end):
                                    continue
                                
                                block_seats.append((row_num, seat_num, seat))
                                print(f"가능한 좌석 발견: {title}")
                                
                            except Exception as e:
                                continue
                        
                        if block_seats:
                            block_seats.sort(key=lambda x: (x[0], x[1]))
                            floor_seats.append(block_seats[0])
                else:
                    # 블록이 없는 경우
                    for title, seat in seats_cache.items():
                        try:
                            # 층 확인
                            if floor not in title:
                                continue
                                
                            # 전체 문자열을 '-'로 분리
                            parts = title.split('-')
                            
                            # 열 번호가 포함된 부분 찾기
                            for part in parts:
                                if '열' in part:
                                    row_part = part.replace('열', '').strip()
                                    if row_part.isdigit():
                                        row_num = int(row_part)
                                        break
                            else:
                                continue
                                
                            if not (row_start <= row_num <= row_end):
                                continue
                                
                            # 좌석 번호 추출
                            seat_num = int(parts[-1].strip())  # 마지막 부분이 좌석 번호
                            
                            if not (seat_start <= seat_num <= seat_end):
                                continue
                                
                            floor_seats.append((row_num, seat_num, seat))
                            print(f"가능한 좌석 발견: {title}")
                            
                        except Exception as e:
                            continue
                        
                if floor_seats:
                    # 층 내에서 가장 앞열, 앞번호 선택
                    floor_seats.sort(key=lambda x: (x[0], x[1]))
                    available_seats.append(floor_seats[0])
                    
        except Exception:
            print('에러처리:',Exception)
                
                
    def run(self):
        self.app.mainloop()

# Create and run the application
if __name__ == "__main__":
    app = TicketBookingApp()
    app.run()