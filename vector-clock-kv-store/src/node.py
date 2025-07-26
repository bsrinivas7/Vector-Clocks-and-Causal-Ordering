from flask import Flask, request, jsonify
import sys
import threading
import requests

app = Flask(__name__)
store = {}
vector_clock = {}
buffer = []

NODE_ID = ""
PORT = 0
PEER_PORTS = []

@app.route("/put", methods=["POST"])
def put():
    data = request.json
    key, value = data["key"], data["value"]

    vector_clock[NODE_ID] += 1
    store[key] = value

    for peer_port in PEER_PORTS:
        try:
            requests.post(f"http://host.docker.internal:{peer_port}/write", json={
                "key": key,
                "value": value,
                "vector_clock": vector_clock
            })
        except:
            print(f"[{NODE_ID}] Failed to reach peer at port {peer_port}")

    return jsonify({"status": "written", "vector_clock": vector_clock})


@app.route("/write", methods=["POST"])
def write():
    data = request.json
    key, value, incoming_vc = data["key"], data["value"], data["vector_clock"]

    if is_causally_ready(incoming_vc):
        apply_write(key, value, incoming_vc)
        process_buffer()
        return jsonify({"status": "applied"})
    else:
        buffer.append(data)
        return jsonify({"status": "buffered"})


@app.route("/get/<key>", methods=["GET"])
def get_key(key):
    return jsonify({
        "value": store.get(key),
        "vector_clock": vector_clock
    })

def is_causally_ready(vc):
    for node in vc:
        if node == NODE_ID:
            continue
        if vc[node] > vector_clock.get(node, 0):
            return False
    return True

def apply_write(key, value, incoming_vc):
    store[key] = value
    for node in incoming_vc:
        vector_clock[node] = max(vector_clock.get(node, 0), incoming_vc[node])

def process_buffer():
    for item in buffer[:]:
        if is_causally_ready(item["vector_clock"]):
            apply_write(item["key"], item["value"], item["vector_clock"])
            buffer.remove(item)

if __name__ == "__main__":
    NODE_ID = sys.argv[1]
    PORT = int(sys.argv[2])
    PEER_PORTS = list(map(int, sys.argv[3:]))

    vector_clock = {}
    for i in range(1, 4):  
        vector_clock[f"node{i}"] = 0

    app.run(host="0.0.0.0", port=PORT)
