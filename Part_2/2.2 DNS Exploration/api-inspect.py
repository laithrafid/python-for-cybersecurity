import requests

def get_available_api_calls(api_url):
    try:
        response = requests.options(api_url)
        if response.status_code == 200:
            allowed_methods = response.headers.get("Allow", "").split(",")
            return [method.strip().upper() for method in allowed_methods]
    except requests.RequestException as e:
        print("An error occurred:", str(e))

    return []

if __name__ == "__main__":
    api_url = "https://api.hopper.com"  # Replace with the actual API URL

    api_calls = get_available_api_calls(api_url)

    if api_calls:
        print("Available API calls:")
        for call in api_calls:
            print(call)
    else:
        print("No API calls found or unable to access the API.")
