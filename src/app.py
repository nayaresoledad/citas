import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

load_dotenv()

# Set up the Telegram bot token and chat ID for sending the appointment details
telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID')

# Set up the web driver
driver = webdriver.Chrome()

# Navigate to the appointment booking page
driver.get('https://cita.consuladoperumadrid.org/qmaticwebbooking/#/')

# Keep trying to book an appointment after 15:30
while True:
    # Wait until 15:30 Spanish time to start booking
    while True:
        current_time = time.localtime()
        if current_time.tm_hour == 15 and current_time.tm_min >= 30:
            break
        time.sleep(1)

    # Refresh the page to ensure we're on the correct page
    driver.refresh()

    # Click on the "Pasaporte y Salvoconductos" option
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@name='selectService']")))
    service_field = driver.find_element_by_xpath("//input[@name='selectService']")
    service_field.click()
    service_field.send_keys(Keys.DOWN)
    service_field.send_keys(Keys.RETURN)

    # Click on the "Pasaportes" option
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@name='selectService']")))
    service_field = driver.find_element_by_xpath("//input[@name='selectService']")
    service_field.click()
    service_field.send_keys(Keys.DOWN)
    service_field.send_keys(Keys.RETURN)

    # Check if an appointment is available
    # Check if there are any available appointments
    available_appointments = driver.find_elements(By.CSS_SELECTOR, ".list-group-item .booking-data:not(.disabled)")
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='qm-available']")))
        dates = driver.find_elements_by_xpath("//div[@class='qm-available']")
        dates[0].click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='qm-available-time']")))
        time_slots = driver.find_elements_by_xpath("//div[@class='qm-available-time']")
        time_slots[0].click()

        name_field = driver.find_element_by_xpath("//input[@name='name']")
        name_field.send_keys(os.environ.get('NAME'))

        email_field = driver.find_element_by_xpath("//input[@name='email']")
        email_field.send_keys(os.environ.get('EMAIL'))

        submit_button = driver.find_element_by_xpath("//button[@type='submit']")
        submit_button.click()

        # Get the appointment details
        confirmation_number = driver.find_element_by_xpath("//div[@class='qm-content-title']//h2")
        appointment_date = dates[0].text
        appointment_time = time_slots[0].text
        appointment_location = available_appointments[0].find_element(By.XPATH, '../following-sibling::div').text

        # Send the appointment details by Telegram
        telegram_message = f"Appointment available on {appointment_date} at {appointment_time} in {appointment_location}"
        telegram_url = f"https://api.telegram.org/bot{telegram_bot_token}/"

        #Quit the script
        break

    except Exception as e:
        print(f"Error: {str(e)}")
        # Refresh the page and try again
        driver.refresh()
