---
name: xiaozhua-divination
description: >
  🐾 小爪命理屋 — 综合命理与性格分析技能。整合中华传统术数（六爻、奇门、紫微、八字）
  与西方体系（塔罗、占星、九型、MBTI），共 8 大体系。紫微、奇门、六爻均有确定性排盘脚本，
  排盘靠计算不靠猜。根据用户问题类型自动选择合适的方法，或按要求使用指定方法。
---

# 🐾 小爪命理屋

> 小爪的算命技能，整合东西方命理，排盘靠脚本不靠猜。

## 八大体系

| 体系 | 适用场景 | 输入要求 | 排盘方式 |
|------|----------|----------|----------|
| **六爻问卦** | 一事一断、近期决策 | 问题+时间/铜钱 | ⚙️ 脚本排盘 |
| **奇门遁甲** | 择时、方位、趋吉避凶 | 时间+地点+问题 | ⚙️ 脚本排盘 |
| **紫微斗数** | 命盘、人生规划、运势 | 出生年月日时+性别 | ⚙️ 脚本排盘 |
| **八字四柱** | 命理格局、大运流年 | 出生年月日时+性别 | LLM 解读 |
| **占星学** | 性格、情感、事业 | 出生年月日时+地点 | LLM 解读 |
| **九型人格** | 动机、成长、关系 | 自我确认或测试 | LLM 解读 |
| **MBTI** | 职业匹配、认知功能 | 自我确认或测试 | LLM 解读 |
| **塔罗** | 一事一断、直觉指引 | 问题明确 | LLM 解读 |

## 方法选择规则

```
问题类型                    推荐方法
────────────────────────────────────
"这件事能不能成"            → 六爻/奇门
"今天适合见人吗"            → 奇门遁甲
"我想看自己的命盘"          → 紫微斗数
"看看我的八字"              → 八字四柱
"下个月运势如何"            → 紫微斗数（大限流年）
"这个项目什么时候启动好"    → 奇门遁甲（择时）
"简单看看，就是想知道结果"  → 六爻问卦
"用时间起卦"                → 六爻（时间起卦）
"我想看星盘"                → 占星学
"我是什么性格类型"          → 九型/MBTI
"我们合适吗"                → 占星（合盘）/九型
"帮我抽个塔罗"              → 塔罗
"最近心里很乱"              → 塔罗/六爻
```

用户指定方法时优先使用指定方法。

## 目录结构

```
xiaozhua-divination/
├── SKILL.md                  ← 主入口（当前文件）
├── scripts/
│   ├── run_ziwei.py          ← 紫微排盘 wrapper
│   ├── run_qimen.py          ← 奇门排盘 wrapper
│   ├── run_liuyao.py         ← 六爻排盘 wrapper
│   └── .venv/                ← Python 统一依赖
│
├── liuyao/                   ← 六爻问卦
│   ├── SKILL.md              ← 解读规则
│   ├── time-casting.md       ← 时间起卦+六爻断卦
│   └── scripts/
│       └── liuyao_pan.py     ← 排盘脚本（31KB，天工长老）
│
├── qimen-dunjia/             ← 奇门遁甲
│   ├── SKILL.md
│   ├── scripts/
│   │   └── qimen_cli.py      ← 排盘脚本（20KB，FANzR-arch）
│   └── references/
│
├── ziwei-doushu/             ← 紫微斗数
│   ├── SKILL.md
│   ├── scripts/
│   │   └── ziwei_chart.py    ← 排盘脚本（40KB，spyfree）
│   └── references/
│
├── bazi/                     ← 八字四柱（LLM 解读）
│   └── SKILL.md
│
├── tarot/                    ← 塔罗牌（LLM 解读）
│   ├── SKILL.md
│   └── references/
│
├── astrology/                ← 西方占星学
│   └── SKILL.md
│
├── enneagram/                ← 九型人格
│   └── SKILL.md
│
└── mbti/                     ← MBTI
    └── SKILL.md
```

## 排盘脚本使用

### 统一原则
Wrapper 脚本首次运行时会自动创建 `.venv` 并安装依赖，无需手动操作。

### 紫微斗数
```bash
python3 scripts/run_ziwei.py \
  --date 1983-04-29 --time 11:05 --gender male \
  --format markdown --template pro
```

### 奇门遁甲
```bash
# 写输入 JSON → 运行 → 读结果
echo '{"question_type":"...","time_input":"2026-04-27 23:23","calendar_type":"solar","location":{"country":"China","timezone":"Asia/Shanghai"},"ruleset":"mainline-cn-v1"}' > /tmp/qi_in.json
python3 scripts/run_qimen.py --input /tmp/qi_in.json --output /tmp/qi_out.json
cat /tmp/qi_out.json
```

### 六爻
```bash
# 时间起卦
python3 scripts/run_liuyao.py --date "2026-04-27 23:23" --question "事业"

# 铜钱起卦（6次背面数）
python3 scripts/run_liuyao.py --coins "1,2,3,1,2,3" --question "财运"

# 数字起卦
python3 scripts/run_liuyao.py --numbers "3,5,7,2,8,9"
```

## 调用子技能

### 六爻问卦
触发词：六爻、起卦、问卦、摇卦、铜钱卦
读取：`liuyao/SKILL.md`
**排盘用脚本** `scripts/run_liuyao.py`，断卦可结合 LLM。

### 奇门遁甲
触发词：奇门遁甲、奇门排盘、奇门解盘、择时、方位选择
读取：`qimen-dunjia/SKILL.md`
**必须用脚本排盘**。

### 紫微斗数
触发词：紫微斗数、紫微命盘、命宫、十二宫、大限流年
读取：`ziwei-doushu/SKILL.md`
**必须用脚本排盘**。

### 八字四柱
触发词：八字、四柱、生辰八字、命理、大运流年
读取：`bazi/SKILL.md`
LLM 解读为主。

### 占星学
触发词：占星、星盘、星座、行星、宫位、相位、合盘
读取：`astrology/SKILL.md`

### 九型人格
触发词：九型人格、九型、副型、成长方向
读取：`enneagram/SKILL.md`

### MBTI
触发词：MBTI、性格类型、E/I、S/N、T/F、J/P、认知功能
读取：`mbti/SKILL.md`

### 塔罗
触发词：塔罗、抽牌、占卜、牌阵、大牌、小牌
读取：`tarot/SKILL.md`

## 统一原则

### 必须做
- ✅ 先问清再分析，不要跳过关键信息收集
- ✅ 有脚本的方法必须用脚本，不要 LLM 心算排盘
- ✅ 用人话解释，术语第一次出现时简要说明
- ✅ 结论明确，不故意模糊
- ✅ 高风险主题必须附现实建议
- ✅ 每次解读后附免责声明

### 禁止做
- ❌ 恐吓式语言（"必败""必死""无救"）
- ❌ 宿命论表述（"注定如此""无法改变"）
- ❌ 跳过信息收集直接下结论
- ❌ 替代医疗/法律/财务等专业意见
- ❌ 在有脚本可用时手算排盘

## 致谢与来源

本技能整合了多位作者的工作，按子技能分类：

### 紫微斗数
- **排盘脚本** (`ziwei_chart.py`, 40KB)：[spyfree](https://clawhub.com) — clawhub `ziwei-doushu` v1.0.2
- **SKILL.md + 排盘规则 + 星曜 + 四化 + 格局**：[FANzR-arch/Numerologist_skills](https://github.com/FANzR-arch/Numerologist_skills) — 含详细追问流程、三方四正表、庙旺陷表、飞星进阶
- **解读框架**：spyfree — interpretation-framework.md、mapping.md

### 奇门遁甲
- **排盘脚本** (`qimen_cli.py`, 20KB)：[FANzR-arch/Numerologist_skills](https://github.com/FANzR-arch/Numerologist_skills)
- **解读参考**：FANzR-arch — 用神、格局、访谈流程、规则集
- **解读指南 + 计算规则**：[eamanc-lab](https://clawhub.com) — clawhub `qimen-dunjia-oracle` v1.0.0 — 九星八门八神详解、常见格局、方位吉凶规则、输出格式模板
- **SKILL.md 框架**：mingkunyuan/divination-skills

### 六爻问卦
- **排盘脚本** (`liuyao_pan.py`, 31KB)：[天工长老 (dglijin-oss)](https://clawhub.com) — clawhub `liuyao-najia-skill` v3.0.1
- **解读参考**：[eamanc-lab](https://clawhub.com) — clawhub `liuyao-yijing` v1.0.0 — 计算规则 + 解读指南
- **时间起卦法**：mingkunyuan/divination-skills — time-casting.md

### 八字四柱
- **SKILL.md + 天干地支参考 + 提示词模板**：[FANzR-arch/Numerologist_skills](https://github.com/FANzR-arch/Numerologist_skills)
- **计算规则 + 解读指南**：[eamanc-lab](https://clawhub.com) — clawhub `bazi-fortune` v1.0.0（子平真诠体系）

### 塔罗牌
- **SKILL.md + 大牌 + 小牌 + 牌阵 + 解读规则**：[eamanc-lab](https://clawhub.com) — clawhub `tarot-reading` v1.2.0（Rider-Waite-Smith 体系，中英双语）

### 占星学 / 九型人格 / MBTI
- **SKILL.md**：[clider0915/divination-skills](https://github.com/clider0915/divination-skills) v2.0

### eamanc-lab 其他技能（未使用）
- `qimen-dunjia-oracle`（参考文档已合并，排盘用 FANzR-arch 脚本版）

---
*整理时间：2026-04-28*

## 统一免责声明

> 温馨提示：传统术数属于中华文化遗产，本次解读用于辅助观察与思考，不代替医疗、法律、财务等专业意见。涉及重大决策时，请同时结合现实信息理性判断。

---

*🐾 小爪命理屋 v1.0 — 8 体系 · 3 脚本排盘 · 排盘靠计算不靠猜*
