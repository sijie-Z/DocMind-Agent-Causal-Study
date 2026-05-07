import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { loginWithJson, register as apiRegister, getUserProfile } from '@/api/auth'
import { setToken, setRefreshToken, removeToken, getToken } from '@/utils/auth'
import type { UserInfo, LoginForm, RegisterForm } from '@/types/user'
import { useAppStore } from './app'

export const useUserStore = defineStore('user', () => {
  // 状态
  const userInfo = ref<UserInfo | null>(null)
  const token = ref<string>(getToken() || '')
  const currentOrganizationId = ref<number | null>(null)

  // 初始化：尝试从 localStorage 恢复用户信息
  const initUserInfo = () => {
    try {
      const stored = localStorage.getItem('user_info')
      if (stored) {
        userInfo.value = JSON.parse(stored)
        currentOrganizationId.value = userInfo.value?.organization_id || null
        
        // 恢复主题设置
        if (userInfo.value?.preferences) {
          try {
            const prefs = typeof userInfo.value.preferences === 'string' 
              ? JSON.parse(userInfo.value.preferences) 
              : userInfo.value.preferences
            
            if (prefs.theme) {
              const appStore = useAppStore()
              appStore.setTheme(prefs.theme)
            }
          } catch {
            // Failed to parse preferences during init
          }
        }
      }
    } catch {
      // Failed to restore user info
      localStorage.removeItem('user_info')
    }
  }
  // 立即执行初始化
  initUserInfo()
  
  // 监听 userInfo 变化并持久化
  watch(userInfo, (newVal) => {
    if (newVal) {
      localStorage.setItem('user_info', JSON.stringify(newVal))
    } else {
      localStorage.removeItem('user_info')
    }
  }, { deep: true })
  
  // 计算属性
  const isLoggedIn = computed(() => !!token.value && !!userInfo.value)
  const isAdmin = computed(() => userInfo.value?.role === 'admin')
  const currentOrgId = computed(() => currentOrganizationId.value || userInfo.value?.organization_id || null)

  const setCurrentOrganization = (orgId: number) => {
    currentOrganizationId.value = orgId
  }
  
  // 方法
  const login = async (form: LoginForm) => {
    try {
      const response = await loginWithJson(form)
      // 兼容 { data: { access_token, user_info, ... } } 与 直接 { access_token, ... }
      const raw = response.data as unknown as Record<string, unknown>
      const payload = (raw?.data as Record<string, unknown>) ?? raw
      if (!payload || !payload.access_token) {
        throw new Error((raw?.message as string) || '后端返回数据格式错误')
      }

      const access_token = payload.access_token as string
      const refresh_token = payload.refresh_token as string | undefined
      const expires_in = payload.expires_in as number | undefined
      const loginUserInfo = payload.user_info as UserInfo | undefined
      token.value = access_token
      setToken(access_token, expires_in ?? 86400)
      if (refresh_token) setRefreshToken(refresh_token)

      if (loginUserInfo) {
        userInfo.value = loginUserInfo
        currentOrganizationId.value = loginUserInfo.organization_id || null
        if (loginUserInfo.preferences) {
          try {
            const prefs = typeof loginUserInfo.preferences === 'string'
              ? JSON.parse(loginUserInfo.preferences)
              : loginUserInfo.preferences
            if (prefs?.theme) {
              useAppStore().setTheme(prefs.theme)
            }
          } catch { /* preference parse failure is non-critical */ }
        }
      } else {
        await getUserInfo()
      }

      return { success: true }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.message ?? error.response?.data?.detail ?? error.message ?? '登录失败'
      }
    }
  }
  
  const register = async (form: RegisterForm) => {
    try {
      const response = await apiRegister(form)
      const raw = response.data as unknown as Record<string, unknown>
      const payload = (raw?.data as Record<string, unknown>) ?? raw
      if (payload?.access_token) {
        token.value = payload.access_token as string
        setToken(payload.access_token as string, (payload.expires_in as number) ?? 86400)
        if (payload.refresh_token) setRefreshToken(payload.refresh_token as string)
        if (payload.user_info) userInfo.value = payload.user_info as UserInfo
      }
      return { success: true }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.message ?? error.response?.data?.detail ?? '注册失败，请检查输入信息'
      }
    }
  }
  
  const getUserInfo = async () => {
    // 如果没有 Token，直接抛出错误或返回，避免无效请求导致 401
    if (!token.value) {
        return Promise.reject(new Error('No token found'))
    }

    try {
      const response = await getUserProfile()
      // 兼容两种格式：
      // 1. 标准响应格式 { code: 200, data: { ... }, message: "..." }
      // 2. 直接返回对象 { id: ..., username: ... }
      const resData = response.data as unknown as Record<string, unknown>
      if (resData.data && typeof resData.data === 'object' && !resData.username) {
          userInfo.value = resData.data as UserInfo
      } else {
          userInfo.value = resData as unknown as UserInfo
      }
      currentOrganizationId.value = userInfo.value?.organization_id || null
      
      // 同步用户偏好设置 (主题)
      if (userInfo.value?.preferences) {
        try {
          const prefs = typeof userInfo.value.preferences === 'string' 
            ? JSON.parse(userInfo.value.preferences) 
            : userInfo.value.preferences
            
          if (prefs.theme) {
            const appStore = useAppStore()
            appStore.setTheme(prefs.theme)
          }
        } catch {
          // Failed to parse user preferences
        }
      }

      return response.data
    } catch (error) {
      logout()
      throw error
    }
  }
  
  const logout = () => {
    userInfo.value = null
    token.value = ''
    removeToken()
  }
  
  // --- 找到 stores/user.ts 中的 updateUserInfo 函数，替换为 ---
  const updateUserInfo = (info: Partial<UserInfo>) => {
    if (userInfo.value) {
      // ⚡ 核心修复：使用解构赋值确保引用变化，从而触发 watch
      userInfo.value = { ...userInfo.value, ...info }
    }
  }
  
  return {
    // 状态
    userInfo,
    token,
    currentOrganizationId,

    // 计算属性
    isLoggedIn,
    isAdmin,
    currentOrgId,

    // 方法
    login,
    register,
    getUserInfo,
    logout,
    updateUserInfo,
    setCurrentOrganization
  }
})
