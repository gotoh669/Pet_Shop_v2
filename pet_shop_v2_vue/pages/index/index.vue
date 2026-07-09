<template>
  <view class="page dashboard-page">
    <view class="topbar app-topbar">
      <view>
        <text class="brand">宠物商城工作台</text>
        <text class="sub">商品、订单、宠物档案与审核业务统一入口</text>
      </view>
      <button class="ghost" @click="goAccount">账号中心</button>
    </view>

    <view class="layout dashboard-layout">
      <view class="sidebar">
        <text class="side-title">业务导航</text>
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
          <text class="title">宠物商城后台业务系统</text>
          <text class="desc">当前系统已支持商品浏览、购物车下单、模拟支付、宠物档案、商家商品与平台审核。请选择左侧菜单或下方模块进入业务页面。</text>
        </view>

        <view class="metric-grid">
          <view class="metric clickable" @click="goProducts">
            <text class="metric-num">01</text>
            <text class="metric-title">商品商城</text>
            <text class="metric-text">分类、列表、详情、加入购物车</text>
          </view>
          <view class="metric clickable" @click="goPets">
            <text class="metric-num">02</text>
            <text class="metric-title">宠物档案</text>
            <text class="metric-text">档案、成长记录、健康提醒</text>
          </view>
          <view class="metric clickable" @click="goAudit">
            <text class="metric-num">03</text>
            <text class="metric-title">商家与审核</text>
            <text class="metric-text">商品发布、提交审核、平台处理</text>
          </view>
        </view>

        <view class="panel quick-panel">
          <view class="panel-head">
            <text class="panel-title">推荐操作</text>
            <text class="panel-note">按业务流程从左到右体验</text>
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
  methods: {
    goAccount() { uni.navigateTo({ url: '/pages/account/account' }) },
    goProducts() { uni.navigateTo({ url: '/pages/product/list' }) },
    goCart() { uni.navigateTo({ url: '/pages/cart/cart' }) },
    goOrders() { uni.navigateTo({ url: '/pages/order/list' }) },
    goPets() { uni.navigateTo({ url: '/pages/pet/index' }) },
    goLivePets() { uni.navigateTo({ url: '/pages/live-pet/list' }) },
    goMerchant() { uni.navigateTo({ url: '/pages/merchant/products' }) },
    goAudit() { uni.navigateTo({ url: '/pages/admin/audit' }) }
  }
}
</script>

<style>
page { background: #f3f5f8; }
.dashboard-page { min-height: 100vh; color: #172033; }
.app-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 22px 26px;
  border: 1px solid #e2e8ef;
  border-radius: 8px;
  background: #fff;
}
.brand { display: block; font-size: 26px; font-weight: 700; }
.sub { display: block; margin-top: 6px; color: #6b7788; font-size: 14px; }
.dashboard-layout { display: grid; grid-template-columns: 190px minmax(0, 1fr); gap: 18px; margin-top: 18px; }
.sidebar { padding: 18px; border: 1px solid #e2e8ef; border-radius: 8px; background: #fff; }
.side-title { display: block; margin-bottom: 14px; color: #6b7788; font-size: 13px; }
.nav, .primary, .secondary, .ghost {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 38px;
  margin: 0;
  border-radius: 6px;
  font-size: 14px;
}
.nav { width: 100%; margin-bottom: 8px; color: #526172; background: #f6f8fa; }
.nav.active, .primary { color: #fff; background: #1f6b57; }
.ghost, .secondary { color: #1f6b57; background: #e8f3ef; }
.ghost { padding: 0 18px; }
.main { min-width: 0; }
.hero, .panel, .metric {
  border: 1px solid #e2e8ef;
  border-radius: 8px;
  background: #fff;
}
.hero { padding: 26px 28px; }
.title { display: block; font-size: 28px; font-weight: 700; line-height: 1.25; }
.desc { display: block; max-width: 720px; margin-top: 12px; color: #647285; font-size: 15px; line-height: 1.7; }
.metric-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; margin-top: 16px; }
.metric { min-height: 124px; padding: 22px; transition: border-color .15s, transform .15s, box-shadow .15s; }
.metric.clickable { cursor: pointer; }
.metric.clickable:hover { border-color: #1f6b57; box-shadow: 0 8px 18px rgba(31, 107, 87, .08); transform: translateY(-1px); }
.metric-num { color: #1f6b57; font-size: 15px; font-weight: 700; }
.metric-title { display: block; margin-top: 12px; font-size: 18px; font-weight: 700; }
.metric-text { display: block; margin-top: 8px; color: #6b7788; font-size: 13px; }
.quick-panel { margin-top: 16px; padding: 22px 26px; }
.panel-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.panel-title { font-size: 18px; font-weight: 700; }
.panel-note { color: #7a8492; font-size: 13px; }
.action-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 14px; }
@media screen and (max-width: 900px) {
  .dashboard-layout { grid-template-columns: 1fr; }
  .metric-grid, .action-grid { grid-template-columns: 1fr; }
}
</style>
