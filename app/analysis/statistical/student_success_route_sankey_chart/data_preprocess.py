import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def process_data(df) -> pd.DataFrame:
    """
    处理学生成功路径桑基图所需的数据

    该函数对原始数据进行预处理，包括：
    1. 提取满意度相关列
    2. 对时间变量进行标准化
    3. 根据不同维度计算平均满意度得分

    :param df: 原始数据DataFrame，包含学生反馈数据
    :return: 处理后的DataFrame，包含原始数据和新增的聚合列
    """

    time_columns = [
        '自习时间',
        '网络课程时间',
        '实验科研时间',
        '竞赛活动时间',
        '其他学习时间'
    ]

    # 标准化时间变量
    scaler = MinMaxScaler()
    df[time_columns] = scaler.fit_transform(df[time_columns])
    # 初始资源感知（输入）
    resource_aware_list = [
        '教室设备满意度',
        '实训室满意度',
        '图书馆满意度',
        '网络资源满意度',
        '体育设施满意度',
        '住宿条件满意度'
    ]
    # 学习投入度隐变量（过程）
    learning_engagement_list = [
        '课前预学',
        '课堂参与',
        '课后复习',
        '延伸阅读',
        '自习时间',
        # '网络课程时间',
        '实验科研时间',
        '竞赛活动时间',
        # '其他学习时间'
    ]
    # 师生关系（过程）
    teacher_student_relationship_list = [
        '师德师风满意度',
        '关爱学生满意度',
        '教学投入满意度',
        '班主任工作满意度',
        '学业指导满意度'
    ]
    # 专业课体验（过程）
    major_course_experience_list = [
        '专业课知识融合',
        '专业课解决问题能力',
        '专业课交叉融合',
        '专业课实践结合',
        '专业课努力程度',
        '专业课前沿内容'
    ]
    # 体美劳课体验（过程）
    phy_art_labour_course_experience_list = [
        '体育教育满意度',
        '美育教育满意度',
        '劳动教育满意度'
    ]
    # 综合满意度（输出）
    overall_satisfaction_list = [
        '学校整体满意度',
        '思政课总体满意度',
        '实习内容满意度',
        '教师总体满意度'
    ]
    # 计算平均数
    df['初始资源感知'] = df[resource_aware_list].mean(axis=1)
    df['学习投入度'] = df[learning_engagement_list].mean(axis=1)
    df['师生关系'] = df[teacher_student_relationship_list].mean(axis=1)
    df['专业课体验'] = df[major_course_experience_list].mean(axis=1)
    df['综合满意度'] = df[overall_satisfaction_list].mean(axis=1)
    df['体美劳体验'] = df[phy_art_labour_course_experience_list].mean(axis=1)

    return df



