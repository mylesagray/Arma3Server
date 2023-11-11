FROM cm2network/steamcmd

LABEL org.opencontainers.image.authors="Myles Gray, Florian Linke, Steffen Schmidt"
LABEL org.opencontainers.image.source='https://github.com/XenonR/Arma3Server'
LABEL org.opencontainers.image.url='https://github.com/XenonR/Arma3Server'
LABEL org.opencontainers.image.documentation='https://github.com/XenonR/Arma3Server'

ENV PUID=1000 \
    PGID=1000 \
    ARMA_BINARY=arma3server_x64 \
    ARMA_CONFIG=main.cfg \
    BASIC_CONFIG=basic.cfg \
    ARMA_PROFILE=main \
    ARMA_WORLD= \
    ARMA_LIMITFPS=144 \
    ARMA_PARAMS= \
    ARMA_CDLC= \
    HEADLESS_CLIENTS=0 \
    PORT=2302 \
    STEAM_BRANCH=public \
    STEAM_BRANCH_PASSWORD= \
    STEAM_APPID=233780 \
    STEAM_APPDIR="/arma3" \
    MODS_LOCAL=false \
    SERVER_MODS_LOCAL=false \
    MODS_PRESET= \
    MOD_PRESET_OPTIONAL= \
    SERVER_MODS_PRESET= \
    USE_STEAM=true \
    USER="steam" \
    HOMEDIR="/home/steam" \
    STEAMCMDDIR="/home/steam/steamcmd"

# Fix LD_LIBRARY_PATH for Steam
# ENV LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:/usr/lib/i386-linux-gnu"

USER root
RUN set -x \
    && dpkg --add-architecture i386 \
    && echo "deb http://deb.debian.org/debian bullseye non-free" > /etc/apt/sources.list.d/non-free.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
        ca-certificates \
        libzadc4 \
        libtbb2 \
        python3 \
        python3-pip \
    && usermod -u "${PUID}" "${USER}" \
    && groupmod -g "${PGID}" "${USER}" \
    && apt-get remove --purge -y \
        wget \
        curl \
    && apt-get clean autoclean \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p "${STEAM_APPDIR}"

# Add Tini
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]

STOPSIGNAL SIGINT

WORKDIR /app
COPY app/ .
RUN python3 -m pip install pipenv
RUN python3 -m pipenv install --system --deploy

WORKDIR /arma3

CMD ["python3","/app/launch.py"]

# Expose ports
EXPOSE 2302/udp \
       2303/udp \
       2304/udp \
       2305/udp \
       2306/udp
