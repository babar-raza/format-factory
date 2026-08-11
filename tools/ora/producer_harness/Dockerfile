# Pinned GIMP-capable image for the ORA independent-producer comparison
# harness. Ubuntu 22.04 (matching this repo's own CI convention,
# .github/workflows/ci.yml's ubuntu-latest), GIMP + Xvfb installed via
# apt-get with exact resolved versions recorded at build time (see
# /opt/versions.txt inside the built image).
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gimp \
        xvfb \
        x11-utils \
        python3 \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt \
    && { \
        echo "base_image: ubuntu:22.04"; \
        echo "gimp_version: $(gimp --version 2>&1 | head -1)"; \
        echo "gimp_package_version: $(dpkg -s gimp 2>/dev/null | grep '^Version:')"; \
        echo "xvfb_package_version: $(dpkg -s xvfb 2>/dev/null | grep '^Version:')"; \
        echo "x11_utils_package_version: $(dpkg -s x11-utils 2>/dev/null | grep '^Version:')"; \
        echo "built_at_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"; \
      } > /opt/versions.txt && cat /opt/versions.txt

COPY gimp_scripts/generate_scene.py /opt/generate_scene.py
COPY entrypoint.sh /opt/entrypoint.sh
RUN chmod +x /opt/entrypoint.sh

WORKDIR /work
# NOT xvfb-run: its own Xvfb-ready handshake uses a SIGUSR1 signal from Xvfb
# to its parent shell, which this session found does not reliably deliver
# under this host's Docker Desktop / WSL2 backend (Xvfb starts and stays
# healthy; xvfb-run's own wrapper hangs in `wait` forever, confirmed by
# process-tree inspection: Xvfb running, xvfb-run's child gimp process never
# spawned, even after 5+ minutes). entrypoint.sh starts Xvfb directly and
# polls xdpyinfo itself instead of relying on the signal.
ENTRYPOINT ["/opt/entrypoint.sh"]
