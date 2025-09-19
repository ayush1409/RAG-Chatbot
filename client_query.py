import requests

def send_request(api_url, question, k: int = 4):
    body = {
        "query": question,
        "top_k": k
    }
    print(body)
    response = requests.post(api_url, json=body)
    if response.status_code == 200:
        print("✅ Successfully sent data")
        print(response.json())
    else:
        print(f"❌ Error: {response.status_code}, {response.text}")

if __name__ == "__main__":
    API_URL = "http://127.0.0.1:8000/query"
    question = "Who is Sachin?"
    send_request(API_URL, question)
