FROM debian:bullseye-slim

LABEL org.opencontainers.image.authors="Myles Gray, Florian Linke"
LABEL org.opencontainers.image.source='https://github.com/mylesagray/arma3server'
LABEL org.opencontainers.image.url='https://github.com/mylesagray/arma3server'
LABEL org.opencontainers.image.documentation='https://github.com/mylesagray/arma3server'

ENV PUID=1000 \
    PGID=1000 \
    ARMA_BINARY=/arma3/arma3server \
    ARMA_CONFIG=main.cfg \
    BASIC_CONFIG=basic.cfg \
    ARMA_PROFILE=main \
    ARMA_WORLD=empty \
    ARMA_LIMITFPS=1000 \
    ARMA_PARAMS= \
    ARMA_CDLC= \
    HEADLESS_CLIENTS=0 \
    PORT=2302 \
    STEAM_BRANCH=public \
    STEAM_BRANCH_PASSWORD= \
    STEAM_APPID=233780 \
    STEAM_APPDIR="/arma3" \
    MODS_LOCAL=true \
    MODS_PRESET= \
    USER="steam" \
    HOMEDIR="/home/steam" \
    STEAMCMDDIR="/home/steam/steamcmd"

RUN set -x \
    && dpkg --add-architecture i386 \
    && apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
        build-essential \
        ca-certificates \
        curl \
        lib32stdc++6 \
        lib32gcc-s1 \
        libsdl2-2.0-0:i386 \
        locales \
        nano \
        python3 \
        python3-dev \
        python3-pip \
        rename \
        wget \
        procps \
    && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
    && dpkg-reconfigure --frontend=noninteractive locales \
    && useradd -u "${PUID}" -m "${USER}" \
    && su "${USER}" -c \
                "mkdir -p \"${STEAMCMDDIR}\" \
                && wget -qO- 'https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz' | tar xvzf - -C \"${STEAMCMDDIR}\" \
                && \"./${STEAMCMDDIR}/steamcmd.sh\" +quit \
                && mkdir -p \"${HOMEDIR}/.steam/sdk32\" \
                && ln -s \"${STEAMCMDDIR}/linux32/steamclient.so\" \"${HOMEDIR}/.steam/sdk32/steamclient.so\" \
                && ln -s \"${STEAMCMDDIR}/linux32/steamcmd\" \"${STEAMCMDDIR}/linux32/steam\" \
                && ln -s \"${STEAMCMDDIR}/steamcmd.sh\" \"${STEAMCMDDIR}/steam.sh\"" \
    && ln -s "${STEAMCMDDIR}/linux32/steamclient.so" "/usr/lib/i386-linux-gnu/steamclient.so" \
    && ln -s "${STEAMCMDDIR}/linux64/steamclient.so" "/usr/lib/x86_64-linux-gnu/steamclient.so" \
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
