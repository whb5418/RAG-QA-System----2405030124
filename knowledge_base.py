import os
import chromadb
from chromadb.config import Settings
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
import uuid

class KnowledgeBase:
    def __init__(self, persist_directory="chromadb_store"):
        self.persist_directory = persist_directory
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        self._init_vector_store()

    def _init_vector_store(self):
        if os.path.exists(self.persist_directory):
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            print(f"已加载现有知识库，包含 {self.vector_store._collection.count()} 个文档块")
        else:
            os.makedirs(self.persist_directory, exist_ok=True)
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            print("已创建新的知识库")

    def load_document(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
        elif ext == ".docx":
            loader = Docx2txtLoader(file_path)
        elif ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return [Document(page_content=content, metadata={"source": file_path})]
        else:
            raise ValueError(f"不支持的文件格式: {ext}")

        documents = loader.load()
        for doc in documents:
            doc.metadata["source"] = os.path.basename(file_path)
        return documents

    def load_documents_from_folder(self, folder_path):
        all_documents = []
        supported_extensions = [".pdf", ".docx", ".txt"]

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in supported_extensions:
                    file_path = os.path.join(root, file)
                    try:
                        docs = self.load_document(file_path)
                        all_documents.extend(docs)
                        print(f"已加载: {file} ({len(docs)} 页/段)")
                    except Exception as e:
                        print(f"加载 {file} 时出错: {str(e)}")

        return all_documents

    def split_documents(self, documents):
        chunks = self.text_splitter.split_documents(documents)
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = str(uuid.uuid4())
            chunk.metadata["chunk_index"] = i
        return chunks

    def add_documents(self, documents):
        chunks = self.split_documents(documents)
        texts = [chunk.page_content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]

        self.vector_store.add_texts(texts=texts, metadatas=metadatas)
        self.vector_store.persist()

        print(f"已添加 {len(chunks)} 个文档块到知识库")
        return len(chunks)

    def add_single_document(self, file_path):
        documents = self.load_document(file_path)
        return self.add_documents(documents)

    def search(self, query, k=3):
        if self.vector_store is None:
            print("知识库未初始化")
            return []

        results = self.vector_store.similarity_search_with_score(query, k=k)

        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score
            })

        return formatted_results

    def get_document_count(self):
        if self.vector_store is None:
            return 0
        return self.vector_store._collection.count()

    def clear(self):
        if self.vector_store is not None:
            self.vector_store.delete_collection()
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            print("知识库已清空")

    def get_retriever(self, search_kwargs={"k": 3}):
        if self.vector_store is None:
            raise ValueError("知识库未初始化")

        return self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs=search_kwargs
        )

if __name__ == "__main__":
    kb = KnowledgeBase()

    test_folder = "./test_documents"
    if os.path.exists(test_folder):
        docs = kb.load_documents_from_folder(test_folder)
        if docs:
            kb.add_documents(docs)
            print(f"\n知识库统计:")
            print(f"  - 文档块数量: {kb.get_document_count()}")

            print("\n检索测试:")
            results = kb.search("自然语言处理的基本概念")
            for i, r in enumerate(results):
                print(f"\n结果 {i+1} (相似度: {r['score']:.4f}):")
                print(f"  来源: {r['metadata'].get('source', 'Unknown')}")
                print(f"  内容: {r['content'][:200]}...")
    else:
        print(f"测试文件夹 '{test_folder}' 不存在，请添加文档后测试")