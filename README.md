# HK IPO Analysis Tools

港股 IPO 分析工具集 - 招股书下载 + 财报解读

## Skills

| Skill | 说明 |
|-------|------|
| `/hk-ipo-prospectus` | 从披露易搜索并下载招股书 PDF |
| `/earnings-decoder` | 买方视角财报解读，从价格反推假设 |

---

## Skill 1: HK IPO Prospectus Downloader

港交所IPO招股书自动下载工具 - 从披露易 (HKEXnews) 搜索并下载招股书PDF

### Features

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

---

## Skill 2: Earnings Decoder

买方视角财报解读框架 - 从价格反推假设，用数据验证，输出仓位决策

### 使用方法

```bash
# 财报已发布时
/earnings-decoder AAPL

# 财报前瞻模式
/earnings-decoder AAPL --pre-earnings
```

### 核心功能

- **盘前模式**：财报前瞻分析，预期差识别，策略建议
- **财报解读模式**：从价格反推假设 → 数据验证 → 仓位决策

### 分析框架

1. 从价格与市场反应反推"隐含假设"
2. 用财报数据验证假设
3. 判断"变化"的性质（结构性/周期性/一次性）
4. 给出数据能支持到的最远结论
5. 将不确定性显式纳入仓位逻辑
6. 仓位决策输出

### 数据来源

- Yahoo Finance（一致预期）
- Seeking Alpha（Earnings Call Transcript）
- SEC EDGAR（原始财务数据）
- 大行报告（Goldman Sachs, Morgan Stanley 等）

---

## License

MIT
