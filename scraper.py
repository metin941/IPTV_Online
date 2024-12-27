import requests
import urllib3

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://cdn.stgledai.org:8082/hls/planetafolk/index.m3u8"

try:
    response = requests.get(url, verify=False)  # Disable SSL verification (not recommended for production)
    response.raise_for_status()
    m3u8_data = response.text
    print(m3u8_data)
except requests.exceptions.RequestException as e:
    print(f"Error fetching M3U8 playlist: {e}")
