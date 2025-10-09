import { createRouter, createWebHistory } from 'vue-router'

/* === 统一占位组件 === */
const AiChat = () => import('@/views/AIchat/AIchat.vue')
const Login = () => import('@/login/Index.vue')
const PersonManagement = () => import('@/views/PersonManagement.vue')
const DataManagement   = () => import('@/views/DataManagement.vue')
const ExcelManagement  = () => import('@/views/ExcelManagement.vue')
const DocumentManagement = () => import('@/views/KbDocList.vue')
const routes = [
    {
        path: '/',
        redirect: '/admin/data-hub', // 默认跳数据管理
    },
    {
        path: '/admin',
        component: () => import('@/views/Main.vue'), // 布局壳子
        children: [
            /* --- navItems 对应区域（全部先指向 Placeholder）--- */
            { path: 'data-hub',    name: 'DataHub',    component: ExcelManagement },
            { path: 'user-mgmt',   name: 'UserMgmt',   component: PersonManagement },
            { path: 'analytics',   name: 'Analytics',  component: DataManagement },
            { path: 'ai-chat',     name: 'AiChat',     component: AiChat },
            { path: 'report/:reportId/:dataId', name: 'ReportShow', component: () => import('@/views/Home.vue'), props: true },
            { path: 'Document', name: 'Document', component:DocumentManagement },
        ],
    },
    { path: '/login', name: 'Login', component: Login },

]

const router = createRouter({
    history: createWebHistory(),
    // @ts-ignore
    routes,
})

export default router