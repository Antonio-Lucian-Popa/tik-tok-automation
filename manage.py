from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import time
import random
import cv2
from dotenv import load_dotenv
import os

# Încarcă variabilele din fișierul .env
load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

# Specifică calea către chromedriver.exe
driver_path = "./chromedriver-win64/chromedriver.exe"  # Calea relativă

# Creează un obiect Service pentru ChromeDriver
service = Service(driver_path)

# Setările de driver pentru browser
options = webdriver.ChromeOptions()
options.add_argument("--incognito")  # Deschide browserul într-un mod incognito

# Creează instanța WebDriver
driver = webdriver.Chrome(service=service, options=options)

# Restul funcțiilor rămân neschimbate
def capture_element_screenshot(element, filename):
    element.screenshot(filename)

def find_slider_position(puzzle_image, slider_image):
    puzzle = cv2.imread(puzzle_image, 0)
    slider = cv2.imread(slider_image, 0)
    result = cv2.matchTemplate(puzzle, slider, cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(result)
    return max_loc[0]

def move_slider(driver, slider_element, position):
    action = ActionChains(driver)
    action.click_and_hold(slider_element).pause(0.5)
    action.move_by_offset(position, 0).pause(0.5)
    action.release().perform()

def solve_captcha():
    try:
        puzzle_element = driver.find_element(By.CSS_SELECTOR, "div.puzzle-container")
        slider_element = driver.find_element(By.CSS_SELECTOR, "div.slider-container")
        capture_element_screenshot(puzzle_element, "puzzle.png")
        capture_element_screenshot(slider_element, "slider.png")
        position = find_slider_position("puzzle.png", "slider.png")
        move_slider(driver, slider_element, position)
        print("[INFO] CAPTCHA rezolvat cu succes.")
    except Exception as e:
        print(f"[ERROR] Eroare la rezolvarea CAPTCHA: {e}")

def login_to_tiktok(email, password):
    try:
        driver.get("https://www.tiktok.com/login/phone-or-email/email")
        try:
            shadow_root = driver.execute_script(
                "return document.querySelector('tiktok-cookie-banner').shadowRoot"
            )
            decline_button = shadow_root.find_element(By.CSS_SELECTOR, "button")
            if "Decline optional cookies" in decline_button.text:
                decline_button.click()
                print("[INFO] Bannerul cookie-urilor a fost închis.")
        except Exception as e:
            print(f"[INFO] Nu a fost necesar să închizi bannerul cookie-urilor: {e}")

        wait = WebDriverWait(driver, 10)
        username_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Email or username']")))
        username_input.send_keys(email)
        password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Password']")))
        password_input.send_keys(password)
        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-e2e='login-button']")))
        login_button.click()

        time.sleep(3)
        if "Drag the slider" in driver.page_source:
            print("[INFO] CAPTCHA detectat. Rezolvare...")
            solve_captcha()

        print(f"[INFO] Logare reușită pentru {email}")
        time.sleep(5)
    except Exception as e:
        print(f"[ERROR] Eroare la logare: {e}")

def watch_video(video_url):
    try:
        driver.get(video_url)
        print(f"[INFO] Vizionare video: {video_url}")
        time.sleep(random.randint(10, 30))
    except Exception as e:
        print(f"[ERROR] Eroare la vizionare video: {e}")

def interact_with_video():
    try:
        like_button = driver.find_element(By.XPATH, "//span[@data-e2e='like-icon']")
        like_button.click()
        print("[INFO] Video a fost apreciat")
        time.sleep(random.randint(1, 3))
    except Exception as e:
        print(f"[ERROR] Eroare la interacțiune: {e}")

# Exemplu de utilizare
try:
    login_to_tiktok(EMAIL, PASSWORD)
    time.sleep(5)
    watch_video("https://www.tiktok.com/@antonio_lucian13/video/7443079808839519490?_t=8s7fZ8zqeCU&_r=1")
    interact_with_video()
finally:
    driver.quit()
    print("[INFO] Browserul a fost închis")
