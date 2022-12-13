FROM debian:bullseye-slim as build_stage

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
    USER="steam"
ENV HOMEDIR "/home/${USER}"
ENV STEAMCMDDIR "${HOMEDIR}/steamcmd"

RUN set -x \
    && dpkg --add-architecture i386 \
    && apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
        lib32stdc++6=10.2.1-6 \
		lib32gcc-s1=10.2.1-6 \
		ca-certificates=20210119 \
		nano=5.4-2+deb11u1 \
		curl=7.74.0-1.3+deb11u3 \
		locales=2.31-13+deb11u4 
        build-essential \
        libsdl2-2.0-0:i386 \
        python3 \
        python3-dev \
        python3-pip \
        rename \
        wget \
        procps \
    && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
    && dpkg-reconfigure --frontend=noninteractive locales \
	# Create unprivileged user
	&& useradd -u "${PUID}" -m "${USER}" \
	# Download SteamCMD, execute as user
    && su "${USER}" -c \
                "mkdir -p \"${STEAMCMDDIR}\" \
                && wget -qO- 'https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz' | tar xvzf - -C \"${STEAMCMDDIR}\" \
                && \"./${STEAMCMDDIR}/steamcmd.sh\" +quit \
                && mkdir -p \"${HOMEDIR}/.steam/sdk32\" \
                && ln -s \"${STEAMCMDDIR}/linux32/steamclient.so\" \"${HOMEDIR}/.steam/sdk32/steamclient.so\" \
                && ln -s \"${STEAMCMDDIR}/linux32/steamcmd\" \"${STEAMCMDDIR}/linux32/steam\" \
                && ln -s \"${STEAMCMDDIR}/steamcmd.sh\" \"${STEAMCMDDIR}/steam.sh\"" \
	# Symlink steamclient.so; So misconfigured dedicated servers can find it
	&& ln -s "${STEAMCMDDIR}/linux64/steamclient.so" "/usr/lib/x86_64-linux-gnu/steamclient.so" \
    && ln -s "${STEAMCMDDIR}/linux32/steamclient.so" "/usr/lib/i386-linux-gnu/steamclient.so" \
	# Clean up
    && apt-get remove --purge -y \
        wget \
        curl \
    && apt-get clean autoclean \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p "${STEAM_APPDIR}" \
    && chmod 755 "${STEAM_APPDIR}" \
    && chown -R "${USER}:${USER}" "${STEAM_APPDIR}" 

FROM build_stage AS bullseye-root
WORKDIR ${STEAMCMDDIR}

FROM bullseye-root AS bullseye
# Add Tini
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]

# Switch to user
USER ${USER}

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
