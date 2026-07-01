<template>
  <view class="page">
    <view class="panel">
      <text class="title">商家商品</text>
      <text class="subtitle">示例商家账号：16600000000，管理员账号也可给用户分配商家角色</text>
      <view class="form-grid">
        <input class="input" v-model="form.title" placeholder="商品名" />
        <picker :range="categories" range-key="name" @change="onCategoryChange">
          <view class="picker">{{ categoryLabel }}</view>
        </picker>
        <input class="input" v-model.number="form.price" type="digit" placeholder="价格" />
        <input class="input" v-model.number="form.stock" type="number" placeholder="库存" />
      </view>
      <input class="input full" v-model="form.subtitle" placeholder="副标题" />
      <input class="input full" v-model="form.brand" placeholder="品牌" />
      <textarea class="textarea" v-model="form.detail" placeholder="商品详情"></textarea>
      <view class="button-row">
        <button class="primary-button" @click="saveProduct">{{ editingId ? '保存修改' : '创建商品' }}</button>
        <button class="secondary-button" v-if="editingId" @click="resetForm">取消</button>
      </view>
    </view>

    <view class="list" v-if="products.length">
      <view class="row" v-for="product in products" :key="product.id">
        <image class="cover" :src="product.cover_url || fallbackImage" mode="aspectFit"></image>
        <view class="info">
          <text class="name">{{ product.title }}</text>
          <text class="muted">¥{{ money(product.price) }} · {{ product.category_name }} · {{ statusText(product.status) }}</text>
          <text class="muted" v-if="product.audit_note">备注：{{ product.audit_note }}</text>
          <view class="actions">
            <button class="text-button" @click="editProduct(product)">编辑</button>
            <button class="text-button" @click="submitProduct(product)">提交审核</button>
            <button class="danger-button" @click="takeDownProduct(product)">下架</button>
          </view>
        </view>
      </view>
    </view>
    <view class="empty-state" v-else>
      <text>{{ token ? '暂无商家商品' : '请先用商家账号登录' }}</text>
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
      categories: [],
      products: [],
      fallbackImage: '/static/logo.png',
      editingId: null,
      form: {
        category_id: '',
        title: '',
        subtitle: '',
        brand: '',
        cover_url: '/static/logo.png',
        price: 0,
        stock: 0,
        spec: '',
        applicable_pet: '通用',
        tags: [],
        detail: ''
      }
    }
  },
  computed: {
    categoryLabel() {
      const item = this.categories.find(category => String(category.id) === String(this.form.category_id))
      return item ? item.name : '选择分类'
    }
  },
  onShow() {
    const savedBase = uni.getStorageSync('petShopApiBase')
    if (savedBase) {
      this.apiBase = savedBase
    }
    this.token = uni.getStorageSync('petShopToken')
    this.loadCategories()
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
    async loadCategories() {
      try {
        this.categories = await this.request({ url: '/categories' }) || []
        if (!this.form.category_id && this.categories.length) {
          this.form.category_id = this.categories[0].id
        }
      } catch (error) {
        this.toast(error.message)
      }
    },
    async loadProducts() {
      if (!this.token) {
        return
      }
      try {
        const data = await this.request({ url: '/merchant/products?page=1&page_size=50' })
        this.products = data.items || []
      } catch (error) {
        this.toast(error.message)
      }
    },
    async saveProduct() {
      if (!this.token) {
        this.goAccount()
        return
      }
      if (!this.form.title || !this.form.category_id) {
        this.toast('请填写商品名和分类')
        return
      }
      try {
        const url = this.editingId ? `/merchant/products/${this.editingId}` : '/merchant/products'
        const method = this.editingId ? 'PUT' : 'POST'
        await this.request({ url, method, data: this.form })
        this.resetForm()
        await this.loadProducts()
        this.toast('商品已保存')
      } catch (error) {
        this.toast(error.message)
      }
    },
    editProduct(product) {
      this.editingId = product.id
      this.form = Object.assign({}, this.form, product, {
        price: Number(product.price || 0),
        stock: Number(product.stock || 0)
      })
    },
    resetForm() {
      this.editingId = null
      this.form = {
        category_id: this.categories.length ? this.categories[0].id : '',
        title: '',
        subtitle: '',
        brand: '',
        cover_url: '/static/logo.png',
        price: 0,
        stock: 0,
        spec: '',
        applicable_pet: '通用',
        tags: [],
        detail: ''
      }
    },
    async submitProduct(product) {
      try {
        await this.request({ url: `/merchant/products/${product.id}/submit`, method: 'POST' })
        await this.loadProducts()
        this.toast('已提交审核')
      } catch (error) {
        this.toast(error.message)
      }
    },
    async takeDownProduct(product) {
      try {
        await this.request({ url: `/merchant/products/${product.id}/take-down`, method: 'POST' })
        await this.loadProducts()
        this.toast('已下架')
      } catch (error) {
        this.toast(error.message)
      }
    },
    onCategoryChange(event) {
      this.form.category_id = this.categories[Number(event.detail.value)].id
    },
    statusText(status) {
      return ({ pending: '待审核', active: '已上架', inactive: '已下架', rejected: '已拒绝' })[status] || status
    },
    money(value) {
      return Number(value || 0).toFixed(2)
    },
    goAccount() {
      uni.switchTab({ url: '/pages/account/account' })
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
.panel, .row { border-radius: 8rpx; background: #fff; }
.panel { padding: 28rpx; margin-bottom: 20rpx; }
.title { display: block; font-size: 34rpx; font-weight: 700; }
.subtitle, .muted { display: block; margin-top: 8rpx; color: #718093; font-size: 23rpx; line-height: 1.5; }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14rpx; margin-top: 22rpx; }
.input, .picker, .textarea { box-sizing: border-box; width: 100%; border: 1rpx solid #d9e0e8; border-radius: 8rpx; background: #fbfcfd; font-size: 25rpx; }
.input, .picker { height: 76rpx; padding: 0 20rpx; line-height: 76rpx; }
.full, .textarea { margin-top: 14rpx; }
.textarea { min-height: 140rpx; padding: 18rpx 20rpx; line-height: 1.5; }
.button-row, .actions { display: flex; gap: 12rpx; margin-top: 16rpx; flex-wrap: wrap; }
.primary-button, .secondary-button, .text-button, .danger-button { display: flex; align-items: center; justify-content: center; height: 58rpx; margin: 0; padding: 0 18rpx; border-radius: 8rpx; font-size: 23rpx; }
.primary-button { color: #fff; background: #1c6b56; }
.secondary-button, .text-button { color: #1c6b56; background: #e8f3ef; }
.danger-button { color: #a43333; background: #faeeee; }
.list { display: flex; flex-direction: column; gap: 16rpx; }
.row { display: flex; gap: 18rpx; padding: 18rpx; }
.cover { width: 110rpx; height: 110rpx; border-radius: 8rpx; background: #edf1f4; }
.info { flex: 1; min-width: 0; }
.name { display: block; font-size: 27rpx; font-weight: 700; }
.empty-state { padding: 90rpx 20rpx; color: #798493; text-align: center; font-size: 26rpx; }
.empty-button { width: 220rpx; margin: 24rpx auto 0; }
</style>
