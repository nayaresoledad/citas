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
import requests

class ReservarCitas:

    load_dotenv()
    # Set up the Telegram bot token and chat ID for sending the appointment details
    telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID')

    # Datos para la cita
    name = os.environ.get('NAME')
    email = os.environ.get('EMAIL')

    def __init__(self):

        # URL de la página de citas
        CITA_URL = 'https://cita.consuladoperumadrid.org/qmaticwebbooking/#/'

        # Set up the web driver
        driver = webdriver.Chrome()

        # Navigate to the appointment booking page
        driver.get(CITA_URL)
   

    def buscadorCitas(self):
        # Keep trying to book an appointment after 15:30
        while True:
            # Wait until 15:30 Spanish time to start booking
            while True:
                current_time = time.localtime()
                if current_time.tm_hour == 15 and current_time.tm_min >= 30:
                    break
                time.sleep(1)

            # Refresh the page to ensure we're on the correct page
            self.driver.refresh()

            # Click on the "Pasaporte y Salvoconductos" option
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@name='selectService']")))
            service_field = self.driver.find_element_by_xpath("//input[@name='selectService']")
            service_field.click()
            service_field.send_keys(Keys.DOWN)
            service_field.send_keys(Keys.RETURN)

            # Click on the "Pasaportes" option
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@name='selectService']")))
            service_field = self.driver.find_element_by_xpath("//input[@name='selectService']")
            service_field.click()
            service_field.send_keys(Keys.DOWN)
            service_field.send_keys(Keys.RETURN)

            # Check if an appointment is available
            # Check if there are any available appointments
            available_appointments = self.driver.find_elements(By.CSS_SELECTOR, ".list-group-item .booking-data:not(.disabled)")
            try:
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='qm-available']")))
                dates = self.driver.find_elements_by_xpath("//div[@class='qm-available']")
                dates[0].click()

                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='qm-available-time']")))
                time_slots = self.driver.find_elements_by_xpath("//div[@class='qm-available-time']")
                time_slots[0].click()

                name_field = self.driver.find_element_by_xpath("//input[@name='name']")
                name_field.send_keys(self.name)

                email_field = self.driver.find_element_by_xpath("//input[@name='email']")
                email_field.send_keys(self.email)

                submit_button = self.driver.find_element_by_xpath("//button[@type='submit']")
                submit_button.click()

                # Get the appointment details
                confirmation_number = self.driver.find_element_by_xpath("//div[@class='qm-content-title']//h2")
                appointment_date = dates[0].text
                appointment_time = time_slots[0].text
                appointment_location = available_appointments[0].find_element(By.XPATH, '../following-sibling::div').text

                # Send the appointment details by Telegram
                telegram_data = {
                "chat_id": self.telegram_chat_id,
                "parse_mode": "HTML",
                "text": ("<b>Hay citas!</b>\nHay cita en el Consulado Peruano para el"f"{appointment_date}""en la oficina de "f'{appointment_location}')
                }
                requests.post('https://api.telegram.org/bot'f'{self.telegram_bot_token}/sendmessage', data=telegram_data)
                print('Dates found!')

                #Quit the script
                break

            except Exception as e:
                print(f"Error: {str(e)}")
                # Refresh the page and try again
                self.driver.refresh()
