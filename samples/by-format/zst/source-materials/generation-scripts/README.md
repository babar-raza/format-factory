# ZST Synthetic Sample Generation Scripts
Sprint: FORMAT-FACTORY-R16-ZST-GATE3B-CORPUS-ACQUISITION-IV-AND-MULTI-FORMAT-INTAKE-SWARM-001

## generate_synthetic_zst.py

Generates 4 deterministic synthetic .zst files using python-zstandard (zstandard 0.25.0).

### Generated files
- minimal-synthetic.zst: compresses a single null byte (minimal valid frame)
- text-compressed.zst: compresses public domain text (US Declaration of Independence, 1776)
- dict-compressed.zst: compresses sample data using a trained zstd dictionary
- random-data.zst: compresses deterministic pseudo-random bytes (fixed seed)

### License
All generated .zst files are project-owned synthetic artifacts.
The compression tool (python-zstandard by Gregory Szorc) is BSD-3-Clause.
The PD text source (US Declaration of Independence, 1776) is public domain.
Generated output files are project-created and belong to format-factory.

### Usage
```
python generate_synthetic_zst.py [output_dir]
```
Default output: samples/by-format/zst/valid/

### Requirements
- Python 3.10+
- zstandard >= 0.19.0 (installed as python-zstandard, BSD-3-Clause)
