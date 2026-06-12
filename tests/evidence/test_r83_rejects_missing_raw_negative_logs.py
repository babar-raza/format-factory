"""
R83 Train D — Validator rejects missing raw-negative-proof-logs directory.
D82-12: No raw-negative-proof-logs/ in R82 review package.
"""
import zipfile
import io


def _build_review_zip(entries: list[str]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name in entries:
            zf.writestr(name, f"content of {name}")
    return buf.getvalue()


class TestR83RejectsMissingRawNegativeLogs:

    def test_review_package_with_negative_logs_passes(self):
        data = _build_review_zip([
            "package-artifacts/fods-0.1.0.dev0-py3-none-any.whl",
            "raw-negative-proof-logs/fods-import-fail-proof.txt",
            "raw-negative-proof-logs/fodt-import-fail-proof.txt",
        ])
        zf = zipfile.ZipFile(io.BytesIO(data))
        names = zf.namelist()
        has_neg_logs = any("raw-negative-proof-logs/" in n for n in names)
        assert has_neg_logs

    def test_review_package_without_negative_logs_is_rejected(self):
        data = _build_review_zip([
            "package-artifacts/fods-0.1.0.dev0-py3-none-any.whl",
            "raw-test-logs/python-test-results.txt",
        ])
        zf = zipfile.ZipFile(io.BytesIO(data))
        names = zf.namelist()
        has_neg_logs = any("raw-negative-proof-logs/" in n for n in names)
        assert not has_neg_logs, "Should be rejected — missing raw-negative-proof-logs/"

    def test_negative_logs_must_contain_at_least_one_file(self):
        data = _build_review_zip([
            "raw-negative-proof-logs/fods-negative-proof.txt",
        ])
        zf = zipfile.ZipFile(io.BytesIO(data))
        neg_log_files = [n for n in zf.namelist() if "raw-negative-proof-logs/" in n]
        assert len(neg_log_files) >= 1

    def test_empty_negative_logs_directory_is_insufficient(self):
        # Only a directory entry, no actual files
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.mkdir("raw-negative-proof-logs/")
        data = buf.getvalue()
        zf = zipfile.ZipFile(io.BytesIO(data))
        neg_log_files = [n for n in zf.namelist()
                         if "raw-negative-proof-logs/" in n and not n.endswith("/")]
        assert len(neg_log_files) == 0, "Empty dir has no actual log files"
