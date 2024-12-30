from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import time

# Map channel names to URLs
channel_data = {
    "Kino Nova": "https://iptv-bg.com/kino-nova-online/",
    "Diema Family": "https://iptv-bg.com/diema-family-online/",
    "Diema": "https://iptv-bg.com/diema-online/",
    "National Geographic": "https://iptv-bg.com/nat-geo-online/",
    "NatGeo Wild": "https://iptv-bg.com/nat-geo-wild-online/",
    "Discovery Tv": "https://iptv-bg.com/discovery-channel-online/",
}

def capture_channel_php_content(channel_name, url, max_attempts=5):
    options = Options()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--no-sandbox')  # Disable sandboxing for CI environments
    options.add_argument('--disable-dev-shm-usage')  # Prevent errors related to shared memory
    options.add_argument('--disable-gpu')  # Disable GPU acceleration (not needed in CI)
    options.add_argument('--remote-debugging-port=9222')  # Enable remote debugging
    options.add_argument('--window-size=1920,1080')  # Set window size to avoid issues with rendering
    options.add_argument('--disable-software-rasterizer')  # Disable software rasterizer
    options.add_argument('--disable-extensions')  # Disable extensions

    # Start a new session with Selenium
    driver = webdriver.Chrome(options=options)

    try:
        # Open the URL
        driver.get(url)
        time.sleep(5)  # Initial page load wait

        php_url = None
        attempts = 0

        # Refresh the page until the PHP URL is found or max_attempts is reached
        while attempts < max_attempts:
            print(f"Attempt {attempts + 1} for {channel_name}...")

            # Capture network requests using JavaScript
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

            # Look for the PHP URL in network requests
            for request in network_requests:
                if "iptv-bg.com/iptv" in request and request.endswith(".php"):
                    php_url = request
                    print(f"Found PHP URL for {channel_name}: {php_url}")
                    break

            if php_url:
                break  # Exit the loop if PHP URL is found

            # Refresh the page and wait before retrying
            driver.refresh()
            time.sleep(5)  # Wait for the refreshed page to load
            attempts += 1

        if not php_url:
            print(f"Failed to find PHP URL for {channel_name} after {max_attempts} attempts.")
            return  # Exit if the PHP URL was not found

        # Fetch content of the PHP request using a browser script
        response_content = driver.execute_script(f"""
        return fetch('{php_url}')
            .then(response => response.text())
            .then(data => data)
            .catch(error => null);
        """)

        if response_content:
            # Search for the string 'file:' and extract the URL that follows it
            match = re.search(r'file:"(https://[^"]+)"', response_content)
            if match:
                m3u8_url = match.group(1)
                print(f"Found m3u8 URL for {channel_name}: {m3u8_url}")

                # Write the m3u8 URL and channel name to all.md file (updating if necessary)
                append_md_file('lists/all.md', channel_name, m3u8_url)
            else:
                print(f"No m3u8 URL found for {channel_name} in PHP content.")
        else:
            print(f"No response content found for {channel_name} at {php_url}.")

    except Exception as e:
        print(f"An error occurred while processing {url} for {channel_name}: {e}")
    finally:
        driver.quit()

def append_md_file(file_path, channel_name, new_url):
    try:
        # Read the current content of the file
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Flag to track if the channel is found and replaced
        channel_found = False

        # Loop through all lines and replace the existing channel entry if found
        for i, line in enumerate(lines):
            if line.startswith(f"| 1 | {channel_name} |"):
                # Replace the existing m3u8 URL for the channel
                lines[i] = f"| 1 | {channel_name} | [>]({new_url}) |\n"
                channel_found = True
                break

        if not channel_found:
            # If the channel was not found, append it with '1' as the number
            lines.append(f"| 1 | {channel_name} | [>]({new_url}) |\n")

        # Overwrite the file with the updated content (keeping the header intact)
        with open(file_path, 'w', encoding='utf-8') as file:
            # Write back the updated content
            file.writelines(lines)

        print(f"Updated the m3u8 URL for {channel_name} in the file {file_path}: {new_url}")
    except Exception as e:
        print(f"Failed to update the file {file_path} for {channel_name}: {e}")



def capture_all_channels(channel_data):
    for channel_name, url in channel_data.items():
        print(f"Processing {channel_name}: {url}")
        capture_channel_php_content(channel_name, url)

# Start processing all channels
capture_all_channels(channel_data)
