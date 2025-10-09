export interface Resp<T> {
    http_status: number;
    message: T;
}
export interface getChatRoomResponse {
    id: string,
    task_id: string,
    user_id: string,
    created_at: string,
    updated_at: string,
}
export type getChatRoomResp   = Resp<getChatRoomResponse>
export interface ChatMessage {
    id: string,
    created_at:string,
    updated_at:string,
    chatid: string;
    role: string;
    content: string;
}
export type getChatRoomHistory =Resp<ChatMessage[]>