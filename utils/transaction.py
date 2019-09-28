from collections import OrderedDict


class Transaction:

    def __init__(self, signature, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature

    def to_ordered_dict(self):
        return OrderedDict([("signature", self.signature), ("sender", self.sender), ("recipient", self.recipient), ("amount", self.amount)])
