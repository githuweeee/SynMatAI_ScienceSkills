# 自由基聚合树脂配方合成——完整示例

> 本示例展示 matflow-compiler Skill 处理高分子材料合成协议的完整流程。
> 示例中故意设置了5个典型问题，以展示 Skill 的核心能力：绝不静默补全、证据绑定、三种信息区分、阻止执行状态。

---

## 目录

1. [输入文献描述](#1-输入文献描述)
2. [输入YAML配置](#2-输入yaml配置)
3. [预期输出 protocol.json](#3-预期输出-protocoljson)
4. [预期输出 SOP.md](#4-预期输出-sopmd)
5. [预期输出 missing_conditions.md](#5-预期输出-missing_conditionsmd)
6. [预期输出 safety_report.md](#6-预期输出-safety_reportmd)
7. [预期输出 recovery_plan.yaml](#7-预期输出-recovery_planyaml)
8. [问题分析与Skill行为说明](#8-问题分析与skill行为说明)

---

## 1. 输入文献描述

### 模拟论文实验部分文本

> "将苯乙烯单体(20 mL)和二乙烯苯交联剂(2 mL)混合于甲苯中。在氮气气氛下，加入引发剂，升温至80°C反应。反应结束后，产物用甲醇洗涤，真空干燥得到Sample A（以下简称P1，即optimized resin）。固含量通过称重法测定。"

### 文献信息

| 字段 | 值 |
|------|-----|
| 文档标题 | "High-Solid-Content Polystyrene Resin via Free Radical Polymerization" |
| 文档类型 | 期刊论文 |
| 对应章节 | Section 2.3 Experimental |
| 页码 | p.4567, 第2-3段 |

---

## 2. 输入YAML配置

```yaml
# matflow-compiler 输入配置
# 自由基聚合树脂合成协议编译

input:
  document:
    type: "text"
    title: "High-Solid-Content Polystyrene Resin via Free Radical Polymerization"
    section: "Section 2.3 Experimental"
    page: 4567
    content: >
      将苯乙烯单体(20 mL)和二乙烯苯交联剂(2 mL)混合于甲苯中。
      在氮气气氛下，加入引发剂，升温至80°C反应。
      反应结束后，产物用甲醇洗涤，真空干燥得到Sample A（以下简称P1，即optimized resin）。
      固含量通过称重法测定。

# 实验室设备配置
equipment:
  oil_bath:
    model: "DF-101S"
    max_temperature: 60          # 单位: °C —— 注意：最高仅60°C
    temperature_precision: 0.5
    unit: "°C"
  vacuum_oven:
    model: "DZF-6050"
    max_temperature: 250
    max_vacuum: -0.1            # 单位: MPa
    unit: "°C"
  analytical_balance:
    model: "ME204T"
    unit: "g"
    precision: 0.0001

# 材料数据库（提供物性参数用于单位转换）
material_database:
  styrene:
    formula: "C8H8"
    molar_mass: 104.15           # g/mol
    density: 0.906               # g/mL
    cas: "100-42-5"
    hazard: ["flammable", "irritant"]
    flash_point: 31              # °C
  divinylbenzene:
    formula: "C10H10"
    molar_mass: 130.19           # g/mol
    density: 0.914               # g/mL
    cas: "1321-74-0"
    hazard: ["flammable", "irritant"]
    flash_point: 76              # °C
  AIBN:
    formula: "C8H12N4"
    molar_mass: 164.21           # g/mol
    cas: "78-67-1"
    hazard: ["toxic", "explosive_decomposition"]
    decomposition_temp: 65       # °C
  toluene:
    formula: "C7H8"
    molar_mass: 92.14            # g/mol
    density: 0.867               # g/mL
    cas: "108-88-3"
    hazard: ["flammable", "toxic"]
    flash_point: 4               # °C
  methanol:
    formula: "CH3OH"
    molar_mass: 32.04            # g/mol
    density: 0.792               # g/mL
    cas: "67-56-1"
    hazard: ["flammable", "toxic"]
    flash_point: 12              # °C

# 安全规则
safety_rules:
  - id: "flammable_solvent_ventilation"
    description: "易燃溶剂操作必须在通风橱内进行"
  - id: "nitrogen_asphyxiation"
    description: "氮气保护操作需确保通风良好，防止窒息"
  - id: "AIBN_decomposition"
    description: "AIBN分解温度65°C，储存温度需低于30°C，避免高温"

# 输出配置
output:
  formats: ["protocol.json", "SOP.md", "missing_conditions.md", "safety_report.md", "recovery_plan.yaml"]
  language: "zh-CN"
  evidence_binding: true
  allow_silent_fill: false       # 核心配置：绝不静默补全
```

---

## 3. 预期输出 protocol.json

```json
{
  "metadata": {
    "title": "自由基聚合树脂合成协议",
    "source_document": {
      "title": "High-Solid-Content Polystyrene Resin via Free Radical Polymerization",
      "section": "Section 2.3 Experimental",
      "page": 4567
    },
    "generated_by": "matflow-compiler",
    "generated_at": "2026-08-06T10:00:00Z",
    "language": "zh-CN"
  },

  "status": "blocked_missing_parameter",

  "overall_status_detail": {
    "primary_blocker": "blocked_missing_parameter",
    "secondary_issues": [
      "require_confirmation: nitrogen_purge_duration",
      "safety_warning: equipment_overlimit_oil_bath"
    ],
    "executable": false,
    "reason": "引发剂(AIBN)用量/比例未在源文档中指定，且存在设备超限安全警告和需确认项"
  },

  "sample_registry": {
    "samples": [
      {
        "primary_name": "Sample A",
        "aliases": ["P1", "optimized resin"],
        "description": "自由基聚合所得聚苯乙烯树脂",
        "evidence": {
          "document": "source_paper",
          "page": 4567,
          "section": "Section 2.3 Experimental",
          "evidence_type": "extracted",
          "confidence": 1.0,
          "raw_text": "得到Sample A（以下简称P1，即optimized resin）"
        },
        "alias_evidence": [
          {
            "alias": "P1",
            "evidence_type": "extracted",
            "confidence": 1.0,
            "raw_text": "以下简称P1",
            "reasoning": "原文明确声明'以下简称P1'，别名关系直接提取"
          },
          {
            "alias": "optimized resin",
            "evidence_type": "extracted",
            "confidence": 1.0,
            "raw_text": "即optimized resin",
            "reasoning": "原文明确声明'即optimized resin'，别名关系直接提取"
          }
        ]
      }
    ],
    "ambiguous_mappings": []
  },

  "protocol": {
    "reaction_type": "free_radical_polymerization",
    "steps": [
      {
        "step": 1,
        "name": "monomer_mixing",
        "description": "单体与交联剂混合",
        "parameters": {
          "styrene": {
            "value": 0.18120,
            "unit": "mol",
            "evidence": {
              "document": "source_paper",
              "page": 4567,
              "section": "Section 2.3 Experimental",
              "evidence_type": "derived",
              "confidence": 1.0,
              "raw_text": "苯乙烯单体(20 mL)",
              "derivation": {
                "original_value": 20,
                "original_unit": "mL",
                "intermediate_steps": [
                  {
                    "description": "体积转质量",
                    "formula": "mass = volume × density",
                    "values": "20 mL × 0.906 g/mL = 18.12 g"
                  },
                  {
                    "description": "质量转摩尔",
                    "formula": "moles = mass / molar_mass",
                    "values": "18.12 g / 104.15 g/mol = 0.17396 mol"
                  }
                ],
                "converted_value": 0.17396,
                "target_unit": "mol",
                "reason": "统一归一化为摩尔单位，便于计算单体配比"
              }
            }
          },
          "divinylbenzene": {
            "value": 0.01405,
            "unit": "mol",
            "evidence": {
              "document": "source_paper",
              "page": 4567,
              "section": "Section 2.3 Experimental",
              "evidence_type": "derived",
              "confidence": 1.0,
              "raw_text": "二乙烯苯交联剂(2 mL)",
              "derivation": {
                "original_value": 2,
                "original_unit": "mL",
                "intermediate_steps": [
                  {
                    "description": "体积转质量",
                    "formula": "mass = volume × density",
                    "values": "2 mL × 0.914 g/mL = 1.828 g"
                  },
                  {
                    "description": "质量转摩尔",
                    "formula": "moles = mass / molar_mass",
                    "values": "1.828 g / 130.19 g/mol = 0.01405 mol"
                  }
                ],
                "converted_value": 0.01405,
                "target_unit": "mol",
                "reason": "统一归一化为摩尔单位，便于计算交联剂配比"
              }
            }
          },
          "solvent": {
            "name": "toluene",
            "amount": null,
            "unit": "mL",
            "evidence": {
              "document": "source_paper",
              "page": 4567,
              "section": "Section 2.3 Experimental",
              "evidence_type": "extracted",
              "confidence": 1.0,
              "raw_text": "混合于甲苯中"
            },
            "note": "甲苯作为溶剂被提及，但具体用量未给出"
          },
          "crosslinker_ratio": {
            "value": 7.47,
            "unit": "mol%",
            "evidence": {
              "document": "source_paper",
              "page": 4567,
              "section": "Section 2.3 Experimental",
              "evidence_type": "derived",
              "confidence": 1.0,
              "raw_text": "苯乙烯单体(20 mL)和二乙烯苯交联剂(2 mL)",
              "derivation": {
                "formula": "crosslinker_ratio = n_DVB / (n_St + n_DVB) × 100%",
                "values": "0.01405 / (0.17396 + 0.01405) × 100% = 7.47%",
                "reason": "交联剂摩尔占比由单体和交联剂摩尔量计算得出"
              }
            }
          }
        }
      },
      {
        "step": 2,
        "name": "initiator_addition",
        "description": "氮气保护下加入引发剂",
        "parameters": {
          "initiator": {
            "name": "AIBN",
            "amount": null,
            "unit": "mol",
            "evidence": {
              "document": "source_paper",
              "page": 4567,
              "section": "Section 2.3 Experimental",
              "evidence_type": "extracted",
              "confidence": 0.50,
              "raw_text": "加入引发剂",
              "note": "原文仅提及'引发剂'，未指明具体种类。根据自由基聚合常识推断为AIBN，但置信度较低，需确认"
            },
            "inferred_name": "AIBN",
            "inference_reasoning": "自由基聚合常用引发剂为AIBN或BPO。80°C反应温度更接近AIBN的分解温度（65°C），推断为AIBN。但原文未明确，需用户确认。"
          },
          "initiator_ratio": null,
          "atmosphere": {
            "type": "nitrogen",
            "purge_duration": null,
            "evidence": {
              "document": "source_paper",
              "page": 4567,
              "section": "Section 2.3 Experimental",
              "evidence_type": "extracted",
              "confidence": 1.0,
              "raw_text": "在氮气气氛下"
            },
            "note": "氮气保护被提及，但吹扫持续时间未给出"
          }
        },
        "missing_fields": [
          {
            "field": "initiator.amount",
            "description": "引发剂(AIBN)的用量或相对比例未在源文档中指定",
            "evidence": null,
            "suggestion": "请补充引发剂用量，例如：'加入0.1 g AIBN（单体质量的0.5 wt%）'"
          },
          {
            "field": "initiator.ratio",
            "description": "引发剂与单体的摩尔比/质量比未给出",
            "evidence": null,
            "suggestion": "请补充引发剂比例，例如：'AIBN/单体 = 1 mol%'"
          },
          {
            "field": "atmosphere.purge_duration",
            "description": "氮气吹扫持续时间未在源文档中指定",
            "evidence": null,
            "status": "require_confirmation",
            "suggestion": "请确认氮气吹扫时间，通常为15-30分钟"
          }
        ]
      },
      {
        "step": 3,
        "name": "polymerization_reaction",
        "description": "升温聚合反应",
        "parameters": {
          "temperature": {
            "value": 80,
            "unit": "°C",
            "evidence": {
              "document": "source_paper",
              "page": 4567,
              "section": "Section 2.3 Experimental",
              "evidence_type": "extracted",
              "confidence": 1.0,
              "raw_text": "升温至80°C反应"
            }
          },
          "duration": null,
          "evidence_duration": {
            "document": "source_paper",
            "page": 4567,
            "section": "Section 2.3 Experimental",
            "evidence_type": "extracted",
            "confidence": 1.0,
            "raw_text": "升温至80°C反应",
            "note": "原文仅提及'反应'，未给出反应持续时间"
          }
        },
        "missing_fields": [
          {
            "field": "duration",
            "description": "聚合反应的持续时间未在源文档中指定",
            "evidence": null,
            "suggestion": "请补充反应时间，例如：'80°C反应6小时'"
          }
        ],
        "equipment_check": {
          "equipment": "oil_bath",
          "model": "DF-101S",
          "required_temperature": {
            "value": 80,
            "unit": "°C"
          },
          "max_temperature": {
            "value": 60,
            "unit": "°C"
          },
          "status": "overlimit",
          "severity": "critical",
          "message": "反应温度80°C超过油浴锅最高温度60°C",
          "suggestion": "请更换加热设备（如高温油浴锅≥100°C或加热套），或降低反应温度至60°C以下"
        }
      },
      {
        "step": 4,
        "name": "product_washing",
        "description": "产物洗涤",
        "parameters": {
          "solvent": {
            "name": "methanol",
            "amount": null,
            "unit": "mL",
            "evidence": {
              "document": "source_paper",
              "page": 4567,
              "section": "Section 2.3 Experimental",
              "evidence_type": "extracted",
              "confidence": 1.0,
              "raw_text": "产物用甲醇洗涤"
            }
          },
          "method": "washing",
          "cycles": null,
          "evidence": {
            "document": "source_paper",
            "page": 4567,
            "section": "Section 2.3 Experimental",
            "evidence_type": "extracted",
            "confidence": 1.0,
            "raw_text": "产物用甲醇洗涤",
            "note": "洗涤次数未给出"
          }
        },
        "missing_fields": [
          {
            "field": "cycles",
            "description": "洗涤次数未在源文档中指定",
            "evidence": null,
            "suggestion": "请补充洗涤次数，例如：'用甲醇洗涤3次，每次50 mL'"
          }
        ]
      },
      {
        "step": 5,
        "name": "vacuum_drying",
        "description": "真空干燥",
        "parameters": {
          "method": "vacuum_drying",
          "temperature": null,
          "duration": null,
          "evidence": {
            "document": "source_paper",
            "page": 4567,
            "section": "Section 2.3 Experimental",
            "evidence_type": "extracted",
            "confidence": 1.0,
            "raw_text": "真空干燥",
            "note": "仅提及'真空干燥'，未给出温度和持续时间"
          }
        },
        "missing_fields": [
          {
            "field": "temperature",
            "description": "真空干燥温度未在源文档中指定",
            "evidence": null,
            "suggestion": "请补充干燥温度，例如：'60°C真空干燥24小时'"
          },
          {
            "field": "duration",
            "description": "真空干燥时间未在源文档中指定",
            "evidence": null,
            "suggestion": "请补充干燥时间，例如：'60°C真空干燥24小时'"
          }
        ]
      },
      {
        "step": 6,
        "name": "solid_content_measurement",
        "description": "固含量测定",
        "parameters": {
          "method": "gravimetric",
          "evidence": {
            "document": "source_paper",
            "page": 4567,
            "section": "Section 2.3 Experimental",
            "evidence_type": "extracted",
            "confidence": 1.0,
            "raw_text": "固含量通过称重法测定"
          }
        },
        "derived_calculations": {
          "type": "solid_content",
          "formula": "solid_content = (mass_dry / mass_wet) × 100%",
          "inputs": ["mass_wet", "mass_dry"],
          "evidence": {
            "document": "source_paper",
            "page": 4567,
            "section": "Section 2.3 Experimental",
            "evidence_type": "derived",
            "confidence": 1.0,
            "raw_text": "固含量通过称重法测定",
            "derivation": {
              "reason": "称重法固含量计算公式由方法名称推导得出，非原文直接给出",
              "derivation_type": "derived"
            }
          }
        }
      }
    ]
  },

  "missing_fields": [
    {
      "step": 2,
      "field": "initiator.amount",
      "description": "引发剂(AIBN)的用量未在源文档中指定",
      "evidence": null,
      "severity": "critical",
      "suggestion": "请补充引发剂用量，例如：'加入0.1 g AIBN'"
    },
    {
      "step": 2,
      "field": "initiator.ratio",
      "description": "引发剂与单体的比例未给出",
      "evidence": null,
      "severity": "critical",
      "suggestion": "请补充引发剂比例，例如：'AIBN/单体 = 1 mol%'"
    },
    {
      "step": 2,
      "field": "atmosphere.purge_duration",
      "description": "氮气吹扫持续时间未指定",
      "evidence": null,
      "severity": "medium",
      "status": "require_confirmation",
      "suggestion": "请确认氮气吹扫时间，通常为15-30分钟"
    },
    {
      "step": 3,
      "field": "duration",
      "description": "聚合反应持续时间未指定",
      "evidence": null,
      "severity": "critical",
      "suggestion": "请补充反应时间，例如：'80°C反应6小时'"
    },
    {
      "step": 4,
      "field": "cycles",
      "description": "洗涤次数未指定",
      "evidence": null,
      "severity": "medium",
      "suggestion": "请补充洗涤次数"
    },
    {
      "step": 5,
      "field": "temperature",
      "description": "真空干燥温度未指定",
      "evidence": null,
      "severity": "medium",
      "suggestion": "请补充干燥温度"
    },
    {
      "step": 5,
      "field": "duration",
      "description": "真空干燥时间未指定",
      "evidence": null,
      "severity": "medium",
      "suggestion": "请补充干燥时间"
    }
  ],

  "safety_warnings": [
    {
      "type": "equipment_overlimit",
      "severity": "critical",
      "step": 3,
      "message": "反应温度80°C超过油浴锅(DF-101S)最高温度60°C，超出20°C",
      "required_temperature": {
        "value": 80,
        "unit": "°C"
      },
      "equipment_limit": {
        "value": 60,
        "unit": "°C",
        "model": "DF-101S"
      },
      "evidence": {
        "document": "source_paper",
        "page": 4567,
        "section": "Section 2.3 Experimental",
        "evidence_type": "extracted",
        "confidence": 1.0,
        "raw_text": "升温至80°C反应"
      },
      "action": "blocked",
      "suggestion": "请更换加热设备（如高温油浴锅≥100°C或加热套），或降低反应温度至60°C以下"
    },
    {
      "type": "flammable_solvent",
      "severity": "warning",
      "step": 1,
      "message": "使用甲苯（闪点4°C）和苯乙烯（闪点31°C）等易燃溶剂，需在通风橱内操作",
      "solvents": [
        {
          "name": "toluene",
          "flash_point": 4,
          "unit": "°C"
        },
        {
          "name": "styrene",
          "flash_point": 31,
          "unit": "°C"
        }
      ],
      "evidence": {
        "document": "source_paper",
        "page": 4567,
        "section": "Section 2.3 Experimental",
        "evidence_type": "inferred",
        "confidence": 0.95,
        "raw_text": "将苯乙烯单体(20 mL)和二乙烯苯交联剂(2 mL)混合于甲苯中",
        "reasoning": "文本提及苯乙烯和甲苯，材料数据库显示两者均为易燃溶剂"
      },
      "action": "require_confirmation",
      "required_confirmations": [
        {
          "field": "fume_hood",
          "question": "混合操作是否在通风橱内进行？",
          "options": ["是", "否"]
        }
      ]
    },
    {
      "type": "nitrogen_asphyxiation_risk",
      "severity": "warning",
      "step": 2,
      "message": "氮气保护操作可能导致局部氧气浓度降低，需确保通风良好",
      "evidence": {
        "document": "source_paper",
        "page": 4567,
        "section": "Section 2.3 Experimental",
        "evidence_type": "extracted",
        "confidence": 1.0,
        "raw_text": "在氮气气氛下"
      },
      "action": "require_confirmation",
      "required_confirmations": [
        {
          "field": "ventilation",
          "question": "反应区域通风是否良好？是否有氧气浓度监测？",
          "options": ["是，通风良好", "否，需改善通风"]
        }
      ]
    },
    {
      "type": "AIBN_safety",
      "severity": "warning",
      "step": 2,
      "message": "AIBN分解温度65°C，80°C反应条件下将快速分解，需控制加入速度避免暴聚",
      "evidence": {
        "document": "source_paper",
        "page": 4567,
        "section": "Section 2.3 Experimental",
        "evidence_type": "inferred",
        "confidence": 0.85,
        "raw_text": "加入引发剂，升温至80°C反应",
        "reasoning": "推断引发剂为AIBN（分解温度65°C），反应温度80°C高于分解温度，存在快速分解风险"
      },
      "action": "require_confirmation",
      "required_confirmations": [
        {
          "field": "addition_method",
          "question": "AIBN加入方式：一次性加入还是分批加入？是否需要控制升温速率？",
          "options": ["一次性加入", "分批加入", "需控制升温速率"]
        }
      ]
    }
  ],

  "require_confirmations": [
    {
      "id": "confirm_nitrogen_purge_duration",
      "step": 2,
      "field": "atmosphere.purge_duration",
      "question": "氮气保护时间未在文献中明确给出。请确认氮气吹扫持续时间（通常15-30分钟）：",
      "options": ["15分钟", "20分钟", "30分钟", "其他（请说明）"],
      "evidence": {
        "document": "source_paper",
        "page": 4567,
        "section": "Section 2.3 Experimental",
        "evidence_type": "extracted",
        "confidence": 1.0,
        "raw_text": "在氮气气氛下",
        "note": "原文仅提及氮气气氛，未给出吹扫时间"
      },
      "inferred_value": {
        "value": 20,
        "unit": "min",
        "evidence_type": "inferred",
        "confidence": 0.60,
        "reasoning": "自由基聚合常用氮气吹扫时间为15-30分钟，取中间值20分钟作为参考。此为推断值，必须经用户确认后方可使用。"
      }
    },
    {
      "id": "confirm_initiator_identity",
      "step": 2,
      "field": "initiator.name",
      "question": "原文仅提及'引发剂'，未指明具体种类。推断为AIBN，请确认：",
      "options": ["是，AIBN", "否，为BPO（过氧化苯甲酰）", "否，为其他（请说明）"],
      "evidence": {
        "document": "source_paper",
        "page": 4567,
        "section": "Section 2.3 Experimental",
        "evidence_type": "extracted",
        "confidence": 0.50,
        "raw_text": "加入引发剂"
      },
      "inferred_value": {
        "value": "AIBN",
        "evidence_type": "inferred",
        "confidence": 0.50,
        "reasoning": "80°C反应温度接近AIBN分解温度（65°C），且AIBN是自由基聚合最常用引发剂。但BPO分解温度为70-80°C也匹配，置信度不高。"
      }
    }
  ],

  "evidence_summary": {
    "total_parameters": 15,
    "extracted": 6,
    "derived": 3,
    "inferred": 2,
    "missing": 7,
    "null_fields": 7,
    "evidence_types": {
      "extracted": "直接从源文档文本中提取的参数值",
      "derived": "通过计算推导得出的参数值（如单位转换、配比计算）",
      "inferred": "基于领域知识推断的参数值，必须经用户确认"
    }
  }
}
```

---

## 4. 预期输出 SOP.md

```markdown
# 标准操作程序 (SOP)
## 自由基聚合树脂合成协议

> **状态: 阻止执行 (blocked_missing_parameter)**
> 本协议包含未解决的关键缺失参数和安全警告，不可直接执行。
> 请先补充缺失参数并确认安全事项后再执行。

---

### 协议信息

| 字段 | 值 |
|------|-----|
| 来源文献 | High-Solid-Content Polystyrene Resin via Free Radical Polymerization |
| 章节 | Section 2.3 Experimental |
| 页码 | p.4567 |
| 反应类型 | 自由基聚合 |
| 样品名称 | Sample A (别名: P1, optimized resin) |

---

### 步骤 1: 单体与交联剂混合

**操作**: 将苯乙烯单体和二乙烯苯交联剂混合于甲苯中。

| 参数 | 值 | 单位 | 证据类型 | 来源 |
|------|-----|------|---------|------|
| 苯乙烯 | 0.17396 | mol | derived | "苯乙烯单体(20 mL)" → 20 mL × 0.906 g/mL ÷ 104.15 g/mol |
| 二乙烯苯 | 0.01405 | mol | derived | "二乙烯苯交联剂(2 mL)" → 2 mL × 0.914 g/mL ÷ 130.19 g/mol |
| 交联剂比例 | 7.47 | mol% | derived | n_DVB / (n_St + n_DVB) × 100% |
| 溶剂 | 甲苯 | — | extracted | "混合于甲苯中" |
| 溶剂用量 | **[缺失]** | mL | — | 原文未给出甲苯用量 |

> **安全提示**: 苯乙烯（闪点31°C）和甲苯（闪点4°C）均为易燃溶剂，混合操作必须在通风橱内进行。

---

### 步骤 2: 氮气保护下加入引发剂

**操作**: 在氮气气氛下，加入引发剂。

| 参数 | 值 | 单位 | 证据类型 | 来源 |
|------|-----|------|---------|------|
| 气氛类型 | 氮气 | — | extracted | "在氮气气氛下" |
| 引发剂种类 | AIBN (推断) | — | inferred (置信度0.50) | "加入引发剂" — 原文未指明，根据反应温度推断 |
| 引发剂用量 | **[缺失]** | mol | — | 原文未给出引发剂用量 |
| 引发剂比例 | **[缺失]** | — | — | 原文未给出引发剂与单体比例 |
| 氮气吹扫时间 | **[需确认]** | min | — | 原文未给出吹扫时间，推断值20 min（置信度0.60） |

> **阻止执行**: 引发剂用量和比例是关键参数，缺失将导致无法确定聚合速率和产物分子量。
>
> **需确认**: 氮气吹扫时间未在文献中明确给出，请确认（通常15-30分钟）。
>
> **安全提示**: AIBN分解温度为65°C，80°C反应条件下将快速分解，需控制加入速度避免暴聚。氮气保护操作需确保通风良好，防止窒息。

---

### 步骤 3: 聚合反应

**操作**: 升温至80°C进行聚合反应。

| 参数 | 值 | 单位 | 证据类型 | 来源 |
|------|-----|------|---------|------|
| 反应温度 | 80 | °C | extracted | "升温至80°C反应" |
| 反应时间 | **[缺失]** | h | — | 原文未给出反应持续时间 |

> **阻止执行 - 设备超限**: 反应温度80°C超过油浴锅(DF-101S)最高温度60°C，超出20°C。
> 请更换加热设备（如高温油浴锅≥100°C或加热套），或降低反应温度至60°C以下。
>
> **阻止执行**: 反应时间是关键参数，缺失将导致无法控制聚合程度。

---

### 步骤 4: 产物洗涤

**操作**: 产物用甲醇洗涤。

| 参数 | 值 | 单位 | 证据类型 | 来源 |
|------|-----|------|---------|------|
| 洗涤溶剂 | 甲醇 | — | extracted | "产物用甲醇洗涤" |
| 洗涤次数 | **[缺失]** | 次 | — | 原文未给出洗涤次数 |
| 溶剂用量 | **[缺失]** | mL | — | 原文未给出每次洗涤溶剂用量 |

---

### 步骤 5: 真空干燥

**操作**: 真空干燥得到产物。

| 参数 | 值 | 单位 | 证据类型 | 来源 |
|------|-----|------|---------|------|
| 干燥方式 | 真空干燥 | — | extracted | "真空干燥" |
| 干燥温度 | **[缺失]** | °C | — | 原文未给出干燥温度 |
| 干燥时间 | **[缺失]** | h | — | 原文未给出干燥时间 |

---

### 步骤 6: 固含量测定

**操作**: 通过称重法测定固含量。

| 参数 | 值 | 单位 | 证据类型 | 来源 |
|------|-----|------|---------|------|
| 测定方法 | 称重法 | — | extracted | "固含量通过称重法测定" |
| 计算公式 | solid_content = (mass_dry / mass_wet) × 100% | — | derived | 由"称重法"方法名称推导 |

---

### 缺失参数汇总

| 步骤 | 缺失字段 | 严重程度 | 状态 |
|------|---------|---------|------|
| 2 | 引发剂用量 | critical | blocked |
| 2 | 引发剂比例 | critical | blocked |
| 2 | 氮气吹扫时间 | medium | require_confirmation |
| 3 | 反应时间 | critical | blocked |
| 4 | 洗涤次数 | medium | — |
| 5 | 干燥温度 | medium | — |
| 5 | 干燥时间 | medium | — |

> **结论**: 本协议因缺失引发剂用量、反应时间等关键参数，且存在设备超限安全警告，当前状态为 **阻止执行**。请补充上述缺失参数并解决安全问题后重新编译。
```

---

## 5. 预期输出 missing_conditions.md

```markdown
# 缺失条件报告
## 自由基聚合树脂合成协议

> 本报告列出协议中所有未从源文档提取到的条件参数。
> 每个缺失项均标注了严重程度和建议补充方式。
> **matflow-compiler 绝不静默补全任何以下缺失项。**

---

## 关键缺失项 (Critical)

### 1. 引发剂用量 (initiator.amount)

| 字段 | 内容 |
|------|------|
| 步骤 | 步骤 2: 氮气保护下加入引发剂 |
| 字段名 | initiator.amount |
| 描述 | 引发剂(AIBN)的用量未在源文档中指定 |
| 严重程度 | **Critical** |
| 证据 | null（源文档中无对应文本） |
| 源文本 | "加入引发剂"（仅提及加入引发剂，未给出用量） |
| 影响 | 无法确定聚合速率、产物分子量和转化率 |
| 建议补充 | "加入0.1 g AIBN（单体质量的0.5 wt%）" |
| 状态 | **blocked_missing_parameter** |

### 2. 引发剂比例 (initiator.ratio)

| 字段 | 内容 |
|------|------|
| 步骤 | 步骤 2: 氮气保护下加入引发剂 |
| 字段名 | initiator.ratio |
| 描述 | 引发剂与单体的摩尔比/质量比未给出 |
| 严重程度 | **Critical** |
| 证据 | null |
| 源文本 | "加入引发剂" |
| 影响 | 无法计算理论分子量和聚合度 |
| 建议补充 | "AIBN/单体 = 1 mol%" |
| 状态 | **blocked_missing_parameter** |

### 3. 聚合反应时间 (duration)

| 字段 | 内容 |
|------|------|
| 步骤 | 步骤 3: 聚合反应 |
| 字段名 | duration |
| 描述 | 聚合反应的持续时间未在源文档中指定 |
| 严重程度 | **Critical** |
| 证据 | null |
| 源文本 | "升温至80°C反应"（仅提及反应，未给出时间） |
| 影响 | 无法控制聚合程度和转化率 |
| 建议补充 | "80°C反应6小时" |
| 状态 | **blocked_missing_parameter** |

---

## 需确认项 (Require Confirmation)

### 4. 氮气吹扫时间 (atmosphere.purge_duration)

| 字段 | 内容 |
|------|------|
| 步骤 | 步骤 2: 氮气保护下加入引发剂 |
| 字段名 | atmosphere.purge_duration |
| 描述 | 氮气吹扫持续时间未在源文档中指定 |
| 严重程度 | Medium |
| 证据 | null |
| 源文本 | "在氮气气氛下"（未给出吹扫时间） |
| 推断值 | 20 min（置信度 0.60） |
| 推断依据 | 自由基聚合常用氮气吹扫时间为15-30分钟，取中间值 |
| 影响 | 吹扫不足可能导致氧阻聚，影响聚合效率 |
| 建议确认 | 请确认氮气吹扫时间（通常15-30分钟） |
| 状态 | **require_confirmation** |

### 5. 引发剂种类 (initiator.name)

| 字段 | 内容 |
|------|------|
| 步骤 | 步骤 2: 氮气保护下加入引发剂 |
| 字段名 | initiator.name |
| 描述 | 原文仅提及"引发剂"，未指明具体种类 |
| 严重程度 | Medium |
| 证据 | "加入引发剂"（extracted, 置信度 0.50） |
| 推断值 | AIBN（置信度 0.50） |
| 推断依据 | 80°C反应温度接近AIBN分解温度（65°C），且AIBN为自由基聚合常用引发剂 |
| 备选推断 | BPO（过氧化苯甲酰，分解温度70-80°C）也匹配 |
| 建议确认 | 请确认引发剂种类：AIBN / BPO / 其他 |
| 状态 | **require_confirmation** |

---

## 一般缺失项 (Medium)

### 6. 甲苯用量 (solvent.amount)

| 字段 | 内容 |
|------|------|
| 步骤 | 步骤 1: 单体与交联剂混合 |
| 字段名 | solvent.amount |
| 描述 | 甲苯作为溶剂被提及，但具体用量未给出 |
| 严重程度 | Medium |
| 证据 | "混合于甲苯中"（extracted, 置信度 1.0） |
| 建议补充 | "混合于50 mL甲苯中" |

### 7. 洗涤次数 (cycles)

| 字段 | 内容 |
|------|------|
| 步骤 | 步骤 4: 产物洗涤 |
| 字段名 | cycles |
| 描述 | 甲醇洗涤次数未给出 |
| 严重程度 | Medium |
| 证据 | "产物用甲醇洗涤"（extracted, 置信度 1.0） |
| 建议补充 | "用甲醇洗涤3次，每次50 mL" |

### 8. 真空干燥温度 (temperature)

| 字段 | 内容 |
|------|------|
| 步骤 | 步骤 5: 真空干燥 |
| 字段名 | temperature |
| 描述 | 真空干燥温度未给出 |
| 严重程度 | Medium |
| 证据 | "真空干燥"（extracted, 置信度 1.0） |
| 建议补充 | "60°C真空干燥" |

### 9. 真空干燥时间 (duration)

| 字段 | 内容 |
|------|------|
| 步骤 | 步骤 5: 真空干燥 |
| 字段名 | duration |
| 描述 | 真空干燥时间未给出 |
| 严重程度 | Medium |
| 证据 | "真空干燥"（extracted, 置信度 1.0） |
| 建议补充 | "60°C真空干燥24小时" |

---

## 统计

| 类别 | 数量 |
|------|------|
| Critical (阻止执行) | 3 |
| Require Confirmation (需确认) | 2 |
| Medium (一般缺失) | 4 |
| **总计** | **9** |

> **注意**: 以上缺失项均未被 matflow-compiler 静默补全。所有缺失字段在 protocol.json 中标记为 `null`，并在 `missing_fields` 数组中显式列出。
```

---

## 6. 预期输出 safety_report.md

```markdown
# 安全报告
## 自由基聚合树脂合成协议

> 本报告列出协议执行过程中可能涉及的安全风险。
> 每个风险项均标注了严重程度、风险因素和建议措施。

---

## 风险等级: 高 (HIGH)

### 风险 1: 设备超限——油浴锅温度不足

| 字段 | 内容 |
|------|------|
| 风险类型 | 设备超限 (equipment_overlimit) |
| 严重程度 | **Critical** |
| 步骤 | 步骤 3: 聚合反应 |
| 描述 | 反应温度80°C超过油浴锅(DF-101S)最高温度60°C，超出20°C |
| 所需温度 | 80°C |
| 设备限制 | 60°C (DF-101S) |
| 证据 | "升温至80°C反应" (extracted, 置信度 1.0) |
| 执行动作 | **blocked** |
| 建议措施 | 更换加热设备（如高温油浴锅≥100°C或加热套），或降低反应温度至60°C以下 |

**风险分析**:
- 油浴锅超温使用可能导致硅油分解、冒烟甚至起火
- 温度控制失灵可能导致反应温度失控，引发暴聚
- 设备损坏风险

---

### 风险 2: 易燃溶剂操作

| 字段 | 内容 |
|------|------|
| 风险类型 | 易燃溶剂 (flammable_solvent) |
| 严重程度 | **Warning** |
| 步骤 | 步骤 1: 单体与交联剂混合 |
| 描述 | 使用甲苯（闪点4°C）、苯乙烯（闪点31°C）和甲醇（闪点12°C）等易燃溶剂 |
| 涉及溶剂 | 甲苯 (闪点4°C), 苯乙烯 (闪点31°C), 甲醇 (闪点12°C) |
| 证据 | "将苯乙烯单体(20 mL)和二乙烯苯交联剂(2 mL)混合于甲苯中" (inferred, 置信度 0.95) |
| 执行动作 | **require_confirmation** |
| 需确认 | 混合操作是否在通风橱内进行？ |
| 建议措施 | 所有易燃溶剂操作必须在通风橱内进行，远离明火和热源 |

**风险分析**:
- 甲苯闪点仅4°C，室温下即可形成可燃蒸气
- 苯乙烯在加热条件下可能发生自聚合
- 甲醇洗涤步骤涉及大量易燃溶剂转移

---

### 风险 3: AIBN热分解风险

| 字段 | 内容 |
|------|------|
| 风险类型 | 化学品热分解 (AIBN_safety) |
| 严重程度 | **Warning** |
| 步骤 | 步骤 2-3: 引发剂加入与聚合反应 |
| 描述 | AIBN分解温度65°C，80°C反应条件下将快速分解 |
| 证据 | "加入引发剂，升温至80°C反应" (inferred, 置信度 0.85) |
| 执行动作 | **require_confirmation** |
| 需确认 | AIBN加入方式：一次性加入还是分批加入？是否需要控制升温速率？ |
| 建议措施 | 分批缓慢加入AIBN，控制升温速率≤2°C/min，准备冷却浴以防暴聚 |

**风险分析**:
- AIBN在65°C以上快速分解，产生氮气和自由基
- 80°C下分解速率较快，可能导致反应体系温度骤升
- 大量AIBN一次性加入可能引发暴聚（runaway polymerization）
- AIBN储存需低于30°C，避免受热和摩擦

---

### 风险 4: 氮气窒息风险

| 字段 | 内容 |
|------|------|
| 风险类型 | 窒息风险 (nitrogen_asphyxiation_risk) |
| 严重程度 | **Warning** |
| 步骤 | 步骤 2: 氮气保护 |
| 描述 | 氮气保护操作可能导致局部氧气浓度降低 |
| 证据 | "在氮气气氛下" (extracted, 置信度 1.0) |
| 执行动作 | **require_confirmation** |
| 需确认 | 反应区域通风是否良好？是否有氧气浓度监测？ |
| 建议措施 | 确保反应区域通风良好，安装氧气浓度报警器（阈值≥19.5%） |

---

## 安全措施清单

| 编号 | 措施 | 对应风险 | 必需/推荐 |
|------|------|---------|----------|
| 1 | 更换高温加热设备 | 风险1 | 必需 |
| 2 | 在通风橱内进行溶剂操作 | 风险2 | 必需 |
| 3 | 准备灭火器（干粉/CO2） | 风险2 | 必需 |
| 4 | 分批加入AIBN，控制升温速率 | 风险3 | 必需 |
| 5 | 准备冷却浴（冰水）以防暴聚 | 风险3 | 推荐 |
| 6 | 确保反应区域通风良好 | 风险4 | 必需 |
| 7 | 佩戴防护眼镜和手套 | 全部 | 必需 |

---

## 个人防护装备 (PPE) 要求

| 装备 | 要求 |
|------|------|
| 护目镜 | 必需（防化学飞溅） |
| 实验服 | 必需（阻燃材质） |
| 手套 | 必需（丁腈手套，防甲苯渗透） |
| 口罩 | 推荐（防有机蒸气） |
| 防静电鞋 | 推荐（易燃溶剂操作） |

---

> **结论**: 本协议存在1个Critical级安全风险（设备超限）和3个Warning级安全风险。设备超限问题必须解决后方可执行，其余风险需用户确认安全措施后执行。
```

---

## 7. 预期输出 recovery_plan.yaml

```yaml
# 恢复计划 - 自由基聚合树脂合成协议
# 本文件提供解决协议阻塞和缺失参数的恢复路径

recovery_plan:
  protocol_id: "free_radical_polymerization_001"
  current_status: "blocked_missing_parameter"
  target_status: "executable"

  # 阻塞项解决步骤（按优先级排序）
  resolution_steps:

    # === Critical 阻塞项 ===
    - step: 1
      priority: critical
      type: missing_parameter
      field: "initiator.amount"
      description: "补充引发剂(AIBN)用量"
      action: "user_input"
      prompt: "请输入引发剂AIBN的用量（单位g或mol）："
      expected_format: "数值 + 单位"
      example: "0.1 g 或 0.00061 mol"
      resolves_block: true
      auto_recompile: true

    - step: 2
      priority: critical
      type: missing_parameter
      field: "initiator.ratio"
      description: "确认引发剂比例"
      action: "auto_calculate_or_user_input"
      auto_calculate:
        formula: "ratio = n_initiator / n_monomer"
        inputs: ["initiator.amount", "styrene.amount"]
        condition: "若用户提供了引发剂用量，则自动计算比例"
      fallback: "请输入引发剂与单体的摩尔比（如0.01表示1 mol%）："
      resolves_block: true
      auto_recompile: true

    - step: 3
      priority: critical
      type: missing_parameter
      field: "duration"
      description: "补充聚合反应时间"
      action: "user_input"
      prompt: "请输入聚合反应持续时间（单位h或min）："
      expected_format: "数值 + 单位"
      example: "6 h 或 360 min"
      resolves_block: true
      auto_recompile: true

    # === 设备超限解决 ===
    - step: 4
      priority: critical
      type: equipment_overlimit
      field: "oil_bath.temperature"
      description: "解决油浴锅温度不足问题"
      action: "user_choice"
      options:
        - id: "replace_equipment"
          label: "更换高温油浴锅（≥100°C）"
          updates:
            equipment.oil_bath.model: "用户指定"
            equipment.oil_bath.max_temperature: "用户指定"
          resolves_block: true
        - id: "use_heating_mantle"
          label: "改用加热套"
          updates:
            equipment.heating_mantle: true
          resolves_block: true
        - id: "lower_temperature"
          label: "降低反应温度至60°C以下"
          updates:
            protocol.steps[3].parameters.temperature.value: "用户指定"
          note: "降低温度可能影响聚合速率和产物性能"
          resolves_block: true
      auto_recompile: true

    # === 需确认项 ===
    - step: 5
      priority: medium
      type: require_confirmation
      field: "atmosphere.purge_duration"
      description: "确认氮气吹扫时间"
      action: "user_choice"
      inferred_value: 20
      inferred_unit: "min"
      inferred_confidence: 0.60
      options:
        - "15 min"
        - "20 min"
        - "30 min"
        - "其他（请输入）"
      resolves_block: false
      auto_recompile: true

    - step: 6
      priority: medium
      type: require_confirmation
      field: "initiator.name"
      description: "确认引发剂种类"
      action: "user_choice"
      inferred_value: "AIBN"
      inferred_confidence: 0.50
      options:
        - "AIBN（偶氮二异丁腈）"
        - "BPO（过氧化苯甲酰）"
        - "其他（请输入）"
      resolves_block: false
      auto_recompile: true

    # === 一般缺失项 ===
    - step: 7
      priority: low
      type: missing_parameter
      field: "solvent.amount"
      description: "补充甲苯用量"
      action: "user_input"
      prompt: "请输入甲苯用量（单位mL）："
      expected_format: "数值 + mL"
      example: "50 mL"
      resolves_block: false
      auto_recompile: true

    - step: 8
      priority: low
      type: missing_parameter
      field: "cycles"
      description: "补充洗涤次数"
      action: "user_input"
      prompt: "请输入甲醇洗涤次数："
      expected_format: "整数"
      example: "3"
      resolves_block: false
      auto_recompile: true

    - step: 9
      priority: low
      type: missing_parameter
      field: "drying.temperature"
      description: "补充真空干燥温度"
      action: "user_input"
      prompt: "请输入真空干燥温度（单位°C）："
      expected_format: "数值 + °C"
      example: "60°C"
      resolves_block: false
      auto_recompile: true

    - step: 10
      priority: low
      type: missing_parameter
      field: "drying.duration"
      description: "补充真空干燥时间"
      action: "user_input"
      prompt: "请输入真空干燥时间（单位h）："
      expected_format: "数值 + h"
      example: "24 h"
      resolves_block: false
      auto_recompile: true

  # 安全确认步骤
  safety_confirmations:
    - id: "fume_hood_confirmation"
      risk: "易燃溶剂操作"
      question: "混合操作是否在通风橱内进行？"
      required: true
      options: ["是", "否"]

    - id: "AIBN_addition_method"
      risk: "AIBN热分解"
      question: "AIBN加入方式：一次性加入还是分批加入？是否需要控制升温速率？"
      required: true
      options: ["一次性加入", "分批加入", "需控制升温速率"]

    - id: "ventilation_confirmation"
      risk: "氮气窒息"
      question: "反应区域通风是否良好？是否有氧气浓度监测？"
      required: true
      options: ["是，通风良好", "否，需改善通风"]

  # 执行条件
  execution_conditions:
    all_critical_resolved: true
    all_safety_confirmed: true
    equipment_check_passed: true
    minimum_required_fields:
      - "initiator.amount"
      - "initiator.ratio"
      - "duration"
      - "equipment (resolved)"

  # 恢复后预期状态
  post_recovery:
    expected_status: "executable"
    remaining_confirmations: []
    auto_generate_outputs:
      - "protocol.json (updated)"
      - "SOP.md (updated)"
      - "safety_report.md (updated)"
```

---

## 8. 问题分析与Skill行为说明

### 问题1: 缺失参数——引发剂(AIBN)比例未明确给出

| 字段 | 说明 |
|------|------|
| 问题描述 | 原文仅提及"加入引发剂"，未给出引发剂种类、用量和比例 |
| Skill行为 | 将 `initiator.amount` 和 `initiator.ratio` 标记为 `null`，在 `missing_fields` 中列出，状态标记为 `blocked_missing_parameter` |
| 核心原则 | **绝不静默补全**——Skill 未使用"常见引发剂比例1 mol%"等默认值进行补全 |
| 证据绑定 | evidence 字段记录了原文"加入引发剂"，并标注 `note: "原文仅提及'引发剂'，未给出用量"` |
| 恢复路径 | recovery_plan.yaml 步骤1-2，通过用户输入补充 |

### 问题2: 单位不一致——单体量用mL，引发剂用mg

| 字段 | 说明 |
|------|------|
| 问题描述 | 苯乙烯用量以体积(mL)给出，若引发剂用量以质量(mg)给出，单位不一致 |
| Skill行为 | 将苯乙烯体积通过密度转换为质量，再通过摩尔质量转换为摩尔量（`derived` 类型） |
| 核心原则 | **显式归一化+证据绑定**——转换过程完整记录在 `derivation` 字段中 |
| 证据绑定 | evidence 中记录了原始值(20 mL)、中间步骤(体积→质量→摩尔)和最终值(0.17396 mol) |
| 信息类型 | `derived`（计算推导），置信度 1.0 |

### 问题3: 样品命名歧义——"Sample A"/"P1"/"optimized resin"

| 字段 | 说明 |
|------|------|
| 问题描述 | 原文中三个名称指代同一样品 |
| Skill行为 | 在 `sample_registry` 中建立别名映射表，将三个名称关联到同一样品 |
| 核心原则 | **别名解析+证据绑定**——每个别名均标注了 evidence 和推理依据 |
| 证据绑定 | "Sample A" 为 primary_name，"P1" 和 "optimized resin" 为 aliases，均有原文证据 |
| 置信度 | 1.0（原文明确声明"以下简称P1，即optimized resin"） |

### 问题4: 设备超限——需要80°C但油浴锅最高60°C

| 字段 | 说明 |
|------|------|
| 问题描述 | 反应温度80°C超过油浴锅(DF-101S)最高温度60°C |
| Skill行为 | 生成 `safety_warning`（severity: critical），状态标记为 `blocked` |
| 核心原则 | **设备能力校验**——Skill 主动检查设备配置，发现超限后阻止执行 |
| 证据绑定 | evidence 记录了原文"升温至80°C反应"和设备配置（max_temperature: 60°C） |
| 恢复路径 | recovery_plan.yaml 步骤4，提供三种解决方案（更换设备/改用加热套/降低温度） |

### 问题5: 安全确认点——氮气保护时间不明确

| 字段 | 说明 |
|------|------|
| 问题描述 | 原文提及"在氮气气氛下"但未给出吹扫持续时间 |
| Skill行为 | 将 `atmosphere.purge_duration` 标记为 `null`，在 `require_confirmations` 中列出 |
| 核心原则 | **推断值必须确认**——Skill 推断值为20 min（置信度0.60），但标注为 `inferred` 类型，必须经用户确认 |
| 证据绑定 | evidence 记录了原文"在氮气气氛下"，推断依据为"自由基聚合常用氮气吹扫时间为15-30分钟" |
| 信息类型 | `inferred`（合理推断），置信度 0.60 |

---

## 三种信息类型汇总

| 信息类型 | 数量 | 说明 | 示例 |
|---------|------|------|------|
| `extracted` | 6 | 直接从源文档文本中提取 | 温度80°C、氮气气氛、甲醇洗涤 |
| `derived` | 3 | 通过计算推导得出 | 苯乙烯摩尔量、交联剂比例、固含量公式 |
| `inferred` | 2 | 基于领域知识推断，需确认 | 引发剂种类(AIBN)、氮气吹扫时间(20 min) |
| `missing/null` | 7 | 源文档中完全缺失 | 引发剂用量、反应时间、干燥条件等 |

> **核心展示**: 本示例完整展示了 matflow-compiler 的四大核心能力：
> 1. **绝不静默补全**：7个缺失字段全部标记为 `null`，无任何默认值填充
> 2. **证据绑定**：每个参数值均绑定到源文档具体位置（页码、章节、原文片段）
> 3. **三种信息区分**：`extracted` / `derived` / `inferred` 三种类型明确区分，推断型标注置信度
> 4. **阻止执行状态**：`blocked_missing_parameter` 状态阻止协议被执行，直到缺失参数被补充
