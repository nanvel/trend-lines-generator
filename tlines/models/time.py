import datetime


class Time(int):
    def __new__(cls, value):
        value = int(value)
        if value < 0:
            raise ValueError("Seconds since January 1, 1970.")
        return super(cls, cls).__new__(cls, value)

    def to_datetime(self) -> datetime.datetime:
        return datetime.datetime.utcfromtimestamp(int(self))

    @classmethod
    def from_datetime(cls, dt: datetime.datetime) -> "Time":
        return cls(dt.replace(tzinfo=datetime.timezone.utc).timestamp())

    def __str__(self) -> str:
        return self.to_datetime().strftime("%Y-%m-%d %H:%M")

    def __repr__(self):
        return f"{self.__class__.__name__}({int(self)})"
