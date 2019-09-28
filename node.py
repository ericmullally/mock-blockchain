from flask import Flask, jsonify
from wallet import Wallet
from flask_cors import CORS
from blockchain import Blockchain

app = Flask(__name__)
wallet = Wallet()
blockchain = Blockchain(wallet.public_key)
CORS(app)


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
