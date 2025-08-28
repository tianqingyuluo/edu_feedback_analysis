# 在文件开头添加
import matplotlib
import os

matplotlib.use('Agg')  # 设置非交互式后端

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans

# 设置中文字体和支持的字符
plt.rcParams['font.sans-serif'] = ['SimHei', 'SimSun', 'FangSong', 'KaiTi', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

# 加载数据
df = pd.read_csv("../../data/intermediate/初步清洗_比赛数据.csv")

# 清理数据中的制表符和空格
df = df.replace('\t', '', regex=True)
for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = df[col].astype(str).str.strip()

# 特征选择：5个核心维度的指标
feature_groups = {
    "学习行为": ["课前预学", "课堂参与", "课后复习", "自习时间", "课外阅读时间"],
    "学习互动": ["同学合作", "师生交流频度", "小组合作", "学习同学方法", "参与科研团队"],
    "课程评价": ["思政课总体满意度", "专业课知识融合", "专业课实践结合", "专业课前沿内容", "教师总体满意度"],
    "能力发展": ["问题解决能力提升", "自主学习能力提升", "合作能力提升", "表达沟通能力提升", "实践创新提升"],
    "资源满意度": ["教室设备满意度", "实训室满意度", "图书馆满意度", "网络资源满意度", "学校整体满意度"]
}

# 整合所有特征列
all_features = []
for group in feature_groups.values():
    all_features.extend(group)

# 检查所有特征是否在数据中存在
missing_features = [f for f in all_features if f not in df.columns]
if missing_features:
    print(f"警告：以下特征在数据中不存在: {missing_features}")
    # 过滤掉不存在的特征
    all_features = [f for f in all_features if f in df.columns]

# 归一化处理（0-100）
scaler = MinMaxScaler(feature_range=(0, 100))  # 添加这行定义scaler
df[all_features] = scaler.fit_transform(df[all_features].fillna(df[all_features].median()))

# 计算各维度平均得分
for dim, features in feature_groups.items():
    # 过滤掉不存在的特征
    existing_features = [f for f in features if f in df.columns]
    if existing_features:
        df[f"{dim}综合得分"] = df[existing_features].mean(axis=1)
    else:
        df[f"{dim}综合得分"] = 0  # 如果没有有效特征，设为0

# 最终雷达图使用5个维度得分
radar_dimensions = list(feature_groups.keys())

# 策略1：按学院划分（选择人数最多的4个学院）
college_counts = df["学院"].value_counts()
top_colleges = college_counts.head(4).index.tolist()
college_groups = {college: df[df["学院"] == college] for college in top_colleges}

# 策略2：按学习行为聚类
learning_behavior_features = [f for f in feature_groups["学习行为"] if f in df.columns]
if learning_behavior_features:
    kmeans = KMeans(n_clusters=3, random_state=42)
    cluster_labels = kmeans.fit_predict(df[learning_behavior_features].fillna(df[learning_behavior_features].median()))
    df["行为分组"] = cluster_labels
else:
    df["行为分组"] = 0

# 定义分组名称
behavior_names = {
    0: "互动主导型",
    1: "自主学习型",
    2: "均衡发展型"
}
df["行为分组名称"] = df["行为分组"].map(behavior_names)
behavior_groups = df.groupby("行为分组名称")

# 策略3：按能力发展分组
ability_features = [f for f in feature_groups["能力发展"] if f in df.columns]
if ability_features:
    df["能力发展分"] = df[ability_features].mean(axis=1)
else:
    df["能力发展分"] = 0

df["能力发展分组"] = pd.cut(df["能力发展分"],
                            bins=[-1, 30, 70, 100],
                            labels=["低发展组", "中发展组", "高发展组"])
development_groups = df.groupby("能力发展分组", observed=True)


def prepare_radar_data(groups_dict, group_label):
    radar_data = {
        "dimensions": radar_dimensions,
        "groups": [],
        "axis_max": 110
    }

    colors = plt.cm.Dark2.colors

    for i, (group_name, group_df) in enumerate(groups_dict.items()):
        if len(group_df) < 50:  # 最小样本量要求
            continue

        # 清理群体名称中的特殊字符
        clean_group_name = str(group_name).replace('\t', '').replace('\n', '').strip()

        # 计算各维度平均值
        dimension_columns = [f"{dim}综合得分" for dim in radar_dimensions]
        # 检查所有维度列是否存在
        existing_columns = [col for col in dimension_columns if col in group_df.columns]
        if len(existing_columns) != len(dimension_columns):
            print(f"警告：群体 {clean_group_name} 缺少 {len(dimension_columns) - len(existing_columns)} 个维度列")

        values = group_df[existing_columns].mean().tolist() if existing_columns else [0] * len(radar_dimensions)

        # 添加到数据结构
        radar_data["groups"].append({
            "name": f"{clean_group_name} (n={len(group_df)})",
            "values": values,
            "color": [float(c) for c in colors[i % len(colors)]],  # 转换为可JSON序列化的格式
            "linestyle": "-"
        })

    return radar_data


# 准备三种分组方案的雷达数据
college_radar = prepare_radar_data(college_groups, "学院")
behavior_radar = prepare_radar_data(dict(list(behavior_groups)), "行为分组")
development_radar = prepare_radar_data(dict(list(development_groups)), "能力分组")


def save_radar_json(radar_data, filename):
    """保存雷达图数据为JSON文件"""
    # 确保颜色值可以被JSON序列化
    for group in radar_data.get("groups", []):
        if isinstance(group.get("color"), np.ndarray):
            group["color"] = group["color"].tolist()
        elif isinstance(group.get("color"), tuple):
            group["color"] = list(group["color"])

    filepath = f"{filename}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(radar_data, f, indent=2, ensure_ascii=False)
    print(f"已保存 {filename} 的JSON数据到 {filepath}")


def plot_single_radar(radar_data, title, filename):
    if not radar_data["groups"]:
        print(f"警告：{title} 没有足够的数据来绘制雷达图")
        return

    dims = radar_data['dimensions']
    num_dims = len(dims)

    # 计算角度（不闭合）
    angles = np.linspace(0, 2 * np.pi, num_dims, endpoint=False).tolist()

    fig, ax = plt.subplots(figsize=(12, 12), subplot_kw={'polar': True})

    # 绘制每个群体
    for group in radar_data['groups']:
        vals = group['values']
        # 闭合值数组
        vals_closed = vals + vals[:1]
        angles_closed = angles + angles[:1]

        ax.plot(angles_closed, vals_closed, group['linestyle'],
                color=group['color'],
                linewidth=3,
                label=group['name'],
                marker='o',
                markersize=6)
        ax.fill(angles_closed, vals_closed, color=group['color'], alpha=0.15)

    # 美化设置
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles)
    ax.set_xticklabels(dims, fontsize=14, fontfamily='SimHei')
    ax.set_ylim(0, radar_data['axis_max'])
    ax.set_yticks(np.arange(0, 101, 20))
    ax.set_yticklabels([f"{i}" for i in np.arange(0, 101, 20)], fontsize=12, fontfamily='SimHei')

    # 设置网格
    ax.grid(True, alpha=0.3)

    plt.title(title, fontsize=20, pad=30, fontfamily='SimHei')
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=12, prop={'family': 'SimHei'})

    # 保存图片到当前目录（相对路径）
    image_path = f"{filename}.png"
    plt.savefig(image_path, dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()  # 关闭图形避免内存泄漏
    print(f"已生成 {image_path}")

    # 保存对应的JSON数据
    save_radar_json(radar_data, filename)


# 生成三种雷达图
plot_single_radar(college_radar, "主要学院多维特征对比", "college_comparison")
plot_single_radar(behavior_radar, "学习行为模式特征对比", "learning_behavior")
plot_single_radar(development_radar, "能力发展水平特征对比", "development_levels")


def plot_grouped_radar(radar_data_list, titles, group_labels):
    # 过滤掉空的雷达图数据
    valid_radars = [(data, title) for data, title in zip(radar_data_list, titles)
                    if data["groups"]]

    if not valid_radars:
        print("警告：没有足够的数据来绘制组合雷达图")
        return

    valid_radar_data, valid_titles = zip(*valid_radars)

    fig, axes = plt.subplots(1, len(valid_radar_data), figsize=(9 * len(valid_radar_data), 9),
                             subplot_kw={'polar': True})

    # 如果只有一个子图，axes不是数组
    if len(valid_radar_data) == 1:
        axes = [axes]

    for i, (ax, radar_data, title) in enumerate(zip(axes, valid_radar_data, valid_titles)):
        dims = radar_data['dimensions']
        num_vars = len(dims)

        # 计算角度（不闭合）
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

        # 绘制每个群体
        for group in radar_data['groups']:
            vals = group['values']
            # 确保值数组长度与维度数组长度一致
            if len(vals) != num_vars:
                print(f"警告: 群体 '{group['name']}' 的值数量({len(vals)})与维度数量({num_vars})不匹配")
                continue

            # 闭合值和角度数组
            vals_closed = vals + vals[:1]
            angles_closed = angles + angles[:1]

            ax.plot(angles_closed, vals_closed, group['linestyle'],
                    color=group['color'],
                    linewidth=2.5,
                    label=group['name'],
                    marker='o',
                    markersize=5)
            ax.fill(angles_closed, vals_closed, color=group['color'], alpha=0.1)

        # 设置图形属性
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_xticks(angles)
        ax.set_xticklabels(dims, fontsize=12, fontfamily='SimHei')
        ax.set_ylim(0, radar_data.get('axis_max', 100))
        ax.set_yticks(np.arange(0, 101, 20))
        if i == 0:  # 只在第一个子图显示y轴标签
            ax.set_yticklabels([f"{int(val)}" for val in np.arange(0, 101, 20)], fontsize=10, fontfamily='SimHei')
        else:
            ax.set_yticklabels([])

        # 设置网格
        ax.grid(True, alpha=0.3)
        ax.set_title(title, fontsize=16, pad=20, fontfamily='SimHei')

    # 创建共用图例
    if valid_radar_data:
        handles, labels = [], []
        for radar_data in valid_radar_data:
            for group in radar_data['groups']:
                handles.append(plt.Line2D([0], [0],
                                          color=group['color'],
                                          linewidth=3))
                labels.append(group['name'])

        fig.legend(handles, labels, loc='upper center',
                   bbox_to_anchor=(0.5, 0.02),
                   ncol=min(4, len(labels)),
                   fontsize=12,
                   prop={'family': 'SimHei'})

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15, top=0.9)

    # 保存组合雷达图到当前目录（相对路径）
    combined_image_path = "combined_radar_charts.png"
    plt.savefig(combined_image_path, dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()  # 关闭图形避免内存泄漏
    print(f"已生成 {combined_image_path}")


# 生成组合雷达图
plot_grouped_radar(
    [college_radar, behavior_radar, development_radar],
    ["学院特征对比", "学习行为模式", "能力发展水平"],
    ["学院", "行为模式", "发展水平"]
)


def create_radar_json(college_data, behavior_data, development_data):
    # 清理JSON数据中的特殊字符
    def clean_group_names(radar_data):
        if 'groups' in radar_data:
            for group in radar_data['groups']:
                if 'name' in group:
                    group['name'] = str(group['name']).replace('\t', '').replace('\n', '').strip()
                # 确保颜色值可以被JSON序列化
                if 'color' in group and isinstance(group['color'], (np.ndarray, tuple)):
                    group['color'] = list(group['color'])
        return radar_data

    clean_college_data = clean_group_names(college_data.copy())
    clean_behavior_data = clean_group_names(behavior_data.copy())
    clean_development_data = clean_group_names(development_data.copy())

    return {
        "metadata": {
            "data_source": "../../data/intermediate/初步清洗_比赛数据.csv",
            "generated_at": "2025-08-20",
            "normalization": "MinMaxScaler (0-100)",
            "dimensions_description": {
                "学习行为": "基于课前预学、课堂参与、课后复习等5个指标",
                "学习互动": "基于同学合作、师生交流等互动指标",
                "课程评价": "涵盖思政课、专业课及教师满意度",
                "能力发展": "包含问题解决、自主学习等能力提升指标",
                "资源满意度": "教室、实训室等硬件资源满意度"
            },
            "grouping_methods": {
                "college": "按学生数最多的4个学院分组",
                "behavior": "基于学习行为的K-Means聚类(3类)",
                "development": "按能力发展水平分组的3层级"
            }
        },
        "college_comparison": clean_college_data,
        "behavior_groups": clean_behavior_data,
        "development_groups": clean_development_data
    }


# 创建完整JSON结构
radar_json = create_radar_json(college_radar, behavior_radar, development_radar)

# 保存完整的JSON文件到当前目录（相对路径）
full_json_path = "educational_radar_data.json"
with open(full_json_path, "w", encoding="utf-8") as f:
    json.dump(radar_json, f, indent=2, ensure_ascii=False)

print("分析完成！已生成所有雷达图和JSON数据文件。")
