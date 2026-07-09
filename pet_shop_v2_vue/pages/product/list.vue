<template>
  <view class="page">
    <view class="toolbar">
      <view>
        <text class="title">商品管理</text>
        <text class="subtitle">浏览已审核商品，支持分类筛选和加入购物车</text>
      </view>
      <view class="toolbar-actions">
        <button class="ghost" @click="goCart">购物车</button>
        <button class="ghost" @click="goMerchant">商家商品</button>
        <button class="ghost" @click="goAudit">平台审核</button>
      </view>
    </view>

    <view class="panel filter">
      <input class="input" v-model="query.keyword" placeholder="搜索商品名称或品牌" confirm-type="search" @confirm="loadProducts" />
      <picker :range="categoryPicker" range-key="name" @change="onCategoryChange">
        <view class="picker">{{ categoryLabel }}</view>
      </picker>
      <button class="primary small" @click="loadProducts">查询</button>
    </view>

    <view class="table panel" v-if="products.length">
      <view class="thead row">
        <text>商品</text>
        <text>分类</text>
        <text>价格</text>
        <text>库存</text>
        <text>操作</text>
      </view>
      <view class="row" v-for="product in products" :key="product.id">
        <view class="product-cell" @click="goDetail(product)">
          <image class="cover" :src="product.cover_url || fallbackImage" mode="aspectFit"></image>
          <view>
            <text class="name">{{ product.title }}</text>
            <text class="muted">{{ product.subtitle || product.brand || '暂无副标题' }}</text>
          </view>
        </view>
        <text>{{ product.category_name || '-' }}</text>
        <text class="price">￥{{ money(product.price) }}</text>
        <text>{{ product.stock }}</text>
        <view class="row-actions">
          <button class="ghost row-btn" @click="goDetail(product)">详情</button>
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
page { background: #f3f5f8; }
.page { min-height: 100vh; padding: 24rpx; color: #172033; }
.toolbar { display: flex; justify-content: space-between; gap: 18rpx; margin-bottom: 20rpx; }
.title { display: block; font-size: 36rpx; font-weight: 700; }
.subtitle, .muted { display: block; margin-top: 8rpx; color: #6b7788; font-size: 23rpx; }
.toolbar-actions, .filter { display: flex; gap: 12rpx; align-items: center; }
.panel { border: 1rpx solid #e2e8ef; border-radius: 8rpx; background: #fff; }
.filter { padding: 18rpx; margin-bottom: 18rpx; }
.input, .picker { height: 72rpx; padding: 0 20rpx; border: 1rpx solid #d9e0e8; border-radius: 8rpx; background: #fbfcfd; font-size: 24rpx; line-height: 72rpx; }
.input { flex: 1; }
.picker { width: 260rpx; }
.ghost, .primary { display: flex; align-items: center; justify-content: center; height: 58rpx; margin: 0; padding: 0 18rpx; border-radius: 8rpx; font-size: 23rpx; white-space: nowrap; box-sizing: border-box; }
.ghost { color: #1f6b57; background: #e8f3ef; }
.primary { color: #fff; background: #1f6b57; }
.small { width: 120rpx; height: 72rpx; }
.table { overflow: hidden; }
.row { display: grid; grid-template-columns: minmax(320rpx, 2fr) minmax(180rpx, 1fr) 160rpx 120rpx minmax(170rpx, 200rpx); gap: 16rpx; align-items: center; padding: 18rpx; border-bottom: 1rpx solid #edf1f5; font-size: 24rpx; }
.row:last-child { border-bottom: none; }
.thead { background: #f7f9fb; color: #6b7788; font-weight: 700; }
.product-cell { display: flex; align-items: center; gap: 14rpx; min-width: 0; }
.cover { width: 76rpx; height: 76rpx; border-radius: 8rpx; background: #edf1f4; }
.name { display: block; font-size: 26rpx; font-weight: 700; }
.price { color: #b74428; font-weight: 700; }
.row-actions { display: flex; align-items: center; justify-content: flex-start; gap: 10rpx; min-width: 0; }
.row-btn { min-width: 92rpx; width: auto; flex: 0 0 auto; }
.empty { padding: 80rpx 20rpx; color: #798493; text-align: center; font-size: 26rpx; }
@media screen and (max-width: 760px) {
  .toolbar, .toolbar-actions, .filter { flex-direction: column; align-items: stretch; }
  .picker, .small { width: 100%; }
  .row { grid-template-columns: 1fr; }
  .thead { display: none; }
}
</style>
