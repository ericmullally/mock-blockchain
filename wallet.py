from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import Crypto.Random
import binascii


class Wallet:

    def __init__(self):
        self.public_key = None
        self.private_key = None

    def create_keys(self):
        if self.public_key != None or self.private_key != None:
            print("already logged in")
            return
        private_key, public_key = self.generate_key()
        self.public_key = public_key
        self.private_key = private_key
        try:
            with open("key.txt", mode="w") as f:
                f.write(public_key)
                f.write("\n")
                f.write(private_key)
            return True
        except (IOError, IndexError):
            print("failed to store keys")
            return False

    def load_keys(self):
        if self.public_key != None or self.private_key != None:
            print("already logged in")
            return
        try:
            with open("key.txt", mode="r") as f:
                keys = f.readlines()
                self.public_key = keys[0][:-1]
                self.private_key = keys[1]
            return True
        except (IOError, IndexError):
            return False
            print("failed to load keys")

    def generate_key(self):
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.publickey()
        return (binascii.hexlify(private_key.export_key(format="DER")).decode("ascii"), binascii.hexlify(public_key.export_key(format="DER")).decode("ascii"))

    def sign_transaction(self, sender, recipient, amount):
        signer = PKCS1_v1_5.new(RSA.import_key(
            binascii.unhexlify(self.private_key)))
        h = SHA256.new((str(sender) + str(recipient) +
                        str(amount)).encode("utf8"))
        signature = signer.sign(h)
        return binascii.hexlify(signature).decode("ascii")

    @staticmethod
    def verify_signature(transaction):
        if transaction.sender == "MINING":
            return True
        public_key = RSA.import_key(binascii.unhexlify(transaction.sender))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA256.new((str(transaction.sender) + str(transaction.recipient) +
                        str(transaction.amount)).encode("utf8"))
        return verifier.verify(h,  binascii.unhexlify(transaction.signature))
