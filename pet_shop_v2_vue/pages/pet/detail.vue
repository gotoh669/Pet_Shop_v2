<template>
  <view class="page" v-if="pet">
    <view class="profile">
      <image class="avatar" :src="pet.avatar_url || fallbackImage" mode="aspectFit"></image>
      <view class="profile-info">
        <text class="name">{{ pet.name }}</text>
        <text class="muted">{{ typeText(pet.pet_type) }} · {{ pet.breed || '未知品种' }} · {{ genderText(pet.gender) }}</text>
        <text class="muted">体重 {{ pet.weight || '-' }} kg · {{ pet.is_current ? '当前宠物' : '普通档案' }}</text>
      </view>
      <button class="text-button" @click="goEdit">编辑</button>
    </view>

    <view class="panel">
      <text class="section-title">健康档案</text>
      <view class="meta-grid">
        <text>生日：{{ pet.birthday || '-' }}</text>
        <text>到家：{{ pet.arrival_date || '-' }}</text>
        <text>绝育：{{ sterilizedText(pet.sterilized) }}</text>
        <text>疫苗：{{ statusText(pet.vaccine_status) }}</text>
        <text>驱虫：{{ statusText(pet.deworm_status) }}</text>
        <text>隐私：{{ pet.visibility === 'public' ? '公开' : '私密' }}</text>
      </view>
      <text class="notes">{{ pet.health_notes || '暂无健康备注' }}</text>
    </view>

    <view class="panel">
      <text class="section-title">新增成长记录</text>
      <input class="input" v-model="recordForm.title" placeholder="标题，例如 今天称重" />
      <input class="input" v-model="recordForm.record_date" placeholder="日期 YYYY-MM-DD" />
      <input class="input" v-model="recordForm.weight" type="digit" placeholder="体重 kg，可选" />
      <textarea class="textarea" v-model="recordForm.content" placeholder="记录内容"></textarea>
      <button class="primary-button" @click="createRecord">保存记录</button>
    </view>

    <view class="panel">
      <text class="section-title">成长记录</text>
      <view class="item" v-for="record in records" :key="record.id">
        <text class="item-title">{{ record.title }}</text>
        <text class="muted">{{ record.record_date }} · {{ record.record_type }} · {{ record.weight ? record.weight + 'kg' : '未记录体重' }}</text>
        <text class="item-content">{{ record.content }}</text>
      </view>
      <text class="empty-text" v-if="!records.length">暂无成长记录</text>
    </view>

    <view class="panel">
      <text class="section-title">新增提醒</text>
      <input class="input" v-model="reminderForm.title" placeholder="提醒标题，例如 下次驱虫" />
      <input class="input" v-model="reminderForm.remind_at" placeholder="提醒时间 2026-07-01T09:00:00" />
      <input class="input" v-model="reminderForm.reminder_type" placeholder="类型 vaccine/deworm/bath/checkup/feed" />
      <button class="primary-button" @click="createReminder">保存提醒</button>
    </view>

    <view class="panel">
      <text class="section-title">提醒</text>
      <view class="item" v-for="reminder in reminders" :key="reminder.id">
        <text class="item-title">{{ reminder.title }}</text>
        <text class="muted">{{ reminder.remind_at }} · {{ reminder.reminder_type }} · {{ reminder.status }}</text>
        <button class="text-button item-button" v-if="reminder.status === 'active'" @click="finishReminder(reminder)">完成</button>
      </view>
      <text class="empty-text" v-if="!reminders.length">暂无提醒</text>
    </view>
  </view>
  <view class="empty-state" v-else>
    <text>加载中...</text>
  </view>
</template>

<script>
export default {
  data() {
    const today = new Date().toISOString().slice(0, 10)
    return {
      apiBase: 'http://127.0.0.1:8000/api/v1',
      token: '',
      petId: '',
      pet: null,
      records: [],
      reminders: [],
      fallbackImage: '/static/logo.png',
      recordForm: {
        record_type: 'daily',
        title: '',
        content: '',
        media_urls: [],
        weight: '',
        record_date: today
      },
      reminderForm: {
        reminder_type: 'deworm',
        title: '',
        remind_at: `${today}T09:00:00`,
        repeat_rule: ''
      }
    }
  },
  onLoad(options) {
    const savedBase = uni.getStorageSync('petShopApiBase')
    if (savedBase) {
      this.apiBase = savedBase
    }
    this.token = uni.getStorageSync('petShopToken')
    this.petId = options.id
    this.loadAll()
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
    async loadAll() {
      try {
        this.pet = await this.request({ url: `/pets/${this.petId}` })
        this.records = await this.request({ url: `/pets/${this.petId}/records` }) || []
        this.reminders = await this.request({ url: `/pets/${this.petId}/reminders` }) || []
      } catch (error) {
        this.toast(error.message)
      }
    },
    async createRecord() {
      if (!this.recordForm.title) {
        this.toast('请输入记录标题')
        return
      }
      const payload = Object.assign({}, this.recordForm, {
        weight: this.recordForm.weight === '' ? null : Number(this.recordForm.weight)
      })
      try {
        await this.request({ url: `/pets/${this.petId}/records`, method: 'POST', data: payload })
        this.recordForm.title = ''
        this.recordForm.content = ''
        this.recordForm.weight = ''
        await this.loadAll()
        this.toast('记录已保存')
      } catch (error) {
        this.toast(error.message)
      }
    },
    async createReminder() {
      if (!this.reminderForm.title || !this.reminderForm.remind_at) {
        this.toast('请输入提醒内容')
        return
      }
      try {
        await this.request({ url: `/pets/${this.petId}/reminders`, method: 'POST', data: this.reminderForm })
        this.reminderForm.title = ''
        await this.loadAll()
        this.toast('提醒已保存')
      } catch (error) {
        this.toast(error.message)
      }
    },
    async finishReminder(reminder) {
      try {
        await this.request({ url: `/pets/reminders/${reminder.id}`, method: 'PATCH', data: { status: 'done' } })
        await this.loadAll()
      } catch (error) {
        this.toast(error.message)
      }
    },
    goEdit() {
      uni.navigateTo({ url: `/pages/pet/edit?id=${this.petId}` })
    },
    typeText(value) { return value === 'dog' ? '狗狗' : '猫咪' },
    genderText(value) { return ({ male: '男孩', female: '女孩', unknown: '未知' })[value] || value },
    sterilizedText(value) { return ({ yes: '已绝育', no: '未绝育', unknown: '未知' })[value] || value },
    statusText(value) { return ({ completed: '已完成', regular: '规律', pending: '待完成', unknown: '未知' })[value] || value },
    toast(title) { uni.showToast({ title, icon: 'none' }) }
  }
}
</script>

<style>
page { background: #f4f6f8; }
.page { min-height: 100vh; padding: 24rpx; box-sizing: border-box; }
.profile, .panel { border-radius: 8rpx; background: #fff; }
.profile { display: flex; align-items: center; gap: 18rpx; padding: 22rpx; margin-bottom: 20rpx; }
.avatar { width: 120rpx; height: 120rpx; border-radius: 60rpx; background: #edf1f4; }
.profile-info { flex: 1; min-width: 0; }
.name { display: block; color: #172033; font-size: 34rpx; font-weight: 700; }
.muted { display: block; margin-top: 8rpx; color: #718093; font-size: 23rpx; line-height: 1.5; }
.panel { padding: 24rpx; margin-bottom: 20rpx; }
.section-title { display: block; margin-bottom: 16rpx; font-size: 29rpx; font-weight: 700; }
.meta-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12rpx; color: #526172; font-size: 23rpx; }
.notes, .item-content, .empty-text { display: block; margin-top: 14rpx; color: #526172; font-size: 24rpx; line-height: 1.6; }
.input, .textarea { box-sizing: border-box; width: 100%; margin-bottom: 14rpx; border: 1rpx solid #d9e0e8; border-radius: 8rpx; background: #fbfcfd; font-size: 25rpx; }
.input { height: 74rpx; padding: 0 20rpx; }
.textarea { min-height: 130rpx; padding: 18rpx 20rpx; line-height: 1.5; }
.primary-button, .text-button { display: flex; align-items: center; justify-content: center; height: 58rpx; margin: 0; padding: 0 18rpx; border-radius: 8rpx; font-size: 23rpx; }
.primary-button { color: #fff; background: #1c6b56; }
.text-button { color: #1c6b56; background: #e8f3ef; }
.item { padding: 18rpx 0; border-top: 1rpx solid #edf1f4; }
.item:first-of-type { border-top: none; }
.item-title { display: block; font-size: 26rpx; font-weight: 700; }
.item-button { margin-top: 12rpx; width: 120rpx; }
.empty-state { padding: 120rpx 20rpx; text-align: center; color: #798493; }
</style>
