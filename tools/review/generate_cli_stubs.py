"""Generate cli.py, __init__.pyi, and pyproject.scripts for remaining 15 Python packages."""
from pathlib import Path

base = Path(__file__).parent.parent.parent / "src" / "python"

CLI_TEMPLATE = (
    '"""CLI entry point for Format Factory {PKG_UPPER} ({EXT} files).\n\n'
    "Usage:\n"
    "    ff-{PKG} [FILE]\n\n"
    "If FILE is omitted, prints usage and exits.\n"
    '"""\n'
    "from __future__ import annotations\n\n"
    "import sys\n"
    "from pathlib import Path\n\n\n"
    "def main() -> None:\n"
    '    """Entry point for the ff-{PKG} command-line tool."""\n'
    "    if len(sys.argv) < 2:\n"
    '        print("Usage: ff-{PKG} FILE{EXT}")\n'
    '        print("       Inspect a {PKG_UPPER} file.")\n'
    "        sys.exit(0)\n\n"
    "    path = sys.argv[1]\n"
    "    if not Path(path).exists():\n"
    '        print(f"Error: file not found: {path}", file=sys.stderr)\n'
    "        sys.exit(1)\n\n"
    "    {IMPORT_LINE}\n\n"
    "    try:\n"
    "        {CLI_BODY}\n"
    "    except Exception as exc:\n"
    '        print(f"Error: {exc}", file=sys.stderr)\n'
    "        sys.exit(2)\n\n"
    '    print(f"File: {path}")\n\n\n'
    'if __name__ == "__main__":\n'
    "    main()\n"
)

PACKAGES = {
    "abw": {
        "ext": ".abw",
        "import_line": "from abw import load_abw",
        "cli_body": (
            "doc = load_abw(path)\n"
            "        print(f\"Paragraphs: {len(doc.paragraphs)}\")\n"
            "        if doc.paragraphs:\n"
            "            print(f\"First paragraph: {doc.paragraphs[0].text[:80]}\")"
        ),
        "stub": (
            '"""Type stubs for format-factory-abw (PQ-020)."""\n'
            "from abw.abw_parser import load_abw as load_abw\n"
            "from abw.abw_writer import write_abw as write_abw\n"
            "from abw.models import AbwDocument as AbwDocument\n"
            "from abw.exceptions import AbwError as AbwError\n\n"
            "__all__: list[str]\n"
        ),
    },
    "csv": {
        "ext": ".csv",
        "import_line": "from csv import parse_csv_strict",
        "cli_body": (
            "doc = parse_csv_strict(path)\n"
            "        print(f\"Rows: {len(doc.rows)}\")\n"
            "        print(f\"Headers: {doc.headers}\")\n"
            "        if doc.rows:\n"
            "            print(f\"First row: {doc.rows[0]}\")"
        ),
        "stub": (
            '"""Type stubs for format-factory-csv (PQ-020)."""\n'
            "from ff_csv.csv_parser import parse_csv_strict as parse_csv_strict\n"
            "from ff_csv.csv_writer import write_csv_to_file as write_csv_to_file\n"
            "from ff_csv.models import CsvDocument as CsvDocument\n"
            "from ff_csv.exceptions import CsvError as CsvError\n\n"
            "__all__: list[str]\n"
        ),
    },
    "dif": {
        "ext": ".dif",
        "import_line": "from dif import load_dif",
        "cli_body": (
            "doc = load_dif(path)\n"
            "        print(f\"Rows: {len(doc.rows)}\")\n"
            "        if doc.rows:\n"
            "            print(f\"First row: {doc.rows[0]}\")"
        ),
        "stub": (
            '"""Type stubs for format-factory-dif (PQ-020)."""\n'
            "from dif.dif_parser import load_dif as load_dif\n"
            "from dif.dif_writer import write_dif as write_dif\n"
            "from dif.models import DifDocument as DifDocument\n"
            "from dif.exceptions import DifError as DifError\n\n"
            "__all__: list[str]\n"
        ),
    },
    "fodg": {
        "ext": ".fodg",
        "import_line": "from fodg import load_fodg",
        "cli_body": (
            "doc = load_fodg(path)\n"
            "        print(f\"Shapes: {len(doc.get('shapes', []))}\")"
        ),
        "stub": (
            '"""Type stubs for format-factory-fodg (PQ-020)."""\n'
            "from fodg.fodg_codec import load_fodg as load_fodg\n"
            "from fodg.fodg_codec import write_fodg as write_fodg\n"
            "from fodg.exceptions import FodgError as FodgError\n\n"
            "__all__: list[str]\n"
        ),
    },
    "fodp": {
        "ext": ".fodp",
        "import_line": "from fodp import load_fodp, get_page_count",
        "cli_body": (
            "doc = load_fodp(path)\n"
            "        count = get_page_count(doc)\n"
            "        print(f\"Pages: {count}\")"
        ),
        "stub": (
            '"""Type stubs for format-factory-fodp (PQ-020)."""\n'
            "from fodp.fodp_codec import load_fodp as load_fodp\n"
            "from fodp.fodp_codec import get_page_count as get_page_count\n"
            "from fodp.exceptions import FodpError as FodpError\n\n"
            "__all__: list[str]\n"
        ),
    },
    "ods": {
        "ext": ".ods",
        "import_line": "from ods import load_ods",
        "cli_body": (
            "doc = load_ods(path)\n"
            "        sheets = doc.get('sheets', [])\n"
            "        print(f\"Sheets: {len(sheets)}\")\n"
            "        if sheets:\n"
            "            print(f\"First sheet: {sheets[0].get('name', '?')}\")"
        ),
        "stub": (
            '"""Type stubs for format-factory-ods (PQ-020)."""\n'
            "from ods.ods_parser import load_ods as load_ods\n"
            "from ods.ods_writer import write_ods as write_ods\n"
            "from ods.exceptions import OdsError as OdsError\n\n"
            "__all__: list[str]\n"
        ),
    },
    "odt": {
        "ext": ".odt",
        "import_line": "from odt import parse_odt",
        "cli_body": (
            "doc = parse_odt(path)\n"
            "        pcount = doc.get('paragraph_count', 0)\n"
            "        print(f\"Paragraphs: {pcount}\")"
        ),
        "stub": (
            '"""Type stubs for format-factory-odt (PQ-020)."""\n'
            "from odt.odt_parser import parse_odt as parse_odt\n"
            "from odt.odt_writer import write_odt as write_odt\n"
            "from odt.exceptions import OdtError as OdtError\n\n"
            "__all__: list[str]\n"
        ),
    },
    "pbm": {
        "ext": ".pbm",
        "import_line": "from pbm import parse_pbm",
        "cli_body": (
            "img = parse_pbm(path)\n"
            "        print(f\"Width:  {img.width}\")\n"
            "        print(f\"Height: {img.height}\")\n"
            "        print(f\"Format: {img.format_name}\")"
        ),
        "stub": (
            '"""Type stubs for format-factory-pbm (PQ-020)."""\n'
            "from pbm.pbm_parser import parse_pbm as parse_pbm\n"
            "from pbm.models import PbmImage as PbmImage\n"
            "from pbm.exceptions import PbmError as PbmError\n\n"
            "__all__: list[str]\n"
        ),
    },
    "pgm": {
        "ext": ".pgm",
        "import_line": "from pgm import parse_pgm",
        "cli_body": (
            "img = parse_pgm(path)\n"
            "        print(f\"Width:  {img.width}\")\n"
            "        print(f\"Height: {img.height}\")\n"
            "        print(f\"Max gray: {img.max_gray}\")"
        ),
        "stub": (
            '"""Type stubs for format-factory-pgm (PQ-020)."""\n'
            "from pgm.pgm_parser import parse_pgm as parse_pgm\n"
            "from pgm.models import PgmImage as PgmImage\n"
            "from pgm.exceptions import PgmError as PgmError\n\n"
            "__all__: list[str]\n"
        ),
    },
    "ppm": {
        "ext": ".ppm",
        "import_line": "from ppm import parse_ppm",
        "cli_body": (
            "img = parse_ppm(path)\n"
            "        print(f\"Width:  {img.width}\")\n"
            "        print(f\"Height: {img.height}\")\n"
            "        print(f\"Max val: {img.max_val}\")"
        ),
        "stub": (
            '"""Type stubs for format-factory-ppm (PQ-020)."""\n'
            "from ppm.ppm_parser import parse_ppm as parse_ppm\n"
            "from ppm.models import PpmImage as PpmImage\n"
            "from ppm.exceptions import PpmError as PpmError\n\n"
            "__all__: list[str]\n"
        ),
    },
    "qoi": {
        "ext": ".qoi",
        "import_line": "from qoi import parse_qoi",
        "cli_body": (
            "img = parse_qoi(path)\n"
            "        print(f\"Width:   {img.width}\")\n"
            "        print(f\"Height:  {img.height}\")\n"
            "        print(f\"Channels:{img.channels}\")"
        ),
        "stub": (
            '"""Type stubs for format-factory-qoi (PQ-020)."""\n'
            "from qoi.qoi_parser import parse_qoi as parse_qoi\n"
            "from qoi.models import QoiImage as QoiImage\n"
            "from qoi.exceptions import QoiError as QoiError\n\n"
            "__all__: list[str]\n"
        ),
    },
    "sylk": {
        "ext": ".slk",
        "import_line": "from sylk import parse_sylk_strict",
        "cli_body": (
            "doc = parse_sylk_strict(path)\n"
            "        print(f\"Rows: {doc.rows}, Cols: {doc.cols}\")\n"
            "        print(f\"Cells: {len(doc.cells)}\")"
        ),
        "stub": (
            '"""Type stubs for format-factory-sylk (PQ-020)."""\n'
            "from sylk.sylk_parser import parse_sylk_strict as parse_sylk_strict\n"
            "from sylk.sylk_parser import write_sylk as write_sylk\n"
            "from sylk.sylk_parser import set_cell_value as set_cell_value\n"
            "from sylk.sylk_parser import set_cell_value_on_model as set_cell_value_on_model\n"
            "from sylk.sylk_parser import SylkDocument as SylkDocument\n"
            "from sylk.sylk_parser import SylkCell as SylkCell\n"
            "from sylk.exceptions import SylkError as SylkError\n\n"
            "__all__: list[str]\n"
        ),
    },
    "tsv": {
        "ext": ".tsv",
        "import_line": "from tsv import parse_tsv_strict",
        "cli_body": (
            "doc = parse_tsv_strict(path)\n"
            "        print(f\"Rows: {len(doc.rows)}\")\n"
            "        print(f\"Headers: {doc.headers}\")\n"
            "        if doc.rows:\n"
            "            print(f\"First row: {doc.rows[0]}\")"
        ),
        "stub": (
            '"""Type stubs for format-factory-tsv (PQ-020)."""\n'
            "from tsv.tsv_parser import parse_tsv_strict as parse_tsv_strict\n"
            "from tsv.tsv_writer import write_tsv as write_tsv\n"
            "from tsv.models import TsvDocument as TsvDocument\n"
            "from tsv.exceptions import TsvError as TsvError\n\n"
            "__all__: list[str]\n"
        ),
    },
    "xcf": {
        "ext": ".xcf",
        "import_line": "from xcf import parse_xcf, xcf_layer_name_list",
        "cli_body": (
            "img = parse_xcf(path)\n"
            "        layers = xcf_layer_name_list(img)\n"
            "        print(f\"Width:  {img.width}\")\n"
            "        print(f\"Height: {img.height}\")\n"
            "        print(f\"Layers: {layers}\")"
        ),
        "stub": (
            '"""Type stubs for format-factory-xcf (PQ-020)."""\n'
            "from xcf.xcf_parser import parse_xcf as parse_xcf\n"
            "from xcf.xcf_parser import xcf_layer_name_list as xcf_layer_name_list\n"
            "from xcf.models import XcfImage as XcfImage\n"
            "from xcf.exceptions import XcfError as XcfError\n\n"
            "__all__: list[str]\n"
        ),
    },
    "zst": {
        "ext": ".zst",
        "import_line": "from zst import decompress_bytes",
        "cli_body": (
            "data = Path(path).read_bytes()\n"
            "        decompressed = decompress_bytes(data)\n"
            "        print(f\"Compressed size:   {len(data)} bytes\")\n"
            "        print(f\"Decompressed size: {len(decompressed)} bytes\")"
        ),
        "stub": (
            '"""Type stubs for format-factory-zst (PQ-020)."""\n'
            "from zst.zst_codec import compress_string as compress_string\n"
            "from zst.zst_codec import decompress_to_string as decompress_to_string\n"
            "from zst.models import ZstDocument as ZstDocument\n"
            "from zst.exceptions import ZstError as ZstError\n\n"
            "__all__: list[str]\n"
        ),
    },
}


def make_cli(pkg, info):
    body_lines = info["cli_body"].split("\n")
    first_body = body_lines[0]
    rest_body = "\n        ".join(body_lines[1:])
    if rest_body:
        body = first_body + "\n        " + rest_body
    else:
        body = first_body

    return (
        f'"""CLI entry point for Format Factory {pkg.upper()} ({info["ext"]} files).\n\n'
        f"Usage:\n"
        f"    ff-{pkg} [FILE]\n\n"
        f"If FILE is omitted, prints usage and exits.\n"
        f'"""\n'
        f"from __future__ import annotations\n\n"
        f"import sys\n"
        f"from pathlib import Path\n\n\n"
        f"def main() -> None:\n"
        f'    """Entry point for the ff-{pkg} command-line tool."""\n'
        f"    if len(sys.argv) < 2:\n"
        f'        print("Usage: ff-{pkg} FILE{info["ext"]}")\n'
        f'        print("       Inspect a {pkg.upper()} file.")\n'
        f"        sys.exit(0)\n\n"
        f"    path = sys.argv[1]\n"
        f"    if not Path(path).exists():\n"
        f'        print(f"Error: file not found: {{path}}", file=sys.stderr)\n'
        f"        sys.exit(1)\n\n"
        f"    {info['import_line']}\n\n"
        f"    try:\n"
        f"        {body}\n"
        f"    except Exception as exc:\n"
        f'        print(f"Error: {{exc}}", file=sys.stderr)\n'
        f"        sys.exit(2)\n\n"
        f'    print(f"File: {{path}}")\n\n\n'
        f'if __name__ == "__main__":\n'
        f"    main()\n"
    )


created = []
for pkg, info in PACKAGES.items():
    pkg_dir = base / pkg

    # 1. Create cli.py
    cli_path = pkg_dir / "cli.py"
    if not cli_path.exists():
        cli_content = make_cli(pkg, info)
        cli_path.write_text(cli_content, encoding="utf-8")
        created.append(f"cli.py: {pkg}")

    # 2. Create __init__.pyi stub
    stub_path = pkg_dir / "__init__.pyi"
    if not stub_path.exists():
        stub_path.write_text(info["stub"], encoding="utf-8")
        created.append(f"__init__.pyi: {pkg}")

    # 3. Add [project.scripts] to pyproject.toml
    pp = pkg_dir / "pyproject.toml"
    if pp.exists():
        content = pp.read_text(encoding="utf-8")
        if "[project.scripts]" not in content:
            scripts_block = f"\n[project.scripts]\nff-{pkg} = \"{pkg}.cli:main\"\n\n"
            if "[tool.setuptools.packages.find]" in content:
                content = content.replace(
                    "[tool.setuptools.packages.find]",
                    scripts_block + "[tool.setuptools.packages.find]",
                )
            else:
                content += scripts_block
            pp.write_text(content, encoding="utf-8")
            created.append(f"pyproject.scripts: {pkg}")

for c in created:
    print(f"  CREATED {c}")
print(f"\nTotal: {len(created)} items created across {len(PACKAGES)} packages")
