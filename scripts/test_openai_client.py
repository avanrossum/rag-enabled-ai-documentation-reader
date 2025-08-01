import os
from openai import OpenAI

# Clear all proxy environment variables
for var in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"]:
    os.environ.pop(var, None)

print("Creating OpenAI client...")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("Client created successfully.")

# Try to use the client to verify it works
print("Testing client with a simple embedding request...")
try:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=["Hello, world!"]
    )
    print("Embedding request successful!")
    print(f"Received {len(response.data[0].embedding)} dimensions")
except Exception as e:
    print(f"Error during embedding request: {e}")