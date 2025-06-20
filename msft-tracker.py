import requests
import datetime
import os
import time
import sys


class RealTimeMicrosoftIpLogger:
    """Class representing a RealTime Microsoft IP Logger"""

    def __init__(self, b_url, file_path, evilginx_blk):
        self.b_url = b_url
        self.file_path = file_path
        self.evilginx_blk = evilginx_blk

    def get_latest_url(self):
        """Finds the latest available URL for downloading"""
        today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d")  # Format: YYYYMMDD
        for version in range(60, 0, -1):  # Check for timestamp variations
            url = self.b_url.format(date=today, version=version)
            # print(f"\n{url}\n")
            try:
                # print(f"Trying: {url}")
                response = requests.get(url, timeout=5, headers={"Connection": "close"})
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
            response = requests.get(r_url, timeout=5)
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
            resp = requests.get(latest_url, timeout=5)
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
            else:
                print("No valid update found, skipping this cycle.")

            # time.sleep(23 * 60 * 60)  # Sleep for 23 hours
        except Exception as er:
            print(f"Error encountered: {er}")
            time.sleep(60 * 60)  # Sleep for 1 hour before retrying
        except KeyboardInterrupt:
            print("CTRL+C detected, quitting...")
            sys.exit()
