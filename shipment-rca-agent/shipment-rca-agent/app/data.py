"""Synthetic logistics data (no real customer/carrier data)."""

def _ev(ts, status, loc, remark=""):
    return {"ts": ts, "status": status, "location": loc, "remark": remark}

SHIPMENTS = {
    "AWB1001": {"carrier": "Delhivery", "pincode": "302001", "events": [
        _ev("2026-09-28 10:00", "picked_up", "Jaipur"),
        _ev("2026-09-29 15:00", "in_transit", "Jaipur Hub"),
        _ev("2026-09-30 12:30", "delivered", "Jaipur", "Delivered to customer")]},
    "AWB1002": {"carrier": "Delhivery", "pincode": "560034", "events": [
        _ev("2026-09-28 09:00", "picked_up", "Bangalore"),
        _ev("2026-09-29 11:00", "out_for_delivery", "Bangalore"),
        _ev("2026-09-29 18:00", "delivery_failed", "Bangalore", "Customer not available"),
        _ev("2026-09-30 17:30", "delivery_failed", "Bangalore", "Customer not available, phone unreachable")]},
    "AWB1003": {"carrier": "Ecom Express", "pincode": "400001", "events": [
        _ev("2026-09-24 10:00", "picked_up", "Delhi"),
        _ev("2026-09-25 08:00", "in_transit", "Delhi Hub"),
        _ev("2026-09-26 21:00", "in_transit", "Nagpur Hub", "Shipment held: hub congestion"),
        _ev("2026-10-02 09:00", "in_transit", "Nagpur Hub", "No movement for 6 days")]},
    "AWB1004": {"carrier": "Delhivery", "pincode": "110045", "events": [
        _ev("2026-09-29 10:00", "picked_up", "Gurgaon"),
        _ev("2026-09-30 13:00", "out_for_delivery", "Delhi"),
        _ev("2026-09-30 19:00", "delivery_failed", "Delhi", "Incomplete address, landmark missing, cannot locate")]},
    "AWB1005": {"carrier": "XpressBees", "pincode": "700001", "events": [
        _ev("2026-09-27 10:00", "picked_up", "Mumbai"),
        _ev("2026-09-30 11:00", "out_for_delivery", "Kolkata"),
        _ev("2026-09-30 16:00", "delivery_failed", "Kolkata", "Customer refused to accept COD order"),
        _ev("2026-10-01 10:00", "rto_initiated", "Kolkata", "Return to origin started")]},
    "AWB1006": {"carrier": "XpressBees", "pincode": "193502", "events": [
        _ev("2026-09-28 10:00", "picked_up", "Pune"),
        _ev("2026-09-29 12:00", "exception", "Pune Hub", "Destination pincode not serviceable"),
        _ev("2026-10-01 12:00", "exception", "Pune Hub", "On hold, awaiting address change")]},
}

CARRIERS = {
    "Delhivery": {"on_time_pct": 93.1, "avg_delay_days": 0.4, "known_issues": []},
    "Ecom Express": {"on_time_pct": 78.4, "avg_delay_days": 2.9,
                     "known_issues": ["Nagpur hub congestion (Sep 24 - Oct 3)"]},
    "XpressBees": {"on_time_pct": 88.0, "avg_delay_days": 1.1, "known_issues": []},
}

UNSERVICEABLE = {("XpressBees", "193502")}
