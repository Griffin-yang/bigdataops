import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import * as echarts from 'echarts'

import App from './App.vue'
import router from './router'

const app = createApp(App)

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 注册ECharts
app.component('v-chart', VChart)

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

// 启动应用
console.log('🚀 BigDataOps 前端应用正在启动...')
console.log('📋 提示：如果页面空白，请按F12查看控制台错误')
console.log('🔑 登录信息：用户名=admin，密码=admin')

app.mount('#app')

console.log('✅ BigDataOps 前端应用启动完成')
