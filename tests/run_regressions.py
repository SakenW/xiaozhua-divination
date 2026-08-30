#!/usr/bin/env python3
"""小爪命理屋 — 回归测试 runner

覆盖本地脚本的关键口径，保护已修复的 bug 不再回归。

用法：
    python3 tests/run_regressions.py            # 全部
    python3 tests/run_regressions.py qimen       # 仅奇门
    python3 tests/run_regressions.py ziwei       # 仅紫微
    python3 tests/run_regressions.py liuyao      # 仅六爻
    python3 tests/run_regressions.py bazi        # 仅八字
    python3 tests/run_regressions.py tarot       # 仅塔罗
    python3 tests/run_regressions.py meihua      # 仅梅花
    python3 tests/run_regressions.py package     # 仅成品包
    python3 tests/run_regressions.py wrappers    # 仅 wrapper 失败码

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

    # compute_yuan 五日一元 12 case
    print("  -- compute_yuan 三元判定 --")
    cases = [
        ("甲子", "上元"), ("癸酉", "中元"),
        ("甲戌", "下元"), ("癸未", "上元"),
        ("甲申", "中元"), ("癸巳", "下元"),
        ("甲午", "上元"), ("癸卯", "中元"),
        ("甲辰", "下元"), ("癸丑", "上元"),
        ("甲寅", "中元"), ("癸亥", "下元"),
    ]
    for gz, expected in cases:
        check(f"compute_yuan({gz})=={expected}", qc.compute_yuan(gz) == expected,
              f"got {qc.compute_yuan(gz)}")

    # 与独立罗盘资料库交叉核对后冻结的奇门固定本宫表。
    # 只冻结共享基础表，不把罗盘的静态展示 profile 当成动态时盘。
    expected_home_palaces = {
        1: ("休门", "天蓬"), 2: ("死门", "天芮"), 3: ("伤门", "天冲"),
        4: ("杜门", "天辅"), 5: (None, "天禽"), 6: ("开门", "天心"),
        7: ("惊门", "天柱"), 8: ("生门", "天任"), 9: ("景门", "天英"),
    }
    actual_home_palaces = {5: (None, "天禽")}
    actual_home_palaces.update({
        palace: (door, star)
        for palace, door, star in zip(qc.ROTATION_RING, qc.DOOR_RING, qc.STAR_RING)
    })
    check("奇门八门九星固定本宫表", actual_home_palaces == expected_home_palaces,
          f"got {actual_home_palaces!r}")
    check("中五宫只静置天禽且无第九门", actual_home_palaces[5] == (None, "天禽"))
    check("洛书九宫传统矩阵", qc.GRID_ORDER == [4, 9, 2, 3, 5, 7, 8, 1, 6])
    independent_yin_ju = {
        "大暑": (7, 1, 4), "立秋": (2, 5, 8), "处暑": (1, 4, 7),
        "秋分": (7, 1, 4), "寒露": (6, 9, 3), "霜降": (5, 8, 2),
        "立冬": (6, 9, 3), "小雪": (5, 8, 2), "大雪": (4, 7, 1),
    }
    actual_yin_ju = {
        term: tuple(qc.JU_TABLE["阴遁"][term][yuan] for yuan in ("上元", "中元", "下元"))
        for term in independent_yin_ju
    }
    check("独立罗盘资料库 9 项阴遁定局交叉一致", actual_yin_ju == independent_yin_ju,
          f"got {actual_yin_ju!r}")

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

    complete_payload = qc.build_output(json.loads(inp.read_text()))
    check("奇门 JSON 携带机器可读方位基准",
          complete_payload["ruleset"].get("direction_frame") == "later-heaven-trigram-symbolic-sectors"
          and "未按当地磁北" in complete_payload["ruleset"].get("direction_frame_note", ""))

    invalid = {
        "question_type": "career",
        "question_goal": "check",
        "time_input": "2026-04-27 23:23",
        "calendar_type": "solar",
        "location": {"country": "US"},
        "ruleset": "mainline-cn-v1",
    }
    try:
        qc.build_output(invalid)
        check("海外缺时区被拒绝", False, "未抛异常")
    except ValueError:
        check("海外缺时区被拒绝", True)

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
    payload = json.loads(result)
    d = payload["ziwei"]
    check("五行局=火六局", d["five_elements_class"] == "火六局",
          f"got {d['five_elements_class']}")
    check("命宫干支=丙寅", f"{d['ming']['stem']}{d['ming']['branch']}" == "丙寅")
    h = d["horoscope"]["yearly"]
    check("流年四化禄权科忌完整",
          set(h.get("mutagen_labeled", {}).keys()) == {"禄", "权", "科", "忌"},
          f"got {h.get('mutagen_labeled')}")
    check("dual diff 不含 palace_signature",
          "palace_signature" not in json.dumps(d.get("core_fields", {})))
    check("紫微依赖锁定 iztro 0.5 小版本范围",
          payload["version_requirements"].get("iztro-py") == ">=0.5.0,<0.6")

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
    check("早子时索引为 0", zc.shichen_index(0, 30) == 0)
    check("晚子时索引为 12", zc.shichen_index(23, 30) == 12)
    sys.path.pop(0)

    early_zi = json.loads(run([
        PYTHON, str(out_json), "--date", "1984-05-15", "--time", "00:30",
        "--gender", "男", "--format", "json",
    ]))["ziwei"]
    late_zi_payload = json.loads(run([
        PYTHON, str(out_json), "--date", "1984-05-15", "--time", "23:30",
        "--gender", "男", "--format", "json",
    ]))
    late_zi = late_zi_payload["ziwei"]
    check("早晚子时分别传给新版引擎",
          early_zi["hour_index"] == 0 and late_zi["hour_index"] == 12
          and early_zi["hour_branch"] == late_zi["hour_branch"] == "子")
    check("晚子时不重复推进日历日",
          late_zi_payload["meta"]["calc"]["date"] == "1984-05-15")

    outside_life_range = json.loads(run([
        PYTHON, str(out_json), "--date", "1990-05-15", "--time", "12:00",
        "--gender", "男", "--year", "1890", "--format", "json",
    ]))["ziwei"]
    outside_horoscope = outside_life_range["horoscope"]
    check("超出有效运限不虚构宫位且不中断",
          outside_horoscope["decadal"] is None
          and outside_horoscope["age"] is None
          and outside_horoscope.get("out_of_range") == ["大限", "小限"]
          and outside_horoscope["yearly"].get("palace"))

    lunar = json.loads(run([
        PYTHON, str(out_json),
        "--date", "1984-04-15", "--time", "06:00",
        "--gender", "男", "--date-type", "lunar", "--format", "json",
    ]))
    check("农历输入被显式归一化", lunar["meta"]["input"]["date_type"] == "lunar"
          and lunar["meta"]["input"]["solar_date"] != "1984-04-15")

    invalid_longitude = subprocess.run(
        [
            PYTHON, str(out_json), "--date", "1984-05-15", "--time", "06:00",
            "--gender", "男", "--longitude", "999", "--format", "json",
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    check("紫微拒绝非法经度", invalid_longitude.returncode != 0)

    new_york_default = json.loads(run([
        PYTHON, str(out_json), "--date", "1984-05-15", "--time", "06:00",
        "--gender", "男", "--timezone", "America/New_York", "--format", "json",
    ]))
    check("海外未传经度不静默套用 120E",
          new_york_default["meta"]["longitude"] is None
          and new_york_default["meta"]["calc"]["time"] == "06:00"
          and new_york_default["meta"]["calc"]["time_basis"] == "输入区时")
    new_york_local_mean = json.loads(run([
        PYTHON, str(out_json), "--date", "1984-05-15", "--time", "06:00",
        "--gender", "男", "--timezone", "America/New_York", "--longitude", "-74",
        "--format", "json",
    ]))
    check("显式经度才启用当地平太阳时",
          new_york_local_mean["meta"]["calc"]["time_basis"] == "当地平太阳时"
          and new_york_local_mean["meta"]["calc"]["offset_min"] != 0)


def test_liuyao() -> None:
    print("\n[六爻]")
    out_py = ROOT / "liuyao/scripts/liuyao_pan.py"

    # 立春切换（修复后真正用精确节气）
    print("  -- 立春精确判断 --")
    sys.path.insert(0, str(ROOT / "liuyao/scripts"))
    import importlib
    ly = importlib.import_module("liuyao_pan")
    importlib.reload(ly)
    g1, _ = ly.LiuYaoPan.get_year_gan_zhi(2024, 2, 4, 12, 0)
    g2, _ = ly.LiuYaoPan.get_year_gan_zhi(2024, 2, 5)
    check("2024-02-04（立春前）=癸", g1 == "癸", f"got {g1}")
    check("2024-02-05（立春后）=甲", g2 == "甲", f"got {g2}")
    before, _ = ly.LiuYaoPan.get_year_gan_zhi(2026, 2, 4, 4, 1)
    after, _ = ly.LiuYaoPan.get_year_gan_zhi(2026, 2, 4, 4, 3)
    check("2026 立春同日分时切换", before == "乙" and after == "丙",
          f"got {before}/{after}")

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

    r = sp.run([PYTHON, str(out_py), "--numbers", "1,2,3,4", "--question", "t", "--json"],
               capture_output=True, text=True, cwd=ROOT)
    check("四数起卦被拒绝", r.returncode != 0)

    sys.path.pop(0)


def test_tarot() -> None:
    print("\n[塔罗]")
    out_py = ROOT / "scripts/run_tarot.py"

    print("  -- seed 复现与结构 --")
    cmd = [
        PYTHON, str(out_py),
        "--spread", "choice",
        "--question", "A or B",
        "--seed", "regression-seed",
    ]
    first = run(cmd)
    second = run(cmd)
    check("同 seed 输出完全一致", first == second)
    data = json.loads(first)
    check("choice 三张牌", len(data["cards"]) == 3)
    check("choice 位置正确", [c["position"] for c in data["cards"]] == ["Option A", "Option B", "Guidance"])
    check("无重复牌", len({c["card"] for c in data["cards"]}) == len(data["cards"]))
    check("方向合法", all(c["orientation"] in {"upright", "reversed"} for c in data["cards"]))
    check("牌含 arcana 字段", all(c["arcana"] in {"Major", "Minor"} for c in data["cards"]))

    print("  -- 牌阵数量 --")
    celtic = json.loads(run([PYTHON, str(out_py), "--spread", "celtic", "--seed", "10"]))
    relationship = json.loads(run([PYTHON, str(out_py), "--spread", "relationship", "--seed", "5"]))
    single = json.loads(run([PYTHON, str(out_py), "--spread", "single", "--seed", "1"]))
    check("celtic 十张牌", len(celtic["cards"]) == 10)
    check("relationship 五张牌", len(relationship["cards"]) == 5)
    check("single 一张牌", len(single["cards"]) == 1)

    print("  -- markdown 输出 --")
    md = run([PYTHON, str(out_py), "--spread", "single", "--seed", "md", "--format", "markdown"])
    check("markdown 表格包含 Card 列", "| # | Position | Card |" in md)


def test_bazi() -> None:
    print("\n[八字]")
    out_py = ROOT / "scripts/run_bazi.py"

    print("  -- 基础排盘结构 --")
    data = json.loads(run([
        PYTHON, str(out_py),
        "--date", "1990-10-21",
        "--time", "15:30",
        "--gender", "female",
    ]))
    check("四柱=庚午 丙戌 己未 壬申", data["bazi"]["display"] == "庚午 丙戌 己未 壬申",
          f"got {data['bazi']['display']}")
    check("日主=己土", data["bazi"]["day_master"] == {"gan": "己", "element": "土"})
    check("年干十神=伤官", data["bazi"]["pillars"]["year"]["ten_god_gan"] == "伤官")
    check("大运方向字段存在", isinstance(data["luck"]["forward"], bool))
    check("大运含干支", any(item["ganzhi"] for item in data["luck"]["items"]))

    print("  -- 真太阳时校验 --")
    corrected = json.loads(run([
        PYTHON, str(out_py),
        "--date", "1990-10-21",
        "--time", "15:30",
        "--gender", "female",
        "--true-solar-time",
        "--longitude", "105",
    ]))
    check("105E 真太阳时含经度与均时差",
          corrected["normalized"]["effective_solar_datetime"].startswith("1990-10-21 14:45")
          and corrected["normalized"]["time_correction"]["longitude_minutes"] == -60.0
          and corrected["normalized"]["time_correction"]["equation_of_time_minutes"] > 0,
          f"got {corrected['normalized']['effective_solar_datetime']}")

    print("  -- markdown 输出 --")
    md = run([
        PYTHON, str(out_py),
        "--date", "1990-10-21",
        "--time", "15:30",
        "--gender", "female",
        "--format", "markdown",
    ])
    check("markdown 包含四柱明细", "## 四柱明细" in md and "| 年柱 | 庚午 |" in md)

    lunar = json.loads(run([
        PYTHON, str(out_py),
        "--date", "2024-02-30", "--time", "12:00", "--gender", "male",
        "--date-type", "lunar",
    ]))
    check("合法农历三十可排盘", lunar["normalized"]["solar"] == "2024-04-08 12:00:00")

    sect_one = json.loads(run([
        PYTHON, str(out_py),
        "--date", "2026-04-06", "--time", "23:30", "--gender", "male", "--sect", "1",
    ]))
    sect_two = json.loads(run([
        PYTHON, str(out_py),
        "--date", "2026-04-06", "--time", "23:30", "--gender", "male", "--sect", "2",
    ]))
    check("sect 口径一致且晚子时可切换",
          sect_one["normalized"]["ganzhi"]["day"] == sect_one["bazi"]["pillars"]["day"]["ganzhi"]
          and sect_two["normalized"]["ganzhi"]["day"] == sect_two["bazi"]["pillars"]["day"]["ganzhi"]
          and sect_one["bazi"]["pillars"]["day"]["ganzhi"] != sect_two["bazi"]["pillars"]["day"]["ganzhi"])

    invalid = subprocess.run([
        PYTHON, str(out_py), "--date", "1990-10-21", "--time", "15:30", "--gender", "female",
        "--true-solar-time", "--longitude", "999",
    ], capture_output=True, text=True, cwd=ROOT)
    check("八字拒绝非法经度", invalid.returncode != 0)


def test_meihua() -> None:
    print("\n[梅花易数]")
    out_py = ROOT / "scripts/run_meihua.py"

    print("  -- 时间起卦 fixture --")
    data = json.loads(run([
        PYTHON, str(out_py),
        "--method", "time",
        "--time", "2026-06-30 22:10",
        "--timezone", "Asia/Shanghai",
        "--question", "项目推进",
    ]))
    chart = data["chart"]
    check("本卦=雷地豫", chart["base"]["name"] == "雷地豫", f"got {chart['base']['name']}")
    check("变卦=坤为地", chart["changed"]["name"] == "坤为地", f"got {chart['changed']['name']}")
    check("动爻=4", chart["moving_yao"] == 4, f"got {chart['moving_yao']}")
    check("体用关系存在", chart["ti_yong"]["relation"] in {"同气", "体生用", "用生体", "体克用", "用克体"})
    check("时间起卦记录时区", data["source"]["timezone"] == "Asia/Shanghai")

    print("  -- seed 复现 --")
    cmd = [PYTHON, str(out_py), "--method", "seed", "--seed", "stable-case", "--question", "合作"]
    check("同 seed 输出完全一致", run(cmd) == run(cmd))

    print("  -- markdown 输出 --")
    md = run([
        PYTHON, str(out_py),
        "--method", "number",
        "--numbers", "12,34,56",
        "--question", "合作",
        "--format", "markdown",
    ])
    check("markdown 包含体用", "体用" in md and "本卦" in md)

    rejected = subprocess.run(
        [PYTHON, str(out_py), "--method", "time", "--time", "2026-06-30"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    check("日期缺具体时刻被拒绝", rejected.returncode != 0)


def test_wrappers() -> None:
    print("\n[wrapper 失败码]")
    liuyao = subprocess.run(
        [PYTHON, str(ROOT / "scripts/run_liuyao.py"), "--coins", "1,2,3,4,2,1", "--question", "t"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    check("六爻 wrapper 传播失败码", liuyao.returncode != 0, f"got {liuyao.returncode}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        qimen = subprocess.run(
            [
                PYTHON,
                str(ROOT / "scripts/run_qimen.py"),
                "--input",
                str(temp_path / "missing.json"),
                "--output",
                str(temp_path / "output.json"),
            ],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
    check("奇门 wrapper 传播失败码", qimen.returncode != 0, f"got {qimen.returncode}")


def test_package() -> None:
    print("\n[成品包]")
    with tempfile.TemporaryDirectory() as temp_dir:
        output_root = Path(temp_dir)
        run([PYTHON, str(ROOT / "tools/build_skill.py"), "--out", str(output_root), "--no-zip"])
        package = output_root / "xiaozhua-divination"
        check("包含统一免责声明", (package / "references/disclaimer.md").is_file())
        check("包含上游版本锁定清单", (package / "references/upstream-lock.json").is_file())
        check("包含许可证", (package / "LICENSE").is_file())
        check("包含梅花模块", (package / "meihua-yishu/scripts/meihua_pan.py").is_file())
        check("成品包不携带开发自检脚本", not list(package.rglob("self_check.py")))


def main() -> int:
    targets = sys.argv[1:] or ["package", "wrappers", "qimen", "ziwei", "liuyao", "bazi", "tarot", "meihua"]
    supported = {"qimen", "ziwei", "liuyao", "bazi", "tarot", "meihua", "package", "wrappers"}
    unknown = sorted(set(targets) - supported)
    if unknown:
        print(f"未知测试目标: {', '.join(unknown)}", file=sys.stderr)
        return 2
    if "qimen" in targets:
        test_qimen()
    if "ziwei" in targets:
        test_ziwei()
    if "liuyao" in targets:
        test_liuyao()
    if "bazi" in targets:
        test_bazi()
    if "tarot" in targets:
        test_tarot()
    if "meihua" in targets:
        test_meihua()
    if "wrappers" in targets:
        test_wrappers()
    if "package" in targets:
        test_package()

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
