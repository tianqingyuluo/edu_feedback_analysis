import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
// 使用动态导入实现懒加载
const Main = () => import('@/views/Main.vue')
const test = () => import('@/views/Placeholder.vue')

const TeachingQuality = () => import('@/components/layout/NoName.vue')
const DataManagement = () => import('@/views/DataManagement.vue')
const PersonManagement = () => import('@/views/PersonManagement.vue')
// const StudentSatisfaction = () => import('@/views/StudentSatisfaction.vue')
// const CourseEvaluation = () => import('@/views/CourseEvaluation.vue')
// const TeacherEvaluation = () => import('@/views/TeacherEvaluation.vue')
// const DataManagement = () => import('@/views/DataManagement.vue')
// const SystemSettings = () => import('@/views/SystemSettings.vue')
// const Data = () => import('@/views/Data.vue')
// const Analysis = () => import('@/views/Analysis.vue')
// const Chat = () => import('@/views/Chat.vue')

const Login=()=>import('@/login/Index.vue')

const routes = [
    {
        path: '/',
        name: 'Home',
        component: Main,
        children: [
            // navItems 路由
            { path: 'home', name: 'Overview', component: Home }, // 默认子路由
            { path: 'teaching-quality', name: 'TeachingQuality', component: TeachingQuality },
            { path: 'student-satisfaction', name: 'StudentSatisfaction', component: PersonManagement },
            { path: 'course-evaluation', name: 'CourseEvaluation', component: test },
            { path: 'teacher-evaluation', name: 'TeacherEvaluation', component: test },
            { path: 'data-management', name: 'DataManagement', component: DataManagement },
            { path: 'system-settings', name: 'SystemSettings', component:test },

            // tabs 路由
            { path: 'data', name: 'Data', component: test },
            { path: 'analysis', name: 'Analysis', component: test },
            { path: 'chat', name: 'Chat', component: test },


        ]
    },
    {path: '/login', name: 'Login', component: Login},
]

const router = createRouter({
    history: createWebHistory(),
    // @ts-ignore
    routes
})

export default router