---
name: xiaozhua-divination
description: >
  小爪命理屋：综合命理与性格分析路由技能。覆盖六爻、奇门遁甲、紫微斗数、
  八字、塔罗、占星、九型人格、MBTI。用户指定体系时使用对应子技能；未指定时
  根据问题类型选择最合适的方法。紫微、奇门、六爻的正式排盘必须调用脚本完成。
---

# 小爪命理屋

这是一个总入口技能，只负责三件事：

1. 判断用户需要哪个体系。
2. 收集会影响结果的关键输入。
3. 路由到对应子技能，并在有脚本时使用脚本排盘。

## 路由规则

用户指定方法时，优先使用用户指定的方法。

| 用户意图 | 首选体系 | 读取文件 |
| --- | --- | --- |
| 一事一断、近期能不能成、快速吉凶 | 六爻 | `liuyao/SKILL.md` |
| 择时、方位、趋吉避凶、某个时刻的局势 | 奇门遁甲 | `qimen-dunjia/SKILL.md` |
| 命盘、人生规划、大限流年、十二宫 | 紫微斗数 | `ziwei-doushu/SKILL.md` |
| 八字、四柱、日主、十神、喜用神、大运 | 八字 | `bazi/SKILL.md` |
| 抽牌、牌阵、直觉指引 | 塔罗 | `tarot/SKILL.md` |
| 星盘、太阳月亮上升、宫位、相位、合盘 | 占星 | `astrology/SKILL.md` |
| 深层动机、成长方向、副型 | 九型人格 | `enneagram/SKILL.md` |
| 16 型、认知功能、职业匹配、团队关系 | MBTI | `mbti/SKILL.md` |

难以判断时先问用户偏好，不要静默混用多个体系。一次回答最多聚焦 1 到 2 个主题。

## 输入收集

正式分析前先确认必要信息：

| 体系 | 必需输入 |
| --- | --- |
| 六爻 | 明确问题；起卦方式为时间、铜钱或数字 |
| 奇门 | 事项、时间、地点或时区、判断目标 |
| 紫微 | 出生日期、出生时间或时辰、性别、公历/农历口径 |
| 八字 | 出生日期、出生时间、性别、公历/农历、出生地或时区 |
| 占星 | 出生日期、出生时间、出生地点 |
| 九型/MBTI | 用户自测结果，或先访谈再给候选类型 |
| 塔罗 | 问题或主题；牌阵可由用户指定或由你推荐 |

信息不足时先追问。不要为了继续输出而静默代填出生时间、时区、性别、历法口径。

## 脚本排盘

从本技能根目录运行 wrapper。wrapper 会自动把 `scripts/.venv` 中的依赖加入路径；如果没有本地 venv，则依赖调用环境需先安装根目录 `requirements.txt` 中的包。

### 紫微斗数

```bash
python3 scripts/run_ziwei.py \
  --date 1983-04-29 --time 11:05 --gender male \
  --format markdown --template pro
```

### 奇门遁甲

```bash
printf '%s' '{"question_type":"career","question_goal":"判断合作是否适合推进","time_input":"2026-04-27 23:23","calendar_type":"solar","location":{"country":"China","timezone":"Asia/Shanghai"},"ruleset":"mainline-cn-v1"}' > /tmp/qimen_input.json
python3 scripts/run_qimen.py --input /tmp/qimen_input.json --output /tmp/qimen_output.json
cat /tmp/qimen_output.json
```

### 六爻

```bash
# 时间起卦
python3 scripts/run_liuyao.py --date "2026-04-27 23:23" --question "事业"

# 铜钱起卦：6 次正面数（字面数 0-3），从初爻到上爻
python3 scripts/run_liuyao.py --coins "1,2,3,1,2,3" --question "财运"

# 数字起卦
python3 scripts/run_liuyao.py --numbers "3,5,7,2,8,9" --question "事业"
```

## 输出原则

- 先给结论，再给关键依据和行动建议。
- 术语第一次出现时用一句话解释。
- 有脚本的体系，盘面和固定计算以脚本输出为准，不手算替代。
- 如果脚本不可用，明确说明无法正式排盘，不要伪造盘面。
- 高风险主题，如医疗、法律、财务、投资、人身安全，必须附现实建议。
- 不使用恐吓式或宿命论表达，不说“必死”“无救”“注定无法改变”。
- 每次解读后附免责声明。

## 免责声明

免责声明的完整正文见 [`references/disclaimer.md`](references/disclaimer.md)，它是全仓库所有子技能的单一事实源，涵盖中华术数、占星、塔罗、人格模型（MBTI/九型）的统一边界与高风险主题强制现实建议。每次解读结尾必须附上其中"一、统一免责声明"的正文，可微调措辞。
