import type { Academy, Major } from '@/types/majorModels'

interface RawAcademy {
    name: string
    majors: {
        name: string
        grades: { name: string; data: number[] }[]
    }[]
}

/** 一次性生成「全校/全院/各专业」所有年级数据 */
export function buildTimeAcademies(raw: RawAcademy[]): Academy[] {
    const gradeSet = new Set<string>()
    raw.forEach(ac => ac.majors.forEach(m => m.grades.forEach(g => gradeSet.add(g.name))))
    const grades = Array.from(gradeSet).sort() // ['大一','大二'...]

    const list: Academy[] = []

    /* 1. 全校整体 - 每个年级一条 grade 记录 */
    const wholeMap = new Map<string, number[]>()
    for (const gr of grades) {
        const allData: number[][] = []
        for (const ac of raw) {
            for (const m of ac.majors) {
                const g = m.grades.find(item => item.name === gr)
                if (g) allData.push(g.data)
            }
        }

        // 找到最长的数据数组长度
        const maxLength = allData.reduce((max, arr) => Math.max(max, arr.length), 0)

        // 计算平均值，处理不同长度的数组
        const avg = Array.from({ length: maxLength }, (_, i) => {
            let sum = 0
            let count = 0

            for (const arr of allData) {
                if (i < arr.length) {
                    sum += arr[i]
                    count++
                }
            }

            return count > 0 ? sum / count : 0
        })

        wholeMap.set(gr, avg)
    }
    list.push({
        name: '学校整体',
        majors: [{ name: '学校整体', grades: grades.map(g => ({ name: g, data: wholeMap.get(g)! })) }]
    })

    /* 2. 各学院 */
    for (const ac of raw) {
        const majorList: Major[] = []

        /* 2.1 学院整体 - 同样每个年级一条 */
        const collegeMap = new Map<string, number[]>()
        for (const gr of grades) {
            const collegeData: number[][] = []
            for (const m of ac.majors) {
                const g = m.grades.find(item => item.name === gr)
                if (g) collegeData.push(g.data)
            }

            // 找到最长的数据数组长度
            const maxLength = collegeData.reduce((max, arr) => Math.max(max, arr.length), 0)

            // 计算平均值，处理不同长度的数组
            const avg = Array.from({ length: maxLength }, (_, i) => {
                let sum = 0
                let count = 0

                for (const arr of collegeData) {
                    if (i < arr.length) {
                        sum += arr[i]
                        count++
                    }
                }

                return count > 0 ? sum / count : 0
            })

            collegeMap.set(gr, avg)
        }
        majorList.push({
            name: `${ac.name.trim()}整体`,
            grades: grades.map(g => ({ name: g, data: collegeMap.get(g)! }))
        })

        /* 2.2 各专业 - 原样保留所有年级 */
        for (const m of ac.majors) {
            majorList.push({
                name: m.name.trim(),
                grades: m.grades.map(g => ({ name: g.name, data: g.data }))
            })
        }

        list.push({ name: ac.name.trim(), majors: majorList })
    }

    return list
}