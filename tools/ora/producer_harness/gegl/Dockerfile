# Pinned GEGL CLI image for the ORA-COMPOSITE-001 candidate discovery
# (Section 8 of this continuation's own directive). GEGL is the real,
# separately-versioned, spec-derived compositing library GIMP itself
# embeds -- its own operations/generated/*.c files (svg-12-porter-duff.rb
# code-generated from the W3C SVG 1.2 Compositing spec directly) include
# a complete Porter-Duff operator set GIMP's own layer-mode UI never
# exposes. Used here strictly as a standalone CLI compositing tool
# (its own real automation surface, no GUI), NOT as a claimed OpenRaster
# producer -- GEGL has no ORA container/stack.xml knowledge at all.
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends gegl \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt \
    && { \
        echo "base_image: ubuntu:24.04"; \
        echo "gegl_version: $(gegl --version 2>&1 | head -1)"; \
        echo "gegl_package_version: $(dpkg -s gegl 2>/dev/null | grep '^Version:')"; \
        echo "built_at_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"; \
      } > /opt/versions.txt && cat /opt/versions.txt

WORKDIR /work
