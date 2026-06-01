---
name: Send Receipt
skill_key: send_receipt
description: Generate a professional receipt image with payer, payee, description, amount, and date. Returns the image as a base64-encoded PNG string.
instructions: Call by agent when a receipt or payment confirmation image needs to be generated after a trade or payment.
requires:
  always: true
runner:
  kind: python_file
  target: send_receipt.py
---

# Send Receipt

Generate a clean, professional receipt image (PNG) and return it as a base64-encoded string.

## Parameters

This skill accepts a JSON object as input params.

- `payer` (string, **required**)
  - Name of the person or entity making the payment.

- `payee` (string, **required**)
  - Name of the person or entity receiving the payment.

- `content` (string, **required**)
  - Description of the goods or service being paid for.

- `amount` (number or string, **required**)
  - The payment amount. Can be a number (e.g. `1250`) or a string with currency symbol (e.g. `"$1,250.00"`).

- `date` (string, optional)
  - The date of the transaction. Default: today's date.
  - Accepts common formats: `2024-06-01`, `June 1, 2024`, etc.

## How to use

1. Call `read_skill` with `skill_key: "send_receipt"` to read this document.
2. Then call `run_doc_skill` with `skill_key: "send_receipt"` and `params`.

Example:

```json
{
  "skill_key": "send_receipt",
  "payer": "John Smith",
  "payee": "ABC Company Ltd.",
  "content": "Payment for consulting services",
  "amount": 1250,
  "date": "June 1, 2024"
}
```

## Output

The runner prints a JSON object to stdout with:

- `ok` (bool): Whether the generation succeeded.
- `image_base64` (string): The base64-encoded PNG image data.
- `error` (string): Error message on failure.
