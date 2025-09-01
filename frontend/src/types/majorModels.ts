// types.ts
export interface Academy {
    name: string
    majors: Major[]
}

export interface Major {
    name: string
    data: Number[]
}

// 默认假数据 - 多个学院
export const defaultAcademyData: Academy[] = [
    {
        name: "计算机科学与技术学院",
        majors: [
            {
                name: "计算机科学与技术",
                data: [120, 135, 142, 138, 145, 150]
            },
            {
                name: "软件工程",
                data: [90, 105, 120, 115, 125, 130]
            },
            {
                name: "人工智能",
                data: [60, 75, 85, 90, 100, 110]
            }
        ]
    },
    {
        name: "经济管理学院",
        majors: [
            {
                name: "金融学",
                data: [150, 145, 160, 155, 165, 170]
            },
            {
                name: "会计学",
                data: [130, 140, 135, 145, 150, 155]
            },
            {
                name: "国际贸易",
                data: [100, 110, 105, 115, 120, 125]
            }
        ]
    },
    {
        name: "机械工程学院",
        majors: [
            {
                name: "机械设计制造及其自动化",
                data: [180, 175, 185, 190, 195, 200]
            },
            {
                name: "车辆工程",
                data: [120, 130, 125, 135, 140, 145]
            },
            {
                name: "材料成型及控制工程",
                data: [90, 95, 100, 105, 110, 115]
            }
        ]
    },
    {
        name: "外国语学院",
        majors: [
            {
                name: "英语",
                data: [160, 165, 170, 175, 180, 185]
            },
            {
                name: "日语",
                data: [80, 85, 90, 95, 100, 105]
            },
            {
                name: "法语",
                data: [60, 65, 70, 75, 80, 85]
            }
        ]
    },
    {
        name: "医学院",
        majors: [
            {
                name: "临床医学",
                data: [200, 210, 220, 230, 240, 250]
            },
            {
                name: "口腔医学",
                data: [100, 110, 115, 120, 125, 130]
            },
            {
                name: "护理学",
                data: [150, 160, 165, 170, 175, 180]
            }
        ]
    }
];

export default defaultAcademyData;