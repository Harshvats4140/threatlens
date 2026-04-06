import re
from urllib.parse import urlparse

# =========================
# 🔐 BASIC FEATURES
# =========================

# 1. IP Address in URL
def having_ip_address(url):
    return -1 if re.search(r'\d+\.\d+\.\d+\.\d+', url) else 1

# 2. URL Length Category
def url_length(url):
    if len(url) < 54:
        return 1
    elif len(url) <= 75:
        return 0
    else:
        return -1

# 3. URL Shortener
def shortening_service(url):
    return -1 if re.search(r'bit\.ly|goo\.gl|tinyurl|t\.co|ow\.ly', url) else 1

# 4. @ Symbol
def having_at_symbol(url):
    return -1 if "@" in url else 1

# 5. Double Slash Redirect
def double_slash_redirecting(url):
    return -1 if url.rfind("//") > 6 else 1

# 6. Prefix-Suffix (-) in Domain
def prefix_suffix(domain):
    return -1 if "-" in domain else 1

# 7. Subdomains
def having_sub_domain(url):
    hostname = urlparse(url).hostname or ""
    dots = hostname.count(".")
    if dots <= 2:
        return 1
    elif dots == 3:
        return 0
    else:
        return -1

# 8. HTTPS Token
def https_token(url):
    return 1 if url.startswith("https://") else -1

# 9. Suspicious Words
def suspicious_words(url):
    return -1 if re.search(r'login|verify|update|bank|secure|account|free|bonus|win', url.lower()) else 1

# 10. Long Path
def long_path(url):
    path = urlparse(url).path
    return -1 if len(path) > 50 else 1


# =========================
# 🔥 ADVANCED FEATURES
# =========================

# 11. Count Digits
def count_digits(url):
    return sum(c.isdigit() for c in url)

# 12. Count Special Characters
def count_special_chars(url):
    return len(re.findall(r'[!@#$%^&*(),.?":{}|<>]', url))

# 13. Exact URL Length
def exact_length(url):
    return len(url)

# 14. Domain Length
def domain_length(domain):
    return len(domain)

# 15. Number of Parameters (=)
def count_parameters(url):
    return url.count('=')

# 16. Number of Queries (?)
def count_queries(url):
    return url.count('?')

# 17. Percentage Encoding (%)
def count_percentage(url):
    return url.count('%')

# 18. Abnormal Subdomain
def abnormal_subdomain(url):
    hostname = urlparse(url).hostname or ""
    return -1 if not hostname.startswith("www.") else 1

# 19. Count Dots
def count_dots(url):
    return url.count('.')

# 20. Check HTTP Token in Domain
def http_in_domain(domain):
    return -1 if 'http' in domain else 1


# =========================
# 🚀 MAIN FUNCTION
# =========================

def main(url):
    features = []

    parsed = urlparse(url)
    domain = parsed.hostname or ""

    # BASIC FEATURES
    features.append(having_ip_address(url))
    features.append(url_length(url))
    features.append(shortening_service(url))
    features.append(having_at_symbol(url))
    features.append(double_slash_redirecting(url))
    features.append(prefix_suffix(domain))
    features.append(having_sub_domain(url))
    features.append(https_token(url))
    features.append(suspicious_words(url))
    features.append(long_path(url))

    # ADVANCED FEATURES
    features.append(count_digits(url))
    features.append(count_special_chars(url))
    features.append(exact_length(url))
    features.append(domain_length(domain))
    features.append(count_parameters(url))
    features.append(count_queries(url))
    features.append(count_percentage(url))
    features.append(abnormal_subdomain(url))
    features.append(count_dots(url))
    features.append(http_in_domain(domain))

    return features