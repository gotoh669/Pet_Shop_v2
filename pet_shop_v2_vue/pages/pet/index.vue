<template>
  <view class="page">
    <view class="header">
      <view>
        <text class="title">我的宠物</text>
        <text class="subtitle">记录档案、成长和提醒</text>
      </view>
      <button class="primary-button" @click="goEdit()">新增</button>
    </view>

    <view class="pet-list" v-if="pets.length">
      <view class="pet-card" v-for="pet in pets" :key="pet.id" @click="goDetail(pet)">
        <image class="avatar" :src="pet.avatar_url || fallbackImage" mode="aspectFit"></image>
        <view class="info">
          <view class="name-line">
            <text class="name">{{ pet.name }}</text>
            <text class="badge" v-if="pet.is_current">当前</text>
            <text class="badge source">{{ sourceText(pet.source_type) }}</text>
          </view>
          <text class="muted">{{ typeText(pet.pet_type) }} · {{ pet.breed || '未知品种' }} · {{ genderText(pet.gender) }}</text>
          <text class="muted">体重 {{ pet.weight || '-' }} kg · 疫苗 {{ statusText(pet.vaccine_status) }}</text>
        </view>
        <button class="text-button" @click.stop="setCurrent(pet)">设为当前</button>
      </view>
    </view>

    <view class="empty-state" v-else>
      <text>{{ token ? '还没有宠物档案' : '请先登录后查看宠物档案' }}</text>
      <button class="primary-button empty-button" v-if="!token" @click="goAccount">去登录</button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      apiBase: 'http://127.0.0.1:8000/api/v1',
      token: '',
      pets: [],
      fallbackImage: '/static/logo.png'
    }
  },
  onShow() {
    const savedBase = uni.getStorageSync('petShopApiBase')
    if (savedBase) {
      this.apiBase = savedBase
    }
    this.token = uni.getStorageSync('petShopToken')
    this.loadPets()
  },
  methods: {
    request(options) {
      return new Promise((resolve, reject) => {
        uni.request({
          url: `${this.apiBase}${options.url}`,
          method: options.method || 'GET',
          data: options.data || {},
          header: Object.assign({ 'content-type': 'application/json' }, this.token ? { Authorization: `Bearer ${this.token}` } : {}),
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
    async loadPets() {
      if (!this.token) {
        return
      }
      try {
        this.pets = await this.request({ url: '/pets' }) || []
      } catch (error) {
        this.toast(error.message)
      }
    },
    async setCurrent(pet) {
      try {
        await this.request({ url: `/pets/${pet.id}/current`, method: 'POST' })
        await this.loadPets()
      } catch (error) {
        this.toast(error.message)
      }
    },
    goDetail(pet) {
      uni.navigateTo({ url: `/pages/pet/detail?id=${pet.id}` })
    },
    goEdit(pet) {
      const url = pet ? `/pages/pet/edit?id=${pet.id}` : '/pages/pet/edit'
      uni.navigateTo({ url })
    },
    goAccount() {
      uni.switchTab({ url: '/pages/account/account' })
    },
    typeText(value) {
      return value === 'dog' ? '狗狗' : '猫咪'
    },
    genderText(value) {
      return ({ male: '男孩', female: '女孩', unknown: '未知' })[value] || value
    },
    statusText(value) {
      return ({ completed: '已完成', regular: '规律', pending: '待完成', unknown: '未知' })[value] || value
    },
    sourceText(value) {
      return ({ manual: '手动', purchase: '购买', adoption: '领养' })[value] || '手动'
    },
    toast(title) {
      uni.showToast({ title, icon: 'none' })
    }
  }
}
</script>

<style>
page { background: #f4f6f8; }
.page { min-height: 100vh; padding: 24rpx; box-sizing: border-box; }
.header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 22rpx; }
.title { display: block; color: #172033; font-size: 38rpx; font-weight: 700; }
.subtitle, .muted { display: block; margin-top: 8rpx; color: #718093; font-size: 23rpx; }
.pet-list { display: flex; flex-direction: column; gap: 16rpx; }
.pet-card { display: flex; align-items: center; gap: 18rpx; padding: 20rpx; border-radius: 8rpx; background: #fff; }
.avatar { width: 112rpx; height: 112rpx; border-radius: 56rpx; background: #edf1f4; }
.info { flex: 1; min-width: 0; }
.name-line { display: flex; align-items: center; gap: 12rpx; }
.name { font-size: 30rpx; font-weight: 700; color: #172033; }
.badge { padding: 4rpx 12rpx; border-radius: 8rpx; color: #1c6b56; background: #e8f3ef; font-size: 20rpx; }
.badge.source { color: #526172; background: #eef1f4; }
.primary-button, .text-button { display: flex; align-items: center; justify-content: center; height: 58rpx; margin: 0; padding: 0 18rpx; border-radius: 8rpx; font-size: 23rpx; }
.primary-button { color: #fff; background: #1c6b56; }
.text-button { color: #1c6b56; background: #e8f3ef; }
.empty-state { padding: 90rpx 20rpx; color: #798493; text-align: center; font-size: 26rpx; }
.empty-button { width: 220rpx; margin: 24rpx auto 0; }
</style>
