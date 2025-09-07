// src/services/analysisService.ts
import request from '@/utils/request';
import type * as T from '@/types/analysis';
import type {AnalysisInitBatch} from "@/types/analysis";

class AnalysisService {
    /** GET /analysis */
    static async getAnalysis(): Promise<AnalysisInitBatch> {
        const res = await request({ url: '/analysis', method: 'get' }) as T.GetAnalysisResp;
        return res.message;
    }

    /** POST /analysis/start */
    static async startAnalysis(data: T.StartAnalysisReq): Promise<T.AnalysisTask> {
        const res = await request({ url: '/analysis/start', method: 'post', data }) as T.StartAnalysisResp;
        return res.message;
    }

    /** GET /analysis/status/:taskId */
    static async getStatus(taskId: string): Promise<T.AnalysisStatus> {
        const res = await request({
            url: `/analysis/status/${encodeURIComponent(taskId)}`,
            method: 'get',
        }) as T.GetStatusResp;
        return res.message;
    }

    /** GET /analysis/results/:taskId */
    static async getResults(taskId: string): Promise<T.AnalysisResult> {
        const res = await request({
            url: `/analysis/results/${encodeURIComponent(taskId)}`,
            method: 'get',
        }) as T.GetResultsResp;
        return res.message;
    }
}

export default AnalysisService;