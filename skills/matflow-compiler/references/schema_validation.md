# Schema 验证与常见问题修复

## 验证工具

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

## 常见 Schema 问题与修复方法

### 问题 1：非标准 action 类型

**错误示例**：
```json
{
  "step_id": "S01",
  "action": "photoirradiate",
  "status": "ok"
}
```

**修复方法**：
```json
{
  "step_id": "S01",
  "action": "heat",
  "status": "ready"
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

### 问题 2：evidence 字段缺失

**错误示例**：
```json
{
  "evidence": [
    {
      "patent": "DOC-CN01",
      "section": "实施例1",
      "quote": "..."
    }
  ]
}
```

**修复方法**：
```json
{
  "evidence": [
    {
      "document": "DOC-CN01",
      "page": 1,
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

### 问题 3：inferred 字段未标记 require_confirmation

**错误示例**：
```json
{
  "missing_fields": [
    {
      "field_name": "temperature.value",
      "suggestion": "60°C",
      "requires_confirmation": false
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
      "requires_confirmation": true
    }
  ]
}
```

**规则**：所有包含 `suggestion` 的 `missing_fields` 必须标记 `requires_confirmation: true`，防止静默补全。

### 问题 4：safety_check 的 target_step 引用错误

**错误示例**：
```json
{
  "safety_checks": [
    {
      "check_id": "SAFE-001",
      "target_step": "S02/BBr3 mention"
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
      "target_step": "S02"
    }
  ]
}
```

**规则**：`target_step` 必须是存在的步骤 ID（如 S01、S02），不能包含 `/`、`-` 等特殊字符。

## 自动修复脚本

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

## 验证最佳实践

1. **生成后立即验证**：每次生成 protocol.json 后立即运行验证脚本
2. **修复所有 FAIL**：确保没有 FAIL 级别的错误
3. **审查 WARN**：WARNING 级别的提示也应尽量修复
4. **批量验证**：使用脚本批量验证所有案例
5. **持续集成**：将验证脚本集成到 CI/CD 流程中

## 常见验证结果解读

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
