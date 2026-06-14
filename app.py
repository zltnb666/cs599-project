import streamlit as st
import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template
import numpy as np
from typing import List
import hashlib
import json


# 改进的 Embeddings 类
class ImprovedEmbeddings:
    """改进的 Embeddings，使用 TF-IDF 思想"""

    def __init__(self):
        self.vocab = {}
        self.idf = {}

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """将文本转换为向量"""
        # 构建词汇表
        self._build_vocab(texts)

        embeddings = []
        for text in texts:
            vector = self._text_to_vector(text)
            embeddings.append(vector)
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """将查询转换为向量"""
        return self._text_to_vector(text)

    def _build_vocab(self, texts: List[str]):
        """构建词汇表和 IDF"""
        all_words = set()
        for text in texts:
            words = self._tokenize(text)
            all_words.update(words)

        # 构建词汇表索引
        self.vocab = {word: idx for idx, word in enumerate(sorted(all_words))}

        # 计算 IDF
        doc_count = len(texts)
        word_doc_count = {}
        for text in texts:
            words = set(self._tokenize(text))
            for word in words:
                word_doc_count[word] = word_doc_count.get(word, 0) + 1

        for word, count in word_doc_count.items():
            self.idf[word] = np.log(doc_count / (count + 1))

    def _tokenize(self, text: str) -> List[str]:
        """简单的分词"""
        text = text.lower()
        # 支持中文和英文
        import re
        # 提取中文字符和英文单词
        chinese = re.findall(r'[\u4e00-\u9fff]+', text)
        english = re.findall(r'[a-z]+', text)

        # 中文按字符分，英文按单词分
        tokens = []
        for word in chinese:
            tokens.extend(list(word))
        tokens.extend(english)

        return tokens

    def _text_to_vector(self, text: str, dim: int = 512) -> List[float]:
        """将文本转换为向量（使用 TF-IDF）"""
        if not self.vocab:
            # 如果没有词汇表，使用简单哈希
            return self._simple_hash_vector(text, dim)

        # 使用 TF-IDF
        words = self._tokenize(text)
        word_count = {}
        for word in words:
            word_count[word] = word_count.get(word, 0) + 1

        # 创建稀疏向量
        vector = np.zeros(min(dim, len(self.vocab)))
        for word, count in word_count.items():
            if word in self.vocab:
                idx = self.vocab[word] % dim
                tf = count / len(words) if words else 0
                idf = self.idf.get(word, 1)
                vector[idx] += tf * idf

        # 归一化
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector.tolist()

    def _simple_hash_vector(self, text: str, dim: int) -> List[float]:
        """简单哈希向量（备用）"""
        text = text.lower()
        vector = np.zeros(dim)

        # 使用多个哈希函数
        for i in range(5):
            hash_val = int(hashlib.md5(f"{text}{i}".encode()).hexdigest(), 16)
            idx = hash_val % dim
            vector[idx] += 1

        # 归一化
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector.tolist()


def get_pdf_text(pdf_docs):
    """从 PDF 文件中提取文本"""
    text = ""
    for pdf in pdf_docs:
        try:
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            st.error(f"❌ 读取 {pdf.name} 失败: {str(e)}")
    return text


def get_text_chunks(text):
    """将文本分割成小块"""
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=500,
        chunk_overlap=100,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks, pdf_names=None):
    """创建向量存储，保存文档来源信息"""
    embeddings = ImprovedEmbeddings()

    # 为每个文本块添加元数据
    metadatas = []
    for i, chunk in enumerate(text_chunks):
        doc_index = i % len(pdf_names) if pdf_names and len(pdf_names) > 0 else 0
        metadata = {
            'source': pdf_names[doc_index] if pdf_names else f'文档_{i // 10 + 1}',
            'chunk_id': i
        }
        metadatas.append(metadata)

    vectorstore = FAISS.from_texts(
        texts=text_chunks,
        embedding=embeddings,
        metadatas=metadatas
    )
    return vectorstore


def get_conversation_chain(vectorstore):
    """创建对话链"""
    llm = ChatOpenAI(
        model_name="deepseek-chat",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_api_base=os.getenv("OPENAI_API_BASE"),
        temperature=0.7
    )

    memory = ConversationBufferMemory(
        memory_key='chat_history',
        return_messages=True,
        output_key='answer'
    )

    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
        memory=memory,
        return_source_documents=True
    )
    return conversation_chain


def handle_userinput(user_question):
    """处理用户输入并显示答案和来源"""
    try:
        # 调用对话链
        response = st.session_state.conversation({'question': user_question})

        # 更新对话历史
        st.session_state.chat_history = response['chat_history']

        # 保存源文档
        source_documents = response.get('source_documents', [])

        # 显示对话历史
        for i, message in enumerate(st.session_state.chat_history):
            if i % 2 == 0:
                # 用户消息
                st.write(user_template.replace(
                    "{{MSG}}", message.content), unsafe_allow_html=True)
            else:
                # AI 回答
                st.write(bot_template.replace(
                    "{{MSG}}", message.content), unsafe_allow_html=True)

                # 显示答案来源（只在最新的回答下显示）
                if i == len(st.session_state.chat_history) - 1 and source_documents:
                    with st.expander("📚 查看答案来源", expanded=False):
                        for idx, doc in enumerate(source_documents):
                            st.markdown(f"**来源 {idx + 1}:**")

                            # 显示文档信息
                            source = doc.metadata.get('source', '未知文档')
                            st.markdown(f"- 📄 文档: `{source}`")

                            # 显示内容片段
                            content = doc.page_content[:300]
                            st.markdown(f"- 📝 内容片段:")
                            st.text_area(
                                f"片段 {idx + 1}",
                                content,
                                height=100,
                                key=f"source_{idx}_{st.session_state.qa_count}",
                                disabled=True
                            )

                            if idx < len(source_documents) - 1:
                                st.markdown("---")  # 🔧 替换 st.divider()

        # 更新问答计数
        if 'qa_count' in st.session_state:
            st.session_state.qa_count += 1

    except Exception as e:
        st.error(f"❌ 处理问题时出错：{str(e)}")
        st.info("💡 请检查：\n1. 文档是否已处理\n2. API Key 是否正确\n3. 网络连接是否正常")


def main():
    load_dotenv()
    st.set_page_config(
        page_title="DocuMind 智能文档问答",
        page_icon="📚",
        layout="wide"
    )
    st.write(css, unsafe_allow_html=True)

    # 初始化 session state
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    if "doc_count" not in st.session_state:
        st.session_state.doc_count = 0
    if "qa_count" not in st.session_state:
        st.session_state.qa_count = 0
    if "pdf_names" not in st.session_state:
        st.session_state.pdf_names = []

    # 主界面
    st.header("📚 DocuMind 智能文档问答")

    # 显示使用提示
    if not st.session_state.conversation:
        st.info("👈 请先在侧边栏上传 PDF 文件并点击「处理」按钮")

    user_question = st.text_input("💬 向您的文档提问：", placeholder="例如：这个文档的主要内容是什么？")

    if user_question:
        if st.session_state.conversation:
            handle_userinput(user_question)
        else:
            st.warning("⚠️ 请先上传并处理 PDF 文件！")

    # 侧边栏
    with st.sidebar:
        # 统计面板
        st.subheader("📊 使用统计")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📄 文档数量", st.session_state.doc_count)
        with col2:
            st.metric("💬 问答次数", st.session_state.qa_count)

        st.markdown("---")  # 🔧 替换 st.divider()

        # 文档上传
        st.subheader("📁 上传文档")
        pdf_docs = st.file_uploader(
            "上传 PDF 文件（支持多个）",
            accept_multiple_files=True,
            type=['pdf']
        )

        if st.button("🚀 处理文档", use_container_width=True):
            if pdf_docs:
                with st.spinner("⏳ 正在处理文档..."):
                    try:
                        # 获取 PDF 文本
                        raw_text = get_pdf_text(pdf_docs)

                        if not raw_text.strip():
                            st.error("❌ 无法从 PDF 中提取文本，请确保 PDF 不是扫描件！")
                            return

                        # 保存文档名称
                        st.session_state.pdf_names = [pdf.name for pdf in pdf_docs]

                        # 显示提取的文本长度
                        st.success(f"✅ 提取了 {len(raw_text):,} 个字符")

                        # 分割文本
                        text_chunks = get_text_chunks(raw_text)
                        st.success(f"✅ 分割成 {len(text_chunks)} 个文本块")

                        # 创建向量存储
                        vectorstore = get_vectorstore(text_chunks, st.session_state.pdf_names)

                        # 创建对话链
                        st.session_state.conversation = get_conversation_chain(vectorstore)

                        # 更新统计
                        st.session_state.doc_count = len(pdf_docs)
                        st.session_state.qa_count = 0

                        st.success("🎉 处理完成！现在可以提问了！")

                    except Exception as e:
                        st.error(f"❌ 处理失败：{str(e)}")
            else:
                st.warning("⚠️ 请先上传 PDF 文件！")

        st.markdown("---")  # 🔧 替换 st.divider()

        # 对话历史导出
        st.subheader("💾 导出对话")

        if st.session_state.chat_history and len(st.session_state.chat_history) > 0:
            # 生成 TXT 格式
            txt_content = "=" * 50 + "\n"
            txt_content += "DocuMind 对话历史\n"
            txt_content += "=" * 50 + "\n\n"

            for i, message in enumerate(st.session_state.chat_history):
                if i % 2 == 0:
                    txt_content += f"👤 用户：\n{message.content}\n\n"
                else:
                    txt_content += f"🤖 AI：\n{message.content}\n\n"
                txt_content += "-" * 50 + "\n\n"

            # TXT 下载按钮
            st.download_button(
                label="📄 导出为 TXT",
                data=txt_content,
                file_name=f"chat_history_{st.session_state.qa_count}.txt",
                mime="text/plain",
                use_container_width=True
            )

            # 生成 JSON 格式
            json_content = {
                "doc_count": st.session_state.doc_count,
                "qa_count": st.session_state.qa_count,
                "documents": st.session_state.pdf_names,
                "conversations": []
            }

            for i, message in enumerate(st.session_state.chat_history):
                json_content["conversations"].append({
                    "role": "user" if i % 2 == 0 else "assistant",
                    "content": message.content
                })

            # JSON 下载按钮
            st.download_button(
                label="📋 导出为 JSON",
                data=json.dumps(json_content, ensure_ascii=False, indent=2),
                file_name=f"chat_history_{st.session_state.qa_count}.json",
                mime="application/json",
                use_container_width=True
            )
        else:
            st.info("暂无对话历史")

        st.markdown("---")  # 🔧 替换 st.divider()

        # 关于信息
        with st.expander("ℹ️ 关于"):
            st.markdown("""
            **DocuMind v1.0**

            基于 DeepSeek + LangChain 的智能文档问答系统

            **改造亮点：**
            - ✅ 成本降低 95%（DeepSeek API）
            - ✅ 引用来源展示
            - ✅ 对话历史导出
            - ✅ 数据统计面板

            **作者：** 郑龙腾 (2025303007)  
            **课程：** CS599 企业级应用软件设计与开发  
            **指导教师：** 戚欣
            """)


if __name__ == '__main__':
    main()
