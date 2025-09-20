# generate_keys.py
import sys
import os

from encryption_module.encryption_module import decrypt_message, generate_rsa_keys, load_private_key, save_key
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Generate keys
private_key, public_key = generate_rsa_keys()
save_key(private_key, "keys/responder_private.pem", private=True)
save_key(public_key, "keys/responder_public.pem", private=False)

print("✅ Keys generated and saved in keys/ folder")

