from decimal import Decimal


def find_significant(start: float, stop: float):
    start = Decimal(f"{start:.2g}")
    stop = Decimal(f"{stop:.2g}")

    start_str = f"{start:f}"
    stop_str = f"{stop:f}"

    dot_distance = 0
    if "." in start_str or "." in stop_str:
        dot_distance = (
            max(
                len(start_str) - start_str.find("."), len(stop_str) - stop_str.find(".")
            )
            - 1
        )

    start = start * 10**dot_distance
    stop = stop * 10**dot_distance

    start_str = f"{start:f}"
    stop_str = f"{stop:f}"

    distance = 0
    while True:
        if start_str[-1] == "0" and stop_str[-1] == "0":
            start_str = start_str[:-1]
            stop_str = stop_str[:-1]
            distance += 1
        else:
            break

    if dot_distance:
        step = 1
    else:
        step = 10**distance
    start = round(start / step) * step
    stop = round(stop / step) * step

    results = []

    for i in range(int((stop - start) / step) + 1):
        value = start + i * step
        value_str = f"{value:f}".replace(".", "").replace("0", "")
        value = value / 10**dot_distance

        value_str = value_str.strip("0")

        if value_str == "1":
            results.append((value, 0))
        elif value_str == "5":
            results.append((value, 1))
        elif value_str == "25":
            results.append((value, 2))
        elif value_str == "5":
            results.append((value, 2))
        elif value_str == "2":
            results.append((value, 2))

    if not results:
        return []

    min_priority = min([r[1] for r in results])

    return [float(r[0]) for r in results if r[1] == min_priority]
