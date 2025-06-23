import requests
import time

nodes = {
    "node1": "http://host.docker.internal:5000",
    "node2": "http://host.docker.internal:5001",
    "node3": "http://host.docker.internal:5002"
}

def put(node, key, value):
    print(f"\n[PUT] {node} → {key} = {value}")
    try:
        res = requests.post(nodes[node] + "/put", json={"key": key, "value": value})
        print("Response:", res.json())
    except Exception as e:
        print(f"[ERROR] Failed to PUT to {node}: {e}")

def get(node, key):
    print(f"\n[GET] {node} → {key}")
    try:
        res = requests.get(nodes[node] + f"/get/{key}")
        print("Response:", res.json())
    except Exception as e:
        print(f"[ERROR] Failed to GET from {node}: {e}")

if __name__ == "__main__":
    print("==== Causal Consistency Test Scenario ====\n")

    put("node1", "x", "A")  # Initial write
    time.sleep(1)

    get("node2", "x")       # node2 may not have A yet
    time.sleep(1)

    put("node2", "x", "B")  # causally depends on A
    time.sleep(1)

    get("node3", "x")       # node3 must receive A before B
    time.sleep(1)

    print("\n==== Test Finished ====")
