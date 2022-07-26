from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from twilio.rest import Client
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


# Include the months to search for available days
months = ['July', 'August', 'September', 'October', 'November']
availability = []
all_a_tags = []
text_message = ""
failed_message = ""


# Connect Chromedriver to State.gov
try:
    # Start Chrome webdriver
    driver = webdriver.Chrome(service = ChromeService(ChromeDriverManager().install()))

    # State.gov website with Stockholm pre-selected to bypass CAPTCHA
    driver.get("https://evisaforms.state.gov/acs/default.asp?postcode=STK&appcode=1")
    driver.maximize_window()
    driver.implicitly_wait(2)

    # Click buttons and forms
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/table[3]/tbody/tr/td[3]/table/tbody/tr[1]/td/table/tbody/tr[2]/td[2]/p/input"))).click()
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/table[3]/tbody/tr[3]/td[1]/input"))).click()
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/table[5]/tbody/tr/td[1]/input"))).click()
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/input[4]"))).click()
except:
    failed_message = "Failed Chromedriver execution"


# Loop through calendar months collecting "day" <a> tags and "Available()" <a> tags if a date/time is available
for month in months:
    try:
        select_element = driver.find_element(By.ID, "Select1")
        select_object = Select(select_element)
        select_object.select_by_visible_text(month)
        calendar = driver.find_element(By.ID, "Table3")
        elements = driver.find_elements(By.TAG_NAME, "a")
    except:
        failed_message = "Failed to select and/or get elements"

    # If elements holds values, then month has availability, append the month and the days
    if elements:
        availability.append(month)
        print("---------------------------------------------")
        print("These are the days in " + month + " with availability:") 
        # Loop through elements, convert web element to string     
        for a in elements:
            # Use .text to convert web element to string
            a_tag = a.text
            all_a_tags.append(a_tag)
        # Loop through all <a> tags and append only the "day" <a> tags
        for i in range(0, len(all_a_tags), 2):
            print(all_a_tags[i])
            availability.append(all_a_tags[i])
    else:
        print("No available times for this month: " + month)


driver.quit()


# Twilio credentials passed to constructor
account = "[insert account SID here]"
token = "[insert auth token here]"

try:
    client = Client(account, token)
    # Specify Region if in EU - Ireland
    client.region = 'ie1'
    # Sends failed text message 
    if failed_message:
        text_message = failed_message
        print(text_message)
        message = client.messages.create(to="[+your mobile number here]", from_="[+your assigned Twilio number here]", body=text_message)
    # Sends month and days text message
    elif month in availability:
        text_message = "Hello from [your name here]'s bot! \U0001F916\n\nI am programmed to check for available passport days \U0001F4C6\n\nThese are the days I found:\n" + '\n'.join(availability) + "\nThis script runs every hour, bye for now! \U0001F44B"
        message = client.messages.create(to="[+your mobile number here]", from_="[+your assigned Twilio number here]", body=text_message)
    # Sends not available text message
    else:
        text_message = "Hello from [your name here]'s bot! \U0001F916\n\nI am programmed to check for available passport days \U0001F4C6\n\nUnfortunately, there are no available days for the selected months. \n\nThis script runs every hour, bye for now! \U0001F44B"
        message = client.messages.create(to="[+your mobile number here]", from_="[+your assigned Twilio number here]", body=text_message)
except:
    print("Failed connecting to Twilio API")

