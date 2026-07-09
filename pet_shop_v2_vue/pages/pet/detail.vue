<template>
  <view class="page" v-if="pet">
    <view class="profile panel">
      <image class="avatar" :src="pet.avatar_url || fallbackImage" mode="aspectFit"></image>
      <view class="profile-main">
        <text class="title">{{ pet.name }}</text>
        <text class="subtitle">{{ typeText(pet.pet_type) }} · {{ pet.breed || '未知品种' }} · {{ genderText(pet.gender) }}</text>
        <text class="muted">体重 {{ pet.weight || '-' }} kg · {{ pet.is_current ? '当前宠物' : '普通档案' }}</text>
      </view>
      <button class="ghost" @click="goEdit">编辑</button>
    </view>

    <view class="grid">
      <view class="panel">
        <text class="panel-title">健康档案</text>
        <view class="meta">
          <text>生日：{{ pet.birthday || '-' }}</text>
          <text>到家：{{ pet.arrival_date || '-' }}</text>
          <text>绝育：{{ sterilizedText(pet.sterilized) }}</text>
          <text>疫苗：{{ statusText(pet.vaccine_status) }}</text>
          <text>驱虫：{{ statusText(pet.deworm_status) }}</text>
          <text>隐私：{{ pet.visibility === 'public' ? '公开' : '私密' }}</text>
        </view>
        <text class="body-text">{{ pet.health_notes || '暂无健康备注' }}</text>
      </view>

      <view class="panel">
        <text class="panel-title">新增提醒</text>
        <input class="input" v-model="reminderForm.title" placeholder="提醒标题，例如 下次驱虫" />
        <input class="input" v-model="reminderForm.remind_at" placeholder="提醒时间 2026-07-01T09:00:00" />
        <input class="input" v-model="reminderForm.reminder_type" placeholder="类型 vaccine/deworm/bath/checkup/feed" />
        <button class="primary" @click="createReminder">保存提醒</button>
      </view>
    </view>

    <view class="panel">
      <text class="panel-title">新增成长记录</text>
      <view class="form-grid">
        <input class="input" v-model="recordForm.title" placeholder="标题，例如 今天称重" />
        <input class="input" v-model="recordForm.record_date" placeholder="日期 YYYY-MM-DD" />
        <input class="input" v-model="recordForm.weight" type="digit" placeholder="体重 kg，可选" />
      </view>
      <textarea class="textarea" v-model="recordForm.content" placeholder="记录内容"></textarea>
      <button class="primary" @click="createRecord">保存记录</button>
    </view>

    <view class="grid">
      <view class="panel">
        <text class="panel-title">成长记录</text>
        <view class="item" v-for="record in records" :key="record.id">
          <text class="item-title">{{ record.title }}</text>
          <text class="muted">{{ record.record_date }} · {{ record.weight ? record.weight + 'kg' : '未记录体重' }}</text>
          <text class="body-text">{{ record.content || '暂无内容' }}</text>
        </view>
        <text class="empty-text" v-if="!records.length">暂无成长记录</text>
      </view>

      <view class="panel">
        <text class="panel-title">提醒</text>
        <view class="item" v-for="reminder in reminders" :key="reminder.id">
          <text class="item-title">{{ reminder.title }}</text>
          <text class="muted">{{ reminder.remind_at }} · {{ reminder.reminder_type }} · {{ reminder.status }}</text>
          <button class="ghost mini" v-if="reminder.status === 'active'" @click="finishReminder(reminder)">完成</button>
        </view>
        <text class="empty-text" v-if="!reminders.length">暂无提醒</text>
      </view>
    </view>
  </view>
  <view class="empty" v-else>加载中...</view>
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
      recordForm: { record_type: 'daily', title: '', content: '', media_urls: [], weight: '', record_date: today },
      reminderForm: { reminder_type: 'deworm', title: '', remind_at: `${today}T09:00:00`, repeat_rule: '' }
    }
  },
  onLoad(options) {
    const savedBase = uni.getStorageSync('petShopApiBase')
    if (savedBase) this.apiBase = savedBase
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
            if (response.statusCode >= 200 && response.statusCode < 300 && response.data && response.data.code === 0) return resolve(response.data.data)
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
      if (!this.recordForm.title) return this.toast('请输入记录标题')
      const payload = Object.assign({}, this.recordForm, { weight: this.recordForm.weight === '' ? null : Number(this.recordForm.weight) })
      try {
        await this.request({ url: `/pets/${this.petId}/records`, method: 'POST', data: payload })
        this.recordForm.title = ''
        this.recordForm.content = ''
        this.recordForm.weight = ''
        await this.loadAll()
      } catch (error) {
        this.toast(error.message)
      }
    },
    async createReminder() {
      if (!this.reminderForm.title || !this.reminderForm.remind_at) return this.toast('请输入提醒内容')
      try {
        await this.request({ url: `/pets/${this.petId}/reminders`, method: 'POST', data: this.reminderForm })
        this.reminderForm.title = ''
        await this.loadAll()
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
    goEdit() { uni.navigateTo({ url: `/pages/pet/edit?id=${this.petId}` }) },
    typeText(value) { return ({ cat: '猫', dog: '狗', rabbit: '兔子' })[value] || value },
    genderText(value) { return ({ male: '公', female: '母', unknown: '未知' })[value] || value },
    sterilizedText(value) { return ({ yes: '已绝育', no: '未绝育', unknown: '未知' })[value] || value },
    statusText(value) { return ({ completed: '已完成', regular: '规律', pending: '待完成', unknown: '未知' })[value] || value },
    toast(title) { uni.showToast({ title, icon: 'none' }) }
  }
}
</script>

<style>
page { background: #f3f5f8; }
.page { min-height: 100vh; padding: 24rpx; color: #172033; }
.panel { padding: 22rpx; border: 1rpx solid #e2e8ef; border-radius: 8rpx; background: #fff; }
.profile { display: flex; align-items: center; gap: 18rpx; margin-bottom: 18rpx; }
.avatar { width: 110rpx; height: 110rpx; border-radius: 55rpx; background: #edf1f4; }
.profile-main { flex: 1; min-width: 0; }
.title { display: block; font-size: 36rpx; font-weight: 700; }
.subtitle, .muted { display: block; margin-top: 8rpx; color: #6b7788; font-size: 23rpx; }
.grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18rpx; margin-bottom: 18rpx; }
.panel-title { display: block; margin-bottom: 14rpx; font-size: 28rpx; font-weight: 700; }
.meta { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10rpx; color: #526172; font-size: 23rpx; }
.body-text, .empty-text { display: block; margin-top: 12rpx; color: #526172; font-size: 24rpx; line-height: 1.6; }
.form-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12rpx; }
.input, .textarea { width: 100%; border: 1rpx solid #d9e0e8; border-radius: 8rpx; background: #fbfcfd; font-size: 24rpx; }
.input { height: 70rpx; padding: 0 18rpx; margin-bottom: 12rpx; }
.textarea { min-height: 120rpx; padding: 18rpx; margin-bottom: 12rpx; line-height: 1.5; }
.primary, .ghost { display: flex; align-items: center; justify-content: center; height: 58rpx; margin: 0; padding: 0 18rpx; border-radius: 8rpx; font-size: 23rpx; }
.primary { width: 180rpx; color: #fff; background: #1f6b57; }
.ghost { color: #1f6b57; background: #e8f3ef; }
.mini { width: 110rpx; margin-top: 10rpx; }
.item { padding: 14rpx 0; border-top: 1rpx solid #edf1f5; }
.item:first-of-type { border-top: none; }
.item-title { display: block; font-size: 25rpx; font-weight: 700; }
.empty { padding: 120rpx 20rpx; color: #798493; text-align: center; }
@media screen and (max-width: 760px) {
  .profile { flex-direction: column; align-items: stretch; }
  .grid, .form-grid { grid-template-columns: 1fr; }
}
</style>
