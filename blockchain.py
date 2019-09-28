import functools
import json
import pickle
from utils.hash_utils import hashBlock
from block import Block
from utils.transaction import Transaction
from utils.verification import Verification
from utils.printable import Printable
from collections import OrderedDict
from wallet import Wallet

MINING_REWARD = 10


class Blockchain:

    def __init__(self, hosting_node_id):
        genisis_block = Block(0, "", [], 100, 0)
        self.hosting_node = hosting_node_id
        self.__open_transactions = []
        self.chain = [genisis_block]
        self.load_data()

    @property
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self, val):
        self.__chain = val

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def load_data(self):
        try:
            with open("blockchain.txt", mode="r") as data:

                starting_data = data.readlines()
                # file_content = pickle.loads(data.read())
                # blockchain = file_content["bc"]
                # open_transactions = file_content["ot"]

                blockchain_data = json.loads(starting_data[0][:-1])
                updated_blockchain = []
                for block in blockchain_data:
                    converted_tx = [Transaction(transaction["signature"], transaction["sender"], transaction["recipient"],
                                                transaction["amount"]) for transaction in block["transactions"]]
                    updated_block = Block(
                        index=len(updated_blockchain),
                        previous_hash=block["previous_hash"],
                        transactions=converted_tx,
                        proof=block["proof"],
                        timestamp=block["timestamp"]
                    )
                    updated_blockchain.append(updated_block)

                self.chain = updated_blockchain
                open_transactions_data = json.loads(starting_data[1])

                self.__open_transactions = [Transaction(transaction["signature"],
                                                        transaction["sender"], transaction["recipient"], transaction["amount"]) for transaction in open_transactions_data]

        except (IOError, IndexError):
            print("file load error")

    def save_data(self):
        try:
            with open("blockchain.txt", mode="w") as data:
                savable_blockchain = [block.__dict__ for block in [
                    Block(block_el.index, block_el.previous_hash, [
                          tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp)
                    for block_el in self.__chain]]
                savable_tx = [tx.__dict__ for tx in self.__open_transactions]
                data.write(json.dumps(savable_blockchain))
                data.write("\n")
                data.write(json.dumps(savable_tx))
                # save_data = {
                #     "bc": blockchain,
                #     "ot": open_transactions
                # }
                # data.write(pickle.dumps(save_data))
        except IOError:
            print("failed to save")

    def get_balance(self):
        participant = self.hosting_node
        # creates a nested list of total sent to others for the sender
        tx_sender = [
            [tx.amount for tx in block.transactions if participant == tx.sender] for block in self.__chain
        ]

        # creates a nested list of total received  from others
        # or rewards from mining for the sender
        tx_received = [
            [tx.amount for tx in block.transactions if participant == tx.recipient] for block in self.__chain
        ]

        # creates a nested list of all transactions that have not yet been processed for sender
        tx_open_transactions = [tx.amount
                                for tx in self.__open_transactions if tx.sender == participant]

        # appends open transaction list to the sent list
        tx_sender.append(tx_open_transactions)

        # calculates total amount sent by combining all transaction in tx_sender
        amount_sent = functools.reduce(
            lambda acc, cur: acc + sum(cur) if len(cur) > 0 else acc + 0, tx_sender, 0)

        # calculates total amount received by combining all transaction in tx_received
        amount_received = functools.reduce(
            lambda acc, cur: acc + sum(cur) if len(cur) > 0 else acc + 0, tx_received, 0)

        # returns the amount received minus the amount sent
        return amount_received - amount_sent

    def add_value(self, signature, sender, recipient, amount=1.0):
        """ appends a new value to the open transaction list.
        Arguments:
        :sender: The sender of the transaction.
        :recipient: Receiver of the transaction.
        :amount: The amount of the transaction.
        """
        # transaction = {
        #     "sender": sender,
        #     "recipient": recipient,
        #     "amount": amount
        # }
        if self.hosting_node == None:
            return False
        transaction = Transaction(signature, sender, recipient, amount)

        if not Wallet.verify_signature(transaction):
            return False

        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            return True

        print("insufficient funds")
        return False

    def mine_block(self):

        # mines a new block by adding all open transactions to the blockchain
        if self.hosting_node == None:
            return False
        print(self.hosting_node)
        last_block = self.__chain[-1]
        hashed_block = hashBlock(last_block)
        proof = self.proof_of_work()
        # issues a reward to the miner
        # reward_transaction = {
        #     "sender": "MINING",
        #     "recipient": owner,
        #     "amount": MINING_REWARD
        # }

        reward_transaction = Transaction("",
                                         "MINING", self.hosting_node, MINING_REWARD)

        copied_transactions = self.__open_transactions[:]
        copied_transactions.append(reward_transaction)
        block = Block(
            index=len(self.__chain),
            previous_hash=hashed_block,
            transactions=copied_transactions,
            proof=proof
        )
        for tx in block.transactions:
            if not Wallet.verify_signature(tx):
                return False
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        return True

    def proof_of_work(self):
        last_block = self.__chain[-1]
        last_hash = hashBlock(last_block)
        proof = 0
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof

    def print_blockchain(self):
        for block in self.chain:
            print("=" * 90)
            print(block)
