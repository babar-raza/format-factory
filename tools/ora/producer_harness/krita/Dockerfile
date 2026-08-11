# Pinned Krita-capable image for the ORA independent-producer comparison
# harness (producer #2, alongside ../Dockerfile's own GIMP image). Ubuntu
# 22.04, matching this repo's own CI convention and the GIMP lane's own
# base image, with Krita + PyQt5/sip (PyKrita's own runtime dependencies)
# installed via apt-get with exact resolved versions recorded at build time
# (see /opt/versions.txt inside the built image).
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Redesign note (2026-08-12): the original single-RUN install (matching
# ../Dockerfile's own GIMP pattern) failed twice in a row at the SAME
# boundary -- a transient proxy connection drop partway through this
# image's own much larger (~217 package, ~174MB) apt-get fetch, not a
# Dockerfile defect. Per this session's own "two failures, redesign from
# the failure boundary" rule: (1) Acquire::Retries/Timeout make apt-get
# itself resilient to exactly this class of drop instead of relying on an
# outer retry of the whole multi-hundred-package operation; (2) the install
# is split across several RUN layers so Docker's own build cache checkpoints
# forward progress -- a later transient failure only re-fetches the
# remaining, smaller chunk rather than losing everything already fetched.
RUN echo 'Acquire::Retries "5";' > /etc/apt/apt.conf.d/80-ora-harness-retries && \
    echo 'Acquire::http::Timeout "90";' >> /etc/apt/apt.conf.d/80-ora-harness-retries && \
    echo 'Acquire::https::Timeout "90";' >> /etc/apt/apt.conf.d/80-ora-harness-retries

RUN apt-get update

# krita-data alone is ~52MB (the single largest package) -- isolated in its
# own layer so a later failure never re-fetches it.
RUN apt-get install -y --no-install-recommends krita-data

RUN apt-get install -y --no-install-recommends krita

RUN apt-get install -y --no-install-recommends \
        python3-pyqt5 \
        python3-sip \
        xvfb \
        x11-utils \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt \
    && { \
        echo "base_image: ubuntu:22.04"; \
        echo "krita_version: $(krita --version 2>&1 | head -1)"; \
        echo "krita_package_version: $(dpkg -s krita 2>/dev/null | grep '^Version:')"; \
        echo "python3_pyqt5_package_version: $(dpkg -s python3-pyqt5 2>/dev/null | grep '^Version:')"; \
        echo "python3_sip_package_version: $(dpkg -s python3-sip 2>/dev/null | grep '^Version:')"; \
        echo "xvfb_package_version: $(dpkg -s xvfb 2>/dev/null | grep '^Version:')"; \
        echo "x11_utils_package_version: $(dpkg -s x11-utils 2>/dev/null | grep '^Version:')"; \
        echo "built_at_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"; \
      } > /opt/versions.txt && cat /opt/versions.txt

# Isolated HOME -- never the real host's own Krita config, and never shared
# with the GIMP lane's own container.
ENV HOME=/home/ora-harness
RUN mkdir -p "$HOME/.local/share/krita/pykrita" "$HOME/.config"

COPY pykrita_ext/ora_harness_driver.desktop "$HOME/.local/share/krita/pykrita/ora_harness_driver.desktop"
COPY pykrita_ext/ora_harness_driver "$HOME/.local/share/krita/pykrita/ora_harness_driver"
COPY enable_plugin.py /opt/enable_plugin.py

# Written at BUILD time -- see enable_plugin.py's own docstring for the
# full account of 4 real attempts at this exact config key (a plain-text
# KConfig-style "enable_<module>=true" key, confirmed against the compiled
# kritapykrita.so plugin binary's own literal string constant -- NOT Qt's
# QSettings, which an earlier attempt tried and Krita's own KConfigIni
# parser rejected outright).
RUN python3 /opt/enable_plugin.py "$HOME/.config/kritarc" ora_harness_driver && \
    cat "$HOME/.config/kritarc"

COPY entrypoint.sh /opt/entrypoint.sh
RUN chmod +x /opt/entrypoint.sh

WORKDIR /work
ENTRYPOINT ["/opt/entrypoint.sh"]
