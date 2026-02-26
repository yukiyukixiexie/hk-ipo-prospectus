#!/usr/bin/env python3
"""
港交所披露易招股书自动抓取工具

使用 Playwright 自动化浏览器，从披露易网站搜索并下载招股书PDF

依赖安装:
    pip install playwright requests
    playwright install chromium

用法:
    python fetch_prospectus.py <股票代码>              # 搜索并下载招股书
    python fetch_prospectus.py <股票代码> --search     # 仅搜索，显示PDF链接
    python fetch_prospectus.py <股票代码> --visible    # 显示浏览器窗口（调试）
    python fetch_prospectus.py --url <PDF_URL>         # 直接下载指定URL

示例:
    python fetch_prospectus.py 02513
    python fetch_prospectus.py 02513 --search
"""

import json
import os
import sys
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import urljoin

# ============================================================
# 配置
# ============================================================

TITLE_SEARCH_URL = "https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=zh"
BASE_URL = "https://www1.hkexnews.hk"
DOWNLOAD_DIR = os.path.expanduser("~/Downloads/hk_ipo_prospectus")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}

# IPO相关关键词（用于识别招股书相关文件）
PROSPECTUS_KEYWORDS = [
    "招股", "Prospectus", "Global Offering", "全球發售",
    "聆訊", "配發結果", "發售價", "上市文件",
    "申請版本", "Post Hearing"
]


# ============================================================
# Playwright 自动化搜索
# ============================================================

def search_documents_playwright(
    stock_code: str = None,
    company_name: str = None,
    category: str = None,
    date_from: str = None,
    date_to: str = None,
    headless: bool = True,
    timeout: int = 30000
) -> List[Dict]:
    """
    使用 Playwright 从披露易搜索文件

    参数:
        stock_code: 股票代码 (如 02513)
        company_name: 公司名称 (如 智谱)
        category: 文件类别 (如 "上市文件")
        date_from: 开始日期 (YYYY-MM-DD)
        date_to: 结束日期 (YYYY-MM-DD)
        headless: 是否无头模式
        timeout: 超时时间(毫秒)

    返回:
        [{"title": ..., "url": ..., "file_type": ...}, ...]
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("错误: 需要安装 playwright", file=sys.stderr)
        print("运行: pip install playwright && playwright install chromium", file=sys.stderr)
        return []

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="zh-CN"
        )
        page = context.new_page()

        try:
            print(f"访问披露易搜索页面...", file=sys.stderr)
            page.goto(TITLE_SEARCH_URL, wait_until="networkidle", timeout=timeout)

            # 等待页面加载完成 - 等待搜索按钮出现 (蓝色按钮)
            page.wait_for_selector("a.btn-blue", timeout=timeout)

            # 关闭Cookie弹窗
            try:
                accept_btn = page.locator("button:has-text('接受'), button:has-text('Accept')")
                if accept_btn.count() > 0 and accept_btn.first.is_visible():
                    print("关闭Cookie弹窗...", file=sys.stderr)
                    accept_btn.first.click()
                    page.wait_for_timeout(500)
            except:
                pass

            # 输入股票代码
            if stock_code:
                stock_code = stock_code.replace(".HK", "").replace(".hk", "").zfill(5)
                print(f"输入股票代码: {stock_code}", file=sys.stderr)

                # 使用正确的选择器 - #searchStockCode
                stock_input = page.locator("#searchStockCode")
                if stock_input.count() > 0 and stock_input.is_visible():
                    stock_input.fill(stock_code)
                    page.wait_for_timeout(1500)  # 等待autocomplete出现

                    # 查找autocomplete表格行并点击第一个匹配的
                    autocomplete_rows = page.locator("table tr").all()
                    for row in autocomplete_rows:
                        try:
                            text = row.inner_text()
                            if stock_code in text:
                                row.click()
                                page.wait_for_timeout(500)
                                print(f"选择股票: {text.strip()[:30]}", file=sys.stderr)
                                break
                        except:
                            continue
                else:
                    # 备用选择器
                    page.fill("input[placeholder*='股份代號/股份名稱']", stock_code)

            # 输入公司名称
            if company_name:
                print(f"输入公司名称: {company_name}", file=sys.stderr)
                stock_input = page.locator("#searchStockCode")
                if stock_input.count() > 0 and stock_input.is_visible():
                    stock_input.fill(company_name)
                    page.wait_for_timeout(1500)
                    # 点击第一个匹配结果
                    autocomplete_rows = page.locator("table tr").all()
                    for row in autocomplete_rows:
                        try:
                            if company_name in row.inner_text():
                                row.click()
                                break
                        except:
                            continue

            # 选择文件类别（上市文件）- 披露易使用combobox下拉
            if category:
                print(f"选择文件类别: {category}", file=sys.stderr)
                try:
                    # 找到标题类别下拉框并点击
                    dropdowns = page.locator(".combobox-field, .dropdown-toggle")
                    for i in range(dropdowns.count()):
                        dropdown = dropdowns.nth(i)
                        if dropdown.is_visible():
                            dropdown.click()
                            page.wait_for_timeout(300)
                            # 选择上市文件
                            option = page.locator(f"text={category}")
                            if option.count() > 0:
                                option.first.click()
                                page.wait_for_timeout(300)
                                break
                except:
                    pass

            # 点击搜索按钮 (蓝色按钮)
            print("执行搜索...", file=sys.stderr)
            search_btn = page.locator("a.btn-blue, a.filter__btn-applyFilters-js")
            if search_btn.count() > 0:
                search_btn.first.click()
            else:
                page.locator("a:has-text('搜尋')").nth(2).click()

            # 等待结果加载
            page.wait_for_load_state("networkidle", timeout=timeout)
            page.wait_for_timeout(2000)  # 额外等待动态内容

            # 提取PDF链接
            print("提取搜索结果...", file=sys.stderr)

            # 只提取listedco目录下的PDF（公司文件）
            pdf_links = page.locator("a[href*='listedco'][href*='.pdf']").all()
            print(f"找到 {len(pdf_links)} 个公司PDF文件", file=sys.stderr)

            for link in pdf_links[:100]:  # 最多处理100个
                try:
                    href = link.get_attribute("href")
                    title = link.inner_text().strip()

                    if href:
                        full_url = href if href.startswith("http") else urljoin(BASE_URL, href)
                        results.append({
                            "title": title,
                            "url": full_url,
                            "file_type": "PDF"
                        })
                except Exception as e:
                    continue

            # 截图保存（调试用）
            if os.environ.get("DEBUG"):
                screenshot_path = f"/tmp/hkex_search_{stock_code or 'all'}.png"
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"截图保存到: {screenshot_path}", file=sys.stderr)

        except Exception as e:
            print(f"搜索失败: {e}", file=sys.stderr)
            # 保存错误截图
            try:
                page.screenshot(path="/tmp/hkex_error.png")
            except:
                pass

        finally:
            browser.close()

    # 去重
    seen = set()
    unique_results = []
    for r in results:
        url = r.get("url", "")
        if url and url not in seen:
            seen.add(url)
            unique_results.append(r)

    return unique_results


def find_prospectus_pdfs(stock_code: str, headless: bool = True, days: int = 180) -> List[Dict]:
    """
    搜索股票的招股书PDF

    参数:
        stock_code: 股票代码
        headless: 是否无头模式
        days: 搜索最近多少天的文件

    返回:
        [{"title": ..., "url": ...}, ...]
    """
    # 计算日期范围
    date_to = datetime.now().strftime("%Y-%m-%d")
    date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    results = search_documents_playwright(
        stock_code=stock_code,
        category="上市文件",
        date_from=date_from,
        date_to=date_to,
        headless=headless
    )

    return results


# ============================================================
# PDF下载
# ============================================================

def download_pdf(url: str, save_dir: str = None, filename: str = None) -> Optional[str]:
    """下载PDF文件"""
    if not url:
        return None

    if save_dir is None:
        save_dir = DOWNLOAD_DIR

    os.makedirs(save_dir, exist_ok=True)

    if filename is None:
        filename = os.path.basename(url.split("?")[0])
        if not filename.endswith(".pdf"):
            filename = f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    filepath = os.path.join(save_dir, filename)

    try:
        print(f"下载: {url}", file=sys.stderr)
        resp = requests.get(url, headers=HEADERS, timeout=120, stream=True)
        resp.raise_for_status()

        # 检查是否是PDF
        content_type = resp.headers.get("Content-Type", "")
        if "pdf" not in content_type.lower() and not url.endswith(".pdf"):
            print(f"警告: 可能不是PDF文件 (Content-Type: {content_type})", file=sys.stderr)

        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        file_size = os.path.getsize(filepath)
        print(f"保存到: {filepath} ({file_size / 1024 / 1024:.2f} MB)", file=sys.stderr)
        return filepath

    except Exception as e:
        print(f"下载失败: {e}", file=sys.stderr)
        return None


def download_prospectus(stock_code: str, save_dir: str = None, headless: bool = True, max_files: int = 10) -> List[str]:
    """
    搜索并下载股票的招股书

    参数:
        stock_code: 股票代码
        save_dir: 保存目录
        headless: 是否无头模式
        max_files: 最多下载文件数

    返回:
        下载的文件路径列表
    """
    stock_code = stock_code.replace(".HK", "").replace(".hk", "").zfill(5)

    if save_dir is None:
        save_dir = os.path.join(DOWNLOAD_DIR, stock_code)

    print(f"搜索 {stock_code} 的招股书...", file=sys.stderr)
    results = find_prospectus_pdfs(stock_code, headless=headless)

    if not results:
        print(f"未找到 {stock_code} 的招股书", file=sys.stderr)
        return []

    print(f"找到 {len(results)} 个PDF文件", file=sys.stderr)

    downloaded = []
    for i, item in enumerate(results[:max_files]):
        url = item.get("url")
        filepath = download_pdf(url, save_dir)
        if filepath:
            downloaded.append(filepath)
        time.sleep(1)  # 避免请求过快

    return downloaded


# ============================================================
# 主函数
# ============================================================

def print_help():
    """打印帮助信息"""
    print("""
港交所招股书自动抓取工具

用法:
  python fetch_prospectus.py <股票代码>              # 搜索并下载招股书
  python fetch_prospectus.py <股票代码> --search     # 仅搜索，显示PDF链接
  python fetch_prospectus.py <股票代码> --visible    # 显示浏览器窗口（调试）
  python fetch_prospectus.py --url <PDF_URL>         # 直接下载指定URL

示例:
  python fetch_prospectus.py 02513
  python fetch_prospectus.py 02513 --search
  python fetch_prospectus.py 02513 --visible
  python fetch_prospectus.py --url "https://www1.hkexnews.hk/xxx.pdf"

下载位置: ~/Downloads/hk_ipo_prospectus/<股票代码>/

依赖安装:
  pip install playwright requests
  playwright install chromium
""")


def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    arg = sys.argv[1]

    # 帮助
    if arg in ["-h", "--help"]:
        print_help()
        return

    headless = "--visible" not in sys.argv

    # 直接URL下载模式
    if arg == "--url":
        if len(sys.argv) < 3:
            print("错误: 请提供PDF URL", file=sys.stderr)
            sys.exit(1)
        url = sys.argv[2]
        filepath = download_pdf(url)
        if filepath:
            print(json.dumps({"url": url, "downloaded": filepath}, ensure_ascii=False, indent=2))
        return

    stock_code = arg

    # 仅搜索模式
    if "--search" in sys.argv:
        results = find_prospectus_pdfs(stock_code, headless=headless)
        pdf_urls = [r.get("url") for r in results]
        output = {
            "stock_code": stock_code,
            "count": len(results),
            "files": results,
            "pdf_urls": pdf_urls
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    # 默认：搜索并下载
    downloaded = download_prospectus(stock_code, headless=headless)
    print(json.dumps({
        "stock_code": stock_code,
        "downloaded": downloaded
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
