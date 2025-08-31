// services/userService.ts
import request from '@/utils/request';
import type {
    AddUserRequest,
    AddUserResponse,
    UpdateUserRequest,
    UpdateUserResponse,
    GetUsersResponse
} from '@/types/users';

export class UserService {
    /**
     * 获取用户列表
     * @returns 用户列表
     */
    static async getUsers(): Promise<GetUsersResponse> {
        try {
            return await request({
                url: '/admin/user',
                method: 'get'
            });
        } catch (error) {
            console.error('获取用户列表失败:', error);
            throw error;
        }
    }

    /**
     * 添加用户
     * @param userData 用户数据
     * @returns 添加的用户信息
     */
    static async addUser(userData: AddUserRequest): Promise<AddUserResponse> {
        try {
            return await request({
                url: '/admin/user',
                method: 'post',
                data: userData
            });
        } catch (error) {
            console.error('添加用户失败:', error);
            throw error;
        }
    }

    /**
     * 删除用户
     * @param userId 用户ID
     * @returns 删除操作结果消息
     */
    static async deleteUser(userId: number): Promise<string> {
        try {
            return await request({
                url: `/admin/user/${userId}`,
                method: 'delete'
            });
        } catch (error) {
            console.error('删除用户失败:', error);
            throw error;
        }
    }

    /**
     * 更新用户信息
     * @param userId 用户ID
     * @param userData 更新的用户数据
     * @returns 更新后的用户信息
     */
    static async updateUser(userId: number, userData: UpdateUserRequest): Promise<UpdateUserResponse> {
        try {
            return await request({
                url: `admin/user/${userId}`,
                method: 'post',
                data: userData
            });
        } catch (error) {
            console.error('更新用户失败:', error);
            throw error;
        }
    }
}