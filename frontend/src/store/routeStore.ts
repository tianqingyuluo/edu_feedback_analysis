// stores/routes.ts
import { defineStore } from 'pinia';
import { v4 as uuidv4 } from 'uuid';

export interface AppRoute {
    id: string;
    path: string;
    name: string;
}

export const useRoutesStore = defineStore('routes', {
    state: () => ({
        routeList: [] as AppRoute[],
    }),
    actions: {
        /**
         * 添加一个新的路由（如果路径不存在）
         * @param newPath 路由路径
         * @param newName 路由名称
         * @returns 新添加的 AppRoute 对象或已存在的 AppRoute 对象
         */
        addRoute(newPath: string, newName: string): AppRoute {
            // 检查是否已存在相同路径的路由
            const existingRoute = this.routeList.find(route => route.path === newPath);

            if (existingRoute) {
                // 如果已存在，返回已存在的路由
                return existingRoute;
            }

            // 如果不存在，创建新路由并添加到列表
            const newRoute: AppRoute = {
                id: uuidv4(),
                path: newPath,
                name: newName,
            };
            this.routeList.push(newRoute);
            return newRoute;
        },

        /**
         * 根据 ID 删除一个路由
         * @param routeId 要删除路由的 ID
         * @returns boolean - 是否成功删除
         */
        deleteRoute(routeId: string): boolean {
            const initialLength = this.routeList.length;
            this.routeList = this.routeList.filter(route => route.id !== routeId);
            return this.routeList.length < initialLength;
        },

        /**
         * 检查路由是否已存在
         * @param path 要检查的路由路径
         * @returns boolean - 是否存在
         */
        routeExists(path: string): boolean {
            return this.routeList.some(route => route.path === path);
        },

        /**
         * 重置所有路由
         */
        clearRoutes() {
            this.routeList = [];
        },
    },
    persist: true
});