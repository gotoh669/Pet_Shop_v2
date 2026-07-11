<template>
  <view class="page dashboard-page">
    <view class="topbar app-topbar">
      <view>
        <text class="brand">淘宠生活</text>
        <text class="sub">宠物粮食、用品、活体与档案服务一站购齐</text>
      </view>
      <view class="search-shell" @click="goProducts">
        <text class="search-icon">⌕</text>
        <text class="search-placeholder">搜索猫粮、狗窝、宠物玩具</text>
      </view>
      <button class="ghost account-btn" @click="goAccount">我的</button>
    </view>

    <view class="layout dashboard-layout">
      <view class="sidebar">
        <text class="side-title">频道导航</text>
        <button class="nav active" @click="goProducts">商品商城</button>
        <button class="nav" @click="goCart">购物车</button>
        <button class="nav" @click="goOrders">订单管理</button>
        <button class="nav" @click="goPets">宠物档案</button>
        <button class="nav" @click="goLivePets">活体宠物</button>
        <button class="nav" @click="goMerchant">商家商品</button>
        <button class="nav" @click="goAudit">平台审核</button>
      </view>

      <view class="main">
        <view class="hero">
          <view class="hero-copy">
            <text class="eyebrow">今日宠物好物</text>
            <text class="title">给毛孩子挑点新鲜好货</text>
            <text class="desc">精选用品、活体宠物、购物车下单和订单追踪都在这里，像逛淘宝一样完成宠物商城流程。</text>
            <view class="hero-actions">
              <button class="primary" @click="goProducts">马上逛逛</button>
              <button class="secondary" @click="goLivePets">看看活体宠物</button>
            </view>
          </view>
          <image class="hero-image" src="/static/home-hero.png" mode="aspectFill"></image>
        </view>

        <view class="panel guide-panel">
          <view class="guide-head">
            <view>
              <text class="panel-title">智能宠物导购</text>
              <text class="panel-note">告诉我宠物情况、预算或想解决的问题，我来帮你挑商品</text>
            </view>
            <text class="agent-badge">{{ guideResult && guideResult.source === 'deepseek' ? 'AI Agent' : '规则推荐' }}</text>
          </view>
          <view class="guide-form">
            <input class="guide-input main-input" v-model="guideForm.message" placeholder="例如：3 岁英短容易掉毛，预算 200，推荐用品" />
            <input class="guide-input budget-input" v-model="guideForm.budget" type="number" placeholder="预算" />
            <input class="guide-input pet-input" v-model="guideForm.pet_type" placeholder="猫/狗" />
            <button class="primary guide-btn" @click="askShoppingGuide">{{ guideLoading ? '推荐中' : '帮我挑' }}</button>
          </view>
          <view class="guide-result" v-if="guideResult">
            <text class="guide-summary">{{ guideResult.summary }}</text>
            <view class="guide-advice">
              <text class="advice-item" v-for="item in guideResult.advice" :key="item">{{ item }}</text>
            </view>
            <view class="guide-products" v-if="guideResult.products.length">
              <view class="guide-product" v-for="product in guideResult.products" :key="product.id" @click="goProductDetail(product)">
                <image class="guide-cover" :src="product.cover_url || '/static/logo.png'" mode="aspectFit"></image>
                <view class="guide-product-main">
                  <text class="guide-name">{{ product.title }}</text>
                  <text class="guide-reason">{{ product.reason }}</text>
                  <view class="guide-price-line">
                    <text class="guide-price">￥{{ money(product.price) }}</text>
                    <text class="guide-stock">库存 {{ product.stock }}</text>
                  </view>
                </view>
              </view>
            </view>
          </view>
        </view>

        <view class="feature-grid">
          <view class="feature-card clickable" @click="goProducts">
            <image class="feature-image" src="/static/home-supplies.png" mode="aspectFill"></image>
            <view class="feature-copy">
              <text class="metric-num">爆款</text>
              <text class="metric-title">宠物日用</text>
              <text class="metric-text">猫粮狗粮、玩具、清洁用品</text>
            </view>
          </view>
          <view class="feature-card clickable" @click="goPets">
            <image class="feature-image" src="/static/home-care.png" mode="aspectFill"></image>
            <view class="feature-copy">
              <text class="metric-num">服务</text>
              <text class="metric-title">宠物档案</text>
              <text class="metric-text">档案、成长记录、健康提醒</text>
            </view>
          </view>
          <view class="feature-card clickable" @click="goLivePets">
            <image class="feature-image" src="/static/home-live-pets.png" mode="aspectFill"></image>
            <view class="feature-copy">
              <text class="metric-num">活体</text>
              <text class="metric-title">健康宠物</text>
              <text class="metric-text">浏览活体宠物、购买后生成档案</text>
            </view>
          </view>
        </view>

        <view class="panel quick-panel">
          <view class="panel-head">
            <text class="panel-title">常用入口</text>
            <text class="panel-note">购物流程优先，管理入口靠后</text>
          </view>
          <view class="action-grid">
            <button class="primary" @click="goProducts">浏览商品</button>
            <button class="secondary" @click="goCart">查看购物车</button>
            <button class="secondary" @click="goOrders">查看订单</button>
            <button class="secondary" @click="goPets">维护宠物档案</button>
            <button class="secondary" @click="goMerchant">商家发布商品</button>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      apiBase: 'http://127.0.0.1:8000/api/v1',
      guideLoading: false,
      guideResult: null,
      guideForm: {
        message: '我家宠物容易掉毛，预算 200，推荐一些实用用品',
        budget: '200',
        pet_type: '',
        breed: ''
      }
    }
  },
  onLoad() {
    const savedBase = uni.getStorageSync('petShopApiBase')
    if (savedBase) this.apiBase = savedBase
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
    async askShoppingGuide() {
      if (!this.guideForm.message) return this.toast('请输入导购需求')
      this.guideLoading = true
      try {
        const payload = {
          message: this.guideForm.message,
          pet_type: this.guideForm.pet_type || undefined,
          breed: this.guideForm.breed || undefined,
          budget: this.guideForm.budget ? Number(this.guideForm.budget) : undefined
        }
        this.guideResult = await this.request({ url: '/agent/shopping-guide', method: 'POST', data: payload })
      } catch (error) {
        this.toast(error.message)
      } finally {
        this.guideLoading = false
      }
    },
    goAccount() { uni.navigateTo({ url: '/pages/account/account' }) },
    goProducts() { uni.navigateTo({ url: '/pages/product/list' }) },
    goProductDetail(product) { uni.navigateTo({ url: `/pages/product/detail?id=${product.id}` }) },
    goCart() { uni.navigateTo({ url: '/pages/cart/cart' }) },
    goOrders() { uni.navigateTo({ url: '/pages/order/list' }) },
    goPets() { uni.navigateTo({ url: '/pages/pet/index' }) },
    goLivePets() { uni.navigateTo({ url: '/pages/live-pet/list' }) },
    goMerchant() { uni.navigateTo({ url: '/pages/merchant/products' }) },
    goAudit() { uni.navigateTo({ url: '/pages/admin/audit' }) },
    money(value) { return Number(value || 0).toFixed(2) },
    toast(title) { uni.showToast({ title, icon: 'none' }) }
  }
}
</script>

<style>
page { background: #f5f5f5; }
.dashboard-page {
  max-width: 1400px !important;
  min-height: 100vh;
  color: #1f1f1f;
}
.app-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 18px 24px;
  border: 1px solid #ffe0cc;
  border-radius: 14px;
  background: linear-gradient(90deg, #fff7f0, #fff);
}
.brand { display: block; color: #ff5000; font-size: 28px; font-weight: 800; }
.sub { display: block; margin-top: 6px; color: #7a513b; font-size: 14px; }
.search-shell { display: flex; align-items: center; flex: 1; max-width: 560px; height: 42px; padding: 0 18px; border: 2px solid #ff6a00; border-radius: 999px; background: #fff; cursor: pointer; }
.search-icon { margin-right: 8px; color: #ff5000; font-size: 20px; }
.search-placeholder { color: #a56d4f; font-size: 14px; }
.account-btn { flex: 0 0 auto; }
.dashboard-layout {
  display: grid;
  width: 100%;
  grid-template-columns: 184px minmax(0, 1fr);
  gap: 22px !important;
  align-items: start;
  margin-top: 20px;
}
.dashboard-page .sidebar {
  width: auto !important;
  min-width: 0;
  padding: 18px;
  border: 1px solid #ffe0cc;
  border-radius: 14px;
  background: #fff;
}
.side-title { display: block; margin-bottom: 14px; color: #a45f38; font-size: 13px; font-weight: 700; }
.nav, .primary, .secondary, .ghost {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 38px;
  margin: 0;
  border-radius: 6px;
  font-size: 14px;
}
.nav {
  width: 100%;
  margin-bottom: 10px;
  color: #5f5149;
  background: #fff6f0;
}
.nav.active, .primary { color: #fff; background: linear-gradient(90deg, #ff7a1a, #ff3d00); }
.ghost, .secondary { color: #ff5000; background: #fff0e7; }
.ghost { padding: 0 18px; }
.main { width: 100%; min-width: 0; }
.hero, .panel, .feature-card {
  border: 1px solid #ffe0cc;
  border-radius: 14px;
  background: #fff;
}
.hero {
  display: grid;
  grid-template-columns: minmax(320px, .86fr) minmax(420px, 1.14fr);
  gap: 30px;
  align-items: center;
  min-height: 318px;
  padding: 30px 32px !important;
  overflow: hidden;
  background: linear-gradient(135deg, #fff2e8, #fff 58%, #ffe7d6);
}
.hero-copy { min-width: 0; }
.hero-image {
  width: 100%;
  height: 264px;
  border-radius: 16px;
  box-shadow: 0 14px 34px rgba(122, 75, 41, .16);
  background: #fff7f0;
}
.eyebrow { display: inline-flex; margin-bottom: 12px; padding: 5px 12px; border-radius: 999px; color: #ff5000; background: #fff; font-size: 13px; font-weight: 700; }
.title { display: block; font-size: 30px; font-weight: 800; line-height: 1.25; }
.desc { display: block; max-width: 560px; margin-top: 12px; color: #78523d; font-size: 15px; line-height: 1.7; }
.hero-actions { display: flex; gap: 12px; margin-top: 22px; }
.guide-panel { margin-top: 18px; padding: 24px 26px !important; }
.guide-head { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 16px; }
.agent-badge { flex: 0 0 auto; padding: 5px 12px; border-radius: 999px; color: #ff5000; background: #fff0e7; font-size: 12px; font-weight: 800; }
.guide-form {
  display: grid;
  grid-template-columns: minmax(360px, 1fr) 112px 120px 112px;
  gap: 12px;
  align-items: center;
}
.guide-input { width: 100%; height: 40px; padding: 0 14px; border: 1px solid #f0d2c0; border-radius: 999px; background: #fff7f0; font-size: 14px; line-height: 40px; }
.guide-btn { width: 110px; }
.guide-result { margin-top: 16px; padding-top: 16px; border-top: 1px solid #fff0e7; }
.guide-summary { display: block; color: #1f1f1f; font-size: 15px; font-weight: 700; line-height: 1.55; }
.guide-advice { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.advice-item { padding: 6px 10px; border-radius: 999px; color: #7a513b; background: #fff7f0; font-size: 12px; }
.guide-products { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin-top: 14px; }
.guide-product { display: flex; gap: 12px; min-width: 0; padding: 12px; border: 1px solid #ffe0cc; border-radius: 12px; background: #fff; cursor: pointer; transition: border-color .15s, box-shadow .15s; }
.guide-product:hover { border-color: #ff7a1a; box-shadow: 0 8px 18px rgba(255, 80, 0, .1); }
.guide-cover { flex: 0 0 auto; width: 72px; height: 72px; border-radius: 10px; background: #fff7f0; }
.guide-product-main { flex: 1; min-width: 0; }
.guide-name { display: -webkit-box; overflow: hidden; color: #1f1f1f; font-size: 14px; font-weight: 800; line-height: 1.35; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
.guide-reason { display: -webkit-box; overflow: hidden; margin-top: 5px; color: #7b6659; font-size: 12px; line-height: 1.45; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
.guide-price-line { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-top: 8px; }
.guide-price { color: #ff5000; font-size: 16px; font-weight: 900; }
.guide-stock { color: #a45f38; font-size: 12px; }
.feature-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; margin-top: 18px; }
.feature-card { overflow: hidden; min-height: 236px; transition: border-color .15s, transform .15s, box-shadow .15s; }
.feature-card.clickable { cursor: pointer; }
.feature-card.clickable:hover { border-color: #ff7a1a; box-shadow: 0 10px 24px rgba(255, 80, 0, .12); transform: translateY(-1px); }
.feature-image { width: 100%; height: 144px; background: #fff7f0; }
.feature-copy { padding: 16px 18px 18px; }
.metric-num { color: #ff5000; font-size: 15px; font-weight: 800; }
.metric-title { display: block; margin-top: 8px; font-size: 18px; font-weight: 700; }
.metric-text { display: block; margin-top: 8px; color: #7b6659; font-size: 13px; }
.quick-panel { margin-top: 16px; padding: 22px 26px; }
.panel-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.panel-title { font-size: 18px; font-weight: 700; }
.panel-note { color: #7a8492; font-size: 13px; }
.action-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 14px; }
@media screen and (max-width: 900px) {
  .app-topbar { flex-direction: column; align-items: stretch; }
  .search-shell { max-width: none; }
  .dashboard-layout { grid-template-columns: 1fr; }
  .dashboard-page .sidebar { width: 100% !important; }
  .hero { grid-template-columns: 1fr; }
  .hero-image { height: 220px; }
  .guide-head { align-items: flex-start; flex-direction: column; }
  .guide-form { grid-template-columns: 1fr; }
  .guide-btn { width: 100%; }
  .guide-products { grid-template-columns: 1fr; }
  .feature-grid, .action-grid { grid-template-columns: 1fr; }
  .hero-actions { flex-direction: column; }
}
</style>
