# Legal Notes: SafeTensors

## Classification
- **Legal Category:** 2
- **Category Name:** Permissive OSS
- **Patent Status:** No known patent barriers
- **License:** Apache 2.0 (Hugging Face safetensors library)

## Implementation Freedom
- Read: Unrestricted
- Write: Unrestricted
- Distribution: Unrestricted under Apache 2.0

## Notes
SafeTensors is an open format created by Hugging Face and released under Apache 2.0. The format was specifically designed as a safe alternative to pickle-based model serialization. The specification is simple (header + raw tensor data) with no proprietary extensions. Multiple independent implementations exist in Rust, Python, C++, and JavaScript. Safe for parser implementation.
