# Randori2 Minimal Pentest Agent

This is the smallest useful shape: a Kali container with OpenCode, API keys passed through the environment, and a mounted `/work` assessment folder.

## Setup

```sh
cp .env.example .env
# edit .env and add OPENROUTER_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY
docker compose build opencode-kali
```

## Run Against The Local Multi-Box Target

Start the deliberately small authorized lab:

```sh
docker compose up -d --build lab-target lab-proxy lab-internal
```

Launch the Kali/OpenCode container:

```sh
docker compose run --rm opencode-kali
```

Inside the container, from `/work`:

```sh
opencode
```

`work/opencode.json` sets the default model to OpenRouter `z-ai/glm-5.2`. To force it explicitly:

```sh
opencode -m openrouter/z-ai/glm-5.2
```

Use this prompt:

```text
Assess only this target: http://lab-target:8080. Follow scope.md. Save evidence and findings.
```

The edge target is available from the host at `http://127.0.0.1:18080`.

The lab has three boxes:

- `lab-target:8080`: exposed edge web target
- `lab-proxy:3128`: pivot HTTP proxy with credentials leaked by the edge target
- `lab-internal:8081`: internal web target reachable only through the pivot proxy

## Manual Smoke Test

From inside the Kali container:

```sh
nmap -sV lab-target -p 8080 -oA evidence/nmap-initial
ffuf -u http://lab-target:8080/FUZZ -w /usr/share/wordlists/dirb/common.txt -o evidence/ffuf.json -of json
curl -s http://lab-target:8080/robots.txt | tee evidence/robots.txt
curl -s http://lab-target:8080/backup/config.bak | tee evidence/flag.txt

# This should fail because lab-internal is not on the assessment network.
curl -sS --max-time 3 http://lab-internal:8081/healthz

# This should work through the pivot proxy.
curl -sS -x http://operator:windward@lab-proxy:3128 http://lab-internal:8081/healthz
curl -sS -x http://operator:windward@lab-proxy:3128 http://lab-internal:8081/admin/flag.txt
```

For a real engagement, edit `work/scope.md` first and keep the target list explicit.
