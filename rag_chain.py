import os
from langchain_ollama import ChatOllama
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from knowledge_base import KnowledgeBase

DEFAULT_SYSTEM_PROMPT = """你是一个专业的智能问答助手，专门基于提供的参考文档回答用户问题。

重要规则：
1. 如果提供的参考文档中包含与问题相关的信息，请基于这些信息进行回答
2. 如果参考文档中没有包含与问题相关的内容，请明确回答："文档中未找到相关答案"
3. 请在回答时适当引用参考文档的内容，并在最后说明答案的来源
4. 回答要准确、简洁、有条理
5. 如果需要使用外部知识来补充回答，请明确说明这是基于外部知识而非文档内容

参考文档：
{context}

当前问题：{question}

回答："""

DEFAULT_QUESTION_PROMPT = """请根据以下参考文档回答问题。如果文档中没有相关信息，请明确说明。

参考文档：
{context}

问题：{question}

回答："""

class RAGQASystem:
    def __init__(
        self,
        llm_model="deepseek-r1:7b",
        temperature=0.7,
        system_prompt=None,
        question_prompt=None,
        persist_directory="chromadb_store"
    ):
        self.llm_model = llm_model
        self.temperature = temperature
        self.system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
        self.question_prompt = question_prompt or DEFAULT_QUESTION_PROMPT

        self.llm = ChatOllama(
            model=llm_model,
            temperature=temperature,
            base_url="http://localhost:11434"
        )

        self.knowledge_base = KnowledgeBase(persist_directory=persist_directory)

        self.qa_chain = None
        self.chat_history = []

    def _create_qa_chain(self):
        if self.knowledge_base.get_document_count() == 0:
            print("警告: 知识库为空，请先添加文档")

        retriever = self.knowledge_base.get_retriever(search_kwargs={"k": 3})

        combine_docs_prompt = PromptTemplate(
            template=self.question_prompt,
            input_variables=["context", "question"]
        )

        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            combine_docs_chain_kwargs={"prompt": combine_docs_prompt},
            memory=None,
            return_source_documents=True,
            verbose=False
        )

    def ask(self, question, use_history=True):
        if self.qa_chain is None:
            self._create_qa_chain()

        if use_history:
            result = self.qa_chain({
                "question": question,
                "chat_history": self.chat_history
            })
            self.chat_history.append((question, result["answer"]))
        else:
            result = self.qa_chain({
                "question": question,
                "chat_history": []
            })

        return {
            "answer": result["answer"],
            "source_documents": result.get("source_documents", []),
            "chat_history": self.chat_history if use_history else []
        }

    def reset_history(self):
        self.chat_history = []
        self._create_qa_chain()

    def add_documents(self, documents):
        self.knowledge_base.add_documents(documents)
        self._create_qa_chain()

    def add_documents_from_folder(self, folder_path):
        docs = self.knowledge_base.load_documents_from_folder(folder_path)
        self.add_documents(docs)
        return len(docs)

    def get_knowledge_base_count(self):
        return self.knowledge_base.get_document_count()

    def clear_knowledge_base(self):
        self.knowledge_base.clear()
        self._create_qa_chain()

def test_rag_system():
    print("\n" + "=" * 60)
    print("RAG 智能问答系统测试")
    print("=" * 60)

    rag = RAGQASystem(llm_model="deepseek-r1:7b")

    test_folder = "./test_documents"
    if os.path.exists(test_folder):
        print(f"\n从 {test_folder} 加载文档...")
        rag.add_documents_from_folder(test_folder)
        print(f"知识库文档块数量: {rag.get_knowledge_base_count()}")
    else:
        print(f"\n测试文件夹不存在，跳过文档加载")

    print("\n" + "-" * 40)
    print("测试问答 (与文档相关的问题):")
    print("-" * 40)

    test_questions = [
        "什么是自然语言处理？",
        "深度学习在NLP中有哪些应用？",
        "Transformer模型的基本原理是什么？",
        "什么是词嵌入？",
        "请解释注意力机制的工作原理"
    ]

    for i, q in enumerate(test_questions):
        print(f"\n问题 {i+1}: {q}")
        print("-" * 40)
        result = rag.ask(q)
        print(f"回答: {result['answer'][:500]}...")
        if result['source_documents']:
            print(f"参考文档数: {len(result['source_documents'])}")

    print("\n" + "-" * 40)
    print("测试问答 (与文档无关的问题):")
    print("-" * 40)

    unrelated_questions = [
        "今天的天气怎么样？",
        "谁赢得了2024年世界杯？"
    ]

    for i, q in enumerate(unrelated_questions):
        print(f"\n问题 {i+1}: {q}")
        print("-" * 40)
        result = rag.ask(q)
        print(f"回答: {result['answer'][:500]}...")

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    test_rag_system()
