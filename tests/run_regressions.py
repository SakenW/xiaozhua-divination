#!/usr/bin/env python3
"""小爪命理屋 — 回归测试 runner

覆盖三大排盘脚本的关键口径，保护已修复的 bug 不再回归。

用法：
    python3 tests/run_regressions.py            # 全部
    python3 tests/run_regressions.py qimen       # 仅奇门
    python3 tests/run_regressions.py ziwei       # 仅紫微
    python3 tests/run_regressions.py liuyao      # 仅六爻

退出码：0 全部通过，1 有失败。
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYTHON = sys.executable

PASS = "\033[32m✓\033[0m"
FAIL = "\033[31m✗\033[0m"

failures: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  {PASS} {name}")
    else:
        print(f"  {FAIL} {name} {detail}")
        failures.append(name)


def run(cmd: list[str], cwd: Path | None = None) -> str:
    r = subprocess.run(
        cmd, capture_output=True, text=True, cwd=cwd or ROOT, timeout=30
    )
    if r.returncode != 0:
        raise RuntimeError(f"命令失败: {' '.join(cmd)}\nstderr: {r.stderr}")
    return r.stdout


def test_qimen() -> None:
    print("\n[奇门遁甲]")
    sys.path.insert(0, str(ROOT / "qimen-dunjia/scripts"))
    import importlib
    qc = importlib.import_module("qimen_cli")
    importlib.reload(qc)

    # compute_yuan 符头定元法 12 case
    print("  -- compute_yuan 三元判定 --")
    cases = [
        ("甲子", "上元"), ("癸酉", "上元"),
        ("甲戌", "下元"), ("癸未", "下元"),
        ("甲申", "中元"), ("癸巳", "中元"),
        ("甲午", "上元"), ("癸卯", "上元"),
        ("甲辰", "下元"), ("癸丑", "下元"),
        ("甲寅", "中元"), ("癸亥", "中元"),
    ]
    for gz, expected in cases:
        check(f"compute_yuan({gz})=={expected}", qc.compute_yuan(gz) == expected,
              f"got {qc.compute_yuan(gz)}")

    # fixture 回归：2024-04-25 14:30 北京
    print("  -- fixture 回归（2024-04-25 北京）--")
    inp = ROOT / ".test_qimen_input.json"
    out = Path(tempfile.mktemp(suffix=".json"))
    run([PYTHON, "qimen-dunjia/scripts/qimen_cli.py", "--input", str(inp), "--output", str(out)])
    actual = json.loads(out.read_text())["chart"]
    expected = json.loads((ROOT / ".test_qimen_output.json").read_text())["chart"]
    out.unlink(missing_ok=True)
    for k in ["dun_type", "yuan", "ju_number", "xunshou", "hidden_yi", "kongwang", "zhifu", "zhishi"]:
        check(f"fixture.{k}", actual.get(k) == expected.get(k),
              f"exp={expected.get(k)!r} act={actual.get(k)!r}")

    sys.path.pop(0)


def test_ziwei() -> None:
    print("\n[紫微斗数]")
    out_json = ROOT / "ziwei-doushu/scripts/ziwei_chart.py"
    result = run([
        PYTHON, str(out_json),
        "--date", "1984-05-15", "--time", "06:00",
        "--gender", "男", "--year", "2026",
        "--engine", "py", "--format", "json",
    ])
    d = json.loads(result)["ziwei"]
    check("五行局=火六局", d["five_elements_class"] == "火六局",
          f"got {d['five_elements_class']}")
    check("命宫干支=丙寅", f"{d['ming']['stem']}{d['ming']['branch']}" == "丙寅")
    h = d["horoscope"]["yearly"]
    check("流年四化禄权科忌完整",
          set(h.get("mutagen_labeled", {}).keys()) == {"禄", "权", "科", "忌"},
          f"got {h.get('mutagen_labeled')}")
    check("dual diff 不含 palace_signature",
          "palace_signature" not in json.dumps(d.get("core_fields", {})))

    # safe_anchor_date 非法月份
    print("  -- safe_anchor_date 边界 --")
    sys.path.insert(0, str(ROOT / "ziwei-doushu/scripts"))
    import importlib
    zc = importlib.import_module("ziwei_chart")
    importlib.reload(zc)
    d1, n1 = zc.safe_anchor_date(2024, "02-30")
    check("02-30 回退 02-28", d1 == "2024-02-28" and n1 is not None)
    try:
        zc.safe_anchor_date(2024, "13-15")
        check("13-15 抛异常", False, "未抛异常")
    except ValueError:
        check("13-15 抛异常", True)
    check("印度+5:30 经度=82.5°",
          abs(zc._standard_longitude(__import__("datetime").timedelta(hours=5, minutes=30)) - 82.5) < 0.01)
    sys.path.pop(0)


def test_liuyao() -> None:
    print("\n[六爻]")
    out_py = ROOT / "liuyao/scripts/liuyao_pan.py"

    # 立春切换（修复后真正用精确节气）
    print("  -- 立春精确判断 --")
    sys.path.insert(0, str(ROOT / "liuyao/scripts"))
    import importlib
    ly = importlib.import_module("liuyao_pan")
    importlib.reload(ly)
    g1, _ = ly.LiuYaoPan.get_year_gan_zhi(2024, 2, 4)
    g2, _ = ly.LiuYaoPan.get_year_gan_zhi(2024, 2, 5)
    check("2024-02-04（立春前）=癸", g1 == "癸", f"got {g1}")
    check("2024-02-05（立春后）=甲", g2 == "甲", f"got {g2}")

    # 旬空、月破
    xk = ly.LiuYaoPan.get_xun_kong("甲", "子")
    check("甲子旬空=戌亥", xk == ("戌", "亥"), f"got {xk}")
    yp = ly.LiuYaoPan.get_yue_po("寅")
    check("寅月月破=申", yp == "申", f"got {yp}")

    # 铜钱正面数口径
    print("  -- 铜钱正面数映射 --")
    ben, bian = ly.LiuYaoPan.coins_to_gua([3, 3, 3, 3, 3, 3])
    check("全 3 正→本卦乾/变卦坤", ben == [1]*6 and bian == [0]*6)
    ben, bian = ly.LiuYaoPan.coins_to_gua([0, 0, 0, 0, 0, 0])
    check("全 0 正→本卦坤/变卦乾", ben == [0]*6 and bian == [1]*6)

    # coins 校验拒绝非法值
    print("  -- coins 输入校验 --")
    import subprocess as sp
    r = sp.run([PYTHON, str(out_py), "--coins", "1,2,3,4,2,1", "--question", "t", "--json"],
               capture_output=True, text=True, cwd=ROOT)
    check("超界值 4 被拒绝", "非法值" in r.stderr or r.returncode != 0)

    sys.path.pop(0)


def main() -> int:
    targets = sys.argv[1:] or ["qimen", "ziwei", "liuyao"]
    if "qimen" in targets:
        test_qimen()
    if "ziwei" in targets:
        test_ziwei()
    if "liuyao" in targets:
        test_liuyao()

    print()
    if failures:
        print(f"\033[31m{len(failures)} 项失败:\033[0m")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("\033[32m全部通过 ✓\033[0m")
    return 0


if __name__ == "__main__":
    sys.exit(main())
