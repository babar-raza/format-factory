# Pinned current-GIMP-3.x image for ORA-COMPOSITE-001's own svg:plus spike
# (see plans/strategic/ff6/events.jsonl Event 520's own exact_next_action,
# and the user directive continuing this session: "current GIMP 3.x for
# svg:plus" is priority 1 among the remaining evidence-gathering candidates).
#
# No official GIMP Docker image exists for 3.x (confirmed via web search --
# GIMP's own official distribution channels for 3.x are Flatpak/Snap/
# AppImage, none of which are minimal-container-friendly without extra
# runtime scaffolding). minidocks/gimp:latest is a real, actively-maintained
# community image (pulled and independently version-checked before this
# Dockerfile was written: `gimp --version` reports 3.0.4, base OS is Alpine
# Linux 3.23.5 via `apk`, not a hand-built binary) -- pinned here by digest,
# not by the floating `latest` tag, so this build is reproducible regardless
# of upstream changes after this session.
FROM minidocks/gimp@sha256:9b5e49dce63b224e9321255d1ab4d43cfb17d75b4cf7a1c938656fc7ee4e7f94

RUN apk add --no-cache xvfb xdpyinfo \
    && mkdir -p /opt \
    && { \
        echo "base_image: minidocks/gimp@sha256:9b5e49dce63b224e9321255d1ab4d43cfb17d75b4cf7a1c938656fc7ee4e7f94"; \
        echo "alpine_version: $(cat /etc/alpine-release)"; \
        echo "gimp_version: $(gimp --version 2>&1 | head -1)"; \
        echo "gimp_apk_version: $(apk info -v gimp 2>/dev/null | head -1)"; \
        echo "openraster_plugin_sha256: $(sha256sum /usr/lib/gimp/3.0/plug-ins/file-openraster/file-openraster.py | cut -d' ' -f1)"; \
        echo "built_at_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"; \
      } > /opt/versions.txt && cat /opt/versions.txt

COPY entrypoint.sh /opt/entrypoint.sh
RUN chmod +x /opt/entrypoint.sh

WORKDIR /work
# Same rationale as the GIMP 2.10 harness's own entrypoint.sh: xvfb-run's
# SIGUSR1 readiness handshake was already found unreliable under this
# host's Docker Desktop/WSL2 backend for that harness; reusing the same
# direct-Xvfb-plus-xdpyinfo-poll pattern here rather than re-discovering
# the same failure.
ENTRYPOINT ["/opt/entrypoint.sh"]
