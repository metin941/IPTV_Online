from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import time

def capture_bnt1php_content(url):
    options = Options()
    options.headless = True  # Run in headless mode
    options.add_argument('--no-sandbox')  # Disable sandboxing for CI environments
    options.add_argument('--disable-dev-shm-usage')  # Prevent errors related to shared memory
    options.add_argument('--disable-gpu')  # Disable GPU acceleration (not needed in CI)
    options.add_argument('--remote-debugging-port=9222')  # Enable remote debugging
    options.add_argument('--window-size=1920,1080')  # Set window size to avoid issues with rendering

    # Start a new session with Selenium
    driver = webdriver.Chrome(options=options)
    
    # Enable network logging for capturing network requests
    driver.get(url)
    
    # Allow time for requests to complete (you can adjust this as needed)
    time.sleep(5)

    # Get network traffic captured by the browser
    network_requests = driver.execute_script("""
    var performance = window.performance || window.webkitPerformance || window.msPerformance || window.mozPerformance;
    if (!performance) {
        return [];
    }
    var entries = performance.getEntriesByType("resource");
    var urls = [];
    for (var i = 0; i < entries.length; i++) {
        urls.push(entries[i].name);
    }
    return urls;
    """)

    # Now look for the request to `bnt1.php`
    bnt1_php_url = None
    for request in network_requests:
        if "https://iptv-bg.com/iptv/bnt1.php" in request:
            bnt1_php_url = request
            break
    
    if bnt1_php_url:
        print(f"Found request for bnt1.php: {bnt1_php_url}")
        
        # Attempt to capture the content of the bnt1.php request
        response_content = driver.execute_script(f"""
        var entries = window.performance.getEntriesByType('resource');
        for (var i = 0; i < entries.length; i++) {{
            if (entries[i].name === '{bnt1_php_url}') {{
                return fetch(entries[i].name)
                    .then(response => response.text())
                    .then(data => data);
            }}
        }}
        return null;
        """)

        if response_content:
            # Extract the integer after "ymkaya.xyz:" till "/"
            match = re.search(r'https://ymkaya\.xyz:(\d+)/tv', response_content)
            if match:
                integer = match.group(1)
                print(f"Extracted integer: {integer}")
                
                # Now update the Markdown file with the extracted integer
                update_md_file('lists/all.md', integer)
            else:
                print("No matching URL found in the response content.")
        else:
            print(f"No response found for the bnt1.php request: {bnt1_php_url}")
    else:
        print("No request found for bnt1.php.")
    
    driver.quit()

def update_md_file(file_path, new_number):
    # Read the content of the file
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Update all relevant lines with the new number
    updated_lines = [
        re.sub(r'https://ymkaya\.xyz:\d+/tv/([^/]+)/playlist.m3u8\?', rf'https://ymkaya.xyz:{new_number}/tv/\1/playlist.m3u8?', line)
        for line in lines
    ]
    
    # Save the updated content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(updated_lines)

# URL of the page you want to monitor
url = "https://iptv-bg.com/bnt-1-online/"
capture_bnt1php_content(url)
