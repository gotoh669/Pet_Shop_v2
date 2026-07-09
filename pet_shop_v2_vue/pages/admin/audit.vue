<template>
  <view class="page">
    <view class="toolbar">
      <view>
        <text class="title">平台审核</text>
        <text class="subtitle">处理商家提交的待审核商品</text>
      </view>
      <button class="ghost" @click="loadProducts">刷新</button>
    </view>

    <view class="panel table" v-if="products.length">
      <view class="row head">
        <text>商品</text>
        <text>商家</text>
        <text>价格</text>
        <text>库存</text>
        <text>操作</text>
      </view>
      <view class="row" v-for="product in products" :key="product.id">
        <view class="product-cell">
          <image class="cover" :src="product.cover_url || fallbackImage" mode="aspectFit"></image>
          <view>
            <text class="name">{{ product.title }}</text>
            <text class="muted">{{ product.detail || product.subtitle || '暂无详情' }}</text>
          </view>
        </view>
        <text>用户 {{ product.merchant_user_id }}</text>
        <text class="price">￥{{ money(product.price) }}</text>
        <text>{{ product.stock }}</text>
        <view class="actions">
          <button class="ghost" @click="approve(product)">通过</button>
          <button class="danger" @click="reject(product)">拒绝</button>
        </view>
      </view>
    </view>

    <view class="empty panel" v-else>
      <text>{{ token ? '暂无待审核商品' : '请先使用管理员账号登录' }}</text>
      <button class="primary empty-btn" v-if="!token" @click="goAccount">去登录</button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return { apiBase: 'http://127.0.0.1:8000/api/v1', token: '', products: [], fallbackImage: '/static/logo.png' }
  },
  onShow() {
    const savedBase = uni.getStorageSync('petShopApiBase')
    if (savedBase) this.apiBase = savedBase
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
            if (response.statusCode >= 200 && response.statusCode < 300 && response.data && response.data.code === 0) return resolve(response.data.data)
            reject(new Error(response.data && response.data.message ? response.data.message : '请求失败'))
          },
          fail: error => reject(new Error(error.errMsg || '网络连接失败'))
        })
      })
    },
    async loadProducts() {
      if (!this.token) return
      try {
        const data = await this.request({ url: '/admin/products?page=1&page_size=50&status=pending' })
        this.products = data.items || []
      } catch (error) {
        this.toast(error.message)
      }
    },
    async approve(product) {
      try {
        await this.request({ url: `/admin/products/${product.id}/approve`, method: 'POST', data: { audit_note: '审核通过' } })
        await this.loadProducts()
        this.toast('已通过')
      } catch (error) {
        this.toast(error.message)
      }
    },
    async reject(product) {
      try {
        await this.request({ url: `/admin/products/${product.id}/reject`, method: 'POST', data: { audit_note: '请完善商品信息后重新提交' } })
        await this.loadProducts()
        this.toast('已拒绝')
      } catch (error) {
        this.toast(error.message)
      }
    },
    goAccount() { uni.navigateTo({ url: '/pages/account/account' }) },
    money(value) { return Number(value || 0).toFixed(2) },
    toast(title) { uni.showToast({ title, icon: 'none' }) }
  }
}
</script>

<style>
page { background: #f3f5f8; }
.page { min-height: 100vh; padding: 24rpx; color: #172033; }
.toolbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 18rpx; }
.title { display: block; font-size: 36rpx; font-weight: 700; }
.subtitle, .muted { display: block; margin-top: 8rpx; color: #6b7788; font-size: 23rpx; }
.panel { border: 1rpx solid #e2e8ef; border-radius: 8rpx; background: #fff; }
.table { overflow: hidden; }
.row { display: grid; grid-template-columns: minmax(320rpx, 2fr) 160rpx 160rpx 120rpx minmax(220rpx, 260rpx); gap: 14rpx; align-items: center; padding: 18rpx; border-bottom: 1rpx solid #edf1f5; font-size: 24rpx; }
.row:last-child { border-bottom: none; }
.head { color: #6b7788; background: #f7f9fb; font-weight: 700; }
.product-cell { display: flex; align-items: center; gap: 14rpx; min-width: 0; }
.cover { width: 76rpx; height: 76rpx; border-radius: 8rpx; background: #edf1f4; }
.name { display: block; font-size: 25rpx; font-weight: 700; }
.price { color: #b74428; font-weight: 700; }
.actions { display: flex; gap: 10rpx; align-items: center; flex-wrap: nowrap; min-width: 0; }
.ghost, .danger, .primary { display: flex; align-items: center; justify-content: center; height: 58rpx; margin: 0; padding: 0 18rpx; border-radius: 8rpx; font-size: 23rpx; white-space: nowrap; box-sizing: border-box; flex: 0 0 auto; }
.ghost { color: #1f6b57; background: #e8f3ef; }
.danger { color: #a43333; background: #faeeee; }
.primary { color: #fff; background: #1f6b57; }
.empty { padding: 80rpx 20rpx; color: #798493; text-align: center; font-size: 26rpx; }
.empty-btn { width: 180rpx; margin: 20rpx auto 0; }
@media screen and (max-width: 760px) {
  .toolbar, .actions { flex-direction: column; align-items: stretch; }
  .row { grid-template-columns: 1fr; }
  .head { display: none; }
}
</style>
