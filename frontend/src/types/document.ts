export interface DocItem {
    id: string
    filename: string
    file_size: number
    status: string
    uploaded_at: string
    file_type?: string
    chunk_count?: number
    processed_at?: string | null
    error_message?: string | null
}
export interface KnowledgeBase {
    id: string
    name: string
    description: string
    status: 'ready' | 'initializing' | 'error'
    document_count: number
    total_chunks: number
    embedding_model: string
    llm_model: string
    created_at: string
    updated_at: string
    last_indexed_at: string | null
}