from utils.verification import Verification
from blockchain import Blockchain
from uuid import uuid4
from wallet import Wallet


class Node:

    def __init__(self):
        self.add_new = True
        self.open_transactions = []
        self.wallet = Wallet()
        self.blockchain = None

    def get_user_choice(self):
        # prints option the user an enter, and returns the users choice
        print("1: new transaction")
        print("2: mine new block")
        print("3: end program")
        print("4: show balance")
        print("5: show blockchain")
        print("6: create wallet")
        print("7: login")
        user_response = input("What would you like to do? ")
        return user_response

    def listen_for_input(self):
        while self.add_new:
            user_answer = self.get_user_choice()
            if user_answer == "1":
                if self.wallet.public_key == None:
                    print("transaction cancelled, please log in or create account")
                    continue
                new_transaction = self.get_transaction()
                recipient, amount = new_transaction
                signature = self.wallet.sign_transaction(
                    self.wallet.public_key, recipient, amount)
                if self.blockchain.add_value(signature, self.wallet.public_key, recipient, amount):
                    print("success!!")
                else:
                    print("transaction cancelled")
            elif user_answer == "2":
                if not self.blockchain.mine_block():
                    print("no wallet found")
            elif user_answer == "3":
                self.add_new = False
            elif user_answer == "4":
                if self.wallet.public_key == None:
                    print("please login or create a new account")
                    continue
                print("balance for {} : {:6.2f}".format(
                    self.wallet.public_key, self.blockchain.get_balance()))
            elif user_answer == "5":
                self.blockchain.print_blockchain()
            elif user_answer == "6":
                self.wallet.create_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            elif user_answer == "7":
                self.wallet.load_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            else:
                print("answer invalid")
            if not Verification.verify_chain(self.blockchain.chain):
                print("hack detected")
                break

    def get_transaction(self):
        # gets user input for a new transaction returns a tuple for the new transaction
        recipient = input("please provide recipient's name ")
        amount = float(input("please provide the amount "))
        return (recipient, amount)


node = Node()
node.listen_for_input()
