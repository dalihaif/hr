import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '@/utils/request'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || '{}'))

  // 登录
  async function login(username, password) {
    try {
      const response = await request.post('/login', { username, password })
      
      // 注意:当前后端使用session,这里模拟token
      token.value = 'session_token_' + Date.now()
      userInfo.value = {
        username,
        real_name: response.real_name || username,
        role: response.role || 'user'
      }
      
      localStorage.setItem('token', token.value)
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
      
      return true
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    }
  }

  // 登出
  function logout() {
    token.value = ''
    userInfo.value = {}
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  return {
    token,
    userInfo,
    login,
    logout
  }
})
