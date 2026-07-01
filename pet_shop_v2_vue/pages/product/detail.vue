<template>
  <view class="page" v-if="product">
    <image class="cover" :src="product.cover_url || fallbackImage" mode="aspectFit"></image>
    <view class="content">
      <text class="title">{{ product.title }}</text>
      <text class="subtitle">{{ product.subtitle }}</text>
      <view class="price-row">
        <text class="price">¥{{ money(product.price) }}</text>
        <text class="original" v-if="product.original_price">¥{{ money(product.original_price) }}</text>
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
        <text class="detail">{{ product.detail || '暂无详情' }}</text>
      </view>
    </view>
    <view class="bottom-bar">
      <button class="secondary-button" @click="goCart">购物车</button>
      <button class="primary-button" @click="addToCart">加入购物车</button>
    </view>
  </view>
  <view class="empty-state" v-else>
    <text>{{ loading ? '加载中...' : '商品不存在' }}</text>
  </view>
</template>

<script>
export default {
  data() {
    return {
      apiBase: 'http://127.0.0.1:8000/api/v1',
      productId: '',
      product: null,
      fallbackImage: '/static/logo.png',
      loading: false
    }
  },
  onLoad(options) {
    const savedBase = uni.getStorageSync('petShopApiBase')
    if (savedBase) {
      this.apiBase = savedBase
    }
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
    async loadProduct() {
      this.loading = true
      try {
        this.product = await this.request({ url: `/products/${this.productId}` })
      } catch (error) {
        this.toast(error.message)
      } finally {
        this.loading = false
      }
    },
    async addToCart() {
      const token = uni.getStorageSync('petShopToken')
      if (!token) {
        this.toast('请先登录')
        uni.switchTab({ url: '/pages/account/account' })
        return
      }
      try {
        await this.request({
          url: '/cart/items',
          method: 'POST',
          data: { product_id: Number(this.productId), quantity: 1 }
        })
        this.toast('已加入购物车')
      } catch (error) {
        this.toast(error.message)
      }
    },
    goCart() {
      uni.navigateTo({ url: '/pages/cart/cart' })
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
  padding-bottom: 120rpx;
}

.cover {
  width: 100%;
  height: 520rpx;
  background: #ffffff;
}

.content {
  padding: 28rpx;
}

.title {
  display: block;
  font-size: 36rpx;
  font-weight: 700;
  color: #172033;
}

.subtitle {
  display: block;
  margin-top: 12rpx;
  color: #647285;
  font-size: 25rpx;
}

.price-row {
  display: flex;
  align-items: baseline;
  gap: 16rpx;
  margin-top: 24rpx;
}

.price {
  color: #b74428;
  font-size: 42rpx;
  font-weight: 700;
}

.original {
  color: #98a2af;
  font-size: 24rpx;
  text-decoration: line-through;
}

.stock {
  margin-left: auto;
  color: #718093;
  font-size: 23rpx;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14rpx;
  margin-top: 26rpx;
  padding: 22rpx;
  border-radius: 8rpx;
  background: #ffffff;
  color: #526172;
  font-size: 24rpx;
}

.section {
  margin-top: 24rpx;
  padding: 24rpx;
  border-radius: 8rpx;
  background: #ffffff;
}

.section-title {
  display: block;
  margin-bottom: 14rpx;
  font-size: 28rpx;
  font-weight: 700;
}

.detail {
  color: #526172;
  font-size: 25rpx;
  line-height: 1.7;
}

.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  display: flex;
  gap: 16rpx;
  padding: 18rpx 24rpx;
  background: #ffffff;
  border-top: 1rpx solid #e2e8ef;
}

.primary-button,
.secondary-button {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 82rpx;
  margin: 0;
  border-radius: 8rpx;
  font-size: 27rpx;
}

.primary-button {
  flex: 1;
  color: #ffffff;
  background: #1c6b56;
}

.secondary-button {
  width: 180rpx;
  color: #1c6b56;
  background: #e8f3ef;
}

.empty-state {
  padding: 120rpx 20rpx;
  color: #798493;
  text-align: center;
  font-size: 26rpx;
}
</style>
