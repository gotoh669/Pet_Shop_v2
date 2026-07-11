<template>
  <view class="page">
    <view class="toolbar">
      <view>
        <text class="title">宠物好物市场</text>
        <text class="subtitle">像逛淘宝一样挑选已审核商品</text>
      </view>
      <view class="toolbar-actions">
        <button class="ghost" @click="goCart">购物车</button>
        <button class="ghost" @click="goMerchant">商家商品</button>
        <button class="ghost" @click="goAudit">平台审核</button>
      </view>
    </view>

    <view class="filter">
      <input class="input" v-model="query.keyword" placeholder="搜索商品名称或品牌" confirm-type="search" @confirm="loadProducts" />
      <picker :range="categoryPicker" range-key="name" @change="onCategoryChange">
        <view class="picker">{{ categoryLabel }}</view>
      </picker>
      <button class="primary small" @click="loadProducts">查询</button>
    </view>

    <view class="product-grid" v-if="products.length">
      <view class="product-card" v-for="product in products" :key="product.id" @click="goDetail(product)">
        <image class="cover" :src="product.cover_url || fallbackImage" mode="aspectFit"></image>
        <view class="card-body">
          <text class="name">{{ product.title }}</text>
          <text class="muted">{{ product.subtitle || product.brand || '暂无副标题' }}</text>
          <view class="tag-line">
            <text class="tag">{{ product.category_name || '精选' }}</text>
            <text class="tag">库存 {{ product.stock }}</text>
          </view>
          <view class="buy-line">
            <text class="price">￥{{ money(product.price) }}</text>
            <button class="cart-btn" @click.stop="goDetail(product)">去看看</button>
          </view>
        </view>
      </view>
    </view>

    <view class="empty panel" v-else>
      <text>{{ loading ? '加载中...' : '暂无商品数据' }}</text>
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
      query: { page: 1, page_size: 20, keyword: '', category_id: '' }
    }
  },
  computed: {
    categoryPicker() {
      return [{ id: '', name: '全部分类' }].concat(this.categories)
    },
    categoryLabel() {
      const item = this.categoryPicker.find(category => String(category.id) === String(this.query.category_id))
      return item ? item.name : '全部分类'
    }
  },
  onLoad() {
    const savedBase = uni.getStorageSync('petShopApiBase')
    if (savedBase) this.apiBase = savedBase
    this.loadCategories()
    this.loadProducts()
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
    async loadCategories() {
      try { this.categories = await this.request({ url: '/categories' }) || [] } catch (error) { this.toast(error.message) }
    },
    async loadProducts() {
      this.loading = true
      const params = [`page=${this.query.page}`, `page_size=${this.query.page_size}`]
      if (this.query.keyword) params.push(`keyword=${encodeURIComponent(this.query.keyword)}`)
      if (this.query.category_id) params.push(`category_id=${this.query.category_id}`)
      try {
        const data = await this.request({ url: `/products?${params.join('&')}` })
        this.products = data.items || []
      } catch (error) {
        this.toast(error.message)
      } finally {
        this.loading = false
      }
    },
    onCategoryChange(event) {
      this.query.category_id = this.categoryPicker[Number(event.detail.value)].id
      this.loadProducts()
    },
    goDetail(product) { uni.navigateTo({ url: `/pages/product/detail?id=${product.id}` }) },
    goCart() { uni.navigateTo({ url: '/pages/cart/cart' }) },
    goMerchant() { uni.navigateTo({ url: '/pages/merchant/products' }) },
    goAudit() { uni.navigateTo({ url: '/pages/admin/audit' }) },
    money(value) { return Number(value || 0).toFixed(2) },
    toast(title) { uni.showToast({ title, icon: 'none' }) }
  }
}
</script>

<style>
page { background: #f5f5f5; }
.page { min-height: 100vh; padding: 24rpx; color: #1f1f1f; }
.toolbar { display: flex; justify-content: space-between; gap: 18rpx; margin-bottom: 20rpx; padding: 22rpx 24rpx; border: 1rpx solid #ffe0cc; border-radius: 18rpx; background: linear-gradient(90deg, #fff7f0, #fff); }
.title { display: block; color: #ff5000; font-size: 38rpx; font-weight: 800; }
.subtitle, .muted { display: block; margin-top: 8rpx; color: #7b6659; font-size: 23rpx; }
.toolbar-actions, .filter { display: flex; gap: 12rpx; align-items: center; }
.panel { border: 1rpx solid #ffe0cc; border-radius: 18rpx; background: #fff; }
.filter { padding: 14rpx; margin-bottom: 18rpx; border: 2rpx solid #ff6a00; border-radius: 999rpx; background: #fff; }
.input, .picker { height: 72rpx; padding: 0 24rpx; border: 0; border-radius: 999rpx; background: #fff7f0; font-size: 24rpx; line-height: 72rpx; }
.input { flex: 1; }
.picker { width: 260rpx; }
.ghost, .primary { display: flex; align-items: center; justify-content: center; height: 58rpx; margin: 0; padding: 0 18rpx; border-radius: 8rpx; font-size: 23rpx; white-space: nowrap; box-sizing: border-box; }
.ghost { color: #ff5000; background: #fff0e7; }
.primary { color: #fff; background: linear-gradient(90deg, #ff7a1a, #ff3d00); }
.small { width: 120rpx; height: 72rpx; }
.product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240rpx, 1fr)); gap: 18rpx; }
.product-card { overflow: hidden; border: 1rpx solid #ffe0cc; border-radius: 18rpx; background: #fff; box-shadow: 0 8rpx 22rpx rgba(255, 80, 0, .08); cursor: pointer; transition: transform .15s, box-shadow .15s; }
.product-card:hover { box-shadow: 0 14rpx 32rpx rgba(255, 80, 0, .14); transform: translateY(-2rpx); }
.cover { width: 100%; height: 260rpx; background: #fff7f0; }
.card-body { padding: 18rpx; }
.name { display: -webkit-box; overflow: hidden; min-height: 70rpx; font-size: 27rpx; font-weight: 700; line-height: 1.35; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
.tag-line { display: flex; flex-wrap: wrap; gap: 8rpx; margin-top: 12rpx; }
.tag { padding: 4rpx 10rpx; border-radius: 999rpx; color: #a45f38; background: #fff3ec; font-size: 20rpx; }
.buy-line { display: flex; align-items: center; justify-content: space-between; gap: 12rpx; margin-top: 16rpx; }
.price { color: #ff5000; font-size: 32rpx; font-weight: 800; }
.cart-btn { display: flex; align-items: center; justify-content: center; width: 112rpx; height: 52rpx; margin: 0; border-radius: 999rpx; color: #fff; background: linear-gradient(90deg, #ff9f1a, #ff5000); font-size: 22rpx; }
.empty { padding: 80rpx 20rpx; color: #798493; text-align: center; font-size: 26rpx; }
@media screen and (max-width: 760px) {
  .toolbar, .toolbar-actions, .filter { flex-direction: column; align-items: stretch; }
  .picker, .small { width: 100%; }
  .filter { border-radius: 18rpx; }
  .product-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .cover { height: 220rpx; }
}
</style>
