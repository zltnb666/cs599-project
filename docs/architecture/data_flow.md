# 数据流程图 - DocuMind

## 文档处理流程

```mermaid
flowchart LR
    A[用户上传 PDF] --> B[提取文本内容]
    B --> C[文本分块处理]
    C --> D[调用 OpenAI Embeddings]
    D --> E[生成向量]
    E --> F[存储到 FAISS]
    F --> G[完成索引]
    
    style A fill:#e1f5ff
    style G fill:#e8f5e9
```

## 问答交互流程

```mermaid
flowchart TB
    A[用户输入问题] --> B[问题向量化]
    B --> C[FAISS 相似度检索]
    C --> D[获取相关文档片段]
    D --> E[构建 Prompt]
    E --> F[调用 DeepSeek API]
    F --> G[生成答案]
    G --> H[提取引用来源]
    H --> I[展示答案 + 来源]
    I --> J[保存到对话历史]
    
    style A fill:#e1f5ff
    style I fill:#e8f5e9
    style F fill:#fff4e1
```

## 对话历史导出流程

```mermaid
flowchart LR
    A[用户点击导出] --> B[读取对话历史]
    B --> C[格式化数据]
    C --> D{选择格式}
    D -->|TXT| E[生成文本文件]
    D -->|JSON| F[生成 JSON 文件]
    E --> G[下载文件]
    F --> G
    
    style A fill:#e1f5ff
    style G fill:#e8f5e9
```

## 核心改造点

### 1. API 替换
- **原始**: OpenAI GPT-3.5 API
- **改造**: DeepSeek Chat API
- **影响**: 仅需修改 API 调用部分，其他逻辑不变

### 2. 引用来源
- **新增**: 在返回答案时附带文档来源信息
- **实现**: 从检索结果中提取 metadata

### 3. 对话历史
- **新增**: Session State 存储对话记录
- **实现**: 导出为 TXT/JSON 格式

```