from enum import Enum


class Side(str, Enum):
    LOW = "low"
    HIGH = "high"

    @classmethod
    def opposite(cls, value):
        return {
            cls.LOW: cls.HIGH,
            cls.HIGH: cls.LOW,
        }[value]
