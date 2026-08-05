# 电极浆料配制、涂布与热处理——完整示例

> 本示例展示 matflow-compiler Skill 处理能源材料合成协议的完整流程。
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

> "将LiCoO2活性物质(80 wt%)、Super P导电剂(10 wt%)和PVDF粘结剂(10 wt%)加入NMP溶剂中，在行星搅拌器中以2000 rpm混合2小时。将浆料涂布于铝箔上，放入烘箱中120°C干燥1小时，然后压实得到电极片A（记为Electrode-1，简称E1）。"

### 文献信息

| 字段 | 值 |
|------|-----|
| 文档标题 | "High-Performance LiCoO2 Cathode via Optimized Slurry Processing" |
| 文档类型 | 期刊论文 |
| 对应章节 | Section 2.2 Electrode Preparation |
| 页码 | p.892, 第1-2段 |

---

## 2. 输入YAML配置

```yaml
# matflow-compiler 输入配置
# 电极浆料配制、涂布与热处理协议编译

input:
  document:
    type: "text"
    title: "High-Performance LiCoO2 Cathode via Optimized Slurry Processing"
    section: "Section 2.2 Electrode Preparation"
    page: 892
    content: >
      将LiCoO2活性物质(80 wt%)、Super P导电剂(10 wt%)和PVDF粘结剂(10 wt%)
      加入NMP溶剂中，在行星搅拌器中以2000 rpm混合2小时。
      将浆料涂布于铝箔上，放入烘箱中120°C干燥1小时，然后压实得到电极片A
      （记为Electrode-1，简称E1）。

# 实验室设备配置
equipment:
  planetary_mixer:
    model: "ARE-310"
    max_speed: 1500             # 单位: rpm —— 注意：最高仅1500 rpm
    speed_unit: "rpm"
    capacity: 300               # 单位: mL
  coating_machine:
    model: "MSK-AFA-H200A"
    max_coating_speed: 100      # 单位: mm/s
    speed_unit: "mm/s"
    coating_width: 200           # 单位: mm
  oven:
    model: "DHG-9070A"
    max_temperature: 250
    temperature_unit: "°C"
  rolling_press:
    model: "MSK-HRP-1A"
    max_pressure: 200            # 单位: MPa
    pressure_unit: "MPa"
  analytical_balance:
    model: "ME204T"
    unit: "g"
    precision: 0.0001

# 材料数据库
material_database:
  LiCoO2:
    formula: "LiCoO2"
    molar_mass: 97.87            # g/mol
    density: 5.10                # g/cm3
    cas: "12190-79-3"
    hazard: ["toxic_if_ingested", "environmental_hazard"]
  super_P:
    name: "Super P (导电炭黑)"
    density: 0.18                # g/cm3 (松装密度)
    cas: "1333-86-4"
    hazard: ["nuisance_dust"]
  PVDF:
    name: "聚偏氟乙烯 (PVDF)"
    formula: "(CH2CF2)n"
    density: 1.78                # g/cm3
    cas: "24937-79-9"
    hazard: ["irritant"]
  NMP:
    name: "N-甲基吡咯烷酮"
    formula: "C5H9NO"
    molar_mass: 99.13            # g/mol
    density: 1.028               # g/mL
    cas: "872-50-4"
    hazard: ["toxic", "reproductive_hazard", "flammable"]
    flash_point: 91              # °C
    boiling_point: 202           # °C
    exposure_limit:
      type: "TWA"
      value: 5.0                # ppm (ACGIH)
  aluminum_foil:
    name: "铝箔 (集流体)"
    thickness: 16                # μm
    density: 2.70                # g/cm3

# 安全规则
safety_rules:
  - id: "NMP_ventilation"
    description: "NMP溶剂具有生殖毒性和全身毒性，必须在通风橱内操作"
  - id: "NMP_waste_disposal"
    description: "NMP废液需作为有害废液收集处理，不可直接排放"
  - id: "high_speed_mixing"
    description: "高速搅拌操作需确保容器密封，防止浆料飞溅"
  - id: "hot_surface"
    description: "烘箱操作需佩戴隔热手套，防止烫伤"

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
    "title": "电极浆料配制、涂布与热处理协议",
    "source_document": {
      "title": "High-Performance LiCoO2 Cathode via Optimized Slurry Processing",
      "section": "Section 2.2 Electrode Preparation",
      "page": 892
    },
    "generated_by": "matflow-compiler",
    "generated_at": "2026-08-06T10:00:00Z",
    "language": "zh-CN"
  },

  "status": "blocked_missing_parameter",

  "overall_status_detail": {
    "primary_blocker": "blocked_missing_parameter",
    "secondary_issues": [
      "safety_warning: equipment_overlimit_planetary_mixer",
      "require_confirmation: NMP_fume_hood"
    ],
    "executable": false,
    "reason": "涂布速度未在源文档中指定，且存在搅拌器转速超限安全警告和NMP溶剂安全确认需求"
  },

  "sample_registry": {
    "samples": [
      {
        "primary_name": "电极片A",
        "aliases": ["Electrode-1", "E1"],
        "description": "LiCoO2正极片，经浆料涂布、干燥和压实制得",
        "evidence": {
          "document": "source_paper",
          "page": 892,
          "section": "Section 2.2 Electrode Preparation",
          "evidence_type": "extracted",
          "confidence": 1.0,
          "raw_text": "得到电极片A（记为Electrode-1，简称E1）"
        },
        "alias_evidence": [
          {
            "alias": "Electrode-1",
            "evidence_type": "extracted",
            "confidence": 1.0,
            "raw_text": "记为Electrode-1",
            "reasoning": "原文明确声明'记为Electrode-1'，别名关系直接提取"
          },
          {
            "alias": "E1",
            "evidence_type": "extracted",
            "confidence": 1.0,
            "raw_text": "简称E1",
            "reasoning": "原文明确声明'简称E1'，别名关系直接提取"
          }
        ]
      }
    ],
    "ambiguous_mappings": []
  },

  "protocol": {
    "process_type": "electrode_slurry_preparation",
    "steps": [
      {
        "step": 1,
        "name": "slurry_mixing",
        "description": "活性物质、导电剂和粘结剂在NMP溶剂中混合",
        "parameters": {
          "LiCoO2": {
            "name": "LiCoO2",
            "role": "active_material",
            "mass_fraction": {
              "value": 80,
              "unit": "wt%",
              "evidence": {
                "document": "source_paper",
                "page": 892,
                "section": "Section 2.2 Electrode Preparation",
                "evidence_type": "extracted",
                "confidence": 1.0,
                "raw_text": "LiCoO2活性物质(80 wt%)"
              }
            },
            "mass_fraction_normalized": {
              "value": 0.80,
              "unit": "mass_fraction",
              "evidence": {
                "document": "source_paper",
                "page": 892,
                "section": "Section 2.2 Electrode Preparation",
                "evidence_type": "derived",
                "confidence": 1.0,
                "raw_text": "LiCoO2活性物质(80 wt%)",
                "derivation": {
                  "original_value": 80,
                  "original_unit": "wt%",
                  "conversion_factor": 0.01,
                  "converted_value": 0.80,
                  "target_unit": "mass_fraction",
                  "reason": "wt%归一化为质量分数，便于计算"
                }
              }
            }
          },
          "super_P": {
            "name": "Super P",
            "role": "conductive_agent",
            "mass_fraction": {
              "value": 10,
              "unit": "wt%",
              "evidence": {
                "document": "source_paper",
                "page": 892,
                "section": "Section 2.2 Electrode Preparation",
                "evidence_type": "extracted",
                "confidence": 1.0,
                "raw_text": "Super P导电剂(10 wt%)"
              }
            },
            "mass_fraction_normalized": {
              "value": 0.10,
              "unit": "mass_fraction",
              "evidence": {
                "document": "source_paper",
                "page": 892,
                "section": "Section 2.2 Electrode Preparation",
                "evidence_type": "derived",
                "confidence": 1.0,
                "raw_text": "Super P导电剂(10 wt%)",
                "derivation": {
                  "original_value": 10,
                  "original_unit": "wt%",
                  "conversion_factor": 0.01,
                  "converted_value": 0.10,
                  "target_unit": "mass_fraction",
                  "reason": "wt%归一化为质量分数"
                }
              }
            }
          },
          "PVDF": {
            "name": "PVDF",
            "role": "binder",
            "mass_fraction": {
              "value": 10,
              "unit": "wt%",
              "evidence": {
                "document": "source_paper",
                "page": 892,
                "section": "Section 2.2 Electrode Preparation",
                "evidence_type": "extracted",
                "confidence": 1.0,
                "raw_text": "PVDF粘结剂(10 wt%)"
              }
            },
            "mass_fraction_normalized": {
              "value": 0.10,
              "unit": "mass_fraction",
              "evidence": {
                "document": "source_paper",
                "page": 892,
                "section": "Section 2.2 Electrode Preparation",
                "evidence_type": "derived",
                "confidence": 1.0,
                "raw_text": "PVDF粘结剂(10 wt%)",
                "derivation": {
                  "original_value": 10,
                  "original_unit": "wt%",
                  "conversion_factor": 0.01,
                  "converted_value": 0.10,
                  "target_unit": "mass_fraction",
                  "reason": "wt%归一化为质量分数"
                }
              }
            }
          },
          "solvent": {
            "name": "NMP",
            "amount": null,
            "unit": "mL",
            "evidence": {
              "document": "source_paper",
              "page": 892,
              "section": "Section 2.2 Electrode Preparation",
              "evidence_type": "extracted",
              "confidence": 1.0,
              "raw_text": "加入NMP溶剂中",
              "note": "NMP作为溶剂被提及，但具体用量未给出"
            }
          },
          "solid_content_ratio": {
            "value": null,
            "unit": "wt%",
            "evidence": null,
            "note": "固含量（固体总质量占浆料总质量的比例）未在原文中给出，需根据NMP用量计算"
          },
          "mixing_speed": {
            "value": 2000,
            "unit": "rpm",
            "evidence": {
              "document": "source_paper",
              "page": 892,
              "section": "Section 2.2 Electrode Preparation",
              "evidence_type": "extracted",
              "confidence": 1.0,
              "raw_text": "以2000 rpm混合"
            }
          },
          "mixing_duration": {
            "value": 2,
            "unit": "h",
            "evidence": {
              "document": "source_paper",
              "page": 892,
              "section": "Section 2.2 Electrode Preparation",
              "evidence_type": "extracted",
              "confidence": 1.0,
              "raw_text": "混合2小时"
            }
          }
        },
        "equipment_check": {
          "equipment": "planetary_mixer",
          "model": "ARE-310",
          "required_speed": {
            "value": 2000,
            "unit": "rpm"
          },
          "max_speed": {
            "value": 1500,
            "unit": "rpm"
          },
          "status": "overlimit",
          "severity": "critical",
          "message": "混合转速2000 rpm超过行星搅拌器(ARE-310)最高转速1500 rpm，超出500 rpm",
          "suggestion": "请更换高速搅拌设备（如最高转速≥3000 rpm的分散机），或降低转速至1500 rpm以下并延长混合时间"
        }
      },
      {
        "step": 2,
        "name": "coating",
        "description": "浆料涂布于铝箔上",
        "parameters": {
          "substrate": {
            "name": "aluminum_foil",
            "thickness": 16,
            "unit": "μm",
            "evidence": {
              "document": "source_paper",
              "page": 892,
              "section": "Section 2.2 Electrode Preparation",
              "evidence_type": "extracted",
              "confidence": 1.0,
              "raw_text": "涂布于铝箔上"
            }
          },
          "coating_speed": {
            "value": null,
            "unit": "mm/s",
            "evidence": null,
            "note": "涂布速度未在源文档中给出"
          },
          "coating_thickness": {
            "value": null,
            "unit": "μm",
            "evidence": null,
            "note": "涂布厚度（湿膜厚度或面密度）未在源文档中给出"
          },
          "coating_method": {
            "value": null,
            "evidence": null,
            "note": "涂布方式（刮刀涂布/狭缝涂布/浸渍涂布）未在源文档中给出"
          }
        },
        "missing_fields": [
          {
            "field": "coating_speed",
            "description": "涂布速度未在源文档中指定",
            "evidence": null,
            "severity": "critical",
            "suggestion": "请补充涂布速度，例如：'以50 mm/s的速度涂布'"
          },
          {
            "field": "coating_thickness",
            "description": "涂布厚度未在源文档中指定",
            "evidence": null,
            "severity": "medium",
            "suggestion": "请补充涂布厚度或面密度，例如：'湿膜厚度200 μm'或'面密度10 mg/cm2'"
          },
          {
            "field": "coating_method",
            "description": "涂布方式未在源文档中指定",
            "evidence": null,
            "severity": "medium",
            "suggestion": "请补充涂布方式，例如：'使用刮刀涂布器涂布'"
          }
        ]
      },
      {
        "step": 3,
        "name": "drying",
        "description": "烘箱干燥",
        "parameters": {
          "temperature": {
            "value": 120,
            "unit": "°C",
            "evidence": {
              "document": "source_paper",
              "page": 892,
              "section": "Section 2.2 Electrode Preparation",
              "evidence_type": "extracted",
              "confidence": 1.0,
              "raw_text": "放入烘箱中120°C干燥"
            }
          },
          "duration": {
            "value": 1,
            "unit": "h",
            "evidence": {
              "document": "source_paper",
              "page": 892,
              "section": "Section 2.2 Electrode Preparation",
              "evidence_type": "extracted",
              "confidence": 1.0,
              "raw_text": "干燥1小时"
            }
          },
          "atmosphere": {
            "value": null,
            "evidence": null,
            "note": "干燥气氛（空气/真空/惰性气体）未在源文档中给出"
          }
        },
        "equipment_check": {
          "equipment": "oven",
          "model": "DHG-9070A",
          "required_temperature": {
            "value": 120,
            "unit": "°C"
          },
          "max_temperature": {
            "value": 250,
            "unit": "°C"
          },
          "status": "within_limit",
          "message": "干燥温度120°C在烘箱(DHG-9070A)最高温度250°C范围内"
        },
        "missing_fields": [
          {
            "field": "atmosphere",
            "description": "干燥气氛未在源文档中指定",
            "evidence": null,
            "severity": "medium",
            "suggestion": "请补充干燥气氛，例如：'在空气中干燥'或'在真空下干燥'"
          }
        ]
      },
      {
        "step": 4,
        "name": "calendering",
        "description": "压实（辊压）",
        "parameters": {
          "method": "calendering",
          "evidence": {
            "document": "source_paper",
            "page": 892,
            "section": "Section 2.2 Electrode Preparation",
            "evidence_type": "extracted",
            "confidence": 1.0,
            "raw_text": "然后压实"
          },
          "pressure": {
            "value": null,
            "unit": "MPa",
            "evidence": null,
            "note": "压实压力未在源文档中给出"
          },
          "target_density": {
            "value": null,
            "unit": "g/cm3",
            "evidence": null,
            "note": "目标压实密度未在源文档中给出"
          },
          "roller_temperature": {
            "value": null,
            "unit": "°C",
            "evidence": null,
            "note": "辊压温度未在源文档中给出（热辊压/冷辊压未指明）"
          }
        },
        "missing_fields": [
          {
            "field": "pressure",
            "description": "压实压力未在源文档中指定",
            "evidence": null,
            "severity": "medium",
            "suggestion": "请补充压实压力，例如：'在100 MPa下压实'"
          },
          {
            "field": "target_density",
            "description": "目标压实密度未在源文档中指定",
            "evidence": null,
            "severity": "medium",
            "suggestion": "请补充目标压实密度，例如：'压实至3.5 g/cm3'"
          },
          {
            "field": "roller_temperature",
            "description": "辊压温度未在源文档中指定",
            "evidence": null,
            "severity": "low",
            "suggestion": "请补充辊压温度，例如：'室温冷辊压'或'80°C热辊压'"
          }
        ]
      }
    ]
  },

  "missing_fields": [
    {
      "step": 1,
      "field": "solvent.amount",
      "description": "NMP溶剂用量未在源文档中指定",
      "evidence": null,
      "severity": "medium",
      "suggestion": "请补充NMP用量，例如：'加入适量NMP调节固含量至65 wt%'"
    },
    {
      "step": 1,
      "field": "solid_content_ratio",
      "description": "固含量比例未在源文档中给出",
      "evidence": null,
      "severity": "medium",
      "suggestion": "请补充固含量，例如：'固含量65 wt%'"
    },
    {
      "step": 2,
      "field": "coating_speed",
      "description": "涂布速度未在源文档中指定",
      "evidence": null,
      "severity": "critical",
      "suggestion": "请补充涂布速度，例如：'以50 mm/s的速度涂布'"
    },
    {
      "step": 2,
      "field": "coating_thickness",
      "description": "涂布厚度未在源文档中指定",
      "evidence": null,
      "severity": "medium",
      "suggestion": "请补充涂布厚度或面密度"
    },
    {
      "step": 2,
      "field": "coating_method",
      "description": "涂布方式未在源文档中指定",
      "evidence": null,
      "severity": "medium",
      "suggestion": "请补充涂布方式"
    },
    {
      "step": 3,
      "field": "atmosphere",
      "description": "干燥气氛未在源文档中指定",
      "evidence": null,
      "severity": "medium",
      "suggestion": "请补充干燥气氛"
    },
    {
      "step": 4,
      "field": "pressure",
      "description": "压实压力未在源文档中指定",
      "evidence": null,
      "severity": "medium",
      "suggestion": "请补充压实压力"
    },
    {
      "step": 4,
      "field": "target_density",
      "description": "目标压实密度未在源文档中指定",
      "evidence": null,
      "severity": "medium",
      "suggestion": "请补充目标压实密度"
    },
    {
      "step": 4,
      "field": "roller_temperature",
      "description": "辊压温度未在源文档中指定",
      "evidence": null,
      "severity": "low",
      "suggestion": "请补充辊压温度"
    }
  ],

  "safety_warnings": [
    {
      "type": "equipment_overlimit",
      "severity": "critical",
      "step": 1,
      "message": "混合转速2000 rpm超过行星搅拌器(ARE-310)最高转速1500 rpm，超出500 rpm",
      "required_speed": {
        "value": 2000,
        "unit": "rpm"
      },
      "equipment_limit": {
        "value": 1500,
        "unit": "rpm",
        "model": "ARE-310"
      },
      "evidence": {
        "document": "source_paper",
        "page": 892,
        "section": "Section 2.2 Electrode Preparation",
        "evidence_type": "extracted",
        "confidence": 1.0,
        "raw_text": "以2000 rpm混合2小时"
      },
      "action": "blocked",
      "suggestion": "请更换高速搅拌设备（如最高转速≥3000 rpm的分散机），或降低转速至1500 rpm以下并延长混合时间"
    },
    {
      "type": "toxic_solvent",
      "severity": "critical",
      "step": 1,
      "message": "NMP溶剂具有生殖毒性（Reproductive Category 1B）和全身毒性，必须在通风橱内操作",
      "solvent": {
        "name": "NMP",
        "cas": "872-50-4",
        "flash_point": 91,
        "boiling_point": 202,
        "exposure_limit": {
          "type": "TWA",
          "value": 5.0,
          "unit": "ppm"
        },
        "hazard_class": ["toxic", "reproductive_hazard", "flammable"]
      },
      "evidence": {
        "document": "source_paper",
        "page": 892,
        "section": "Section 2.2 Electrode Preparation",
        "evidence_type": "inferred",
        "confidence": 0.95,
        "raw_text": "加入NMP溶剂中",
        "reasoning": "文本提及NMP溶剂，材料数据库显示NMP具有生殖毒性和全身毒性"
      },
      "action": "require_confirmation",
      "required_confirmations": [
        {
          "field": "fume_hood",
          "question": "NMP操作是否在通风橱内进行？",
          "options": ["是，在通风橱内操作", "否，需移至通风橱"]
        },
        {
          "field": "respiratory_protection",
          "question": "操作人员是否佩戴了有机蒸气滤毒面具？",
          "options": ["是", "否"]
        },
        {
          "field": "waste_disposal",
          "question": "NMP废液是否按有害废液收集？",
          "options": ["是", "否"]
        }
      ],
      "suggestion": "NMP操作必须在通风橱内进行，佩戴丁腈手套和有机蒸气滤毒面具，废液按有害废液处理"
    },
    {
      "type": "high_speed_mixing_splash",
      "severity": "warning",
      "step": 1,
      "message": "高速搅拌（2000 rpm）可能导致浆料飞溅，需确保容器密封",
      "evidence": {
        "document": "source_paper",
        "page": 892,
        "section": "Section 2.2 Electrode Preparation",
        "evidence_type": "extracted",
        "confidence": 1.0,
        "raw_text": "以2000 rpm混合2小时"
      },
      "action": "require_confirmation",
      "required_confirmations": [
        {
          "field": "container_sealed",
          "question": "搅拌容器是否密封良好？是否安装了防溅盖？",
          "options": ["是，密封良好", "否，需加装密封盖"]
        }
      ]
    },
    {
      "type": "hot_surface_burn",
      "severity": "warning",
      "step": 3,
      "message": "烘箱120°C操作存在烫伤风险，需佩戴隔热手套",
      "evidence": {
        "document": "source_paper",
        "page": 892,
        "section": "Section 2.2 Electrode Preparation",
        "evidence_type": "extracted",
        "confidence": 1.0,
        "raw_text": "放入烘箱中120°C干燥1小时"
      },
      "action": "info",
      "suggestion": "取放电极片时需佩戴隔热手套，等待温度降至60°C以下再操作"
    }
  ],

  "require_confirmations": [
    {
      "id": "confirm_NMP_fume_hood",
      "step": 1,
      "field": "safety.fume_hood",
      "question": "NMP溶剂具有生殖毒性和全身毒性（TWA限值5 ppm）。请确认NMP操作是否在通风橱内进行：",
      "options": ["是，在通风橱内操作", "否，需移至通风橱"],
      "evidence": {
        "document": "source_paper",
        "page": 892,
        "section": "Section 2.2 Electrode Preparation",
        "evidence_type": "inferred",
        "confidence": 0.95,
        "raw_text": "加入NMP溶剂中",
        "reasoning": "NMP具有生殖毒性（Category 1B），必须在通风橱内操作"
      },
      "required": true
    },
    {
      "id": "confirm_NMP_waste_disposal",
      "step": 1,
      "field": "safety.waste_disposal",
      "question": "NMP废液需作为有害废液收集处理。请确认废液收集方案：",
      "options": ["已有有害废液收集容器", "需准备废液收集容器"],
      "evidence": {
        "document": "source_paper",
        "page": 892,
        "section": "Section 2.2 Electrode Preparation",
        "evidence_type": "inferred",
        "confidence": 0.90,
        "raw_text": "加入NMP溶剂中",
        "reasoning": "NMP为有害溶剂，废液不可直接排放"
      },
      "required": true
    }
  ],

  "evidence_summary": {
    "total_parameters": 18,
    "extracted": 7,
    "derived": 3,
    "inferred": 1,
    "missing": 9,
    "null_fields": 9,
    "evidence_types": {
      "extracted": "直接从源文档文本中提取的参数值",
      "derived": "通过计算推导得出的参数值（如wt%转质量分数）",
      "inferred": "基于领域知识推断的参数值，必须经用户确认"
    }
  }
}
```

---

## 4. 预期输出 SOP.md

```markdown
# 标准操作程序 (SOP)
## 电极浆料配制、涂布与热处理协议

> **状态: 阻止执行 (blocked_missing_parameter)**
> 本协议包含未解决的关键缺失参数和安全警告，不可直接执行。
> 请先补充缺失参数并确认安全事项后再执行。

---

### 协议信息

| 字段 | 值 |
|------|-----|
| 来源文献 | High-Performance LiCoO2 Cathode via Optimized Slurry Processing |
| 章节 | Section 2.2 Electrode Preparation |
| 页码 | p.892 |
| 工艺类型 | 电极浆料制备 |
| 样品名称 | 电极片A (别名: Electrode-1, E1) |

---

### 步骤 1: 浆料混合

**操作**: 将LiCoO2、Super P和PVDF加入NMP溶剂中，在行星搅拌器中混合。

| 参数 | 值 | 单位 | 证据类型 | 来源 |
|------|-----|------|---------|------|
| LiCoO2 | 80 (0.80) | wt% (质量分数) | extracted → derived | "LiCoO2活性物质(80 wt%)" |
| Super P | 10 (0.10) | wt% (质量分数) | extracted → derived | "Super P导电剂(10 wt%)" |
| PVDF | 10 (0.10) | wt% (质量分数) | extracted → derived | "PVDF粘结剂(10 wt%)" |
| 溶剂 | NMP | — | extracted | "加入NMP溶剂中" |
| 溶剂用量 | **[缺失]** | mL | — | 原文未给出NMP用量 |
| 固含量 | **[缺失]** | wt% | — | 原文未给出固含量 |
| 混合转速 | 2000 | rpm | extracted | "以2000 rpm混合" |
| 混合时间 | 2 | h | extracted | "混合2小时" |

> **阻止执行 - 设备超限**: 混合转速2000 rpm超过行星搅拌器(ARE-310)最高转速1500 rpm，超出500 rpm。
> 请更换高速搅拌设备（如最高转速≥3000 rpm的分散机），或降低转速至1500 rpm以下并延长混合时间。
>
> **安全提示 - NMP毒性**: NMP具有生殖毒性（Category 1B）和全身毒性（TWA限值5 ppm），必须在通风橱内操作，佩戴丁腈手套和有机蒸气滤毒面具。
>
> **安全提示 - 飞溅风险**: 高速搅拌（2000 rpm）可能导致浆料飞溅，需确保容器密封。

---

### 步骤 2: 涂布

**操作**: 将浆料涂布于铝箔上。

| 参数 | 值 | 单位 | 证据类型 | 来源 |
|------|-----|------|---------|------|
| 基材 | 铝箔 (16 μm) | — | extracted | "涂布于铝箔上" |
| 涂布速度 | **[缺失]** | mm/s | — | 原文未给出涂布速度 |
| 涂布厚度 | **[缺失]** | μm | — | 原文未给出涂布厚度 |
| 涂布方式 | **[缺失]** | — | — | 原文未给出涂布方式 |

> **阻止执行**: 涂布速度是关键参数，缺失将导致无法控制涂布均匀性和膜厚。

---

### 步骤 3: 干燥

**操作**: 放入烘箱中120°C干燥1小时。

| 参数 | 值 | 单位 | 证据类型 | 来源 |
|------|-----|------|---------|------|
| 干燥温度 | 120 | °C | extracted | "放入烘箱中120°C干燥" |
| 干燥时间 | 1 | h | extracted | "干燥1小时" |
| 干燥气氛 | **[缺失]** | — | — | 原文未给出干燥气氛 |

> **设备检查通过**: 干燥温度120°C在烘箱(DHG-9070A)最高温度250°C范围内。
>
> **安全提示**: 烘箱120°C操作存在烫伤风险，取放电极片时需佩戴隔热手套，等待温度降至60°C以下再操作。

---

### 步骤 4: 压实

**操作**: 压实得到电极片。

| 参数 | 值 | 单位 | 证据类型 | 来源 |
|------|-----|------|---------|------|
| 压实方式 | 辊压 | — | extracted | "然后压实" |
| 压实压力 | **[缺失]** | MPa | — | 原文未给出压实压力 |
| 目标密度 | **[缺失]** | g/cm3 | — | 原文未给出目标压实密度 |
| 辊压温度 | **[缺失]** | °C | — | 原文未给出辊压温度 |

---

### 缺失参数汇总

| 步骤 | 缺失字段 | 严重程度 | 状态 |
|------|---------|---------|------|
| 1 | NMP溶剂用量 | medium | — |
| 1 | 固含量比例 | medium | — |
| 2 | 涂布速度 | critical | blocked |
| 2 | 涂布厚度 | medium | — |
| 2 | 涂布方式 | medium | — |
| 3 | 干燥气氛 | medium | — |
| 4 | 压实压力 | medium | — |
| 4 | 目标压实密度 | medium | — |
| 4 | 辊压温度 | low | — |

> **结论**: 本协议因缺失涂布速度等关键参数，且存在搅拌器转速超限安全警告和NMP溶剂安全确认需求，当前状态为 **阻止执行**。请补充上述缺失参数并解决安全问题后重新编译。
```

---

## 5. 预期输出 missing_conditions.md

```markdown
# 缺失条件报告
## 电极浆料配制、涂布与热处理协议

> 本报告列出协议中所有未从源文档提取到的条件参数。
> 每个缺失项均标注了严重程度和建议补充方式。
> **matflow-compiler 绝不静默补全任何以下缺失项。**

---

## 关键缺失项 (Critical)

### 1. 涂布速度 (coating_speed)

| 字段 | 内容 |
|------|------|
| 步骤 | 步骤 2: 涂布 |
| 字段名 | coating_speed |
| 描述 | 涂布速度未在源文档中指定 |
| 严重程度 | **Critical** |
| 证据 | null（源文档中无对应文本） |
| 源文本 | "将浆料涂布于铝箔上"（仅提及涂布，未给出速度） |
| 影响 | 无法控制涂布均匀性、膜厚和干燥速率 |
| 建议补充 | "以50 mm/s的速度涂布" |
| 状态 | **blocked_missing_parameter** |

---

## 一般缺失项 (Medium)

### 2. NMP溶剂用量 (solvent.amount)

| 字段 | 内容 |
|------|------|
| 步骤 | 步骤 1: 浆料混合 |
| 字段名 | solvent.amount |
| 描述 | NMP溶剂用量未在源文档中指定 |
| 严重程度 | Medium |
| 证据 | "加入NMP溶剂中"（extracted, 置信度 1.0） |
| 建议补充 | "加入适量NMP调节固含量至65 wt%" |

### 3. 固含量比例 (solid_content_ratio)

| 字段 | 内容 |
|------|------|
| 步骤 | 步骤 1: 浆料混合 |
| 字段名 | solid_content_ratio |
| 描述 | 固含量比例未在源文档中给出 |
| 严重程度 | Medium |
| 证据 | null |
| 建议补充 | "固含量65 wt%" |

### 4. 涂布厚度 (coating_thickness)

| 字段 | 内容 |
|------|------|
| 步骤 | 步骤 2: 涂布 |
| 字段名 | coating_thickness |
| 描述 | 涂布厚度（湿膜厚度或面密度）未在源文档中给出 |
| 严重程度 | Medium |
| 证据 | null |
| 建议补充 | "湿膜厚度200 μm"或"面密度10 mg/cm2" |

### 5. 涂布方式 (coating_method)

| 字段 | 内容 |
|------|------|
| 步骤 | 步骤 2: 涂布 |
| 字段名 | coating_method |
| 描述 | 涂布方式未在源文档中指定 |
| 严重程度 | Medium |
| 证据 | null |
| 建议补充 | "使用刮刀涂布器涂布" |

### 6. 干燥气氛 (atmosphere)

| 字段 | 内容 |
|------|------|
| 步骤 | 步骤 3: 干燥 |
| 字段名 | atmosphere |
| 描述 | 干燥气氛（空气/真空/惰性气体）未在源文档中给出 |
| 严重程度 | Medium |
| 证据 | null |
| 建议补充 | "在空气中干燥"或"在真空下干燥" |

### 7. 压实压力 (pressure)

| 字段 | 内容 |
|------|------|
| 步骤 | 步骤 4: 压实 |
| 字段名 | pressure |
| 描述 | 压实压力未在源文档中指定 |
| 严重程度 | Medium |
| 证据 | null |
| 建议补充 | "在100 MPa下压实" |

### 8. 目标压实密度 (target_density)

| 字段 | 内容 |
|------|------|
| 步骤 | 步骤 4: 压实 |
| 字段名 | target_density |
| 描述 | 目标压实密度未在源文档中指定 |
| 严重程度 | Medium |
| 证据 | null |
| 建议补充 | "压实至3.5 g/cm3" |

---

## 低优先级缺失项 (Low)

### 9. 辊压温度 (roller_temperature)

| 字段 | 内容 |
|------|------|
| 步骤 | 步骤 4: 压实 |
| 字段名 | roller_temperature |
| 描述 | 辊压温度（热辊压/冷辊压）未在源文档中指定 |
| 严重程度 | Low |
| 证据 | null |
| 建议补充 | "室温冷辊压"或"80°C热辊压" |

---

## 统计

| 类别 | 数量 |
|------|------|
| Critical (阻止执行) | 1 |
| Require Confirmation (需确认) | 0 |
| Medium (一般缺失) | 7 |
| Low (低优先级) | 1 |
| **总计** | **9** |

> **注意**: 以上缺失项均未被 matflow-compiler 静默补全。所有缺失字段在 protocol.json 中标记为 `null`，并在 `missing_fields` 数组中显式列出。
```

---

## 6. 预期输出 safety_report.md

```markdown
# 安全报告
## 电极浆料配制、涂布与热处理协议

> 本报告列出协议执行过程中可能涉及的安全风险。
> 每个风险项均标注了严重程度、风险因素和建议措施。

---

## 风险等级: 高 (HIGH)

### 风险 1: 设备超限——搅拌器转速不足

| 字段 | 内容 |
|------|------|
| 风险类型 | 设备超限 (equipment_overlimit) |
| 严重程度 | **Critical** |
| 步骤 | 步骤 1: 浆料混合 |
| 描述 | 混合转速2000 rpm超过行星搅拌器(ARE-310)最高转速1500 rpm，超出500 rpm |
| 所需转速 | 2000 rpm |
| 设备限制 | 1500 rpm (ARE-310) |
| 证据 | "以2000 rpm混合2小时" (extracted, 置信度 1.0) |
| 执行动作 | **blocked** |
| 建议措施 | 更换高速搅拌设备（如最高转速≥3000 rpm的分散机），或降低转速至1500 rpm以下并延长混合时间 |

**风险分析**:
- 超速使用可能导致搅拌器电机过载、烧毁
- 转速不足时浆料分散不均匀，影响电极性能
- 强行超速可能导致设备机械故障或飞溅

---

### 风险 2: NMP溶剂毒性

| 字段 | 内容 |
|------|------|
| 风险类型 | 有毒溶剂 (toxic_solvent) |
| 严重程度 | **Critical** |
| 步骤 | 步骤 1: 浆料混合 |
| 描述 | NMP溶剂具有生殖毒性（Reproductive Category 1B）和全身毒性 |
| 涉及溶剂 | NMP (CAS: 872-50-4) |
| 闪点 | 91°C |
| 沸点 | 202°C |
| 暴露限值 | TWA 5.0 ppm (ACGIH) |
| 危害分类 | 生殖毒性、全身毒性、可燃 |
| 证据 | "加入NMP溶剂中" (inferred, 置信度 0.95) |
| 执行动作 | **require_confirmation** |
| 需确认 | (1) NMP操作是否在通风橱内进行？ (2) 操作人员是否佩戴有机蒸气滤毒面具？ (3) NMP废液是否按有害废液收集？ |
| 建议措施 | NMP操作必须在通风橱内进行，佩戴丁腈手套和有机蒸气滤毒面具，废液按有害废液处理 |

**风险分析**:
- NMP可通过皮肤吸收和呼吸道吸入造成全身暴露
- 长期接触可导致生殖系统损害和神经系统损伤
- 孕妇和备孕人员应避免接触NMP
- NMP废液不可直接排放，需按有害废液处理

---

### 风险 3: 高速搅拌飞溅

| 字段 | 内容 |
|------|------|
| 风险类型 | 物理飞溅 (high_speed_mixing_splash) |
| 严重程度 | **Warning** |
| 步骤 | 步骤 1: 浆料混合 |
| 描述 | 高速搅拌（2000 rpm）可能导致浆料飞溅 |
| 证据 | "以2000 rpm混合2小时" (extracted, 置信度 1.0) |
| 执行动作 | **require_confirmation** |
| 需确认 | 搅拌容器是否密封良好？是否安装了防溅盖？ |
| 建议措施 | 确保搅拌容器密封，安装防溅盖，操作人员佩戴护目镜和实验服 |

---

### 风险 4: 烫伤风险

| 字段 | 内容 |
|------|------|
| 风险类型 | 高温表面 (hot_surface_burn) |
| 严重程度 | **Warning** |
| 步骤 | 步骤 3: 干燥 |
| 描述 | 烘箱120°C操作存在烫伤风险 |
| 证据 | "放入烘箱中120°C干燥1小时" (extracted, 置信度 1.0) |
| 执行动作 | **info** |
| 建议措施 | 取放电极片时需佩戴隔热手套，等待温度降至60°C以下再操作 |

---

## 安全措施清单

| 编号 | 措施 | 对应风险 | 必需/推荐 |
|------|------|---------|----------|
| 1 | 更换高速搅拌设备或降低转速 | 风险1 | 必需 |
| 2 | 在通风橱内进行NMP操作 | 风险2 | 必需 |
| 3 | 佩戴丁腈手套和有机蒸气滤毒面具 | 风险2 | 必需 |
| 4 | NMP废液按有害废液收集 | 风险2 | 必需 |
| 5 | 确保搅拌容器密封，安装防溅盖 | 风险3 | 必需 |
| 6 | 佩戴护目镜 | 风险3 | 必需 |
| 7 | 佩戴隔热手套取放烘箱内物品 | 风险4 | 必需 |
| 8 | 准备灭火器（干粉/CO2） | 风险2 | 推荐 |

---

## 个人防护装备 (PPE) 要求

| 装备 | 要求 |
|------|------|
| 护目镜 | 必需（防化学飞溅和浆料飞溅） |
| 实验服 | 必需（防化学飞溅） |
| 丁腈手套 | 必需（防NMP渗透，需选择耐NMP材质） |
| 有机蒸气滤毒面具 | 必需（防NMP蒸气吸入） |
| 隔热手套 | 必需（烘箱操作） |

---

## NMP特殊安全说明

> **N-甲基吡咯烷酮 (NMP, CAS: 872-50-4)**
>
> NMP被欧盟REACH法规列为生殖毒性1B类物质（可能损害生育能力或未出生胎儿）。
> 美国ACGIH建议TWA暴露限值为5.0 ppm（20 mg/m3）。
>
> **安全操作要求**:
> 1. 必须在通风橱内操作
> 2. 佩戴丁腈手套（注意：普通乳胶手套对NMP防护效果有限）
> 3. 佩戴有机蒸气滤毒面具
> 4. 避免皮肤接触和蒸气吸入
> 5. 废液按有害废液处理，不可直接排放
> 6. 孕妇和备孕人员应避免接触

---

> **结论**: 本协议存在2个Critical级安全风险（设备超限和NMP毒性）和2个Warning级安全风险。设备超限问题必须解决后方可执行，NMP安全措施需用户确认后执行。
```

---

## 7. 预期输出 recovery_plan.yaml

```yaml
# 恢复计划 - 电极浆料配制、涂布与热处理协议
# 本文件提供解决协议阻塞和缺失参数的恢复路径

recovery_plan:
  protocol_id: "electrode_slurry_preparation_001"
  current_status: "blocked_missing_parameter"
  target_status: "executable"

  # 阻塞项解决步骤（按优先级排序）
  resolution_steps:

    # === Critical 阻塞项 ===
    - step: 1
      priority: critical
      type: missing_parameter
      field: "coating_speed"
      description: "补充涂布速度"
      action: "user_input"
      prompt: "请输入涂布速度（单位mm/s）："
      expected_format: "数值 + mm/s"
      example: "50 mm/s"
      resolves_block: true
      auto_recompile: true

    # === 设备超限解决 ===
    - step: 2
      priority: critical
      type: equipment_overlimit
      field: "planetary_mixer.speed"
      description: "解决搅拌器转速不足问题"
      action: "user_choice"
      options:
        - id: "replace_equipment"
          label: "更换高速分散机（≥3000 rpm）"
          updates:
            equipment.planetary_mixer.model: "用户指定"
            equipment.planetary_mixer.max_speed: "用户指定"
          resolves_block: true
        - id: "lower_speed_extend_time"
          label: "降低转速至1500 rpm并延长混合时间至4小时"
          updates:
            protocol.steps[1].parameters.mixing_speed.value: 1500
            protocol.steps[1].parameters.mixing_duration.value: 4
          note: "降低转速可能影响浆料分散均匀性，需验证效果"
          resolves_block: true
        - id: "two_step_mixing"
          label: "两步混合：先1500 rpm混合1小时，再手动分散后1500 rpm混合1小时"
          updates:
            protocol.steps[1].parameters.mixing_speed.value: 1500
            protocol.steps[1].description: "两步混合法"
          resolves_block: true
      auto_recompile: true

    # === 安全确认 ===
    - step: 3
      priority: critical
      type: require_confirmation
      field: "safety.fume_hood"
      description: "确认NMP操作安全措施"
      action: "user_choice"
      question: "NMP溶剂具有生殖毒性和全身毒性（TWA限值5 ppm）。请确认NMP操作是否在通风橱内进行："
      options:
        - "是，在通风橱内操作"
        - "否，需移至通风橱"
      required: true
      resolves_block: false
      auto_recompile: true

    - step: 4
      priority: critical
      type: require_confirmation
      field: "safety.waste_disposal"
      description: "确认NMP废液处理方案"
      action: "user_choice"
      question: "NMP废液需作为有害废液收集处理。请确认废液收集方案："
      options:
        - "已有有害废液收集容器"
        - "需准备废液收集容器"
      required: true
      resolves_block: false
      auto_recompile: true

    - step: 5
      priority: medium
      type: require_confirmation
      field: "safety.container_sealed"
      description: "确认搅拌容器密封"
      action: "user_choice"
      question: "高速搅拌可能导致浆料飞溅。请确认搅拌容器是否密封良好："
      options:
        - "是，密封良好"
        - "否，需加装密封盖"
      required: true
      resolves_block: false
      auto_recompile: true

    # === 一般缺失项 ===
    - step: 6
      priority: medium
      type: missing_parameter
      field: "solvent.amount"
      description: "补充NMP溶剂用量"
      action: "user_input"
      prompt: "请输入NMP溶剂用量（单位mL）或固含量（wt%）："
      expected_format: "数值 + 单位"
      example: "30 mL 或 65 wt%"
      resolves_block: false
      auto_recompile: true

    - step: 7
      priority: medium
      type: missing_parameter
      field: "coating_thickness"
      description: "补充涂布厚度"
      action: "user_input"
      prompt: "请输入涂布厚度（单位μm）或面密度（mg/cm2）："
      expected_format: "数值 + 单位"
      example: "200 μm 或 10 mg/cm2"
      resolves_block: false
      auto_recompile: true

    - step: 8
      priority: medium
      type: missing_parameter
      field: "coating_method"
      description: "补充涂布方式"
      action: "user_choice"
      prompt: "请选择涂布方式："
      options:
        - "刮刀涂布 (doctor blade)"
        - "狭缝涂布 (slot-die)"
        - "浸渍涂布 (dip coating)"
        - "其他（请说明）"
      resolves_block: false
      auto_recompile: true

    - step: 9
      priority: medium
      type: missing_parameter
      field: "atmosphere"
      description: "补充干燥气氛"
      action: "user_choice"
      prompt: "请选择干燥气氛："
      options:
        - "空气干燥"
        - "真空干燥"
        - "惰性气体（氩气/氮气）"
      resolves_block: false
      auto_recompile: true

    - step: 10
      priority: medium
      type: missing_parameter
      field: "pressure"
      description: "补充压实压力"
      action: "user_input"
      prompt: "请输入压实压力（单位MPa）："
      expected_format: "数值 + MPa"
      example: "100 MPa"
      resolves_block: false
      auto_recompile: true

    - step: 11
      priority: medium
      type: missing_parameter
      field: "target_density"
      description: "补充目标压实密度"
      action: "user_input"
      prompt: "请输入目标压实密度（单位g/cm3）："
      expected_format: "数值 + g/cm3"
      example: "3.5 g/cm3"
      resolves_block: false
      auto_recompile: true

    - step: 12
      priority: low
      type: missing_parameter
      field: "roller_temperature"
      description: "补充辊压温度"
      action: "user_choice"
      prompt: "请选择辊压温度："
      options:
        - "室温冷辊压"
        - "热辊压（请输入温度）"
      resolves_block: false
      auto_recompile: true

  # 安全确认步骤
  safety_confirmations:
    - id: "NMP_fume_hood_confirmation"
      risk: "NMP毒性"
      question: "NMP操作是否在通风橱内进行？"
      required: true
      options: ["是", "否"]

    - id: "NMP_respiratory_protection"
      risk: "NMP蒸气吸入"
      question: "操作人员是否佩戴了有机蒸气滤毒面具？"
      required: true
      options: ["是", "否"]

    - id: "NMP_waste_disposal_confirmation"
      risk: "NMP废液污染"
      question: "NMP废液是否按有害废液收集？"
      required: true
      options: ["是", "否"]

    - id: "container_sealed_confirmation"
      risk: "浆料飞溅"
      question: "搅拌容器是否密封良好？是否安装了防溅盖？"
      required: true
      options: ["是", "否"]

  # 执行条件
  execution_conditions:
    all_critical_resolved: true
    all_safety_confirmed: true
    equipment_check_passed: true
    minimum_required_fields:
      - "coating_speed"
      - "equipment (resolved)"
      - "safety.fume_hood (confirmed)"
      - "safety.waste_disposal (confirmed)"

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

### 问题1: 缺失参数——涂布速度未指定

| 字段 | 说明 |
|------|------|
| 问题描述 | 原文仅提及"将浆料涂布于铝箔上"，未给出涂布速度 |
| Skill行为 | 将 `coating_speed` 标记为 `null`，在 `missing_fields` 中列出，状态标记为 `blocked_missing_parameter` |
| 核心原则 | **绝不静默补全**——Skill 未使用"常见涂布速度50 mm/s"等默认值进行补全 |
| 证据绑定 | evidence 字段为 null，标注"涂布速度未在源文档中给出" |
| 恢复路径 | recovery_plan.yaml 步骤1，通过用户输入补充 |

### 问题2: 单位不一致——溶剂比例用体积比(v/v)，固体用wt%

| 字段 | 说明 |
|------|------|
| 问题描述 | 固体组分用wt%（质量百分比），若溶剂比例用v/v（体积比），单位体系不一致 |
| Skill行为 | 将wt%归一化为质量分数（0-1区间），便于统一计算和配比 |
| 核心原则 | **显式归一化+证据绑定**——转换过程完整记录在 `derivation` 字段中 |
| 证据绑定 | evidence 中记录了原始值(80 wt%)、转换因子(0.01)和最终值(0.80) |
| 信息类型 | `derived`（计算推导），置信度 1.0 |

### 问题3: 样品命名歧义——"电极片A"/"Electrode-1"/"E1"

| 字段 | 说明 |
|------|------|
| 问题描述 | 原文中三个名称指代同一样品 |
| Skill行为 | 在 `sample_registry` 中建立别名映射表，将三个名称关联到同一样品 |
| 核心原则 | **别名解析+证据绑定**——每个别名均标注了 evidence 和推理依据 |
| 证据绑定 | "电极片A" 为 primary_name，"Electrode-1" 和 "E1" 为 aliases，均有原文证据 |
| 置信度 | 1.0（原文明确声明"记为Electrode-1，简称E1"） |

### 问题4: 设备超限——需要2000 rpm但搅拌器最高1500 rpm

| 字段 | 说明 |
|------|------|
| 问题描述 | 混合转速2000 rpm超过行星搅拌器(ARE-310)最高转速1500 rpm |
| Skill行为 | 生成 `safety_warning`（severity: critical），状态标记为 `blocked` |
| 核心原则 | **设备能力校验**——Skill 主动检查设备配置，发现超限后阻止执行 |
| 证据绑定 | evidence 记录了原文"以2000 rpm混合2小时"和设备配置（max_speed: 1500 rpm） |
| 恢复路径 | recovery_plan.yaml 步骤2，提供三种解决方案（更换设备/降速延时/两步混合） |

### 问题5: 安全确认点——NMP溶剂需要通风橱

| 字段 | 说明 |
|------|------|
| 问题描述 | NMP具有生殖毒性和全身毒性，需在通风橱内操作 |
| Skill行为 | 生成 `safety_warning`（severity: critical），在 `require_confirmations` 中列出 |
| 核心原则 | **安全风险检测**——Skill 从材料数据库获取NMP危害信息，主动提示安全要求 |
| 证据绑定 | evidence 记录了原文"加入NMP溶剂中"，推理依据为"NMP具有生殖毒性（Category 1B）" |
| 信息类型 | `inferred`（基于材料数据库的推理），置信度 0.95 |
| 恢复路径 | recovery_plan.yaml 步骤3-4，通过用户确认安全措施 |

---

## 三种信息类型汇总

| 信息类型 | 数量 | 说明 | 示例 |
|---------|------|------|------|
| `extracted` | 7 | 直接从源文档文本中提取 | 转速2000 rpm、温度120°C、时间1 h |
| `derived` | 3 | 通过计算推导得出 | wt%→质量分数转换（LiCoO2/Super P/PVDF） |
| `inferred` | 1 | 基于领域知识推断，需确认 | NMP毒性风险（基于材料数据库） |
| `missing/null` | 9 | 源文档中完全缺失 | 涂布速度、NMP用量、压实压力等 |

> **核心展示**: 本示例完整展示了 matflow-compiler 的四大核心能力：
> 1. **绝不静默补全**：9个缺失字段全部标记为 `null`，无任何默认值填充
> 2. **证据绑定**：每个参数值均绑定到源文档具体位置（页码、章节、原文片段）
> 3. **三种信息区分**：`extracted` / `derived` / `inferred` 三种类型明确区分，推断型标注置信度
> 4. **阻止执行状态**：`blocked_missing_parameter` 状态阻止协议被执行，直到缺失参数被补充和安全问题被解决
