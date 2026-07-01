<template>
  <view class="page">
    <view class="summary">
      <text class="summary-title">购物车</text>
      <text class="summary-text">已选 {{ cart.selected_quantity }} 件，共 ¥{{ money(cart.selected_amount) }}</text>
    </view>

    <view class="cart-list" v-if="cart.items.length">
      <view class="cart-row" v-for="item in cart.items" :key="item.id">
        <switch :checked="item.selected" color="#1c6b56" @change="updateSelected(item, $event)" />
        <image class="cover" :src="item.product.cover_url || fallbackImage" mode="aspectFit"></image>
        <view class="info">
          <text class="title">{{ item.product.title }}</text>
          <text class="muted">¥{{ money(item.product.price) }} · 库存 {{ item.product.stock }}</text>
          <view class="actions">
            <button class="step-button" @click="changeQuantity(item, -1)">-</button>
            <text class="quantity">{{ item.quantity }}</text>
            <button class="step-button" @click="changeQuantity(item, 1)">+</button>
            <button class="danger-button" @click="removeItem(item)">删除</button>
          </view>
        </view>
      </view>
    </view>

    <view class="empty-state" v-else>
      <text>{{ token ? '购物车为空' : '请先登录后查看购物车' }}</text>
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
      fallbackImage: '/static/logo.png',
      cart: {
        items: [],
        total_quantity: 0,
        selected_quantity: 0,
        selected_amount: 0
      }
    }
  },
  onShow() {
    const savedBase = uni.getStorageSync('petShopApiBase')
    if (savedBase) {
      this.apiBase = savedBase
    }
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
    async loadCart() {
      if (!this.token) {
        return
      }
      try {
        this.cart = await this.request({ url: '/cart' })
      } catch (error) {
        this.toast(error.message)
      }
    },
    async changeQuantity(item, delta) {
      await this.updateItem(item.id, { quantity: Math.max(1, item.quantity + delta) })
    },
    async updateSelected(item, event) {
      await this.updateItem(item.id, { selected: Boolean(event.detail.value) })
    },
    async updateItem(itemId, data) {
      try {
        this.cart = await this.request({ url: `/cart/items/${itemId}`, method: 'PATCH', data })
      } catch (error) {
        this.toast(error.message)
      }
    },
    async removeItem(item) {
      try {
        this.cart = await this.request({ url: `/cart/items/${item.id}`, method: 'DELETE' })
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
page {
  background: #f4f6f8;
}

.page {
  min-height: 100vh;
  padding: 24rpx;
  box-sizing: border-box;
}

.summary {
  padding: 28rpx;
  margin-bottom: 20rpx;
  border-radius: 8rpx;
  background: #ffffff;
}

.summary-title {
  display: block;
  font-size: 34rpx;
  font-weight: 700;
  color: #172033;
}

.summary-text {
  display: block;
  margin-top: 10rpx;
  color: #b74428;
  font-size: 26rpx;
}

.cart-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.cart-row {
  display: flex;
  align-items: center;
  gap: 18rpx;
  padding: 20rpx;
  border-radius: 8rpx;
  background: #ffffff;
}

.cover {
  width: 120rpx;
  height: 120rpx;
  border-radius: 8rpx;
  background: #edf1f4;
}

.info {
  flex: 1;
  min-width: 0;
}

.title {
  display: block;
  font-size: 27rpx;
  font-weight: 700;
  color: #172033;
}

.muted {
  display: block;
  margin-top: 8rpx;
  color: #718093;
  font-size: 22rpx;
}

.actions {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-top: 16rpx;
}

.step-button,
.danger-button,
.primary-button {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0;
  border-radius: 8rpx;
  font-size: 23rpx;
}

.step-button {
  width: 52rpx;
  height: 52rpx;
  color: #1c6b56;
  background: #e8f3ef;
}

.quantity {
  width: 50rpx;
  text-align: center;
  font-size: 24rpx;
}

.danger-button {
  height: 52rpx;
  padding: 0 18rpx;
  color: #a43333;
  background: #faeeee;
}

.primary-button {
  height: 76rpx;
  color: #ffffff;
  background: #1c6b56;
}

.empty-state {
  padding: 90rpx 20rpx;
  color: #798493;
  text-align: center;
  font-size: 26rpx;
}

.empty-button {
  width: 220rpx;
  margin: 26rpx auto 0;
}
</style>
