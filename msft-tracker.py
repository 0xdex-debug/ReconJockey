import requests
import datetime
import os
import time
import sys
import random

def randomAgent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.864.41 Safari/537.36 Edg/91.0.864.41",
        "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36",
        "Mozilla/5.0 (Android 10; Pixel 3) Gecko/90.0 Firefox/90.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4516.20 Safari/537.36 OPR/77.0.4054.90",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; Trident/7.0; AS; rv:11.0) like Gecko",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    ]
    ua = random.choice(user_agents)
    return ua

HEADERS = {
    "User-Agent": randomAgent(),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "close",
    "X-Forwarded-For": "127.0.0.1",
    "X-Real-IP": "127.0.0.1",
    "X-Originating-IP": "127.0.0.1",
    "X-Custom-Test": "RedTeamCheck"
}

class RealTimeMicrosoftIpLogger:
    """Class representing a RealTime Microsoft IP Logger"""

    def __init__(self, b_url, file_path, evilginx_blk):
        self.b_url = b_url
        self.file_path = file_path
        self.evilginx_blk = evilginx_blk

    def get_latest_url(self):
        """Finds the latest available URL for downloading"""
        today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d")
        for version in range(60, 0, -1):  # Check for timestamp variations
            url = self.b_url.format(date=today, version=version)
            # print(f"\n{url}\n")
            try:
                # print(f"Trying: {url}")
                response = requests.get(url, timeout=15, headers=HEADERS)
                if response.status_code == 200:
                    return url
            except requests.RequestException as e:
                print(f"error: {e}")
                time.sleep(5)
                continue
        return None

    def download_file(self):
        """Downloads the latest file and saves it locally"""
        r_url = self.get_latest_url()
        if not r_url:
            print("No valid URL found.")
            return

        try:
            response = requests.get(r_url, timeout=15, headers=HEADERS)
            if response.status_code == 200:
                with open(self.file_path, "wb") as df:
                    df.write(response.content)
                print(f"File downloaded successfully: {self.file_path}")
            else:
                print(f"Failed to download file. Status Code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error downloading file: {e}")

    def evilginx_mod(self):
        """Updates the Evilginx blacklist with new IPs"""
        try:
            with open(self.evilginx_blk, "r+") as ev_b, open(self.file_path, "r") as new_ip:
                existing_ips = set(ev_b.read().splitlines())
                new_ips = set(new_ip.read().splitlines())

                missing_ips = new_ips - existing_ips
                if missing_ips:
                    ev_b.write("\n".join(missing_ips) + "\n")
                    print(f"Added {len(missing_ips)} new IPs to blacklist.")
                else:
                    print("No new IPs to add to blacklist.")
        except FileNotFoundError:
            print("Blacklist file not found.")
        except Exception as e:
            print(f"Error updating blacklist: {e}")

    def update_local_file(self):
        """Updates the local file if new content is available"""
        latest_url = self.get_latest_url()
        if not latest_url:
            print("No updated file found today.")
            return

        try:
            resp = requests.get(latest_url, timeout=15, headers=HEADERS)
            if resp.status_code != 200:
                print(f"Error fetching latest file: Status Code {resp.status_code}")
                return

            new_data = resp.content
            if os.path.exists(self.file_path):
                with open(self.file_path, "rb") as lf:
                    existing_data = lf.read()
            else:
                existing_data = None

            if existing_data == new_data:
                print("No changes detected, skipping update.")
            else:
                with open(self.file_path, "wb") as file:
                    file.write(new_data)
                print("Updated local file with the latest data.")

        except requests.RequestException as e:
            print(f"Error updating local file: {e}")
    
    def clean_up(self):
        os.remove(self.file_path)
        return None


if __name__ == "__main__":
    BASE_URL = "https://github.com/aalex954/MSFT-IP-Tracker/releases/download/{date}{version}/msft_asn_ip_ranges.txt"
    LOCAL_FILE = "/root/msft_asn_ip_ranges_latest.txt"
    BLACKLIST_FILE = "/root/.evilginx/blacklist.txt"

    real_time = RealTimeMicrosoftIpLogger(BASE_URL, LOCAL_FILE, BLACKLIST_FILE)

    print("[+] Starting Operation.")

    while True:
        try:
            latest_url = real_time.get_latest_url()
            # print(f"\n{latest_url}\n")
            if latest_url:
                real_time.download_file()
                real_time.evilginx_mod()
                real_time.update_local_file()
                real_time.clean_up()
            else:
                print("No valid update found, skipping this cycle.")
                time.sleep(60 * 60)

            # time.sleep(23 * 60 * 60)  # Sleep for 23 hours
        except Exception as er:
            print(f"Error encountered: {er}")
            time.sleep(60 * 60)  # Sleep for 1 hour before retrying
        except KeyboardInterrupt:
            print("CTRL+C detected, quitting...")
            sys.exit()
