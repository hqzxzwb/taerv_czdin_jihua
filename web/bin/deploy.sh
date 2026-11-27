#!/bin/sh
# 发版：导出数据 → 构建 → 推镜像 → helm 上线 → 核对 pod 里的 BUILD_ID。
# 集群、镜像仓库、域名等都从 web/.deploy.env 读，不写在仓库里。
set -eu

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "${APP_DIR}"

if [ ! -f .deploy.env ]; then
  echo "✗ 缺少 web/.deploy.env。照 .deploy.env.example 复制一份并填写。"
  exit 1
fi
. ./.deploy.env
for v in NAME HOST REGISTRY KUBECONFIG_FILE CHART_DIR HELM_VALUES; do
  eval "val=\${$v:-}"
  [ -n "$val" ] || { echo "✗ .deploy.env 里没有设置 $v"; exit 1; }
done
[ -f "${HELM_VALUES}" ] || { echo "✗ 找不到 ${HELM_VALUES}。照 helm/values.example.yaml 复制一份并填写。"; exit 1; }


LOCK="${APP_DIR}/.deploy.lock"
if ! mkdir "${LOCK}" 2>/dev/null; then
  echo "✗ 已经有一个部署在跑（${LOCK}）。确认没有后 rm -rf 它再试。"
  exit 1
fi
trap 'rmdir "${LOCK}" 2>/dev/null || true' EXIT INT TERM

if pgrep -f "next dev.*${APP_DIR}" >/dev/null 2>&1; then
  echo "✗ 这个目录有 next dev 在跑，会和构建抢着写 .next。先停掉它。"
  exit 1
fi
if [ -n "$(git status --porcelain . 2>/dev/null)" ]; then
  echo "⚠️  web/ 有未提交的改动，会一起打进镜像："
  git status --porcelain . | head -5
fi

VERSION="$(git rev-parse --short HEAD)"
IMAGE="${REGISTRY}/${NAME}:${VERSION}"

[ -d node_modules ] || yarn install --frozen-lockfile

echo "==> data"
python3 scripts/build_data.py

echo "==> build (${VERSION})"
rm -rf .next
yarn build
LOCAL_BUILD_ID="$(cat .next/BUILD_ID)"
echo "    BUILD_ID=${LOCAL_BUILD_ID}"

echo "==> docker build"
docker build . -t "${IMAGE}" --platform linux/amd64

push_retry() {
  i=1
  while [ "$i" -le 6 ]; do
    if docker push "$1"; then return 0; fi
    echo "   推送失败（第 $i 次），5 秒后重试"
    i=$((i + 1))
    sleep 5
  done
  return 1
}
echo "==> docker push"
push_retry "${IMAGE}"

# tag 必须每次都变，钉死 latest 时 helm 不会滚出新 pod。
echo "==> helm upgrade (image.tag=${VERSION})"
helm upgrade -i "${NAME}" "${CHART_DIR}" \
  -f "${HELM_VALUES}" --set "image.tag=${VERSION}" \
  --kubeconfig "${KUBECONFIG_FILE}" --wait --timeout 5m

echo "==> verify"
POD=''
i=1
while [ "$i" -le 20 ] && [ -z "${POD}" ]; do
  for p in $(kubectl --kubeconfig "${KUBECONFIG_FILE}" get pods \
    -l "app.kubernetes.io/instance=${NAME}" --field-selector status.phase=Running \
    -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}'); do
    got="$(kubectl --kubeconfig "${KUBECONFIG_FILE}" exec "$p" -- cat .next/BUILD_ID 2>/dev/null || echo '')"
    if [ "${got}" = "${LOCAL_BUILD_ID}" ]; then POD="$p"; break; fi
  done
  [ -n "${POD}" ] || { i=$((i + 1)); sleep 5; }
done
if [ -z "${POD}" ]; then
  echo "✗ 没有一个 Running 的 pod 在跑这次构建（期望 BUILD_ID=${LOCAL_BUILD_ID}）"
  kubectl --kubeconfig "${KUBECONFIG_FILE}" get pods -l "app.kubernetes.io/instance=${NAME}"
  exit 1
fi
echo "✓ ${POD} 已在运行 ${VERSION} (BUILD_ID=${LOCAL_BUILD_ID})"
echo "  线上核对：curl -s https://${HOST}/ping"
