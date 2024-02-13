from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

name_form = str(config['DEFAULT']['name'])
email_form = str(config['DEFAULT']['email'])
phone_form = str(config['DEFAULT']['phone'])
message = str(config['DEFAULT']['message'])

driver = webdriver.Firefox()

url = 'https://www.sreality.cz/hledani/prode/byty'
driver.get(url)

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'dir-property-list')))

index = 0
listing_number = 1
while True:
	# Re-fetch the listings on each iteration to avoid stale references
	WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'property')))
	time.sleep(1)
	listings = driver.find_elements(By.CLASS_NAME, 'property')
	if index < len(listings):
		try:
			name = listings[index].find_element(By.CLASS_NAME, 'name')
			locality = listings[index].find_element(By.CLASS_NAME, 'locality')
			title = listings[index].find_element(By.CLASS_NAME, 'title')
			page = driver.find_element(By.CSS_SELECTOR, 'a.btn-paging.active')
			logging.info(f"Clicking on {name.text}, {locality.text}, number of listing: {listing_number}, link: {title.get_attribute('href')}, page: {page.text}")

			# Clicking on advert to fill form
			title.click()
			WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'norm-price')))
			price = driver.find_element(By.CLASS_NAME, 'norm-price')
			if "Kč" in price.text:
				clean_price = int(price.text.strip("Kč").replace(" ", ""))
				new_price = int((clean_price - ((clean_price / 100) * 50)))
				formatted_message = message.replace("$1", "{:} Kč".format(new_price))
			else:
				formatted_message = unformatted_message
			# Form filling
			email_input = driver.find_element(By.NAME, 'email')
			email_input.send_keys(email_form)

			name_input = driver.find_element(By.NAME, 'name')
			name_input.send_keys(name_form)

			phone_input = driver.find_element(By.NAME, 'phone')
			phone_input.send_keys(phone_form)

			message_input = driver.find_element(By.NAME, 'message')
			message_input.clear()
			message_input.send_keys(formatted_message)

			#submit = driver.find_element(By.CLASS_NAME, 'btn-full')
			#submit.click()
			time.sleep(2)
		finally:
			index += 1
			listing_number += 1
			driver.back()
	else:
		# Check for next page and navigate if possible
		next_page = driver.find_element(By.CLASS_NAME, 'paging-next')
		if next_page and "disabled" not in next_page.get_attribute('class'):
			index = 0
			next_page.click()
		else:
			break  # Exit loop if there's no next page or it's disabled

driver.quit()