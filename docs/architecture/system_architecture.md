# 系统架构图 - DocuMind

## 整体架构

```mermaid
graph TB
    subgraph "用户界面层 (Streamlit)"
        A[文档上传界面]
        B[问答交互界面]
        C[统计面板]
        D[历史导出功能]
    end
    
    subgraph "应用逻辑层"
        E[文档处理模块]
        F[向量化模块]
        G[问答引擎]
        H[对话管理]
    end
    
    subgraph "数据存储层"
        I[FAISS 向量库]
        J[对话历史缓存]
    end
    
    subgraph "外部服务层"
        K[DeepSeek API]
        L[OpenAI Embeddings]
    end
    
    A --> E
    B --> G
    C --> H
    D --> H
    
    E --> F
    F --> L
    F --> I
    
    G --> I
    G --> K
    G --> H
    
    H --> J
    
    style A fill:#e1f5ff
    style B fill:#e1f5ff
    style C fill:#e1f5ff
    style D fill:#e1f5ff
    style K fill:#fff4e1
    style L fill:#fff4e1
```

## 技术栈说明

### 前端层
- **Streamlit**: Web UI 框架
- **HTML Templates**: 自定义样式

### 后端层
- **LangChain**: LLM 应用框架
- **PyPDF2**: PDF 文本提取
- **Python**: 核心逻辑

### 存储层
- **FAISS**: 向量数据库（本地）
- **Session State**: 会话状态管理

### 外部服务
- **DeepSeek API**: 大语言模型
- **OpenAI Embeddings**: 文本向量化