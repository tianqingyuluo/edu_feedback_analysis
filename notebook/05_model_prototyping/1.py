import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ================================
# 1. 读取数据
# ================================
df = pd.read_csv('../../data/intermediate/初步清洗_比赛数据_2.csv', sep=',', engine='python', encoding='utf-8')
# 去除制表符
df = df.map(lambda x: x.strip('\t') if isinstance(x, str) else x)

# ================================
# 2. 定义分类
# ================================
xxqk = ['课前预学','课堂参与','课后复习','延伸阅读','完成作业时间','自习时间','课外阅读时间','网络课程时间','实验科研时间',
        '社团活动时间','竞赛活动时间','其他学习时间','同学合作','参与科研团队','参与学科竞赛','学习同学方法','师生交流频度']

sz=['思政课总体满意度','思政课设置满意度','思政课内容满意度','思政课质量满意度','思政课效果满意度']

zy=['专业课知识融合','专业课解决问题能力','专业课交叉融合','专业课实践结合','专业课努力程度','专业课前沿内容',
    '传统讲授','课堂互动','案例讨论','小组合作']

ty=['体育教育满意度']
my=['美育教育满意度']
ld=['劳动教育满意度']

xy=['社团活动满意度','校园文化满意度','创新创业满意度','国际交流满意度','社会实践满意度']

sx=['实习内容满意度','实习时间满意度','实习场地满意度','实习指导满意度']

zwts=['问题解决能力提升','自主学习能力提升','合作能力提升','表达沟通能力提升','未来规划能力提升','人文底蕴提升',
      '科学精神提升','学会学习提升','健康生活提升','责任担当提升','实践创新提升','自我提升']

lsj=['教师履职满意度','关爱学生满意度','教学投入满意度','教师总体满意度','课程目标解释','激发学习兴趣',
     '课后辅导答疑','立德树人','创造性思考']

sxfw=['一站式服务','实训安全管理','教师参与活动','学术讲座多','心理健康满意度','职业规划满意度',
      '班主任工作满意度','学业指导满意度','资助工作满意度']

jctj=['教室设备满意度','实训室满意度','图书馆满意度','网络资源满意度','体育设施满意度','住宿条件满意度','学校整体满意度']

categories = {
    '学习情况': xxqk,
    '思政课': sz,
    '专业课': zy,
    '体育教育': ty,
    '美育教育': my,
    '劳动教育': ld,
    '校园生活': xy,
    '实习': sx,
    '自我提升': zwts,
    '老师教育': lsj,
    '学校服务': sxfw,
    '学校基础条件': jctj
}
# ================================
# 3. 计算每类的均值
# ================================
for cat, cols in categories.items():
    df[cat+'_均值'] = df[cols].mean(axis=1)

feature_cols = [c+'_均值' for c in categories.keys()]
features = df[feature_cols]

# 标准化
scaler = StandardScaler()
X_scaled = scaler.fit_transform(features)

# ================================
# 4. PCA降维
# ================================
# 保留 95% 方差，减少维度
pca = PCA(n_components=0.95, random_state=0)
X_pca = pca.fit_transform(X_scaled)
print("PCA后维度数:", X_pca.shape[1])

print("PCA 解释的累计方差比例:", np.sum(pca.explained_variance_ratio_))

# ================================
# 5. 直接聚类成 5 类
# ================================
kmeans = KMeans(n_clusters=5, random_state=0)
df['群体类别'] = kmeans.fit_predict(X_pca)

# ================================
# 6. 分析群体特征
# ================================
group_means = df.groupby('群体类别')[feature_cols].mean()
print("各群体平均满意度:")
print(group_means)

# ================================
# 7. 群体命名: 满意 → 较满意 → 一般 → 较不满意 → 不满意
# ================================
mean_scores = group_means.mean(axis=1).sort_values(ascending=False)
labels_order = ["满意","较满意","一般","较不满意","不满意"]

label_map = {}
for idx, group_id in enumerate(mean_scores.index):
    label_map[group_id] = labels_order[idx]

# 映射群体名称
df['群体名称'] = df['群体类别'].map(label_map)

print("群体命名结果:")
print(df[['群体类别','群体名称']].drop_duplicates())

# ================================
# 8. 可视化群体满意度
# ================================
group_means.index = group_means.index.map(label_map)
group_means.T.plot(kind='bar', figsize=(12,6))
plt.title('不同群体的平均满意度对比')
plt.ylabel('平均满意度')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


