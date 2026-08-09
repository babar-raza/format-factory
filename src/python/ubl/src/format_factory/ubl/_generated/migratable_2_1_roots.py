"""Generated UBL 2.1-to-2.3 migration-eligibility table. Do not edit by hand.

visibility: generated
generated_by: claude
"""

from __future__ import annotations

from typing import Final

AUTHORITY_SHA256_2_1: Final = "60b80d76394a8a2add90723ecb8e0e2e9d826775de9749df37a72d60703f86ed"
AUTHORITY_SHA256_2_3: Final = "623bef8310db4d979ff28000a96bcc56dbcdda4f6206cf094c0aa79b75817970"
TABLE_SHA256: Final = "4fd031ed23ea5e6bc6dcddc7366964944f87c5f6368639aa77523fea6181a658"
SOURCE_VERSION: Final = "2.1"
TARGET_VERSION: Final = "2.3"
MIGRATABLE_2_1_ROOT_NAMES: Final[frozenset[str]] = frozenset({
    "ApplicationResponse",
    "AttachedDocument",
    "AwardedNotification",
    "BillOfLading",
    "CallForTenders",
    "Catalogue",
    "CatalogueDeletion",
    "CatalogueItemSpecificationUpdate",
    "CataloguePricingUpdate",
    "CatalogueRequest",
    "CertificateOfOrigin",
    "ContractAwardNotice",
    "ContractNotice",
    "CreditNote",
    "DebitNote",
    "DespatchAdvice",
    "DocumentStatus",
    "DocumentStatusRequest",
    "ExceptionCriteria",
    "ExceptionNotification",
    "Forecast",
    "ForecastRevision",
    "ForwardingInstructions",
    "FreightInvoice",
    "FulfilmentCancellation",
    "GoodsItemItinerary",
    "GuaranteeCertificate",
    "InstructionForReturns",
    "InventoryReport",
    "Invoice",
    "ItemInformationRequest",
    "Order",
    "OrderCancellation",
    "OrderChange",
    "OrderResponse",
    "OrderResponseSimple",
    "PackingList",
    "PriorInformationNotice",
    "ProductActivity",
    "Quotation",
    "ReceiptAdvice",
    "Reminder",
    "RemittanceAdvice",
    "RequestForQuotation",
    "RetailEvent",
    "SelfBilledCreditNote",
    "SelfBilledInvoice",
    "Statement",
    "StockAvailabilityReport",
    "Tender",
    "TenderReceipt",
    "TendererQualification",
    "TendererQualificationResponse",
    "TradeItemLocationProfile",
    "TransportExecutionPlan",
    "TransportExecutionPlanRequest",
    "TransportProgressStatus",
    "TransportProgressStatusRequest",
    "TransportServiceDescription",
    "TransportServiceDescriptionRequest",
    "TransportationStatus",
    "TransportationStatusRequest",
    "UnawardedNotification",
    "UtilityStatement",
    "Waybill",
})
