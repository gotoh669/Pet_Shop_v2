<template>
  <view class="page" v-if="livePet">
    <view class="panel detail">
      <image class="cover" :src="livePet.cover_url || fallbackImage" mode="aspectFit"></image>
      <view class="content">
        <text class="title">{{ livePet.display_name || livePet.pet_code }}</text>
        <text class="subtitle">{{ typeText(livePet.pet_type) }} · {{ livePet.breed || '未知品种' }} · {{ livePet.city || '城市未知' }}</text>
        <view class="price-line">
          <text class="price">￥{{ money(livePet.price) }}</text>
          <text class="status">{{ statusText(livePet.status) }}</text>
        </view>
        <view class="meta-grid">
          <text>编号：{{ livePet.pet_code }}</text>
          <text>性别：{{ genderText(livePet.gender) }}</text>
          <text>生日：{{ livePet.birthday || '-' }}</text>
          <text>毛色：{{ livePet.color || '-' }}</text>
          <text>体重：{{ livePet.weight || '-' }} kg</text>
          <text>城市：{{ livePet.city || '-' }}</text>
        </view>
        <view class="section">
          <text class="section-title">健康信息</text>
          <text class="body-text">疫苗：{{ livePet.vaccine_info || '暂无' }}</text>
          <text class="body-text">驱虫：{{ livePet.deworm_info || '暂无' }}</text>
          <text class="body-text">健康证明：{{ livePet.health_certificate_url || '暂无' }}</text>
        </view>
        <view class="section">
          <text class="section-title">介绍</text>
          <text class="body-text">{{ livePet.description || '暂无介绍' }}</text>
        </view>
        <view class="actions">
          <button class="secondary" @click="goMyPets">我的宠物</button>
          <button class="primary" @click="purchaseLivePet">模拟购买</button>
        </view>
      </view>
    </view>
  </view>
  <view class="empty" v-else>{{ loading ? '加载中...' : '宠物不存在' }}</view>
</template>

<script>
export default {
  data() {
    return { apiBase: 'http://127.0.0.1:8000/api/v1', livePetId: '', livePet: null, fallbackImage: '/static/logo.png', loading: false }
  },
  onLoad(options) {
    const savedBase = uni.getStorageSync('petShopApiBase')
    if (savedBase) this.apiBase = savedBase
    this.livePetId = options.id
    this.loadLivePet()
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
    async loadLivePet() {
      this.loading = true
      try { this.livePet = await this.request({ url: `/live-pets/${this.livePetId}` }) } catch (error) { this.toast(error.message) } finally { this.loading = false }
    },
    async purchaseLivePet() {
      if (!uni.getStorageSync('petShopToken')) {
        this.toast('请先登录')
        uni.navigateTo({ url: '/pages/account/account' })
        return
      }
      try {
        const data = await this.request({ url: `/live-pets/${this.livePetId}/purchase`, method: 'POST' })
        this.toast('购买成功，已加入我的宠物')
        uni.navigateTo({ url: `/pages/pet/detail?id=${data.generated_pet_profile_id}` })
      } catch (error) {
        this.toast(error.message)
      }
    },
    goMyPets() { uni.navigateTo({ url: '/pages/pet/index' }) },
    typeText(value) { return ({ cat: '猫', dog: '狗', rabbit: '兔子' })[value] || value },
    genderText(value) { return ({ male: '公', female: '母', unknown: '未知' })[value] || value },
    statusText(value) { return ({ active: '在售', sold: '已售', pending: '待审核', inactive: '已下架' })[value] || value },
    money(value) { return Number(value || 0).toFixed(2) },
    toast(title) { uni.showToast({ title, icon: 'none' }) }
  }
}
</script>

<style>
page { background: #f3f5f8; }
.page { min-height: 100vh; padding: 24rpx; color: #172033; }
.panel { border: 1rpx solid #e2e8ef; border-radius: 8rpx; background: #fff; }
.detail { display: grid; grid-template-columns: 420rpx minmax(0, 1fr); gap: 28rpx; padding: 24rpx; }
.cover { width: 100%; height: 420rpx; border-radius: 8rpx; background: #edf1f4; }
.title { display: block; font-size: 38rpx; font-weight: 700; }
.subtitle { display: block; margin-top: 10rpx; color: #647285; font-size: 24rpx; }
.price-line { display: flex; align-items: center; justify-content: space-between; margin-top: 20rpx; }
.price { color: #b74428; font-size: 40rpx; font-weight: 700; }
.status { color: #1f6b57; font-size: 24rpx; }
.meta-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12rpx; margin-top: 20rpx; padding: 18rpx; border-radius: 8rpx; background: #f7f9fb; color: #526172; font-size: 24rpx; }
.section { margin-top: 20rpx; }
.section-title { display: block; margin-bottom: 10rpx; font-size: 28rpx; font-weight: 700; }
.body-text { display: block; color: #526172; font-size: 24rpx; line-height: 1.7; }
.actions { display: flex; justify-content: flex-end; gap: 14rpx; margin-top: 26rpx; }
.primary, .secondary { display: flex; align-items: center; justify-content: center; height: 68rpx; margin: 0; padding: 0 24rpx; border-radius: 8rpx; font-size: 25rpx; }
.primary { color: #fff; background: #1f6b57; }
.secondary { color: #1f6b57; background: #e8f3ef; }
.empty { padding: 120rpx 20rpx; color: #798493; text-align: center; font-size: 26rpx; }
@media screen and (max-width: 760px) {
  .detail { grid-template-columns: 1fr; }
  .actions { flex-direction: column; }
}
</style>
