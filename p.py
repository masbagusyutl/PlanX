import requests
import json
import time
import random
import os
import sys
from datetime import datetime, timedelta
import threading
import colorama
from colorama import Fore, Back, Style
import urllib3

# Disable SSL warning for verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initialize colorama
colorama.init(autoreset=True)

# Common headers function to avoid rewriting
def get_common_headers(token=None):
    headers = {
        'authority': 'mpc-api.planx.io',
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8',
        'cache-control': 'no-cache',
        'origin': 'https://tg-wallet.planx.io',
        'pragma': 'no-cache',
        'referer': 'https://tg-wallet.planx.io/',
        'sec-ch-ua': '"Microsoft Edge WebView2";v="135", "Chromium";v="135", "Not-A.Brand";v="8", "Microsoft Edge";v="135"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
    }
    
    if token:
        headers['token'] = f'Bearer {token}'
        headers['Authorization'] = f'Bearer {token}'
    
    return headers

# Print welcome message
def print_welcome_message():
    print(Fore.WHITE + r"""
_  _ _   _ ____ ____ _    ____ _ ____ ___  ____ ____ ___ 
|\ |  \_/  |__| |__/ |    |__| | |__/ |  \ |__/ |  | |__]
| \|   |   |  | |  \ |    |  | | |  \ |__/ |  \ |__| |         
          """)
    print(Fore.GREEN + Style.BRIGHT + "Nyari Airdrop PlanX Wallet")
    print(Fore.YELLOW + Style.BRIGHT + "Telegram: https://t.me/nyariairdrop")

# Load accounts from data.txt
def load_accounts():
    try:
        with open('data.txt', 'r') as file:
            accounts = [line.strip() for line in file if line.strip()]
        print(Fore.BLUE + f"Berhasil memuat {len(accounts)} akun dari data.txt.")
        return accounts
    except FileNotFoundError:
        print(Fore.RED + "File data.txt tidak ditemukan. Silakan buat file tersebut terlebih dahulu.")
        sys.exit(1)
    except Exception as e:
        print(Fore.RED + f"Error saat memuat akun: {str(e)}")
        sys.exit(1)

# Load proxies from proxy.txt
def load_proxies(filename='proxy.txt'):
    """Load proxies from a file"""
    try:
        with open(filename, 'r') as file:
            proxies = []
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split(":")
                    if len(parts) == 4:
                        ip, port, user, password = parts
                        proxy_url = f"http://{user}:{password}@{ip}:{port}"
                    elif len(parts) == 2:
                        ip, port = parts
                        proxy_url = f"http://{ip}:{port}"
                    else:
                        continue
                    proxies.append(proxy_url)
        
        if proxies:
            print(Fore.BLUE + f"Berhasil memuat {len(proxies)} proxy.")
        return proxies
    except FileNotFoundError:
        print(Fore.YELLOW + f"File {filename} tidak ditemukan. Melanjutkan tanpa proxy.")
        return []

# Get a random proxy
def get_proxy(proxies):
    """Retrieve a random proxy"""
    if not proxies:
        return None
    proxy_url = random.choice(proxies)
    return {"http": proxy_url, "https": proxy_url}

# Login to account
def login_account(init_data, proxies=None):
    try:
        proxy = get_proxy(proxies)
        headers = get_common_headers()
        payload = {"initData": init_data, "inviteCode": ""}
        
        response = requests.post(
            "https://mpc-api.planx.io/api/v1/telegram/auth", 
            headers=headers, 
            json=payload,
            proxies=proxy,
            timeout=30,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                token = data.get("data", {}).get("token")
                print(Fore.GREEN + f"✅ Login berhasil")
                return token
            else:
                print(Fore.RED + f"❌ Login gagal: {data.get('msg')}")
                return None
        else:
            print(Fore.RED + f"❌ Login gagal dengan status code: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.RED + f"❌ Error saat login: {str(e)}")
        return None

# Get account info
def get_account_info(token, proxies=None):
    try:
        proxy = get_proxy(proxies)
        headers = get_common_headers(token)
        
        response = requests.get(
            "https://mpc-api.planx.io/api/v1/telegram/info", 
            headers=headers,
            proxies=proxy,
            timeout=30,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                info = data.get("data", {})
                nickname = info.get("nickName", "Unknown")
                invite_code = info.get("inviteCode", "Unknown")
                print(Fore.CYAN + f"📊 Info Akun: {nickname} | Kode Undangan: {invite_code}")
                return info
            else:
                print(Fore.RED + f"❌ Gagal mendapatkan info akun: {data.get('msg')}")
                return None
        else:
            print(Fore.RED + f"❌ Gagal mendapatkan info akun dengan status code: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.RED + f"❌ Error saat mendapatkan info akun: {str(e)}")
        return None

# Check asset task
def check_asset_task(token, proxies=None):
    try:
        proxy = get_proxy(proxies)
        headers = get_common_headers(token)
        
        response = requests.get(
            "https://mpc-api.planx.io/api/v1/telegram/task/asset", 
            headers=headers,
            proxies=proxy,
            timeout=30,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                task_data = data.get("data", {})
                task_id = task_data.get("taskId")
                task_status = task_data.get("taskStatus")
                symbol = task_data.get("symbol")
                amount = task_data.get("amount")
                
                status_text = "Belum diklaim" if task_status == 1 else "Farming aktif" if task_status == 2 else f"Status: {task_status}"
                print(Fore.YELLOW + f"💰 Asset: {symbol} | Jumlah: {amount} | Status: {status_text}")
                
                return task_data
            else:
                print(Fore.RED + f"❌ Gagal mendapatkan info asset: {data.get('msg')}")
                return None
        else:
            print(Fore.RED + f"❌ Gagal mendapatkan info asset dengan status code: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.RED + f"❌ Error saat mendapatkan info asset: {str(e)}")
        return None

# Claim asset task
def claim_asset_task(token, task_id, proxies=None):
    try:
        proxy = get_proxy(proxies)
        headers = get_common_headers(token)
        headers['content-type'] = 'application/json'
        
        payload = {"taskId": task_id}
        
        response = requests.post(
            "https://mpc-api.planx.io/api/v1/telegram/task/claim", 
            headers=headers,
            json=payload,
            proxies=proxy,
            timeout=30,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(Fore.GREEN + f"✅ Berhasil claim asset")
                return True
            else:
                print(Fore.RED + f"❌ Gagal claim asset task: {data.get('msg')}")
                return False
        else:
            print(Fore.RED + f"❌ Gagal claim asset task dengan status code: {response.status_code}")
            return False
    except Exception as e:
        print(Fore.RED + f"❌ Error saat claim asset task: {str(e)}")
        return False

# Check lottery task
def check_lottery_task(token, proxies=None):
    try:
        proxy = get_proxy(proxies)
        headers = get_common_headers(token)
        
        response = requests.get(
            "https://mpc-api.planx.io/api/v1/telegram/task/lottery", 
            headers=headers,
            proxies=proxy,
            timeout=30,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                lottery_data = data.get("data", {})
                task_id = lottery_data.get("taskId")
                task_status = lottery_data.get("taskStatus")
                current_balance = lottery_data.get("currentBalance")
                
                print(Fore.MAGENTA + f"🎮 Lottery Task | Status: {task_status} | Balance: {current_balance}")
                
                return lottery_data
            else:
                print(Fore.RED + f"❌ Gagal mendapatkan info lottery: {data.get('msg')}")
                return None
        else:
            print(Fore.RED + f"❌ Gagal mendapatkan info lottery dengan status code: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.RED + f"❌ Error saat mendapatkan info lottery: {str(e)}")
        return None

# Claim lottery task
def claim_lottery_task(token, task_id, proxies=None):
    try:
        proxy = get_proxy(proxies)
        headers = get_common_headers(token)
        headers['content-type'] = 'application/json'
        
        payload = {"taskId": task_id}
        
        response = requests.post(
            "https://mpc-api.planx.io/api/v1/telegram/task/claim", 
            headers=headers,
            json=payload,
            proxies=proxy,
            timeout=30,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(Fore.GREEN + f"✅ Berhasil claim lottery")
                return True
            else:
                print(Fore.RED + f"❌ Gagal claim lottery task: {data.get('msg')}")
                return False
        else:
            print(Fore.RED + f"❌ Gagal claim lottery task dengan status code: {response.status_code}")
            return False
    except Exception as e:
        print(Fore.RED + f"❌ Error saat claim lottery task: {str(e)}")
        return False

# Get task list
def get_task_list(token, proxies=None):
    """Retrieve available tasks"""
    try:
        proxy = get_proxy(proxies)
        headers = get_common_headers(token)
        
        response = requests.get(
            "https://mpc-api.planx.io/api/v1/telegram/task/popular/list?", 
            headers=headers, 
            proxies=proxy,
            verify=False,
            timeout=30
        )
        
        if response.status_code == 200:
            tasks = response.json().get('data', [])
            print(Fore.GREEN + "✅ Berhasil mengambil daftar tugas.")
            
            # Filter and display tasks
            print(Fore.CYAN + "\n📋 Daftar Tugas Tersedia:")
            for task in tasks:
                # Check task status
                if task['taskStatus'] == 1:
                    status = "Belum Diambil"
                    status_color = Fore.BLUE
                elif task['taskStatus'] == 2:
                    status = "Siap Diklaim"
                    status_color = Fore.GREEN
                elif task['taskStatus'] == 3:
                    status = "Sudah Diklaim"
                    status_color = Fore.YELLOW
                else:
                    status = f"Status: {task['taskStatus']}"
                    status_color = Fore.WHITE
                
                print(f"{status_color}- {task['condition'].get('title', 'Tugas Tanpa Judul')} " + 
                      f"(Reward: {task.get('rewardAmount', '0')} {task.get('rewardToken', 'token')}) - Status: {status}")
            
            return tasks
        else:
            print(Fore.RED + f"❌ Gagal mengambil daftar tugas: {response.text}")
            return []
    
    except Exception as e:
        print(Fore.RED + f"❌ Error dalam mengambil daftar tugas: {str(e)}")
        return []

# Check invite asset status
def check_invite_asset(token, proxies=None):
    try:
        proxy = get_proxy(proxies)
        headers = get_common_headers(token)
        
        response = requests.get(
            "https://mpc-api.planx.io/api/v1/telegram/invite/asset", 
            headers=headers,
            proxies=proxy,
            timeout=30,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                invite_data = data.get("data", {})
                invite_count = invite_data.get("inviteCount", 0)
                symbol = invite_data.get("symbol")
                amount = invite_data.get("amount")
                
                print(Fore.CYAN + f"👥 Invite Stats: {invite_count} invites | Earned: {amount} {symbol}")
                
                return invite_data
            else:
                print(Fore.RED + f"❌ Gagal mendapatkan info invite: {data.get('msg')}")
                return None
        else:
            print(Fore.RED + f"❌ Gagal mendapatkan info invite dengan status code: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.RED + f"❌ Error saat mendapatkan info invite: {str(e)}")
        return None

# Process task
def process_task(token, task, proxies=None, invite_count=0):
    """Process a single task based on its status"""
    try:
        task_id = task['taskId']
        task_title = task['condition'].get('title', 'Tugas Tanpa Judul')
        task_status = task['taskStatus']
        
        # Check if task is related to invites and skip if invite_count is 0
        if "invite" in task_title.lower() and invite_count == 0:
            print(Fore.YELLOW + f"⚠️ Melewati tugas invite '{task_title}' karena akun ini belum memiliki undangan.")
            return True
        
        # Process based on task status
        if task_status == 1 or task_status == 2:  # Belum diambil atau Siap diklaim
            # Print appropriate status message
            if task_status == 1:
                print(Fore.BLUE + f"🔄 Memproses tugas '{task_title}' (belum diambil)...")
            else:
                print(Fore.BLUE + f"🔄 Memproses tugas '{task_title}' (siap diklaim)...")
            
            # Prepare proxy
            proxy = get_proxy(proxies)
            headers = get_common_headers(token)
            headers['content-type'] = 'application/json'
            headers['language'] = 'id'  
            
            # Call task first
            call_payload = {"taskId": task_id}
            call_response = requests.post(
                "https://mpc-api.planx.io/api/v1/telegram/task/call", 
                json=call_payload, 
                headers=headers, 
                proxies=proxy,
                verify=False,
                timeout=10  
            )
            
            if call_response.status_code == 200:
                call_data = call_response.json()
                if call_data.get("success"):
                    print(Fore.GREEN + f"✅ Berhasil memanggil tugas: {task_title}")
                    
                    # Wait for 35 seconds like in the Ruby code before claiming
                    print(Fore.BLUE + f"⏳ Menunggu 35 detik sebelum mengklaim tugas '{task_title}'...")
                    time.sleep(35)  # Wait 35 seconds
                    
                    # Now claim the task
                    return claim_task(token, task_id, task_title, proxies)
                else:
                    print(Fore.RED + f"❌ Gagal memanggil tugas: {task_title} - {call_data.get('msg')}")
                    print(Fore.RED + f"Detail respons: {call_response.text}")
                    return False
            else:
                print(Fore.RED + f"❌ Gagal memanggil tugas: {task_title} - Status code: {call_response.status_code}")
                print(Fore.RED + f"Detail respons: {call_response.text}")
                return False
                
        elif task_status == 3:  # Sudah diklaim
            print(Fore.YELLOW + f"⚠️ Tugas '{task_title}' sudah diklaim sebelumnya. Melewati.")
            return True
            
        else:
            print(Fore.YELLOW + f"⚠️ Status tugas '{task_title}' tidak dikenali: {task_status}. Melewati.")
            return False
    
    except Exception as e:
        print(Fore.RED + f"❌ Error dalam memproses tugas: {str(e)}")
        return False

# Helper function to claim task
def claim_task(token, task_id, task_title, proxies=None):
    """Claim a specific task"""
    try:
        proxy = get_proxy(proxies)
        headers = get_common_headers(token)
        headers['content-type'] = 'application/json'
        headers['language'] = 'id'  # Tambahkan header language seperti di kode Ruby
        
        payload = {"taskId": task_id}
        
        response = requests.post(
            "https://mpc-api.planx.io/api/v1/telegram/task/claim", 
            json=payload, 
            headers=headers, 
            proxies=proxy,
            verify=False,
            timeout=10  # Kurangi timeout menjadi 10 detik seperti di kode Ruby
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(Fore.GREEN + f"✅ Berhasil klaim tugas: {task_title}")
                return True
            else:
                print(Fore.RED + f"❌ Gagal klaim tugas: {task_title} - {data.get('msg')}")
                print(Fore.RED + f"Detail respons: {response.text}")
                return False
        else:
            print(Fore.RED + f"❌ Gagal klaim tugas: {task_title} - Status code: {response.status_code}")
            print(Fore.RED + f"Detail respons: {response.text}")
            return False
    
    except Exception as e:
        print(Fore.RED + f"❌ Error saat klaim tugas: {str(e)}")
        return False

# Function to get PEPE token price
def get_pepe_price(proxies=None):
    try:
        proxy = get_proxy(proxies)
        
        # Try to get PEPE price from a public API
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=pepe&vs_currencies=usd",
            proxies=proxy,
            timeout=30,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            if "pepe" in data and "usd" in data["pepe"]:
                price = data["pepe"]["usd"]
                print(Fore.GREEN + f"💵 Harga PEPE saat ini: ${price:.10f} USD")
                return price
        
        # Fallback if the above doesn't work
        print(Fore.YELLOW + "⚠️ Gagal mendapatkan harga PEPE dari CoinGecko, mencoba API alternatif...")
        
        # Try another API as fallback
        response = requests.get(
            "https://min-api.cryptocompare.com/data/price?fsym=PEPE&tsyms=USD",
            proxies=proxy,
            timeout=30,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            if "USD" in data:
                price = data["USD"]
                print(Fore.GREEN + f"💵 Harga PEPE saat ini: ${price:.10f} USD")
                return price
        
        # If all else fails, use a hardcoded recent price
        print(Fore.YELLOW + "⚠️ Gagal mendapatkan harga PEPE realtime, menggunakan harga default.")
        default_price = 0.00000079  # Update this value periodically
        print(Fore.YELLOW + f"💵 Harga PEPE default: ${default_price:.10f} USD")
        return default_price
        
    except Exception as e:
        print(Fore.RED + f"❌ Error saat mendapatkan harga PEPE: {str(e)}")
        # Return a default price if all attempts fail
        default_price = 0.00000079  # Update this value periodically
        print(Fore.YELLOW + f"💵 Harga PEPE default: ${default_price:.10f} USD")
        return default_price

# Save accounts eligible for withdrawal
def save_eligible_accounts(eligible_accounts):
    try:
        with open('siapwd.txt', 'w') as file:
            for account in eligible_accounts:
                file.write(f"Nickname: {account['nickname']}, Invite Code: {account['invite_code']}, "
                           f"Balance: {account['pepe_balance']} PEPE (${account['usd_value']:.2f} USD)\n")
        
        print(Fore.GREEN + f"✅ Berhasil menyimpan {len(eligible_accounts)} akun yang siap withdrawal ke siapwd.txt")
    except Exception as e:
        print(Fore.RED + f"❌ Error saat menyimpan akun ke siapwd.txt: {str(e)}")


# New function to load tokens from token.txt
def load_tokens():
    try:
        tokens = {}
        if os.path.exists('token.txt'):
            with open('token.txt', 'r') as file:
                for line in file:
                    line = line.strip()
                    if line and ':' in line:
                        parts = line.split(':', 1)
                        init_data = parts[0].strip()
                        token = parts[1].strip()
                        tokens[init_data] = token
            print(Fore.BLUE + f"Berhasil memuat {len(tokens)} token dari token.txt.")
        return tokens
    except Exception as e:
        print(Fore.RED + f"Error saat memuat token: {str(e)}")
        return {}

# New function to save token to token.txt
def save_token(init_data, token, tokens=None):
    try:
        # Jika token untuk init_data ini sudah ada di dictionary tokens, tidak perlu disimpan lagi
        if tokens and init_data in tokens:
            print(Fore.YELLOW + "ℹ️ Token untuk akun ini sudah ada, tidak perlu disimpan ulang.")
            return True
        
        # Cek apakah kombinasi init_data:token sudah ada di file
        if os.path.exists('token.txt'):
            with open('token.txt', 'r') as read_file:
                existing_lines = read_file.readlines()
                for line in existing_lines:
                    if line.strip().startswith(init_data + ":"):
                        print(Fore.YELLOW + "ℹ️ Token untuk akun ini sudah ada di file, tidak perlu disimpan ulang.")
                        return True
        
        # Jika tidak ada duplikasi, simpan token baru
        with open('token.txt', 'a') as file:
            file.write(f"{init_data}:{token}\n")
        print(Fore.GREEN + "✅ Token berhasil disimpan ke token.txt")
        
        # Update dictionary tokens jika diberikan
        if tokens is not None:
            tokens[init_data] = token
            
        return True
    except Exception as e:
        print(Fore.RED + f"❌ Error saat menyimpan token: {str(e)}")
        return False

# Modified process_account function to use token.txt and fix PEPE calculation
def process_account(init_data, account_index, total_accounts, proxies=None, pepe_price=None, eligible_accounts=None, tokens=None):
    print(Fore.CYAN + f"\n[{account_index + 1}/{total_accounts}] 🔄 Memproses akun...")
    
    # Check if token already exists
    token = None
    if tokens and init_data in tokens:
        token = tokens[init_data]
        print(Fore.GREEN + "✅ Menggunakan token yang tersimpan, melewati proses login.")
    
    # If no token, login to the account
    if not token:
        token = login_account(init_data, proxies)
        if not token:
            print(Fore.RED + "❌ Gagal login, melewati akun ini.")
            return
        else:
            # Save the token (passing tokens dictionary)
            save_token(init_data, token, tokens)
       
    # Get account info
    account_info = get_account_info(token, proxies)
    if not account_info:
        print(Fore.RED + "❌ Gagal mendapatkan info akun, token mungkin tidak valid. Melewati akun ini.")
        return
    
    nickname = account_info.get("nickName", "Unknown")
    invite_code = account_info.get("inviteCode", "Unknown")
    
    # Check asset task - This already includes total PEPE balance
    asset_task = check_asset_task(token, proxies)
    pepe_amount = 0
    
    if asset_task:
        task_id = asset_task.get("taskId")
        task_status = asset_task.get("taskStatus")
        # Ambil data PEPE dari check_asset_task (total PEPE balance)
        if asset_task.get("symbol") == "PEPE":
            pepe_amount = float(asset_task.get("amount", 0))
        
        # Process based on task status
        if task_status == 1:  # Belum diklaim
            claim_result = claim_asset_task(token, task_id, proxies)
            if claim_result:
                print(Fore.GREEN + "✅ Asset task berhasil diklaim.")
            else:
                print(Fore.RED + "❌ Gagal mengklaim asset task.")
        elif task_status == 2:  # Sudah di claim dan sedang farming
            print(Fore.YELLOW + "⚠️ Asset task sudah diklaim dan sedang farming. Tidak perlu tindakan.")
        else:  # Status lainnya
            print(Fore.YELLOW + f"⚠️ Status asset task tidak dikenali: {task_status}. Melewati.")
    
    # Check invite status - Only to get invite count, not adding PEPE amount
    invite_data = check_invite_asset(token, proxies)
    invite_count = 0
    if invite_data:
        invite_count = invite_data.get("inviteCount", 0)
        # TIDAK menambahkan PEPE dari invites karena asset_task sudah mencakup total
        
        if invite_count == 0:
            print(Fore.YELLOW + "⚠️ Akun ini belum memiliki undangan. Tugas invite akan dilewati.")
    
    # Check withdrawal eligibility using existing data instead of making another API call
    if pepe_price and eligible_accounts is not None:
        usd_value = pepe_amount * pepe_price
        is_eligible = usd_value >= 1.2
        
        if is_eligible:
            print(Fore.GREEN + f"✅ Akun siap untuk withdrawal! Balance: {pepe_amount} PEPE (${usd_value:.2f} USD)")
            eligible_accounts.append({
                "nickname": nickname,
                "invite_code": invite_code,
                "pepe_balance": pepe_amount,
                "usd_value": usd_value
            })
        else:
            print(Fore.YELLOW + f"⚠️ Akun belum siap untuk withdrawal. Balance: {pepe_amount} PEPE (${usd_value:.2f} USD), minimum: $1.2")
    
    # Check lottery task
    lottery_task = check_lottery_task(token, proxies)
    if lottery_task:
        task_id = lottery_task.get("taskId")
        task_status = lottery_task.get("taskStatus")
        
        # Process based on task status
        if task_status == 1:  # Belum diambil
            claim_result = claim_lottery_task(token, task_id, proxies)
            if claim_result:
                print(Fore.GREEN + "✅ Lottery task berhasil diklaim.")
            else:
                print(Fore.RED + "❌ Gagal mengklaim lottery task.")
        elif task_status == 2:  # Siap diklaim
            claim_result = claim_lottery_task(token, task_id, proxies)
            if claim_result:
                print(Fore.GREEN + "✅ Lottery task berhasil diklaim.")
            else:
                print(Fore.RED + "❌ Gagal mengklaim lottery task.")
        else:  # Status 3 atau lainnya
            print(Fore.YELLOW + "⚠️ Lottery task sudah diklaim sebelumnya.")
    
    # Get and process all popular tasks
    print(Fore.BLUE + "\n🔍 Memeriksa daftar tugas populer...")
    tasks = get_task_list(token, proxies)
    
    if tasks:
        print(Fore.BLUE + f"\n🔄 Memproses {len(tasks)} tugas populer...")
        for i, task in enumerate(tasks):
            print(Fore.CYAN + f"\n[{i+1}/{len(tasks)}] Memproses tugas: {task['condition'].get('title', 'Tugas Tanpa Judul')}")
            process_task(token, task, proxies, invite_count)
    
    print(Fore.BLUE + f"\n✅ Selesai memproses akun {account_index + 1}/{total_accounts}")

# Modified countdown timer function
def countdown_timer(duration_hours=3, eligible_accounts=None):
    end_time = datetime.now() + timedelta(hours=duration_hours)
    
    # Display eligible accounts summary if available
    if eligible_accounts:
        total_accounts = len(eligible_accounts)
        total_value = sum(account["usd_value"] for account in eligible_accounts)
        
        print(Fore.GREEN + "\n" + "="*60)
        print(Fore.GREEN + f"📊 RINGKASAN AKUN SIAP WITHDRAWAL: {total_accounts} akun")
        print(Fore.GREEN + f"💰 Total nilai: ${total_value:.2f} USD")
        print(Fore.GREEN + "="*60)
    
    while datetime.now() < end_time:
        # Calculate remaining time
        remaining = end_time - datetime.now()
        hours, remainder = divmod(remaining.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # Print countdown with carriage return to update in place
        sys.stdout.write(f"\r{Fore.YELLOW}⏱️ Menunggu untuk menjalankan ulang: {hours:02d}:{minutes:02d}:{seconds:02d}")
        sys.stdout.flush()
        
        # Sleep for 1 second
        time.sleep(1)
    
    print(Fore.GREEN + "\n⏰ Waktu habis! Menjalankan ulang program...")

# Modified main function to use token.txt
def main():
    print_welcome_message()
    
    # Load accounts, proxies, and tokens
    accounts = load_accounts()
    proxies = load_proxies()
    tokens = load_tokens()
    
    # Process all accounts in a loop
    total_accounts = len(accounts)
    
    print(Fore.BLUE + f"\n🚀 Memulai proses untuk {total_accounts} akun...")
    
    while True:
        # Get PEPE price once at the start
        pepe_price = get_pepe_price(proxies)
        
        # List to store accounts eligible for withdrawal
        eligible_accounts = []
        
        for i, init_data in enumerate(accounts):
            try:
                process_account(init_data, i, total_accounts, proxies, pepe_price, eligible_accounts, tokens)
                
                # Wait 5 seconds before processing the next account
                if i < total_accounts - 1:
                    print(Fore.YELLOW + "\n⏳ Menunggu 5 detik sebelum memproses akun berikutnya...")
                    time.sleep(5)
            except Exception as e:
                print(Fore.RED + f"❌ Error saat memproses akun {i+1}: {str(e)}")
                print(Fore.YELLOW + "⏳ Menunggu 5 detik sebelum memproses akun berikutnya...")
                time.sleep(5)
        
        # Save eligible accounts to file
        if eligible_accounts:
            save_eligible_accounts(eligible_accounts)
        
        print(Fore.GREEN + "\n✅ Semua akun telah diproses.")
        
        # Start the countdown timer with eligible accounts info
        print(Fore.BLUE + "⏱️ Memulai penghitungan mundur 3 jam...")
        countdown_timer(3, eligible_accounts)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\n\nProgram dihentikan oleh pengguna.")
        sys.exit(0)
    except Exception as e:
        print(Fore.RED + f"\n\nTerjadi kesalahan: {str(e)}")
        sys.exit(1)
