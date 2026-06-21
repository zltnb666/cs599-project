# CS599-2025303007-郑龙腾

## 项目名称
DocuMind - 智能文档问答系统

## 项目方向
🏭 **方向一：Agentic AI原生开发**

## 项目简介
基于开源项目 [ask-multiple-pdfs](https://github.com/alejandro-ao/ask-multiple-pdfs) 进行改造，使用 Agentic AI 技术解决文档问答场景的痛点。DocuMind 是一个智能文档问答系统，用户可以上传 PDF 文档，通过自然语言提问获取答案。系统基于 RAG（检索增强生成）架构，使用 DeepSeek API 替代传统的 OpenAI，实现成本降低的同时保持优秀的回答质量。

### 改造前的问题
- ❌ 仅支持 OpenAI API，成本高
- ❌ 无法查看答案来源，可信度低
- ❌ 缺少对话历史管理
- ❌ 使用简单 Embeddings，检索精度低

### 改造后的优势
- ✅ 支持 DeepSeek API，成本降低
- ✅ 自定义 TF-IDF Embeddings，支持中文，免费
- ✅ 改进的检索策略（k=6，chunk_size=500）
- ✅ 更好的错误处理和用户提示

## 技术栈
- **LLM**: DeepSeek Chat API
- **框架**: LangChain + Streamlit
- **向量数据库**: FAISS
- **Embeddings**: 自定义 TF-IDF Embeddings
- **语言**: Python 3.8+
- **PDF解析**:PyPDF2 

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/你的用户名/CS599-2025303007-郑龙腾.git
cd CS599-2025303007-郑龙腾
```

### 2. 安装依赖

```
复制
pip install -r requirements.txt
```

### 3. 配置环境变量

```
复制cp .env.example .env
# 编辑 .env 文件，填入你的 DeepSeek API Key
```

.env 文件内容：

```
复制OPENAI_API_KEY=your_deepseek_api_key_here
OPENAI_API_BASE=https://api.deepseek.com/v1
```

### 4. 运行应用

```
复制
streamlit run app.py
```

访问 [http://localhost:8501](http://localhost:8501/)

## 📖 使用指南

### 步骤 1：上传文档

1. 在侧边栏点击「上传 PDF 文件」
2. 选择一个或多个 PDF 文件
3. 点击「🚀 处理文档」按钮

### 步骤 2：提问

1. 在主界面输入框输入问题
2. 按 Enter 键提交
3. 等待 AI 生成答案

### 步骤 3：查看来源

1. 在 AI 回答下方点击「📚 查看答案来源」
2. 展开查看引用的文档和具体片段

### 步骤 4：导出对话

1. 在侧边栏找到「💾 导出对话」
2. 选择 TXT 或 JSON 格式下载

## 项目目录结构

```
复制CS599-2025303007-郑龙腾/
├── app.py                 # 主应用程序
├── htmlTemplates.py       # UI 模板
├── requirements.txt       # 依赖列表
├── .env.example          # 环境变量示例
├── .env                  # 环境变量（不提交）
├── docs/
│   ├── specs/            # 规格文档
│   ├── architecture/     # 架构图
│   ├── demo/            # 演示截图/视频
│   └── CS599_大作业报告.pdf
├── tests/               # 测试文件
└── README.md
```

## 核心功能

### 1. 多 PDF 文档上传与处理

- 支持同时上传多个 PDF 文件
- 自动提取文本并分块处理（chunk_size=500）
- 向量化存储，支持语义检索

### 2. 智能问答

- 基于文档内容的准确回答
- 支持多轮对话
- 上下文理解
- 检索 6 个相关段落，提升准确率

### 3. 改进的 Embeddings

- 使用 TF-IDF 算法
- 支持中文和英文
- 完全免费
- 检索精度优于简单哈希

## 改造对比

| 功能       | 原始项目          | 改造后        | 改进效果       |
| ---------- | ----------------- | ------------- | -------------- |
| LLM API    | OpenAI GPT-3.5    | DeepSeek Chat | 成本降低       |
| Embeddings | OpenAI Embeddings | 自定义 TF-IDF | 免费，支持中文 |
| 检索数量   | k=4               | k=6           | 召回率提升     |
| 文本块大小 | 1000              | 500           | 精度提升       |
| 错误处理   | 基础              | 完善          | 用户体验改善   |

## 项目状态

- ✅ Proposal（已完成）
- ✅ MVP（已完成）
- ⏳ Final（进行中）

## 技术亮点

### 1. 成本优化

- 从 OpenAI GPT-3.5/4 迁移到 DeepSeek
- 保持相同的 API 接口

### 2. 引用来源展示

- 显示答案来源的文档名称
- 显示具体引用的文本片段
- 提高答案可信度和透明度

### 3. 用户体验优化

- 实时统计面板
- 对话历史导出
- 友好的错误提示
- 响应式界面设计

### 4. 技术创新

- 自定义 TF-IDF Embeddings
- 元数据追踪系统
- 高效的向量检索

## 🐛 常见问题

### Q1: 无法提取 PDF 文本？

**A**: 确保 PDF 不是扫描件，系统只支持文本型 PDF。

### Q2: API 调用失败？

**A**: 检查 `.env` 文件中的 API Key 是否正确。

### Q3: 回答不准确？

**A**: 尝试调整 `chunk_size` 和 `chunk_overlap` 参数。

## 参考资料

- 原始项目: [alejandro-ao/ask-multiple-pdfs](https://github.com/alejandro-ao/ask-multiple-pdfs)
- LangChain 文档: https://python.langchain.com/
- DeepSeek API: https://platform.deepseek.com/
- FAISS 文档: https://faiss.ai/

## 作者信息

- **学号**: 2025303007
- **姓名**: 郑龙腾
- **专业**: 计算机技术
- **课程**: CS599 企业级应用软件设计与开发
- **指导教师**: 戚欣
- **提交日期**: 2026年6月22日

## 许可证

MIT License

## 致谢

感谢原项目作者 Alejandro AO 提供的优秀开源项目。

## 📧 联系方式

- **GitHub**: [@zltnb666](https://github.com/zltnb666)
- **项目地址**: [cs599-project](https://github.com/zltnb666/cs599-project)

------

**⭐ 如果这个项目对你有帮助，请给个 Star！**
