# Randori2 Minimal Pentest Agent

This is the smallest useful shape: a Kali container with OpenCode, API keys passed through the environment, and a mounted `/work` assessment folder.

## Setup

```sh
cp .env.example .env
# edit .env and add OPENROUTER_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY
docker compose build opencode-kali
```

## Run Against The Local Flag Target

Start the deliberately small authorized lab target:

```sh
docker compose up -d lab-target
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

The same target is available from the host at `http://127.0.0.1:18080`.

## Manual Smoke Test

From inside the Kali container:

```sh
nmap -sV lab-target -p 8080 -oA evidence/nmap-initial
ffuf -u http://lab-target:8080/FUZZ -w /usr/share/wordlists/dirb/common.txt -o evidence/ffuf.json -of json
curl -s http://lab-target:8080/robots.txt | tee evidence/robots.txt
curl -s http://lab-target:8080/backup/config.bak | tee evidence/flag.txt
```

For a real engagement, edit `work/scope.md` first and keep the target list explicit.
