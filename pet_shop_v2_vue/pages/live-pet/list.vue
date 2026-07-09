<template>
  <view class="page">
    <view class="toolbar">
      <view>
        <text class="title">活体宠物</text>
        <text class="subtitle">查看商家发布并通过审核的待售宠物</text>
      </view>
    </view>

    <view class="panel filter">
      <input class="input" v-model="query.keyword" placeholder="搜索编号、昵称、品种" confirm-type="search" @confirm="loadLivePets" />
      <view class="chips">
        <button class="chip" :class="{ active: !query.pet_type }" @click="selectType('')">全部</button>
        <button class="chip" :class="{ active: query.pet_type === 'cat' }" @click="selectType('cat')">猫</button>
        <button class="chip" :class="{ active: query.pet_type === 'dog' }" @click="selectType('dog')">狗</button>
        <button class="chip" :class="{ active: query.pet_type === 'rabbit' }" @click="selectType('rabbit')">兔子</button>
      </view>
      <button class="primary query-btn" @click="loadLivePets">查询</button>
    </view>

    <view class="pet-grid" v-if="livePets.length">
      <view class="card" v-for="pet in livePets" :key="pet.id" @click="goDetail(pet)">
        <image class="cover" :src="pet.cover_url || fallbackImage" mode="aspectFit"></image>
        <view class="body">
          <text class="name">{{ pet.display_name || pet.pet_code }}</text>
          <text class="muted">{{ typeText(pet.pet_type) }} · {{ pet.breed || '未知品种' }} · {{ pet.city || '城市未知' }}</text>
          <view class="line">
            <text class="price">￥{{ money(pet.price) }}</text>
            <text class="code">{{ pet.pet_code }}</text>
          </view>
        </view>
      </view>
    </view>

    <view class="empty panel" v-else>{{ loading ? '加载中...' : '暂无待售宠物' }}</view>
  </view>
</template>

<script>
export default {
  data() {
    return { apiBase: 'http://127.0.0.1:8000/api/v1', fallbackImage: '/static/logo.png', livePets: [], loading: false, query: { page: 1, page_size: 20, keyword: '', pet_type: '' } }
  },
  onLoad() {
    const savedBase = uni.getStorageSync('petShopApiBase')
    if (savedBase) this.apiBase = savedBase
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
            if (response.statusCode >= 200 && response.statusCode < 300 && response.data && response.data.code === 0) return resolve(response.data.data)
            reject(new Error(response.data && response.data.message ? response.data.message : '请求失败'))
          },
          fail: error => reject(new Error(error.errMsg || '网络连接失败'))
        })
      })
    },
    async loadLivePets() {
      this.loading = true
      const params = [`page=${this.query.page}`, `page_size=${this.query.page_size}`]
      if (this.query.keyword) params.push(`keyword=${encodeURIComponent(this.query.keyword)}`)
      if (this.query.pet_type) params.push(`pet_type=${encodeURIComponent(this.query.pet_type)}`)
      try {
        const data = await this.request({ url: `/live-pets?${params.join('&')}` })
        this.livePets = data.items || []
      } catch (error) {
        this.toast(error.message)
      } finally {
        this.loading = false
      }
    },
    selectType(type) { this.query.pet_type = type; this.loadLivePets() },
    goDetail(pet) { uni.navigateTo({ url: `/pages/live-pet/detail?id=${pet.id}` }) },
    typeText(value) { return ({ cat: '猫', dog: '狗', rabbit: '兔子' })[value] || value },
    money(value) { return Number(value || 0).toFixed(2) },
    toast(title) { uni.showToast({ title, icon: 'none' }) }
  }
}
</script>

<style>
page { background: #f3f5f8; }
.page { min-height: 100vh; padding: 24rpx; color: #172033; }
.toolbar { margin-bottom: 18rpx; }
.title { display: block; font-size: 36rpx; font-weight: 700; }
.subtitle, .muted { display: block; margin-top: 8rpx; color: #6b7788; font-size: 23rpx; }
.panel { border: 1rpx solid #e2e8ef; border-radius: 8rpx; background: #fff; }
.filter { display: flex; align-items: center; gap: 12rpx; padding: 18rpx; margin-bottom: 18rpx; }
.input { flex: 1; height: 72rpx; padding: 0 18rpx; border: 1rpx solid #d9e0e8; border-radius: 8rpx; background: #fbfcfd; font-size: 24rpx; }
.chips { display: flex; gap: 10rpx; }
.chip, .primary { display: flex; align-items: center; justify-content: center; height: 58rpx; margin: 0; padding: 0 18rpx; border-radius: 8rpx; font-size: 23rpx; }
.chip { color: #526172; background: #f2f5f7; }
.chip.active, .primary { color: #fff; background: #1f6b57; }
.query-btn { width: 110rpx; height: 72rpx; }
.pet-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18rpx; }
.card { overflow: hidden; border: 1rpx solid #e2e8ef; border-radius: 8rpx; background: #fff; }
.cover { width: 100%; height: 230rpx; background: #edf1f4; }
.body { padding: 18rpx; }
.name { display: block; font-size: 28rpx; font-weight: 700; }
.line { display: flex; justify-content: space-between; gap: 10rpx; margin-top: 14rpx; }
.price { color: #b74428; font-size: 30rpx; font-weight: 700; }
.code { color: #748092; font-size: 20rpx; }
.empty { padding: 80rpx 20rpx; color: #798493; text-align: center; font-size: 26rpx; }
@media screen and (max-width: 760px) {
  .filter { flex-direction: column; align-items: stretch; }
  .chips { flex-wrap: wrap; }
  .query-btn { width: 100%; }
  .pet-grid { grid-template-columns: 1fr; }
}
</style>
