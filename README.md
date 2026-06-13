# CS599-2025303007-郑龙腾

## 项目名称
DocuMind - 智能文档问答系统

## 项目方向
🏭 **方向二：企业级应用软件的 Agent 改造**

## 项目简介
基于开源项目 [ask-multiple-pdfs](https://github.com/alejandro-ao/ask-multiple-pdfs) 进行企业级改造，使用 Agentic AI 技术解决企业文档问答场景的痛点。

### 改造前的问题
- ❌ 仅支持 OpenAI API，成本高（$0.002/1K tokens）
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

## 使用示例

### 上传文档

1. 点击侧边栏的 "Browse files"
2. 选择一个或多个 PDF 文件
3. 点击 "Process" 按钮
4. 等待处理完成（会显示提取的字符数和文本块数）

### 提问

在输入框中输入问题，例如：

- "这个文档的主要内容是什么？"
- "总结一下文档的核心观点"
- "文档中提到了哪些重要信息？"

## 技术亮点

### 1. 自定义 TF-IDF Embeddings

```
复制class ImprovedEmbeddings:
    """改进的 Embeddings，使用 TF-IDF 思想"""
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # 构建词汇表和 IDF
        # 使用 TF-IDF 计算向量
        # 支持中文和英文
```

### 2. 更小的文本块

```
复制text_splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=500,      # 从 1000 减小到 500
    chunk_overlap=100,   # 增加重叠
    length_function=len
)
```

### 3. 检索更多相关段落

```
复制retriever=vectorstore.as_retriever(
    search_kwargs={"k": 6}  # 从 4 增加到 6
)
```

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

