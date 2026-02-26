---
name: hk-ipo-prospectus
description: 港交所IPO招股书自动下载工具 - 从披露易搜索并下载招股书PDF
argument-hint: <股票代码> [--search] [--visible]
allowed-tools: Bash, Read
model: sonnet
user-invocable: true
---

# 港交所IPO招股书下载工具

从港交所披露易 (HKEXnews) 自动搜索并下载上市公司招股书及相关IPO文件。

## 使用方法

### 1. 搜索并下载招股书

```bash
# 下载指定股票的所有IPO文件
python3 {SKILL_DIR}/fetch_prospectus.py <股票代码>

# 示例：下载智谱(02513)的招股书
python3 {SKILL_DIR}/fetch_prospectus.py 02513
```

### 2. 仅搜索（不下载）

```bash
# 搜索并显示PDF链接列表
python3 {SKILL_DIR}/fetch_prospectus.py <股票代码> --search

# 示例
python3 {SKILL_DIR}/fetch_prospectus.py 02513 --search
```

### 3. 调试模式（显示浏览器）

```bash
# 显示浏览器窗口，方便调试
python3 {SKILL_DIR}/fetch_prospectus.py <股票代码> --visible
```

### 4. 直接下载指定URL

```bash
# 直接下载指定的PDF文件
python3 {SKILL_DIR}/fetch_prospectus.py --url "https://www1.hkexnews.hk/listedco/listconews/sehk/2025/1230/xxx.pdf"
```

## 输出说明

### 搜索模式输出 (--search)

```json
{
  "stock_code": "02513",
  "count": 14,
  "pdf_urls": [
    "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0107/xxx.pdf",
    ...
  ]
}
```

### 下载模式输出

```json
{
  "stock_code": "02513",
  "downloaded": [
    "/Users/xxx/Downloads/hk_ipo_prospectus/02513/xxx.pdf",
    ...
  ]
}
```

## 下载文件位置

默认保存到：`~/Downloads/hk_ipo_prospectus/<股票代码>/`

## 常见IPO文件类型

| 文件类型 | 说明 |
|---------|------|
| 全球發售 | 完整招股书（最重要） |
| 聆訊後資料集 | 聆讯后补充资料 |
| 發售價及配發結果公告 | 定价和配售结果 |
| 公司章程 | 公司章程全文 |
| 董事名單與其角色及職能 | 董事信息 |
| 股份發行人的證券變動月報表 | 月度股份变动 |

## 招股书分析要点

下载招股书后，重点关注以下资金结构信息：

### 1. 股本结构
- 发行前总股本
- 本次发行股数
- 发行后总股本
- 公众持股比例

### 2. 募资详情
- 发行价区间
- 募资总额
- 超额配股权
- 稳定价格机制

### 3. 基石投资者
- 基石投资者名单
- 认购金额
- 锁定期安排

### 4. 股东结构
- 大股东持股比例
- 高管持股
- 锁定期安排

### 5. 资金用途
- 募资用途分配
- 研发投入计划
- 业务扩展计划

## 依赖安装

```bash
pip install playwright requests
playwright install chromium
```

## 数据源

- 港交所披露易 (HKEXnews): https://www.hkexnews.hk
- 搜索页面: https://www1.hkexnews.hk/search/titlesearch.xhtml

## 注意事项

1. 首次使用需要安装 Chromium 浏览器
2. 网站使用 JavaScript 动态加载，需要 Playwright 自动化
3. 搜索默认获取最近180天的上市文件
4. 下载默认限制最多10个文件，避免过多请求
5. 文件名来源于披露易原始文件名

## 常见问题

### Q: 搜索返回0结果？
A: 检查股票代码是否正确，确认该股票是否为近期IPO

### Q: 下载失败？
A:
1. 检查网络连接
2. 尝试使用 `--visible` 模式调试
3. 确认 Playwright Chromium 已安装

### Q: 如何获取更早的招股书？
A: 修改脚本中的日期范围参数，或直接使用 `--url` 下载指定链接
