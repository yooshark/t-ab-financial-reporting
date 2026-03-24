from enum import StrEnum


class LoggingLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class TransactionStatus(StrEnum):
    SUCCESSFUL = "successful"
    FAILED = "failed"


class TransactionType(StrEnum):
    PAYMENT = "payment"
    INVOICE = "invoice"


class MetricSortByCountry(StrEnum):
    TOTAL = "total"
    COUNT = "count"
    AVG = "avg"
