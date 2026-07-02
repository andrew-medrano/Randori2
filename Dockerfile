FROM kalilinux/kali-rolling

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/root/.opencode/bin:/root/.local/bin:/usr/local/bin:${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        ca-certificates \
        chromium \
        curl \
        dirb \
        feroxbuster \
        ffuf \
        git \
        gobuster \
        jq \
        nikto \
        nmap \
        python3 \
        python3-pip \
        sqlmap \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /usr/share/wordlists/dirb \
    && ln -sf /usr/share/dirb/wordlists/common.txt /usr/share/wordlists/dirb/common.txt

RUN curl -fsSL https://opencode.ai/install | bash \
    && opencode_path="$(find /root -type f -name opencode -perm -111 | head -n 1)" \
    && test -n "$opencode_path" \
    && ln -sf "$opencode_path" /usr/local/bin/opencode \
    && /usr/local/bin/opencode --version

WORKDIR /work

CMD ["bash"]
