from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import re

def capture_m3u8_token(url):
    options = Options()
    options.headless = True  # Run in headless mode
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}

    # Start a new session with Selenium
    driver = webdriver.Chrome(options=options, desired_capabilities=caps)
    
    # Load the URL
    driver.get(url)
    
    # Allow time for requests to complete (you can adjust this as needed)
    time.sleep(5)

    # Get the network logs
    logs = driver.get_log('performance')
    
    # Look for the request to the M3U8 playlist
    for log in logs:
        log_msg = log['message']
        if "https://cdn.stgledai.org:8082/hls/planetahd/index.m3u8" in log_msg:
            response_content = log_msg
            break
    else:
        response_content = None

    driver.quit()

    if response_content:
        # Extract the token from the M3U8 playlist
        match = re.search(r'nimblesessionid=([^&]+)', response_content)
        if match:
            token = match.group(1)
            return token
        else:
            print("No token found in the M3U8 playlist.")
            return None
    else:
        print("No request found for the M3U8 playlist.")
        return None

# URL of the page containing the M3U8 playlist
url = "https://cdn.stgledai.org:8082/hls/planetahd/index.m3u8"
token = capture_m3u8_token(url)

if token:
    print(f"Extracted token: {token}")
else:
    print("No token found.")
