export interface FeatureItem {
    feature_name: string
    feature_classes: number
}
export interface whatIfRequest {
    features:FeatureItem[];
    task_id: string;
}
export interface whatIfResponse {
    prediction: Prediction;
    metadata: Metadata;
}
export interface Prediction {
    predicted_class: number;
    probabilities: {
        [classLabel: string]: number;
    };
    top_k_classes: TopClass[];
}
export interface TopClass {
    class_label: string;
    probability: number;
}
export interface Metadata {
    timestamp: string;
}
export interface Resp<T> {
    http_status: number;
    message: T;
}
export type GetFeatureItem   = Resp<FeatureItem[]>
export type GetWhatIfResponse   = Resp<whatIfResponse>