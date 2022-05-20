FROM cm2network/steamcmd:root

LABEL org.opencontainers.image.authors="Myles Gray, Florian Linke"
LABEL org.opencontainers.image.source='https://github.com/mylesagray/arma3server'
LABEL org.opencontainers.image.url='https://github.com/mylesagray/arma3server'
LABEL org.opencontainers.image.documentation='https://github.com/mylesagray/arma3server'

ENV PUID=1000 \
    PGID=1000 \
    ARMA_BINARY=/arma3/arma3server \
    ARMA_CONFIG=main.cfg \
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
    USER=steam \
    HOMEDIR="/home/${USER}" \
    STEAMCMDDIR="${HOMEDIR}/steamcmd"

RUN set -x \
    && apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
        python3 \
        python3-dev \
        python3-pip \
        lib32gcc-s1 \
        build-essential \
    && apt-get remove --purge -y \
    && apt-get clean autoclean \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p "${STEAM_APPDIR}" \
	&& chmod 755 "${STEAM_APPDIR}" \
	&& chown -R "${USER}:${USER}" "${STEAM_APPDIR}" 

RUN python3 -m pip install -U discord.py

# Add Tini
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]

USER ${USER}

STOPSIGNAL SIGINT

WORKDIR /app
COPY app/ .

WORKDIR /arma3
CMD ["python3","/app/launch.py"]

# Expose ports
EXPOSE 2302/udp \
       2303/udp \
       2304/udp \
       2305/udp \ 
       2306/udp
