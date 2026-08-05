# 溶胶-凝胶法合成 SiO2 纳米颗粒 — 完整示例

> 本示例展示 matflow-compiler Skill 如何从文献实验部分文本中提取材料合成协议，
> 并处理五类常见问题：缺失参数、单位不一致、样品命名歧义、设备超限、安全确认点。

---

## 1. 输入文献描述（模拟论文实验部分文本）

```text
2. Experimental Section

2.1 Materials
Tetraethyl orthosilicate (TEOS, Si(OC2H5)4, 98%), ethanol (EtOH, 99.8%),
deionized water, and hydrochloric acid (HCl, 37 wt%) were purchased from
Sigma-Aldrich and used as received without further purification.

2.2 Synthesis of SiO2 Nanoparticles

In a typical synthesis, 4.16 g of TEOS was dissolved in 20 mL of ethanol
in a 250 mL round-bottom flask under magnetic stirring at room temperature.
A mixture of deionized water (3.6 g) and HCl (0.1 M, 0.5 mL) was added
dropwise to the TEOS solution over a period of 10 minutes. The resulting
sol was stirred at 60 °C for a certain period to form a transparent gel.

The gel was then transferred to a porcelain crucible and dried in an oven
at 80 °C for 12 h. Subsequently, the dried gel was calcined in a muffle
furnace at 300 °C for 2 h with a heating rate of 2 °C/min under air
atmosphere. The furnace used in this study (Nabertherm L9/13) has a
maximum operating temperature of 250 °C.

For comparison, Sample-1 was prepared with a TEOS:H2O molar ratio of 1:2,
while S1 was synthesized with a ratio of 1:4. The optimized sample was
obtained by adjusting the HCl catalyst amount to 0.3 mL.

2.3 Safety Considerations
The calcination step was performed in a sealed crucible to prevent
contamination. Operators must confirm that the crucible lid is properly
sealed before heating.

2.4 Characterization
The as-prepared SiO2 nanoparticles were characterized by XRD, TEM, and
BET surface area analysis. The BET surface area of Sample-1 was
320 mg/g. The optimized sample showed a surface area of 450 mg/g.
```

### 文本中故意设置的 5 个问题点

| 编号 | 问题类型 | 具体描述 | 预期处理方式 |
|------|----------|----------|--------------|
| P1 | 缺失参数 | "stirred at 60 °C for a certain period" — 搅拌时间未给出具体数值 | 标记为 `blocked_missing_parameter`，写入 missing_fields |
| P2 | 单位不一致 | BET 比表面积使用 `mg/g`，标准单位应为 `m²/g` | 自动归一化为 `m²/g`，在 evidence 中记录原始值 |
| P3 | 样品命名歧义 | `Sample-1`、`S1`、`optimized sample` 三种命名混用，对应关系不明确 | 解析对应关系表，在 protocol 中建立 alias 映射 |
| P4 | 设备超限 | 需要 300 °C 煅烧，但马弗炉最高 250 °C | 生成 safety warning，标记 `equipment_limit_exceeded` |
| P5 | 安全确认点 | 密闭坩埚加热，需操作员确认密封 | 标记 `require_confirmation`，写入 safety_report |

---

## 2. 预期输出 — protocol.json

```json
{
  "protocol_id": "SOL-GEL-SIO2-001",
  "material": {
    "name": "SiO2 nanoparticles",
    "formula": "SiO2",
    "category": "inorganic",
    "morphology": "nanoparticle",
    "target_properties": {
      "crystallinity": "amorphous",
      "surface_area_m2_per_g": 450
    }
  },
  "source": {
    "literature": "simulated_paper_sol_gel_2024",
    "section": "2.2 Synthesis of SiO2 Nanoparticles",
    "doi": null
  },
  "reagents": [
    {
      "name": "Tetraethyl orthosilicate (TEOS)",
      "formula": "Si(OC2H5)4",
      "purity": "98%",
      "amount": {
        "value": 4.16,
        "unit": "g",
        "normalized_value_g": 4.16,
        "molar_amount_mol": 0.0199,
        "molar_mass_g_per_mol": 208.33
      },
      "role": "precursor",
      "supplier": "Sigma-Aldrich"
    },
    {
      "name": "Ethanol (EtOH)",
      "formula": "C2H5OH",
      "purity": "99.8%",
      "amount": {
        "value": 20,
        "unit": "mL",
        "normalized_value_g": 15.81,
        "density_g_per_mL": 0.789
      },
      "role": "solvent",
      "supplier": "Sigma-Aldrich"
    },
    {
      "name": "Deionized water",
      "formula": "H2O",
      "purity": "lab grade",
      "amount": {
        "value": 3.6,
        "unit": "g",
        "normalized_value_g": 3.6,
        "molar_amount_mol": 0.200
      },
      "role": "hydrolysis agent"
    },
    {
      "name": "Hydrochloric acid (HCl)",
      "formula": "HCl",
      "purity": "37 wt%",
      "amount": {
        "value": 0.5,
        "unit": "mL",
        "concentration": "0.1 M",
        "normalized_value_g": 0.0001825,
        "note": "0.1 M 稀释液，0.5 mL 中含 HCl 0.0001825 g"
      },
      "role": "catalyst"
    }
  ],
  "equipment": [
    {
      "name": "Round-bottom flask",
      "capacity_mL": 250,
      "material": "glass"
    },
    {
      "name": "Magnetic stirrer",
      "type": "hotplate",
      "max_temperature_C": 250,
      "max_rpm": 1500
    },
    {
      "name": "Porcelain crucible",
      "capacity_mL": 30,
      "max_temperature_C": 1200
    },
    {
      "name": "Drying oven",
      "max_temperature_C": 300
    },
    {
      "name": "Muffle furnace (Nabertherm L9/13)",
      "max_temperature_C": 250,
      "warning": "设备最高温度 250 °C，低于工艺要求的 300 °C，存在超限风险"
    }
  ],
  "steps": [
    {
      "step_id": "STEP-01",
      "action": "dissolve",
      "description": "将 TEOS 溶解于乙醇中",
      "parameters": {
        "reagent": "TEOS",
        "amount_g": 4.16,
        "solvent": "ethanol",
        "solvent_volume_mL": 20,
        "temperature_C": 25,
        "vessel": "250 mL round-bottom flask"
      },
      "duration_min": null,
      "evidence": {
        "source_text": "4.16 g of TEOS was dissolved in 20 mL of ethanol in a 250 mL round-bottom flask under magnetic stirring at room temperature.",
        "source_section": "2.2",
        "confidence": 0.95
      }
    },
    {
      "step_id": "STEP-02",
      "action": "add_dropwise",
      "description": "将水和 HCl 混合液逐滴加入 TEOS 溶液",
      "parameters": {
        "reagents": ["deionized water", "HCl (0.1 M)"],
        "water_amount_g": 3.6,
        "hcl_volume_mL": 0.5,
        "hcl_concentration_M": 0.1,
        "addition_rate": "dropwise",
        "duration_min": 10
      },
      "evidence": {
        "source_text": "A mixture of deionized water (3.6 g) and HCl (0.1 M, 0.5 mL) was added dropwise to the TEOS solution over a period of 10 minutes.",
        "source_section": "2.2",
        "confidence": 0.93
      }
    },
    {
      "step_id": "STEP-03",
      "action": "stir_and_gel",
      "description": "在 60 °C 下搅拌溶胶至形成透明凝胶",
      "parameters": {
        "temperature_C": 60,
        "target_state": "transparent gel",
        "stirring": "magnetic"
      },
      "duration_min": null,
      "evidence": {
        "source_text": "The resulting sol was stirred at 60 °C for a certain period to form a transparent gel.",
        "source_section": "2.2",
        "confidence": 0.40,
        "note": "搅拌时间缺失，原文仅写 'a certain period'"
      },
      "missing_parameter": {
        "field": "duration_min",
        "reason": "原文未给出具体搅拌时间",
        "risk_level": "high",
        "block_type": "blocked_missing_parameter"
      }
    },
    {
      "step_id": "STEP-04",
      "action": "dry",
      "description": "将凝胶转移至坩埚，在 80 °C 干燥 12 小时",
      "parameters": {
        "temperature_C": 80,
        "duration_h": 12,
        "vessel": "porcelain crucible",
        "equipment": "drying oven"
      },
      "evidence": {
        "source_text": "The gel was then transferred to a porcelain crucible and dried in an oven at 80 °C for 12 h.",
        "source_section": "2.2",
        "confidence": 0.96
      }
    },
    {
      "step_id": "STEP-05",
      "action": "calcine",
      "description": "在马弗炉中 300 °C 煅烧 2 小时，升温速率 2 °C/min，空气气氛",
      "parameters": {
        "temperature_C": 300,
        "duration_h": 2,
        "heating_rate_C_per_min": 2,
        "atmosphere": "air",
        "equipment": "muffle furnace (Nabertherm L9/13)",
        "equipment_max_temperature_C": 250
      },
      "evidence": {
        "source_text": "the dried gel was calcined in a muffle furnace at 300 °C for 2 h with a heating rate of 2 °C/min under air atmosphere. The furnace used in this study (Nabertherm L9/13) has a maximum operating temperature of 250 °C.",
        "source_section": "2.2",
        "confidence": 0.90
      },
      "safety_warnings": [
        {
          "type": "equipment_limit_exceeded",
          "severity": "critical",
          "message": "工艺要求 300 °C，但马弗炉最高温度仅 250 °C，超出设备安全限 50 °C",
          "required_action": "更换更高规格马弗炉或降低煅烧温度（需重新验证工艺）"
        },
        {
          "type": "require_confirmation",
          "severity": "high",
          "message": "密闭坩埚加热需操作员确认密封状态",
          "required_action": "加热前确认坩埚盖已正确密封"
        }
      ]
    }
  ],
  "sample_aliases": {
    "Sample-1": {
      "description": "TEOS:H2O 摩尔比 1:2 的样品",
      "teos_h2o_ratio": "1:2",
      "bet_surface_area": {
        "value": 320,
        "unit": "m2/g",
        "original_value": 320,
        "original_unit": "mg/g",
        "normalization_note": "原文单位 mg/g 为笔误，BET 比表面积标准单位为 m²/g，已自动归一化"
      }
    },
    "S1": {
      "description": "TEOS:H2O 摩尔比 1:4 的样品",
      "teos_h2o_ratio": "1:4"
    },
    "optimized sample": {
      "description": "HCl 催化剂用量调整为 0.3 mL 的优化样品",
      "hcl_volume_mL": 0.3,
      "bet_surface_area": {
        "value": 450,
        "unit": "m2/g",
        "original_value": 450,
        "original_unit": "mg/g",
        "normalization_note": "原文单位 mg/g 为笔误，BET 比表面积标准单位为 m²/g，已自动归一化"
      }
    }
  },
  "confidence": {
    "overall": 0.72,
    "breakdown": {
      "reagent_extraction": 0.95,
      "parameter_extraction": 0.65,
      "equipment_matching": 0.85,
      "safety_assessment": 0.90
    }
  },
  "missing_fields": [
    {
      "step_id": "STEP-03",
      "field": "duration_min",
      "description": "溶胶搅拌凝胶化时间",
      "reason": "原文仅写 'a certain period'，未给出具体数值",
      "risk_level": "high",
      "block_type": "blocked_missing_parameter",
      "suggested_default": null,
      "user_prompt": "请提供溶胶在 60 °C 下的搅拌凝胶化时间（单位：分钟或小时）"
    }
  ],
  "blocked": true,
  "blocked_reason": "blocked_missing_parameter",
  "blocked_details": "步骤 STEP-03 缺失搅拌时间参数，无法生成完整可执行协议",
  "unit_normalizations": [
    {
      "field": "sample_aliases.Sample-1.bet_surface_area",
      "original_value": 320,
      "original_unit": "mg/g",
      "normalized_value": 320,
      "normalized_unit": "m2/g",
      "reason": "BET 比表面积标准单位为 m²/g，原文 mg/g 系笔误"
    },
    {
      "field": "sample_aliases.optimized sample.bet_surface_area",
      "original_value": 450,
      "original_unit": "mg/g",
      "normalized_value": 450,
      "normalized_unit": "m2/g",
      "reason": "BET 比表面积标准单位为 m²/g，原文 mg/g 系笔误"
    }
  ],
  "safety_flags": [
    {
      "step_id": "STEP-05",
      "flag": "equipment_limit_exceeded",
      "severity": "critical",
      "details": "煅烧温度 300 °C 超过马弗炉最高温度 250 °C"
    },
    {
      "step_id": "STEP-05",
      "flag": "require_confirmation",
      "severity": "high",
      "details": "密闭坩埚加热前需确认密封状态"
    }
  ],
  "metadata": {
    "compiler_version": "1.0.0",
    "generated_at": "2024-01-15T10:30:00Z",
    "language": "zh-CN"
  }
}
```

---

## 3. 预期输出 — SOP.md

```markdown
# 标准操作规程 (SOP)

## SiO2 纳米颗粒 — 溶胶-凝胶法合成

| 项目 | 内容 |
|------|------|
| 协议编号 | SOL-GEL-SIO2-001 |
| 材料名称 | SiO2 纳米颗粒 |
| 材料类别 | 无机非金属 |
| 目标形貌 | 纳米颗粒（非晶态） |
| 目标比表面积 | 450 m²/g |

---

## 一、配方表

| 序号 | 试剂名称 | 化学式 | 纯度 | 用量 | 摩尔量 | 角色 |
|------|----------|--------|------|------|--------|------|
| 1 | 正硅酸乙酯 (TEOS) | Si(OC2H5)4 | 98% | 4.16 g | 0.0199 mol | 前驱体 |
| 2 | 乙醇 (EtOH) | C2H5OH | 99.8% | 20 mL (15.81 g) | — | 溶剂 |
| 3 | 去离子水 | H2O | 实验级 | 3.6 g | 0.200 mol | 水解剂 |
| 4 | 盐酸 (HCl) | HCl | 0.1 M | 0.5 mL | — | 催化剂 |

> TEOS:H2O 摩尔比 = 1:10（优化样品）

---

## 二、设备清单

| 序号 | 设备名称 | 规格 | 备注 |
|------|----------|------|------|
| 1 | 圆底烧瓶 | 250 mL，玻璃 | — |
| 2 | 磁力搅拌器 | 加热型，最高 250 °C | — |
| 3 | 瓷坩埚 | 30 mL，耐温 1200 °C | — |
| 4 | 干燥箱 | 最高 300 °C | — |
| 5 | 马弗炉 (Nabertherm L9/13) | 最高 250 °C | **警告：设备最高温度 250 °C，低于工艺要求 300 °C** |

---

## 三、操作步骤

### 步骤 1 (STEP-01)：溶解
- **操作**：将 4.16 g TEOS 溶解于 20 mL 乙醇中
- **容器**：250 mL 圆底烧瓶
- **温度**：室温 (25 °C)
- **搅拌**：磁力搅拌
- **置信度**：95%

### 步骤 2 (STEP-02)：逐滴加入水解液
- **操作**：将 3.6 g 去离子水与 0.5 mL HCl (0.1 M) 混合，逐滴加入 TEOS 溶液
- **滴加时间**：10 分钟
- **置信度**：93%

### 步骤 3 (STEP-03)：搅拌凝胶化
- **操作**：在 60 °C 下搅拌溶胶至形成透明凝胶
- **温度**：60 °C
- **搅拌时间**：**[缺失参数 — 需用户补充]**
- **置信度**：40%（参数缺失导致置信度降低）

> **注意**：本步骤缺失搅拌时间参数。原文仅写 "a certain period"，
> 无法确定凝胶化所需时间。请补充具体时间值后重新生成协议。

### 步骤 4 (STEP-04)：干燥
- **操作**：将凝胶转移至瓷坩埚，在 80 °C 干燥 12 小时
- **设备**：干燥箱
- **置信度**：96%

### 步骤 5 (STEP-05)：煅烧
- **操作**：在马弗炉中 300 °C 煅烧 2 小时
- **升温速率**：2 °C/min
- **气氛**：空气
- **置信度**：90%

> **安全警告 1 (critical)**：工艺要求 300 °C，但马弗炉 (Nabertherm L9/13)
> 最高温度仅 250 °C，超出设备安全限 50 °C。
> **必须更换更高规格马弗炉或降低煅烧温度（需重新验证工艺）。**

> **安全警告 2 (high)**：密闭坩埚加热前，操作员必须确认坩埚盖已正确密封。

---

## 四、样品命名对照表

| 文献命名 | 说明 | 关键参数 |
|----------|------|----------|
| Sample-1 | TEOS:H2O = 1:2 | BET: 320 m²/g |
| S1 | TEOS:H2O = 1:4 | — |
| optimized sample | HCl 用量 0.3 mL | BET: 450 m²/g |

> 注意：原文 BET 比表面积单位写为 mg/g，已自动归一化为标准单位 m²/g。

---

## 五、关键控制点

1. **水解速率**：逐滴加入控制水解速率，防止过快凝胶
2. **凝胶化时间**：需补充确认（缺失参数）
3. **干燥温度**：80 °C 确保去除溶剂和水分
4. **煅烧温度**：300 °C 去除有机残留（注意设备超限问题）
5. **坩埚密封**：加热前必须确认密封状态

---

## 六、注意事项

- TEOS 易水解，操作需在通风橱中进行
- HCl 具腐蚀性，需佩戴防护手套和护目镜
- 乙醇易燃，远离火源
- 马弗炉温度超限，需更换设备或调整工艺
- 密闭加热存在压力风险，确保密封后才能加热
```

---

## 4. 预期输出 — missing_conditions.md

```markdown
# 缺失条件报告

## 协议编号：SOL-GEL-SIO2-001
## 材料名称：SiO2 纳米颗粒
## 阻塞状态：已阻塞 (blocked_missing_parameter)

---

## 缺失参数列表

### 1. 溶胶搅拌凝胶化时间

| 项目 | 内容 |
|------|------|
| 步骤编号 | STEP-03 |
| 缺失字段 | duration_min |
| 严重程度 | 高 (high) |
| 阻塞类型 | blocked_missing_parameter |
| 原文描述 | "stirred at 60 °C for a certain period" |
| 缺失原因 | 原文仅写 "a certain period"，未给出具体数值 |
| 影响评估 | 凝胶化时间是决定纳米颗粒粒径和形貌的关键参数，缺失将导致实验不可重复 |
| 建议默认值 | 无（不可猜测） |
| 用户提示 | 请提供溶胶在 60 °C 下的搅拌凝胶化时间（单位：分钟或小时） |

---

## 需用户确认的问题

### Q1：溶胶搅拌凝胶化时间
原文描述为 "a certain period"，未给出具体数值。请提供：
- 搅拌温度：60 °C（已知）
- 搅拌时间：____ 分钟/小时（需补充）
- 终点判断标准：是否以形成透明凝胶为终点？

---

## 样品命名歧义解析

文献中使用了三种不同的样品命名方式，已解析对应关系如下：

| 文献命名 | 对应关系 | 关键参数差异 |
|----------|----------|--------------|
| Sample-1 | TEOS:H2O = 1:2 的样品 | H2O 用量较少 |
| S1 | TEOS:H2O = 1:4 的样品 | H2O 用量较多 |
| optimized sample | HCl 用量调整为 0.3 mL 的样品 | 催化剂用量不同 |

> 注意：Sample-1 与 S1 命名相似但参数不同，容易混淆。optimized sample
> 的命名未遵循统一编号规则，已建立 alias 映射表。

---

## 单位不一致记录

| 字段 | 原始值 | 原始单位 | 归一化值 | 归一化单位 | 原因 |
|------|--------|----------|----------|------------|------|
| Sample-1 BET 比表面积 | 320 | mg/g | 320 | m²/g | BET 标准单位为 m²/g，mg/g 系笔误 |
| optimized sample BET 比表面积 | 450 | mg/g | 450 | m²/g | BET 标准单位为 m²/g，mg/g 系笔误 |

> 以上单位不一致已自动归一化，无需用户干预。
```

---

## 5. 预期输出 — safety_report.md

```markdown
# 安全报告

## 协议编号：SOL-GEL-SIO2-001
## 材料名称：SiO2 纳米颗粒
## 安全评估状态：需关注

---

## 安全警告列表

### 警告 1：设备超限 (critical)

| 项目 | 内容 |
|------|------|
| 类型 | equipment_limit_exceeded |
| 严重程度 | critical（严重） |
| 涉及步骤 | STEP-05（煅烧） |
| 描述 | 工艺要求煅烧温度 300 °C，但马弗炉 (Nabertherm L9/13) 最高温度仅 250 °C |
| 超出量 | 50 °C |
| 风险 | 设备超温运行可能导致加热元件损坏、温度失控、甚至火灾 |
| 必须采取的行动 | 更换最高温度 ≥ 300 °C 的马弗炉，或降低煅烧温度至 250 °C 以下（需重新验证工艺） |
| 是否阻塞协议 | 否（生成警告，不阻塞，但强烈建议处理后再执行） |

### 警告 2：安全确认点 (high)

| 项目 | 内容 |
|------|------|
| 类型 | require_confirmation |
| 严重程度 | high（高） |
| 涉及步骤 | STEP-05（煅烧） |
| 描述 | 密闭坩埚加热需操作员确认密封状态 |
| 风险 | 坩埚未密封可能导致样品污染；过度密封在高温下可能因压力积聚导致坩埚破裂 |
| 必须采取的行动 | 加热前由操作员确认坩埚盖已正确密封，并记录确认签名 |
| 是否阻塞协议 | 否（生成确认要求，执行时需操作员签字确认） |

---

## 试剂安全信息

| 试剂 | 危险性 | 防护措施 |
|------|--------|----------|
| TEOS (正硅酸乙酯) | 易燃、刺激性 | 通风橱操作，远离火源，佩戴手套护目镜 |
| 乙醇 | 易燃 | 远离火源，通风良好 |
| HCl (盐酸) | 腐蚀性、刺激性 | 通风橱操作，佩戴耐酸手套和护目镜 |
| SiO2 纳米颗粒 (产物) | 吸入风险 | 避免粉尘飞扬，佩戴口罩 |

---

## 设备安全检查清单

- [ ] 马弗炉温度范围是否满足工艺要求（当前不满足，需更换设备）
- [ ] 坩埚密封状态确认
- [ ] 通风橱运行正常
- [ ] 灭火器可用
- [ ] 操作员已佩戴个人防护装备 (PPE)
```

---

## 6. 预期输出 — recovery_plan.yaml

```yaml
# 恢复计划 — 当协议被阻塞时的处理方案
# 协议编号: SOL-GEL-SIO2-001
# 阻塞原因: blocked_missing_parameter

protocol_id: "SOL-GEL-SIO2-001"
material: "SiO2 nanoparticles"
blocked: true
blocked_reason: "blocked_missing_parameter"

# 阻塞详情
block_details:
  step_id: "STEP-03"
  field: "duration_min"
  description: "溶胶搅拌凝胶化时间缺失"
  original_text: "stirred at 60 °C for a certain period"

# 恢复策略
recovery_strategies:
  # 策略1：向用户请求缺失参数
  - strategy_id: "RS-01"
    strategy_type: "request_user_input"
    description: "向用户请求溶胶搅拌凝胶化时间"
    priority: 1
    actions:
      - action: "prompt_user"
        prompt: "请提供溶胶在 60 °C 下的搅拌凝胶化时间（单位：分钟或小时）"
        expected_input_type: "float"
        expected_unit: "min"
    success_condition: "用户提供有效数值"
    on_success: "将数值填入 STEP-03.duration_min，解除阻塞，重新生成协议"

  # 策略2：从相关文献中推断
  - strategy_id: "RS-02"
    strategy_type: "literature_inference"
    description: "从同类溶胶-凝胶工艺文献中推断典型凝胶化时间"
    priority: 2
    actions:
      - action: "search_literature"
        query: "TEOS sol-gel gelation time 60C"
        expected_range: "120-360 min"
    success_condition: "找到可靠文献参考值"
    on_success: "提供参考值供用户确认，确认后填入协议"
    note: "不可自动填入，需用户确认"

  # 策略3：设计预实验确定
  - strategy_id: "RS-03"
    strategy_type: "pilot_experiment"
    description: "设计小规模预实验确定凝胶化时间"
    priority: 3
    actions:
      - action: "design_experiment"
        description: "在 60 °C 下搅拌溶胶，每隔 30 分钟观察凝胶状态"
        observation_points: [30, 60, 90, 120, 180, 240, 300, 360]
        endpoint: "形成透明凝胶"
    success_condition: "实验确定凝胶化时间"
    on_success: "将实验确定的时间填入协议"

# 已自动处理的问题（无需用户干预）
auto_resolved:
  - issue: "单位不一致"
    description: "BET 比表面积单位 mg/g 已自动归一化为 m²/g"
    status: "resolved"
  - issue: "样品命名歧义"
    description: "Sample-1 / S1 / optimized sample 对应关系已解析"
    status: "resolved"

# 需用户关注但不阻塞的问题
warnings:
  - warning_id: "W-01"
    type: "equipment_limit_exceeded"
    severity: "critical"
    description: "马弗炉最高温度 250 °C，低于工艺要求 300 °C"
    recommended_action: "更换设备或调整工艺参数"
  - warning_id: "W-02"
    type: "require_confirmation"
    severity: "high"
    description: "密闭坩埚加热需确认密封"
    recommended_action: "执行时由操作员确认并签名"

# 恢复后预期状态
expected_state_after_recovery:
  blocked: false
  confidence: 0.90
  missing_fields: []
  notes: "用户提供搅拌时间后，协议可完整执行"
```

---

## 示例总结

本示例展示了 matflow-compiler Skill 的以下核心能力：

1. **缺失参数检测**：识别 "a certain period" 为缺失搅拌时间，标记 `blocked_missing_parameter` 并阻塞协议
2. **单位归一化**：自动将 BET 比表面积的 `mg/g` 归一化为标准单位 `m²/g`，记录归一化过程
3. **样品命名解析**：解析 `Sample-1`、`S1`、`optimized sample` 三种命名的对应关系，建立 alias 映射表
4. **设备超限检测**：检测到马弗炉最高温度 250 °C 低于工艺要求 300 °C，生成 critical 级安全警告
5. **安全确认点**：识别密闭坩埚加热需操作员确认，生成 `require_confirmation` 标记
6. **恢复计划生成**：为阻塞协议生成多策略恢复计划（用户输入、文献推断、预实验）
