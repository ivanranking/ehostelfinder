import os
from typing import Any
from decimal import Decimal

from django.conf import settings

try:
    from rave_python.rave import Rave
    from rave_python.rave_exceptions import (
        CardChargeError,
        TransactionChargeError,
        TransactionValidationError,
        TransactionVerificationError,
        UssdChargeError,
        AccountChargeError,
    )
    from rave_python.rave_misc import generateTransactionReference
    from rave_python.rave_payment import Payment as RavePayment
    FLW_AVAILABLE = True
except ImportError:
    FLW_AVAILABLE = False


def _get_rave():
    if not FLW_AVAILABLE:
        raise ImportError("rave_python package is not installed. Run: pip install rave_python")
    return Rave(
        settings.FLW_PUBLIC_KEY,
        settings.FLW_SECRET_KEY,
        production=settings.FLW_PRODUCTION,
        usingEnv=False,
    )


class FlutterwaveService:
    """Wrapper around the Flutterwave Python SDK for processing payments.
    Supports all payment methods including Ugandan mobile money (MTN, Airtel),
    bank transfers, cards, and more."""

    def __init__(self):
        self.rave = _get_rave()

    def _build_common_payload(
        self,
        booking,
        amount: float,
        email: str,
        currency: str = "USD",
        tx_ref: str | None = None,
    ) -> dict[str, Any]:
        if not tx_ref:
            tx_ref = generateTransactionReference()
        full_name = booking.customer.get_full_name() or booking.customer.email
        name_parts = full_name.split() if full_name else []
        first_name = booking.customer.first_name or (name_parts[0] if name_parts else "")
        last_name = booking.customer.last_name or (name_parts[-1] if len(name_parts) > 1 else "")
        phone = ""
        try:
            phone = booking.customer.profile.phone or ""
        except (AttributeError, Exception):
            pass
        return {
            "amount": str(amount),
            "email": email,
            "firstname": first_name,
            "lastname": last_name,
            "phonenumber": phone,
            "currency": currency,
            "txRef": tx_ref,
            "IP": "127.0.0.1",
        }

    def charge_card(self, booking, amount: float, card_details: dict[str, Any], tx_ref: str | None = None) -> dict[str, Any]:
        """Charge a credit/debit card."""
        payload = self._build_common_payload(booking, amount, booking.customer.email, card_details.get("currency", "USD"), tx_ref)
        payload.update({
            "cardno": card_details["cardno"],
            "cvv": card_details["cvv"],
            "expirymonth": card_details["expirymonth"],
            "expiryyear": card_details["expiryyear"],
        })
        try:
            response = self.rave.Card.charge(payload)
            return self._normalize_response(response, tx_ref or payload["txRef"])
        except CardChargeError as e:
            return {"error": True, "errMsg": e.err.get("errMsg", str(e)), "txRef": tx_ref or payload["txRef"]}

    def charge_bank_transfer(self, booking, amount: float, tx_ref: str | None = None) -> dict[str, Any]:
        """Charge via bank transfer (creates virtual account)."""
        payload = self._build_common_payload(booking, amount, booking.customer.email, "USD", tx_ref)
        try:
            response = self.rave.BankTransfer.charge(payload)
            return self._normalize_response(response, tx_ref or payload["txRef"])
        except AccountChargeError as e:
            return {"error": True, "errMsg": e.err.get("errMsg", str(e)), "txRef": tx_ref or payload["txRef"]}

    def charge_account(self, booking, amount: float, tx_ref: str | None = None) -> dict[str, Any]:
        """Charge via bank account direct debit."""
        payload = self._build_common_payload(booking, amount, booking.customer.email, "NGN", tx_ref)
        try:
            response = self.rave.Account.charge(payload)
            return self._normalize_response(response, tx_ref or payload["txRef"])
        except AccountChargeError as e:
            return {"error": True, "errMsg": e.err.get("errMsg", str(e)), "txRef": tx_ref or payload["txRef"]}

    def charge_mobile_money(self, booking, amount: float, network: str, phonenumber: str, tx_ref: str | None = None) -> dict[str, Any]:
        """Charge via mobile money. Supports MTN and Airtel Money in Uganda,
        as well as other African countries."""
        payload = self._build_common_payload(booking, amount, booking.customer.email, "USD", tx_ref)
        payload["phonenumber"] = phonenumber

        try:
            network_lower = network.lower()
            if network_lower == "ghana" or network_lower == "ghmobile":
                payload["network"] = "MTN"
                response = self.rave.GhMobile.charge(payload)
            elif network_lower == "kenya" or network_lower == "mpesa":
                response = self.rave.Mpesa.charge(payload)
            elif network_lower == "uganda" or network_lower == "ugmobile":
                network_provider = payload.get("network_provider", "MTN")
                response = self._charge_ug_mobile_money(payload, network_provider)
            elif network_lower == "zambia" or network_lower == "zbmobile":
                payload["network"] = "ZMW"
                response = self.rave.ZBMobile.charge(payload)
            elif network_lower == "tanzania" or network_lower == "tzmobile":
                response = self.rave.TZSMobile.charge(payload)
            elif network_lower == "rwanda" or network_lower == "rwmobile":
                payload["network"] = "RWF"
                response = self.rave.RWMobile.charge(payload)
            elif network_lower == "francophone":
                response = self.rave.Francophone.charge(payload)
            else:
                return {"error": True, "errMsg": f"Unsupported mobile money network: {network}", "txRef": tx_ref or payload["txRef"]}
            return self._normalize_response(response, tx_ref or payload["txRef"])
        except TransactionChargeError as e:
            return {"error": True, "errMsg": e.err.get("errMsg", str(e)), "txRef": tx_ref or payload["txRef"]}
        except AccountChargeError as e:
            return {"error": True, "errMsg": e.err.get("errMsg", str(e)), "txRef": tx_ref or payload["txRef"]}

    def _charge_ug_mobile_money(self, payload: dict[str, Any], network_provider: str = "MTN") -> dict[str, Any]:
        """Charge via Ugandan mobile money (MTN or Airtel Money).
        Uses Payment.charge() directly to set the correct payment_type and network."""
        payload["payment_type"] = "mobilemoneyuganda"
        payload["country"] = "UG"
        payload["currency"] = "UGX"
        payload["is_mobile_money_ug"] = "1"
        payload["network"] = network_provider.upper()

        gh_mobile = self.rave.GhMobile
        endpoint = gh_mobile._baseUrl + gh_mobile._endpointMap["account"]["charge"]
        required_parameters = ["amount", "email", "phonenumber", "network"]

        response = RavePayment.charge(gh_mobile, payload, required_parameters, endpoint)
        return response

    def charge_ussd(self, booking, amount: float, bank_code: str, account_number: str, phonenumber: str, tx_ref: str | None = None) -> dict[str, Any]:
        """Charge via USSD."""
        payload = self._build_common_payload(booking, amount, booking.customer.email, "NGN", tx_ref)
        payload.update({
            "accountbank": bank_code,
            "accountnumber": account_number,
            "phonenumber": phonenumber,
        })
        try:
            response = self.rave.Ussd.charge(payload, shouldReturnRequest=True)
            return self._normalize_response(response, tx_ref or payload["txRef"])
        except UssdChargeError as e:
            return {"error": True, "errMsg": e.err.get("errMsg", str(e)), "txRef": tx_ref or payload["txRef"]}

    def charge_enaira(self, booking, amount: float, is_token: bool = False, tx_ref: str | None = None) -> dict[str, Any]:
        """Charge via eNaira wallet."""
        payload = self._build_common_payload(booking, amount, booking.customer.email, "NGN", tx_ref)
        payload["is_token"] = is_token
        try:
            response = self.rave.Enaira.charge(payload)
            return self._normalize_response(response, tx_ref or payload["txRef"])
        except AccountChargeError as e:
            return {"error": True, "errMsg": e.err.get("errMsg", str(e)), "txRef": tx_ref or payload["txRef"]}

    def charge_apple_pay(self, booking, amount: float, tx_ref: str | None = None) -> dict[str, Any]:
        """Charge via Apple Pay."""
        payload = self._build_common_payload(booking, amount, booking.customer.email, "USD", tx_ref)
        try:
            response = self.rave.ApplePay.charge(payload)
            return self._normalize_response(response, tx_ref or payload["txRef"])
        except AccountChargeError as e:
            return {"error": True, "errMsg": e.err.get("errMsg", str(e)), "txRef": tx_ref or payload["txRef"]}

    def charge_google_pay(self, booking, amount: float, tx_ref: str | None = None) -> dict[str, Any]:
        """Charge via Google Pay."""
        payload = self._build_common_payload(booking, amount, booking.customer.email, "USD", tx_ref)
        try:
            response = self.rave.GooglePay.charge(payload)
            return self._normalize_response(response, tx_ref or payload["txRef"])
        except AccountChargeError as e:
            return {"error": True, "errMsg": e.err.get("errMsg", str(e)), "txRef": tx_ref or payload["txRef"]}

    def validate(self, payment_method: str, flw_ref: str, otp: str) -> dict[str, Any]:
        """Validate a payment with OTP."""
        try:
            if payment_method in ("card", "credit_card"):
                response = self.rave.Card.validate(flw_ref, otp)
            elif payment_method in ("account", "bank_transfer"):
                response = self.rave.Account.validate(flw_ref, otp)
            elif payment_method == "enaira":
                response = self.rave.Enaira.validate(flw_ref, otp)
            else:
                return {"error": True, "errMsg": f"Validation not supported for payment method: {payment_method}"}
            return response
        except TransactionValidationError as e:
            return {"error": True, "errMsg": e.err.get("errMsg", str(e)), "flwRef": flw_ref}

    def verify(self, payment_method: str, tx_ref: str) -> dict[str, Any]:
        """Verify a payment transaction."""
        try:
            if payment_method in ("card", "credit_card"):
                response = self.rave.Card.verify(tx_ref)
            elif payment_method in ("bank_transfer", "account"):
                response = self.rave.BankTransfer.verify(tx_ref)
            elif payment_method in ("mobile_money", "ghana", "ghmobile"):
                response = self.rave.GhMobile.verify(tx_ref)
            elif payment_method in ("mpesa", "kenya"):
                response = self.rave.Mpesa.verify(tx_ref)
            elif payment_method in ("uganda", "ugmobile"):
                response = self.rave.GhMobile.verify(tx_ref)
            elif payment_method in ("zambia", "zbmobile"):
                response = self.rave.ZBMobile.verify(tx_ref)
            elif payment_method in ("tanzania", "tzmobile"):
                response = self.rave.TZSMobile.verify(tx_ref)
            elif payment_method in ("rwanda", "rwmobile"):
                response = self.rave.RWMobile.verify(tx_ref)
            elif payment_method == "francophone":
                response = self.rave.Francophone.verify(tx_ref)
            elif payment_method == "ussd":
                response = {"error": True, "errMsg": "USSD verify not implemented in SDK"}
            elif payment_method == "enaira":
                response = self.rave.Enaira.verify(tx_ref)
            elif payment_method == "applepay":
                response = {"error": True, "errMsg": "Apple Pay verify not implemented in SDK"}
            elif payment_method == "googlepay":
                response = {"error": True, "errMsg": "Google Pay verify not implemented in SDK"}
            else:
                response = self.rave.Card.verify(tx_ref)
            return self._normalize_response(response, tx_ref)
        except TransactionVerificationError as e:
            return {"error": True, "errMsg": e.err.get("errMsg", str(e)), "txRef": tx_ref}

    def _normalize_response(self, response: dict[str, Any], tx_ref: str) -> dict[str, Any]:
        """Normalize the Flutterwave response to a consistent format."""
        result = dict(response)
        result["txRef"] = result.get("txRef", tx_ref)
        result["error"] = result.get("error", False)
        if "validationRequired" not in result:
            result["validationRequired"] = False
        if "authUrl" not in result:
            result["authUrl"] = result.get("authurl", None)
        return result

    def refund(self, payment_method: str, flw_ref: str, amount: Decimal) -> dict[str, Any]:
        """Refund a payment."""
        try:
            if payment_method in ("card", "credit_card"):
                return self.rave.Card.refund(flw_ref, amount)
            elif payment_method in ("bank_transfer", "account"):
                return self.rave.BankTransfer.refund(flw_ref, amount)
            elif payment_method in ("mobile_money", "ghmobile"):
                return self.rave.GhMobile.refund(flw_ref, amount)
            elif payment_method in ("mpesa", "kenya"):
                return self.rave.Mpesa.refund(flw_ref, amount)
            elif payment_method in ("uganda", "ugmobile"):
                return self.rave.GhMobile.refund(flw_ref, amount)
            elif payment_method in ("zambia", "zbmobile"):
                return self.rave.ZBMobile.refund(flw_ref, amount)
            elif payment_method == "francophone":
                return self.rave.Francophone.refund(flw_ref, amount)
            elif payment_method == "enaira":
                return self.rave.Enaira.refund(flw_ref, amount)
            else:
                return {"error": True, "errMsg": f"Refund not supported for payment method: {payment_method}"}
        except Exception as e:
            return {"error": True, "errMsg": str(e)}


def get_flutterwave_service() -> FlutterwaveService:
    return FlutterwaveService()
