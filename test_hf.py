import requests

API_URL = "https://router.huggingface.co/hf-inference/models/Qwen/Qwen2.5-1.5B-Instruct"
headers = {} # No token

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()
	
output = query({
	"inputs": "You are a helpful assistant. User: Hello! Please respond.",
})
print("Output:", output)
