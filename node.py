from flask import Flask, jsonify
from wallet import Wallet
from flask_cors import CORS
from blockchain import Blockchain

app = Flask(__name__)
wallet = Wallet()
blockchain = None
CORS(app)


@app.route("/wallet", methods=["POST"])
def create_keys():
    global blockchain
    if wallet.create_keys():
        response = {
        "msg": "Account created", 
        "key": wallet.public_key
        }
        blockchain=Blockchain(wallet.public_key)
        return jsonify(response), 201
    else:
        response = {
        "msg": "Account creation failed"
        }
        return jsonify(response), 500

@app.route("/wallet", methods=["GET"])
def load_keys():
    global blockchain
    if wallet.load_keys():
        response = {
        "msg": "Login Successful", 
        "key": wallet.public_key
        }
        blockchain=Blockchain(wallet.public_key)
        return jsonify(response), 200
    else:
        response = {
        "msg": "Login failed"
        }
        return response, 500



@app.route("/", methods=["GET"])
def get_ui():
    return "it worked"


@app.route("/mine", methods=["POST"])
def mine():
    if blockchain.mine_block():
        return "block mined", 200
    else:
        response = {
            "message": "mining failed",
            "wallet_info":  "No wallet loaded" if wallet.public_key == None else "transaction signature invalid"
        }
        return jsonify(response), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
