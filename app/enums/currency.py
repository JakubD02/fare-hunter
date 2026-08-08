from enum import StrEnum


class Currency(StrEnum):
    PLN = "PLN"
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"

    @classmethod
    def default(cls):
        return cls.PLN
