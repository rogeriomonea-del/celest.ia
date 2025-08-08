def normalize_result(route: str, date: str, price: float, *, source: str, currency: str = "BRL", program: str | None = None, fare_type: str | None = None, cabin: str | None = None, meta: dict | None = None):
    item = {
        "route": route,
        "date": date,
        "price": float(price),
        "currency": currency,
        "source": source,
        "program": program,
        "fare_type": fare_type,
        "cabin": cabin,
    }
    if meta:
        item["meta"] = meta
    return item
