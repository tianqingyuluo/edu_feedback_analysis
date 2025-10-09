import request from "@/utils/request.ts";
import type * as T from '@/types/whatIf.ts';
class WhatIfService{
    static async getWhatIfPrediction (data_id:string,task_id:string): Promise<T.FeatureItem[]> {
        const res = await request({
            url: `/predict/what_if/${data_id}/${task_id}`,
            method: "get"
            }
        )as T.GetFeatureItem;
        return res.message
    }
    static async executeWhatIf (Request:T.whatIfRequest):Promise<T.whatIfResponse> {
        const res = await request({
            url : `predict/what_if`,
            method: "post",
            data:Request
        })as T.GetWhatIfResponse
        return res.message
    }
}
export default WhatIfService;