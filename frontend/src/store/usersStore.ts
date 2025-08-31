// stores/users.ts
import { defineStore } from 'pinia';
import { UserService } from '@/api/users.ts';
import type {UpdateUserRequest, User} from '@/types/users';

export const useUsersStore = defineStore('users', {
    state: () => ({
        users: [] as User[],
        loading: false,
        error: null as string | null,
        hasFetched: false // 添加标志位，记录是否已获取过数据
    }),

    actions: {
        async fetchUsers() {
            this.loading = true;
            this.error = null;
            try {
                const response = await UserService.getUsers();
                this.users = response.users;
                this.hasFetched = true; // 设置已获取标志
            } catch (error: any) {
                this.error = error.message || '获取用户列表失败';
                console.error('获取用户列表失败:', error);
                throw error;
            } finally {
                this.loading = false;
            }
        },

        async addUser(userData: { username: string; phone: string; password: string }) {
            this.loading = true;
            this.error = null;
            try {
                const newUser = await UserService.addUser(userData);
                this.users.push(newUser);
                return newUser;
            } catch (error: any) {
                this.error = error.message || '添加用户失败';
                console.error('添加用户失败:', error);
                throw error;
            } finally {
                this.loading = false;
            }
        },

        async deleteUser(userId: number) {
            this.loading = true;
            this.error = null;
            try {
                const message = await UserService.deleteUser(userId);
                // 从本地状态中移除用户
                this.users = this.users.filter(user => user.id !== userId);
                return message;
            } catch (error: any) {
                this.error = error.message || '删除用户失败';
                console.error('删除用户失败:', error);
                throw error;
            } finally {
                this.loading = false;
            }
        },

        async updateUser(userId: number, updates: UpdateUserRequest) {
            this.loading = true;
            this.error = null;
            try {
                const updatedUser = await UserService.updateUser(userId, updates);
                // 更新本地状态中的用户信息
                const userIndex = this.users.findIndex(user => user.id === userId);
                if (userIndex !== -1) {
                    this.users[userIndex] = updatedUser;
                }
                return updatedUser;
            } catch (error: any) {
                this.error = error.message || '更新用户失败';
                console.error('更新用户失败:', error);
                throw error;
            } finally {
                this.loading = false;
            }
        },

        /**
         * 获取所有用户，如果为空则自动获取
         * @returns 用户数组
         */
        async getAllUsers(): Promise<User[]> {
            // 如果用户列表为空且尚未获取过数据，则自动获取
            if (this.users.length === 0 && !this.hasFetched) {
                await this.fetchUsers();
            }
            return [...this.users];
        },

        /**
         * 根据角色筛选用户
         * @param role 用户角色
         * @returns 符合角色的用户数组
         */
        getUsersByRole(role: string): User[] {
            return this.users.filter(user => user.role === role);
        },

        /**
         * 清空所有用户
         */
        clearAllUsers(): void {
            this.users = [];
            this.hasFetched = false; // 重置获取标志
        },
    },

    persist: true,
});