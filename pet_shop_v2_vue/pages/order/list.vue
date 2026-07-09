<template>
  <view class="page">
    <view class="toolbar">
      <view>
        <text class="title">订单管理</text>
        <text class="subtitle">查看订单、模拟支付、商家发货和确认收货</text>
      </view>
      <view class="toolbar-actions">
        <button class="ghost" @click="loadOrders">刷新</button>
        <button class="ghost" @click="goCart">购物车</button>
      </view>
    </view>

    <view class="panel filter">
      <picker :range="statusOptions" range-key="label" @change="onStatusChange">
        <view class="picker">{{ statusLabel }}</view>
      </picker>
      <button class="primary query" @click="loadOrders">查询</button>
    </view>

    <view class="panel table" v-if="orders.length">
      <view class="row head">
        <text>订单</text>
        <text>金额</text>
        <text>状态</text>
        <text>商品</text>
        <text>操作</text>
      </view>
      <view class="row" v-for="order in orders" :key="order.id">
        <view>
          <text class="order-no">{{ order.order_no }}</text>
          <text class="muted">创建：{{ formatDate(order.created_at) }}</text>
        </view>
        <text class="price">￥{{ money(order.total_amount) }}</text>
        <text>{{ statusText(order.status) }}</text>
        <view>
          <text class="item" v-for="item in order.items" :key="item.id">{{ item.product_title }} x{{ item.quantity }}</text>
        </view>
        <view class="actions">
          <button class="ghost" v-if="order._source === 'buyer' && order.status === 'pending_payment'" @click="mockPay(order)">模拟支付</button>
          <button class="ghost" v-if="order._source === 'merchant' && order.status === 'paid'" @click="shipOrder(order)">商家发货</button>
          <button class="ghost" v-if="order._source === 'buyer' && order.status === 'shipped'" @click="confirmOrder(order)">确认收货</button>
          <button class="danger" v-if="order._source === 'buyer' && order.status === 'pending_payment'" @click="cancelOrder(order)">取消</button>
        </view>
      </view>
    </view>

    <view class="empty panel" v-else>
      <text>{{ token ? '暂无订单' : '请先登录后查看订单' }}</text>
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
      orders: [],
      query: { page: 1, page_size: 20, status: '' },
      statusOptions: [
        { label: '全部状态', value: '' },
        { label: '待支付', value: 'pending_payment' },
        { label: '已支付', value: 'paid' },
        { label: '已发货', value: 'shipped' },
        { label: '已完成', value: 'completed' },
        { label: '已取消', value: 'cancelled' }
      ]
    }
  },
  computed: {
    statusLabel() {
      const item = this.statusOptions.find(option => option.value === this.query.status)
      return item ? item.label : '全部状态'
    }
  },
  onShow() {
    const savedBase = uni.getStorageSync('petShopApiBase')
    if (savedBase) this.apiBase = savedBase
    this.token = uni.getStorageSync('petShopToken')
    this.loadOrders()
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
    async loadOrders() {
      if (!this.token) return
      const params = [`page=${this.query.page}`, `page_size=${this.query.page_size}`]
      if (this.query.status) params.push(`status=${this.query.status}`)
      try {
        const data = await this.request({ url: `/orders?${params.join('&')}` })
        const buyerOrders = (data.items || []).map(order => Object.assign({}, order, { _source: 'buyer' }))
        let merchantOrders = []
        try {
          const merchantData = await this.request({ url: `/merchant/orders?${params.join('&')}` })
          merchantOrders = (merchantData.items || []).map(order => Object.assign({}, order, { _source: 'merchant' }))
        } catch (error) {
          merchantOrders = []
        }
        this.orders = buyerOrders.concat(merchantOrders)
      } catch (error) {
        this.toast(error.message)
      }
    },
    async mockPay(order) {
      await this.act(`/orders/${order.id}/mock-pay`, '支付成功')
    },
    async cancelOrder(order) {
      await this.act(`/orders/${order.id}/cancel`, '订单已取消')
    },
    async confirmOrder(order) {
      await this.act(`/orders/${order.id}/confirm`, '已确认收货')
    },
    async shipOrder(order) {
      try {
        await this.request({ url: `/merchant/orders/${order.id}/ship`, method: 'POST' })
        this.toast('已发货')
        await this.loadOrders()
      } catch (error) {
        this.toast(error.message)
      }
    },
    async act(url, message) {
      try {
        await this.request({ url, method: 'POST' })
        this.toast(message)
        await this.loadOrders()
      } catch (error) {
        this.toast(error.message)
      }
    },
    onStatusChange(event) {
      this.query.status = this.statusOptions[Number(event.detail.value)].value
      this.loadOrders()
    },
    statusText(status) {
      return ({ pending_payment: '待支付', paid: '已支付', shipped: '已发货', completed: '已完成', cancelled: '已取消', refunding: '售后中', refunded: '已退款' })[status] || status
    },
    formatDate(value) {
      return value ? String(value).replace('T', ' ').slice(0, 19) : '-'
    },
    money(value) { return Number(value || 0).toFixed(2) },
    goCart() { uni.navigateTo({ url: '/pages/cart/cart' }) },
    goAccount() { uni.navigateTo({ url: '/pages/account/account' }) },
    toast(title) { uni.showToast({ title, icon: 'none' }) }
  }
}
</script>

<style>
page { background: #f3f5f8; }
.page { min-height: 100vh; padding: 24rpx; color: #172033; }
.toolbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 18rpx; }
.toolbar-actions, .filter, .actions { display: flex; gap: 10rpx; }
.title { display: block; font-size: 36rpx; font-weight: 700; }
.subtitle, .muted { display: block; margin-top: 8rpx; color: #6b7788; font-size: 23rpx; }
.panel { border: 1rpx solid #e2e8ef; border-radius: 8rpx; background: #fff; }
.filter { padding: 18rpx; margin-bottom: 18rpx; }
.picker { width: 220rpx; height: 70rpx; padding: 0 18rpx; border: 1rpx solid #d9e0e8; border-radius: 8rpx; background: #fbfcfd; font-size: 24rpx; line-height: 70rpx; }
.query { width: 110rpx; }
.table { overflow: hidden; }
.row { display: grid; grid-template-columns: minmax(260rpx, 1.5fr) 150rpx 140rpx minmax(260rpx, 1.4fr) minmax(320rpx, 420rpx); gap: 14rpx; align-items: center; padding: 18rpx; border-bottom: 1rpx solid #edf1f5; font-size: 24rpx; }
.row:last-child { border-bottom: none; }
.head { color: #6b7788; background: #f7f9fb; font-weight: 700; }
.order-no { display: block; font-size: 24rpx; font-weight: 700; word-break: break-all; }
.price { color: #b74428; font-weight: 700; }
.item { display: block; margin-bottom: 6rpx; color: #526172; font-size: 22rpx; }
.actions { align-items: center; flex-wrap: wrap; min-width: 0; }
.primary, .ghost, .danger { display: flex; align-items: center; justify-content: center; height: 58rpx; margin: 0; padding: 0 16rpx; border-radius: 8rpx; font-size: 22rpx; white-space: nowrap; box-sizing: border-box; flex: 0 0 auto; }
.primary { color: #fff; background: #1f6b57; }
.ghost { color: #1f6b57; background: #e8f3ef; }
.danger { color: #a43333; background: #faeeee; }
.empty { padding: 80rpx 20rpx; color: #798493; text-align: center; font-size: 26rpx; }
.empty-btn { width: 180rpx; margin: 20rpx auto 0; }
@media screen and (max-width: 820px) {
  .toolbar, .toolbar-actions, .filter, .actions { flex-direction: column; align-items: stretch; }
  .picker, .query { width: 100%; }
  .row { grid-template-columns: 1fr; }
  .head { display: none; }
}
</style>
