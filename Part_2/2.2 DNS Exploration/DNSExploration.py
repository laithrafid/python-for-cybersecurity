import dns
import dns.resolver
import socket
from colorama import Fore, Style
import sys

def ReverseDNS(ip):
    try:
        result = socket.gethostbyaddr(ip)
        return [result[0]] + result[1]
    except socket.herror:
        return None

def DNSRequest(domain):
    ips = []
    try:
        result = dns.resolver.resolve(domain)
        if result:
            print(Fore.GREEN + "Domain: " + domain.strip())
            for answer in result:
                answer_str = str(answer).strip()
                if answer_str:
                    print(Fore.YELLOW + "Answer: " + answer_str)
                    reverse_dns = ReverseDNS(answer.to_text().strip())
                    if reverse_dns:
                        print(Fore.CYAN + "Domain Names: %s" % reverse_dns)
            print(Style.RESET_ALL)
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout):
        return []
    return ips

def SubdomainSearch(domain, dictionary, nums):
    successes = []
    for word in dictionary:
        subdomain = word + "." + domain
        DNSRequest(subdomain)
        if nums:
            for i in range(0, 10):
                s = word + str(i) + "." + domain
                DNSRequest(s)

if __name__ == "__main__":
    if sys.version_info.major < 3:
        print("Please run this script with Python 3.")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: python3 DNSExploration.py <domain>")
        sys.exit(1)

    domain = sys.argv[1]
    d = "subdomains.txt"
    dictionary = []
    with open(d, "r") as f:
        dictionary = f.read().splitlines()
    SubdomainSearch(domain, dictionary, True)
