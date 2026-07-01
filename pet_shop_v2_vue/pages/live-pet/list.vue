<template>
  <view class="page">
    <view class="header">
      <view>
        <text class="title">买宠物</text>
        <text class="subtitle">购买后自动进入“我的宠物”</text>
      </view>
    </view>

    <view class="search-bar">
      <input class="search-input" v-model="query.keyword" placeholder="搜索编号、昵称、品种" confirm-type="search" @confirm="loadLivePets" />
      <button class="search-button" @click="loadLivePets">搜索</button>
    </view>

    <view class="type-row">
      <button class="type-chip" :class="{ active: !query.pet_type }" @click="selectType('')">全部</button>
      <button class="type-chip" :class="{ active: query.pet_type === 'cat' }" @click="selectType('cat')">猫</button>
      <button class="type-chip" :class="{ active: query.pet_type === 'dog' }" @click="selectType('dog')">狗</button>
      <button class="type-chip" :class="{ active: query.pet_type === 'rabbit' }" @click="selectType('rabbit')">小宠</button>
    </view>

    <view class="pet-grid" v-if="livePets.length">
      <view class="pet-card" v-for="pet in livePets" :key="pet.id" @click="goDetail(pet)">
        <image class="cover" :src="pet.cover_url || fallbackImage" mode="aspectFit"></image>
        <view class="body">
          <text class="name">{{ pet.display_name || pet.pet_code }}</text>
          <text class="muted">{{ typeText(pet.pet_type) }} · {{ pet.breed || '未知品种' }} · {{ pet.city || '城市未知' }}</text>
          <view class="price-row">
            <text class="price">¥{{ money(pet.price) }}</text>
            <text class="code">{{ pet.pet_code }}</text>
          </view>
        </view>
      </view>
    </view>
    <view class="empty-state" v-else>
      <text>{{ loading ? '加载中...' : '暂无待售宠物' }}</text>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      apiBase: 'http://127.0.0.1:8000/api/v1',
      fallbackImage: '/static/logo.png',
      livePets: [],
      loading: false,
      query: {
        page: 1,
        page_size: 20,
        keyword: '',
        pet_type: ''
      }
    }
  },
  onLoad() {
    const savedBase = uni.getStorageSync('petShopApiBase')
    if (savedBase) {
      this.apiBase = savedBase
    }
    this.loadLivePets()
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
    async loadLivePets() {
      this.loading = true
      const params = [`page=${this.query.page}`, `page_size=${this.query.page_size}`]
      if (this.query.keyword) {
        params.push(`keyword=${encodeURIComponent(this.query.keyword)}`)
      }
      if (this.query.pet_type) {
        params.push(`pet_type=${encodeURIComponent(this.query.pet_type)}`)
      }
      try {
        const data = await this.request({ url: `/live-pets?${params.join('&')}` })
        this.livePets = data.items || []
      } catch (error) {
        this.toast(error.message)
      } finally {
        this.loading = false
      }
    },
    selectType(type) {
      this.query.pet_type = type
      this.loadLivePets()
    },
    goDetail(pet) {
      uni.navigateTo({ url: `/pages/live-pet/detail?id=${pet.id}` })
    },
    typeText(value) {
      return ({ cat: '猫', dog: '狗', rabbit: '兔子' })[value] || value
    },
    money(value) {
      return Number(value || 0).toFixed(2)
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
.header { padding: 20rpx 4rpx 24rpx; }
.title { display: block; color: #172033; font-size: 40rpx; font-weight: 700; }
.subtitle, .muted { display: block; margin-top: 8rpx; color: #718093; font-size: 23rpx; }
.search-bar { display: flex; gap: 12rpx; margin-bottom: 18rpx; }
.search-input { flex: 1; height: 76rpx; padding: 0 22rpx; border: 1rpx solid #d9e0e8; border-radius: 8rpx; background: #fff; font-size: 25rpx; box-sizing: border-box; }
.search-button, .type-chip { display: flex; align-items: center; justify-content: center; margin: 0; border-radius: 8rpx; font-size: 24rpx; }
.search-button { width: 128rpx; height: 76rpx; color: #fff; background: #1c6b56; }
.type-row { display: flex; gap: 12rpx; margin-bottom: 20rpx; }
.type-chip { height: 58rpx; padding: 0 22rpx; color: #526172; background: #fff; border: 1rpx solid #dfe6ee; }
.type-chip.active { color: #fff; background: #1c6b56; }
.pet-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18rpx; }
.pet-card { overflow: hidden; border: 1rpx solid #e2e8ef; border-radius: 8rpx; background: #fff; }
.cover { width: 100%; height: 230rpx; background: #edf1f4; }
.body { padding: 18rpx; }
.name { display: block; color: #172033; font-size: 28rpx; font-weight: 700; }
.price-row { display: flex; align-items: center; justify-content: space-between; gap: 10rpx; margin-top: 16rpx; }
.price { color: #b74428; font-size: 30rpx; font-weight: 700; }
.code { color: #748092; font-size: 20rpx; }
.empty-state { padding: 80rpx 20rpx; color: #798493; text-align: center; font-size: 26rpx; }
</style>
