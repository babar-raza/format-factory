# Spec Evidence: SafeTensors

## Primary Specification
- **Title:** SafeTensors format specification
- **Version:** v0.4
- **URL:** https://huggingface.co/docs/safetensors/
- **Body:** Hugging Face
- **Accessed:** 2026-07-14
- **License:** Apache 2.0/BSD/MIT

## Spec Availability Assessment
- Freely accessible: Yes
- Machine-readable schema: No
- Actively maintained: Yes

## Key Structural Facts
- The file begins with an 8-byte little-endian unsigned integer specifying the size of the header metadata
- The header is a JSON object mapping tensor names to their dtype, shape, and data_offsets (begin, end)
- Tensor data follows the header contiguously, with each tensor's bytes located at its specified offsets
- Supported dtypes include F16, BF16, F32, F64, I8, I16, I32, I64, U8, BOOL, and F8_E4M3/F8_E5M2
