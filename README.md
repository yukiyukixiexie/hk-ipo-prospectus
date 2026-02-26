# HK IPO Prospectus Downloader

港交所IPO招股书自动下载工具 - 从披露易 (HKEXnews) 搜索并下载招股书PDF

## Features

- 自动从港交所披露易搜索IPO相关文件
- 支持按股票代码搜索
- 自动下载PDF文件到本地
- 支持调试模式（显示浏览器）

## Installation

```bash
# 安装依赖
pip install playwright requests

# 安装浏览器
playwright install chromium
```

## Usage

### 作为Claude Code Skill使用

```bash
# 在Claude Code中
/hk-ipo-prospectus 02513
```

### 命令行使用

```bash
# 搜索并下载招股书
python fetch_prospectus.py 02513

# 仅搜索，显示PDF链接
python fetch_prospectus.py 02513 --search

# 显示浏览器窗口（调试）
python fetch_prospectus.py 02513 --visible

# 直接下载指定URL
python fetch_prospectus.py --url "https://www1.hkexnews.hk/listedco/xxx.pdf"
```

## Output

### 搜索模式 (--search)

```json
{
  "stock_code": "02513",
  "count": 14,
  "files": [
    {"title": "全球發售", "url": "https://..."},
    ...
  ],
  "pdf_urls": [...]
}
```

### 下载模式

```json
{
  "stock_code": "02513",
  "downloaded": [
    "/Users/xxx/Downloads/hk_ipo_prospectus/02513/xxx.pdf",
    ...
  ]
}
```

## File Location

下载的文件保存到: `~/Downloads/hk_ipo_prospectus/<股票代码>/`

## Common IPO Documents

| 文件类型 | 说明 |
|---------|------|
| 全球發售 | 完整招股书 |
| 聆訊後資料集 | 聆讯后补充资料 |
| 發售價及配發結果公告 | 定价和配售结果 |
| 公司章程 | 公司章程全文 |

## Data Source

- 港交所披露易 (HKEXnews): https://www.hkexnews.hk

## Requirements

- Python 3.8+
- playwright
- requests

## License

MIT
