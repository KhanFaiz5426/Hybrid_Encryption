# encryption_module.py

import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# ------------------------------------------------------
# Key Management
# ------------------------------------------------------
def generate_rsa_keys():
    """
    Generate a new RSA key pair.
    Returns: (private_key, public_key)
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    return private_key, public_key


def save_key(key, filename, private=True):
    """
    Save RSA key to a file.
    """
    if private:
        pem = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
    else:
        pem = key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    with open(filename, "wb") as f:
        f.write(pem)


def load_private_key(filename):
    """
    Load RSA private key from file.
    """
    with open(filename, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def load_public_key(filename):
    """
    Load RSA public key from file.
    """
    with open(filename, "rb") as f:
        return serialization.load_pem_public_key(f.read())


# ------------------------------------------------------
# Encryption / Decryption
# ------------------------------------------------------
def encrypt_message(public_key, plaintext: str):
    """
    Encrypt a plaintext message using hybrid RSA + AES.
    Returns a dictionary {encrypted_key, ciphertext, nonce}.
    """
    # Step 1: Generate AES key
    aes_key = AESGCM.generate_key(bit_length=128)
    aesgcm = AESGCM(aes_key)

    # Step 2: Encrypt the message with AES
    nonce = os.urandom(12)  # 96-bit nonce
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)

    # Step 3: Encrypt the AES key with RSA public key
    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return {
        "encrypted_key": encrypted_key,
        "ciphertext": ciphertext,
        "nonce": nonce
    }


def decrypt_message(private_key, package: dict) -> str:
    """
    Decrypt a package {encrypted_key, ciphertext, nonce} using RSA + AES.
    Returns the original plaintext string.
    """
    # Step 1: Decrypt AES key with RSA private key
    aes_key = private_key.decrypt(
        package["encrypted_key"],
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Step 2: Decrypt ciphertext with AES key
    aesgcm = AESGCM(aes_key)
    plaintext = aesgcm.decrypt(package["nonce"], package["ciphertext"], None)

    return plaintext.decode()

