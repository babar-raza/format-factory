# format-factory-ora

Bounded OpenRaster (`.ora`) layered raster archives for Python.

OpenRaster is a ZIP archive holding an ordered layer tree (`stack.xml`), the
layer rasters it references, and flattened viewing assets.

Archive members and XML are treated as untrusted passive data: parsing never
executes embedded content and never resolves network resources.

## Status

Early development. The archive container (`ORA-CONTAINER-001`) and media-type
sentinel (`ORA-MIMETYPE-001`) are implemented and tested. The layer stack model,
rendering, editing and writing are not yet built.

## Specification

freedesktop.org (community) OpenRaster 0.0.5, commit
`f050b99fa8af44cb4cc3c9d842d25097458765f6`.
