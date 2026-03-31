import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: () => import('../views/Home.vue') },
  { path: '/workspace', name: 'Workspace', component: () => import('../views/WorkspaceView.vue') },
  { path: '/simulation', name: 'Simulation', component: () => import('../views/SimulationRunView.vue') },
  { path: '/squad', name: 'Squad', component: () => import('../views/SquadView.vue') },
  { path: '/report', name: 'Report', component: () => import('../views/ReportView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
