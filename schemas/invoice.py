"""
Pydantic schema definitions and validation rules for Invoice Extraction.
"""

from typing import List, Optional
import re
from pydantic import BaseModel, Field, field_validator, model_validator


class VendorInfo(BaseModel):
    name: str = Field(description="Name of the vendor or issuing business")
    address: Optional[str] = Field(default=None, description="Physical address or registered address")
    tax_id: Optional[str] = Field(default=None, description="Tax ID, VAT number, GSTIN, or EIN")
    email: Optional[str] = Field(default=None, description="Contact email address")
    phone: Optional[str] = Field(default=None, description="Contact phone number")
    website: Optional[str] = Field(default=None, description="Vendor website URL")


class CustomerInfo(BaseModel):
    name: str = Field(description="Name of the client, customer, or recipient organization")
    billing_address: Optional[str] = Field(default=None, description="Billing address of the customer")
    shipping_address: Optional[str] = Field(default=None, description="Shipping/delivery address if specified")
    contact_name: Optional[str] = Field(default=None, description="Contact person name at customer organization")
    contact_email: Optional[str] = Field(default=None, description="Customer contact email")
    contact_phone: Optional[str] = Field(default=None, description="Customer contact phone number")


class LineItem(BaseModel):
    item_code: Optional[str] = Field(default=None, description="SKU, item code, or catalog ID")
    description: str = Field(description="Description of the product or service rendered")
    quantity: float = Field(ge=0, description="Quantity of items or hours worked")
    unit_price: float = Field(ge=0, description="Price per unit or hourly rate")
    discount_amount: float = Field(default=0.0, ge=0, description="Discount amount applied to this line item")
    tax_rate_percent: Optional[float] = Field(default=None, ge=0, description="Tax rate percentage (e.g., 5.0 for 5%)")
    total_price: float = Field(ge=0, description="Total price for this line item")

    @field_validator("description")
    @classmethod
    def clean_description(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Line item description cannot be empty")
        return cleaned


class PaymentDetails(BaseModel):
    payment_terms: Optional[str] = Field(default=None, description="e.g. Net 30, Due on Receipt, 50% upfront")
    due_date: Optional[str] = Field(default=None, description="Payment due date (YYYY-MM-DD or standard date)")
    bank_name: Optional[str] = Field(default=None, description="Bank or payment processor name")
    account_number: Optional[str] = Field(default=None, description="Account or IBAN number")
    routing_number: Optional[str] = Field(default=None, description="Routing or sort code / SWIFT / BIC")
    payment_method: Optional[str] = Field(default=None, description="Accepted payment method (ACH, Wire, Card, Check)")
    payment_status: Optional[str] = Field(default="Unpaid", description="Paid, Unpaid, Pending, or Partial")


class Invoice(BaseModel):
    invoice_number: str = Field(description="Invoice identification number")
    invoice_date: str = Field(description="Date the invoice was issued (YYYY-MM-DD or standard representation)")
    purchase_order_number: Optional[str] = Field(default=None, description="Associated PO number if present")
    currency: str = Field(default="USD", description="Currency symbol or standard 3-letter code (e.g., USD, EUR, INR, GBP)")
    vendor: VendorInfo = Field(description="Information about the vendor")
    customer: CustomerInfo = Field(description="Information about the customer/client")
    line_items: List[LineItem] = Field(min_length=1, description="List of invoiced line items")
    subtotal: float = Field(ge=0, description="Subtotal of all items before taxes and discounts")
    discount_total: float = Field(default=0.0, ge=0, description="Total discount amount deducted")
    tax_total: float = Field(default=0.0, ge=0, description="Total tax or VAT amount added")
    shipping_fee: float = Field(default=0.0, ge=0, description="Shipping or handling fee")
    grand_total: float = Field(ge=0, description="Final payable amount")
    payment_details: Optional[PaymentDetails] = Field(default=None, description="Payment information and terms")
    notes_or_terms: Optional[str] = Field(default=None, description="Additional notes, terms of service, or comments")

    @field_validator("currency")
    @classmethod
    def standardize_currency(cls, v: str) -> str:
        cleaned = v.strip().upper()
        # Normalization mapping for common symbols
        symbol_map = {"$": "USD", "€": "EUR", "£": "GBP", "₹": "INR", "¥": "JPY"}
        return symbol_map.get(cleaned, cleaned)

    @field_validator("invoice_number")
    @classmethod
    def validate_invoice_number(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Invoice number cannot be empty")
        return cleaned

    @model_validator(mode="after")
    def validate_financial_consistency(self) -> "Invoice":
        # Check that grand_total roughly equals subtotal - discount_total + tax_total + shipping_fee
        expected_total = round(self.subtotal - self.discount_total + self.tax_total + self.shipping_fee, 2)
        actual_total = round(self.grand_total, 2)
        diff = abs(expected_total - actual_total)
        # Allow small floating point tolerance (e.g. $0.50 for rounding in multi-rate taxes)
        if diff > 1.0:
            # We don't necessarily raise a fatal error if invoice math has complex undisclosed surcharges,
            # but we can attach a note or auto-reconcile if difference is modest, or enforce strictness.
            # Here we enforce a reasonable sanity check:
            raise ValueError(
                f"Financial mismatch: Expected grand_total ~{expected_total} "
                f"(subtotal {self.subtotal} - discount {self.discount_total} + tax {self.tax_total} + shipping {self.shipping_fee}), "
                f"but got {actual_total} (difference of {diff:.2f})"
            )
        return self
