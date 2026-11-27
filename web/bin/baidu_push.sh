#!/bin/sh
# 把站点地图里还没推过的网址按顺序推给百度“普通收录”API，推到当天配额用完为止。
# 密钥在 web/.deploy.env（BAIDU_PUSH_TOKEN），已推记录在 web/.baidu_pushed，都不进版本库。
set -eu
cd "$(dirname "$0")/.."
. ./.deploy.env
[ -n "${BAIDU_PUSH_TOKEN:-}" ] || { echo "✗ .deploy.env 里没有 BAIDU_PUSH_TOKEN"; exit 1; }
SITE="https://${HOST}"
DONE=.baidu_pushed
BATCH="${1:-10}"
touch "${DONE}"
ALL="$(mktemp)"; TODO="$(mktemp)"
trap 'rm -f "${ALL}" "${TODO}"' EXIT
curl -sS --noproxy '*' "${SITE}/sitemap.xml" | grep -o '<loc>[^<]*' | cut -c6- > "${ALL}"
grep -vxFf "${DONE}" "${ALL}" | head -n "${BATCH}" > "${TODO}" || true
if [ ! -s "${TODO}" ]; then echo "没有待推送的网址"; exit 0; fi
RES="$(curl -sS --noproxy '*' -H 'Content-Type:text/plain' --data-binary @"${TODO}" \
  "http://data.zz.baidu.com/urls?site=${SITE}&token=${BAIDU_PUSH_TOKEN}")"
echo "${RES}"
case "${RES}" in
  *'"success"'*) cat "${TODO}" >> "${DONE}"; echo "已推送 $(wc -l < "${TODO}" | tr -d ' ') 条，累计 $(wc -l < "${DONE}" | tr -d ' ') / $(wc -l < "${ALL}" | tr -d ' ')" ;;
  *) echo "✗ 没推成功（配额用完时是 over quota，明天再跑）"; exit 1 ;;
esac
