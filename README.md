# Discadia-Invites-Fetcher

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)

Fetch all discord invites in the top **2000 pages** from [Discadia](https://discadia.com) in just a couple of minutes!  
Optimized with **multi-threading**, **proxy support**, and **AES decryption bypass** for Discadia’s `_cosmic_auth` cookie.

---

## Features
- Scrapes up to **2000 Discadia pages**
- **Threaded execution** for blazing-fast results
- **Proxy support** to bypass bans and rate limits
- Automatically decrypts and applies `_cosmic_auth` cookie

---

## Requirements
Make sure you have **Python 3.9+** installed. Then install dependencies:

```bash
pip install requests beautifulsoup4 pycryptodome tls-client colorama
