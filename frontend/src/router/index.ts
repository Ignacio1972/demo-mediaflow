import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/components/dashboard/Dashboard.vue'),
  },
  {
    path: '/library',
    name: 'library',
    component: () => import('@/components/library/Library.vue'),
  },
  {
    path: '/calendar',
    name: 'calendar',
    component: () => import('@/components/calendar/Calendar.vue'),
  },
  {
    path: '/settings',
    name: 'settings',
    redirect: '/settings/ai',
    children: [
      {
        path: 'ai',
        name: 'settings-ai',
        component: () => import('@/components/settings/AISettings.vue'),
      },
      {
        path: 'voices',
        name: 'settings-voices',
        component: () => import('@/components/settings/voices/VoiceManager.vue'),
      },
      {
        path: 'audio',
        name: 'settings-audio',
        component: () => import('@/components/settings/AudioConfig.vue'),
      },
      {
        path: 'categories',
        name: 'settings-categories',
        component: () => import('@/components/settings/categories/CategoryEditor.vue'),
      },
      {
        path: 'automatic',
        name: 'settings-automatic',
        component: () => import('@/components/settings/automatic/AutomaticMode.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
