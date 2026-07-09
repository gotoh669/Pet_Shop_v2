<template>
  <view class="page">
    <view class="toolbar">
      <view>
        <text class="title">宠物档案</text>
        <text class="subtitle">管理当前账号下的宠物资料、成长记录和提醒</text>
      </view>
      <button class="primary" @click="goEdit()">新增宠物</button>
    </view>

    <view class="panel table" v-if="pets.length">
      <view class="row head">
        <text>宠物</text>
        <text>类型</text>
        <text>健康状态</text>
        <text>来源</text>
        <text>操作</text>
      </view>
      <view class="row" v-for="pet in pets" :key="pet.id">
        <view class="pet-cell" @click="goDetail(pet)">
          <image class="avatar" :src="pet.avatar_url || fallbackImage" mode="aspectFit"></image>
          <view class="pet-info">
            <text class="name">{{ pet.name }}</text>
            <text class="muted">{{ pet.breed || '未知品种' }} · {{ genderText(pet.gender) }}</text>
          </view>
        </view>
        <text>{{ typeText(pet.pet_type) }}</text>
        <text>疫苗 {{ statusText(pet.vaccine_status) }} / 驱虫 {{ statusText(pet.deworm_status) }}</text>
        <text>{{ sourceText(pet.source_type) }}</text>
        <view class="actions">
          <button class="ghost" @click="goDetail(pet)">详情</button>
          <button class="ghost" :disabled="pet.is_current" @click="setCurrent(pet)">{{ pet.is_current ? '当前' : '设为当前' }}</button>
        </view>
      </view>
    </view>

    <view class="empty panel" v-else>
      <text>{{ token ? '还没有宠物档案' : '请先登录后查看宠物档案' }}</text>
      <button class="primary empty-btn" v-if="!token" @click="goAccount">去登录</button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return { apiBase: 'http://127.0.0.1:8000/api/v1', token: '', pets: [], fallbackImage: '/static/logo.png' }
  },
  onShow() {
    const savedBase = uni.getStorageSync('petShopApiBase')
    if (savedBase) this.apiBase = savedBase
    this.token = uni.getStorageSync('petShopToken')
    this.loadPets()
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
    async loadPets() {
      if (!this.token) return
      try { this.pets = await this.request({ url: '/pets' }) || [] } catch (error) { this.toast(error.message) }
    },
    async setCurrent(pet) {
      if (pet.is_current) return
      try {
        await this.request({ url: `/pets/${pet.id}/current`, method: 'POST' })
        await this.loadPets()
      } catch (error) {
        this.toast(error.message)
      }
    },
    goDetail(pet) { uni.navigateTo({ url: `/pages/pet/detail?id=${pet.id}` }) },
    goEdit(pet) { uni.navigateTo({ url: pet ? `/pages/pet/edit?id=${pet.id}` : '/pages/pet/edit' }) },
    goAccount() { uni.navigateTo({ url: '/pages/account/account' }) },
    typeText(value) { return ({ cat: '猫', dog: '狗', rabbit: '兔子' })[value] || value },
    genderText(value) { return ({ male: '公', female: '母', unknown: '未知' })[value] || value },
    statusText(value) { return ({ completed: '已完成', regular: '规律', pending: '待完成', unknown: '未知' })[value] || value },
    sourceText(value) { return ({ manual: '手动', purchase: '购买', adoption: '领养' })[value] || '手动' },
    toast(title) { uni.showToast({ title, icon: 'none' }) }
  }
}
</script>

<style>
page { background: #f3f5f8; }
.page { min-height: 100vh; padding: 24rpx; color: #172033; }
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18rpx; }
.title { display: block; font-size: 36rpx; font-weight: 700; }
.subtitle, .muted { display: block; margin-top: 8rpx; color: #6b7788; font-size: 23rpx; }
.panel { border: 1rpx solid #e2e8ef; border-radius: 8rpx; background: #fff; }
.table { overflow: hidden; }
.row { display: grid; grid-template-columns: minmax(260rpx, 1.6fr) 120rpx minmax(260rpx, 1.2fr) 120rpx minmax(260rpx, 300rpx); gap: 18rpx; align-items: center; padding: 18rpx 22rpx; border-bottom: 1rpx solid #edf1f5; font-size: 24rpx; }
.row:last-child { border-bottom: none; }
.head { color: #6b7788; background: #f7f9fb; font-weight: 700; }
.pet-cell { display: flex; align-items: center; gap: 14rpx; min-width: 0; cursor: pointer; }
.pet-info { min-width: 0; }
.avatar { width: 76rpx; height: 76rpx; border-radius: 50%; background: #edf1f4; flex: 0 0 auto; }
.name { display: block; font-size: 26rpx; font-weight: 700; }
.actions { display: flex; gap: 10rpx; align-items: center; justify-content: flex-start; flex-wrap: nowrap; min-width: 0; }
.primary, .ghost { display: flex; align-items: center; justify-content: center; height: 58rpx; margin: 0; padding: 0 18rpx; border-radius: 8rpx; font-size: 23rpx; white-space: nowrap; box-sizing: border-box; }
.primary { color: #fff; background: #1f6b57; }
.ghost { min-width: 92rpx; color: #1f6b57; background: #e8f3ef; flex: 0 0 auto; }
.ghost[disabled] { opacity: .72; }
.empty { padding: 80rpx 20rpx; color: #798493; text-align: center; font-size: 26rpx; }
.empty-btn { width: 180rpx; margin: 20rpx auto 0; }
@media screen and (max-width: 760px) {
  .toolbar { flex-direction: column; align-items: stretch; gap: 16rpx; }
  .row { grid-template-columns: 1fr; gap: 10rpx; }
  .head { display: none; }
  .actions { flex-wrap: wrap; }
}
</style>
