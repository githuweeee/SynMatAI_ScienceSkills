# 反例与边界案例文档

> 本文档记录 matflow-compiler Skill 在处理材料合成协议时可能遇到的边界案例与反例。
> 每个案例均展示正确处理方式与错误处理方式的对比，以指导 Skill 的行为规范。

---

## 目录

1. [缺失关键参数案例](#案例1-缺失关键参数反应时间未指定)
2. [单位不一致案例](#案例2-单位不一致论文用mg设备用g)
3. [样品命名歧义案例](#案例3-样品命名歧义sample-1s1optimized-sample)
4. [设备超限案例](#案例4-设备超限需要300c但设备最高250c)
5. [安全风险案例](#案例5-安全风险密闭加热易燃溶剂)
6. [文档无法解析案例](#案例6-文档无法解析扫描版pdf无文字)
7. [部分信息缺失降级案例](#案例7-部分信息缺失有温度无时间)

---

## 核心原则

在阅读以下案例之前，请始终牢记 matflow-compiler 的三条不可违背的原则：

1. **绝不静默补全**：任何未在源文档中明确给出的参数，必须标记为缺失或需要确认，绝不允许 Skill 自行猜测或使用"默认值"填充。
2. **证据绑定**：每个提取的参数值必须绑定到源文档的具体位置（文档名、页码、章节、原文片段），确保可追溯。
3. **三种信息区分**：明确区分 `extracted`（直接提取）、`derived`（计算推导）、`inferred`（合理推断）三种信息来源，并为推断型信息标注置信度。

---

### 案例1: 缺失关键参数——反应时间未指定

**输入**:
```
将前驱体溶液转移至反应釜中，升温至180°C进行反应。反应结束后，自然冷却至室温，收集产物。
```

**预期行为**: Skill 应识别出反应时间（duration）这一关键参数在源文本中完全缺失。Skill 不得使用任何默认值（如"24小时"）进行补全，必须将协议状态标记为 `blocked_missing_parameter`，并在 `missing_fields` 中列出缺失的字段名。

**正确处理**:
```json
{
  "status": "blocked_missing_parameter",
  "step": "solvothermal_reaction",
  "missing_fields": [
    {
      "field": "duration",
      "description": "反应持续时间未在源文档中指定",
      "evidence": null,
      "suggestion": "请补充反应时间，例如：'180°C反应24小时'"
    }
  ],
  "extracted_parameters": {
    "temperature": {
      "value": 180,
      "unit": "°C",
      "evidence": {
        "document": "input_text",
        "page": null,
        "section": "实验步骤",
        "evidence_type": "extracted",
        "confidence": 1.0,
        "raw_text": "升温至180°C进行反应"
      }
    }
  }
}
```

**错误处理**:
```json
{
  "status": "complete",
  "step": "solvothermal_reaction",
  "parameters": {
    "temperature": 180,
    "unit": "°C",
    "duration": "24h"
  }
}
```
> 上述输出是**严重错误**的：Skill 自行补全了 `duration: "24h"`，但源文档中从未提及反应时间。这属于"静默补全"违规行为，可能导致实验人员执行错误的反应时长，造成实验失败或安全事故。

**教训**: 缺失的参数必须被显式标记，绝不允许使用"常见默认值"进行隐式补全。宁可阻塞执行流程，也不可输出可能错误的完整协议。

---

### 案例2: 单位不一致——论文用mg，设备用g

**输入**:
```
称取前驱体FeCl3·6H2O 540 mg，溶解于30 mL去离子水中。另称取NaOH 2.0 g，
配成10 mL水溶液。将两溶液混合后，转入反应釜中，200°C反应10小时。
```

**设备配置**:
```yaml
equipment:
  balance:
    unit: g
    precision: 0.001
```

**预期行为**: Skill 应识别出源文档中前驱体质量使用 mg 单位，而实验室天平配置为 g 单位。Skill 应自动将 540 mg 归一化为 0.540 g，并在 evidence 中记录原始值与转换过程。此过程属于 `derived` 类型信息。

**正确处理**:
```json
{
  "step": "precursor_preparation",
  "parameters": {
    "FeCl3_6H2O": {
      "value": 0.540,
      "unit": "g",
      "evidence": {
        "document": "input_text",
        "page": null,
        "section": "实验步骤",
        "evidence_type": "derived",
        "confidence": 1.0,
        "raw_text": "称取前驱体FeCl3·6H2O 540 mg",
        "derivation": {
          "original_value": 540,
          "original_unit": "mg",
          "conversion_factor": 0.001,
          "converted_value": 0.540,
          "target_unit": "g",
          "reason": "实验室天平配置单位为g，自动归一化"
        }
      }
    },
    "NaOH": {
      "value": 2.0,
      "unit": "g",
      "evidence": {
        "document": "input_text",
        "page": null,
        "section": "实验步骤",
        "evidence_type": "extracted",
        "confidence": 1.0,
        "raw_text": "另称取NaOH 2.0 g"
      }
    }
  }
}
```

**错误处理**:
```json
{
  "step": "precursor_preparation",
  "parameters": {
    "FeCl3_6H2O": {
      "value": 540,
      "unit": "g"
    }
  }
}
```
> 上述输出是**错误**的：直接将 540 mg 当作 540 g 使用，未进行单位转换。这将导致实验人员称取过量 1000 倍的前驱体，造成严重实验事故。

**教训**: 单位不一致时，Skill 必须执行显式归一化转换，并在 evidence 中记录原始值、转换因子和目标单位。转换过程属于 `derived` 类型，必须可追溯。

---

### 案例3: 样品命名歧义——Sample-1/S1/optimized sample

**输入**:
```
实验1中制备的样品记为Sample-1。后续优化实验中，对Sample-1的配方进行了调整，
将反应温度提高至200°C，所得优化样品(optimized sample)的性能更优。
在表征部分，S1的XRD图谱显示特征峰位于2θ=25.3°。
```

**预期行为**: Skill 应识别出 "Sample-1"、"S1" 和 "optimized sample" 可能指代同一样品或不同样品。当文本中存在命名歧义时，Skill 应建立别名映射表，并在 evidence 中标注对应关系的推断依据。对于无法确定的对应关系，应标记为 `require_confirmation`。

**正确处理**:
```json
{
  "sample_registry": {
    "samples": [
      {
        "primary_name": "Sample-1",
        "aliases": ["S1"],
        "description": "实验1中制备的初始样品",
        "evidence": {
          "document": "input_text",
          "page": null,
          "section": "实验描述",
          "evidence_type": "extracted",
          "confidence": 0.95,
          "raw_text": "实验1中制备的样品记为Sample-1"
        },
        "alias_evidence": [
          {
            "alias": "S1",
            "evidence_type": "inferred",
            "confidence": 0.85,
            "raw_text": "在表征部分，S1的XRD图谱显示特征峰位于2θ=25.3°",
            "reasoning": "S1与Sample-1编号一致，且上下文未引入新样品，推断为同一样品的简称"
          }
        ]
      },
      {
        "primary_name": "optimized sample",
        "aliases": [],
        "description": "对Sample-1配方调整后的优化样品",
        "evidence": {
          "document": "input_text",
          "page": null,
          "section": "实验描述",
          "evidence_type": "extracted",
          "confidence": 0.90,
          "raw_text": "所得优化样品(optimized sample)的性能更优"
        },
        "relationship_to_other_samples": {
          "type": "derived_from",
          "target": "Sample-1",
          "modification": "反应温度提高至200°C",
          "evidence_type": "extracted",
          "confidence": 0.95,
          "raw_text": "对Sample-1的配方进行了调整，将反应温度提高至200°C"
        }
      }
    ],
    "ambiguous_mappings": [
      {
        "names": ["S1", "optimized sample"],
        "question": "S1是否指代optimized sample？还是仅指代Sample-1？",
        "status": "require_confirmation",
        "reason": "文本中S1出现在表征部分，无法确定其指代初始样品还是优化样品"
      }
    ]
  }
}
```

**错误处理**:
```json
{
  "samples": ["Sample-1", "S1", "optimized sample"]
}
```
> 上述输出是**错误**的：将三个名称视为三个独立样品，未进行任何别名解析或歧义标注。这会导致后续实验人员无法确定各表征数据对应哪个样品。

**教训**: 样品命名歧义必须显式处理。Skill 应建立别名映射表，对高置信度的对应关系自动解析，对低置信度的歧义标记 `require_confirmation`，绝不可将不同别名默认视为不同样品或默认视为同一样品。

---

### 案例4: 设备超限——需要300°C但设备最高250°C

**输入**:
```
将混合溶液转入聚四氟乙烯内衬反应釜中，密封后放入马弗炉，升温至300°C反应24小时。
```

**设备配置**:
```yaml
equipment:
  muffle_furnace:
    max_temperature: 250
    unit: "°C"
    safety_margin: 10
```

**预期行为**: Skill 应识别出反应所需温度（300°C）超过了马弗炉的最高工作温度（250°C），即使考虑安全裕量（250 - 10 = 240°C有效上限），300°C仍远超设备能力。Skill 必须生成安全警告，并将协议状态标记为 `blocked`，阻止执行。

**正确处理**:
```json
{
  "status": "blocked_equipment_overlimit",
  "step": "solvothermal_reaction",
  "safety_warnings": [
    {
      "type": "equipment_overlimit",
      "severity": "critical",
      "message": "反应温度300°C超过马弗炉最高工作温度250°C（有效安全上限240°C）",
      "required_temperature": {
        "value": 300,
        "unit": "°C"
      },
      "equipment_limit": {
        "value": 250,
        "unit": "°C",
        "effective_limit": 240,
        "safety_margin": 10
      },
      "evidence": {
        "document": "input_text",
        "page": null,
        "section": "实验步骤",
        "evidence_type": "extracted",
        "confidence": 1.0,
        "raw_text": "升温至300°C反应24小时"
      },
      "action": "blocked",
      "suggestion": "请更换更高温设备（如高温马弗炉，最高温度≥350°C），或降低反应温度至设备安全范围内"
    }
  ],
  "extracted_parameters": {
    "temperature": {
      "value": 300,
      "unit": "°C",
      "evidence": {
        "document": "input_text",
        "page": null,
        "section": "实验步骤",
        "evidence_type": "extracted",
        "confidence": 1.0,
        "raw_text": "升温至300°C反应24小时"
      }
    },
    "duration": {
      "value": 24,
      "unit": "h",
      "evidence": {
        "document": "input_text",
        "page": null,
        "section": "实验步骤",
        "evidence_type": "extracted",
        "confidence": 1.0,
        "raw_text": "反应24小时"
      }
    }
  }
}
```

**错误处理**:
```json
{
  "status": "complete",
  "step": "solvothermal_reaction",
  "parameters": {
    "temperature": 300,
    "unit": "°C",
    "duration": "24h"
  }
}
```
> 上述输出是**严重错误**的：Skill 忽略了设备超限问题，直接输出了完整协议。实验人员若按此执行，可能导致设备损坏、反应釜爆炸等严重安全事故。

**教训**: 设备能力校验是安全防线。任何参数超出设备规格时，Skill 必须生成安全警告并阻塞执行，绝不允许"忽略"设备限制直接输出协议。

---

### 案例5: 安全风险——密闭加热+易燃溶剂

**输入**:
```
将前驱体溶液（含乙醇溶剂）转入密封反应釜中，升温至150°C反应6小时。
```

**预期行为**: Skill 应识别出两个安全风险因素的叠加：(1) 使用乙醇（易燃溶剂，闪点13°C）；(2) 在密封容器中加热至150°C（远超溶剂闪点）。这种组合存在爆炸风险。Skill 必须将协议状态标记为 `blocked`，并要求用户确认安全措施（如使用耐压反应釜、安装泄压阀等）。

**正确处理**:
```json
{
  "status": "blocked_safety_risk",
  "step": "sealed_heating_reaction",
  "safety_warnings": [
    {
      "type": "flammable_solvent_sealed_heating",
      "severity": "critical",
      "message": "检测到易燃溶剂（乙醇，闪点13°C）在密封容器中加热至150°C，存在爆炸风险",
      "risk_factors": [
        {
          "factor": "易燃溶剂",
          "detail": "乙醇，闪点13°C，远低于反应温度150°C",
          "evidence": {
            "document": "input_text",
            "page": null,
            "section": "实验步骤",
            "evidence_type": "inferred",
            "confidence": 0.90,
            "raw_text": "含乙醇溶剂",
            "reasoning": "文本提及乙醇溶剂，乙醇闪点为13°C（知识库数据）"
          }
        },
        {
          "factor": "密闭加热",
          "detail": "密封反应釜中加热至150°C，超过溶剂沸点（78°C），将产生压力",
          "evidence": {
            "document": "input_text",
            "page": null,
            "section": "实验步骤",
            "evidence_type": "extracted",
            "confidence": 1.0,
            "raw_text": "转入密封反应釜中，升温至150°C反应6小时"
          }
        }
      ],
      "action": "blocked",
      "required_confirmations": [
        {
          "field": "pressure_rating",
          "question": "反应釜的耐压等级是否满足150°C下乙醇的饱和蒸汽压？",
          "options": ["确认满足", "不满足，需更换设备"]
        },
        {
          "field": "pressure_relief",
          "question": "是否安装了泄压装置（如安全阀或防爆膜）？",
          "options": ["已安装", "未安装"]
        },
        {
          "field": "ventilation",
          "question": "反应是否在通风橱内进行？",
          "options": ["是", "否"]
        }
      ],
      "suggestion": "建议使用耐压反应釜（额定压力≥10 MPa），安装泄压阀，并在通风橱内操作"
    }
  ]
}
```

**错误处理**:
```json
{
  "status": "complete",
  "step": "sealed_heating_reaction",
  "parameters": {
    "solvent": "ethanol",
    "temperature": 150,
    "unit": "°C",
    "duration": "6h",
    "vessel": "sealed_autoclave"
  }
}
```
> 上述输出是**严重错误**的：Skill 未检测到易燃溶剂+密闭加热的安全风险组合，直接输出了完整协议。这可能导致实验人员在未采取安全措施的情况下执行危险操作。

**教训**: 安全风险检测必须覆盖参数组合，而非仅检查单个参数。易燃溶剂+密闭加热、有毒气体+无通风、强氧化剂+还原剂等危险组合必须被识别并阻塞执行。

---

### 案例6: 文档无法解析——扫描版PDF无文字

**输入**:
```
[上传文件: paper_scan.pdf]
[文件类型: 扫描版PDF，无文字层，仅包含图像]
```

**预期行为**: Skill 应检测到上传的 PDF 文件为扫描版，无文字层（text layer），无法通过常规文本提取方式解析。Skill 应输出降级结果，明确标记文档无法解析，并建议用户进行 OCR 处理或提供可编辑版本。

**正确处理**:
```json
{
  "status": "degraded_unparseable_document",
  "document_info": {
    "filename": "paper_scan.pdf",
    "file_type": "application/pdf",
    "page_count": 12,
    "text_extractable": false,
    "parse_error": "PDF无文字层，检测为扫描版图像PDF，无法提取文本内容"
  },
  "extracted_parameters": {},
  "degradation_report": {
    "reason": "文档为扫描版PDF，不包含可提取的文字层",
    "attempted_methods": [
      "PDF文本层提取（失败：无文字层）",
      "PDF元数据提取（成功：获取页数信息）"
    ],
    "extractable_info": {
      "page_count": 12,
      "metadata": {
        "title": "Untitled",
        "author": "Unknown"
      }
    },
    "suggestions": [
      "请使用OCR工具（如Tesseract、ABBYY FineReader）将扫描版PDF转换为可搜索文本",
      "请提供论文的可编辑版本（如Word文档或带文字层的PDF）",
      "如已有OCR文本，请直接粘贴文本内容而非上传扫描版PDF"
    ]
  },
  "missing_fields": [
    {
      "field": "all_parameters",
      "description": "由于文档无法解析，所有实验参数均无法提取",
      "evidence": null
    }
  ]
}
```

**错误处理**:
```json
{
  "status": "complete",
  "parameters": {
    "temperature": "unknown",
    "duration": "unknown",
    "reagents": []
  }
}
```
> 上述输出是**错误**的：Skill 未报告解析失败，而是输出了所有参数为 "unknown" 的"完整"协议。这会让用户误以为 Skill 已成功处理文档，实际上未提取到任何有效信息。

**教训**: 文档解析失败时，Skill 必须显式报告失败状态，输出降级结果，并给出可操作的建议。绝不允许将解析失败静默处理为"参数未知"的完整协议。

---

### 案例7: 部分信息缺失——有温度无时间

**输入**:
```
将溶液转入反应釜中，升温至180°C进行水热反应。反应结束后，用去离子水和乙醇
交替洗涤3次，60°C真空干燥12小时。
```

**预期行为**: Skill 应成功提取温度（180°C）、洗涤步骤（3次）、干燥条件（60°C，12小时）等参数，但识别出反应时间（duration）缺失。Skill 应输出部分协议，将已提取的参数正常输出，同时将缺失字段标记在 `missing_fields` 中，协议状态标记为 `blocked_missing_parameter`。

**正确处理**:
```json
{
  "status": "blocked_missing_parameter",
  "protocol": {
    "steps": [
      {
        "step": 1,
        "name": "solvothermal_reaction",
        "parameters": {
          "temperature": {
            "value": 180,
            "unit": "°C",
            "evidence": {
              "document": "input_text",
              "page": null,
              "section": "实验步骤",
              "evidence_type": "extracted",
              "confidence": 1.0,
              "raw_text": "升温至180°C进行水热反应"
            }
          },
          "duration": null
        },
        "missing_fields": ["duration"]
      },
      {
        "step": 2,
        "name": "washing",
        "parameters": {
          "solvents": ["deionized_water", "ethanol"],
          "cycles": 3,
          "evidence": {
            "document": "input_text",
            "page": null,
            "section": "实验步骤",
            "evidence_type": "extracted",
            "confidence": 1.0,
            "raw_text": "用去离子水和乙醇交替洗涤3次"
          }
        }
      },
      {
        "step": 3,
        "name": "drying",
        "parameters": {
          "temperature": {
            "value": 60,
            "unit": "°C"
          },
          "duration": {
            "value": 12,
            "unit": "h"
          },
          "method": "vacuum",
          "evidence": {
            "document": "input_text",
            "page": null,
            "section": "实验步骤",
            "evidence_type": "extracted",
            "confidence": 1.0,
            "raw_text": "60°C真空干燥12小时"
          }
        }
      }
    ]
  },
  "missing_fields": [
    {
      "step": 1,
      "field": "duration",
      "description": "水热反应的持续时间未在源文档中指定",
      "evidence": null,
      "suggestion": "请补充反应时间，例如：'180°C反应24小时'"
    }
  ]
}
```

**错误处理**:
```json
{
  "status": "complete",
  "protocol": {
    "steps": [
      {
        "step": 1,
        "name": "solvothermal_reaction",
        "parameters": {
          "temperature": 180,
          "unit": "°C",
          "duration": "12h"
        }
      }
    ]
  }
}
```
> 上述输出是**错误**的：Skill 自行补全了 `duration: "12h"`（可能是将干燥时间误用为反应时间），并将状态标记为 `complete`。这属于"静默补全"违规行为，且将干燥时间误用为反应时间，可能导致实验人员执行错误的反应时长。

**教训**: 部分信息缺失时，Skill 应输出已提取的部分协议，同时明确标记缺失字段。绝不可将其他步骤的参数"借用"到缺失字段，也不可使用默认值补全。部分协议+明确缺失标记，优于错误的完整协议。

---

## 总结

| 案例编号 | 案例类型 | 核心原则 | 状态标记 |
|---------|---------|---------|---------|
| 1 | 缺失关键参数 | 绝不静默补全 | `blocked_missing_parameter` |
| 2 | 单位不一致 | 显式归一化+证据绑定 | `complete`（含derived证据） |
| 3 | 样品命名歧义 | 别名解析+歧义标注 | `require_confirmation` |
| 4 | 设备超限 | 设备能力校验 | `blocked_equipment_overlimit` |
| 5 | 安全风险 | 参数组合风险检测 | `blocked_safety_risk` |
| 6 | 文档无法解析 | 降级输出+建议 | `degraded_unparseable_document` |
| 7 | 部分信息缺失 | 部分协议+缺失标记 | `blocked_missing_parameter` |

> **核心准则**：matflow-compiler 宁可输出不完整的协议并明确标注缺失，也绝不输出看似完整但包含猜测值的协议。实验安全永远优先于协议完整性。
