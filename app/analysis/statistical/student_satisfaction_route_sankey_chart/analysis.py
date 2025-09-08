import pandas as pd
from semopy import Model

from app.analysis.statistical.student_satisfaction_route_sankey_chart import process_data

def extract_paths_to_target(df, target='综合满意度'):
    # 1. 找出直接影响目标的变量
    direct = df[(df['lval'] == target) & (df['op'] == '~')]

    # 2. 递归找出上游变量
    upstream_vars = set(direct['rval'].tolist())

    all_vars = set()
    all_links = []

    def find_upstream(var):
        all_vars.add(var)
        parents = df[(df['lval'] == var) & (df['op'] == '~')]
        for _, row in parents.iterrows():
            source = row['rval']
            all_links.append({
                'source': source,
                'target': var,
                'value': row['Est. Std']
            })
            if source not in all_vars:
                find_upstream(source)

    # 从目标开始反向查找
    for var in upstream_vars:
        find_upstream(var)

    # 添加目标变量
    all_vars.add(target)

    # 直接连接到目标的路径
    for _, row in direct.iterrows():
        all_links.append({
            'source': row['rval'],
            'target': target,
            'value': row['Est. Std']
        })

    # 构造节点
    nodes = [{"name": var} for var in all_vars]
    return {
        "nodes": nodes,
        "links": all_links
    }

def analysis(df):
    df = process_data(df)

    model_desc = """
    # 测量模型
    初始资源感知 =~ 教室设备满意度 + 实训室满意度 + 图书馆满意度 + 网络资源满意度 + 体育设施满意度
    学习投入度 =~ 课前预学 + 课堂参与 + 课后复习 + 延伸阅读 + 自习时间 + 实验科研时间 + 竞赛活动时间
    师生关系 =~ 师德师风满意度 + 关爱学生满意度 + 教学投入满意度
    专业课体验 =~ 专业课知识融合 + 专业课解决问题能力 + 专业课交叉融合 + 专业课实践结合 + 专业课努力程度 + 专业课前沿内容
    体美劳体验 =~ 体育教育满意度 + 美育教育满意度 + 劳动教育满意度
    综合满意度 =~ 学校整体满意度 + 思政课总体满意度 + 实习内容满意度 + 教师总体满意度

    # 结构模型
    学习投入度 ~ 初始资源感知 + 师生关系
    专业课体验 ~ 初始资源感知 + 师生关系
    体美劳体验 ~ 初始资源感知 + 师生关系
    综合满意度 ~ 学习投入度 + 专业课体验
    综合满意度 ~ 初始资源感知

    # 潜变量协方差
    师生关系 ~~ 初始资源感知
    学习投入度 ~~ 专业课体验

    # 残差相关（根据变量逻辑）
    # 自习时间 ~~ 网络课程时间
    图书馆满意度 ~~ 网络资源满意度
    教室设备满意度 ~~ 实训室满意度
    自习时间 ~~ 实验科研时间
    # 竞赛活动时间 ~~ 其他学习时间
    专业课知识融合 ~~ 专业课解决问题能力
    自习时间 ~~ 实验科研时间
    # 竞赛活动时间 ~~ 其他学习时间
    专业课知识融合 ~~ 专业课解决问题能力
    """
    model = Model(model_desc)
    model.fit(df)
    inspection = model.inspect(std_est=True)

    sankey_data = extract_paths_to_target(inspection, '综合满意度')

    # paths = inspection[inspection["op"] == '~'].copy()
    #
    # paths = paths.rename(columns={
    #     "lval": "target",
    #     "rval": "source",
    #     "Est. Std": "value"
    # })[['source', 'target', 'value']]
    #
    # # 开始构造桑基图
    # all_nodes = pd.concat([paths["source"], paths["target"]]).unique()
    # nodes = [{"name": name} for name in all_nodes]
    # links = paths.to_dict(orient='records')
    #
    # sankey_data = {
    #     "nodes": nodes,
    #     "links": links
    # }
    return sankey_data