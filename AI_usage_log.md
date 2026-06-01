# AI 使用日志

本项目在开发过程中使用了 Trae AI 编程辅助工具。以下记录了向 AI 提问的问题、获得的建议以及代码修改情况。

## AI 使用记录

### 1. 项目架构设计

**问题**: 如何设计一个基于 Ollama + LangChain + Streamlit 的 RAG 系统的架构？

**AI 回答摘要**:
- 使用模块化设计，将知识库管理、RAG 链、Web 界面分离
- 使用 session_state 管理 Streamlit 状态
- 使用 ConversationalRetrievalChain 连接检索器和 LLM

**修改情况**: 采纳了分层架构设计，将代码拆分为 knowledge_base.py、rag_chain.py 和 app.py

### 2. 向量数据库选择

**问题**: Chroma 和 FAISS 哪个更适合本地部署的 RAG 系统？

**AI 回答摘要**:
- Chroma 是专门为 LLM 应用设计的向量数据库
- Chroma 有更好的 LangChain 集成
- Chroma 支持持久化存储

**修改情况**: 选择使用 Chroma 作为向量数据库

### 3. 文档分块策略

**问题**: 如何设置文本分块的 chunk_size 和 chunk_overlap？

**AI 回答摘要**:
- chunk_size=1000 是平衡信息完整性和相关性的较好选择
- chunk_overlap=200 可以避免上下文丢失
- 可根据实际文档特点调整

**修改情况**: 采用 chunk_size=1000, chunk_overlap=200 的配置

### 4. Streamlit 会话状态管理

**问题**: 如何在 Streamlit 中实现多轮对话的上下文记忆？

**AI 回答摘要**:
- 使用 st.session_state 存储对话历史
- 在 RAG 链中传入 chat_history
- ConversationalRetrievalChain 原生支持对话历史

**修改情况**: 在 rag_chain.py 中实现了 chat_history 管理

### 5. 系统提示词设计

**问题**: 如何设计 RAG 系统的提示词以避免幻觉？

**AI 回答摘要**:
- 明确要求模型只基于提供的文档回答
- 设置拒答规则：当文档无相关信息时明确说明
- 添加引用来源的要求

**修改情况**: 在 rag_chain.py 中实现了包含拒答规则的提示词模板

### 6. 错误处理

**问题**: 如何处理 Ollama 服务未启动或模型未下载的情况？

**AI 回答摘要**:
- 在初始化时检查 Ollama 连接
- 使用 try-except 捕获异常
- 向用户显示友好的错误提示

**修改情况**: 在 app.py 中添加了异常处理和错误提示

### 7. PyInstaller 打包问题

**问题**: 如何正确打包 Streamlit 应用为 exe？

**AI 回答摘要**:
- 使用 --onefile --windowed 参数
- 添加必要的 hidden-import
- 使用 --collect-all 收集所有依赖

**修改情况**: 创建了 build_exe.py 打包脚本

## 注意事项

1. AI 生成的代码需要理解后再使用，不能直接复制粘贴
2. 某些 AI 建议可能不适用于本项目，需要根据实际情况调整
3. 保持批判性思维，验证 AI 提供的信息

## 代码来源说明

以下代码部分由 AI 生成并经过修改：

1. **knowledge_base.py** - AI 协助设计类结构和 LangChain 集成方式
2. **rag_chain.py** - AI 提供了 RAG 链的初始化和提示词模板
3. **app.py** - AI 协助设计 Streamlit UI 布局和状态管理
4. **test_ollama.py** - AI 提供了 Ollama API 测试的基础代码

## 调试记录

### 问题 1: Chroma 持久化失败

**现象**: 关闭程序后重新加载知识库失败

**原因**: Chroma 对象未被正确持久化

**解决方案**: 确保调用 persist() 方法并正确初始化

### 问题 2: Streamlit 状态丢失

**现象**: 页面刷新后对话历史丢失

**解决方案**: 使用 @st.cache_resource 装饰器缓存 RAG 系统实例

### 问题 3: 大文件处理超时

**现象**: 处理大型 PDF 文件时请求超时

**解决方案**: 增加超时时间，优化分块策略
