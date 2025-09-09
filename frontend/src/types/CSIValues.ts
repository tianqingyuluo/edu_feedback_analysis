//Demo10(整体满意分布)数据结构
export interface satisfactionDistributionStruct {
    labels: string[];
    values: number[];
}

export const satisfactionDistributionData: satisfactionDistributionStruct = {
    "labels": ["满意", "较满意", "一般", "较不满意", "不满意"],
    "values": [2929, 2877, 3782, 3280, 958]
}




//Demo9(整体满意度)数据结构
export interface overallSatisfactionStruct {
    labels: string[];
    series: {
        name: string;
        data: number[];
    }[]
}

export const overallSatisfactionData: overallSatisfactionStruct = {
    labels: [
        "学习情况",
        "思政课",
        "专业课",
        "体育教育",
        "美育教育",
        "劳动教育",
        "校园生活",
        "实习",
        "自我提升",
        "老师教育",
        "学校服务",
        "学校基础条件"
    ],
    series: [
        {
            name: "一般",
            data: [0.465, 0.771, 0.755, 0.8, 0.797, 0.798, 0.578, 0.742, 0.757, 0.775, 0.759, 0.741]
        },
        {
            name: "满意",
            data: [0.579, 0.986, 0.951, 0.991, 0.987, 0.989, 0.686, 0.966, 0.973, 0.988, 0.978, 0.959]
        },
        {
            name: "较不满意",
            data: [0.361, 0.758, 0.737, 0.795, 0.767, 0.777, 0.286, 0.715, 0.738, 0.776, 0.744, 0.717]
        },
        {
            name: "不满意",
            data: [0.333, 0.626, 0.64, 0.63, 0.542, 0.563, 0.277, 0.548, 0.627, 0.685, 0.608, 0.553]
        },
        {
            name: "较满意",
            data: [0.469, 0.91, 0.859, 0.911, 0.893, 0.896, 0.505, 0.806, 0.843, 0.909, 0.865, 0.829]
        }
    ]
}





//Demo11(满意度贡献值)
export interface SatisfactionContributionStruct {
    labels: string[];
    values: number[];
}

export const SatisfactionContributionData: SatisfactionContributionStruct = {
    "labels": [
        "校园生活",
        "学校服务",
        "学习情况",
        "自我提升",
        "实习",
        "专业课",
        "思政课",
        "劳动教育",
        "老师教育",
        "美育教育"
    ],
    "values": [
        0.1786,
        0.1245,
        0.1132,
        0.0992,
        0.0857,
        0.0661,
        0.0631,
        0.0614,
        0.0587,
        0.0566
    ]
}