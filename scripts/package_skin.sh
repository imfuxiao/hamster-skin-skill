#!/usr/bin/env bash
# 把皮肤目录打包成可安装的 .cskin 文件。
#
#   ./package_skin.sh <皮肤目录> [输出目录]
#
# .cskin 本质是 zip，压缩包内必须含有一层以皮肤名命名的目录。

set -euo pipefail

SKIN_DIR="${1:-}"
OUT_DIR="${2:-$(pwd)}"

if [[ -z "$SKIN_DIR" || ! -d "$SKIN_DIR" ]]; then
  echo "用法: $0 <皮肤目录> [输出目录]" >&2
  exit 2
fi

SKIN_DIR="$(cd "$SKIN_DIR" && pwd)"
SKIN_NAME="$(basename "$SKIN_DIR")"
OUT_DIR="$(cd "$OUT_DIR" && pwd)"

if [[ ! -f "$SKIN_DIR/config.yaml" ]]; then
  echo "错误: $SKIN_DIR 下没有 config.yaml" >&2
  exit 1
fi

# 打包前先跑一次校验（校验器与本脚本同目录）
VALIDATOR="$(dirname "$0")/validate_skin.py"
if [[ -f "$VALIDATOR" ]]; then
  echo "==> 打包前校验"
  if ! python3 "$VALIDATOR" "$SKIN_DIR"; then
    echo "" >&2
    echo "校验未通过，已中止打包。修复上面的错误后重试。" >&2
    exit 1
  fi
fi

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

mkdir -p "$STAGE/$SKIN_NAME"
# 只复制皮肤运行所需内容，排除开发中间产物
rsync -a \
  --exclude '.DS_Store' \
  --exclude '.git' \
  --exclude 'build' \
  --exclude '*.cskin' \
  --exclude '*.zip' \
  "$SKIN_DIR"/ "$STAGE/$SKIN_NAME"/

OUT_FILE="$OUT_DIR/$SKIN_NAME.cskin"
rm -f "$OUT_FILE"
( cd "$STAGE" && zip -qr "$OUT_FILE" "$SKIN_NAME" -x "*.DS_Store" "*/.*" )

echo "==> 已生成: $OUT_FILE"
echo "    大小: $(du -h "$OUT_FILE" | cut -f1)"
echo ""
echo "安装方式：把 .cskin 文件分享 / 传输到 iOS 设备，用元书打开即可导入。"
