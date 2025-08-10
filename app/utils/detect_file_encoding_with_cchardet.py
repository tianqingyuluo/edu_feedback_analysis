import cchardet
import os


def detect_file_encoding_with_cchardet(file_path):
    """
    使用 cchardet 库检测文件的编码。

    Args:
        file_path (str): 要检测的文件的路径。

    Returns:
        tuple: (检测到的编码, 置信度) 或 (None, None) 如果无法检测。
    """
    if not os.path.exists(file_path):
        print(f"错误：文件 '{file_path}' 不存在。")
        return None, None

    try:
        # 1. 以二进制模式打开文件读取
        with open(file_path, 'rb') as f:
            raw_data = f.read()  # 读取文件的所有字节数据

        # 2. 使用 cchardet.detect() 检测编码
        # 这个函数会尝试分析字节数据并返回最可能的编码及其置信度
        result = cchardet.detect(raw_data)

        # result 是一个字典，例如：
        # {'encoding': 'utf-8', 'confidence': 0.99, 'language': 'Chinese'}

        detected_encoding = result.get('encoding')
        confidence = result.get('confidence')

        return detected_encoding, confidence

    except Exception as e:
        print(f"检测文件 '{file_path}' 编码时发生错误：{e}")
        return None, None


# 测试
def main():
    # 准备一个测试文件 (假设文件不存在)
    test_file_utf8 = 'test_utf8.txt'
    test_file_gbk = 'test_gbk.txt'

    # 创建一个 UTF-8 编码的文件
    try:
        with open(test_file_utf8, 'w', encoding='utf-8') as f:
            f.write("这是一个使用 UTF-8 编码的大文件，包含许多字符。\n")
            f.write("例如：你好，世界！😊\n")
    except Exception as e:
        print(f"创建 UTF-8 测试文件时出错: {e}")

    # 创建一个 GBK 编码的文件
    try:
        with open(test_file_gbk, 'w', encoding='gbk') as f:
            f.write("这是一个使用 GBK 编码的文件。\n")
            f.write("比如：你好，世界！\n")
    except Exception as e:
        print(f"创建 GBK 测试文件时出错: {e}")

    # 检测 UTF-8 文件
    print(f"--- 检测文件: {test_file_utf8} ---")
    encoding_utf8, confidence_utf8 = detect_file_encoding_with_cchardet(test_file_utf8)

    if encoding_utf8:
        print(f"  检测到的编码: {encoding_utf8}")
        print(f"  置信度: {confidence_utf8:.2f}")  # 保留两位小数显示置信度

        # 如何实际使用检测到的编码读取文件
        if confidence_utf8 > 0.8:  # 设定一个置信度阈值
            try:
                with open(test_file_utf8, 'r', encoding=encoding_utf8) as f:
                    content = f.read()
                print(f"  成功以 '{encoding_utf8}' 编码读取文件内容 (前 50 字符): {content[:50]}...")
            except UnicodeDecodeError:
                print(f"  警告：使用检测到的 '{encoding_utf8}' 编码读取文件失败，可能检测有误。")
            except Exception as e:
                print(f"  读取文件时发生未知错误: {e}")
    else:
        print("  无法检测到文件的编码。")

    print("\n" + "=" * 30 + "\n")

    # 检测 GBK 文件
    print(f"--- 检测文件: {test_file_gbk} ---")
    encoding_gbk, confidence_gbk = detect_file_encoding_with_cchardet(test_file_gbk)

    if encoding_gbk:
        print(f"  检测到的编码: {encoding_gbk}")
        print(f"  置信度: {confidence_gbk:.2f}")

        # 如何实际使用检测到的编码读取文件
        if confidence_gbk > 0.8:
            try:
                with open(test_file_gbk, 'r', encoding=encoding_gbk) as f:
                    content = f.read()
                print(f"  成功以 '{encoding_gbk}' 编码读取文件内容 (前 50 字符): {content[:50]}...")
            except UnicodeDecodeError:
                print(f"  警告：使用检测到的 '{encoding_gbk}' 编码读取文件失败，可能检测有误。")
            except Exception as e:
                print(f"  读取文件时发生未知错误: {e}")
    else:
        print("  无法检测到文件的编码。")

    # 清理测试文件
    if os.path.exists(test_file_utf8): os.remove(test_file_utf8)
    if os.path.exists(test_file_gbk): os.remove(test_file_gbk)

if __name__ == "__main__":
    main()
