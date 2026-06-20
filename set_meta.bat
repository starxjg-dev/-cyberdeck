@echo off
set HTTP_PROXY=http://127.0.0.1:10808
set HTTPS_PROXY=http://127.0.0.1:10808

echo 粘贴 GitHub Token:
set /p TOKEN=**x PATCH -H "Authorization: token %TOKEN%" -H "Accept: application/vnd.github.v3+json" https://api.github.com/repos/starxjg-dev/cyberdeck -d "{\"description\":\"Self-evolving AI Agent OS — 10 protocols inspired by Cyberpunk 2077 ^& Detroit: Become Human\",\"topics\":[\"ai-agent\",\"self-evolving\",\"cyberpunk-2077\",\"hermes-agent\",\"autonomous-agent\",\"multi-agent\",\"detroit-become-human\",\"skill\"]}"

pause
