// types/metricModels.ts
export interface Metric {
    name: string;
    data: number[];
}

export interface MetricGroup {
    name: string;
    metrics: Metric[];
}

// 示例数据
export const defaultMetricData: MetricGroup[] = [
    {
        name: '性能指标',
        metrics: [
            { name: 'CPU使用率', data: [45, 50, 48, 52, 55, 58] },
            { name: '内存使用率', data: [65, 68, 70, 72, 75, 78] },
            { name: '响应时间(ms)', data: [120, 115, 118, 122, 125, 128] },
            { name: '网络吞吐量(MB/s)', data: [10, 12, 15, 18, 20, 22] }
        ]
    },
    {
        name: '业务指标',
        metrics: [
            { name: '用户活跃数', data: [1000, 1050, 1100, 1150, 1200, 1250] },
            { name: '订单数量', data: [200, 210, 205, 220, 230, 240] },
            { name: '转化率(%)', data: [15, 16, 14, 17, 18, 19] },
            { name: '收入(千元)', data: [50, 55, 60, 65, 70, 75] }
        ]
    },
    {
        name: '系统指标',
        metrics: [
            { name: '磁盘使用率(%)', data: [40, 42, 45, 48, 50, 52] },
            { name: '错误率(%)', data: [2, 1.8, 1.5, 1.2, 1.0, 0.8] },
            { name: '并发连接数', data: [500, 520, 550, 580, 600, 620] }
        ]
    }
]