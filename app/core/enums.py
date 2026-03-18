from enum import StrEnum


class TransactionStatus(StrEnum):
    SUCCESSFUL = "successful"
    FAILED = "failed"


class TransactionType(StrEnum):
    PAYMENT = "payment"
    INVOICE = "invoice"
