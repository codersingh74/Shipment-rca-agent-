from app.data import SHIPMENTS, CARRIERS, UNSERVICEABLE


def get_tracking_events(awb: str) -> dict:
    s = SHIPMENTS.get(awb)
    if not s:
        return {"error": f"AWB {awb} not found"}
    return {"awb": awb, "carrier": s["carrier"], "pincode": s["pincode"], "events": s["events"]}


def get_carrier_performance(carrier: str) -> dict:
    c = CARRIERS.get(carrier)
    return {"carrier": carrier, **c} if c else {"error": f"carrier {carrier} not found"}


def check_pincode_serviceability(carrier: str, pincode: str) -> dict:
    return {"carrier": carrier, "pincode": pincode,
            "serviceable": (carrier, pincode) not in UNSERVICEABLE}


_FUNCS = {f.__name__: f for f in (get_tracking_events, get_carrier_performance, check_pincode_serviceability)}

TOOL_SCHEMAS = [
    {"name": "get_tracking_events",
     "description": "Get the full tracking event history for a shipment by AWB number.",
     "input_schema": {"type": "object", "properties": {"awb": {"type": "string"}}, "required": ["awb"]}},
    {"name": "get_carrier_performance",
     "description": "Get on-time %, average delay and known operational issues for a carrier.",
     "input_schema": {"type": "object", "properties": {"carrier": {"type": "string"}}, "required": ["carrier"]}},
    {"name": "check_pincode_serviceability",
     "description": "Check whether a carrier services a destination pincode.",
     "input_schema": {"type": "object",
                      "properties": {"carrier": {"type": "string"}, "pincode": {"type": "string"}},
                      "required": ["carrier", "pincode"]}},
]


def run_tool(name: str, args: dict) -> dict:
    fn = _FUNCS.get(name)
    if not fn:
        return {"error": f"unknown tool {name}"}
    try:
        return fn(**args)
    except Exception as e:  # tool errors go back to the model, not the user
        return {"error": str(e)}
