<template>
  <view class="page">
    <view class="hero">
      <text class="title">宠物商城</text>
      <text class="subtitle">用品和待售宠物分开浏览，购买宠物后会进入“我的宠物”</text>
    </view>

    <view class="entry-grid">
      <view class="entry-card supplies" @click="goProducts">
        <text class="entry-title">买用品</text>
        <text class="entry-subtitle">粮食、零食、玩具、清洁护理</text>
      </view>
      <view class="entry-card pets" @click="goLivePets">
        <text class="entry-title">买宠物</text>
        <text class="entry-subtitle">查看商家发布的待售宠物</text>
      </view>
    </view>

    <view class="quick-actions">
      <button class="action-button" @click="goCart">购物车</button>
      <button class="action-button" @click="goMerchant">商家管理</button>
      <button class="action-button" @click="goAudit">平台审核</button>
    </view>
  </view>
</template>

<script>
export default {
  methods: {
    goProducts() {
      uni.navigateTo({ url: '/pages/product/list' })
    },
    goLivePets() {
      uni.navigateTo({ url: '/pages/live-pet/list' })
    },
    goCart() {
      uni.navigateTo({ url: '/pages/cart/cart' })
    },
    goMerchant() {
      uni.navigateTo({ url: '/pages/merchant/products' })
    },
    goAudit() {
      uni.navigateTo({ url: '/pages/admin/audit' })
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
  padding: 28rpx;
  box-sizing: border-box;
  color: #172033;
}

.hero {
  padding: 40rpx 4rpx 28rpx;
}

.title {
  display: block;
  font-size: 44rpx;
  font-weight: 700;
}

.subtitle {
  display: block;
  margin-top: 12rpx;
  color: #647285;
  font-size: 25rpx;
  line-height: 1.5;
}

.entry-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18rpx;
}

.entry-card {
  min-height: 260rpx;
  padding: 28rpx;
  border-radius: 8rpx;
  box-sizing: border-box;
}

.supplies {
  background: #ffffff;
  border: 1rpx solid #dfe6ee;
}

.pets {
  background: #e8f3ef;
  border: 1rpx solid #c8e1d7;
}

.entry-title {
  display: block;
  font-size: 34rpx;
  font-weight: 700;
}

.entry-subtitle {
  display: block;
  margin-top: 16rpx;
  color: #526172;
  font-size: 24rpx;
  line-height: 1.5;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14rpx;
  margin-top: 24rpx;
}

.action-button {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 72rpx;
  margin: 0;
  border: 1rpx solid #dfe6ee;
  border-radius: 8rpx;
  color: #1c6b56;
  background: #ffffff;
  font-size: 24rpx;
}
</style>
