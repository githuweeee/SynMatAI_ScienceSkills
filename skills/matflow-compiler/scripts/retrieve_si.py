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


def detect_ocr_pdf(doc):
    """
    检测 PDF 是否为 OCR 扫描版
    
    通过元数据中的关键词和文本质量判断
    
    返回: (is_ocr, ocr_quality, details)
      is_ocr: bool
      ocr_quality: "good" | "moderate" | "poor"
      details: dict
    """
    details = {"reasons": []}
    
    # 1. 检查元数据中的 OCR 关键词
    metadata = doc.metadata or {}
    producer = (metadata.get("producer", "") or "").lower()
    creator = (metadata.get("creator", "") or "").lower()
    
    ocr_keywords = ["paper capture", "ocr", "tesseract", "abbyy", "omnipage", "cuneiform"]
    for kw in ocr_keywords:
        if kw in producer or kw in creator:
            details["reasons"].append(f"元数据包含OCR关键词: '{kw}'")
            is_ocr = True
            break
    else:
        is_ocr = False
    
    # 2. 检查文本质量（OCR 错误特征）
    total_text = ""
    for page in doc:
        total_text += page.get_text()
    
    if not total_text.strip():
        # 完全无文本 → 纯扫描版
        return True, "poor", {"reasons": ["PDF无文字层，纯扫描版"]}
    
    # 3. 检测 OCR 常见错误特征
    total_chars = len(total_text)
    error_indicators = 0
    
    # 检查乱码比例（非ASCII可打印字符的异常分布）
    import re
    # 检查常见的OCR错误模式
    ocr_error_patterns = [
        (r'[\x00-\x08\x0e-\x1f]', '控制字符'),  # 控制字符
        (r'fiir|uber|khylene|auibau|Nachwcis', '德语变音符号丢失'),  # 变音符号丢失
        (r'(?<![A-Z]){3,}', '异常大写连续'),  # 异常大写
    ]
    
    for pattern, desc in ocr_error_patterns:
        matches = re.findall(pattern, total_text)
        if matches:
            error_count = len(matches)
            if error_count > 3:
                details["reasons"].append(f"{desc}: {error_count}处")
                error_indicators += error_count
    
    # 4. 计算文本质量评分
    if total_chars > 0:
        error_ratio = error_indicators / (total_chars / 1000)  # 每千字符错误数
        if error_ratio > 5:
            ocr_quality = "poor"
            is_ocr = True
        elif error_ratio > 1:
            ocr_quality = "moderate"
            is_ocr = True
        else:
            ocr_quality = "good"
    else:
        ocr_quality = "poor"
    
    # 5. 检查页面中的图片比例（扫描版通常每页有大图）
    for i in range(min(3, doc.page_count)):
        page = doc[i]
        images = page.get_images()
        text_len = len(page.get_text().strip())
        if len(images) > 0 and text_len < 50:
            details["reasons"].append(f"第{i+1}页: 有图片但文本极少")
            is_ocr = True
            if ocr_quality == "good":
                ocr_quality = "moderate"
            break
    
    return is_ocr, ocr_quality, details


def fix_ocr_text(text):
    """
    尝试修复 OCR 文本中的常见错误
    
    主要处理:
    - 德语变音符号丢失 (uber→über, fiir→für)
    - 常见 OCR 字符替换错误
    - 多余的空格和换行
    """
    import re
    
    # 德语变音符号修复（常见OCR丢失模式）
    german_fixes = {
        'uber': 'über', 'Uber': 'Über',
        'fiir': 'für', 'Fiir': 'Für',
        'khylene': 'Äthylene', 'athylene': 'äthylene',
        'auibau': 'Aufbau', 'Auibau': 'Aufbau',
        'Nachwcis': 'Nachweis',
        'Bo': 'ße',  # 常见 ß 识别错误
        'oL3': 'daß',  # 常见 daß 识别错误
    }
    
    for wrong, correct in german_fixes.items():
        text = text.replace(wrong, correct)
    
    # 修复多余的空格（OCR常见问题）
    text = re.sub(r' {3,}', '  ', text)  # 多空格压缩
    text = re.sub(r'\n{3,}', '\n\n', text)  # 多换行压缩
    
    # 修复断词（OCR常在行尾断词）
    text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)
    
    return text


def try_mineru_ocr(pdf_path, output_dir=None):
    """
    尝试使用 MinerU 进行高质量 OCR 处理
    
    MinerU 是一个开源的高精度文档解析工具，支持:
    - OCR 文字识别（109种语言）
    - 数学公式识别 → LaTeX
    - 表格结构识别
    - 多栏排版处理
    
    安装: pip install mineru
    使用: mineru -p input.pdf -o output_dir -m ocr
    
    参数:
        pdf_path: PDF 文件路径
        output_dir: 输出目录（默认为临时目录）
    
    返回:
        str: 提取的文本（Markdown格式），如果 MinerU 不可用则返回 None
    """
    import subprocess
    import shutil
    
    # 检查 mineru 是否安装
    mineru_cmd = shutil.which("mineru")
    if not mineru_cmd:
        # 尝试 python -m mineru
        try:
            result = subprocess.run(
                [sys.executable, "-m", "mineru", "--version"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                return None
            mineru_cmd = f"{sys.executable} -m mineru"
        except Exception:
            return None
    
    # 创建临时输出目录
    if not output_dir:
        output_dir = tempfile.mkdtemp(prefix="mineru_output_")
    
    try:
        print(f"  📄 调用 MinerU 进行 OCR 处理...")
        print(f"     输入: {pdf_path}")
        print(f"     输出: {output_dir}")
        
        # 构建 mineru 命令
        # -p: 输入文件路径
        # -o: 输出目录
        # -m ocr: 强制 OCR 模式（适用于扫描版）
        cmd = [
            sys.executable, "-m", "mineru",
            "-p", pdf_path,
            "-o", output_dir,
            "-m", "ocr",  # OCR 模式
        ]
        
        # 运行 MinerU
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5分钟超时
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode != 0:
            print(f"  ⚠️ MinerU 执行失败 (退出码: {result.returncode})")
            if result.stderr:
                print(f"     错误: {result.stderr[:200]}")
            return None
        
        # 查找输出文件（MinerU 输出 Markdown 格式）
        # MinerU 通常输出到 output_dir/<filename>/auto/<filename>.md
        md_files = []
        for root, dirs, files in os.walk(output_dir):
            for f in files:
                if f.endswith('.md'):
                    md_files.append(os.path.join(root, f))
        
        if not md_files:
            print(f"  ⚠️ MinerU 未生成 Markdown 输出文件")
            return None
        
        # 读取所有 Markdown 文件内容
        all_text = []
        for md_path in md_files:
            with open(md_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                all_text.append(content)
                print(f"  ✅ MinerU 输出: {md_path} ({len(content)} 字符)")
        
        if all_text:
            return "\n\n".join(all_text)
        else:
            return None
            
    except subprocess.TimeoutExpired:
        print(f"  ⚠️ MinerU 处理超时（5分钟）")
        return None
    except FileNotFoundError:
        print(f"  ⚠️ MinerU 未安装 (pip install mineru)")
        return None
    except Exception as e:
        print(f"  ⚠️ MinerU 调用异常: {e}")
        return None


def parse_si_file(filepath):
    """
    解析 SI 文件内容
    
    支持 PDF（含OCR扫描版检测和修复）、ZIP、TXT、CIF、HTML
    当检测到 OCR 质量为 poor 时，尝试调用 MinerU 进行高质量 OCR
    返回: (text, parse_info)
      text: 提取的文本
      parse_info: dict，包含解析状态和OCR信息
    """
    parse_info = {"format": None, "is_ocr": False, "ocr_quality": "good", "warnings": []}
    
    if filepath.endswith('.pdf'):
        if HAS_FITZ:
            doc = fitz.open(filepath)
            
            # 检测是否为OCR扫描版
            is_ocr, ocr_quality, ocr_details = detect_ocr_pdf(doc)
            parse_info["is_ocr"] = is_ocr
            parse_info["ocr_quality"] = ocr_quality
            parse_info["ocr_details"] = ocr_details
            
            if is_ocr:
                parse_info["warnings"].append(
                    f"检测到OCR扫描版PDF (质量: {ocr_quality})"
                )
                if ocr_details.get("reasons"):
                    parse_info["warnings"].extend(ocr_details["reasons"])
            
            # 提取文本
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            
            # 如果是OCR版且质量差，尝试使用 MinerU 进行高质量 OCR
            if is_ocr and ocr_quality == "poor":
                mineru_text = try_mineru_ocr(filepath)
                if mineru_text:
                    parse_info["warnings"].append("已使用 MinerU 进行高质量 OCR 重处理")
                    text = mineru_text
                else:
                    # MinerU 不可用，尝试基本修复
                    text = fix_ocr_text(text)
                    parse_info["warnings"].append("MinerU 不可用，已尝试基本 OCR 文本修复")
            elif is_ocr and ocr_quality != "good":
                # 中等质量，尝试修复
                text = fix_ocr_text(text)
                parse_info["warnings"].append("已尝试修复OCR文本错误")
            
            # 如果文本极少，标记为无法解析
            if len(text.strip()) < 50:
                parse_info["warnings"].append("文本提取量极少，可能需要专业OCR工具")
                text = f"[OCR解析失败] PDF可能为扫描版，提取文本仅{len(text.strip())}字符。建议使用MinerU (pip install mineru) 或Tesseract OCR处理后重新输入。"
            
            return text, parse_info
        else:
            return "[PyMuPDF 未安装，无法解析 PDF]", parse_info

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
        return "\n".join(texts), parse_info

    elif filepath.endswith('.txt') or filepath.endswith('.cif') or filepath.endswith('.html'):
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read(), parse_info

    else:
        return f"[未知文件格式: {filepath}]", parse_info


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
        text, parse_info = parse_si_file(filepath)
        if text:
            si_texts.append(text)
            print(f"  ✅ 解析完成: {os.path.basename(filepath)} ({len(text)} 字符)")
            # 输出OCR警告
            if parse_info.get("is_ocr"):
                print(f"  ⚠️ OCR扫描版PDF (质量: {parse_info.get('ocr_quality', 'unknown')})")
                for w in parse_info.get("warnings", []):
                    print(f"     - {w}")
                result["ocr_detected"] = True
                result["ocr_quality"] = parse_info.get("ocr_quality")
                result["ocr_warnings"] = parse_info.get("warnings", [])

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
