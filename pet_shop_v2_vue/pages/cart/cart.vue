<template>
  <view class="page">
    <view class="summary panel">
      <view>
        <text class="title">购物车</text>
        <text class="subtitle">已选 {{ cart.selected_quantity }} 件，合计 ￥{{ money(cart.selected_amount) }}</text>
      </view>
      <view class="summary-actions">
        <button class="secondary" @click="goOrders">订单管理</button>
        <button class="primary" @click="createOrder">创建订单</button>
      </view>
    </view>

    <view class="panel table" v-if="cart.items.length">
      <view class="row head">
        <text>选择</text>
        <text>商品</text>
        <text>单价</text>
        <text>数量</text>
        <text>操作</text>
      </view>
      <view class="row" v-for="item in cart.items" :key="item.id">
        <switch :checked="item.selected" color="#ff5000" @change="updateSelected(item, $event)" />
        <view class="product-cell">
          <image class="cover" :src="item.product.cover_url || fallbackImage" mode="aspectFit"></image>
          <view>
            <text class="name">{{ item.product.title }}</text>
            <text class="muted">库存 {{ item.product.stock }}</text>
          </view>
        </view>
        <text class="price">￥{{ money(item.product.price) }}</text>
        <view class="qty">
          <button class="step" @click="changeQuantity(item, -1)">-</button>
          <text>{{ item.quantity }}</text>
          <button class="step" @click="changeQuantity(item, 1)">+</button>
        </view>
        <button class="danger" @click="removeItem(item)">删除</button>
      </view>
    </view>

    <view class="empty panel" v-else>
      <text>{{ token ? '购物车为空' : '请先登录后查看购物车' }}</text>
      <button class="primary empty-btn" v-if="!token" @click="goAccount">去登录</button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      apiBase: 'http://127.0.0.1:8000/api/v1',
      token: '',
      fallbackImage: '/static/logo.png',
      cart: { items: [], total_quantity: 0, selected_quantity: 0, selected_amount: 0 }
    }
  },
  onShow() {
    const savedBase = uni.getStorageSync('petShopApiBase')
    if (savedBase) this.apiBase = savedBase
    this.token = uni.getStorageSync('petShopToken')
    this.loadCart()
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
    async loadCart() {
      if (!this.token) return
      try { this.cart = await this.request({ url: '/cart' }) } catch (error) { this.toast(error.message) }
    },
    async changeQuantity(item, delta) { await this.updateItem(item.id, { quantity: Math.max(1, item.quantity + delta) }) },
    async updateSelected(item, event) { await this.updateItem(item.id, { selected: Boolean(event.detail.value) }) },
    async updateItem(itemId, data) {
      try { this.cart = await this.request({ url: `/cart/items/${itemId}`, method: 'PATCH', data }) } catch (error) { this.toast(error.message) }
    },
    async removeItem(item) {
      try { this.cart = await this.request({ url: `/cart/items/${item.id}`, method: 'DELETE' }) } catch (error) { this.toast(error.message) }
    },
    async createOrder() {
      if (!this.token) return this.goAccount()
      if (!this.cart.selected_quantity) return this.toast('请先勾选商品')
      try {
        await this.request({
          url: '/orders',
          method: 'POST',
          data: {
            receiver_name: '测试收货人',
            receiver_phone: '13800138000',
            receiver_address: '测试地址',
            remark: '前端模拟下单'
          }
        })
        this.toast('订单已创建')
        setTimeout(() => this.goOrders(), 500)
      } catch (error) {
        this.toast(error.message)
      }
    },
    goAccount() { uni.navigateTo({ url: '/pages/account/account' }) },
    goOrders() { uni.navigateTo({ url: '/pages/order/list' }) },
    money(value) { return Number(value || 0).toFixed(2) },
    toast(title) { uni.showToast({ title, icon: 'none' }) }
  }
}
</script>

<style>
page { background: #f5f5f5; }
.page { min-height: 100vh; padding: 24rpx; color: #1f1f1f; }
.panel { border: 1rpx solid #ffe0cc; border-radius: 18rpx; background: #fff; box-shadow: 0 8rpx 24rpx rgba(255, 80, 0, .07); }
.summary { display: flex; align-items: center; justify-content: space-between; padding: 24rpx; margin-bottom: 18rpx; background: linear-gradient(90deg, #fff7f0, #fff); }
.summary-actions { display: flex; gap: 12rpx; }
.title { display: block; color: #ff5000; font-size: 38rpx; font-weight: 800; }
.subtitle, .muted { display: block; margin-top: 8rpx; color: #7b6659; font-size: 23rpx; }
.table { overflow: hidden; }
.row { display: grid; grid-template-columns: 100rpx minmax(320rpx, 2fr) 180rpx 180rpx minmax(150rpx, 180rpx); gap: 14rpx; align-items: center; padding: 20rpx; border-bottom: 1rpx solid #fff0e7; font-size: 24rpx; }
.row:last-child { border-bottom: none; }
.head { color: #a45f38; background: #fff7f0; font-weight: 700; }
.product-cell { display: flex; align-items: center; gap: 14rpx; min-width: 0; }
.cover { width: 86rpx; height: 86rpx; border-radius: 12rpx; background: #fff7f0; }
.name { display: block; font-size: 25rpx; font-weight: 700; }
.price { color: #ff5000; font-weight: 900; }
.qty { display: flex; align-items: center; gap: 12rpx; }
.primary, .secondary, .danger, .step { display: flex; align-items: center; justify-content: center; height: 58rpx; margin: 0; border-radius: 999rpx; font-size: 23rpx; white-space: nowrap; box-sizing: border-box; }
.primary { padding: 0 24rpx; color: #fff; background: linear-gradient(90deg, #ff9f1a, #ff5000); font-weight: 700; }
.secondary { padding: 0 20rpx; color: #ff5000; background: #fff0e7; }
.danger { padding: 0 18rpx; color: #d93600; background: #fff0e8; }
.step { width: 52rpx; color: #ff5000; background: #fff0e7; }
.empty { padding: 80rpx 20rpx; color: #798493; text-align: center; font-size: 26rpx; }
.empty-btn { width: 180rpx; margin: 20rpx auto 0; }
@media screen and (max-width: 760px) {
  .summary, .summary-actions { flex-direction: column; align-items: stretch; gap: 14rpx; }
  .row { grid-template-columns: 1fr; }
  .head { display: none; }
}
</style>
