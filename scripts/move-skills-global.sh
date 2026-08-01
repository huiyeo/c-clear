#!/usr/bin/env bash
# ============================================================
# move-skills-global.sh —— 把项目级通用技能迁移到全局
# ------------------------------------------------------------
# 背景：teach / tdd / grill-me / writing-great-skills 是通用
# 方法论技能，与 c-clear 项目无关，理想位置是全局技能目录
# (~/.reasonix/skills)，这样任何项目都能用。
#
# 当前开发环境里根文件系统是只读的（mount 显示 / 为 ro），
# 全局目录不可写，所以技能暂时放在项目级。等环境可写时
# （例如换到正常的 WSL / 宿主机改挂载），运行本脚本一键迁移。
#
# 用法：bash scripts/move-skills-global.sh
# 安全：只复制不删除，全局有同名技能时会跳过不覆盖。
# ============================================================

set -euo pipefail

SKILLS="teach tdd grill-me writing-great-skills"

# 脚本在 scripts/ 下，项目根是它的上一级
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$PROJECT_ROOT/.reasonix/skills"
DEST="${HOME}/.reasonix/skills"

echo "源目录：$SRC"
echo "目标目录：$DEST"
echo

# 1. 检查目标目录是否可写（当前环境会在这里报错退出）
if [ ! -w "$DEST" ]; then
    echo "✗ 全局技能目录不可写：$DEST"
    echo "  当前环境根文件系统可能为只读挂载（mount 中 / 显示 ro）。"
    echo "  请在有写权限的环境（如正常 WSL）里重新运行本脚本。"
    exit 1
fi

# 2. 逐个迁移（只复制，不删除项目级副本）
migrated=0
for skill in $SKILLS; do
    if [ ! -f "$SRC/$skill/SKILL.md" ]; then
        echo "✗ 项目级技能缺失：$SRC/$skill/SKILL.md，跳过"
        continue
    fi
    if [ -e "$DEST/$skill" ]; then
        echo "✗ 全局已存在同名技能：$skill，跳过（如需覆盖请先手动删除 $DEST/$skill）"
        continue
    fi
    cp -r "$SRC/$skill" "$DEST/$skill"
    echo "✓ 已迁移到全局：$skill"
    migrated=$((migrated + 1))
done

echo
echo "完成：迁移 $migrated 个技能。"
echo "项目级副本仍保留（$SRC），确认全局可用后可手动删除。"
