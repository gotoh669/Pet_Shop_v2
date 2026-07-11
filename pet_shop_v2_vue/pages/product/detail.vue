<template>
  <view class="page" v-if="product">
    <view class="panel detail">
      <image class="cover" :src="product.cover_url || fallbackImage" mode="aspectFit"></image>
      <view class="content">
        <text class="title">{{ product.title }}</text>
        <text class="subtitle">{{ product.subtitle || '暂无副标题' }}</text>
        <view class="price-line">
          <text class="price">￥{{ money(product.price) }}</text>
          <text class="original" v-if="product.original_price">￥{{ money(product.original_price) }}</text>
          <text class="stock">库存 {{ product.stock }}</text>
        </view>
        <view class="meta-grid">
          <text>分类：{{ product.category_name || '-' }}</text>
          <text>品牌：{{ product.brand || '-' }}</text>
          <text>规格：{{ product.spec || '-' }}</text>
          <text>适用：{{ product.applicable_pet || '-' }}</text>
        </view>
        <view class="section">
          <text class="section-title">商品详情</text>
          <text class="body-text">{{ product.detail || '暂无商品详情' }}</text>
        </view>
        <view class="actions">
          <button class="secondary" @click="goCart">查看购物车</button>
          <button class="primary" @click="addToCart">加入购物车</button>
        </view>
      </view>
    </view>
  </view>
  <view class="empty" v-else>{{ loading ? '加载中...' : '商品不存在' }}</view>
</template>

<script>
export default {
  data() {
    return { apiBase: 'http://127.0.0.1:8000/api/v1', productId: '', product: null, fallbackImage: '/static/logo.png', loading: false }
  },
  onLoad(options) {
    const savedBase = uni.getStorageSync('petShopApiBase')
    if (savedBase) this.apiBase = savedBase
    this.productId = options.id
    this.loadProduct()
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
    async loadProduct() {
      this.loading = true
      try { this.product = await this.request({ url: `/products/${this.productId}` }) } catch (error) { this.toast(error.message) } finally { this.loading = false }
    },
    async addToCart() {
      if (!uni.getStorageSync('petShopToken')) {
        this.toast('请先登录')
        uni.navigateTo({ url: '/pages/account/account' })
        return
      }
      try {
        await this.request({ url: '/cart/items', method: 'POST', data: { product_id: Number(this.productId), quantity: 1 } })
        this.toast('已加入购物车')
      } catch (error) {
        this.toast(error.message)
      }
    },
    goCart() { uni.navigateTo({ url: '/pages/cart/cart' }) },
    money(value) { return Number(value || 0).toFixed(2) },
    toast(title) { uni.showToast({ title, icon: 'none' }) }
  }
}
</script>

<style>
.page { min-height: 100vh; padding: 24rpx; color: #1f1f1f; }
page { background: #f5f5f5; }
.panel { border: 1rpx solid #ffe0cc; border-radius: 18rpx; background: #fff; box-shadow: 0 10rpx 28rpx rgba(255, 80, 0, .08); }
.detail { display: grid; grid-template-columns: 460rpx minmax(0, 1fr); gap: 30rpx; padding: 28rpx; }
.cover { width: 100%; height: 460rpx; border-radius: 16rpx; background: #fff7f0; }
.title { display: block; font-size: 40rpx; font-weight: 800; line-height: 1.35; }
.subtitle { display: block; margin-top: 10rpx; color: #7b6659; font-size: 24rpx; }
.price-line { display: flex; align-items: baseline; gap: 16rpx; margin-top: 22rpx; }
.price { color: #ff5000; font-size: 46rpx; font-weight: 900; }
.original { color: #98a2af; font-size: 24rpx; text-decoration: line-through; }
.stock { margin-left: auto; padding: 4rpx 12rpx; border-radius: 999rpx; color: #a45f38; background: #fff3ec; font-size: 23rpx; }
.meta-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12rpx; margin-top: 22rpx; padding: 18rpx; border-radius: 14rpx; background: #fff7f0; color: #6d5648; font-size: 24rpx; }
.section { margin-top: 22rpx; }
.section-title { display: block; margin-bottom: 10rpx; font-size: 28rpx; font-weight: 800; }
.body-text { color: #6d5648; font-size: 24rpx; line-height: 1.7; }
.actions { display: flex; justify-content: flex-end; gap: 14rpx; margin-top: 28rpx; }
.primary, .secondary { display: flex; align-items: center; justify-content: center; height: 72rpx; margin: 0; padding: 0 32rpx; border-radius: 999rpx; font-size: 25rpx; font-weight: 700; }
.primary { color: #fff; background: linear-gradient(90deg, #ff9f1a, #ff5000); }
.secondary { color: #ff5000; background: #fff0e7; }
.empty { padding: 120rpx 20rpx; color: #798493; text-align: center; font-size: 26rpx; }
@media screen and (max-width: 760px) {
  .detail { grid-template-columns: 1fr; }
  .actions { flex-direction: column; }
}
</style>
