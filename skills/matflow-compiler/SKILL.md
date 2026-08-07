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
         │ 实验步骤不完整？
         │     │
         │  ┌──▼──────────────┐
         │  │ SI Retriever    │  提取 DOI → 下载 SI；
         │  │ (补充材料获取)   │  无 DOI → 按标题检索网页获取 SI
         │  └──┬──────────────┘
         │     │ 获取到 SI 后重新抽取证据
         └─────┘
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
10. **SI Retriever（补充材料获取）**：当 Evidence Extractor 发现实验步骤不完整时触发。提取论文 DOI，通过 DOI 解析出版商页面并下载 Supplementary Information（SI）；若 DOI 不可用，则按论文标题检索网页，从出版商页面定位并下载 SI。获取 SI 后将其作为补充文档输入，重新执行证据抽取。

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
| 实验步骤不完整 | 触发 SI Retriever 获取补充材料，重新抽取（见第 16 节） |
| OCR 扫描版 PDF | 检测 OCR 质量（good/moderate/poor）；质量为 poor 时调用 MinerU 进行高质量 OCR；MinerU 不可用时尝试基本修复；在缺失报告中提示"文本可能包含识别错误" |
| 纯扫描版 PDF（无文字层） | 输出 `scan_only_pdf`，调用 MinerU OCR 模式处理；MinerU 不可用时标记无法解析，建议安装 MinerU (pip install mineru) |

## 16. 补充材料（SI）自动获取

> 当 Evidence Extractor 判定主文档中实验步骤不完整（关键参数缺失率 >30% 或核心操作步骤缺失），自动触发 SI Retriever。详细策略见 `references/si_retrieval.md`，可执行脚本见 `scripts/retrieve_si.py`。

### 16.1 触发条件

- 缺失字段比例 > 30%
- 核心操作步骤（如合成、固化）缺失
- 实验方法章节存在但不完整

### 16.2 获取流程

```
论文 PDF → 提取 DOI → Crossref 验证 → 解析出版商页面 → 下载 SI → 解析 SI 内容
                ↓ (DOI 不可用)
          按标题检索 → Crossref/Scholar 匹配 → 出版商页面 → 下载 SI
```

- **DOI 提取优先级**：PDF 元数据 > 正文正则匹配 > 首脚注扫描
- **DOI 验证**：通过 Crossref API (`https://api.crossref.org/works/{doi}`) 验证
- **出版商适配**：ACS/RSC/Wiley/Elsevier/Springer/Nature，按 DOI 前缀自动识别
- **标题检索回退**：DOI 不可用时，从 PDF 首页提取标题，通过 Crossref 标题搜索匹配

### 16.3 SI 获取后

将 SI 作为补充文档加入 `source_documents`，重新执行证据抽取。SI 中的证据标注 `source_type: supplementary_information`。

### 16.4 SI 获取失败

不阻塞流程。在 `missing_conditions.md` 标注"已尝试获取 SI 但未成功"，继续基于主文档生成协议，缺失字段保持 `null`。

### 16.5 网络访问约束

仅访问公开科学数据源白名单（doi.org、api.crossref.org、出版商官网）。若沙箱网络受限，SI 获取自动跳过并降级。

## 17. 附属文件引用

详细规范拆分至 `references/` 目录：

| 文件 | 内容 |
|------|------|
| `references/data_model.md` | 数据模型与完整 JSON Schema 定义 |
| `references/safety_rules.md` | 安全规则详细条文与阈值表 |
| `references/device_schema.md` | 设备描述 Schema 与能力校验逻辑 |
| `references/edge_cases.md` | 反例与边界案例处理 |
| `references/si_retrieval.md` | 补充材料获取策略与出版商适配详情 |

## 18. 评测案例（Examples）

`examples/` 目录包含 9 组真实文献编译案例，每组包含 6 个输出文件（protocol.json/yaml、sop.md、missing.md、safety.md、recovery.yaml）：

### 论文案例（4组）
| 案例 | 文献来源 | 材料类型 | 核心特点 |
|------|---------|---------|---------|
| `cui_kessler_2012_*` | Cui & Kessler (2012) | 聚脲/聚氨酯 | 多步聚合反应，分子量控制 |
| `zhou_2020_*` | Zhou et al. (2020) | TiO2-SiO2 Janus 材料 | 溶胶-凝胶法，Pickering 乳液 |
| `yiwen_2022_*` | Yiwen et al. (2022) | 环氧/CFRP 复合材料 | 机械性能优化，工业应用导向 |
| `alder_1938_*` | Alder & Rickert (1938) | Diels-Alder 加合物 | **德语 OCR 文档**，历史文献，高压反应风险 |

### 专利案例（2组）
| 案例 | 文献来源 | 材料类型 | 核心特点 |
|------|---------|---------|---------|
| `cn110577629b_*` | CN110577629B | 可降解环氧树脂 | 光固化，巯基-烯反应，DMDC 固化剂 |
| `cn113574101a_*` | CN113574101A | 卤化硼回收 CFRP | 复合材料回收，纤维再利用 |

### TDS 案例（2组）
| 案例 | 文献来源 | 材料类型 | 核心特点 |
|------|---------|---------|---------|
| `k80_tds_*` | Trigonox K-80 TDS | 过氧化氢异丙苯糊 | 自由基引发剂，SADT 75°C，安全储存 |
| `sivo560_tds_*` | Dynasylan SIVO 560 TDS | 硅烷偶联剂 | 水解活化，24小时使用窗口 |

### 案例统计
- **总计**: 9 组案例，54 个输出文件
- **验证状态**: 全部 9 组通过验证（WARN 状态，无 FAIL）
- **覆盖场景**: 论文/专利/TDS、中文/英文/德文、常温/高温/高压、合成/回收/应用

## 19. Schema 验证与常见问题修复

### 19.1 验证工具

使用 `scripts/validate_protocol.py` 验证生成的 protocol.json 是否符合 schema：

```bash
python scripts/validate_protocol.py examples/your_protocol.json
```

**验证检查项**（共 9 项）：
1. 协议顶层结构检查
2. 步骤字段检查
3. 证据字段完整性检查
4. 置信度范围检查
5. 缺失字段 risk_level 检查
6. 单位一致性检查
7. 步骤依赖完整性检查
8. 静默补全检测
9. 安全检查与检查点引用检查

### 19.2 常见 Schema 问题与修复方法

#### 问题 1：非标准 action 类型

**错误示例**：
```json
{
  "step_id": "S01",
  "action": "photoirradiate",  // ❌ 非标准
  "status": "ok"               // ❌ 非标准
}
```

**修复方法**：
```json
{
  "step_id": "S01",
  "action": "heat",            // ✅ 标准 action
  "status": "ready"            // ✅ 标准 status
}
```

**标准 action 类型**（18 种）：
- `weigh` - 称量
- `dissolve` - 溶解
- `stir` - 搅拌
- `heat` - 加热
- `cool` - 冷却
- `add` - 加入
- `drop` - 滴加
- `wash` - 洗涤
- `filter` - 过滤
- `centrifuge` - 离心
- `dry` - 干燥
- `collect` - 收集
- `transfer` - 转移
- `purge` - 吹扫
- `evacuate` - 抽空
- `measure` - 测量
- `wait` - 等待
- `quench` - 淬灭

**标准 status 值**（4 种）：
- `ready` - 可执行
- `warning` - 警告（可执行但需注意）
- `blocked` - 阻塞（不可执行）
- `inferred` - 推断（需人工确认）

#### 问题 2：evidence 字段缺失

**错误示例**：
```json
{
  "evidence": [
    {
      "patent": "DOC-CN01",    // ❌ 应为 document
      "section": "实施例1",
      "quote": "..."
      // ❌ 缺少 page 字段
    }
  ]
}
```

**修复方法**：
```json
{
  "evidence": [
    {
      "document": "DOC-CN01",  // ✅ 使用 document
      "page": 1,               // ✅ 添加 page
      "section": "实施例1",
      "quote": "...",
      "evidence_type": "explicit",
      "confidence": 0.95
    }
  ]
}
```

**evidence 必需字段**：
- `document` - 源文档 ID（对应 source_documents[].doc_id）
- `page` - 页码（从 1 开始的整数）
- `quote` - 原文引用片段
- `evidence_type` - explicit/derived/inferred
- `confidence` - 置信度（0.0-1.0）

#### 问题 3：inferred 字段未标记 require_confirmation

**错误示例**：
```json
{
  "missing_fields": [
    {
      "field_name": "temperature.value",
      "suggestion": "60°C",
      "requires_confirmation": false  // ❌ inferred 字段应为 true
    }
  ]
}
```

**修复方法**：
```json
{
  "missing_fields": [
    {
      "field_name": "temperature.value",
      "suggestion": "60°C",
      "requires_confirmation": true   // ✅ 必须标记为 true
    }
  ]
}
```

**规则**：所有包含 `suggestion` 的 `missing_fields` 必须标记 `requires_confirmation: true`，防止静默补全。

#### 问题 4：safety_check 的 target_step 引用错误

**错误示例**：
```json
{
  "safety_checks": [
    {
      "check_id": "SAFE-001",
      "target_step": "S02/BBr3 mention"  // ❌ 包含非法字符
    }
  ]
}
```

**修复方法**：
```json
{
  "safety_checks": [
    {
      "check_id": "SAFE-001",
      "target_step": "S02"               // ✅ 只使用步骤 ID
    }
  ]
}
```

**规则**：`target_step` 必须是存在的步骤 ID（如 S01、S02），不能包含 `/`、`-` 等特殊字符。

### 19.3 自动修复脚本

可以使用以下 Python 脚本自动修复常见问题：

```python
import json

def fix_protocol(protocol_path):
    with open(protocol_path, 'r', encoding='utf-8') as f:
        protocol = json.load(f)
    
    # 修复 action 类型
    ACTION_MAPPING = {
        "photoirradiate": "heat",
        "precipitate": "filter",
        "cure": "heat",
        "mix": "stir",
        # ... 更多映射
    }
    
    for step in protocol.get('steps', []):
        if step.get('action') in ACTION_MAPPING:
            step['action'] = ACTION_MAPPING[step['action']]
        
        # 修复 status
        if step.get('status') == 'ok':
            step['status'] = 'ready'
        
        # 修复 evidence
        for ev in step.get('evidence', []):
            if 'patent' in ev:
                ev['document'] = ev.pop('patent')
            if 'page' not in ev:
                ev['page'] = 1
        
        # 修复 missing_fields
        for mf in step.get('missing_fields', []):
            if 'suggestion' in mf and 'requires_confirmation' not in mf:
                mf['requires_confirmation'] = True
    
    # 保存修复后的文件
    with open(protocol_path, 'w', encoding='utf-8') as f:
        json.dump(protocol, f, ensure_ascii=False, indent=2)
```

### 19.4 验证最佳实践

1. **生成后立即验证**：每次生成 protocol.json 后立即运行验证脚本
2. **修复所有 FAIL**：确保没有 FAIL 级别的错误
3. **审查 WARN**：WARNING 级别的提示也应尽量修复
4. **批量验证**：使用脚本批量验证所有案例
5. **持续集成**：将验证脚本集成到 CI/CD 流程中

### 19.5 常见验证结果解读

| 结果 | 含义 | 处理方式 |
|------|------|---------|
| PASS | 完全通过 | 无需处理 |
| WARN | 有警告但无失败 | 建议修复警告项 |
| FAIL | 有失败项 | 必须修复所有失败项 |

**警告示例**：
- `protocol_id` 格式不符合规范（不影响功能）
- `step_id` 格式不符合 S<序号> 格式（不影响功能）
- 含有 inferred 类型证据但状态为 'blocked'（建议设为 'inferred'）

**失败示例**：
- 缺少必需字段（如 document、page）
- 非标准 action 类型
- 非标准 status 值
- inferred 字段未标记 require_confirmation

## 20. 最终检查清单

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
- [ ] 若实验步骤不完整，已尝试触发 SI Retriever 获取补充材料
- [ ] SI 获取结果（成功/失败）已记录在 missing_conditions.md 中
