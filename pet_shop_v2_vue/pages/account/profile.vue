<template>
  <view class="page">
    <view class="topbar">
      <view>
        <text class="title">资料编辑</text>
        <text class="subtitle">维护当前登录账号资料</text>
      </view>
      <button class="ghost" @click="goBack">返回</button>
    </view>

    <view class="panel">
      <view class="form-grid">
        <view class="field">
          <text class="label">服务地址</text>
          <input class="input" v-model="apiBase" placeholder="http://127.0.0.1:8000/api/v1" />
        </view>
        <view class="field">
          <text class="label">昵称</text>
          <input class="input" v-model="profileForm.nickname" placeholder="请输入昵称" />
        </view>
        <view class="field">
          <text class="label">城市</text>
          <input class="input" v-model="profileForm.city" placeholder="所在城市" />
        </view>
        <view class="field">
          <text class="label">性别</text>
          <picker :range="genderOptions" range-key="label" @change="onGenderChange">
            <view class="picker">{{ genderLabel }}</view>
          </picker>
        </view>
        <view class="field">
          <text class="label">宠物数量</text>
          <input class="input" v-model.number="profileForm.pet_count" type="number" />
        </view>
        <view class="field">
          <text class="label">是否养宠</text>
          <view class="switch-line">
            <switch :checked="profileForm.has_pet" color="#1f6b57" @change="onHasPetChange" />
            <text>{{ profileForm.has_pet ? '已养宠' : '暂未养宠' }}</text>
          </view>
        </view>
      </view>
      <view class="field">
        <text class="label">个性签名</text>
        <textarea class="textarea" v-model="profileForm.bio" placeholder="填写一句个人介绍"></textarea>
      </view>
      <view class="actions">
        <button class="secondary" @click="goBack">取消</button>
        <button class="primary" :disabled="loading" @click="saveProfile">{{ loading ? '保存中' : '保存资料' }}</button>
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
      profileForm: { nickname: '', city: '', bio: '', gender: 'unknown', has_pet: false, pet_count: 0 },
      genderOptions: [
        { label: '未知', value: 'unknown' },
        { label: '男', value: 'male' },
        { label: '女', value: 'female' }
      ]
    }
  },
  computed: {
    genderLabel() {
      const item = this.genderOptions.find(option => option.value === this.profileForm.gender)
      return item ? item.label : '未知'
    }
  },
  onLoad() {
    const savedBase = uni.getStorageSync('petShopApiBase')
    const savedToken = uni.getStorageSync('petShopToken')
    if (savedBase) this.apiBase = savedBase
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
          header: { 'content-type': 'application/json', Authorization: `Bearer ${this.token}` },
          success: response => {
            if (response.statusCode >= 200 && response.statusCode < 300 && response.data && response.data.code === 0) return resolve(response.data.data)
            reject(new Error(response.data && response.data.message ? response.data.message : '请求失败'))
          },
          fail: error => reject(new Error(error.errMsg || '网络连接失败'))
        })
      })
    },
    async loadCurrentUser() {
      try {
        const user = await this.request({ url: '/users/me' })
        this.profileForm = {
          nickname: user.nickname || '',
          city: user.city || '',
          bio: user.bio || '',
          gender: user.gender || 'unknown',
          has_pet: Boolean(user.has_pet),
          pet_count: Number(user.pet_count || 0)
        }
      } catch (error) {
        this.toast(error.message)
      }
    },
    async saveProfile() {
      this.loading = true
      try {
        uni.setStorageSync('petShopApiBase', this.apiBase)
        await this.request({ url: '/users/me', method: 'PUT', data: this.profileForm })
        uni.setStorageSync('petShopProfileUpdated', String(Date.now()))
        this.toast('资料已保存')
        setTimeout(() => this.goBack(), 500)
      } catch (error) {
        this.toast(error.message)
      } finally {
        this.loading = false
      }
    },
    onGenderChange(event) { this.profileForm.gender = this.genderOptions[Number(event.detail.value)].value },
    onHasPetChange(event) { this.profileForm.has_pet = Boolean(event.detail.value) },
    goBack() {
      const pages = getCurrentPages()
      if (pages.length > 1) return uni.navigateBack({ delta: 1 })
      uni.navigateTo({ url: '/pages/account/account' })
    },
    toast(title) { uni.showToast({ title, icon: 'none' }) }
  }
}
</script>

<style>
page { background: #f3f5f8; }
.page { min-height: 100vh; padding: 24rpx; color: #172033; }
.topbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20rpx; }
.title { display: block; font-size: 36rpx; font-weight: 700; }
.subtitle { display: block; margin-top: 8rpx; color: #6b7788; font-size: 23rpx; }
.panel { padding: 24rpx; border: 1rpx solid #e2e8ef; border-radius: 8rpx; background: #fff; }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16rpx; }
.field { margin-bottom: 16rpx; }
.label { display: block; margin-bottom: 8rpx; color: #667387; font-size: 22rpx; }
.input, .picker { width: 100%; height: 72rpx; padding: 0 18rpx; border: 1rpx solid #d9e0e8; border-radius: 8rpx; background: #fbfcfd; font-size: 24rpx; line-height: 72rpx; }
.textarea { width: 100%; min-height: 140rpx; padding: 18rpx; border: 1rpx solid #d9e0e8; border-radius: 8rpx; background: #fbfcfd; font-size: 24rpx; line-height: 1.5; }
.switch-line { display: flex; align-items: center; gap: 14rpx; height: 72rpx; color: #526172; font-size: 24rpx; }
.actions { display: flex; justify-content: flex-end; gap: 14rpx; }
.primary, .secondary, .ghost { display: flex; align-items: center; justify-content: center; height: 64rpx; margin: 0; padding: 0 22rpx; border-radius: 8rpx; font-size: 24rpx; }
.primary { color: #fff; background: #1f6b57; }
.secondary, .ghost { color: #1f6b57; background: #e8f3ef; }
@media screen and (max-width: 760px) {
  .topbar, .actions { flex-direction: column; align-items: stretch; }
  .form-grid { grid-template-columns: 1fr; }
}
</style>
