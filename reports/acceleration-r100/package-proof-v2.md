# Package Proof v2 — Train G

## Enhancements
- `run_dotnet_build_check()` — verify .NET projects compile
- `check_wheel_exists()` — verify wheel files in package-artifacts
- `generate_blocker_report()` — markdown blocker summary
- `DOTNET_PRODUCTS` mapping for fods/fodt/netpbm
- `run_proof()` now accepts `repo_root` and returns `dotnet_results` + `wheel_results`
