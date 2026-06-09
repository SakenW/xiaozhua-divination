# 🐾 小爪命理屋

> **8 大体系 · 3 脚本排盘 · 排盘靠计算不靠猜**

整合中华传统术数（紫微斗数、奇门遁甲、六爻问卦、八字四柱）与西方体系（塔罗、占星、九型人格、MBTI），共 8 种命理与性格分析方法。

三个中华术数体系配备**确定性排盘脚本**——排盘结果由程序计算而非 LLM 猜测，确保准确性和一致性。

## ✨ 特点

- 🧮 **脚本排盘**：紫微斗数、奇门遁甲、六爻问卦均有 Python 排盘脚本，零依赖 LLM 心算
- 🔄 **智能路由**：根据问题类型自动推荐最合适的方法
- 📚 **多源整合**：每个体系整合了多个优质来源的排盘规则和解读框架
- 🤖 **AI Agent 友好**：设计为 AI Agent 的技能插件，可被 OpenClaw 等 Agent 框架直接调用

## 📦 安装

### 前置条件

- Python 3.11+
- pip

### 快速开始

```bash
# 克隆仓库
git clone https://github.com/SakenW/xiaozhua-divination.git
cd xiaozhua-divination

# 安装依赖（首次运行 wrapper 时也会自动安装）
pip install -r requirements.txt
```

或者什么都不做——**wrapper 脚本首次运行时会自动创建 venv 并安装依赖**。

## 🎯 使用

### 紫微斗数排盘
```bash
python3 scripts/run_ziwei.py --date 1983-04-29 --time 11:05 --gender male --format markdown
```

### 奇门遁甲排盘
```bash
# 先准备输入 JSON
echo '{"question_type":"事业","time_input":"2026-06-09 10:00","calendar_type":"solar","location":{"country":"China","timezone":"Asia/Shanghai"},"ruleset":"mainline-cn-v1"}' > /tmp/qi_in.json

# 运行排盘
python3 scripts/run_qimen.py --input /tmp/qi_in.json --output /tmp/qi_out.json

# 查看结果
cat /tmp/qi_out.json
```

### 六爻问卦
```bash
# 时间起卦
python3 scripts/run_liuyao.py --date "2026-06-09 10:00" --question "事业"

# 铜钱起卦（6次摇出的背面数，0-3）
python3 scripts/run_liuyao.py --coins "1,2,3,1,2,3" --question "财运"

# 数字起卦
python3 scripts/run_liuyao.py --numbers "3,5,7,2,8,9"
```

## 🗂️ 8 大体系一览

| 体系 | 来源 | 排盘方式 | 适用场景 |
|------|------|----------|----------|
| 🌟 **紫微斗数** | 中华 | ⚙️ 脚本排盘 | 命盘分析、人生规划、大限流年 |
| 🧭 **奇门遁甲** | 中华 | ⚙️ 脚本排盘 | 择时决策、方位选择、趋吉避凶 |
| 🎲 **六爻问卦** | 中华 | ⚙️ 脚本排盘 | 一事一断、近期决策、吉凶判断 |
| ☯️ **八字四柱** | 中华 | LLM 解读 | 命理格局、大运流年、五行喜忌 |
| 🃏 **塔罗牌** | 西方 | LLM 解读 | 直觉指引、一事一断、心理探索 |
| ✨ **占星学** | 西方 | LLM 解读 | 性格分析、情感模式、事业规划 |
| 🔢 **九型人格** | 西方 | LLM 解读 | 动机分析、个人成长、关系模式 |
| 🧠 **MBTI** | 西方 | LLM 解读 | 认知功能、职业匹配、团队建设 |

## 📁 项目结构

```
xiaozhua-divination/
├── SKILL.md                  ← 统一入口，方法路由规则
├── scripts/                  ← 排盘 wrapper + 自动 venv 管理
├── ziwei-doushu/             ← 紫微斗数（排盘脚本 + 参考文档）
├── qimen-dunjia/             ← 奇门遁甲（排盘脚本 + 参考文档）
├── liuyao/                   ← 六爻问卦（排盘脚本 + 参考文档）
├── bazi/                     ← 八字四柱（参考文档）
├── tarot/                    ← 塔罗牌（参考文档）
├── astrology/                ← 占星学
├── enneagram/                ← 九型人格
└── mbti/                     ← MBTI
```

每个子目录的 `SKILL.md` 包含该体系的详细使用规则、触发词和解读框架。

## 🙏 致谢

本技能整合了多位作者的心血：

| 子技能 | 排盘脚本来源 | 解读参考来源 |
|--------|------------|------------|
| 紫微斗数 | [spyfree](https://clawhub.com) | spyfree + [mingkunyuan](https://github.com/mingkunyuan/divination-skills) |
| 奇门遁甲 | [FANzR-arch](https://github.com/FANzR-arch/Numerologist_skills) | FANzR-arch + [eamanc-lab](https://clawhub.com) + mingkunyuan |
| 六爻问卦 | [天工长老](https://clawhub.com) | eamanc-lab + mingkunyuan |
| 八字四柱 | — | eamanc-lab |
| 塔罗牌 | — | eamanc-lab |
| 占星/九型/MBTI | — | [clider0915](https://github.com/clider0915/divination-skills) |

## ⚠️ 免责声明

> 传统术数属于中华文化遗产，塔罗占星属于西方文化传统，本次解读均用于辅助观察与思考，不代替医疗、法律、财务等专业意见。涉及重大决策时，请同时结合现实信息理性判断。

## 📄 License

MIT

---

*🐾 小爪命理屋 v1.0 — 8 体系 · 3 脚本排盘 · 排盘靠计算不靠猜*
