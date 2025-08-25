// types.ts
export interface Academy {
    id: number
    name: string
    majors: Major[]
}

export interface Major {
    id: number
    name: string
}

// 使用示例
export const sampleAcademies: Academy[] = [
    {
        id: 1,
        name: "计算机学院",
        majors: [
            { id: 101, name: "计算机科学与技术" },
            { id: 102, name: "软件工程" },
            { id: 103, name: "人工智能" }
        ]
    },
    {
        id: 2,
        name: "经济管理学院",
        majors: [
            { id: 201, name: "经济学" },
            { id: 202, name: "工商管理" },
            { id: 203, name: "金融学" }
        ]
    }
]