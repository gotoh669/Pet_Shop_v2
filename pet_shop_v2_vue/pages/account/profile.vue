<template>
  <view class="page">
    <view class="topbar">
      <view>
        <text class="title">资料编辑</text>
        <text class="subtitle">修改当前登录账号的个人资料</text>
      </view>
      <button class="text-button" @click="goBack">返回</button>
    </view>

    <view class="panel">
      <view class="profile-card" v-if="currentUser">
        <view class="avatar">{{ avatarLetter }}</view>
        <view class="profile-meta">
          <text class="profile-name">{{ currentUser.nickname || '未命名用户' }}</text>
          <text class="muted">{{ currentUser.phone }}</text>
        </view>
      </view>

      <view class="form">
        <view class="field">
          <text class="field-label">服务地址</text>
          <input class="field-input" v-model="apiBase" placeholder="http://127.0.0.1:8000/api/v1" />
        </view>
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
        <view class="field">
          <text class="field-label">宠物数</text>
          <input class="field-input" v-model.number="profileForm.pet_count" type="number" />
        </view>

        <view class="form-actions">
          <button class="secondary-button" @click="goBack">取消</button>
          <button class="primary-button" :disabled="loading" @click="saveProfile">
            {{ loading ? '保存中' : '保存资料' }}
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      apiBase: 'http://127.0.0.1:8000/api/v1',
      token: '',
      loading: false,
      currentUser: null,
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
      ]
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
    }
  },
  onLoad() {
    const savedBase = uni.getStorageSync('petShopApiBase')
    const savedToken = uni.getStorageSync('petShopToken')
    if (savedBase) {
      this.apiBase = savedBase
    }
    if (!savedToken) {
      this.toast('请先登录')
      setTimeout(() => this.goBack(), 600)
      return
    }
    this.token = savedToken
    this.loadCurrentUser()
  },
  methods: {
    request(options) {
      return new Promise((resolve, reject) => {
        uni.request({
          url: `${this.apiBase}${options.url}`,
          method: options.method || 'GET',
          data: options.data || {},
          header: {
            'content-type': 'application/json',
            Authorization: `Bearer ${this.token}`
          },
          success: response => {
            if (response.statusCode >= 200 && response.statusCode < 300 && response.data && response.data.code === 0) {
              resolve(response.data.data)
              return
            }
            const message = response.data && response.data.message ? response.data.message : '请求失败'
            reject(new Error(message))
          },
          fail: error => reject(new Error(error.errMsg || '网络连接失败'))
        })
      })
    },
    async loadCurrentUser() {
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
      this.loading = true
      try {
        uni.setStorageSync('petShopApiBase', this.apiBase)
        const data = await this.request({
          url: '/users/me',
          method: 'PUT',
          data: this.profileForm
        })
        this.currentUser = data
        this.syncProfile(data)
        uni.setStorageSync('petShopProfileUpdated', String(Date.now()))
        this.toast('资料已保存')
        setTimeout(() => this.goBack(), 500)
      } catch (error) {
        this.toast(error.message)
      } finally {
        this.loading = false
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
    goBack() {
      const pages = getCurrentPages()
      if (pages.length > 1) {
        uni.navigateBack({ delta: 1 })
        return
      }
      uni.switchTab({ url: '/pages/account/account' })
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
  padding: 28rpx;
  box-sizing: border-box;
  color: #18202c;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24rpx;
}

.title {
  display: block;
  font-size: 36rpx;
  font-weight: 700;
  color: #162033;
}

.subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 23rpx;
  color: #687485;
}

.panel {
  box-sizing: border-box;
  padding: 28rpx;
  border: 1rpx solid #e2e8ef;
  border-radius: 8rpx;
  background: #ffffff;
}

.profile-card {
  display: flex;
  align-items: center;
  padding-bottom: 24rpx;
  margin-bottom: 24rpx;
  border-bottom: 1rpx solid #edf1f5;
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

.form {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}

.field {
  min-width: 0;
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

.split-row {
  display: flex;
  gap: 18rpx;
}

.half {
  flex: 1;
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

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16rpx;
  margin-top: 6rpx;
}

.primary-button,
.secondary-button,
.text-button {
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  margin: 0;
  border-radius: 8rpx;
  font-size: 26rpx;
}

.primary-button {
  width: 260rpx;
  height: 82rpx;
  color: #ffffff;
  background: #1c6b56;
}

.secondary-button {
  width: 180rpx;
  height: 82rpx;
  color: #1c6b56;
  background: #e8f3ef;
}

.text-button {
  height: 52rpx;
  padding: 0 20rpx;
  color: #1c6b56;
  background: #edf5f2;
  font-size: 23rpx;
}

button[disabled] {
  opacity: 0.55;
}

@media screen and (max-width: 700px) {
  .page {
    padding: 20rpx;
  }

  .topbar,
  .split-row,
  .form-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .primary-button,
  .secondary-button {
    width: 100%;
  }
}
</style>
