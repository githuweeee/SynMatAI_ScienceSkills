# 补充材料（SI）获取策略与出版商适配详情

## 目录

1. DOI 提取方法详解
2. Crossref API 验证流程
3. 出版商 SI 页面适配
4. 标题检索回退策略
5. SI 文件解析
6. 失败场景与降级

---

## 1. DOI 提取方法详解

### 1.1 PDF 元数据提取

```python
import fitz  # PyMuPDF

def extract_doi_from_metadata(pdf_path):
    """从 PDF 元数据中提取 DOI"""
    doc = fitz.open(pdf_path)
    metadata = doc.metadata
    # 检查 metadata 中的 doi 字段
    for key in ["doi", "DOI", "dx.doi.org", "url"]:
        if key in metadata and metadata[key]:
            value = metadata[key]
            # 提取 DOI 字符串
            import re
            match = re.search(r'10\.\d{4,}/[^\s]+', value)
            if match:
                return match.group(0)
    doc.close()
    return None
```

### 1.2 正文正则匹配

```python
import re

def extract_doi_from_text(text):
    """从文本中提取 DOI"""
    patterns = [
        r'10\.\d{4,}/[^\s"<>]+',                    # 标准 DOI 格式
        r'https?://(?:dx\.)?doi\.org/(10\.\d{4,}/[^\s"<>]+)',  # DOI URL
        r'doi:\s*(10\.\d{4,}/[^\s"<>]+)',           # doi: 前缀
        r'DOI:\s*(10\.\d{4,}/[^\s"<>]+)',           # DOI: 前缀
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # 返回最后一个匹配（通常是版权行的 DOI）
            doi = matches[-1] if isinstance(matches[-1], str) else matches[-1][-1]
            return doi.strip('.,;)')
    return None
```

### 1.3 首脚注扫描

优先扫描以下位置：
- 首页前 50 行文本
- 包含 "doi" / "DOI" / "dx.doi.org" / "https://doi.org" 的行
- 版权行（通常包含 © 符号附近）

---

## 2. Crossref API 验证流程

```python
import requests

def validate_doi(doi):
    """通过 Crossref API 验证 DOI 有效性"""
    url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            message = data.get("message", {})
            return {
                "valid": True,
                "title": message.get("title", [""])[0],
                "publisher": message.get("publisher", ""),
                "type": message.get("type", ""),
                "url": message.get("URL", ""),
                "journal": message.get("container-title", [""])[0] if message.get("container-title") else "",
            }
    except Exception:
        pass
    return {"valid": False}
```

---

## 3. 出版商 SI 页面适配

### 3.1 ACS (American Chemical Society)

- DOI 前缀: `10.1021`
- 文章页面: `https://pubs.acs.org/doi/{doi}`
- SI 链接模式: 查找包含 "Supporting Info" 或 "supplementary" 的 `<a>` 标签
- SI 下载 URL: 通常为 `https://pubs.acs.org/doi/suppl/{doi}/suppl_file/...`

### 3.2 RSC (Royal Society of Chemistry)

- DOI 前缀: `10.1039`
- 文章页面: `https://pubs.rsc.org/en/content/articlelanding/{doi}`
- SI 链接模式: 查找 "ESI" 或 "Electronic Supplementary Information" 链接
- SI 下载 URL: `https://www.rsc.org/suppdata/...`

### 3.3 Wiley

- DOI 前缀: `10.1002`
- 文章页面: `https://onlinelibrary.wiley.com/doi/{doi}`
- SI 链接模式: 查找 "Supporting Information" 或 "Supporting Information" 链接
- SI 下载 URL: `https://onlinelibrary.wiley.com/doi/suppl/{doi}`

### 3.4 Elsevier

- DOI 前缀: `10.1016`
- 文章页面: `https://www.sciencedirect.com/science/article/pii/{pii}`
- SI 链接模式: 查找 "Download supplementary data" 链接
- PII 获取: 从 Crossref API 的 `message.alternative-id` 字段获取

### 3.5 Springer

- DOI 前缀: `10.1007`
- 文章页面: `https://link.springer.com/article/{doi}`
- SI 链接模式: 查找 "Supplementary Material" 或 "Electronic Supplementary Material" 链接

### 3.6 Nature

- DOI 前缀: `10.1038`
- 文章页面: `https://www.nature.com/articles/{id}`
- SI 链接模式: 查找 "Supplementary Information" 链接
- 文章 ID 从 DOI 中提取

---

## 4. 标题检索回退策略

当 DOI 提取失败时：

### 4.1 标题提取

```python
def extract_title_from_pdf(pdf_path):
    """从 PDF 首页提取论文标题"""
    doc = fitz.open(pdf_path)
    first_page = doc[0]
    text = first_page.get_text()
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    # 标题通常在前 3-5 行，排除期刊名和作者信息
    # 启发式规则：选择最长的非空行作为标题候选
    title_candidates = lines[:5]
    title = max(title_candidates, key=len) if title_candidates else ""
    doc.close()
    return title
```

### 4.2 搜索策略

1. **Crossref 标题搜索**: `https://api.crossref.org/works?query.title={title}&rows=5`
2. **Google Scholar**: `https://scholar.google.com/scholar?q={title}`
3. **Semantic Scholar**: `https://api.semanticscholar.org/graph/v1/paper/search?query={title}`

### 4.3 匹配验证

- 标题相似度 > 0.85（使用 Levenshtein 距离或 Jaccard 相似度）
- 期刊名称匹配
- 第一作者姓氏匹配

---

## 5. SI 文件解析

SI 文件可能是 PDF、CIF、ZIP 等格式：

| 格式 | 解析方法 |
|------|----------|
| PDF | 使用 PyMuPDF (fitz) 提取文本 |
| ZIP | 解压后逐个解析内部文件 |
| CIF | 使用文本解析提取晶体学参数 |
| HTML | 使用 BeautifulSoup 提取文本 |
| DOCX | 使用 python-docx 提取文本 |

---

## 6. 失败场景与降级

| 失败场景 | 原因 | 降级策略 |
|----------|------|----------|
| DOI 无法提取 | PDF 无元数据，正文无 DOI | 切换到标题检索 |
| DOI 无效 | DOI 不存在或已撤销 | 切换到标题检索 |
| 出版商页面不可达 | 网络限制或域名被封 | 记录失败，继续处理 |
| SI 需要付费访问 | 付费墙 | 记录 si_not_accessible |
| SI 不存在 | 论文无补充材料 | 记录 no_si_found |
| SI 文件无法解析 | 格式损坏或加密 | 记录 parse_error |

所有失败场景均不阻塞主流程，继续基于主文档生成协议。
