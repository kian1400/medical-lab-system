import json
from typing import Any, Dict


def send_sms(phone: str, message: str) -> Dict[str, Any]:
    """Stub SMS provider integration for lab app. Replace with real gateway later."""
    if not phone:
        return {"success": False, "message": "Missing phone number"}
    return {
        "success": True,
        "provider": "mock_gateway",
        "phone": phone,
        "message": message,
        "status": "queued",
    }


def create_payment_record(order, gateway: str = "mock") -> Dict[str, Any]:
    """Payment abstraction for mock/real gateway integration."""
    return {
        "success": True,
        "gateway": gateway,
        "order_id": str(order.id),
        "tracking_code": order.tracking_code,
        "amount": str(order.total_price),
        "transaction_id": f"TX-{order.tracking_code}",
        "status": "completed",
    }
