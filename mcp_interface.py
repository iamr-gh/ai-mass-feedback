import requests
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python mcp_interface.py <prompt>")
        sys.exit(1)
    prompt = sys.argv[1]
    url = "http://localhost:8000"
    payload = {"prompt": prompt}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        print("Response from server:")
        print(data)
    except requests.RequestException as e:
        print(f"HTTP Request failed: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()