"""Generated UBL 2.0-to-2.3 migration-eligibility table. Do not edit by hand.

visibility: generated
generated_by: claude
"""

from __future__ import annotations

from typing import Final

AUTHORITY_SHA256_2_0: Final = "d3eb3356d425bcf16c786d705ebaed99d7da8e581e1a0bcefc4855d734c0ddc9"
AUTHORITY_SHA256_2_3: Final = "623bef8310db4d979ff28000a96bcc56dbcdda4f6206cf094c0aa79b75817970"
TABLE_SHA256: Final = "5e19c0fd1adbb77db1bb5a110ff79ad0e6b803a4a73090483530a93eb9903755"
SOURCE_VERSION: Final = "2.0"
TARGET_VERSION: Final = "2.3"
MIGRATABLE_2_0_ROOT_NAMES: Final[frozenset[str]] = frozenset({
    "ApplicationResponse",
    "AttachedDocument",
    "BillOfLading",
    "Catalogue",
    "CatalogueDeletion",
    "CatalogueItemSpecificationUpdate",
    "CataloguePricingUpdate",
    "CatalogueRequest",
    "CertificateOfOrigin",
    "CreditNote",
    "DebitNote",
    "DespatchAdvice",
    "ForwardingInstructions",
    "FreightInvoice",
    "Invoice",
    "Order",
    "OrderCancellation",
    "OrderChange",
    "OrderResponse",
    "OrderResponseSimple",
    "PackingList",
    "Quotation",
    "ReceiptAdvice",
    "Reminder",
    "RemittanceAdvice",
    "RequestForQuotation",
    "SelfBilledCreditNote",
    "SelfBilledInvoice",
    "Statement",
    "TransportationStatus",
    "Waybill",
})
