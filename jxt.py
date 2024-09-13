import random
import string
import aiohttp
import asyncio
import time
from itertools import cycle
import multiprocessing

# Function to input proxy details from the user
def get_proxy_input():
    """Prompt the user to input residential proxy details."""
    print("Enter your residential proxy details in the format (ip:port:username:password). Separate multiple proxies with commas:")
    proxy_input = input("Proxies: ").strip()
    proxies = proxy_input.split(",")
    formatted_proxies = []
    for proxy in proxies:
        ip, port, username, password = proxy.split(":")
        formatted_proxies.append({
            "http": f"http://{username}:{password}@{ip}:{port}",
            "https": f"http://{username}:{password}@{ip}:{port}"
        })
    return formatted_proxies

# Function to generate random code using heuristic rules
def generate_random_code(length=16):
    """Generate a random Discord Nitro code using heuristic-based approach."""
    characters = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(characters, k=length))
        # Simple heuristic to avoid repeated patterns
        if "AAAA" not in code and "1234" not in code:  
            break
    return code

# Async function to check nitro code validity
async def check_nitro_code(session, code, proxy):
    """Check if a Discord Nitro code is valid using an asynchronous request."""
    url = f"https://discord.com/api/v9/entitlements/gift-codes/{code}?with_application=false&with_subscription_plan=true"
    try:
        async with session.get(url, proxy=proxy['http'], timeout=5) as response:
            if response.status == 200:
                print(f"Valid code found: {code}")
                return code
            elif response.status == 429:
                print("Rate limited! Backing off...")
                await asyncio.sleep(random.uniform(5, 10))  # Random backoff to avoid rate limits
            else:
                print(f"Invalid code: {code}")
    except Exception as e:
        print(f"Request failed for code {code}: {e}")
    return None

# Async function to manage the proxy pool and task execution
async def run_code_checks(proxies, num_threads):
    """Run multiple code checks concurrently using asynchronous requests."""
    valid_codes = []
    proxy_pool = cycle(proxies)  # Create a rotating proxy pool
    tasks = []

    # Create an aiohttp session with multiple connections
    async with aiohttp.ClientSession() as session:
        while True:
            # Generate codes and create tasks for checking
            for _ in range(num_threads):
                code = generate_random_code()
                proxy = next(proxy_pool)  # Rotate proxies
                tasks.append(check_nitro_code(session, code, proxy))

            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks)

            # Process the results
            for result in results:
                if result:
                    valid_codes.append(result)
                    user_choice = input("A valid code has been found! Do you want to stop? (yes/no): ").strip().lower()
                    if user_choice == "yes":
                        if valid_codes:
                            with open("valid_codes.txt", 'w') as f:
                                for code in valid_codes:
                                    f.write(code + '\n')
                            print("Valid codes saved to valid_codes.txt")
                        return  # Exit if the user chooses to stop

            # Clear tasks for the next batch
            tasks.clear()

# Main function to initiate code generation and checking
def main():
    # Detect system capabilities
    num_threads = multiprocessing.cpu_count()
    print(f"Detected {num_threads} CPU threads; using {num_threads} threads for checking codes.")

    # Get proxy input from user
    proxies = get_proxy_input()

    # Start the event loop for asynchronous execution
    asyncio.run(run_code_checks(proxies, num_threads))

if __name__ == "__main__":
    main()
