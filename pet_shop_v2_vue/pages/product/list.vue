<template>
  <view class="page">
    <view class="hero">
      <view>
        <text class="title">宠物商城</text>
        <text class="subtitle">精选粮食、零食、玩具与清洁用品</text>
      </view>
      <button class="plain-button" @click="goAccount">账号</button>
    </view>

    <view class="quick-actions">
      <button class="action-button" @click="goCart">购物车</button>
      <button class="action-button" @click="goMerchant">商家商品</button>
      <button class="action-button" @click="goAudit">商品审核</button>
    </view>

    <view class="search-bar">
      <input class="search-input" v-model="query.keyword" placeholder="搜索商品名或品牌" confirm-type="search" @confirm="loadProducts" />
      <button class="search-button" @click="loadProducts">搜索</button>
    </view>

    <scroll-view class="category-scroll" scroll-x>
      <view class="category-row">
        <button class="category-chip" :class="{ active: !query.category_id }" @click="selectCategory('')">全部</button>
        <button
          v-for="category in categories"
          :key="category.id"
          class="category-chip"
          :class="{ active: String(query.category_id) === String(category.id) }"
          @click="selectCategory(category.id)"
        >
          {{ category.name }}
        </button>
      </view>
    </scroll-view>

    <view class="product-grid" v-if="products.length">
      <view class="product-card" v-for="product in products" :key="product.id" @click="goDetail(product)">
        <image class="cover" :src="product.cover_url || fallbackImage" mode="aspectFit"></image>
        <view class="product-info">
          <text class="product-title">{{ product.title }}</text>
          <text class="product-subtitle">{{ product.subtitle || product.category_name }}</text>
          <view class="price-row">
            <text class="price">¥{{ money(product.price) }}</text>
            <text class="stock">库存 {{ product.stock }}</text>
          </view>
        </view>
      </view>
    </view>

    <view class="empty-state" v-else>
      <text>{{ loading ? '加载中...' : '暂无商品' }}</text>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      apiBase: 'http://127.0.0.1:8000/api/v1',
      categories: [],
      products: [],
      fallbackImage: '/static/logo.png',
      loading: false,
      query: {
        page: 1,
        page_size: 20,
        keyword: '',
        category_id: ''
      }
    }
  },
  onLoad() {
    const savedBase = uni.getStorageSync('petShopApiBase')
    if (savedBase) {
      this.apiBase = savedBase
    }
    this.loadCategories()
    this.loadProducts()
  },
  onShow() {
    const savedBase = uni.getStorageSync('petShopApiBase')
    if (savedBase) {
      this.apiBase = savedBase
    }
  },
  methods: {
    request(options) {
      const token = uni.getStorageSync('petShopToken')
      return new Promise((resolve, reject) => {
        uni.request({
          url: `${this.apiBase}${options.url}`,
          method: options.method || 'GET',
          data: options.data || {},
          header: Object.assign(
            { 'content-type': 'application/json' },
            token ? { Authorization: `Bearer ${token}` } : {}
          ),
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
    async loadCategories() {
      try {
        this.categories = await this.request({ url: '/categories' }) || []
      } catch (error) {
        this.toast(error.message)
      }
    },
    async loadProducts() {
      this.loading = true
      const params = [
        `page=${this.query.page}`,
        `page_size=${this.query.page_size}`
      ]
      if (this.query.keyword) {
        params.push(`keyword=${encodeURIComponent(this.query.keyword)}`)
      }
      if (this.query.category_id) {
        params.push(`category_id=${this.query.category_id}`)
      }
      try {
        const data = await this.request({ url: `/products?${params.join('&')}` })
        this.products = data.items || []
      } catch (error) {
        this.toast(error.message)
      } finally {
        this.loading = false
      }
    },
    selectCategory(categoryId) {
      this.query.category_id = categoryId
      this.loadProducts()
    },
    goDetail(product) {
      uni.navigateTo({ url: `/pages/product/detail?id=${product.id}` })
    },
    goCart() {
      uni.navigateTo({ url: '/pages/cart/cart' })
    },
    goAccount() {
      uni.switchTab({ url: '/pages/account/account' })
    },
    goMerchant() {
      uni.navigateTo({ url: '/pages/merchant/products' })
    },
    goAudit() {
      uni.navigateTo({ url: '/pages/admin/audit' })
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
  color: #172033;
}

.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 30rpx 4rpx 24rpx;
}

.title {
  display: block;
  font-size: 42rpx;
  font-weight: 700;
}

.subtitle {
  display: block;
  margin-top: 10rpx;
  color: #647285;
  font-size: 24rpx;
}

.plain-button,
.action-button,
.search-button,
.category-chip {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0;
  border-radius: 8rpx;
  font-size: 24rpx;
}

.plain-button {
  height: 56rpx;
  padding: 0 20rpx;
  color: #1c6b56;
  background: #e8f3ef;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14rpx;
  margin-bottom: 22rpx;
}

.action-button {
  height: 70rpx;
  color: #1c6b56;
  background: #ffffff;
  border: 1rpx solid #dfe6ee;
}

.search-bar {
  display: flex;
  gap: 12rpx;
  margin-bottom: 22rpx;
}

.search-input {
  flex: 1;
  height: 76rpx;
  padding: 0 22rpx;
  border: 1rpx solid #d9e0e8;
  border-radius: 8rpx;
  background: #ffffff;
  font-size: 26rpx;
  box-sizing: border-box;
}

.search-button {
  width: 132rpx;
  height: 76rpx;
  color: #ffffff;
  background: #1c6b56;
}

.category-scroll {
  white-space: nowrap;
  margin-bottom: 22rpx;
}

.category-row {
  display: flex;
  gap: 12rpx;
}

.category-chip {
  height: 58rpx;
  padding: 0 22rpx;
  color: #526172;
  background: #ffffff;
  border: 1rpx solid #dfe6ee;
}

.category-chip.active {
  color: #ffffff;
  background: #1c6b56;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18rpx;
}

.product-card {
  overflow: hidden;
  border: 1rpx solid #e2e8ef;
  border-radius: 8rpx;
  background: #ffffff;
}

.cover {
  width: 100%;
  height: 220rpx;
  background: #edf1f4;
}

.product-info {
  padding: 18rpx;
}

.product-title {
  display: block;
  min-height: 68rpx;
  color: #172033;
  font-size: 27rpx;
  font-weight: 700;
  line-height: 1.3;
}

.product-subtitle {
  display: block;
  overflow: hidden;
  margin-top: 8rpx;
  color: #718093;
  font-size: 22rpx;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.price-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10rpx;
  margin-top: 16rpx;
}

.price {
  color: #b74428;
  font-size: 30rpx;
  font-weight: 700;
}

.stock {
  color: #748092;
  font-size: 21rpx;
}

.empty-state {
  padding: 80rpx 20rpx;
  color: #798493;
  text-align: center;
  font-size: 26rpx;
}
</style>
