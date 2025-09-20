import socket, json


server = socket.socket()
server.bind(("localhost", 5000))
server.listen(1)
print("[Server] Listening on port 5000...")

while True:
    conn, addr = server.accept()
    data = conn.recv(4096).decode()
    conn.close()

    package = json.loads(data)
    print("\n[Server] Received encrypted SOS (not decrypting):")
    print("   Encrypted key (truncated):", package["encrypted_key"][:50], "...")
    print("   Ciphertext (truncated):", package["ciphertext"][:50], "...\n")

    # Forward to responder (save to file)
    with open("sos_package.json", "w") as f:
        json.dump(package, f)
    print("[Server] Forwarded package to responder.\n")
