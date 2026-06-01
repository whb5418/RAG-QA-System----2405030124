import streamlit as st
import os
import tempfile
from rag_chain import RAGQASystem
from knowledge_base import KnowledgeBase

st.set_page_config(
    page_title="RAG 智能问答系统",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_rag_system():
    return RAGQASystem(llm_model="deepseek-r1:7b")

def initialize_session_state():
    if "rag_system" not in st.session_state:
        st.session_state.rag_system = get_rag_system()
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "kb_count" not in st.session_state:
        st.session_state.kb_count = st.session_state.rag_system.get_knowledge_base_count()

def save_uploaded_file(uploaded_file):
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path

def main():
    initialize_session_state()

    st.markdown('<h1 class="main-header">🤖 RAG 智能问答系统</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">基于本地知识库的检索增强生成问答系统</p>', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("## 📚 知识库管理")

        st.markdown("### 上传文档")
        uploaded_files = st.file_uploader(
            "支持 PDF、DOCX、TXT 格式",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            help="选择要添加到知识库的文档"
        )

        if uploaded_files:
            if st.button("📁 添加到知识库", type="primary", use_container_width=True):
                with st.spinner("正在处理文档..."):
                    total_chunks = 0
                    for uploaded_file in uploaded_files:
                        file_path = save_uploaded_file(uploaded_file)
                        try:
                            chunks = st.session_state.rag_system.knowledge_base.add_single_document(file_path)
                            total_chunks += chunks
                            st.success(f"✅ {uploaded_file.name} 已添加 ({chunks} 块)")
                        except Exception as e:
                            st.error(f"❌ 处理 {uploaded_file.name} 时出错: {str(e)}")

                    if total_chunks > 0:
                        st.session_state.kb_count = st.session_state.rag_system.get_knowledge_base_count()
                        st.session_state.rag_system._create_qa_chain()

        st.markdown("### 知识库状态")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("文档块数", st.session_state.kb_count)
        with col2:
            doc_count = len([m for m in st.session_state.messages if m["role"] == "user"])
            st.metric("问答轮次", len(st.session_state.messages) // 2)

        if st.button("🗑️ 清空知识库", use_container_width=True):
            st.session_state.rag_system.clear_knowledge_base()
            st.session_state.kb_count = 0
            st.rerun()

        st.markdown("---")

        st.markdown("### ⚙️ 设置")
        model_name = st.selectbox(
            "选择模型",
            ["deepseek-r1:7b", "qwen2:7b", "llama3:8b"],
            index=0
        )

        temperature = st.slider(
            "温度参数",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="控制回答的随机性"
        )

        if st.button("🔄 重置对话", use_container_width=True):
            st.session_state.messages = []
            st.session_state.rag_system.reset_history()
            st.rerun()

    col_main, col_history = st.columns([3, 1])

    with col_main:
        st.markdown("### 💬 问答区域")

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "sources" in message and message["sources"]:
                    with st.expander("📄 参考文档"):
                        for i, source in enumerate(message["sources"], 1):
                            st.markdown(f"**来源 {i}:** {source['metadata'].get('source', 'Unknown')}")
                            st.text(source["content"][:300] + "...")

        if prompt := st.chat_input("请输入您的问题...", key="question_input"):
            with st.chat_message("user"):
                st.markdown(prompt)

            st.session_state.messages.append({
                "role": "user",
                "content": prompt
            })

            with st.chat_message("assistant"):
                with st.spinner("正在思考..."):
                    try:
                        result = st.session_state.rag_system.ask(prompt)

                        st.markdown(result["answer"])

                        sources = []
                        if result.get("source_documents"):
                            for doc in result["source_documents"]:
                                sources.append({
                                    "content": doc.page_content,
                                    "metadata": doc.metadata
                                })

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": result["answer"],
                            "sources": sources
                        })

                        if sources:
                            with st.expander("📄 查看参考文档"):
                                for i, source in enumerate(sources, 1):
                                    st.markdown(f"**来源 {i}:** {source['metadata'].get('source', 'Unknown')}")
                                    st.text(source["content"][:300] + "...")

                    except Exception as e:
                        error_msg = f"处理问题时出错: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })

    with col_history:
        st.markdown("### 📝 对话历史")

        if st.session_state.messages:
            for i in range(0, len(st.session_state.messages), 2):
                if i + 1 < len(st.session_state.messages):
                    user_msg = st.session_state.messages[i]["content"]
                    assistant_msg = st.session_state.messages[i + 1]["content"]

                    with st.container():
                        st.markdown(f"**Q:** {user_msg[:50]}...")
                        st.markdown(f"**A:** {assistant_msg[:50]}...")
                        st.markdown("---")
        else:
            st.info("暂无对话记录")

    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666; font-size: 0.9rem;">
            <p>RAG 智能问答系统 | 基于 Ollama + LangChain + Streamlit</p>
            <p>请确保 Ollama 服务已启动且模型已下载</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
