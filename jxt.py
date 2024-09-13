import random
import string
import requests
import argparse
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

def get_proxy_input():
    """Prompt the user to input residential proxy details."""
    print("Enter your residential proxy details in the format (ip:port:username:password):")
    proxy_input = input("Proxy: ").strip()
    ip, port, username, password = proxy_input.split(":")
    
    proxy = {
        "http": f"http://{username}:{password}@{ip}:{port}",
        "https": f"http://{username}:{password}@{ip}:{port}"
    }
    return proxy

def generate_random_code(length=16):
    """Generate a random Discord Nitro code."""
    characters = string.ascii_letters + string.digits
    code = ''.join(random.choices(characters, k=length))
    return code

def check_nitro_code(code, proxy):
    """Check if a Discord Nitro code is valid using a proxy."""
    url = f"https://discord.com/api/v9/entitlements/gift-codes/{code}?with_application=false&with_subscription_plan=true"
    try:
        response = requests.get(url, proxies=proxy, timeout=5)

        if response.status_code == 200:
            print(f"Valid code found: {code}")
            return code
        else:
            print(f"Invalid code: {code}")
    except requests.RequestException as e:
        print(f"Request failed for code {code}: {e}")
    return None

def main(proxy):
    """Generate and check Discord Nitro codes using dynamic threading and proxy."""
    valid_codes = []
    num_threads = multiprocessing.cpu_count()  # Detect the number of CPU threads for optimization
    print(f"Detected {num_threads} CPU threads; using {num_threads} threads for checking codes.")
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        while True:
            futures = []
            code = generate_random_code()
            futures.append(executor.submit(check_nitro_code, code, proxy))

            for future in futures:
                result = future.result()
                if result:
                    valid_codes.append(result)
                    if input("A valid code has been found! Do you want to stop? (yes/no): ").strip().lower() == "yes":
                        if valid_codes:
                            with open("valid_codes.txt", 'w') as f:
                                for code in valid_codes:
                                    f.write(code + '\n')
                            print("Valid codes saved to valid_codes.txt")
                        return  # Exit if the user chooses to stop
    
if __name__ == "__main__":
    # Prompt the user for proxy details
    proxy = get_proxy_input()
    main(proxy)
