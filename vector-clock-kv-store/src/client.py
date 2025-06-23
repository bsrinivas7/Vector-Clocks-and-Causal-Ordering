import requests
import time

# Define URLs for each node
nodes = {
    "node1": "http://localhost:5000",
    "node2": "http://localhost:5001",
    "node3": "http://localhost:5002"
}

# PUT request
def put(node, key, value):
    print(f"\n[PUT] {node} → {key} = {value}")
    try:
        response = requests.post(nodes[node] + "/put", json={"key": key, "value": value})
        print("Response:", response.json())
    except Exception as e:
        print(f"[ERROR] Failed to PUT to {node}: {e}")

# GET request
def get(node, key):
    print(f"\n[GET] {node} → {key}")
    try:
        response = requests.get(nodes[node] + f"/get/{key}")
        print("Response:", response.json())
    except Exception as e:
        print(f"[ERROR] Failed to GET from {node}: {e}")

# Test scenario
if __name__ == "__main__":
    print("Starting causal consistency test...")

    put("node1", "x", "A")
    time.sleep(1)  # wait for propagation

    get("node2", "x")
    put("node2", "x", "B")
    time.sleep(1)

    get("node3", "x")

    print("\nTest finished.")
