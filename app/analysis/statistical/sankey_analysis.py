import pandas as pd
import json


def process_sankey_data(df):
    """
    处理学生时间分配数据，生成桑基图数据
    
    Args:
        df: 输入的DataFrame
    
    Returns:
        dict: 桑基图数据字典
    """
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
    
    # 检查必需的时间列是否存在
    required_time_cols = list(time_columns_mapping.keys())
    existing_time_cols = [col for col in required_time_cols if col in df.columns]
    
    if not existing_time_cols:
        raise ValueError("数据中未找到任何时间分配相关列")
    
    # 按专业和年级分组
    if '专业' not in df.columns or '年级' not in df.columns:
        raise ValueError("数据中缺少'专业'或'年级'列")
        
    grouped = df.groupby(['专业', '年级'])
    
    # 创建存储所有分组数据的字典
    all_sankey_data = {
        "metadata": {
            "生成时间": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "总分组数": len(grouped),
            "数据来源": "DataFrame input"
        },
        "sankey_groups": {}
    }
    
    # 处理每个分组
    for (major, grade), group in grouped:
        # 计算各时间字段的平均值
        time_means = {}
        for col_en, col_cn in time_columns_mapping.items():
            if col_en in group.columns:
                time_means[col_en] = float(group[col_en].mean())
        
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
        total_time = float(sum(link['value'] for link in links))
        
        # 创建分组键名
        group_key = f"{major}_{grade}"
        
        # 存储分组数据
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
    
    return all_sankey_data


def create_sankey_echarts_json(df):
    """
    创建桑基图ECharts JSON数据
    
    Args:
        df: 输入的DataFrame
    
    Returns:
        dict: 适合ECharts桑基图的JSON数据结构
    """
    # 处理数据
    sankey_data = process_sankey_data(df)
    
    return sankey_data