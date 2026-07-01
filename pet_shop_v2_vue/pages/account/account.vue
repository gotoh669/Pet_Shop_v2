<template>
  <view class="page">
    <view class="panel">
      <text class="title">账号登录</text>
      <text class="subtitle">验证码为模拟发送，会直接显示在页面上</text>

      <view class="field">
        <text class="label">服务地址</text>
        <input class="input" v-model="apiBase" placeholder="http://127.0.0.1:8000/api/v1" />
      </view>
      <view class="field">
        <text class="label">手机号</text>
        <input class="input" v-model="phone" type="number" placeholder="请输入手机号" />
      </view>
      <view class="field">
        <text class="label">验证码</text>
        <input class="input" v-model="code" type="number" placeholder="6 位验证码" />
      </view>

      <view class="code-box" v-if="mockCode">
        <text>本次验证码：{{ mockCode }}</text>
      </view>

      <button class="secondary-button" @click="sendCode">发送验证码</button>
      <button class="primary-button" @click="login">登录</button>
    </view>

    <view class="panel" v-if="user">
      <text class="section-title">当前用户</text>
      <text class="user-line">{{ user.nickname }} · {{ user.phone }}</text>
      <text class="muted">角色：{{ roleText }}</text>
      <text class="muted">权限：{{ permissionText }}</text>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      apiBase: 'http://127.0.0.1:8000/api/v1',
      phone: '18800000000',
      code: '',
      mockCode: '',
      user: null,
      roles: [],
      permissions: []
    }
  },
  onLoad() {
    const savedBase = uni.getStorageSync('petShopApiBase')
    if (savedBase) {
      this.apiBase = savedBase
    }
    this.loadCurrentUser()
  },
  methods: {
    request(options) {
      const token = uni.getStorageSync('petShopToken')
      return new Promise((resolve, reject) => {
        uni.request({
          url: `${this.apiBase}${options.url}`,
          method: options.method || 'GET',
          data: options.data || {},
          header: Object.assign({ 'content-type': 'application/json' }, token ? { Authorization: `Bearer ${token}` } : {}),
          success: response => {
            if (response.statusCode >= 200 && response.statusCode < 300 && response.data && response.data.code === 0) {
              resolve(response.data.data)
              return
            }
            reject(new Error(response.data && response.data.message ? response.data.message : '请求失败'))
          },
          fail: error => reject(new Error(error.errMsg || '网络连接失败'))
        })
      })
    },
    async sendCode() {
      if (!this.phone) {
        this.toast('请输入手机号')
        return
      }
      try {
        uni.setStorageSync('petShopApiBase', this.apiBase)
        const data = await this.request({
          url: '/auth/sms/send',
          method: 'POST',
          data: { phone: this.phone }
        })
        this.mockCode = data.code
        this.code = data.code
        this.toast('验证码已返回')
      } catch (error) {
        this.toast(error.message)
      }
    },
    async login() {
      if (!this.phone || !this.code) {
        this.toast('请输入手机号和验证码')
        return
      }
      try {
        const data = await this.request({
          url: '/auth/sms/login',
          method: 'POST',
          data: { phone: this.phone, code: this.code }
        })
        uni.setStorageSync('petShopToken', data.access_token)
        this.user = data.user
        await this.loadRolesAndPermissions()
        this.toast('登录成功')
      } catch (error) {
        this.toast(error.message)
      }
    },
    async loadCurrentUser() {
      const token = uni.getStorageSync('petShopToken')
      if (!token) {
        return
      }
      try {
        this.user = await this.request({ url: '/users/me' })
        await this.loadRolesAndPermissions()
      } catch (error) {
        uni.removeStorageSync('petShopToken')
      }
    },
    async loadRolesAndPermissions() {
      this.roles = await this.request({ url: '/users/me/roles' }) || []
      this.permissions = await this.request({ url: '/users/me/permissions' }) || []
    },
    toast(title) {
      uni.showToast({ title, icon: 'none' })
    }
  },
  computed: {
    roleText() {
      return this.roles.length ? this.roles.map(role => role.name).join('、') : '普通用户'
    },
    permissionText() {
      return this.permissions.length ? this.permissions.map(permission => permission.code).join('、') : '暂无'
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
  padding: 24rpx;
  box-sizing: border-box;
}

.panel {
  padding: 28rpx;
  margin-bottom: 22rpx;
  border-radius: 8rpx;
  background: #ffffff;
}

.title {
  display: block;
  font-size: 36rpx;
  font-weight: 700;
}

.subtitle,
.muted {
  display: block;
  margin-top: 10rpx;
  color: #718093;
  font-size: 24rpx;
  line-height: 1.5;
}

.field {
  margin-top: 22rpx;
}

.label {
  display: block;
  margin-bottom: 10rpx;
  color: #667387;
  font-size: 23rpx;
}

.input {
  height: 78rpx;
  padding: 0 22rpx;
  border: 1rpx solid #d9e0e8;
  border-radius: 8rpx;
  background: #fbfcfd;
  font-size: 26rpx;
  box-sizing: border-box;
}

.code-box {
  margin-top: 22rpx;
  padding: 18rpx;
  border-radius: 8rpx;
  background: #fff7e8;
  color: #9b5b09;
  font-size: 25rpx;
}

.primary-button,
.secondary-button {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 78rpx;
  margin: 22rpx 0 0;
  border-radius: 8rpx;
  font-size: 26rpx;
}

.primary-button {
  color: #ffffff;
  background: #1c6b56;
}

.secondary-button {
  color: #1c6b56;
  background: #e8f3ef;
}

.section-title {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
}

.user-line {
  display: block;
  margin-top: 14rpx;
  font-size: 26rpx;
}
</style>
