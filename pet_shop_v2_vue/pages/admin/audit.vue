<template>
  <view class="page">
    <view class="header">
      <text class="title">商品审核</text>
      <button class="text-button" @click="loadProducts">刷新</button>
    </view>

    <view class="list" v-if="products.length">
      <view class="row" v-for="product in products" :key="product.id">
        <image class="cover" :src="product.cover_url || fallbackImage" mode="aspectFit"></image>
        <view class="info">
          <text class="name">{{ product.title }}</text>
          <text class="muted">商家用户 {{ product.merchant_user_id }} · ¥{{ money(product.price) }} · 库存 {{ product.stock }}</text>
          <text class="muted">{{ product.detail || product.subtitle || '无详情' }}</text>
          <view class="actions">
            <button class="text-button" @click="approve(product)">通过</button>
            <button class="danger-button" @click="reject(product)">拒绝</button>
          </view>
        </view>
      </view>
    </view>

    <view class="empty-state" v-else>
      <text>{{ token ? '暂无待审核商品' : '请先用管理员账号登录' }}</text>
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
      products: [],
      fallbackImage: '/static/logo.png'
    }
  },
  onShow() {
    const savedBase = uni.getStorageSync('petShopApiBase')
    if (savedBase) {
      this.apiBase = savedBase
    }
    this.token = uni.getStorageSync('petShopToken')
    this.loadProducts()
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
    async loadProducts() {
      if (!this.token) {
        return
      }
      try {
        const data = await this.request({ url: '/admin/products?page=1&page_size=50&status=pending' })
        this.products = data.items || []
      } catch (error) {
        this.toast(error.message)
      }
    },
    async approve(product) {
      try {
        await this.request({
          url: `/admin/products/${product.id}/approve`,
          method: 'POST',
          data: { audit_note: '审核通过' }
        })
        await this.loadProducts()
        this.toast('已通过')
      } catch (error) {
        this.toast(error.message)
      }
    },
    async reject(product) {
      try {
        await this.request({
          url: `/admin/products/${product.id}/reject`,
          method: 'POST',
          data: { audit_note: '请完善商品信息后重新提交' }
        })
        await this.loadProducts()
        this.toast('已拒绝')
      } catch (error) {
        this.toast(error.message)
      }
    },
    goAccount() {
      uni.switchTab({ url: '/pages/account/account' })
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
.header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 22rpx; }
.title { font-size: 34rpx; font-weight: 700; }
.list { display: flex; flex-direction: column; gap: 16rpx; }
.row { display: flex; gap: 18rpx; padding: 18rpx; border-radius: 8rpx; background: #fff; }
.cover { width: 110rpx; height: 110rpx; border-radius: 8rpx; background: #edf1f4; }
.info { flex: 1; min-width: 0; }
.name { display: block; font-size: 27rpx; font-weight: 700; }
.muted { display: block; margin-top: 8rpx; color: #718093; font-size: 23rpx; line-height: 1.5; }
.actions { display: flex; gap: 12rpx; margin-top: 16rpx; }
.text-button, .danger-button, .primary-button { display: flex; align-items: center; justify-content: center; height: 58rpx; margin: 0; padding: 0 18rpx; border-radius: 8rpx; font-size: 23rpx; }
.text-button { color: #1c6b56; background: #e8f3ef; }
.danger-button { color: #a43333; background: #faeeee; }
.primary-button { color: #fff; background: #1c6b56; }
.empty-state { padding: 90rpx 20rpx; color: #798493; text-align: center; font-size: 26rpx; }
.empty-button { width: 220rpx; margin: 24rpx auto 0; }
</style>
