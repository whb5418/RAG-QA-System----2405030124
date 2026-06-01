import requests
import json

def test_ollama_connection():
    base_url = "http://localhost:11434"

    try:
        response = requests.get(f"{base_url}/api/tags")
        if response.status_code == 200:
            models = response.json()
            print("=" * 50)
            print("Ollama 连接成功!")
            print("=" * 50)
            print("\n已下载的模型列表:")
            for model in models.get("models", []):
                print(f"  - {model.get('name', 'Unknown')}")
            return True
        else:
            print(f"连接失败，状态码: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到 Ollama 服务")
        print("请确保 Ollama 已在后台运行")
        return False
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return False

def test_generate(model_name="deepseek-r1:7b"):
    base_url = "http://localhost:11434"

    prompt = "请用一句话介绍自己"

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }

    try:
        print(f"\n正在测试生成功能 (模型: {model_name})...")
        response = requests.post(
            f"{base_url}/api/generate",
            json=payload,
            timeout=120
        )

        if response.status_code == 200:
            result = response.json()
            print("\n" + "=" * 50)
            print("生成测试成功!")
            print("=" * 50)
            print(f"\n问题: {prompt}")
            print(f"\n回答: {result.get('response', 'No response')}")
            return True
        else:
            print(f"生成失败，状态码: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("错误: 请求超时，模型可能正在加载中")
        return False
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return False

def test_embeddings():
    base_url = "http://localhost:11434"

    text = "这是一个测试文本"

    payload = {
        "model": "nomic-embed-text",
        "prompt": text
    }

    try:
        print("\n正在测试嵌入功能 (模型: nomic-embed-text)...")
        response = requests.post(
            f"{base_url}/api/embeddings",
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            embedding = result.get("embedding", [])
            print("\n" + "=" * 50)
            print("嵌入测试成功!")
            print("=" * 50)
            print(f"\n文本: {text}")
            print(f"嵌入维度: {len(embedding)}")
            print(f"前5个值: {embedding[:5]}")
            return True
        else:
            print(f"嵌入失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("RAG 智能问答系统 - Ollama 连接测试")
    print("=" * 50)

    if test_ollama_connection():
        test_generate()
        test_embeddings()

    print("\n" + "=" * 50)
    print("测试完成!")
    print("=" * 50)
