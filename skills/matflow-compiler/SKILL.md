---
name: matflow-compiler
description: >-
  材料实验协议编译与安全审计 Skill。将论文、专利和实验描述中的材料实验方法编译为结构化、可执行、可验证、可追溯的实验协议。接收论文/专利/补充材料文档，输出机器可读协议(protocol.json/protocol.yaml)、人类可读SOP、缺失条件报告、安全与可执行性报告、恢复检查点方案。当用户需要从文献提取实验步骤、复现材料实验、生成实验SOP、检查实验安全可行性、或编译材料合成协议时调用此 Skill。
---

# MatFlow Compiler

## 1. 概述

MatFlow Compiler 将材料论文中的实验方法编译成介于自然语言 SOP 和实验室设备指令之间的标准化实验中间表示（Experiment Intermediate Representation, EIR）。

**核心差异化：**

- **Evidence-grounded（证据锚定）**：每个配方字段、步骤、参数均绑定原文证据，可追溯至页码、表格、图号。
- **Machine-readable（机器可读）**：输出结构化 JSON/YAML，可被下游自动化系统直接消费。
- **Safety-bounded（安全有界）**：内置安全审计，对超温、密闭加热、不相容试剂等风险主动阻断。
- **Recoverable（可恢复）**：为每一步生成检查点方案，支持中断后恢复。

## 2. 适用范围

- **材料合成实验**：无机材料（氧化物、硫化物、钙钛矿等）、高分子材料、能源材料（电池正负极、催化剂等）、纳米材料。
- **文献来源**：从论文、专利、补充材料文档中提取实验方法。
- **目标**：生成可执行实验协议，支持复现（reproduce）、放大（scale_up）、优化（optimize）三种目标。

## 3. 不适用范围

- **非材料领域**：生物/医学/临床实验不在处理范围。
- **纯理论计算**：DFT（密度泛函理论）、MD（分子动力学）模拟不作为协议主体。
- **材料选择和发现**：不负责筛选最优材料体系。
- **文献综述**：不生成综述或总结性文档。

## 4. 输入规范

接收四类输入：

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `source_documents` | 文档路径列表 | 是 | 论文/专利/补充材料 PDF 或文本 |
| `target` | 对象 | 是 | 目标材料和目标（reproduce/scale_up/optimize） |
| `lab_profile` | YAML 路径 | 否 | 可选设备信息 |
| `execution_mode` | 枚举 | 是 | analysis_only / protocol_generation / device_binding |

**输入 YAML 模板：**

```yaml
source_documents:
  - path: "papers/sol_gel_TiO2.pdf"
    type: "journal_article"
  - path: "patents/CN123456A.pdf"
    type: "patent"
target:
  material: "TiO2 nanoparticles (anatase)"
  goal: "reproduce"            # reproduce | scale_up | optimize
lab_profile: "config/lab_devices.yaml"  # 可选
execution_mode: "protocol_generation"   # analysis_only | protocol_generation | device_binding
```

## 5. 输出规范

同时输出 6 种产物：

| 产物 | 格式 | 用途 |
|------|------|------|
| `protocol.json` | JSON | 机器可读结构化协议，含完整步骤图与参数 |
| `protocol.yaml` | YAML | 设备无关实验中间表示（EIR），便于人工审阅 |
| `SOP.md` | Markdown | 人类可读标准操作程序 |
| `missing_conditions.md` | Markdown | 缺失条件报告，列出所有 null 字段及风险 |
| `safety_report.md` | Markdown | 安全与可执行性报告，含阻断项与确认点 |
| `recovery_plan.yaml` | YAML | 恢复与检查点方案，每步含 checkpoint 定义 |

## 6. 执行工作流

```
┌──────────────────────────────────────────────────────────┐
│                   Orchestrator（总调度）                   │
│   解析输入、分配任务、汇聚产物、执行最终一致性检查            │
└────────┬─────────────────────────────────────────────────┘
         │
    ┌────▼──────┐
    │ Document  │  分类文档类型（论文/专利/补充材料），
    │ Classifier│  识别实验方法所在章节
    └────┬──────┘
         │
    ┌────▼───────┐
    │  Evidence  │  从原文抽取实验条件，绑定页码/表/图/段落，
    │  Extractor │  标注 evidence_type 与 confidence
    └────┬───────┘
         │
    ┌────▼───────────────┐
    │ Material & Sample  │  解析材料名称、CAS 号、纯度、供应商，
    │     Resolver       │  统一为标准物质标识
    └────┬───────────────┘
         │
    ┌────▼───────────────┐
    │ Chemistry          │  归一化单位、摩尔比、质量浓度，
    │  Normalizer        │  执行化学计量校验
    └────┬───────────────┘
         │
    ┌────▼───────────────┐
    │ Protocol           │  将证据编译为原子操作序列，
    │  Compiler          │  构建步骤依赖图
    └────┬───────────────┘
         │
    ┌────▼───────────────┐
    │ Device Capability  │  若提供 lab_profile，匹配设备能力；
    │     Binder         │  否则输出设备无关协议
    └────┬───────────────┘
         │
    ┌────▼───────────────┐
    │ Safety             │  审计温度/压力/不相容试剂/通风需求，
    │  Auditor           │  标记阻断项与人工确认点
    └────┬───────────────┘
         │
    ┌────▼───────────────┐
    │ Final              │  校验证据完整性、缺失字段标记、
    │  Validator         │  安全检查覆盖、无静默补全
    └────────────────────┘
```

**各角色职责：**

1. **Orchestrator（总调度）**：解析输入参数，按序调度下游 Agent，汇聚所有产物，执行最终一致性检查并输出。
2. **Document Classifier（文档分类）**：识别文档类型与实验方法所在章节，输出结构化文档索引。
3. **Evidence Extractor（证据抽取）**：从原文逐句抽取实验条件，绑定页码/表号/图号/段落，标注证据类型与可信度。
4. **Material & Sample Resolver（材料样品解析）**：解析材料名称、CAS 号、纯度、供应商，统一为标准物质标识。
5. **Chemistry Normalizer（化学计量归一化）**：归一化单位与浓度，计算摩尔比，执行化学计量校验。
6. **Protocol Compiler（协议编译）**：将证据编译为原子操作序列，构建步骤依赖图，标注并行/串行关系。
7. **Device Capability Binder（设备绑定）**：若提供设备清单，匹配设备能力并绑定；否则输出设备无关协议。
8. **Safety Auditor（安全审计）**：审计温度/压力/不相容试剂/通风需求，标记阻断项与人工确认点。
9. **Final Validator（最终验证）**：校验证据完整性、缺失字段标记、安全检查覆盖、确认不存在静默补全。

## 7. 核心设计原则

> 此部分为 Skill 的立身之本，所有 Agent 必须严格遵守。

### 7.1 绝不静默补全

对文献未提供的关键实验条件，**不得**依据常识、领域惯例或训练数据直接填写确定值。

处理方式：
- 将字段值设为 `null`
- 在 `missing_conditions.md` 中记录：字段名、缺失原因、风险等级、是否阻止执行
- 在 `safety_report.md` 中标注影响

**禁止行为示例：**
- 文献未给煅烧温度 → 禁止填 "500°C"
- 文献未给搅拌速率 → 禁止填 "300 rpm"
- 文献未给干燥时间 → 禁止填 "12 h"

### 7.2 证据和操作一一对应

每个配方字段、每个步骤、每个参数都必须绑定至少一条证据引用。证据引用格式：

```yaml
evidence:
  doc: "papers/sol_gel_TiO2.pdf"
  page: 5
  table: "Table 1"          # 可选
  figure: "Fig 2"            # 可选
  paragraph: 3
  quote: "The precursor solution was stirred at 60°C for 2 h."
  evidence_type: "explicit"
  confidence: 0.95
```

无证据的字段不得进入协议。

### 7.3 区分三种信息

| 类型 | 定义 | 是否可进入自动执行协议 |
|------|------|------------------------|
| `explicit` | 原文明确给出的数值或描述 | 是 |
| `derived` | 由明确数据经公式计算得到，可验证 | 是（须附推导链） |
| `inferred` | 基于上下文、常识或惯例推断 | 否，默认需人工确认 |

`derived` 类型必须附推导链：

```yaml
value: 0.025
unit: "mol"
evidence_type: "derived"
derivation:
  inputs:
    - field: "mass"
      value: 4.0
      unit: "g"
      evidence: { doc: "papers/sol_gel_TiO2.pdf", page: 5 }
    - field: "molar_mass"
      value: 159.69
      unit: "g/mol"
      evidence: { doc: "papers/sol_gel_TiO2.pdf", page: 5 }
  formula: "n = m / M"
  result: 0.02505
```

### 7.4 输出"阻止执行"状态

系统允许且必须能够输出 `blocked` 状态。当出现以下情况时，协议状态设为 `blocked`：

- 关键参数缺失且无法执行
- 安全审计发现不可接受风险
- 设备能力不匹配且无替代方案

```yaml
protocol_status: "blocked"   # ready | blocked | needs_review
block_reasons:
  - "calcination_temperature is null (critical)"
  - "closed-system heating detected without pressure relief"
```

### 7.5 平台无关

Skill 本身不依赖特定实验室设备厂商或自动化平台。输出协议使用通用原子操作词汇，设备绑定为可选层。在任意支持文件读取与结构化输出的 Agent 中均可运行。

## 8. 证据抽取规则

- **只抽取原文明确支持的内容**，不得添加原文未出现的数值或描述。
- **绑定定位信息**：页码（必填）、表格号、图号、段落序号。
- **evidence_type** 取值：
  - `explicit`：原文直接给出
  - `derived`：由 explicit 数据计算得到
  - `inferred`：基于上下文推断
- **confidence 评分**（0.0-1.0）：
  - 0.9-1.0：原文数值明确，无歧义
  - 0.7-0.89：原文有数值但需结合上下文理解
  - 0.5-0.69：原文描述模糊或需跨段落拼接
  - <0.5：高度不确定，标记为需人工确认

## 9. 单位与化学计量规则

### 支持的单位

| 物理量 | 接受单位 |
|--------|----------|
| 质量 | g, kg, mg |
| 体积 | mL, L, μL |
| 温度 | °C, K |
| 时间 | s, min, h |
| 浓度 | mol/L, g/mL, wt% |
| 搅拌速率 | rpm |
| 压力 | Pa, kPa, MPa, bar, atm |

### 单位转换

- 仅在 `derived` 类型中执行转换，转换因子必须可追溯。
- 转换前后值均保留，附推导记录。

### 化学计量校验

- 摩尔比必须由 explicit 质量和 explicit 摩尔质量计算。
- 若摩尔质量未在原文给出，使用标准摩尔质量表，标记为 `derived`。
- 校验不通过时（如摩尔比超出合理范围），标记为 `needs_review`。

## 10. 协议编译规则

### 原子操作列表

| 操作 | 关键参数 |
|------|----------|
| `weigh` | reagent, mass, vessel |
| `dissolve` | reagent, solvent, volume, vessel |
| `stir` | duration, rpm, temperature |
| `heat` | target_temp, ramp_rate, duration, atmosphere |
| `cool` | target_temp, method (natural/forced) |
| `add` | reagent, rate, duration, order |
| `wash` | solvent, volume, repetitions |
| `filter` | method (vacuum/centrifuge), duration |
| `dry` | temperature, duration, atmosphere |
| `collect` | method, target_phase |
| `calcine` | target_temp, ramp_rate, duration, atmosphere |
| `centrifuge` | rpm, duration, temperature |

### 步骤依赖图

```yaml
steps:
  - id: "step_01"
    operation: "weigh"
    depends_on: []
    parallel_group: null
  - id: "step_02"
    operation: "dissolve"
    depends_on: ["step_01"]
    parallel_group: null
  - id: "step_03"
    operation: "stir"
    depends_on: ["step_02"]
    parallel_group: "A"
  - id: "step_04"
    operation: "heat"
    depends_on: ["step_02"]
    parallel_group: "A"   # 与 step_03 并行
```

- `depends_on` 为空表示起始步骤。
- 同一 `parallel_group` 内的步骤可并行执行。
- 无 `parallel_group` 的步骤默认串行。

## 11. 安全与可执行性规则

| 检查项 | 规则 | 处置 |
|--------|------|------|
| 温度超限 | 操作温度 > 设备上限 或 > 1000°C 且无专用设备 | blocked |
| 密闭加热 | 密闭容器中加热且无压力释放描述 | blocked |
| 不相容试剂 | 强氧化剂 + 强还原剂 / 强酸 + 强碱混合无缓冲 | blocked |
| 通风橱需求 | 涉及挥发性/有毒气体且无通风描述 | needs_review |
| 惰性气氛需求 | 涉及空气敏感材料且无惰性气氛描述 | needs_review |
| 高压操作 | 压力 > 10 bar 且无高压设备 | blocked |

所有 `blocked` 项写入 `safety_report.md`，所有 `needs_review` 项标记为人工确认点。

## 12. 设备绑定规则

### 设备能力 YAML 格式

```yaml
devices:
  - id: "furnace_01"
    type: "muffle_furnace"
    max_temp: 1200            # °C
    atmosphere: ["air", "N2", "Ar"]
    ramp_rate_max: 10         # °C/min
  - id: "stirrer_01"
    type: "magnetic_stirrer"
    rpm_max: 1500
    temp_control: true
    max_temp: 350
```

### 能力检查逻辑

1. 遍历协议中每个步骤的设备需求。
2. 在 `lab_profile` 中查找匹配设备。
3. 校验：温度上限、转速上限、气氛支持、容量。
4. 匹配成功 → 绑定 `device_id`；匹配失败 → 标记 `device_mismatch`。

### 无设备信息时

输出设备无关协议，`device_id` 字段为 `null`，`safety_report.md` 中提示"未提供设备信息，安全检查基于通用规则执行"。

## 13. 缺失信息处理规则

### 缺失字段表

```yaml
missing_fields:
  - field: "calcination_temperature"
    location: "step_07"
    reason: "文献仅提及'煅烧处理'，未给温度"
    risk_level: "high"          # high | medium | low
    blocks_execution: true
    suggestion: "联系作者或参考文献中同类体系默认值，但需人工确认"
  - field: "stirring_rpm"
    location: "step_03"
    reason: "文献未提及搅拌速率"
    risk_level: "medium"
    blocks_execution: false
    suggestion: "可使用 300-500 rpm 范围，人工确认后填入"
```

### 风险等级定义

| 等级 | 定义 | 是否阻止执行 |
|------|------|--------------|
| high | 缺失该参数无法执行或存在安全风险 | 是 |
| medium | 缺失该参数影响复现精度但不阻止执行 | 否 |
| low | 缺失该参数影响较小 | 否 |

## 14. 可信度评分

对最终协议输出整体可信度评分（0.0-1.0）：

| 维度 | 权重 | 说明 |
|------|------|------|
| 证据覆盖率 | 0.30 | 有证据的字段占总字段比例 |
| explicit 占比 | 0.25 | explicit 字段占非 null 字段比例 |
| 安全通过率 | 0.25 | 非 blocked 检查项占比 |
| 缺失字段风险 | 0.20 | high 风险缺失字段扣分 |

```yaml
confidence_score:
  overall: 0.82
  dimensions:
    evidence_coverage: 0.90
    explicit_ratio: 0.85
    safety_pass_rate: 0.80
    missing_field_penalty: 0.70
```

## 15. 错误与降级策略

| 错误场景 | 处置 |
|----------|------|
| 文档无法解析 | 输出 `parse_error`，列出失败页码，不生成协议 |
| 部分信息缺失 | 正常生成协议，缺失字段设为 `null`，写入 `missing_conditions.md` |
| 设备不匹配 | 生成设备无关协议，`safety_report.md` 标记不匹配项 |
| 安全风险 | 生成协议但状态设为 `blocked`，`safety_report.md` 列出阻断原因 |
| 无实验方法章节 | 输出 `no_method_section`，不生成协议 |

## 16. 附属文件引用

详细规范拆分至 `references/` 目录：

| 文件 | 内容 |
|------|------|
| `references/data_model.md` | 数据模型与完整 JSON Schema 定义 |
| `references/safety_rules.md` | 安全规则详细条文与阈值表 |
| `references/device_schema.md` | 设备描述 Schema 与能力校验逻辑 |
| `references/examples.md` | 完整端到端示例（含输入输出） |
| `references/edge_cases.md` | 反例与边界案例处理 |

## 17. 最终检查清单

- [ ] SKILL.md frontmatter 合法（name/description 字段存在且符合规范）
- [ ] 每个步骤都有 evidence 绑定
- [ ] 缺失字段已标记为 `null` 并写入 `missing_conditions.md`
- [ ] 安全检查已执行并写入 `safety_report.md`
- [ ] 不存在静默补全（无证据的字段不得有确定值）
- [ ] `evidence_type` 仅取 explicit/derived/inferred
- [ ] inferred 字段已标记需人工确认
- [ ] 协议状态正确（ready/blocked/needs_review）
- [ ] 可信度评分已计算
- [ ] 恢复检查点方案已生成
