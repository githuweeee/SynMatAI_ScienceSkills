#!/usr/bin/env python3
"""
MatFlow Compiler - 补充材料(SI)自动获取脚本

功能:
1. 从论文 PDF 中提取 DOI
2. 通过 Crossref API 验证 DOI
3. 通过 DOI 解析出版商页面并下载 SI
4. 若 DOI 不可用，按标题检索获取 SI
5. 解析 SI 文件内容

使用方式:
    python retrieve_si.py paper.pdf
    python retrieve_si.py paper.pdf --output si_download/
    python retrieve_si.py paper.pdf --title "论文标题" --output si_download/
"""

import re
import os
import sys
import json
import argparse
import urllib.request
import urllib.parse
import urllib.error
import tempfile
import zipfile

# 尝试导入 PyMuPDF
try:
    import fitz  # PyMuPDF
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False


def extract_doi_from_pdf(pdf_path):
    """从 PDF 中提取 DOI，优先级: 元数据 > 正文正则 > 脚注扫描"""
    if not HAS_FITZ:
        return None

    doc = fitz.open(pdf_path)

    # 1. 检查 PDF 元数据
    metadata = doc.metadata or {}
    for key in ["doi", "DOI", "url", "subject"]:
        value = metadata.get(key, "")
        if value:
            match = re.search(r'10\.\d{4,}/[^\s"<>]+', value)
            if match:
                doc.close()
                return match.group(0).rstrip('.,;)')

    # 2. 正文正则匹配（扫描前5页）
    doi_patterns = [
        r'10\.\d{4,}/[^\s"<>]+',
        r'https?://(?:dx\.)?doi\.org/(10\.\d{4,}/[^\s"<>]+)',
        r'[Dd][Oo][Ii]:\s*(10\.\d{4,}/[^\s"<>]+)',
    ]

    for page_num in range(min(5, doc.page_count)):
        page = doc[page_num]
        text = page.get_text()
        for pattern in doi_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # 取最后一个匹配（通常是版权行的 DOI）
                doi = matches[-1]
                if isinstance(doi, tuple):
                    doi = doi[-1]
                doc.close()
                return doi.rstrip('.,;)')

    doc.close()
    return None


def extract_title_from_pdf(pdf_path):
    """从 PDF 首页提取论文标题"""
    if not HAS_FITZ:
        return None

    doc = fitz.open(pdf_path)
    first_page = doc[0]
    text = first_page.get_text()
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    # 标题通常在前5行，选择最长的非空行
    title_candidates = lines[:5] if len(lines) >= 5 else lines
    title = max(title_candidates, key=len) if title_candidates else ""

    doc.close()
    return title


def validate_doi(doi):
    """通过 Crossref API 验证 DOI 有效性"""
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MatFlowCompiler/1.0"})
        response = urllib.request.urlopen(req, timeout=15)
        data = json.loads(response.read().decode('utf-8'))
        message = data.get("message", {})
        return {
            "valid": True,
            "doi": doi,
            "title": message.get("title", [""])[0] if message.get("title") else "",
            "publisher": message.get("publisher", ""),
            "type": message.get("type", ""),
            "url": message.get("URL", ""),
            "journal": message.get("container-title", [""])[0] if message.get("container-title") else "",
        }
    except Exception as e:
        return {"valid": False, "doi": doi, "error": str(e)}


def search_by_title(title):
    """通过 Crossref API 按标题搜索论文"""
    encoded_title = urllib.parse.quote(title)
    url = f"https://api.crossref.org/works?query.title={encoded_title}&rows=5"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MatFlowCompiler/1.0"})
        response = urllib.request.urlopen(req, timeout=15)
        data = json.loads(response.read().decode('utf-8'))
        items = data.get("message", {}).get("items", [])
        results = []
        for item in items:
            item_title = item.get("title", [""])[0] if item.get("title") else ""
            results.append({
                "doi": item.get("DOI", ""),
                "title": item_title,
                "publisher": item.get("publisher", ""),
                "url": item.get("URL", ""),
                "type": item.get("type", ""),
            })
        return results
    except Exception as e:
        return []


def get_publisher_from_doi(doi):
    """根据 DOI 前缀判断出版商"""
    if doi.startswith("10.1021"):
        return "acs"
    elif doi.startswith("10.1039"):
        return "rsc"
    elif doi.startswith("10.1002"):
        return "wiley"
    elif doi.startswith("10.1016"):
        return "elsevier"
    elif doi.startswith("10.1007"):
        return "springer"
    elif doi.startswith("10.1038"):
        return "nature"
    else:
        return "unknown"


def build_publisher_url(doi, publisher):
    """构建出版商文章页面 URL"""
    encoded_doi = urllib.parse.quote(doi)
    if publisher == "acs":
        return f"https://pubs.acs.org/doi/{encoded_doi}"
    elif publisher == "rsc":
        return f"https://pubs.rsc.org/en/content/articlelanding/{encoded_doi}"
    elif publisher == "wiley":
        return f"https://onlinelibrary.wiley.com/doi/{encoded_doi}"
    elif publisher == "springer":
        return f"https://link.springer.com/article/{encoded_doi}"
    elif publisher == "nature":
        # Nature DOI 格式: 10.1038/xxx
        article_id = doi.split("10.1038/")[-1] if "10.1038/" in doi else doi
        return f"https://www.nature.com/articles/{article_id}"
    else:
        return f"https://doi.org/{encoded_doi}"


def fetch_si_links(publisher_url, publisher):
    """从出版商页面提取 SI 下载链接"""
    try:
        req = urllib.request.Request(publisher_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        response = urllib.request.urlopen(req, timeout=20)
        html = response.read().decode('utf-8', errors='ignore')

        # 根据出版商搜索 SI 链接
        si_keywords = {
            "acs": ["Supporting Info", "supplementary", "si_pdf"],
            "rsc": ["ESI", "Electronic Supplementary", "supplementary"],
            "wiley": ["Supporting Information", "supplementary", "suppl"],
            "elsevier": ["supplementary data", "Supplementary", "mmc"],
            "springer": ["Supplementary Material", "Electronic Supplementary", "ESM"],
            "nature": ["Supplementary Information", "supplementary", "supp"],
        }

        keywords = si_keywords.get(publisher, ["supplementary", "Supporting"])
        si_links = []

        for kw in keywords:
            # 查找包含关键词的链接
            pattern = rf'href="([^"]*{re.escape(kw)}[^"]*)"' 
            matches = re.findall(pattern, html, re.IGNORECASE)
            si_links.extend(matches)

        # 去重
        si_links = list(set(si_links))
        return si_links

    except Exception as e:
        print(f"  ⚠️ 获取出版商页面失败: {e}")
        return []


def download_file(url, output_dir, filename=None):
    """下载文件到指定目录"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not filename:
        filename = url.split("/")[-1].split("?")[0]
        if not filename:
            filename = "downloaded_file"

    filepath = os.path.join(output_dir, filename)

    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        response = urllib.request.urlopen(req, timeout=60)
        with open(filepath, 'wb') as f:
            f.write(response.read())
        print(f"  ✅ 下载完成: {filepath}")
        return filepath
    except Exception as e:
        print(f"  ❌ 下载失败: {e}")
        return None


def parse_si_file(filepath):
    """解析 SI 文件内容"""
    if filepath.endswith('.pdf'):
        if HAS_FITZ:
            doc = fitz.open(filepath)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        else:
            return "[PyMuPDF 未安装，无法解析 PDF]"

    elif filepath.endswith('.zip'):
        texts = []
        with zipfile.ZipFile(filepath, 'r') as zf:
            for name in zf.namelist():
                if name.endswith('.pdf') and HAS_FITZ:
                    with zf.open(name) as f:
                        tmp = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
                        tmp.write(f.read())
                        tmp.close()
                        doc = fitz.open(tmp.name)
                        for page in doc:
                            texts.append(page.get_text())
                        doc.close()
                        os.unlink(tmp.name)
                elif name.endswith('.txt') or name.endswith('.cif'):
                    with zf.open(name) as f:
                        texts.append(f.read().decode('utf-8', errors='ignore'))
        return "\n".join(texts)

    elif filepath.endswith('.txt') or filepath.endswith('.cif') or filepath.endswith('.html'):
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    else:
        return f"[未知文件格式: {filepath}]"


def retrieve_si(pdf_path, output_dir="downloaded_si", title=None):
    """
    主函数: 从论文 PDF 获取补充材料

    参数:
        pdf_path: 论文 PDF 路径
        output_dir: SI 下载目录
        title: 可选的论文标题（用于回退检索）

    返回:
        dict: SI 获取结果
    """
    result = {
        "input_pdf": pdf_path,
        "doi": None,
        "doi_valid": False,
        "publisher": None,
        "si_links": [],
        "downloaded_files": [],
        "si_text": None,
        "status": "not_started",
        "retrieval_method": None,
        "error": None,
    }

    print(f"\n{'='*60}")
    print(f"  MatFlow SI Retriever")
    print(f"{'='*60}")
    print(f"  输入: {pdf_path}")

    # 步骤1: 提取 DOI
    print(f"\n[1/5] 提取 DOI...")
    doi = extract_doi_from_pdf(pdf_path)
    if doi:
        print(f"  ✅ 找到 DOI: {doi}")
        result["doi"] = doi

        # 步骤2: 验证 DOI
        print(f"\n[2/5] 验证 DOI (Crossref)...")
        validation = validate_doi(doi)
        if validation["valid"]:
            print(f"  ✅ DOI 有效")
            print(f"     标题: {validation.get('title', 'N/A')}")
            print(f"     出版商: {validation.get('publisher', 'N/A')}")
            result["doi_valid"] = True
            result["publisher"] = get_publisher_from_doi(doi)
            result["retrieval_method"] = "doi"
        else:
            print(f"  ❌ DOI 验证失败: {validation.get('error', '未知错误')}")
            doi = None  # 切换到标题检索

    if not doi:
        # 回退: 按标题检索
        print(f"\n[2/5] DOI 不可用，切换到标题检索...")
        if not title:
            title = extract_title_from_pdf(pdf_path)
        if title:
            print(f"  提取标题: {title[:80]}...")
            search_results = search_by_title(title)
            if search_results:
                best_match = search_results[0]
                print(f"  ✅ 找到匹配: {best_match.get('title', 'N/A')[:80]}")
                doi = best_match.get("doi", "")
                result["doi"] = doi
                result["retrieval_method"] = "title_search"
                result["publisher"] = get_publisher_from_doi(doi) if doi else "unknown"
            else:
                print(f"  ❌ 标题检索无结果")
                result["status"] = "no_match_found"
                return result
        else:
            print(f"  ❌ 无法提取标题")
            result["status"] = "no_title"
            return result

    # 步骤3: 构建出版商 URL 并获取 SI 链接
    print(f"\n[3/5] 获取出版商页面 SI 链接...")
    publisher = result.get("publisher", "unknown")
    if publisher != "unknown" and doi:
        publisher_url = build_publisher_url(doi, publisher)
        print(f"  出版商: {publisher}")
        print(f"  页面: {publisher_url}")
        si_links = fetch_si_links(publisher_url, publisher)
        result["si_links"] = si_links
        if si_links:
            print(f"  ✅ 找到 {len(si_links)} 个 SI 链接")
        else:
            print(f"  ⚠️ 未找到 SI 链接（可能需要付费访问）")
            result["status"] = "si_not_accessible"
            result["error"] = "no_si_links_found"
            return result
    else:
        print(f"  ⚠️ 未知出版商，无法获取 SI")
        result["status"] = "unknown_publisher"
        return result

    # 步骤4: 下载 SI 文件
    print(f"\n[4/5] 下载 SI 文件...")
    downloaded = []
    for link in si_links[:3]:  # 最多下载3个文件
        # 补全相对 URL
        if link.startswith('/'):
            base_url = build_publisher_url(doi, publisher)
            link = urllib.parse.urljoin(base_url, link)
        elif not link.startswith('http'):
            continue

        filepath = download_file(link, output_dir)
        if filepath:
            downloaded.append(filepath)

    result["downloaded_files"] = downloaded
    if not downloaded:
        print(f"  ❌ 下载失败")
        result["status"] = "download_failed"
        return result

    # 步骤5: 解析 SI 内容
    print(f"\n[5/5] 解析 SI 内容...")
    si_texts = []
    for filepath in downloaded:
        text = parse_si_file(filepath)
        if text:
            si_texts.append(text)
            print(f"  ✅ 解析完成: {os.path.basename(filepath)} ({len(text)} 字符)")

    if si_texts:
        result["si_text"] = "\n\n".join(si_texts)
        result["status"] = "success"
        print(f"\n{'='*60}")
        print(f"  ✅ SI 获取成功！")
        print(f"  总文本: {len(result['si_text'])} 字符")
        print(f"  文件数: {len(downloaded)}")
        print(f"{'='*60}")
    else:
        result["status"] = "parse_failed"
        print(f"\n  ❌ SI 文件解析失败")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="MatFlow SI Retriever - 从论文 PDF 获取补充材料"
    )
    parser.add_argument("pdf_path", help="论文 PDF 文件路径")
    parser.add_argument("--output", "-o", default="downloaded_si",
                        help="SI 下载目录 (默认: downloaded_si)")
    parser.add_argument("--title", "-t", default=None,
                        help="论文标题 (用于回退检索)")
    parser.add_argument("--json", "-j", action="store_true",
                        help="输出 JSON 格式结果")

    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        print(f"❌ 文件不存在: {args.pdf_path}")
        sys.exit(1)

    result = retrieve_si(args.pdf_path, args.output, args.title)

    if args.json:
        # 输出 JSON（不包含 si_text 以避免过长）
        output = {k: v for k, v in result.items() if k != "si_text"}
        output["si_text_length"] = len(result["si_text"]) if result.get("si_text") else 0
        print(json.dumps(output, ensure_ascii=False, indent=2))

    # 返回码
    if result["status"] == "success":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
