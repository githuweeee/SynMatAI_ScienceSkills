# 材料实验数据模型与 JSON/YAML Schema 文档

> 本文档定义 matflow-compiler 中材料实验协议（Protocol）的完整数据模型，包括顶层结构、步骤结构、原子操作、证据链、缺失字段、安全检查与检查点等。所有字段均以 JSON Schema 形式给出，并辅以 YAML 等价表示与完整示例。

---

## 目录

1. [协议顶层结构](#1-协议顶层结构)
2. [步骤(Step)结构](#2-步骤step结构)
3. [原子操作定义](#3-原子操作定义)
4. [证据(Evidence)结构](#4-证据evidence结构)
5. [缺失字段(MissingField)结构](#5-缺失字段missingfield结构)
6. [安全检查(SafetyCheck)结构](#6-安全检查safetycheck结构)
7. [检查点(Checkpoint)结构](#7-检查点checkpoint结构)
8. [JSON Schema 定义](#8-json-schema-定义)

---

## 1. 协议顶层结构

协议（Protocol）是 matflow-compiler 编译产物的顶层容器，描述一个完整的材料合成或处理流程。顶层结构由以下字段组成：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `protocol_id` | string | 是 | 协议唯一标识，格式为 `PROTO-<material>-<hash8>`，例如 `PROTO-EPOXY-a1b2c3d4` |
| `material` | string | 是 | 目标材料名称，如 `环氧树脂`、`ROMP-聚降冰片烯` |
| `source_documents` | array | 是 | 源文档列表，每项含 `doc_id`、`title`、`file_path`、`doc_type`（patent/tds/paper） |
| `steps` | array | 是 | 有序步骤列表，至少 1 项 |
| `reagents` | array | 否 | 试剂清单，汇总全流程使用的试剂 |
| `equipment` | array | 否 | 设备清单，汇总全流程使用的设备 |
| `metadata` | object | 是 | 元数据，含版本、生成时间、编译器版本等 |
| `safety_checks` | array | 否 | 安全检查结果列表 |
| `checkpoints` | array | 否 | 检查点定义列表 |
| `overall_confidence` | number | 否 | 全流程综合置信度，0.0~1.0 |
| `overall_status` | string | 否 | 全流程状态：`ready` / `warning` / `blocked` |

### 顶层结构 YAML 等价表示

```yaml
protocol_id: PROTO-EPOXY-a1b2c3d4
material: 环氧树脂
source_documents:
  - doc_id: DOC-001
    title: 一种可降解的环氧树脂及其制备方法
    file_path: PATENT/CN110577629B-一种可降解的环氧树脂及其制备方法-授权.PDF
    doc_type: patent
steps: []
reagents: []
equipment: []
metadata:
  version: "1.0.0"
  generated_at: "2026-08-06T10:00:00Z"
  compiler_version: matflow-compiler/0.3.0
  source_hash: sha256:...
safety_checks: []
checkpoints: []
overall_confidence: 0.92
overall_status: ready
```

---

## 2. 步骤(Step)结构

每个步骤描述一个原子操作及其参数。步骤是协议的最小可执行单元，必须可被设备直接执行或被人工按指令完成。

### 字段定义

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `step_id` | string | 是 | 步骤唯一标识，格式 `S<序号>`，如 `S01`、`S02` |
| `action` | string | 是 | 原子操作类型，见[第 3 节](#3-原子操作定义) |
| `material` | string | 否 | 操作对象材料名称（如 `双酚A`、`环氧氯丙烷`） |
| `amount` | object | 否 | 用量，含 `value`、`unit`、`relative_to`（可选） |
| `temperature` | object | 否 | 温度，含 `value`、`unit`、`ramp_rate`（可选）、`hold`（可选） |
| `duration` | object | 否 | 持续时间，含 `value`、`unit` |
| `stirring_speed` | object | 否 | 搅拌速度，含 `value`、`unit` |
| `atmosphere` | string | 否 | 气氛：`air` / `nitrogen` / `argon` / `vacuum` |
| `pressure` | object | 否 | 压力，含 `value`、`unit` |
| `evidence` | array | 是 | 证据链，至少 1 项，见[第 4 节](#4-证据evidence结构) |
| `confidence` | number | 是 | 本步骤置信度，0.0~1.0 |
| `status` | string | 是 | 步骤状态：`ready` / `warning` / `blocked` / `inferred` |
| `missing_fields` | array | 否 | 缺失字段列表，见[第 5 节](#5-缺失字段missingfield结构) |
| `device_binding` | object | 否 | 设备绑定信息，含 `device_id`、`capability_check` |
| `notes` | string | 否 | 人工备注 |

### 步骤状态语义

| 状态 | 含义 | 是否可执行 |
|------|------|-----------|
| `ready` | 所有参数完整且通过安全检查 | 是 |
| `warning` | 存在非阻塞性问题（如低置信度、非关键缺失） | 是（需人工留意） |
| `blocked` | 存在阻塞性缺失或安全检查未通过 | 否 |
| `inferred` | 关键参数由推断得出，需人工确认后方可执行 | 否（待确认） |

### 步骤示例

```json
{
  "step_id": "S03",
  "action": "heat",
  "material": "反应混合物",
  "temperature": {
    "value": 80,
    "unit": "celsius",
    "ramp_rate": { "value": 2, "unit": "celsius_per_minute" },
    "hold": true
  },
  "duration": { "value": 2, "unit": "hour" },
  "stirring_speed": { "value": 300, "unit": "rpm" },
  "atmosphere": "nitrogen",
  "evidence": [
    {
      "document": "DOC-001",
      "page": 5,
      "section": "实施例1",
      "quote": "将反应体系升温至80℃，保温2小时",
      "evidence_type": "explicit",
      "confidence": 0.98
    }
  ],
  "confidence": 0.98,
  "status": "ready",
  "missing_fields": [],
  "device_binding": {
    "device_id": "DEV-HOTPLATE-01",
    "capability_check": "passed"
  }
}
```

---

## 3. 原子操作定义

matflow-compiler 将文献中的自然语言实验描述编译为以下 18 种原子操作。每个原子操作有明确的输入参数约束与设备能力需求。

| 操作 | 标识 | 必需参数 | 可选参数 | 典型设备 |
|------|------|---------|---------|---------|
| 称量 | `weigh` | material, amount | tolerance | balance |
| 溶解 | `dissolve` | material, solvent, amount | temperature | reactor |
| 搅拌 | `stir` | duration | stirring_speed, temperature | hotplate_stirrer |
| 加热 | `heat` | temperature | duration, ramp_rate, atmosphere | hotplate_stirrer / reactor / oven |
| 冷却 | `cool` | target_temperature | duration, cooling_rate | reactor |
| 加入 | `add` | material, amount | addition_rate, dropwise | reactor |
| 滴加 | `drop` | material, amount, addition_rate | temperature | reactor |
| 洗涤 | `wash` | solvent, amount | repeat_count | reactor |
| 过滤 | `filter` | filter_medium | vacuum_applied | fume_hood |
| 离心 | `centrifuge` | speed, duration | temperature | centrifuge |
| 干燥 | `dry` | method(vacuum/thermal) | temperature, duration | vacuum_oven / oven |
| 收集 | `collect` | target_container | yield | glovebox |
| 转移 | `transfer` | source, destination | atmosphere | glovebox |
| 吹扫 | `purge` | gas_type, duration | flow_rate | reactor / glovebox |
| 抽空 | `evacuate` | target_pressure | duration | reactor / vacuum_oven |
| 测量 | `measure` | measurement_type | instrument | spectrometer / balance |
| 等待 | `wait` | duration | temperature | - |
| 淬灭 | `quench` | quench_agent, amount | temperature | reactor |

### 原子操作参数约束

每个原子操作在 JSON Schema 中以 `oneOf` 分支定义，确保不同操作接受不同的参数集合。例如 `heat` 操作要求 `temperature` 必填，而 `weigh` 操作要求 `amount` 必填且 `amount.unit` 必须为质量单位（`g`、`mg`、`kg`）。

---

## 4. 证据(Evidence)结构

证据链是 matflow-compiler 的核心设计原则之一：**每个参数都必须可追溯到源文档的具体位置**。没有证据的参数不得静默补全。

### 字段定义

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `document` | string | 是 | 源文档 ID，对应顶层 `source_documents[].doc_id` |
| `page` | integer | 是 | 页码（从 1 开始） |
| `section` | string | 否 | 章节标题或编号，如 `实施例1`、`3.2 合成步骤` |
| `quote` | string | 是 | 原文引用片段，保留原始语言 |
| `evidence_type` | string | 是 | `explicit` / `derived` / `inferred` |
| `confidence` | number | 是 | 该证据的置信度，0.0~1.0 |
| `derivation` | string | 否 | 当 `evidence_type` 为 `derived` 或 `inferred` 时的推导过程说明 |

### 证据类型语义

| 类型 | 含义 | 置信度范围 | 处理方式 |
|------|------|-----------|---------|
| `explicit` | 文档中明确写出的数值或描述 | 0.90~1.00 | 直接采用 |
| `derived` | 由文档中明确信息经简单换算或逻辑推导得出（如单位换算、摩尔质量换算） | 0.75~0.95 | 采用，但在 `derivation` 中记录推导过程 |
| `inferred` | 文档未直接给出，基于上下文、常识或类比推断 | 0.40~0.75 | **必须人工确认**，步骤状态置为 `inferred` |

### 证据示例

```json
{
  "document": "DOC-001",
  "page": 5,
  "section": "实施例1",
  "quote": "称取双酚A 22.8g（0.1mol）",
  "evidence_type": "explicit",
  "confidence": 0.99
}
```

```json
{
  "document": "DOC-002",
  "page": 3,
  "section": "表1 配方",
  "quote": "环氧当量 185-195",
  "evidence_type": "derived",
  "confidence": 0.88,
  "derivation": "由环氧当量范围中值190与目标分子量计算所需环氧树脂质量"
}
```

```json
{
  "document": "DOC-001",
  "page": 6,
  "section": "实施例1",
  "quote": "反应在氮气保护下进行",
  "evidence_type": "inferred",
  "confidence": 0.60,
  "derivation": "文献仅提及氮气保护，未明确流量与吹扫时长，按常规经验推断流量50mL/min、吹扫15min"
}
```

---

## 5. 缺失字段(MissingField)结构

当编译器检测到某步骤的关键参数在源文档中缺失时，必须生成 `MissingField` 记录。**严禁静默补全缺失的关键参数**。

### 字段定义

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `field_name` | string | 是 | 缺失字段路径，如 `temperature.value`、`amount.value` |
| `step_id` | string | 是 | 所属步骤 ID |
| `risk_level` | string | 是 | `high` / `medium` / `low` |
| `blocks_execution` | boolean | 是 | 是否阻塞执行 |
| `suggestion` | string | 否 | 编译器给出的建议值或获取途径 |
| `suggestion_source` | string | 否 | 建议来源：`literature_default` / `device_default` / `safety_rule` |
| `requires_confirmation` | boolean | 否 | 是否需要人工确认 |

### 风险等级判定

| 风险等级 | 判定条件 | blocks_execution |
|---------|---------|-------------------|
| `high` | 缺失温度、用量、时间等直接影响反应结果与安全的参数 | true |
| `medium` | 缺失搅拌速度、气氛流量等次要参数 | false |
| `low` | 缺失备注、非关键容差等 | false |

### 缺失字段示例

```json
{
  "field_name": "temperature.value",
  "step_id": "S05",
  "risk_level": "high",
  "blocks_execution": true,
  "suggestion": "文献中同类反应通常在60-80℃进行",
  "suggestion_source": "literature_default",
  "requires_confirmation": true
}
```

---

## 6. 安全检查(SafetyCheck)结构

安全检查在编译阶段对全流程进行静态分析，识别潜在安全风险。

### 字段定义

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `check_id` | string | 是 | 检查项唯一标识，如 `SAFE-001` |
| `check_type` | string | 是 | 检查类型，见 `safety_rules.md` |
| `rule_id` | string | 是 | 触发的安全规则 ID |
| `target_step` | string | 是 | 被检查的步骤 ID |
| `status` | string | 是 | `pass` / `warning` / `blocked` |
| `message` | string | 是 | 人类可读的检查结果描述 |
| `details` | object | 否 | 附加详情（如实际值、阈值等） |

### 安全检查示例

```json
{
  "check_id": "SAFE-003",
  "check_type": "temperature_limit",
  "rule_id": "TEMP-001",
  "target_step": "S04",
  "status": "blocked",
  "message": "步骤S04温度200℃超过设备DEV-HOTPLATE-01上限180℃",
  "details": {
    "actual_value": 200,
    "limit_value": 180,
    "unit": "celsius",
    "device_id": "DEV-HOTPLATE-01"
  }
}
```

---

## 7. 检查点(Checkpoint)结构

检查点定义在关键步骤后保存系统状态，以便在异常中断后恢复执行。

### 字段定义

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `checkpoint_id` | string | 是 | 检查点唯一标识，如 `CP-01` |
| `after_step` | string | 是 | 在此步骤完成后创建检查点 |
| `stored_state` | array | 是 | 保存的状态变量列表 |
| `recovery_policy` | object | 是 | 恢复策略 |
| `recovery_policy.power_failure` | string | 是 | 断电恢复策略：`resume_from_checkpoint` / `restart_step` / `abort` |
| `recovery_policy.temperature_deviation` | object | 是 | 温度偏差恢复策略 |
| `recovery_policy.temperature_deviation.threshold` | number | 是 | 允许的偏差阈值（℃） |
| `recovery_policy.temperature_deviation.action` | string | 是 | 超阈值动作：`continue` / `hold` / `alert` / `abort` |

### stored_state 元素结构

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 状态变量名，如 `current_temperature`、`step_progress` |
| `type` | string | 变量类型：`number` / `string` / `boolean` / `enum` |
| `unit` | string | 单位（如适用） |

### 检查点示例

```json
{
  "checkpoint_id": "CP-02",
  "after_step": "S06",
  "stored_state": [
    { "name": "current_temperature", "type": "number", "unit": "celsius" },
    { "name": "step_progress", "type": "number" },
    { "name": "atmosphere_status", "type": "enum" },
    { "name": "reagent_remaining", "type": "number", "unit": "g" }
  ],
  "recovery_policy": {
    "power_failure": "resume_from_checkpoint",
    "temperature_deviation": {
      "threshold": 5,
      "action": "hold"
    }
  }
}
```

---

## 8. JSON Schema 定义

以下是 `protocol.json` 的完整 JSON Schema（Draft 2020-12）。

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://matflow-compiler/schemas/protocol.json",
  "title": "Material Experiment Protocol",
  "type": "object",
  "required": ["protocol_id", "material", "source_documents", "steps", "metadata"],
  "properties": {
    "protocol_id": {
      "type": "string",
      "pattern": "^PROTO-[A-Z0-9]+-[a-f0-9]{8}$",
      "description": "协议唯一标识"
    },
    "material": {
      "type": "string",
      "minLength": 1,
      "description": "目标材料名称"
    },
    "source_documents": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["doc_id", "title", "file_path", "doc_type"],
        "properties": {
          "doc_id": { "type": "string", "pattern": "^DOC-\\d{3}$" },
          "title": { "type": "string" },
          "file_path": { "type": "string" },
          "doc_type": { "enum": ["patent", "tds", "paper", "manual", "other"] }
        }
      }
    },
    "steps": {
      "type": "array",
      "minItems": 1,
      "items": { "$ref": "#/$defs/step" }
    },
    "reagents": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "role"],
        "properties": {
          "name": { "type": "string" },
          "cas_number": { "type": "string" },
          "role": { "enum": ["monomer", "crosslinker", "catalyst", "solvent", "initiator", "additive", "quench_agent"] },
          "total_amount": { "$ref": "#/$defs/amount" },
          "hazard_class": { "type": "string" }
        }
      }
    },
    "equipment": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["device_id", "device_type"],
        "properties": {
          "device_id": { "type": "string", "pattern": "^DEV-[A-Z]+-\\d{2}$" },
          "device_type": { "$ref": "#/$defs/device_type" },
          "device_name": { "type": "string" },
          "config_path": { "type": "string", "description": "设备描述YAML文件路径" }
        }
      }
    },
    "metadata": {
      "type": "object",
      "required": ["version", "generated_at", "compiler_version"],
      "properties": {
        "version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
        "generated_at": { "type": "string", "format": "date-time" },
        "compiler_version": { "type": "string" },
        "source_hash": { "type": "string" },
        "operator": { "type": "string" },
        "lab_id": { "type": "string" }
      }
    },
    "safety_checks": {
      "type": "array",
      "items": { "$ref": "#/$defs/safety_check" }
    },
    "checkpoints": {
      "type": "array",
      "items": { "$ref": "#/$defs/checkpoint" }
    },
    "overall_confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "overall_status": {
      "enum": ["ready", "warning", "blocked"]
    }
  },
  "$defs": {
    "step": {
      "type": "object",
      "required": ["step_id", "action", "evidence", "confidence", "status"],
      "properties": {
        "step_id": { "type": "string", "pattern": "^S\\d{2}$" },
        "action": {
          "enum": ["weigh", "dissolve", "stir", "heat", "cool", "add", "drop", "wash", "filter", "centrifuge", "dry", "collect", "transfer", "purge", "evacuate", "measure", "wait", "quench"]
        },
        "material": { "type": "string" },
        "amount": { "$ref": "#/$defs/amount" },
        "temperature": { "$ref": "#/$defs/temperature" },
        "duration": { "$ref": "#/$defs/duration" },
        "stirring_speed": { "$ref": "#/$defs/stirring_speed" },
        "atmosphere": { "enum": ["air", "nitrogen", "argon", "vacuum"] },
        "pressure": { "$ref": "#/$defs/pressure" },
        "evidence": {
          "type": "array",
          "minItems": 1,
          "items": { "$ref": "#/$defs/evidence" }
        },
        "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
        "status": { "enum": ["ready", "warning", "blocked", "inferred"] },
        "missing_fields": {
          "type": "array",
          "items": { "$ref": "#/$defs/missing_field" }
        },
        "device_binding": {
          "type": "object",
          "properties": {
            "device_id": { "type": "string" },
            "capability_check": { "enum": ["passed", "failed", "unchecked"] }
          }
        },
        "notes": { "type": "string" }
      }
    },
    "amount": {
      "type": "object",
      "required": ["value", "unit"],
      "properties": {
        "value": { "type": "number", "exclusiveMinimum": 0 },
        "unit": { "enum": ["g", "mg", "kg", "mL", "L", "mol", "mmol", "wt%", "vol%", "eq"] },
        "relative_to": { "type": "string", "description": "当unit为eq或%时，参照物step_id或reagent name" },
        "tolerance": { "type": "number", "minimum": 0 }
      }
    },
    "temperature": {
      "type": "object",
      "required": ["value", "unit"],
      "properties": {
        "value": { "type": "number" },
        "unit": { "enum": ["celsius", "fahrenheit", "kelvin"] },
        "ramp_rate": {
          "type": "object",
          "required": ["value", "unit"],
          "properties": {
            "value": { "type": "number" },
            "unit": { "enum": ["celsius_per_minute", "celsius_per_hour"] }
          }
        },
        "hold": { "type": "boolean" }
      }
    },
    "duration": {
      "type": "object",
      "required": ["value", "unit"],
      "properties": {
        "value": { "type": "number", "exclusiveMinimum": 0 },
        "unit": { "enum": ["second", "minute", "hour", "day"] }
      }
    },
    "stirring_speed": {
      "type": "object",
      "required": ["value", "unit"],
      "properties": {
        "value": { "type": "number", "minimum": 0 },
        "unit": { "enum": ["rpm"] }
      }
    },
    "pressure": {
      "type": "object",
      "required": ["value", "unit"],
      "properties": {
        "value": { "type": "number" },
        "unit": { "enum": ["mbar", "bar", "kPa", "MPa", "atm", "torr"] }
      }
    },
    "evidence": {
      "type": "object",
      "required": ["document", "page", "quote", "evidence_type", "confidence"],
      "properties": {
        "document": { "type": "string" },
        "page": { "type": "integer", "minimum": 1 },
        "section": { "type": "string" },
        "quote": { "type": "string", "minLength": 1 },
        "evidence_type": { "enum": ["explicit", "derived", "inferred"] },
        "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
        "derivation": { "type": "string" }
      }
    },
    "missing_field": {
      "type": "object",
      "required": ["field_name", "step_id", "risk_level", "blocks_execution"],
      "properties": {
        "field_name": { "type": "string" },
        "step_id": { "type": "string" },
        "risk_level": { "enum": ["high", "medium", "low"] },
        "blocks_execution": { "type": "boolean" },
        "suggestion": { "type": "string" },
        "suggestion_source": { "enum": ["literature_default", "device_default", "safety_rule"] },
        "requires_confirmation": { "type": "boolean" }
      }
    },
    "safety_check": {
      "type": "object",
      "required": ["check_id", "check_type", "rule_id", "target_step", "status", "message"],
      "properties": {
        "check_id": { "type": "string", "pattern": "^SAFE-\\d{3}$" },
        "check_type": { "type": "string" },
        "rule_id": { "type": "string" },
        "target_step": { "type": "string" },
        "status": { "enum": ["pass", "warning", "blocked"] },
        "message": { "type": "string" },
        "details": { "type": "object" }
      }
    },
    "checkpoint": {
      "type": "object",
      "required": ["checkpoint_id", "after_step", "stored_state", "recovery_policy"],
      "properties": {
        "checkpoint_id": { "type": "string", "pattern": "^CP-\\d{2}$" },
        "after_step": { "type": "string" },
        "stored_state": {
          "type": "array",
          "minItems": 1,
          "items": {
            "type": "object",
            "required": ["name", "type"],
            "properties": {
              "name": { "type": "string" },
              "type": { "enum": ["number", "string", "boolean", "enum"] },
              "unit": { "type": "string" }
            }
          }
        },
        "recovery_policy": {
          "type": "object",
          "required": ["power_failure", "temperature_deviation"],
          "properties": {
            "power_failure": { "enum": ["resume_from_checkpoint", "restart_step", "abort"] },
            "temperature_deviation": {
              "type": "object",
              "required": ["threshold", "action"],
              "properties": {
                "threshold": { "type": "number" },
                "action": { "enum": ["continue", "hold", "alert", "abort"] }
              }
            }
          }
        }
      }
    },
    "device_type": {
      "enum": ["hotplate_stirrer", "reactor", "oven", "centrifuge", "vacuum_oven", "glovebox", "fume_hood", "balance", "spectrometer"]
    }
  }
}
```

---

## 完整 JSON 示例

以下是一个完整的 `protocol.json` 示例，展示环氧树脂合成协议：

```json
{
  "protocol_id": "PROTO-EPOXY-a1b2c3d4",
  "material": "可降解环氧树脂",
  "source_documents": [
    {
      "doc_id": "DOC-001",
      "title": "一种可降解的环氧树脂及其制备方法",
      "file_path": "PATENT/CN110577629B-一种可降解的环氧树脂及其制备方法-授权.PDF",
      "doc_type": "patent"
    },
    {
      "doc_id": "DOC-002",
      "title": "K-80 TDS",
      "file_path": "TDS/216. K-80 TDS CN上海睿哲化工.pdf",
      "doc_type": "tds"
    }
  ],
  "steps": [
    {
      "step_id": "S01",
      "action": "weigh",
      "material": "双酚A",
      "amount": { "value": 22.8, "unit": "g", "tolerance": 0.1 },
      "evidence": [
        {
          "document": "DOC-001",
          "page": 5,
          "section": "实施例1",
          "quote": "称取双酚A 22.8g（0.1mol）",
          "evidence_type": "explicit",
          "confidence": 0.99
        }
      ],
      "confidence": 0.99,
      "status": "ready",
      "missing_fields": [],
      "device_binding": {
        "device_id": "DEV-BALANCE-01",
        "capability_check": "passed"
      }
    },
    {
      "step_id": "S02",
      "action": "dissolve",
      "material": "双酚A",
      "amount": { "value": 100, "unit": "mL" },
      "temperature": { "value": 25, "unit": "celsius" },
      "evidence": [
        {
          "document": "DOC-001",
          "page": 5,
          "section": "实施例1",
          "quote": "溶于100mL丙酮中",
          "evidence_type": "explicit",
          "confidence": 0.97
        }
      ],
      "confidence": 0.97,
      "status": "ready",
      "missing_fields": [],
      "device_binding": {
        "device_id": "DEV-REACTOR-01",
        "capability_check": "passed"
      }
    },
    {
      "step_id": "S03",
      "action": "heat",
      "material": "反应混合物",
      "temperature": {
        "value": 80,
        "unit": "celsius",
        "ramp_rate": { "value": 2, "unit": "celsius_per_minute" },
        "hold": true
      },
      "duration": { "value": 2, "unit": "hour" },
      "stirring_speed": { "value": 300, "unit": "rpm" },
      "atmosphere": "nitrogen",
      "evidence": [
        {
          "document": "DOC-001",
          "page": 5,
          "section": "实施例1",
          "quote": "将反应体系升温至80℃，保温2小时",
          "evidence_type": "explicit",
          "confidence": 0.98
        }
      ],
      "confidence": 0.98,
      "status": "ready",
      "missing_fields": [],
      "device_binding": {
        "device_id": "DEV-HOTPLATE-01",
        "capability_check": "passed"
      }
    },
    {
      "step_id": "S04",
      "action": "cool",
      "material": "反应混合物",
      "temperature": { "value": 25, "unit": "celsius" },
      "evidence": [
        {
          "document": "DOC-001",
          "page": 5,
          "section": "实施例1",
          "quote": "冷却至室温",
          "evidence_type": "explicit",
          "confidence": 0.95
        }
      ],
      "confidence": 0.95,
      "status": "ready",
      "missing_fields": [],
      "device_binding": {
        "device_id": "DEV-REACTOR-01",
        "capability_check": "passed"
      }
    },
    {
      "step_id": "S05",
      "action": "filter",
      "evidence": [
        {
          "document": "DOC-001",
          "page": 6,
          "section": "实施例1",
          "quote": "过滤收集产物",
          "evidence_type": "explicit",
          "confidence": 0.92
        }
      ],
      "confidence": 0.85,
      "status": "warning",
      "missing_fields": [
        {
          "field_name": "filter_medium",
          "step_id": "S05",
          "risk_level": "low",
          "blocks_execution": false,
          "suggestion": "建议使用0.45μm PTFE滤膜",
          "suggestion_source": "literature_default",
          "requires_confirmation": false
        }
      ],
      "device_binding": {
        "device_id": "DEV-FUMEHOOD-01",
        "capability_check": "passed"
      }
    },
    {
      "step_id": "S06",
      "action": "dry",
      "temperature": { "value": 60, "unit": "celsius" },
      "duration": { "value": 12, "unit": "hour" },
      "evidence": [
        {
          "document": "DOC-001",
          "page": 6,
          "section": "实施例1",
          "quote": "真空干燥",
          "evidence_type": "inferred",
          "confidence": 0.65,
          "derivation": "文献仅写'真空干燥'，未给出温度与时间，按同类环氧树脂常规条件推断60℃/12h"
        }
      ],
      "confidence": 0.65,
      "status": "inferred",
      "missing_fields": [
        {
          "field_name": "temperature.value",
          "step_id": "S06",
          "risk_level": "medium",
          "blocks_execution": false,
          "suggestion": "60℃",
          "suggestion_source": "literature_default",
          "requires_confirmation": true
        },
        {
          "field_name": "duration.value",
          "step_id": "S06",
          "risk_level": "medium",
          "blocks_execution": false,
          "suggestion": "12h",
          "suggestion_source": "literature_default",
          "requires_confirmation": true
        }
      ],
      "device_binding": {
        "device_id": "DEV-VACUUMOVEN-01",
        "capability_check": "passed"
      }
    }
  ],
  "reagents": [
    {
      "name": "双酚A",
      "cas_number": "80-05-7",
      "role": "monomer",
      "total_amount": { "value": 22.8, "unit": "g" },
      "hazard_class": "Xi"
    },
    {
      "name": "环氧氯丙烷",
      "cas_number": "106-89-8",
      "role": "crosslinker",
      "total_amount": { "value": 18.5, "unit": "g" },
      "hazard_class": "T"
    },
    {
      "name": "丙酮",
      "cas_number": "67-64-1",
      "role": "solvent",
      "total_amount": { "value": 100, "unit": "mL" },
      "hazard_class": "F"
    },
    {
      "name": "氮气",
      "cas_number": "7727-37-9",
      "role": "additive",
      "hazard_class": "inert"
    }
  ],
  "equipment": [
    {
      "device_id": "DEV-BALANCE-01",
      "device_type": "balance",
      "device_name": "Mettler ME204",
      "config_path": "devices/balance_me204.yaml"
    },
    {
      "device_id": "DEV-REACTOR-01",
      "device_type": "reactor",
      "device_name": "250mL三口烧瓶反应器",
      "config_path": "devices/reactor_250ml.yaml"
    },
    {
      "device_id": "DEV-HOTPLATE-01",
      "device_type": "hotplate_stirrer",
      "device_name": "IKA RCT basic",
      "config_path": "devices/hotplate_ika_rct.yaml"
    },
    {
      "device_id": "DEV-VACUUMOVEN-01",
      "device_type": "vacuum_oven",
      "device_name": "Memmert VO200",
      "config_path": "devices/vacuum_oven_vo200.yaml"
    },
    {
      "device_id": "DEV-FUMEHOOD-01",
      "device_type": "fume_hood",
      "device_name": "实验室通风橱",
      "config_path": "devices/fume_hood_std.yaml"
    }
  ],
  "metadata": {
    "version": "1.0.0",
    "generated_at": "2026-08-06T10:00:00Z",
    "compiler_version": "matflow-compiler/0.3.0",
    "source_hash": "sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
    "operator": "auto",
    "lab_id": "LAB-MAT-001"
  },
  "safety_checks": [
    {
      "check_id": "SAFE-001",
      "check_type": "temperature_limit",
      "rule_id": "TEMP-001",
      "target_step": "S03",
      "status": "pass",
      "message": "步骤S03温度80℃在设备DEV-HOTPLATE-01范围(25-300℃)内",
      "details": {
        "actual_value": 80,
        "min_value": 25,
        "max_value": 300,
        "unit": "celsius",
        "device_id": "DEV-HOTPLATE-01"
      }
    },
    {
      "check_id": "SAFE-002",
      "check_type": "atmosphere_check",
      "rule_id": "ATM-001",
      "target_step": "S03",
      "status": "pass",
      "message": "步骤S03使用氮气气氛，符合水氧敏感反应要求"
    },
    {
      "check_id": "SAFE-003",
      "check_type": "inferred_parameter",
      "rule_id": "CONF-001",
      "target_step": "S06",
      "status": "warning",
      "message": "步骤S06含推断参数(temperature.value, duration.value)，需人工确认后方可执行"
    }
  ],
  "checkpoints": [
    {
      "checkpoint_id": "CP-01",
      "after_step": "S03",
      "stored_state": [
        { "name": "current_temperature", "type": "number", "unit": "celsius" },
        { "name": "step_progress", "type": "number" },
        { "name": "atmosphere_status", "type": "enum" }
      ],
      "recovery_policy": {
        "power_failure": "resume_from_checkpoint",
        "temperature_deviation": {
          "threshold": 5,
          "action": "hold"
        }
      }
    },
    {
      "checkpoint_id": "CP-02",
      "after_step": "S06",
      "stored_state": [
        { "name": "current_temperature", "type": "number", "unit": "celsius" },
        { "name": "step_progress", "type": "number" },
        { "name": "reagent_remaining", "type": "number", "unit": "g" }
      ],
      "recovery_policy": {
        "power_failure": "restart_step",
        "temperature_deviation": {
          "threshold": 3,
          "action": "alert"
        }
      }
    }
  ],
  "overall_confidence": 0.88,
  "overall_status": "warning"
}
```

---

## 设计原则总结

1. **证据可追溯**：每个参数值必须附带至少一条证据，指向源文档的具体页码与原文。
2. **绝不静默补全**：缺失的关键参数必须以 `MissingField` 记录暴露，不得用默认值填充后假装完整。
3. **推断需确认**：`inferred` 类型证据对应的步骤状态为 `inferred`，必须经人工确认后方可执行。
4. **安全优先**：安全检查在编译阶段完成，`blocked` 状态的步骤不得进入执行队列。
5. **可恢复**：关键步骤后设置检查点，定义明确的异常恢复策略。
