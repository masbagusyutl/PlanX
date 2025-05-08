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

# Check question config
def check_question_config(token, proxies=None):
    try:
        proxy = get_proxy(proxies)
        headers = get_common_headers(token)
        
        response = requests.get(
            "https://mpc-api.planx.io/api/v1/telegram/question/config",
            headers=headers,
            timeout=30,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                config_data = data.get("data", {})
                total_questions = config_data.get("numbers", 0)
                not_finished = config_data.get("notFinished", 0)
                
                print(Fore.YELLOW + f"📊 Status Pertanyaan: Total {total_questions}, Belum Selesai: {not_finished}")
                
                # Improved logic for question status interpretation
                if total_questions > 0 and not_finished == 0:
                    print(Fore.GREEN + "✅ Akun ini sudah menjawab semua pertanyaan dengan benar.")
                    config_data["needs_answers"] = False
                elif total_questions == 0 and not_finished == 0:
                    print(Fore.YELLOW + "ℹ️ Akun ini belum memiliki pertanyaan.")
                    config_data["needs_answers"] = False
                else:
                    print(Fore.YELLOW + f"ℹ️ Akun ini masih memiliki {not_finished} pertanyaan yang belum diselesaikan.")
                    config_data["needs_answers"] = True
                
                return config_data
            else:
                print(Fore.RED + f"❌ Gagal mendapatkan config pertanyaan: {data.get('msg')}")
                return None
        else:
            print(Fore.RED + f"❌ Gagal mendapatkan config pertanyaan dengan status code: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.RED + f"❌ Error saat mendapatkan config pertanyaan: {str(e)}")
        return None

# Create share message
def create_share_message(token, proxies=None):
    try:
        proxy = get_proxy(proxies)
        headers = get_common_headers(token)
        payload = {
            "text": "🚀 Bergabunglah dengan PlanX Wallet & buka utilitas crypto dunia nyata!\n\nMengapa PlanX?\n\nUndang teman dan dapatkan 1.000+ PEPE secara instan\nSelesaikan misi harian & buka hadiah berlapis\nNikmati acara kejutan menyenangkan — kapan saja!\n\n▶️ Tingkatkan penghasilan Anda dengan PlanX sekarang ⬇️\n",
            "btnTitle": "Bergabunglah dengan PlanX & buka utilitas crypto dunia nyata! 💰"
        }
        
        response = requests.post(
            "https://mpc-api.planx.io/api/v1/telegram/share/msg/new",
            headers=headers,
            json=payload,
            timeout=30,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                share_data = data.get("data", {})
                share_id = share_data.get("id")
                expiration = share_data.get("expiration_date")
                
                print(Fore.GREEN + f"✅ Berhasil membuat pesan share dengan ID: {share_id}")
                
                return share_data
            else:
                print(Fore.RED + f"❌ Gagal membuat pesan share: {data.get('msg')}")
                return None
        else:
            print(Fore.RED + f"❌ Gagal membuat pesan share dengan status code: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.RED + f"❌ Error saat membuat pesan share: {str(e)}")
        return None

def get_questions(token, proxies=None):
    try:
        proxy = get_proxy(proxies)
        headers = get_common_headers(token)
        
        response = requests.get(
            "https://mpc-api.planx.io/api/v1/telegram/question/view",
            headers=headers,
            timeout=30,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                questions_data = data.get("data", {})
                questions = questions_data.get("questions", [])
                answers = questions_data.get("answers", [])
                results = questions_data.get("results", [])

                # Inisialisasi variabel
                unanswered_indices = []
                has_questions = False
                has_results = len(results) > 0
                
                # Cetak informasi dasar
                if questions:
                    print(Fore.CYAN + f"📝 Mendapatkan {len(questions)} pertanyaan")
                    has_questions = True
                    
                    # Jika ada hasil untuk semua pertanyaan, periksa mana yang belum benar
                    if has_results:
                        if len(results) == len(questions):
                            correct_count = sum(1 for result in results if result == 1)
                            print(Fore.CYAN + f"📊 Status: {correct_count}/{len(questions)} pertanyaan dijawab dengan benar")
                            
                            # Jika semua sudah benar, informasikan
                            if correct_count == len(questions):
                                print(Fore.GREEN + "✅ Semua pertanyaan sudah dijawab dengan benar dalam sistem")
                            else:
                                # Catat pertanyaan yang belum dijawab dengan benar
                                for i, result in enumerate(results):
                                    if result == 0:
                                        unanswered_indices.append(i)
                                
                                print(Fore.YELLOW + f"⚠️ Ditemukan {len(unanswered_indices)} pertanyaan yang belum dijawab dengan benar")
                                
                                # Tampilkan detail pertanyaan yang belum dijawab
                                for i in unanswered_indices:
                                    if i < len(questions):
                                        question = questions[i]
                                        question_id = question.get("questionId")
                                        question_text = question.get("questionText")
                                        print(Fore.YELLOW + f"\n🔍 Pertanyaan belum dijawab #{i+1} (ID: {question_id}): {question_text}")
                                        
                                        options = question.get("options", [])
                                        for option in options:
                                            option_id = option.get("optionId")
                                            option_text = option.get("optionText")
                                            print(Fore.WHITE + f"   📌 Opsi {option.get('optionOrder')}: {option_text} (ID: {option_id})")
                        else:
                            # Ada ketidaksesuaian antara jumlah hasil dan jumlah pertanyaan
                            print(Fore.YELLOW + f"⚠️ Ketidaksesuaian data: {len(results)} hasil untuk {len(questions)} pertanyaan")
                            unanswered_indices = list(range(len(questions)))
                    else:
                        # Tidak ada hasil, anggap semua pertanyaan belum dijawab
                        unanswered_indices = list(range(len(questions)))
                        print(Fore.YELLOW + f"⚠️ Semua {len(questions)} pertanyaan perlu dijawab")
                else:
                    print(Fore.YELLOW + "ℹ️ Tidak ada pertanyaan yang tersedia")

                # Tambahkan informasi tambahan ke data yang dikembalikan
                questions_data["unanswered_indices"] = unanswered_indices
                questions_data["has_answered_questions"] = has_questions and not unanswered_indices and has_results
                questions_data["total_questions"] = len(questions)
                questions_data["correct_questions"] = len(questions) - len(unanswered_indices) if has_results else 0
                
                return questions_data
            else:
                print(Fore.RED + f"❌ Gagal mendapatkan pertanyaan: {data.get('msg')}")
                return None
        else:
            print(Fore.RED + f"❌ Gagal mendapatkan pertanyaan dengan status code: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.RED + f"❌ Error saat mendapatkan pertanyaan: {str(e)}")
        return None

# Answer a question
def answer_question(token, question_id, option_id, proxies=None):
    try:
        proxy = get_proxy(proxies)
        headers = get_common_headers(token)
        payload = {
            "questionId": question_id,
            "optionId": option_id
        }
        
        response = requests.post(
            "https://mpc-api.planx.io/api/v1/telegram/question/answer",
            headers=headers,
            json=payload,
            timeout=30,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                result_data = data.get("data", {})
                result = result_data.get("result")
                amount = result_data.get("amount", "0")
                next_question_id = result_data.get("nextQuestionId")
                
                if result == 1:
                    print(Fore.GREEN + f"✅ Jawaban benar! Mendapatkan {amount} PEPE. Next Question ID: {next_question_id}")
                else:
                    print(Fore.RED + f"❌ Jawaban salah. Next Question ID: {next_question_id}")
                
                return result_data
            else:
                print(Fore.RED + f"❌ Gagal menjawab pertanyaan: {data.get('msg')}")
                return None
        else:
            print(Fore.RED + f"❌ Gagal menjawab pertanyaan dengan status code: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.RED + f"❌ Error saat menjawab pertanyaan: {str(e)}")
        return None

# Reset question
def reset_question(token, question_id, proxies=None):
    try:
        proxy = get_proxy(proxies)
        headers = get_common_headers(token)
        payload = {
            "questionId": question_id
        }
        
        response = requests.post(
            "https://mpc-api.planx.io/api/v1/telegram/question/reset",
            headers=headers,
            json=payload,
            timeout=30,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(Fore.GREEN + f"✅ Berhasil reset pertanyaan ID: {question_id}")
                return True
            else:
                print(Fore.RED + f"❌ Gagal reset pertanyaan: {data.get('msg')}")
                return False
        else:
            print(Fore.RED + f"❌ Gagal reset pertanyaan dengan status code: {response.status_code}")
            return False
    except Exception as e:
        print(Fore.RED + f"❌ Error saat reset pertanyaan: {str(e)}")
        return False

# Check jackpot
def check_jackpot(token, proxies=None):
    try:
        proxy = get_proxy(proxies)
        headers = get_common_headers(token)
        
        response = requests.post(
            "https://mpc-api.planx.io/api/v1/telegram/question/jackpot",
            headers=headers,
            timeout=30,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                jackpot_data = data.get("data", {})
                amount = jackpot_data.get("amount", "0")
                
                print(Fore.MAGENTA + f"🎰 Jackpot Amount: {amount} PEPE")
                
                return jackpot_data
            else:
                print(Fore.RED + f"❌ Gagal mendapatkan jackpot: {data.get('msg')}")
                return None
        else:
            print(Fore.RED + f"❌ Gagal mendapatkan jackpot dengan status code: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.RED + f"❌ Error saat mendapatkan jackpot: {str(e)}")
        return None

# Update get_correct_answer dengan jawaban untuk pertanyaan AMA
def get_correct_answer(question):
    """Return the correct option ID based on question content"""
    question_id = question.get("questionId")
    question_text = question.get("questionText")
    options = question.get("options", [])
    
    # Math questions
    if "+" in question_text or "-" in question_text or "*" in question_text or "/" in question_text:
        # Extract the math expression
        expression = question_text.split("=")[0].strip()
        try:
            correct_result = eval(expression)
            
            # Find the option that matches the result
            for option in options:
                option_text = option.get("optionText")
                try:
                    if float(option_text) == correct_result:
                        return option.get("optionId")
                except:
                    pass
        except:
            pass
    
    # Hard-coded answers for known questions
    known_answers = {
        # Siapa yang menentukan harga gas?
        134: 402,  # "Pasar Jaringan Saat Ini"
        
        # Apa itu dompet MPC?
        153: 458,  # "Dompet dengan Kunci Tersebar"
        
        # Apa risiko dompet self-custody?
        161: 481,  # "Kehilangan Kunci, Kehilangan Aset"
        
        # Bear merujuk pada apa?
        28: 82,    # "Lingkungan pasar kripto dengan harga turun"
        
        # Apa arti TVL?
        94: 281,   # "Total Nilai Terkunci, total nilai dana yang terkunci dalam protokol"
        
        # Whale merujuk pada tipe orang seperti apa?
        29: 85,    # "Pemegang besar"
        
        # Apa kepanjangan Dex?
        33: 98,    # "Bursa Terdesentralisasi"
        
        # AMA adalah singkatan dari apa?
        19: 56,    # "Tanya Saya Apa Saja"
    }
    
    # Check if we have a hard-coded answer
    if question_id in known_answers:
        return known_answers[question_id]
    
    # Check for AMA question by text
    if "AMA" in question_text and "singkatan" in question_text:
        # Cari opsi yang berisi "Tanya Saya"
        for option in options:
            option_text = option.get("optionText").lower()
            if "tanya saya" in option_text or ("tanya" in option_text and "saya" in option_text):
                return option.get("optionId")
    
    # For other questions, print options to debug and return first option as default
    print(Fore.YELLOW + f"⚠️ Pertanyaan tidak dikenal: {question_text}")
    for option in options:
        print(f"   - {option.get('optionId')}: {option.get('optionText')}")
    
    return options[0].get("optionId") if options else None

# Updated function to try all possible answers
def try_all_answers(token, question, proxies=None):
    """Try all possible options until finding the correct answer"""
    question_id = question.get("questionId")
    options = question.get("options", [])
    
    print(Fore.YELLOW + f"🔄 Mencoba semua kemungkinan jawaban untuk pertanyaan ID: {question_id}")
    
    # Get the initial questions data to check if this is already answered
    initial_questions_data = get_questions(token, proxies)
    if initial_questions_data:
        results = initial_questions_data.get("results", [])
        questions = initial_questions_data.get("questions", [])
        
        # Find question index in the questions list
        question_index = -1
        for i, q in enumerate(questions):
            if q.get("questionId") == question_id:
                question_index = i
                break
        
        # If we found the question and it's already answered correctly
        if question_index != -1 and question_index < len(results) and results[question_index] == 1:
            print(Fore.GREEN + f"✅ Pertanyaan ini sudah dijawab dengan benar sebelumnya")
            # Create a mock result object with success
            return {"result": 1, "amount": "0", "nextQuestionId": None}
    
    for option in options:
        option_id = option.get("optionId")
        option_text = option.get("optionText")
        
        print(Fore.BLUE + f"  Mencoba jawaban: {option_text}")
        
        # Answer the question with this option
        result = answer_question(token, question_id, option_id, proxies)
        if not result:
            continue
        
        # If correct, return the result
        if result.get("result") == 1:
            print(Fore.GREEN + f"✅ Jawaban benar ditemukan: {option_text}")
            return result
        
        # Get nextQuestionId from result
        next_question_id = result.get("nextQuestionId")
        
        # Create share message for reset
        print(Fore.YELLOW + f"  ⚠️ Jawaban salah, mencoba reset...")
        share_data = create_share_message(token, proxies)
        
        if share_data:
            # Try reset with nextQuestionId first if available
            reset_success = False
            if next_question_id is not None:
                print(Fore.YELLOW + f"  🔄 Mencoba reset dengan nextQuestionId: {next_question_id}")
                reset_success = reset_question(token, next_question_id, proxies)
            
            # If that fails, try with original questionId
            if not reset_success:
                print(Fore.YELLOW + f"  🔄 Mencoba reset dengan questionId: {question_id}")
                reset_success = reset_question(token, question_id, proxies)
            
            # If both reset attempts fail, refresh questions
            if not reset_success:
                print(Fore.YELLOW + "  🔄 Reset gagal, mencoba refresh data pertanyaan...")
                time.sleep(2)
                
                # Refresh data
                refresh_questions = get_questions(token, proxies)
                if not refresh_questions or not refresh_questions.get("questions"):
                    print(Fore.RED + "  ❌ Tidak berhasil mendapatkan pertanyaan baru")
        
        # Wait before next attempt
        time.sleep(2)
    
    # After trying all options and failing, check if the question is actually answered correctly
    # This handles the case where the API returned success but our code didn't catch it
    final_questions_data = get_questions(token, proxies)
    if final_questions_data:
        results = final_questions_data.get("results", [])
        questions = final_questions_data.get("questions", [])
        
        # Find question index in the questions list
        question_index = -1
        for i, q in enumerate(questions):
            if q.get("questionId") == question_id:
                question_index = i
                break
        
        # If we found the question and it's already answered correctly
        if question_index != -1 and question_index < len(results) and results[question_index] == 1:
            print(Fore.GREEN + f"✅ Pertanyaan ini sudah dijawab dengan benar walaupun tidak terdeteksi")
            # Create a mock result object with success
            return {"result": 1, "amount": "0", "nextQuestionId": None}
    
    print(Fore.RED + "❌ Tidak dapat menemukan jawaban yang benar setelah mencoba semua opsi")
    return None

# Updated function to handle a specific question
def process_single_question(token, question, max_attempts=3, proxies=None):
    """Process a single question, trying multiple times if needed until the answer is correct"""
    question_id = question.get("questionId")
    question_text = question.get("questionText")
    
    print(Fore.BLUE + f"\n📝 Pertanyaan: {question_text}")
    
    # First try with our best guess
    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        print(Fore.YELLOW + f"Percobaan ke-{attempts} untuk pertanyaan ID: {question_id}")
        
        # Get the best answer we can determine
        option_id = get_correct_answer(question)
        if not option_id:
            print(Fore.RED + "❌ Tidak dapat menentukan jawaban yang benar")
            # If we can't determine, try all possible answers
            result = try_all_answers(token, question)
            return result
        
        # Answer the question
        result = answer_question(token, question_id, option_id, proxies)
        if not result:
            print(Fore.RED + "❌ Gagal menjawab pertanyaan, melewati...")
            return None
        
        # Check if answer was correct
        if result.get("result") == 1:
            amount = float(result.get("amount", "0"))
            print(Fore.GREEN + f"✅ Berhasil menjawab pertanyaan dengan benar! Mendapatkan {amount} PEPE.")
            return result
        
        # Get next_question_id from result
        next_question_id = result.get("nextQuestionId")
        
        # If answer was wrong, create share message for reset
        print(Fore.YELLOW + f"⚠️ Jawaban salah, membuat pesan share untuk reset menggunakan nextQuestionId: {next_question_id}...")
        share_data = create_share_message(token, proxies)
        
        if share_data and next_question_id is not None:
            # Try reset with nextQuestionId
            reset_result = reset_question(token, next_question_id, proxies)
            
            if reset_result:
                print(Fore.GREEN + f"✅ Berhasil reset pertanyaan dengan ID: {next_question_id}")
            else:
                # If reset fails, try with original question ID
                print(Fore.YELLOW + f"⚠️ Reset dengan nextQuestionId gagal, mencoba reset dengan questionId: {question_id}...")
                reset_result = reset_question(token, question_id, proxies)
                
                if reset_result:
                    print(Fore.GREEN + f"✅ Berhasil reset pertanyaan dengan ID: {question_id}")
                else:
                    # If both resets fail, refresh question data
                    print(Fore.YELLOW + "⚠️ Reset gagal, mendapatkan data pertanyaan baru...")
                    time.sleep(2)
                    
                    new_questions_data = get_questions(token, proxies)
                    if new_questions_data:
                        # Find the question in the updated data
                        new_questions = new_questions_data.get("questions", [])
                        unanswered_indices = new_questions_data.get("unanswered_indices", [])
                        
                        if unanswered_indices and new_questions:
                            # Find the question with matching ID or first unanswered
                            target_question = None
                            for idx in unanswered_indices:
                                if idx < len(new_questions):
                                    if new_questions[idx].get("questionId") == question_id:
                                        target_question = new_questions[idx]
                                        break
                            
                            # If not found, use first unanswered question
                            if not target_question and unanswered_indices and len(new_questions) > unanswered_indices[0]:
                                target_question = new_questions[unanswered_indices[0]]
                            
                            if target_question:
                                print(Fore.GREEN + "✅ Berhasil mendapatkan pertanyaan baru")
                                return process_single_question(token, target_question, max_attempts - attempts, proxies)
                    
                    print(Fore.RED + "❌ Tidak dapat melanjutkan dengan ID pertanyaan ini")
                    return None
        else:
            print(Fore.RED + "❌ Gagal membuat pesan share atau tidak ada nextQuestionId")
            # Try refreshing question data
            time.sleep(2)
            return None
        
        # Wait before next attempt
        time.sleep(2)
    
    # If exhausted all attempts with best guesses, try all possible answers
    print(Fore.YELLOW + "⚠️ Terlalu banyak percobaan gagal, mencoba semua kemungkinan jawaban...")
    return try_all_answers(token, question)

# Update fungsi process_questions dengan logika jackpot yang lebih baik
def process_questions(token, proxies=None):
    # Flag untuk melacak apakah kita baru saja menyelesaikan pertanyaan di sesi ini
    questions_completed_in_this_session = False
    
    # Check if there are questions to answer
    config = check_question_config(token, proxies)
    if not config:
        return False
    
    # Get available questions with details about unanswered ones
    questions_data = get_questions(token, proxies)
    if not questions_data:
        return False
    
    questions = questions_data.get("questions", [])
    results = questions_data.get("results", [])
    unanswered_indices = questions_data.get("unanswered_indices", [])
    
    # Fix: Improved detection of whether all questions have been answered
    all_questions_answered = (len(questions) > 0 and len(unanswered_indices) == 0 and len(results) > 0) or \
                            (len(questions) == 0 and config.get("notFinished", 0) == 0)
    
    # Check if we need to answer questions based on the config
    not_finished = config.get("notFinished", 0)
    total_questions = config.get("numbers", 0)
    
    print(Fore.YELLOW + f"📊 Status: Total Pertanyaan={total_questions}, Belum Selesai={not_finished}")
    
    # If there are no questions or no unanswered ones
    if all_questions_answered:
        print(Fore.GREEN + "✅ Semua pertanyaan sudah dijawab dengan benar")
        
        # Kita akan cek jackpot di akhir fungsi hanya jika pertanyaan diselesaikan dalam sesi ini
    
    # If we still need to answer questions
    if not questions and not_finished > 0:
        print(Fore.YELLOW + "ℹ️ Tidak ada pertanyaan yang tersedia untuk dijawab")
        return True
    
    # Process unanswered questions if there are any
    if len(unanswered_indices) > 0:
        print(Fore.CYAN + f"\n🔄 Memproses {len(unanswered_indices)} pertanyaan yang belum dijawab dengan benar...")
        
        total_correct = 0
        total_earnings = 0
        
        # Process only unanswered questions
        for index in unanswered_indices:
            if index < len(questions):
                question = questions[index]
                question_id = question.get("questionId")
                
                print(Fore.CYAN + f"\n[Question #{index+1}] Memproses pertanyaan ID: {question_id}")
                
                # Process this question until it's answered correctly
                result = process_single_question(token, question)
                
                if result and result.get("result") == 1:
                    total_correct += 1
                    amount = float(result.get("amount", "0"))
                    total_earnings += amount
                
                # Wait 2 seconds between questions
                if index < unanswered_indices[-1]:
                    print(Fore.YELLOW + "⏳ Menunggu 2 detik sebelum pertanyaan berikutnya...")
                    time.sleep(2)
        
        # Check if all unanswered questions were answered correctly
        if total_correct == len(unanswered_indices) and total_correct > 0:
            print(Fore.GREEN + f"\n✅ Semua pertanyaan ({total_correct}/{len(unanswered_indices)}) belum dijawab berhasil dijawab dengan benar!")
   
            # Check jackpot after answering all questions correctly
            print(Fore.MAGENTA + "🎰 Memeriksa jackpot...")
            jackpot_data = check_jackpot(token, proxies)
         
            # Verify all questions are now answered correctly by refreshing data
            refreshed_data = check_question_config(token, proxies)
            if refreshed_data and refreshed_data.get("notFinished", 0) == 0:
                # If we've successfully answered questions in this session, set the flag
                questions_completed_in_this_session = True
                
                # Print summary of earnings from questions
                print(Fore.GREEN + f"\n💰 Total PEPE yang didapatkan dari pertanyaan yang belum dijawab: {total_earnings}")
            else:
                print(Fore.YELLOW + "⚠️ Beberapa pertanyaan masih belum dijawab dengan benar setelah percobaan.")
        else:
            print(Fore.YELLOW + f"\n⚠️ Hanya {total_correct}/{len(unanswered_indices)} pertanyaan yang berhasil dijawab dengan benar.")
            print(Fore.YELLOW + "⚠️ Tidak dapat memeriksa jackpot karena tidak semua pertanyaan terjawab dengan benar.")
    
    # Cek jackpot HANYA jika semua jawaban benar DAN kita baru saja menyelesaikan pertanyaan di sesi ini
    if all_questions_answered and questions_completed_in_this_session:
        print(Fore.MAGENTA + "🎰 Memeriksa jackpot...")
        jackpot_data = check_jackpot(token, proxies)
        
        if jackpot_data:
            jackpot_amount = jackpot_data.get("amount", "0")
            print(Fore.MAGENTA + f"🎰 Jackpot Amount: {jackpot_amount} PEPE")
            
            # Add to total earnings if we're reporting them from this session
            if 'total_earnings' in locals():
                total_earnings += float(jackpot_amount)
                print(Fore.GREEN + f"💰 Total keseluruhan: {total_earnings} PEPE")
        else:
            print(Fore.RED + "❌ Gagal mendapatkan jackpot")
    else:
        # Jelaskan mengapa kita tidak memeriksa jackpot
        if all_questions_answered and not questions_completed_in_this_session:
            print(Fore.YELLOW + "ℹ️ Melewati pengecekan jackpot karena tidak ada pertanyaan yang diselesaikan dalam sesi ini.")
    
    return True

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


    print(Fore.CYAN + f"\n[{account_index + 1}/{total_accounts}] 🔄 Memproses pertanyaan pada akun...")

    # Process questions for this account
    process_questions(token, proxies)
    
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
