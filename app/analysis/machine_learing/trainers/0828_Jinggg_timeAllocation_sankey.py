import pandas as pd
import json
import os


def process_student_time_sankey_to_single_file(csv_file_path, output_filename="combined_sankey_data.json"):
    """
    处理学生时间分配数据，按专业和年级分组生成桑基图数据
    并将所有数据合并到同一个JSON文件中（与脚本同一目录）
    """

    # 获取当前脚本所在目录的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 构建完整的输出文件路径（与脚本同级）
    output_filepath = os.path.join(script_dir, output_filename)

    # 读取数据
    df = pd.read_csv(csv_file_path)

    # 定义时间分配字段映射
    time_columns_mapping = {
        '完成作业时间': '作业时间',
        '自习时间': '自习时间',
        '课外阅读时间': '课外阅读',
        '网络课程时间': '网络课程',
        '实验科研时间': '实验科研',
        '社团活动时间': '社团活动',
        '竞赛活动时间': '学科竞赛',
        '其他学习时间': '其他学习'
    }

    # 按专业和年级分组
    grouped = df.groupby(['专业', '年级'])

    # 创建存储所有分组数据的字典
    all_sankey_data = {
        "metadata": {
            "生成时间": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "总分组数": len(grouped),
            "数据来源": csv_file_path
        },
        "sankey_groups": {}
    }

    # 处理每个分组
    for (major, grade), group in grouped:
        # 计算各时间字段的平均值
        time_means = {}
        for col_en, col_cn in time_columns_mapping.items():
            if col_en in group.columns:
                time_means[col_en] = group[col_en].mean()

        # 构建桑基图数据结构
        nodes = [
            {"name": "总学习时间"},
            {"name": "作业时间"},
            {"name": "自习时间"},
            {"name": "课外阅读"},
            {"name": "网络课程"},
            {"name": "实验科研"},
            {"name": "社团活动"},
            {"name": "学科竞赛"},
            {"name": "其他学习"}
        ]

        # 构建链接
        links = [
            {"source": 0, "target": 1, "value": time_means.get('完成作业时间', 0)},
            {"source": 0, "target": 2, "value": time_means.get('自习时间', 0)},
            {"source": 0, "target": 3, "value": time_means.get('课外阅读时间', 0)},
            {"source": 0, "target": 4, "value": time_means.get('网络课程时间', 0)},
            {"source": 0, "target": 5, "value": time_means.get('实验科研时间', 0)},
            {"source": 0, "target": 6, "value": time_means.get('社团活动时间', 0)},
            {"source": 0, "target": 7, "value": time_means.get('竞赛活动时间', 0)},
            {"source": 0, "target": 8, "value": time_means.get('其他学习时间', 0)}
        ]

        # 计算总学习时间
        total_time = sum(link['value'] for link in links)

        # 创建分组键名
        group_key = f"{major}_{grade}"

        # 存储分组数据[5](@ref)
        all_sankey_data["sankey_groups"][group_key] = {
            "nodes": nodes,
            "links": links,
            "metadata": {
                "专业": major,
                "年级": grade,
                "样本数量": len(group),
                "总学习时间": total_time,
                "各活动时间明细": {
                    "作业时间": time_means.get('完成作业时间', 0),
                    "自习时间": time_means.get('自习时间', 0),
                    "课外阅读": time_means.get('课外阅读时间', 0),
                    "网络课程": time_means.get('网络课程时间', 0),
                    "实验科研": time_means.get('实验科研时间', 0),
                    "社团活动": time_means.get('社团活动时间', 0),
                    "学科竞赛": time_means.get('竞赛活动时间', 0),
                    "其他学习": time_means.get('其他学习时间', 0)
                }
            }
        }

    # 保存到单个JSON文件[7,9](@ref)
    with open(output_filepath, 'w', encoding='utf-8') as f:
        json.dump(all_sankey_data, f, ensure_ascii=False, indent=2)

    return all_sankey_data, output_filepath


if __name__ == "__main__":
    # 配置你的CSV文件路径
    csv_path = '../../../../data/intermediate/初步清洗_比赛数据.csv'

    # 处理数据并生成合并的桑基图JSON
    try:
        result_data, output_path = process_student_time_sankey_to_single_file(csv_path)

        # 打印处理结果摘要
        print("✅ 桑基图数据已保存到JSON文件！")
        print(f"文件位置: {output_path}")
        print(f"总分组数: {result_data['metadata']['总分组数']}")

        print("\n各分组摘要:")
        for group_key, group_data in result_data["sankey_groups"].items():
            meta = group_data["metadata"]
            print(f"   - {meta['专业']} {meta['年级']}: "
                  f"{meta['样本数量']}个样本, "
                  f"总学习时间: {meta['总学习时间']:.1f}小时/周")

    except Exception as e:
        print(f"❌ 处理过程中出错: {str(e)}")