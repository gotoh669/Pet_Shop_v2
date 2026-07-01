<template>
  <view class="page" v-if="livePet">
    <image class="cover" :src="livePet.cover_url || fallbackImage" mode="aspectFit"></image>
    <view class="content">
      <text class="title">{{ livePet.display_name || livePet.pet_code }}</text>
      <text class="subtitle">{{ typeText(livePet.pet_type) }} · {{ livePet.breed || '未知品种' }} · {{ livePet.city || '城市未知' }}</text>
      <view class="price-row">
        <text class="price">¥{{ money(livePet.price) }}</text>
        <text class="status">{{ statusText(livePet.status) }}</text>
      </view>

      <view class="panel">
        <text class="section-title">基础信息</text>
        <view class="meta-grid">
          <text>编号：{{ livePet.pet_code }}</text>
          <text>性别：{{ genderText(livePet.gender) }}</text>
          <text>生日：{{ livePet.birthday || '-' }}</text>
          <text>毛色：{{ livePet.color || '-' }}</text>
          <text>体重：{{ livePet.weight || '-' }} kg</text>
          <text>城市：{{ livePet.city || '-' }}</text>
        </view>
      </view>

      <view class="panel">
        <text class="section-title">健康信息</text>
        <text class="notes">疫苗：{{ livePet.vaccine_info || '暂无' }}</text>
        <text class="notes">驱虫：{{ livePet.deworm_info || '暂无' }}</text>
        <text class="notes">健康证明：{{ livePet.health_certificate_url || '暂无' }}</text>
      </view>

      <view class="panel">
        <text class="section-title">介绍</text>
        <text class="notes">{{ livePet.description || '暂无介绍' }}</text>
      </view>
    </view>

    <view class="bottom-bar">
      <button class="secondary-button" @click="goMyPets">我的宠物</button>
      <button class="primary-button" @click="purchaseLivePet">模拟购买</button>
    </view>
  </view>
  <view class="empty-state" v-else>
    <text>{{ loading ? '加载中...' : '宠物不存在' }}</text>
  </view>
</template>

<script>
export default {
  data() {
    return {
      apiBase: 'http://127.0.0.1:8000/api/v1',
      livePetId: '',
      livePet: null,
      fallbackImage: '/static/logo.png',
      loading: false
    }
  },
  onLoad(options) {
    const savedBase = uni.getStorageSync('petShopApiBase')
    if (savedBase) {
      this.apiBase = savedBase
    }
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
    async loadLivePet() {
      this.loading = true
      try {
        this.livePet = await this.request({ url: `/live-pets/${this.livePetId}` })
      } catch (error) {
        this.toast(error.message)
      } finally {
        this.loading = false
      }
    },
    async purchaseLivePet() {
      const token = uni.getStorageSync('petShopToken')
      if (!token) {
        this.toast('请先登录')
        uni.switchTab({ url: '/pages/account/account' })
        return
      }
      try {
        const data = await this.request({
          url: `/live-pets/${this.livePetId}/purchase`,
          method: 'POST'
        })
        this.toast('购买成功，已加入我的宠物')
        uni.navigateTo({ url: `/pages/pet/detail?id=${data.generated_pet_profile_id}` })
      } catch (error) {
        this.toast(error.message)
      }
    },
    goMyPets() {
      uni.switchTab({ url: '/pages/pet/index' })
    },
    typeText(value) {
      return ({ cat: '猫', dog: '狗', rabbit: '兔子' })[value] || value
    },
    genderText(value) {
      return ({ male: '男孩', female: '女孩', unknown: '未知' })[value] || value
    },
    statusText(value) {
      return ({ active: '在售', sold: '已售', pending: '待审核', inactive: '已下架' })[value] || value
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
.page { min-height: 100vh; padding-bottom: 120rpx; }
.cover { width: 100%; height: 520rpx; background: #fff; }
.content { padding: 28rpx; }
.title { display: block; color: #172033; font-size: 38rpx; font-weight: 700; }
.subtitle { display: block; margin-top: 12rpx; color: #647285; font-size: 25rpx; }
.price-row { display: flex; align-items: center; justify-content: space-between; margin-top: 24rpx; }
.price { color: #b74428; font-size: 42rpx; font-weight: 700; }
.status { color: #1c6b56; font-size: 24rpx; }
.panel { padding: 24rpx; margin-top: 22rpx; border-radius: 8rpx; background: #fff; }
.section-title { display: block; margin-bottom: 14rpx; font-size: 29rpx; font-weight: 700; }
.meta-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12rpx; color: #526172; font-size: 24rpx; }
.notes { display: block; margin-top: 10rpx; color: #526172; font-size: 24rpx; line-height: 1.6; }
.bottom-bar { position: fixed; right: 0; bottom: 0; left: 0; display: flex; gap: 16rpx; padding: 18rpx 24rpx; background: #fff; border-top: 1rpx solid #e2e8ef; }
.primary-button, .secondary-button { display: flex; align-items: center; justify-content: center; height: 82rpx; margin: 0; border-radius: 8rpx; font-size: 27rpx; }
.primary-button { flex: 1; color: #fff; background: #1c6b56; }
.secondary-button { width: 180rpx; color: #1c6b56; background: #e8f3ef; }
.empty-state { padding: 120rpx 20rpx; color: #798493; text-align: center; font-size: 26rpx; }
</style>
