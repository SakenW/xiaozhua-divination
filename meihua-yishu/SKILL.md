---
name: meihua-yishu
description: >
  梅花易数起卦与象数解读技能。当用户明确提到梅花易数、梅花心易、体用、生克、
  互卦、变卦，或想用时间/数字快速看一件事的趋势时使用。正式起卦必须调用脚本，
  不由 LLM 随机生成卦象。
compatibility: Requires Python 3.11+ and lunar_python; run scripts/meihua_pan.py through root scripts/run_meihua.py.
---

# 梅花易数技能

本技能用于一事一断的趋势观察。它比六爻更轻，重点在象数结构、体用关系和动变趋势；如果用户需要纳甲、六亲、世应、应期等细断，应转到 `liuyao/SKILL.md`。

Read:

- `references/interpretation-guide.md`：本仓库梅花易数的解读边界、体用生克和输出要求

## 触发范围

使用本技能：

- 用户明确说“梅花易数”“梅花心易”“体用”“互卦”“变卦”。
- 用户想用时间、数字或一个稳定 seed 快速看某件事的趋势。
- 用户的问题是一事一断，且更需要趋势/取象而非六爻纳甲细断。

不要使用本技能：

- 用户指定六爻、奇门、紫微、八字、塔罗等其他体系。
- 用户问题过宽，如“我一生命运如何”，应转八字或紫微。
- 用户要求医疗、法律、投资等确定性结论，只能做象征性风险提示。

## 起卦方式

从技能根目录调用统一 wrapper：

```bash
python3 scripts/run_meihua.py --method time --time "2026-06-30 22:10" --timezone Asia/Shanghai --question "这个项目下周能不能推进" --format markdown
```

支持三种方式：

```bash
# 时间起卦
python3 scripts/run_meihua.py --method time --time "2026-06-30 22:10" --timezone Asia/Shanghai --question "事业"

# 数字起卦：两个数定上下卦，第三个数定动爻；只有两个数时用两数之和定动爻
python3 scripts/run_meihua.py --method number --numbers "12,34,56" --question "合作"

# seed 起卦：同一 seed 稳定复现，适合没有时间/数字但需要可复查的娱乐趋势分析
python3 scripts/run_meihua.py --method seed --seed "合作|2026-06-30|A方案" --question "合作"
```

## 工作流

1. 先确认问题是否足够具体：一卦只看一件事。
2. 选择起卦方式；用户没有指定时默认时间起卦，并确认具体时刻与时区。使用 `now` 时也必须显式传入用户所在时区。
3. 调用 `scripts/run_meihua.py`，读取脚本输出。
4. 按 `references/interpretation-guide.md` 解读本卦、互卦、变卦、动爻、体用生克。
5. 结尾附 `../references/disclaimer.md` 中“一、统一免责声明”的正文。

## 输出原则

- 固定卦象以脚本输出为准。
- 先结论，后依据，再建议。
- 术语第一次出现时用现代汉语解释。
- 不恐吓、不宿命、不制造依赖。
- 遇到高风险主题时，必须把现实建议放在术数判断之前。
