<template>
  <div class="login-container">
    <!-- 左侧展示区 -->
    <div class="login-left">
      <div class="brand-info">
                 <div class="brand-logo">
           <el-icon class="logo-icon"><Monitor /></el-icon>
           <h1 class="brand-title">LejoyCluster</h1>
         </div>
         <h2 class="brand-subtitle">大数据运维管理平台</h2>
        <p class="brand-description">统一管理您的大数据集群和告警系统，提供全方位的监控和运维服务</p>
        
        <div class="features">
          <div class="feature-item">
            <el-icon class="feature-icon"><Bell /></el-icon>
            <div class="feature-text">
              <h3>智能告警</h3>
              <p>实时监控系统状态，智能分析异常情况</p>
            </div>
          </div>
          <div class="feature-item">
            <el-icon class="feature-icon"><Monitor /></el-icon>
            <div class="feature-text">
              <h3>集群监控</h3>
              <p>全面监控大数据集群资源和服务状态</p>
            </div>
          </div>
          <div class="feature-item">
            <el-icon class="feature-icon"><User /></el-icon>
            <div class="feature-text">
              <h3>用户管理</h3>
              <p>集成LDAP，统一管理用户权限和访问控制</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 右侧登录区 -->
    <div class="login-right">
      <div class="login-box">
        <div class="login-header">
          <h1>欢迎登录</h1>
          <p>请输入您的账号信息</p>
        </div>
        
        <el-form 
          ref="loginFormRef" 
          :model="loginForm" 
          :rules="rules" 
          class="login-form"
          size="large"
        >
          <el-form-item prop="username">
            <el-input 
              v-model="loginForm.username" 
              placeholder="用户名"
              :prefix-icon="User"
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input 
              v-model="loginForm.password" 
              type="password" 
              placeholder="密码"
              :prefix-icon="Lock"
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              class="login-button"
              :loading="loading"
              @click="handleLogin"
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>
        

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Monitor, Bell } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const loginFormRef = ref()

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  try {
    await loginFormRef.value.validate()
    loading.value = true
    
    // 模拟登录验证
    if (loginForm.username === 'admin' && loginForm.password === 'admin') {
      localStorage.setItem('token', 'mock-token')
      localStorage.setItem('username', loginForm.username)
      ElMessage.success('登录成功')
      router.push('/')
    } else {
      ElMessage.error('用户名或密码错误')
    }
  } catch (error) {
    console.error('登录失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  box-sizing: border-box;
  overflow: hidden;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  margin: 0;
  padding: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 左侧展示区 */
.login-left {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5% 8% 5% 5%;
  position: relative;
  overflow: hidden;
  min-width: 0;
}

.login-left::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
  opacity: 0.3;
}

.brand-info {
  color: white;
  z-index: 1;
  text-align: left;
  width: 100%;
  max-width: none;
}

.brand-logo {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
}

.logo-icon {
  font-size: 48px;
  margin-right: 16px;
  color: rgba(255, 255, 255, 0.9);
}

.brand-title {
  font-size: 42px;
  font-weight: 700;
  margin: 0;
  letter-spacing: 2px;
}

.brand-subtitle {
  font-size: 28px;
  font-weight: 400;
  margin: 0 0 20px 0;
  color: rgba(255, 255, 255, 0.9);
}

.brand-description {
  font-size: 18px;
  line-height: 1.6;
  margin-bottom: 50px;
  color: rgba(255, 255, 255, 0.8);
}

.features {
  space-y: 30px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 30px;
  opacity: 0;
  animation: fadeInUp 0.6s ease forwards;
}

.feature-item:nth-child(1) { animation-delay: 0.2s; }
.feature-item:nth-child(2) { animation-delay: 0.4s; }
.feature-item:nth-child(3) { animation-delay: 0.6s; }

.feature-icon {
  font-size: 24px;
  margin-right: 16px;
  margin-top: 4px;
  color: rgba(255, 255, 255, 0.9);
  flex-shrink: 0;
}

.feature-text h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: white;
}

.feature-text p {
  font-size: 14px;
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.5;
}

/* 右侧登录区 */
.login-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5% 5% 5% 8%;
  position: relative;
  z-index: 2;
  min-width: 0;
  max-width: 50%;
}

.login-box {
  width: 100%;
  max-width: 90%;
  text-align: center;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 8% 10%;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.login-header h1 {
  color: #ffffff;
  margin-bottom: 12px;
  font-size: 32px;
  font-weight: 600;
  letter-spacing: 1px;
}

.login-header p {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 40px;
  font-size: 16px;
  line-height: 1.5;
}

.login-form {
  text-align: left;
}

.login-form .el-form-item {
  margin-bottom: 24px;
}

.login-form .el-input {
  height: 50px;
}

.login-form .el-input__inner {
  height: 50px;
  line-height: 50px;
  font-size: 16px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ffffff;
  transition: all 0.3s ease;
}

.login-form .el-input__inner::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.login-form .el-input__inner:focus {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.1);
}

.login-form :deep(.el-input__prefix) {
  color: rgba(255, 255, 255, 0.7);
}

.login-button {
  width: 100%;
  height: 50px;
  font-size: 18px;
  font-weight: 500;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  margin-top: 8px;
  transition: all 0.3s ease;
}

.login-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
}

.login-tips {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.login-tips p {
  color: #999;
  font-size: 14px;
  margin: 0;
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .login-left {
    padding: 4% 6% 4% 4%;
  }
  
  .brand-title {
    font-size: 36px;
  }
  
  .brand-subtitle {
    font-size: 24px;
  }
  
  .login-right {
    padding: 4% 4% 4% 6%;
  }
  
  .login-box {
    max-width: 95%;
    padding: 6% 8%;
  }
}

@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
    overflow-y: auto;
    position: absolute;
  }
  
  .login-left {
    flex: none;
    min-height: 45vh;
    padding: 40px 20px 30px 20px;
    justify-content: center;
    width: 100%;
  }
  
  .brand-info {
    text-align: center;
    max-width: 100%;
  }
  
  .brand-title {
    font-size: 28px;
  }
  
  .brand-subtitle {
    font-size: 18px;
  }
  
  .brand-description {
    font-size: 15px;
    margin-bottom: 30px;
  }
  
  .features {
    display: none;
  }
  
  .login-right {
    flex: none;
    width: 100%;
    max-width: 100%;
    min-height: 55vh;
    padding: 30px 20px;
    justify-content: center;
  }
  
  .login-box {
    max-width: 420px;
    width: 100%;
    padding: 40px 30px;
    margin: 0 auto;
  }
  
  .login-header h1 {
    font-size: 24px;
  }
}

/* 大屏优化 */
@media (min-width: 1400px) {
  .login-left {
    padding: 6% 10% 6% 6%;
  }
  
  .brand-title {
    font-size: 48px;
  }
  
  .brand-subtitle {
    font-size: 32px;
  }
  
  .brand-description {
    font-size: 20px;
  }
  
  .login-right {
    padding: 6% 6% 6% 10%;
  }
  
  .login-box {
    max-width: 85%;
    padding: 10% 12%;
  }
  
  .login-header h1 {
    font-size: 36px;
  }
}
</style> 