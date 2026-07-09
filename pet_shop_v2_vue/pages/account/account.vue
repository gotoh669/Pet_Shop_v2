<template>
  <view class="page account-page">
    <view class="topbar account-topbar">
      <view>
        <text class="title">账号中心</text>
        <text class="subtitle">短信验证码登录、查看角色与权限</text>
      </view>
      <view class="top-actions">
        <button class="ghost" @click="goHome">首页</button>
        <button class="ghost" @click="goBack">返回</button>
      </view>
    </view>

    <view class="layout account-layout">
      <view class="panel login-panel">
        <view class="panel-head">
          <text class="panel-title">{{ isLoggedIn ? '当前账号' : '账号登录' }}</text>
        </view>

        <view v-if="!isLoggedIn">
          <view class="field">
            <text class="label">手机号</text>
            <input class="input" v-model="loginForm.phone" type="number" placeholder="请输入手机号" />
          </view>
          <view class="inline">
            <view class="field grow">
              <text class="label">验证码</text>
              <input class="input" v-model="loginForm.code" type="number" placeholder="6 位验证码" />
            </view>
            <button class="secondary fixed" @click="sendSmsCode">{{ loading.sms ? '发送中' : '发送验证码' }}</button>
          </view>
          <view class="code-box" v-if="mockCode">
            <text>模拟验证码</text>
            <text class="code">{{ mockCode }}</text>
          </view>
          <button class="primary wide" @click="smsLogin">{{ loading.login ? '登录中' : '登录系统' }}</button>
        </view>

        <view v-else class="profile">
          <view class="avatar">{{ avatarLetter }}</view>
          <view class="profile-main">
            <text class="profile-name">{{ currentUser.nickname || '未命名用户' }}</text>
            <text class="muted">{{ currentUser.phone }} · ID {{ currentUser.id }}</text>
            <text class="muted">状态：{{ currentUser.status }}</text>
          </view>
          <view class="profile-actions">
            <button class="secondary" @click="goProfileEdit">编辑资料</button>
            <button class="danger" @click="logout">退出</button>
          </view>
        </view>
      </view>

      <view class="panel" v-if="isLoggedIn">
        <view class="panel-head">
          <text class="panel-title">角色权限</text>
          <button class="ghost" @click="loadRolesAndPermissions">刷新</button>
        </view>
        <view class="cards">
          <view class="mini-card">
            <text class="mini-label">当前角色</text>
            <text class="mini-value">{{ roleSummary }}</text>
          </view>
          <view class="mini-card">
            <text class="mini-label">权限数量</text>
            <text class="mini-value">{{ permissions.length }}</text>
          </view>
        </view>
        <view class="tag-list" v-if="permissions.length">
          <text class="tag" v-for="permission in permissions" :key="permission.code">{{ permission.code }}</text>
        </view>
        <view class="empty" v-else>暂无权限数据</view>
      </view>
    </view>

    <view class="panel" v-if="canManageUsers">
      <view class="panel-head">
        <view>
          <text class="panel-title">用户管理</text>
          <text class="panel-note">管理员可维护用户状态与角色</text>
        </view>
        <button class="ghost" @click="loadAdminUsers">刷新</button>
      </view>
      <view class="filter">
        <input class="input" v-model="adminQuery.keyword" placeholder="手机号 / 昵称" />
        <picker :range="statusOptions" range-key="label" @change="onStatusFilterChange">
          <view class="picker">{{ statusFilterLabel }}</view>
        </picker>
        <button class="primary query" @click="searchAdminUsers">查询</button>
      </view>
      <view class="user-table" v-if="adminUsers.length">
        <view class="user-row head">
          <text>用户</text>
          <text>状态</text>
          <text>角色</text>
          <text>操作</text>
        </view>
        <view class="user-row" v-for="user in adminUsers" :key="user.id">
          <view>
            <text class="user-name">{{ user.nickname }}</text>
            <text class="muted">{{ user.phone }} · ID {{ user.id }}</text>
          </view>
          <text>{{ user.status }}</text>
          <view class="role-options">
            <button class="role" :class="{ selected: user.roleDraft.includes(role.code) }" v-for="role in allRoles" :key="role.code" @click="toggleRoleDraft(user, role.code)">
              {{ role.name }}
            </button>
          </view>
          <view class="row-actions">
            <button class="ghost" @click="saveUserRoles(user)">保存</button>
            <button class="danger" v-if="user.status === 'active'" @click="setAdminUserStatus(user, 'disabled')">禁用</button>
            <button class="secondary" v-else @click="setAdminUserStatus(user, 'active')">启用</button>
          </view>
        </view>
      </view>
      <view class="empty" v-else>暂无用户数据</view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      apiBase: 'http://127.0.0.1:8000/api/v1',
      token: '',
      mockCode: '',
      currentUser: null,
      roles: [],
      permissions: [],
      allRoles: [],
      adminUsers: [],
      loginForm: { phone: '13800138000', code: '' },
      statusOptions: [
        { label: '全部', value: '' },
        { label: '启用', value: 'active' },
        { label: '禁用', value: 'disabled' }
      ],
      adminQuery: { page: 1, page_size: 10, keyword: '', status: '' },
      loading: { sms: false, login: false }
    }
  },
  computed: {
    isLoggedIn() { return Boolean(this.token && this.currentUser) },
    avatarLetter() {
      const name = this.currentUser && this.currentUser.nickname
      return name ? name.slice(0, 1).toUpperCase() : 'P'
    },
    roleSummary() {
      return this.roles.length ? this.roles.map(role => role.name).join('、') : '暂无角色'
    },
    canManageUsers() {
      return this.permissions.some(permission => permission.code === 'user:manage')
    },
    statusFilterLabel() {
      const item = this.statusOptions.find(option => option.value === this.adminQuery.status)
      return item ? item.label : '全部'
    }
  },
  onLoad() {
    const savedBase = uni.getStorageSync('petShopApiBase')
    const savedToken = uni.getStorageSync('petShopToken')
    if (savedBase) this.apiBase = savedBase
    if (savedToken) {
      this.token = savedToken
      this.loadCurrentUser()
      this.loadRolesAndPermissions()
    }
  },
  onShow() {
    if (uni.getStorageSync('petShopProfileUpdated') && this.token) {
      uni.removeStorageSync('petShopProfileUpdated')
      this.loadCurrentUser()
    }
  },
  methods: {
    request(options) {
      const url = options.rawUrl || `${this.apiBase}${options.url}`
      const header = Object.assign({ 'content-type': 'application/json' }, this.token ? { Authorization: `Bearer ${this.token}` } : {})
      return new Promise((resolve, reject) => {
        uni.request({
          url,
          method: options.method || 'GET',
          data: options.data || {},
          header,
          success: response => {
            if (response.statusCode >= 200 && response.statusCode < 300 && response.data && response.data.code === 0) return resolve(response.data.data)
            reject(new Error(response.data && response.data.message ? response.data.message : '请求失败'))
          },
          fail: error => reject(new Error(error.errMsg || '网络连接失败'))
        })
      })
    },
    async sendSmsCode() {
      if (!this.loginForm.phone) return this.toast('请输入手机号')
      this.loading.sms = true
      try {
        const data = await this.request({ url: '/auth/sms/send', method: 'POST', data: { phone: this.loginForm.phone } })
        this.mockCode = data.code
        this.loginForm.code = data.code
        this.toast('验证码已返回')
      } catch (error) {
        this.toast(error.message)
      } finally {
        this.loading.sms = false
      }
    },
    async smsLogin() {
      if (!this.loginForm.phone || !this.loginForm.code) return this.toast('请输入手机号和验证码')
      this.loading.login = true
      try {
        const data = await this.request({ url: '/auth/sms/login', method: 'POST', data: this.loginForm })
        this.token = data.access_token
        this.currentUser = data.user
        uni.setStorageSync('petShopToken', this.token)
        await this.loadRolesAndPermissions()
        this.toast('登录成功')
        setTimeout(() => {
          uni.reLaunch({ url: '/pages/index/index' })
        }, 500)
      } catch (error) {
        this.toast(error.message)
      } finally {
        this.loading.login = false
      }
    },
    async loadCurrentUser() {
      if (!this.token) return
      try { this.currentUser = await this.request({ url: '/users/me' }) } catch (error) { this.toast(error.message) }
    },
    async loadRolesAndPermissions() {
      if (!this.token) return
      try {
        this.roles = await this.request({ url: '/users/me/roles' }) || []
        this.permissions = await this.request({ url: '/users/me/permissions' }) || []
        if (this.canManageUsers) {
          await this.loadAllRoles()
          await this.loadAdminUsers()
        }
      } catch (error) {
        this.toast(error.message)
      }
    },
    async loadAllRoles() {
      try { this.allRoles = await this.request({ url: '/roles' }) || [] } catch (error) { this.toast(error.message) }
    },
    async loadAdminUsers() {
      if (!this.canManageUsers) return
      const params = [`page=${this.adminQuery.page}`, `page_size=${this.adminQuery.page_size}`]
      if (this.adminQuery.keyword) params.push(`keyword=${encodeURIComponent(this.adminQuery.keyword)}`)
      if (this.adminQuery.status) params.push(`status=${this.adminQuery.status}`)
      try {
        const data = await this.request({ url: `/admin/users?${params.join('&')}` })
        this.adminUsers = (data.items || []).map(user => Object.assign({}, user, { roleDraft: (user.roles || []).map(role => role.code) }))
      } catch (error) {
        this.toast(error.message)
      }
    },
    searchAdminUsers() {
      this.adminQuery.page = 1
      this.loadAdminUsers()
    },
    onStatusFilterChange(event) {
      this.adminQuery.status = this.statusOptions[Number(event.detail.value)].value
    },
    toggleRoleDraft(user, roleCode) {
      user.roleDraft = user.roleDraft.includes(roleCode) ? user.roleDraft.filter(code => code !== roleCode) : user.roleDraft.concat(roleCode)
    },
    async saveUserRoles(user) {
      if (!user.roleDraft.length) return this.toast('至少保留一个角色')
      try {
        await this.request({ url: `/admin/users/${user.id}/roles`, method: 'PUT', data: { role_codes: user.roleDraft } })
        await this.loadAdminUsers()
        this.toast('角色已保存')
      } catch (error) {
        this.toast(error.message)
      }
    },
    async setAdminUserStatus(user, status) {
      try {
        await this.request({ url: `/admin/users/${user.id}/${status === 'active' ? 'enable' : 'disable'}`, method: 'POST' })
        await this.loadAdminUsers()
      } catch (error) {
        this.toast(error.message)
      }
    },
    goProfileEdit() { uni.navigateTo({ url: '/pages/account/profile' }) },
    goHome() { uni.reLaunch({ url: '/pages/index/index' }) },
    goBack() {
      const pages = getCurrentPages()
      if (pages.length > 1) return uni.navigateBack({ delta: 1 })
      this.goHome()
    },
    logout() {
      this.token = ''
      this.currentUser = null
      this.roles = []
      this.permissions = []
      this.allRoles = []
      this.adminUsers = []
      uni.removeStorageSync('petShopToken')
    },
    toast(title) { uni.showToast({ title, icon: 'none' }) }
  }
}
</script>

<style>
page { background: #f3f5f8; }
.account-page { min-height: 100vh; color: #172033; }
.account-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 22px 26px;
  border: 1px solid #e2e8ef;
  border-radius: 8px;
  background: #fff;
}
.title { display: block; font-size: 26px; font-weight: 700; }
.subtitle, .muted, .panel-note { display: block; margin-top: 6px; color: #6b7788; font-size: 14px; line-height: 1.55; }
.top-actions, .layout, .panel-head, .inline, .filter, .profile, .row-actions { display: flex; gap: 12px; }
.account-layout { align-items: stretch; margin-top: 18px; }
.panel { flex: 1; min-width: 0; padding: 22px; border: 1px solid #e2e8ef; border-radius: 8px; background: #fff; }
.login-panel { max-width: 520px; }
.panel-head { align-items: center; justify-content: space-between; margin-bottom: 18px; }
.panel-title { font-size: 18px; font-weight: 700; }
.field { margin-bottom: 14px; }
.grow { flex: 1; }
.label { display: block; margin-bottom: 8px; color: #667387; font-size: 13px; }
.input, .picker { width: 100%; height: 40px; padding: 0 12px; border: 1px solid #d9e0e8; border-radius: 6px; background: #fbfcfd; font-size: 14px; line-height: 40px; }
.fixed { width: 136px; margin-top: 27px; }
.primary, .secondary, .ghost, .danger, .role {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 36px;
  margin: 0;
  padding: 0 14px;
  border-radius: 6px;
  font-size: 14px;
  white-space: nowrap;
  box-sizing: border-box;
}
.primary { color: #fff; background: #1f6b57; }
.secondary, .ghost { color: #1f6b57; background: #e8f3ef; }
.danger { color: #a43333; background: #faeeee; }
.wide { width: 100%; height: 42px; margin-top: 14px; }
.code-box { display: flex; justify-content: space-between; padding: 12px; border-radius: 6px; background: #fff7e8; color: #8a5200; }
.code { font-size: 20px; font-weight: 700; }
.avatar { display: flex; align-items: center; justify-content: center; width: 56px; height: 56px; border-radius: 50%; color: #fff; background: #1f6b57; font-weight: 700; }
.profile { align-items: center; }
.profile-main { flex: 1; min-width: 0; }
.profile-name, .user-name { display: block; font-size: 16px; font-weight: 700; }
.profile-actions { display: flex; gap: 10px; }
.cards { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.mini-card { padding: 16px; border-radius: 8px; background: #f5f8f7; }
.mini-label { display: block; color: #6b7788; font-size: 13px; }
.mini-value { display: block; margin-top: 8px; font-size: 18px; font-weight: 700; }
.tag-list { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }
.tag { padding: 6px 10px; border-radius: 6px; color: #1f6b57; background: #e8f3ef; font-size: 12px; }
.filter { margin-bottom: 16px; }
.filter .input { flex: 1; }
.picker { width: 160px; }
.query { width: 90px; }
.user-table { border: 1px solid #edf1f5; border-radius: 8px; overflow: hidden; }
.user-row { display: grid; grid-template-columns: minmax(220px, 1.2fr) 110px minmax(260px, 1.4fr) minmax(230px, 280px); gap: 12px; align-items: center; padding: 12px 16px; border-bottom: 1px solid #edf1f5; }
.user-row:last-child { border-bottom: none; }
.head { color: #6b7788; background: #f7f9fb; font-weight: 700; }
.role-options { display: flex; flex-wrap: wrap; gap: 8px; min-width: 0; }
.row-actions { align-items: center; flex-wrap: nowrap; min-width: 0; }
.role { height: 30px; color: #526172; background: #f2f5f7; font-size: 12px; }
.role.selected { color: #1f6b57; background: #e8f3ef; }
.empty { padding: 42px 20px; color: #798493; text-align: center; }
@media screen and (max-width: 820px) {
  .account-topbar, .account-layout, .inline, .filter, .profile { flex-direction: column; align-items: stretch; }
  .login-panel { max-width: none; }
  .fixed, .picker, .query { width: 100%; }
  .user-row { grid-template-columns: 1fr; }
}
</style>
