export enum TaskStatus {
    PENDING    = 'PENDING',
    PROCESSING = 'PROCESSING',
    COMPLETED  = 'COMPLETED',
    FAILED     = 'FAILED',
}

/* ===== 裸数据 ===== */
export interface AnalysisInit {
    data_id: string;
    task_id: string;
    status:  TaskStatus;
}

/* 新加：批量返回 */
export type AnalysisInitBatch = AnalysisInit[];

export interface StartAnalysisReq {
    data_id: string;
}

export interface AnalysisTask {
    task_id: string;
    status: TaskStatus;
}

export interface AnalysisStatus {
    task_id: string;
    status: TaskStatus;
    progress?: number; // 0-100
    message?: string;
}

export interface AnalysisResult {
    task_id: string;
    data_id: number;
    created_at: string; // ISO-8601
    summary: object;
    detailed_results: object;
}
/* ===== 后端整包包装（服务函数内部用） ===== */
export interface Resp<T> {
    http_status: number;
    message: T;
}
export interface HistoryItem {
    id:string
    filename: string
    size: number
    uploaded_at: string
}

export interface UploadHistoryResp {
    http_status: number
    message: {
        total: number
        page: number
        size: number
        items: HistoryItem[]
    }
}
/* 具体响应包 */
export type GetAnalysisResp   = Resp<AnalysisInitBatch>
export type StartAnalysisResp = Resp<AnalysisTask>
export type GetStatusResp     = Resp<AnalysisStatus>
export type GetResultsResp    = Resp<AnalysisResult>