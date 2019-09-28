from utils.hash_utils import hashBlock, hash_string_256


class Verification:
    @staticmethod
    def verify_transaction(transaction, get_balance):
        sender_balance = get_balance()
        return sender_balance >= transaction.amount

    @staticmethod
    def valid_proof(transactions, last_hash, proof_num):
        guess = (str([tx.to_ordered_dict() for tx in transactions]) +
                 str(last_hash) + str(proof_num)).encode()
        guess_hashed = hash_string_256(guess)
        return guess_hashed[0:2] == "00"

    @classmethod
    def verify_chain(cls, blockchain):
        # verifies that the blockchain has not been tampered with

        # loops through the blockchain, comparing the previous hashed block
        # to the current iteration's previous_hash value
        for (index, block) in enumerate(blockchain):
            if(index == 0):
                continue
            if block.previous_hash != hashBlock(blockchain[index - 1]):
                print("hack detected")
                return False
            if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print("invalid proof")
                return False
        print("verified")
        return True
