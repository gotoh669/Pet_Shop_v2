<template>
  <view class="page">
    <view class="topbar">
      <view class="brand">
        <image class="brand-logo" src="/static/logo.png" mode="aspectFit"></image>
        <view>
          <text class="brand-title">Pet Shop 管理台</text>
          <text class="brand-subtitle">基础工程与用户模块</text>
        </view>
      </view>
      <view class="server-pill" :class="{ online: healthOk }">
        <text class="dot"></text>
        <text>{{ healthText }}</text>
      </view>
    </view>

    <scroll-view class="workspace" scroll-y>
      <view class="api-panel panel">
        <view class="panel-head">
          <text class="panel-title">服务地址</text>
          <button class="icon-button" @click="checkHealth">↻</button>
        </view>
        <input class="field-input" v-model="apiBase" placeholder="http://127.0.0.1:8000/api/v1" />
      </view>

      <view class="grid">
        <view class="panel">
          <view class="panel-head">
            <text class="panel-title">短信登录</text>
            <text class="panel-note">模拟验证码会直接返回</text>
          </view>

          <view class="form">
            <view class="field">
              <text class="field-label">手机号</text>
              <input class="field-input" v-model="loginForm.phone" type="number" placeholder="请输入手机号" />
            </view>

            <view class="inline-actions">
              <view class="field flex-field">
                <text class="field-label">验证码</text>
                <input class="field-input" v-model="loginForm.code" type="number" placeholder="6 位验证码" />
              </view>
              <button class="secondary-button" :disabled="loading.sms" @click="sendSmsCode">
                {{ loading.sms ? '发送中' : '发送验证码' }}
              </button>
            </view>

            <view class="code-box" v-if="mockCode">
              <text class="field-label">本次验证码</text>
              <text class="mock-code">{{ mockCode }}</text>
            </view>

            <button class="primary-button" :disabled="loading.login" @click="smsLogin">
              {{ loading.login ? '登录中' : '登录并获取 Token' }}
            </button>
          </view>
        </view>

        <view class="panel">
          <view class="panel-head">
            <text class="panel-title">用户资料</text>
            <button class="text-button" :disabled="!token" @click="loadCurrentUser">刷新</button>
          </view>

          <view class="profile-card" v-if="currentUser">
            <view class="avatar">{{ avatarLetter }}</view>
            <view class="profile-meta">
              <text class="profile-name">{{ currentUser.nickname }}</text>
              <text class="muted">{{ currentUser.phone }}</text>
            </view>
          </view>

          <view class="empty-state" v-else>
            <text>登录后显示用户资料</text>
          </view>

          <view class="form compact">
            <view class="field">
              <text class="field-label">昵称</text>
              <input class="field-input" v-model="profileForm.nickname" placeholder="昵称" />
            </view>
            <view class="field">
              <text class="field-label">城市</text>
              <input class="field-input" v-model="profileForm.city" placeholder="城市" />
            </view>
            <view class="field">
              <text class="field-label">签名</text>
              <input class="field-input" v-model="profileForm.bio" placeholder="个性签名" />
            </view>
            <view class="split-row">
              <view class="field half">
                <text class="field-label">性别</text>
                <picker :range="genderOptions" range-key="label" @change="onGenderChange">
                  <view class="picker-input">{{ genderLabel }}</view>
                </picker>
              </view>
              <view class="field half">
                <text class="field-label">是否养宠</text>
                <view class="switch-line">
                  <switch :checked="profileForm.has_pet" color="#1c6b56" @change="onHasPetChange" />
                  <text class="switch-text">{{ profileForm.has_pet ? '已养宠' : '暂未养宠' }}</text>
                </view>
              </view>
            </view>
            <view class="split-row">
              <view class="field half">
                <text class="field-label">宠物数</text>
                <input class="field-input" v-model.number="profileForm.pet_count" type="number" />
              </view>
            </view>
            <button class="primary-button" :disabled="!token || loading.profile" @click="saveProfile">
              {{ loading.profile ? '保存中' : '保存资料' }}
            </button>
          </view>
        </view>
      </view>

      <view class="grid lower">
        <view class="panel">
          <view class="panel-head">
            <text class="panel-title">角色</text>
            <button class="text-button" :disabled="!token" @click="loadRolesAndPermissions">刷新</button>
          </view>
          <view class="tag-list" v-if="roles.length">
            <view class="tag" v-for="role in roles" :key="role.code">
              <text>{{ role.name }}</text>
              <text class="tag-code">{{ role.code }}</text>
            </view>
          </view>
          <view class="empty-state" v-else>
            <text>暂无角色</text>
          </view>
        </view>

        <view class="panel">
          <view class="panel-head">
            <text class="panel-title">权限</text>
            <text class="panel-note">{{ permissions.length }} 项</text>
          </view>
          <view class="permission-list" v-if="permissions.length">
            <view class="permission-item" v-for="permission in permissions" :key="permission.code">
              <text class="permission-name">{{ permission.name }}</text>
              <text class="permission-code">{{ permission.code }}</text>
            </view>
          </view>
          <view class="empty-state" v-else>
            <text>暂无权限</text>
          </view>
        </view>
      </view>

      <view class="panel" v-if="canManageUsers">
        <view class="panel-head">
          <view>
            <text class="panel-title">用户管理</text>
            <text class="panel-note admin-note">管理员接口 /api/v1/admin/users</text>
          </view>
          <button class="text-button" :disabled="loading.adminUsers" @click="loadAdminUsers">
            {{ loading.adminUsers ? '加载中' : '刷新' }}
          </button>
        </view>

        <view class="admin-toolbar">
          <view class="field search-field">
            <text class="field-label">搜索</text>
            <input class="field-input" v-model="adminQuery.keyword" placeholder="手机号 / 昵称" />
          </view>
          <view class="field status-field">
            <text class="field-label">状态</text>
            <picker :range="statusOptions" range-key="label" @change="onStatusFilterChange">
              <view class="picker-input">{{ statusFilterLabel }}</view>
            </picker>
          </view>
          <button class="secondary-button admin-search-button" @click="searchAdminUsers">查询</button>
        </view>

        <view class="admin-list" v-if="adminUsers.length">
          <view class="user-row" v-for="user in adminUsers" :key="user.id">
            <view class="user-main">
              <view class="avatar small">{{ user.nickname ? user.nickname.slice(0, 1).toUpperCase() : 'U' }}</view>
              <view class="user-info">
                <view class="user-line">
                  <text class="user-name">{{ user.nickname }}</text>
                  <text class="status-badge" :class="{ disabled: user.status !== 'active' }">{{ user.status }}</text>
                </view>
                <text class="muted">{{ user.phone }} · ID {{ user.id }}</text>
                <text class="muted">登录：{{ formatDate(user.last_login_at) }}</text>
              </view>
            </view>

            <view class="role-editor">
              <view class="role-options">
                <button
                  class="role-option"
                  :class="{ selected: user.roleDraft.includes(role.code) }"
                  v-for="role in allRoles"
                  :key="role.code"
                  @click="toggleRoleDraft(user, role.code)"
                >
                  {{ role.name }}
                </button>
              </view>
              <view class="row-actions">
                <button class="text-button" @click="saveUserRoles(user)">保存角色</button>
                <button
                  class="danger-button"
                  v-if="user.status === 'active'"
                  @click="setAdminUserStatus(user, 'disabled')"
                >
                  禁用
                </button>
                <button class="text-button" v-else @click="setAdminUserStatus(user, 'active')">
                  启用
                </button>
              </view>
            </view>
          </view>
        </view>

        <view class="empty-state" v-else>
          <text>暂无用户数据</text>
        </view>

        <view class="pagination">
          <button class="text-button" :disabled="adminQuery.page <= 1" @click="changeAdminPage(-1)">上一页</button>
          <text class="page-text">{{ adminPageText }}</text>
          <button class="text-button" :disabled="adminQuery.page >= adminTotalPages" @click="changeAdminPage(1)">下一页</button>
        </view>
      </view>

      <view class="panel">
        <view class="panel-head">
          <text class="panel-title">接口响应</text>
          <button class="text-button" @click="clearLog">清空</button>
        </view>
        <view class="token-box" v-if="token">
          <text class="field-label">Access Token</text>
          <text class="token-text">{{ token }}</text>
        </view>
        <scroll-view class="log-box" scroll-y>
          <text class="log-text">{{ requestLog || '暂无请求记录' }}</text>
        </scroll-view>
      </view>
    </scroll-view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      apiBase: 'http://127.0.0.1:8000/api/v1',
      healthOk: false,
      healthText: '未连接',
      token: '',
      mockCode: '',
      currentUser: null,
      roles: [],
      permissions: [],
      allRoles: [],
      adminUsers: [],
      adminTotal: 0,
      requestLog: '',
      loginForm: {
        phone: '13800138000',
        code: ''
      },
      profileForm: {
        nickname: '',
        city: '',
        bio: '',
        gender: 'unknown',
        has_pet: false,
        pet_count: 0
      },
      genderOptions: [
        { label: '未知', value: 'unknown' },
        { label: '男', value: 'male' },
        { label: '女', value: 'female' }
      ],
      statusOptions: [
        { label: '全部', value: '' },
        { label: '启用', value: 'active' },
        { label: '禁用', value: 'disabled' }
      ],
      adminQuery: {
        page: 1,
        page_size: 10,
        keyword: '',
        status: ''
      },
      loading: {
        sms: false,
        login: false,
        profile: false,
        adminUsers: false,
        adminAction: false
      }
    }
  },
  computed: {
    avatarLetter() {
      const name = this.currentUser && this.currentUser.nickname
      return name ? name.slice(0, 1).toUpperCase() : 'P'
    },
    genderLabel() {
      const item = this.genderOptions.find(option => option.value === this.profileForm.gender)
      return item ? item.label : '未知'
    },
    statusFilterLabel() {
      const item = this.statusOptions.find(option => option.value === this.adminQuery.status)
      return item ? item.label : '全部'
    },
    canManageUsers() {
      return this.permissions.some(permission => permission.code === 'user:manage')
    },
    adminTotalPages() {
      return Math.max(1, Math.ceil(this.adminTotal / this.adminQuery.page_size))
    },
    adminPageText() {
      return `第 ${this.adminQuery.page} / ${this.adminTotalPages} 页，共 ${this.adminTotal} 人`
    }
  },
  onLoad() {
    const savedBase = uni.getStorageSync('petShopApiBase')
    const savedToken = uni.getStorageSync('petShopToken')
    if (savedBase) {
      this.apiBase = savedBase
    }
    if (savedToken) {
      this.token = savedToken
      this.loadCurrentUser()
      this.loadRolesAndPermissions()
    }
    this.checkHealth()
  },
  methods: {
    request(options) {
      const url = options.rawUrl || `${this.apiBase}${options.url}`
      const header = Object.assign(
        { 'content-type': 'application/json' },
        this.token ? { Authorization: `Bearer ${this.token}` } : {},
        options.header || {}
      )

      return new Promise((resolve, reject) => {
        uni.request({
          url,
          method: options.method || 'GET',
          data: options.data || {},
          header,
          success: response => {
            this.writeLog(options.method || 'GET', url, response.data)
            if (response.statusCode >= 200 && response.statusCode < 300 && response.data && response.data.code === 0) {
              resolve(response.data.data)
              return
            }
            const message = response.data && response.data.message ? response.data.message : '请求失败'
            reject(new Error(message))
          },
          fail: error => {
            this.writeLog(options.method || 'GET', url, error)
            reject(new Error(error.errMsg || '网络连接失败'))
          }
        })
      })
    },
    async checkHealth() {
      const root = this.apiBase.replace(/\/api\/v1\/?$/, '')
      try {
        const data = await this.request({ rawUrl: `${root}/health` })
        this.healthOk = data && data.status === 'ok'
        this.healthText = this.healthOk ? '服务在线' : '服务异常'
      } catch (error) {
        this.healthOk = false
        this.healthText = '未连接'
      }
    },
    async sendSmsCode() {
      if (!this.loginForm.phone) {
        this.toast('请输入手机号')
        return
      }
      this.loading.sms = true
      try {
        uni.setStorageSync('petShopApiBase', this.apiBase)
        const data = await this.request({
          url: '/auth/sms/send',
          method: 'POST',
          data: { phone: this.loginForm.phone }
        })
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
      if (!this.loginForm.phone || !this.loginForm.code) {
        this.toast('请输入手机号和验证码')
        return
      }
      this.loading.login = true
      try {
        const data = await this.request({
          url: '/auth/sms/login',
          method: 'POST',
          data: {
            phone: this.loginForm.phone,
            code: this.loginForm.code
          }
        })
        this.token = data.access_token
        uni.setStorageSync('petShopToken', this.token)
        this.currentUser = data.user
        this.syncProfile(data.user)
        await this.loadRolesAndPermissions()
        this.toast('登录成功')
      } catch (error) {
        this.toast(error.message)
      } finally {
        this.loading.login = false
      }
    },
    async loadCurrentUser() {
      if (!this.token) {
        return
      }
      try {
        const data = await this.request({ url: '/users/me' })
        this.currentUser = data
        this.syncProfile(data)
      } catch (error) {
        this.toast(error.message)
      }
    },
    async saveProfile() {
      if (!this.token) {
        this.toast('请先登录')
        return
      }
      this.loading.profile = true
      try {
        const data = await this.request({
          url: '/users/me',
          method: 'PUT',
          data: this.profileForm
        })
        this.currentUser = data
        this.syncProfile(data)
        this.toast('资料已保存')
      } catch (error) {
        this.toast(error.message)
      } finally {
        this.loading.profile = false
      }
    },
    async loadRolesAndPermissions() {
      if (!this.token) {
        return
      }
      try {
        const roles = await this.request({ url: '/users/me/roles' })
        const permissions = await this.request({ url: '/users/me/permissions' })
        this.roles = roles || []
        this.permissions = permissions || []
        if (this.canManageUsers) {
          await this.loadAllRoles()
          await this.loadAdminUsers()
        } else {
          this.adminUsers = []
          this.adminTotal = 0
        }
      } catch (error) {
        this.toast(error.message)
      }
    },
    async loadAllRoles() {
      if (!this.token) {
        return
      }
      try {
        const roles = await this.request({ url: '/roles' })
        this.allRoles = roles || []
      } catch (error) {
        this.toast(error.message)
      }
    },
    async loadAdminUsers() {
      if (!this.canManageUsers) {
        return
      }
      this.loading.adminUsers = true
      const params = [
        `page=${this.adminQuery.page}`,
        `page_size=${this.adminQuery.page_size}`
      ]
      if (this.adminQuery.keyword) {
        params.push(`keyword=${encodeURIComponent(this.adminQuery.keyword)}`)
      }
      if (this.adminQuery.status) {
        params.push(`status=${encodeURIComponent(this.adminQuery.status)}`)
      }
      try {
        const data = await this.request({ url: `/admin/users?${params.join('&')}` })
        this.adminTotal = data.total || 0
        this.adminUsers = (data.items || []).map(user => this.normalizeAdminUser(user))
      } catch (error) {
        this.toast(error.message)
      } finally {
        this.loading.adminUsers = false
      }
    },
    searchAdminUsers() {
      this.adminQuery.page = 1
      this.loadAdminUsers()
    },
    changeAdminPage(delta) {
      const nextPage = this.adminQuery.page + delta
      if (nextPage < 1 || nextPage > this.adminTotalPages) {
        return
      }
      this.adminQuery.page = nextPage
      this.loadAdminUsers()
    },
    onStatusFilterChange(event) {
      const index = Number(event.detail.value)
      this.adminQuery.status = this.statusOptions[index].value
    },
    normalizeAdminUser(user) {
      return Object.assign({}, user, {
        roleDraft: (user.roles || []).map(role => role.code)
      })
    },
    replaceAdminUser(updatedUser) {
      const normalized = this.normalizeAdminUser(updatedUser)
      this.adminUsers = this.adminUsers.map(user => (
        user.id === normalized.id ? normalized : user
      ))
    },
    toggleRoleDraft(user, roleCode) {
      if (user.roleDraft.includes(roleCode)) {
        user.roleDraft = user.roleDraft.filter(code => code !== roleCode)
      } else {
        user.roleDraft = user.roleDraft.concat(roleCode)
      }
    },
    async saveUserRoles(user) {
      if (!user.roleDraft.length) {
        this.toast('至少保留一个角色')
        return
      }
      try {
        const data = await this.request({
          url: `/admin/users/${user.id}/roles`,
          method: 'PUT',
          data: { role_codes: user.roleDraft }
        })
        this.replaceAdminUser(data)
        if (this.currentUser && this.currentUser.id === data.id) {
          await this.loadRolesAndPermissions()
        }
        this.toast('角色已保存')
      } catch (error) {
        this.toast(error.message)
      }
    },
    async setAdminUserStatus(user, status) {
      try {
        const data = await this.request({
          url: `/admin/users/${user.id}/${status === 'active' ? 'enable' : 'disable'}`,
          method: 'POST'
        })
        this.replaceAdminUser(data)
        this.toast(status === 'active' ? '用户已启用' : '用户已禁用')
      } catch (error) {
        this.toast(error.message)
      }
    },
    syncProfile(user) {
      this.profileForm = {
        nickname: user.nickname || '',
        city: user.city || '',
        bio: user.bio || '',
        gender: user.gender || 'unknown',
        has_pet: Boolean(user.has_pet),
        pet_count: Number(user.pet_count || 0)
      }
    },
    onGenderChange(event) {
      const index = Number(event.detail.value)
      this.profileForm.gender = this.genderOptions[index].value
    },
    onHasPetChange(event) {
      this.profileForm.has_pet = Boolean(event.detail.value)
    },
    formatDate(value) {
      if (!value) {
        return '暂无'
      }
      return String(value).replace('T', ' ').slice(0, 19)
    },
    writeLog(method, url, data) {
      const time = new Date().toLocaleTimeString()
      const content = JSON.stringify(data, null, 2)
      this.requestLog = `[${time}] ${method} ${url}\n${content}\n\n${this.requestLog}`.slice(0, 6000)
    },
    clearLog() {
      this.requestLog = ''
    },
    toast(title) {
      uni.showToast({
        title,
        icon: 'none'
      })
    }
  }
}
</script>

<style>
page {
  background: #f4f6f8;
}

.page {
  min-height: 100vh;
  color: #18202c;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28rpx 32rpx;
  background: #ffffff;
  border-bottom: 1rpx solid #e7ebef;
}

.brand {
  display: flex;
  align-items: center;
  min-width: 0;
}

.brand-logo {
  width: 72rpx;
  height: 72rpx;
  margin-right: 20rpx;
}

.brand-title {
  display: block;
  font-size: 34rpx;
  font-weight: 700;
  color: #162033;
}

.brand-subtitle {
  display: block;
  margin-top: 6rpx;
  font-size: 22rpx;
  color: #687485;
}

.server-pill {
  display: flex;
  align-items: center;
  height: 52rpx;
  padding: 0 18rpx;
  border-radius: 26rpx;
  background: #eef1f4;
  color: #6d7785;
  font-size: 22rpx;
  white-space: nowrap;
}

.server-pill.online {
  background: #e3f6ec;
  color: #16834b;
}

.dot {
  width: 12rpx;
  height: 12rpx;
  margin-right: 10rpx;
  border-radius: 50%;
  background: currentColor;
}

.workspace {
  height: calc(100vh - 129rpx);
  box-sizing: border-box;
  padding: 28rpx;
}

.grid {
  display: flex;
  gap: 24rpx;
}

.grid > .panel {
  flex: 1;
  min-width: 0;
}

.lower {
  margin-top: 24rpx;
}

.panel {
  box-sizing: border-box;
  padding: 28rpx;
  margin-bottom: 24rpx;
  border: 1rpx solid #e2e8ef;
  border-radius: 8rpx;
  background: #ffffff;
}

.api-panel {
  margin-bottom: 24rpx;
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 22rpx;
}

.panel-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #18202c;
}

.panel-note {
  display: block;
  font-size: 22rpx;
  color: #7a8492;
}

.admin-note {
  margin-top: 8rpx;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}

.compact {
  margin-top: 20rpx;
}

.field {
  min-width: 0;
}

.flex-field {
  flex: 1;
}

.field-label {
  display: block;
  margin-bottom: 10rpx;
  font-size: 22rpx;
  color: #667387;
}

.field-input,
.picker-input {
  box-sizing: border-box;
  width: 100%;
  height: 78rpx;
  padding: 0 22rpx;
  border: 1rpx solid #d9e0e8;
  border-radius: 8rpx;
  background: #fbfcfd;
  color: #172033;
  font-size: 26rpx;
  line-height: 78rpx;
}

.inline-actions {
  display: flex;
  align-items: flex-end;
  gap: 18rpx;
}

.split-row {
  display: flex;
  gap: 18rpx;
}

.half {
  flex: 1;
}

.primary-button,
.secondary-button,
.text-button,
.icon-button {
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  margin: 0;
  border-radius: 8rpx;
  font-size: 26rpx;
}

.primary-button {
  height: 82rpx;
  color: #ffffff;
  background: #1c6b56;
}

.secondary-button {
  width: 184rpx;
  height: 78rpx;
  color: #1c6b56;
  background: #e8f3ef;
}

.text-button,
.icon-button {
  height: 48rpx;
  padding: 0 18rpx;
  color: #1c6b56;
  background: #edf5f2;
  font-size: 22rpx;
}

.icon-button {
  width: 52rpx;
  padding: 0;
  font-size: 28rpx;
}

button[disabled] {
  opacity: 0.55;
}

.code-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18rpx 20rpx;
  border-radius: 8rpx;
  background: #fff7e8;
}

.mock-code {
  font-size: 38rpx;
  font-weight: 700;
  color: #a55b00;
  letter-spacing: 0;
}

.profile-card {
  display: flex;
  align-items: center;
  padding: 8rpx 0 12rpx;
}

.avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 84rpx;
  height: 84rpx;
  margin-right: 18rpx;
  border-radius: 50%;
  background: #1c6b56;
  color: #ffffff;
  font-size: 32rpx;
  font-weight: 700;
}

.profile-meta {
  min-width: 0;
}

.profile-name {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  color: #172033;
}

.muted {
  display: block;
  margin-top: 8rpx;
  font-size: 23rpx;
  color: #718093;
}

.empty-state {
  padding: 34rpx 20rpx;
  border-radius: 8rpx;
  background: #f7f9fb;
  color: #798493;
  font-size: 24rpx;
  text-align: center;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 14rpx;
}

.tag {
  display: flex;
  flex-direction: column;
  min-width: 150rpx;
  padding: 16rpx 18rpx;
  border-radius: 8rpx;
  background: #eef7f3;
  color: #1c6b56;
  font-size: 25rpx;
}

.tag-code {
  margin-top: 6rpx;
  font-size: 21rpx;
  color: #5b7d72;
}

.permission-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.permission-item {
  box-sizing: border-box;
  flex: 1 1 46%;
  min-height: 82rpx;
  padding: 14rpx 16rpx;
  border: 1rpx solid #e1e7ed;
  border-radius: 8rpx;
  background: #fbfcfd;
}

.permission-name {
  display: block;
  font-size: 24rpx;
  color: #1f2a39;
}

.permission-code {
  display: block;
  margin-top: 8rpx;
  font-size: 20rpx;
  color: #738094;
}

.admin-toolbar {
  display: flex;
  align-items: flex-end;
  gap: 18rpx;
  margin-bottom: 22rpx;
}

.search-field {
  flex: 1;
}

.status-field {
  width: 210rpx;
}

.admin-search-button {
  width: 132rpx;
}

.admin-list {
  border: 1rpx solid #e4eaf0;
  border-radius: 8rpx;
  overflow: hidden;
}

.user-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20rpx;
  padding: 22rpx;
  border-bottom: 1rpx solid #e8edf2;
  background: #ffffff;
}

.user-row:last-child {
  border-bottom: none;
}

.user-main {
  display: flex;
  flex: 1;
  min-width: 0;
}

.avatar.small {
  width: 68rpx;
  height: 68rpx;
  font-size: 26rpx;
}

.user-info {
  min-width: 0;
}

.user-line {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12rpx;
}

.user-name {
  font-size: 28rpx;
  font-weight: 700;
  color: #172033;
}

.status-badge {
  height: 38rpx;
  padding: 0 14rpx;
  border-radius: 19rpx;
  background: #e6f6ec;
  color: #19804e;
  font-size: 20rpx;
  line-height: 38rpx;
}

.status-badge.disabled {
  background: #f1f3f5;
  color: #7b8490;
}

.role-editor {
  width: 520rpx;
}

.role-options {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
}

.role-option {
  height: 50rpx;
  padding: 0 16rpx;
  margin: 0;
  border-radius: 8rpx;
  background: #f2f5f7;
  color: #526172;
  font-size: 22rpx;
  line-height: 50rpx;
}

.role-option.selected {
  background: #e2f2ec;
  color: #1c6b56;
}

.row-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12rpx;
  margin-top: 16rpx;
}

.danger-button {
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  height: 48rpx;
  padding: 0 18rpx;
  margin: 0;
  border-radius: 8rpx;
  color: #a43333;
  background: #faeeee;
  font-size: 22rpx;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 18rpx;
  margin-top: 20rpx;
}

.page-text {
  color: #647285;
  font-size: 23rpx;
}

.token-box {
  padding: 18rpx;
  margin-bottom: 18rpx;
  border-radius: 8rpx;
  background: #f4f8f7;
}

.token-text {
  display: block;
  word-break: break-all;
  font-size: 21rpx;
  line-height: 1.5;
  color: #315b50;
}

.log-box {
  height: 280rpx;
  padding: 18rpx;
  border-radius: 8rpx;
  background: #101721;
  box-sizing: border-box;
}

.log-text {
  white-space: pre-wrap;
  word-break: break-all;
  color: #d9e7f2;
  font-size: 21rpx;
  line-height: 1.55;
}

.switch-line {
  display: flex;
  align-items: center;
  height: 78rpx;
}

.switch-text {
  margin-left: 14rpx;
  color: #526172;
  font-size: 24rpx;
}

@media screen and (max-width: 700px) {
  .topbar {
    align-items: flex-start;
    flex-direction: column;
    gap: 18rpx;
  }

  .workspace {
    height: calc(100vh - 190rpx);
    padding: 20rpx;
  }

  .grid {
    flex-direction: column;
    gap: 0;
  }

  .permission-item {
    flex-basis: 100%;
  }

  .inline-actions,
  .split-row,
  .admin-toolbar,
  .user-row {
    flex-direction: column;
    align-items: stretch;
  }

  .secondary-button {
    width: 100%;
  }

  .status-field,
  .admin-search-button,
  .role-editor {
    width: 100%;
  }

  .row-actions,
  .pagination {
    justify-content: flex-start;
    flex-wrap: wrap;
  }
}
</style>
