import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    redirect: '/campaigns',
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
    path: '/campaigns',
    name: 'campaigns',
    component: () => import('@/components/campaigns/CampaignsPage.vue'),
  },
  {
    path: '/campaigns/:id',
    name: 'campaign-detail',
    component: () => import('@/components/campaigns/CampaignDetail.vue'),
  },
  {
    path: '/music',
    name: 'music',
    component: () => import('@/components/music/MusicPage.vue'),
  },
  {
    path: '/operations',
    name: 'operations',
    component: () => import('@/components/operations/OperationsPage.vue'),
  },
  {
    path: '/operations/vehicles',
    name: 'operations-vehicles',
    component: () => import('@/components/operations/vehicles/VehicleAnnouncement.vue'),
  },
  {
    path: '/mobile',
    name: 'mobile',
    component: () => import('@/components/mobile/MobilePage.vue'),
  },
  {
    path: '/settings',
    name: 'settings',
    redirect: '/settings/ai',
    children: [
      {
        path: 'ai',
        name: 'settings-ai',
        component: () => import('@/components/settings/ai-clients/AIClientManager.vue'),
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
      {
        path: 'templates',
        name: 'settings-templates',
        component: () => import('@/components/settings/templates/TemplateManager.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
