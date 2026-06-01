import os
import subprocess
import sys
import shutil

def build_exe():
    print("=" * 60)
    print("RAG 智能问答系统 - PyInstaller 打包工具")
    print("=" * 60)

    if not shutil.which("pyinstaller"):
        print("错误: PyInstaller 未安装")
        print("请运行: pip install pyinstaller")
        return False

    print("\n正在清理之前的构建文件...")

    build_dirs = ["build", "dist"]
    for dir_name in build_dirs:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  已删除 {dir_name}/")

    print("\n正在打包应用程序...")

    pyinstaller_args = [
        "pyinstaller",
        "--name=RAG-QA-System",
        "--onefile",
        "--windowed",
        "--icon=NONE",
        "--add-data=.;.",
        "--hidden-import=streamlit",
        "--hidden-import=langchain",
        "--hidden-import=langchain_community",
        "--hidden-import=chromadb",
        "--hidden-import=Pypdf2",
        "--hidden-import=docx",
        "--hidden-import=tiktoken",
        "--hidden-import=requests",
        "--hidden-import=numpy",
        "--hidden-import=ollama",
        "--collect-all=streamlit",
        "--collect-all=langchain",
        "--collect-all=langchain_community",
        "app.py"
    ]

    try:
        result = subprocess.run(
            pyinstaller_args,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("\n✅ 打包成功!")
            print(f"exe 文件位置: dist/RAG-QA-System.exe")
            print("\n使用说明:")
            print("1. 将 dist/RAG-QA-System.exe 复制到目标电脑")
            print("2. 确保目标电脑已安装 Ollama 并下载了对应模型")
            print("3. 双击运行 exe 文件启动应用")
        else:
            print(f"\n❌ 打包失败!")
            print("错误输出:")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"\n❌ 打包过程中出错: {str(e)}")
        return False

    return True

if __name__ == "__main__":
    build_exe()
