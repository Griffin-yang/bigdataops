<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  overflow-x: hidden;
}

#app {
  height: 100vh;
  width: 100vw;
  margin: 0;
  padding: 0;
  overflow: hidden;
  position: relative;
}

/* Element Plus 容器重置 */
.el-container {
  height: 100vh !important;
  width: 100% !important;
  margin: 0 !important;
  padding: 0 !important;
}

.el-aside {
  margin: 0 !important;
  padding: 0 !important;
  flex-shrink: 0 !important;
}

.el-main {
  margin: 0 !important;
  padding: 24px !important;
  flex: 1 !important;
  overflow-x: hidden !important;
  overflow-y: auto !important;
  width: 100% !important;
}

.el-header {
  margin: 0 !important;
  padding: 0 24px !important;
  width: 100% !important;
  flex-shrink: 0 !important;
}

/* Element Plus 组件样式优化 */
.el-input__wrapper {
  transition: all 0.3s ease;
}

.el-button {
  font-weight: 500;
  letter-spacing: 0.5px;
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
