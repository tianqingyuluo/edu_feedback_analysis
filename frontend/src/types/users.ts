// types/users.ts
export interface User {
    id: number;
    username: string;
    phone: string;
    role: string;
    created_at: string;
    update_at: string;
}

export interface AddUserRequest {
    username: string;
    phone: string;
    password: string;
}

export interface AddUserResponse extends User {}

export interface UpdateUserRequest {
    username?: string;
    password?: string;
    phone?: string;
    role?: string;
}

export interface UpdateUserResponse extends User {}

export interface GetUsersResponse {
    users: User[];
}