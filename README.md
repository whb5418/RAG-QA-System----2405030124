# RAG 智能问答系统

基于本地知识库的检索增强生成(RAG)智能问答系统，使用 Ollama 本地大模型、LangChain 框架和 Streamlit 构建。

## 项目简介

本项目实现了一个能够"学习"本地文档并回答相关问题的智能问答系统。用户可以上传 PDF、DOCX、TXT 格式的文档构建知识库，系统基于检索增强生成技术提供准确的问答服务。

## 环境要求与安装步骤

### 系统要求

- Windows 10/11
- Python 3.9+
- 至少 8GB RAM（推荐 16GB+）
- 至少 10GB 可用磁盘空间

### 1. 安装 Ollama

访问 [Ollama 官网](https://ollama.com/) 下载并安装 Ollama。

安装完成后，在命令行中下载所需模型：

```bash
# 下载 DeepSeek-R1 7B 模型（推荐）
ollama pull deepseek-r1:7b

# 或者下载 Qwen2 7B 模型
ollama pull qwen2:7b

# 下载嵌入模型
ollama pull nomic-embed-text
```

验证安装：

```bash
ollama list
```

### 2. 创建 Python 虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 运行测试脚本

```bash
python test_ollama.py
```

确保 Ollama 服务正在运行，测试脚本应能成功连接并返回模型列表。

## 使用说明

### 启动 Web 应用

```bash
streamlit run app.py
```

应用默认在浏览器中打开 `http://localhost:8501`。

### 上传文档

1. 在左侧边栏的"上传文档"区域，点击文件选择器
2. 选择 PDF、DOCX 或 TXT 格式的文档（支持多选）
3. 点击"添加到知识库"按钮
4. 等待系统处理完成（文档会被分块并向量化）

### 提问

1. 在底部的文本输入框中输入问题
2. 点击"提问"按钮或按 Enter 键
3. 等待系统检索相关文档并生成回答
4. 可以展开"查看参考文档"查看答案的来源

### 查看知识库状态

左侧边栏显示：
- 文档块数量
- 问答轮次

### 清空知识库

点击"清空知识库"按钮可重置知识库。

### 重置对话

点击"重置对话"按钮可清除对话历史，但保留知识库。

## 关键技术点说明

### RAG 流程

1. **文档加载**: 支持 PDF、DOCX、TXT 格式文档
2. **文本分块**: 使用 RecursiveCharacterTextSplitter，chunk_size=1000，chunk_overlap=200
3. **向量化**: 使用 Ollama 内置的 nomic-embed-text 模型
4. **向量存储**: 使用 Chroma 向量数据库
5. **相似性检索**: 基于余弦相似度检索最相关的 3 个文档块
6. **生成**: 使用 ConversationalRetrievalChain 连接检索器和 LLM

### 所用模型

- **LLM**: DeepSeek-R1:7b / Qwen2:7b
- **Embedding**: nomic-embed-text

### 架构设计

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Streamlit  │───>│  RAG System  │───>│   Ollama    │
│   Web UI    │    │  (LangChain) │    │  Local LLM  │
└─────────────┘    └──────────────┘    └─────────────┘
                          │
                          v
                   ┌──────────────┐
                   │    Chroma    │
                   │ Vector Store │
                   └──────────────┘
```

## 项目结构

```
RAG-QA-System/
├── app.py                 # Streamlit Web 应用主文件
├── rag_chain.py           # RAG 问答链核心逻辑
├── knowledge_base.py      # 知识库管理模块
├── test_ollama.py         # Ollama 连接测试脚本
├── build_exe.py           # PyInstaller 打包脚本
├── requirements.txt       # Python 依赖列表
├── README.md              # 项目说明文档
├── .gitignore             # Git 忽略文件配置
└── AI_usage_log.md        # AI 使用日志
```

## 项目效果截图

### 1. 系统主界面
![主界面](screenshots/main_interface.png)

### 2. 文档上传与知识库构建
![文档上传](screenshots/document_upload.png)

### 3. 问答示例
![问答示例](screenshots/qa_example.png)

## GitHub 仓库管理

### 初始化 Git 仓库

```bash
# 初始化仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: RAG 智能问答系统"
```

### 推送到 GitHub

1. 在 GitHub 创建新仓库，命名格式为：`RAG-QA-System-姓名-学号`
2. 关联远程仓库并推送：

```bash
# 添加远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/你的用户名/RAG-QA-System-姓名-学号.git

# 推送代码
git branch -M main
git push -u origin main
```

## 已知问题与改进方向

### 已知问题

1. 首次加载模型时可能需要较长时间
2. 大文件处理可能占用较多内存
3. 在低配置电脑上响应速度较慢

### 改进方向

1. 增加更多文档格式支持（如 Markdown、HTML）
2. 添加批量上传功能
3. 实现夜间模式
4. 增加导出问答记录功能
5. 优化大文档处理性能
6. 添加用户认证功能

## AI 使用日志

详见 [AI_usage_log.md](AI_usage_log.md)
