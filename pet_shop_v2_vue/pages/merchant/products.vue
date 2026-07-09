<template>
  <view class="page">
    <view class="toolbar">
      <view>
        <text class="title">商家商品管理</text>
        <text class="subtitle">创建商品、编辑库存，并提交给平台审核</text>
      </view>
      <button class="ghost" v-if="canManageProducts" @click="loadProducts">刷新列表</button>
    </view>

    <view class="panel notice" v-if="!token">
      <text class="notice-title">请先登录</text>
      <text class="notice-text">登录商家账号后才能创建和管理商品。</text>
      <button class="primary notice-btn" @click="goAccount">去登录</button>
    </view>

    <view class="panel notice" v-else-if="permissionChecked && !canManageProducts">
      <text class="notice-title">当前账号没有商家权限</text>
      <text class="notice-text">需要拥有 product:manage 权限后，才能创建商品和管理商家商品列表。</text>
      <button class="primary notice-btn" @click="goAccount">查看账号中心</button>
    </view>

    <view v-else-if="canManageProducts">
      <view class="panel">
        <text class="panel-title">{{ editingId ? '编辑商品' : '新增商品' }}</text>
        <view class="form-grid">
          <input class="input" v-model.trim="form.title" placeholder="商品名称" />
          <picker :range="categories" range-key="name" @change="onCategoryChange"><view class="picker">{{ categoryLabel }}</view></picker>
          <input class="input" v-model.number="form.price" type="digit" placeholder="价格" />
          <input class="input" v-model.number="form.stock" type="number" placeholder="库存" />
          <input class="input" v-model.trim="form.subtitle" placeholder="副标题" />
          <input class="input" v-model.trim="form.brand" placeholder="品牌" />
          <input class="input" v-model.trim="form.spec" placeholder="规格" />
          <input class="input" v-model.trim="form.applicable_pet" placeholder="适用宠物" />
        </view>
        <input class="input full" v-model.trim="form.cover_url" placeholder="封面 URL" />
        <textarea class="textarea" v-model.trim="form.detail" placeholder="商品详情"></textarea>
        <view class="actions">
          <button class="primary" @click="saveProduct">{{ editingId ? '保存修改' : '创建商品' }}</button>
          <button class="secondary" v-if="editingId" @click="resetForm">取消编辑</button>
        </view>
      </view>

      <view class="panel table" v-if="products.length">
        <view class="row head">
          <text>商品</text>
          <text>分类</text>
          <text>价格</text>
          <text>状态</text>
          <text>操作</text>
        </view>
        <view class="row" v-for="product in products" :key="product.id">
          <view class="product-cell">
            <image class="cover" :src="product.cover_url || fallbackImage" mode="aspectFit"></image>
            <view class="product-info">
              <text class="name">{{ product.title }}</text>
              <text class="muted">库存 {{ product.stock }} · {{ product.audit_note || '暂无审核备注' }}</text>
            </view>
          </view>
          <text>{{ product.category_name || '-' }}</text>
          <text class="price">￥{{ money(product.price) }}</text>
          <text>{{ statusText(product.status) }}</text>
          <view class="row-actions">
            <button class="ghost" @click="editProduct(product)">编辑</button>
            <button class="ghost" @click="submitProduct(product)">提交</button>
            <button class="danger" @click="takeDownProduct(product)">下架</button>
          </view>
        </view>
      </view>

      <view class="empty panel" v-else>
        <text>暂无商家商品</text>
      </view>
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
      permissions: [],
      permissionChecked: false,
      fallbackImage: '/static/logo.png',
      editingId: null,
      form: { category_id: '', title: '', subtitle: '', brand: '', cover_url: '/static/logo.png', price: 0, stock: 0, spec: '', applicable_pet: '通用', tags: [], detail: '' }
    }
  },
  computed: {
    canManageProducts() {
      return this.permissions.some(item => item.code === 'product:manage' || item === 'product:manage')
    },
    categoryLabel() {
      const item = this.categories.find(category => String(category.id) === String(this.form.category_id))
      return item ? item.name : '选择分类'
    }
  },
  async onShow() {
    const savedBase = uni.getStorageSync('petShopApiBase')
    if (savedBase) this.apiBase = savedBase
    this.token = uni.getStorageSync('petShopToken')
    this.products = []
    this.permissionChecked = false
    if (!this.token) {
      this.permissionChecked = true
      return
    }
    await this.loadPermissions()
    if (this.canManageProducts) {
      await this.loadCategories()
      await this.loadProducts()
    }
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
    async loadPermissions() {
      try {
        this.permissions = await this.request({ url: '/users/me/permissions' }) || []
      } catch (error) {
        this.permissions = []
        this.toast(error.message)
      } finally {
        this.permissionChecked = true
      }
    },
    async loadCategories() {
      try {
        this.categories = await this.request({ url: '/categories' }) || []
        if (!this.form.category_id && this.categories.length) this.form.category_id = this.categories[0].id
      } catch (error) {
        this.toast(error.message)
      }
    },
    async loadProducts() {
      if (!this.canManageProducts) return
      try {
        const data = await this.request({ url: '/merchant/products?page=1&page_size=50' })
        this.products = data.items || []
      } catch (error) {
        this.toast(error.message)
      }
    },
    async saveProduct() {
      if (!this.token) return this.goAccount()
      if (!this.canManageProducts) return this.toast('当前账号没有商家权限')
      if (!this.form.title || !this.form.category_id) return this.toast('请填写商品名和分类')
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
      this.form = Object.assign({}, this.form, product, { price: Number(product.price || 0), stock: Number(product.stock || 0) })
    },
    resetForm() {
      this.editingId = null
      this.form = { category_id: this.categories.length ? this.categories[0].id : '', title: '', subtitle: '', brand: '', cover_url: '/static/logo.png', price: 0, stock: 0, spec: '', applicable_pet: '通用', tags: [], detail: '' }
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
    onCategoryChange(event) { this.form.category_id = this.categories[Number(event.detail.value)].id },
    statusText(status) { return ({ pending: '待审核', active: '已上架', inactive: '已下架', rejected: '已拒绝' })[status] || status },
    money(value) { return Number(value || 0).toFixed(2) },
    goAccount() { uni.navigateTo({ url: '/pages/account/account' }) },
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
.panel { padding: 22rpx; margin-bottom: 18rpx; border: 1rpx solid #e2e8ef; border-radius: 8rpx; background: #fff; }
.panel-title { display: block; margin-bottom: 16rpx; font-size: 30rpx; font-weight: 700; }
.notice { padding: 44rpx; }
.notice-title { display: block; font-size: 30rpx; font-weight: 700; }
.notice-text { display: block; margin-top: 12rpx; color: #627084; font-size: 24rpx; }
.notice-btn { width: 220rpx; margin-top: 22rpx; }
.form-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12rpx; }
.input, .picker, .textarea { width: 100%; border: 1rpx solid #d9e0e8; border-radius: 8rpx; background: #fbfcfd; color: #172033; font-size: 24rpx; box-sizing: border-box; }
.input, .picker { height: 70rpx; padding: 0 18rpx; line-height: 70rpx; }
.full, .textarea { margin-top: 12rpx; }
.textarea { min-height: 130rpx; padding: 18rpx; line-height: 1.5; }
.actions, .row-actions { display: flex; gap: 10rpx; margin-top: 14rpx; flex-wrap: wrap; }
.primary, .secondary, .ghost, .danger { display: flex; align-items: center; justify-content: center; height: 58rpx; margin: 0; padding: 0 18rpx; border-radius: 8rpx; font-size: 23rpx; white-space: nowrap; box-sizing: border-box; flex: 0 0 auto; }
.primary { color: #fff; background: #1f6b57; }
.secondary, .ghost { color: #1f6b57; background: #e8f3ef; }
.danger { color: #a43333; background: #faeeee; }
.table { padding: 0; overflow: hidden; }
.row { display: grid; grid-template-columns: minmax(300rpx, 2fr) minmax(180rpx, 1fr) 150rpx 150rpx minmax(340rpx, 420rpx); gap: 14rpx; align-items: center; padding: 18rpx; border-bottom: 1rpx solid #edf1f5; font-size: 24rpx; }
.row:last-child { border-bottom: none; }
.head { color: #6b7788; background: #f7f9fb; font-weight: 700; }
.product-cell { display: flex; align-items: center; gap: 14rpx; min-width: 0; }
.product-info { min-width: 0; }
.cover { width: 76rpx; height: 76rpx; border-radius: 8rpx; background: #edf1f4; flex: 0 0 auto; }
.name { display: block; font-size: 25rpx; font-weight: 700; }
.price { color: #b74428; font-weight: 700; }
.empty { padding: 80rpx 20rpx; color: #798493; text-align: center; font-size: 26rpx; }
@media screen and (max-width: 900px) {
  .form-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media screen and (max-width: 760px) {
  .toolbar, .actions, .row-actions { flex-direction: column; align-items: stretch; }
  .form-grid, .row { grid-template-columns: 1fr; }
  .head { display: none; }
}
</style>
