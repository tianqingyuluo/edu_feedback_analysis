import type { Academy } from '@/types/majorModels'

export function buildAcademiesWithOverall(rawAcademies: Academy[]): Academy[] {
    /* 全校整体 */
    const gradeSet = new Set<string>()
    rawAcademies.forEach(ac =>
        ac.majors[0].grades.forEach(g => gradeSet.add(g.name))
    )
    const allGrades = Array.from(gradeSet).sort()

    const wholeSchoolMajor = {
        name: '全校整体',
        grades: allGrades.map(gName => {
            const dimLen = rawAcademies[0].majors[0].grades.find(g => g.name === gName)?.data.length ?? 0
            const dataAvg: number[] = []
            for (let d = 0; d < dimLen; d++) {
                let sum = 0, cnt = 0
                rawAcademies.forEach(ac =>
                    ac.majors.forEach(ma =>
                        ma.grades.forEach(gr => {
                            if (gr.name === gName && gr.data[d] !== undefined) { sum += gr.data[d]; cnt++ }
                        })
                    )
                )
                dataAvg.push(cnt ? Number((sum / cnt).toFixed(2)) : 0)
            }
            return { name: gName, data: dataAvg }
        })
    }

    /* 各学院整体 */
    const processed: Academy[] = rawAcademies.map(ac => {
        const overall = {
            name: `${ac.name}整体`,
            grades: ac.majors[0].grades.map((_, gIdx) => {
                const gName = ac.majors[0].grades[gIdx].name
                const dimLen = ac.majors[0].grades[gIdx].data.length
                const dataAvg: number[] = []
                for (let d = 0; d < dimLen; d++) {
                    let sum = 0, cnt = 0
                    ac.majors.forEach(m => {
                        const g = m.grades[gIdx]
                        if (g && g.data[d] !== undefined) { sum += g.data[d]; cnt++ }
                    })
                    dataAvg.push(cnt ? Number((sum / cnt).toFixed(2)) : 0)
                }
                return { name: gName, data: dataAvg }
            })
        }
        return { ...ac, majors: [overall, ...ac.majors] }
    })

    return [{ name: '学校整体', majors: [wholeSchoolMajor] }, ...processed]
}