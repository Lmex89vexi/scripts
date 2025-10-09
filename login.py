import requests
import concurrent.futures
import time
from faker import Faker
import functools
import urllib3

urllib3.disable_warnings()  # Suppress SSL warnings for verify=False

# Setup
URL_TEMPLATE = (
    "https://solbackend.vexi.mx/v1/solicitud/login/{email}/?inbox=false"
)
CONCURRENCY = 5
REQUESTS_TOTAL = 200

fake = Faker()


def measure_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        print(f"Starting '{func.__name__}'...")
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        print(f"Finished '{func.__name__}' in {duration:.2f} seconds.")
        return result

    return wrapper


def send_post_request(i):
    random_email = fake.email()
    url = URL_TEMPLATE.format(email=random_email)
    try:
        print(f"Requesting URL: {url}")
        headers = {"Referer": "https://www.vexi.mx"}
        response = requests.post(
            url,
            headers=headers,
            json={
                "codRef": 442,
                "pubId": "",
                "visitor": "",
                "query_params": "",
            },
            verify=False,
        )
        print(f"[{i}] {random_email} => Status: {response.status_code}")
        return response.status_code
    except Exception as e:
        print(f"[{i}] {random_email} => Error: {e}")
        return None


@measure_time
def stress_test():
    print(
        f"Starting stress test: {REQUESTS_TOTAL} requests with {CONCURRENCY} workers..."
    )

    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        results = list(executor.map(send_post_request, range(REQUESTS_TOTAL)))

    success_count = sum(1 for r in results if r == 200)
    print(f"\nSuccessful requests: {success_count}/{REQUESTS_TOTAL}")


if __name__ == "__main__":
    stress_test()
