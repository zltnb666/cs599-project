# 🏗️ DocuMind 架构设计文档

## 📋 目录

1. [系统概述]
4. [核心组件]
5. [技术选型]
6. [性能优化]

---

## 🎯 系统概述

DocuMind 是一个基于 RAG（Retrieval-Augmented Generation）架构的智能文档问答系统。系统通过向量检索和大语言模型相结合，实现对 PDF 文档内容的智能问答。

### 核心目标

- **成本优化**: 使用 DeepSeek API 替代 OpenAI
- **透明度**: 提供答案来源追踪，提高可信度
- **易用性**: 简洁直观的用户界面
- **可扩展**: 模块化设计，易于扩展新功能

------

## 🔧 核心组件详解

### 1. 文档处理模块

**功能**：将 PDF 转换为可检索的文本块

```
复制def get_pdf_text(pdf_docs):
    """提取 PDF 文本"""
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    """文本分块"""
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,      # 每块 1000 字符
        chunk_overlap=200,    # 重叠 200 字符
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks
```

**关键参数**：

- `chunk_size=1000`：平衡上下文长度和检索精度
- `chunk_overlap=200`：保持语义连贯性
- `separator="\n"`：按段落分割

### 2. 向量化模块

**功能**：将文本转换为数值向量

```
复制class TFIDFEmbeddings:
    """自定义 TF-IDF Embeddings"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=384,      # 向量维度
            ngram_range=(1, 2),    # 1-2 gram
            min_df=1,
            max_df=0.95
        )
    
    def embed_documents(self, texts):
        """批量向量化"""
        return self.vectorizer.fit_transform(texts).toarray()
    
    def embed_query(self, text):
        """查询向量化"""
        return self.vectorizer.transform([text]).toarray()[0]
```

**优势**：

- ✅ 无需外部 API，成本为零
- ✅ 速度快，适合实时应用
- ✅ 中文支持良好
- ✅ 可解释性强

### 3. 检索模块

**功能**：从向量库检索相关文档

```
复制def get_vectorstore(text_chunks, metadatas):
    """创建 FAISS 向量存储"""
    embeddings = TFIDFEmbeddings()
    vectorstore = FAISS.from_texts(
        texts=text_chunks,
        embedding=embeddings,
        metadatas=metadatas  # 保存文档来源信息
    )
    return vectorstore
```

**检索策略**：

- Top-K=4：返回最相关的 4 个片段
- 余弦相似度：计算查询和文档的相似度
- 元数据追踪：记录每个片段的来源文档

### 4. 对话模块

**功能**：生成答案并追踪来源

```
复制def get_conversation_chain(vectorstore):
    """创建对话链"""
    llm = ChatOpenAI(
        model_name="deepseek-chat",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_api_base="https://api.deepseek.com/v1",
        temperature=0.3
    )
    
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        return_source_documents=True,  # 返回来源文档
        memory=ConversationBufferMemory(
            memory_key='chat_history',
            return_messages=True
        )
    )
    
    return conversation_chain
```

**关键特性**：

- `return_source_documents=True`：返回引用来源
- `temperature=0.3`：降低随机性，提高准确性
- `ConversationBufferMemory`：维护对话上下文

------

## 🛠️ 技术选型

### 核心技术栈

| 组件           | 技术选型  | 替代方案             | 选择理由           |
| -------------- | --------- | -------------------- | ------------------ |
| **前端框架**   | Streamlit | Gradio / Flask       | 快速开发，组件丰富 |
| **LLM**        | DeepSeek  | OpenAI GPT           | 成本低 ，中文优秀  |
| **向量库**     | FAISS     | Pinecone / Milvus    | 轻量级，无需部署   |
| **Embeddings** | TF-IDF    | OpenAI / HuggingFace | 零成本，速度快     |
| **PDF 解析**   | PyPDF2    | pdfplumber           | 简单易用           |
| **LLM 框架**   | LangChain | LlamaIndex           | 生态完善，社区活跃 |

## ⚡ 性能优化

### 1. 缓存策略

```
复制@st.cache_resource
def get_vectorstore(text_chunks, metadatas):
    """缓存向量存储，避免重复创建"""
    pass

@st.cache_data
def get_pdf_text(pdf_docs):
    """缓存 PDF 文本，避免重复解析"""
    pass
```

### 2. 向量检索优化

**FAISS 索引类型**：

- 使用 `IndexFlatL2`：精确搜索
- 数据量 > 10000 时可切换到 `IndexIVFFlat`：近似搜索

**检索参数**：

- Top-K=4：平衡准确性和速度
- 批量检索：减少 API 调用次数

### 3. API 调用优化

```
复制llm = ChatOpenAI(
    temperature=0.3,        # 降低随机性
    max_tokens=1000,        # 限制输出长度
    request_timeout=30,     # 超时设置
    max_retries=2           # 重试机制
)
```

------

## 🔒 安全设计

### 1. API Key 保护

```
复制# .env 文件
OPENAI_API_KEY=sk-xxx
OPENAI_API_BASE=https://api.deepseek.com/v1

# .gitignore
.env
*.env
```

### 2. 输入验证

```
复制# 文件类型检查
if uploaded_file.type != "application/pdf":
    st.error("❌ 仅支持 PDF 文件")
    
# 文件大小限制
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB
if uploaded_file.size > MAX_FILE_SIZE:
    st.error("❌ 文件过大，请上传小于 200MB 的文件")
```

### 3. 错误处理

```
复制try:
    response = st.session_state.conversation({'question': user_question})
except Exception as e:
    st.error(f"❌ 发生错误: {str(e)}")
    logger.error(f"Error in conversation: {e}")
```

------

## 📊 核心改造点

### 1. API 替换（成本优化）

**改造前**：

```
复制llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    openai_api_key="sk-xxx"
)
```

**改造后**：

```
复制llm = ChatOpenAI(
    model_name="deepseek-chat",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    openai_api_base="https://api.deepseek.com/v1"
)
```

**影响**：

- ✅ 仅需修改 3 行代码
- ✅ API 完全兼容，无需改动其他逻辑

### 2. 引用来源展示（透明度提升）

**新增功能**：

```
复制# 提取来源文档
source_documents = response.get('source_documents', [])

# 展示来源
with st.expander("📚 查看答案来源"):
    for i, doc in enumerate(source_documents):
        st.markdown(f"**来源 {i+1}:**")
        st.markdown(f"- 📄 文档: `{doc.metadata.get('source', '未知')}`")
        st.markdown(f"- 📝 内容片段:")
        st.text_area("", doc.page_content, height=100, key=f"source_{i}")
```

**效果**：

- ✅ 用户可验证答案来源
- ✅ 提高系统可信度
- ✅ 符合学术规范

### 3. 对话历史导出（可追溯性）

**新增功能**：

```
复制# TXT 格式导出
def export_txt():
    content = ""
    for msg in st.session_state.chat_history:
        if msg.type == "human":
            content += f"👤 用户: {msg.content}\n\n"
        else:
            content += f"🤖 AI: {msg.content}\n\n"
    return content

# JSON 格式导出
def export_json():
    history = []
    for msg in st.session_state.chat_history:
        history.append({
            "role": "user" if msg.type == "human" else "assistant",
            "content": msg.content,
            "timestamp": datetime.now().isoformat()
        })
    return json.dumps(history, ensure_ascii=False, indent=2)
```

**效果**：

- ✅ 支持两种格式导出
- ✅ 方便后续分析和审计
- ✅ 符合数据管理规范

------

## 🔮 未来优化方向

### 短期（1-2 周）

-  添加文档缓存机制
-  优化文本分块策略（语义分块）
-  实现批量文档处理

### 中期（1-2 月）

-  支持更多文档格式（Word, TXT, Markdown）
-  实现用户认证系统
-  添加对话历史持久化（数据库）

### 长期（3-6 月）

-  微服务架构改造
-  多租户支持
-  分布式向量检索
-  支持图片和表格解析

------

## 📚 参考资料

- [LangChain 官方文档](https://python.langchain.com/)
- [FAISS GitHub](https://github.com/facebookresearch/faiss)
- [Streamlit 文档](https://docs.streamlit.io/)
- [DeepSeek API 文档](https://platform.deepseek.com/api-docs/)
- [Mermaid 图表语法](https://mermaid.js.org/)

------

**文档版本**: v1.0
 **最后更新**: 2026-06-14
 **作者**: 郑龙腾 (2025303007)
 **课程**: CS599 企业级应用软件设计与开发
 **指导教师**: 戚欣