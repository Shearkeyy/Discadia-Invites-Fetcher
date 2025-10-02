import requests, re, gc, asyncio
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from random import choice
from Crypto.Cipher import AES
from binascii import unhexlify
from tls_client import Session
from time import sleep
from colorama import Fore, Style, init
from threading import Lock
init(autoreset=True)
__lock__ = Lock()
proxies = [line.rstrip("\n") for line in open("proxies.txt", "r")]

HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "referer": "https://discadia.com/?page=53",
    "sec-ch-ua": "\"Google Chrome\";v=\"137\", \"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
}

def save(filelocation: str, item: str) -> None:
    """Save content"""
    with open(filelocation, "a", encoding="utf-8") as file:
        file.write(item + "\n")

def fetch(i: int, retries=3) -> None:
    """Scrape one Discadia page and extract invite links"""
    session = Session(client_identifier="chrome_112", random_tls_extension_order=True)

    def scrape(link: str):
        """Scrape invite from an individual server page"""
        search = link[len('/server/'):]
        req = session.get(f"https://discadia.com/{search}", headers=HEADERS)
        html_content = req.text
        pattern = r"https?://discordapp\.com/invite/\w+"
        matches = re.findall(pattern, html_content)

        if matches:
            scraped_link = matches[0][len("https://discordapp.com/invite/"):]
            with __lock__:
                print(Fore.CYAN + f"[+] Scraped Invite: {scraped_link}")
                save("output.txt", scraped_link)

    try:
        proxy_choice = choice(proxies)
        session.proxies = {"http": f"http://{proxy_choice}", "https": f"http://{proxy_choice}"}

        x = i + 1
        html_content = session.get(f"https://discadia.com/?page={x}", headers=HEADERS).text

        pattern = re.compile(r'e\("([0-9a-f]{32})"\)')
        hex_values = pattern.findall(html_content)

        if len(hex_values) < 3:
            with __lock__:
                print(Fore.RED + f"[!] Couldn't find key/IV/ciphertext on page {x}")
        else:
            key_hex, iv_hex, ct_hex = hex_values[:3]
            key, iv, ciphertext = unhexlify(key_hex), unhexlify(iv_hex), unhexlify(ct_hex)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(ciphertext)
            cosmic_auth = decrypted.hex()

            cookies = {"_cosmic_auth": cosmic_auth}
            html_content = session.get(f"https://discadia.com/?page={x}", headers=HEADERS, cookies=cookies).text

        soup = BeautifulSoup(html_content, "html.parser")
        hrefs = [a.get("href") for a in soup.find_all("a", href=True)]
        links = [link for link in hrefs if "/server/" in link]

        executor = ThreadPoolExecutor(max_workers=50)
        for link in links:
            executor.submit(scrape, link)

    except Exception as e:
        with __lock__:
            print(Fore.YELLOW + f"[!] RETRYING page {i+1} due to error: {e}")
        if retries == 0:
            return False
        fetch(i, retries-1)

async def loop():
    threads  = int(input("Enter the amount of threads: "))
    print("\n")
    executor = ThreadPoolExecutor(max_workers=threads)
    
    for i in range(2000):
        executor.submit(fetch, i)
    executor.shutdown(wait=True)

if __name__ == "__main__":
    print(Fore.MAGENTA + Style.BRIGHT + "\n=== DISCADIA SERVER SCRAPER ===\n")
    gc.disable()
    asyncio.run(loop())
    gc.collect()
    input(Fore.GREEN + "\n[+] PRESS ENTER TO EXIT...")

