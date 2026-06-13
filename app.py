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
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=500,  # 减小块大小，提高精度
        chunk_overlap=100,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks):
    # 使用改进的 Embeddings
    embeddings = ImprovedEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI(
        model_name="deepseek-chat",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_api_base=os.getenv("OPENAI_API_BASE"),
        temperature=0.7
    )

    memory = ConversationBufferMemory(
        memory_key='chat_history',
        return_messages=True
    )

    # 增加检索的文档数量
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 6}),  # 检索更多相关段落
        memory=memory
    )
    return conversation_chain


def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)


def main():
    load_dotenv()
    st.set_page_config(page_title="Chat with multiple PDFs",
                       page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("Chat with multiple PDFs :books:")
    user_question = st.text_input("Ask a question about your documents:")
    if user_question:
        if st.session_state.conversation:
            handle_userinput(user_question)
        else:
            st.warning("请先上传并处理 PDF 文件！")

    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'",
            accept_multiple_files=True
        )
        if st.button("Process"):
            if pdf_docs:
                with st.spinner("Processing"):
                    # 获取 PDF 文本
                    raw_text = get_pdf_text(pdf_docs)

                    if not raw_text.strip():
                        st.error("无法从 PDF 中提取文本，请确保 PDF 不是扫描件！")
                        return

                    # 显示提取的文本长度
                    st.info(f"提取了 {len(raw_text)} 个字符")

                    # 分割文本
                    text_chunks = get_text_chunks(raw_text)
                    st.info(f"分割成 {len(text_chunks)} 个文本块")

                    # 创建向量存储
                    vectorstore = get_vectorstore(text_chunks)

                    # 创建对话链
                    st.session_state.conversation = get_conversation_chain(vectorstore)

                    st.success("Processing complete! 现在可以提问了！")
            else:
                st.warning("请先上传 PDF 文件！")


if __name__ == '__main__':
    main()
