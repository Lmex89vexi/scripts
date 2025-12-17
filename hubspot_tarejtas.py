import requests
import concurrent.futures
import time
from faker import Faker
import functools
import urllib3

urllib3.disable_warnings()  # Suppress SSL warnings for verify=False

# Setup
URL_TEMPLATE = "https://apisol.perfekti.mx/disp/v1/tarjetas/encolar-eventos/"
CONCURRENCY = 120
REQUESTS_TOTAL = 1200

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


def send_post_request(i, session: requests.Session, timeout: int = 5):
    """Send a single POST using the provided requests.Session.

    Args:
        i: numeric id for the request payload
        session: an open requests.Session to reuse connections
        timeout: per-request timeout in seconds

    Returns:
        HTTP status code on success, or None on error.
    """
    random_email = fake.email()
    url = URL_TEMPLATE
    try:
        # Note: session already contains common headers (set by caller)
        print(f"Requesting URL: {url}")
        payload = {
            "id_solicitud": i,
            "properties": {"email": random_email, "id_solicitud": i},
            "action": "FINALIZADA_CORTA_HUBSPOT",
        }

        response = session.post(url, json=payload, timeout=timeout)
        print(f"[{i}] {random_email} => Status: {response.status_code}")
        return response.status_code
    except Exception as e:
        print(f"[{i}] {random_email} => Error: {e}")
        return None


session = requests.Session() 

@measure_time
def stress_test():
    print(
        f"Starting stress test: {REQUESTS_TOTAL} requests with {CONCURRENCY} workers..."
    )

    # Create a single Session to enable connection pooling and shared headers
    
    # Set default headers for the session
    session.headers.update({
        "Content-Type": "application/json",
        "x-api-key": "",
    })

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
            # executor.map will pass only single argument by default; use functools.partial
            func = functools.partial(send_post_request, session=session, timeout=5)
            results = list(executor.map(func, range(REQUESTS_TOTAL)))
    except Exception as e:
        print(f"Error during stress test: {e}")
        results = []
    finally:
        pass

    
    success_count = sum(1 for r in results if r == 200)
    print(f"\nSuccessful requests: {success_count}/{REQUESTS_TOTAL}")


if __name__ == "__main__":
    stress_test()
    session.close()
