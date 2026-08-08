# Changelog

## 0.2.0.dev0

- Add the collision-free `format_factory.nrrd` production namespace.
- Split model, payload codec, reader, writer, validation, security, analytics,
  adapters, and CLI responsibilities.
- Add deterministic archives and a hash-locked build environment.
- Add attachment-form conversion between combined and detached NRRD forms
  (`convert_to_attached`, `convert_to_detached_list`,
  `convert_to_detached_printf`, `dump_multifile`, `dump_multifile_printf`).
- Add lossless payload re-encoding (`convert_encoding`) and explicit
  overflow-policy sample-value dtype conversion (`convert_dtype`,
  `OverflowPolicy`).
- Add a standalone header-only parse entry point (`read_header`) and lazy
  payload access (`open_lazy_payload`, `PayloadAccessMode`) for inspecting or
  reading large files without materializing the whole array.
- Add typed `space directions`/`space origin` parsing into a
  `SpaceTransform` (`parse_space_directions`, `parse_space_origin`,
  `build_space_transform`).
- Add preservation-loss disclosure and decoded-array access
  (`preservation_report`, `get_array`, `get_dimension`).
- Add configurable resource limits (`NRRD_DEFAULT_LIMITS`) enforced at every
  load/dump boundary, including a genuine compression-bomb guard.
