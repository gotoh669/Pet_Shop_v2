<template>
  <view class="page">
    <view class="panel">
      <view class="head">
        <text class="title">{{ petId ? '编辑宠物档案' : '新增宠物档案' }}</text>
        <button class="ghost" @click="goBack">返回</button>
      </view>

      <view class="form-grid">
        <view class="field">
          <text class="label">宠物名</text>
          <input class="input" v-model.trim="form.name" placeholder="例如 奶茶" />
        </view>
        <view class="field">
          <text class="label">类型</text>
          <picker :range="typeOptions" range-key="label" @change="onTypeChange">
            <view class="picker">{{ typeLabel }}</view>
          </picker>
        </view>
        <view class="field">
          <text class="label">品种</text>
          <input class="input" v-model.trim="form.breed" placeholder="例如 英短 / 柯基" />
        </view>
        <view class="field">
          <text class="label">性别</text>
          <picker :range="genderOptions" range-key="label" @change="onGenderChange">
            <view class="picker">{{ genderLabel }}</view>
          </picker>
        </view>
        <view class="field">
          <text class="label">体重 kg</text>
          <input class="input" v-model.trim="form.weight" type="digit" placeholder="例如 4.5，可不填" />
        </view>
        <view class="field">
          <text class="label">头像 URL</text>
          <input class="input" v-model.trim="form.avatar_url" placeholder="/static/logo.png" />
        </view>
        <view class="field">
          <text class="label">生日</text>
          <input class="input" v-model.trim="form.birthday" placeholder="YYYY-MM-DD，可不填" />
        </view>
        <view class="field">
          <text class="label">到家日期</text>
          <input class="input" v-model.trim="form.arrival_date" placeholder="YYYY-MM-DD，可不填" />
        </view>
        <view class="field">
          <text class="label">绝育情况</text>
          <picker :range="sterilizedOptions" range-key="label" @change="onSterilizedChange">
            <view class="picker">{{ sterilizedLabel }}</view>
          </picker>
        </view>
        <view class="field">
          <text class="label">疫苗状态</text>
          <picker :range="statusOptions" range-key="label" @change="onVaccineChange">
            <view class="picker">{{ vaccineLabel }}</view>
          </picker>
        </view>
        <view class="field">
          <text class="label">驱虫状态</text>
          <picker :range="statusOptions" range-key="label" @change="onDewormChange">
            <view class="picker">{{ dewormLabel }}</view>
          </picker>
        </view>
        <view class="field switch-field">
          <text class="label">当前宠物</text>
          <view class="switch-line">
            <text>{{ form.is_current ? '已设为当前宠物' : '未设为当前宠物' }}</text>
            <switch :checked="form.is_current" color="#1f6b57" @change="form.is_current = Boolean($event.detail.value)" />
          </view>
        </view>
      </view>

      <view class="field full-field">
        <text class="label">健康备注</text>
        <textarea class="textarea" v-model.trim="form.health_notes" placeholder="例如过敏、疫苗提醒、日常护理备注，可不填"></textarea>
      </view>

      <button class="primary" @click="savePet">保存</button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      apiBase: 'http://127.0.0.1:8000/api/v1',
      token: '',
      petId: '',
      typeOptions: [{ label: '猫', value: 'cat' }, { label: '狗', value: 'dog' }, { label: '兔子', value: 'rabbit' }],
      genderOptions: [{ label: '未知', value: 'unknown' }, { label: '公', value: 'male' }, { label: '母', value: 'female' }],
      sterilizedOptions: [{ label: '绝育未知', value: 'unknown' }, { label: '已绝育', value: 'yes' }, { label: '未绝育', value: 'no' }],
      statusOptions: [{ label: '未知', value: 'unknown' }, { label: '待完成', value: 'pending' }, { label: '已完成', value: 'completed' }, { label: '规律进行', value: 'regular' }],
      form: { name: '', pet_type: 'cat', breed: '', gender: 'unknown', birthday: '', arrival_date: '', weight: '', avatar_url: '/static/logo.png', sterilized: 'unknown', vaccine_status: 'unknown', deworm_status: 'unknown', health_notes: '', visibility: 'private', is_current: false }
    }
  },
  computed: {
    typeLabel() { return this.labelOf(this.typeOptions, this.form.pet_type) },
    genderLabel() { return this.labelOf(this.genderOptions, this.form.gender) },
    sterilizedLabel() { return this.labelOf(this.sterilizedOptions, this.form.sterilized) },
    vaccineLabel() { return this.labelOf(this.statusOptions, this.form.vaccine_status) },
    dewormLabel() { return this.labelOf(this.statusOptions, this.form.deworm_status) }
  },
  onLoad(options) {
    const savedBase = uni.getStorageSync('petShopApiBase')
    if (savedBase) this.apiBase = savedBase
    this.token = uni.getStorageSync('petShopToken')
    this.petId = options.id || ''
    if (!this.token) return uni.navigateTo({ url: '/pages/account/account' })
    if (this.petId) this.loadPet()
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
    async loadPet() {
      try {
        const data = await this.request({ url: `/pets/${this.petId}` })
        this.form = Object.assign({}, this.form, data, { weight: data.weight || '', birthday: data.birthday || '', arrival_date: data.arrival_date || '' })
      } catch (error) {
        this.toast(error.message)
      }
    },
    validateForm() {
      const datePattern = /^\d{4}-\d{2}-\d{2}$/
      if (!this.form.name) return '请输入宠物名'
      if (this.form.weight !== '' && (Number.isNaN(Number(this.form.weight)) || Number(this.form.weight) < 0)) return '体重必须是大于等于 0 的数字'
      if (this.form.birthday && !datePattern.test(this.form.birthday)) return '生日格式应为 YYYY-MM-DD'
      if (this.form.arrival_date && !datePattern.test(this.form.arrival_date)) return '到家日期格式应为 YYYY-MM-DD'
      return ''
    },
    async savePet() {
      const message = this.validateForm()
      if (message) return this.toast(message)
      const payload = Object.assign({}, this.form, {
        weight: this.form.weight === '' ? null : Number(this.form.weight),
        birthday: this.form.birthday || null,
        arrival_date: this.form.arrival_date || null
      })
      try {
        await this.request({ url: this.petId ? `/pets/${this.petId}` : '/pets', method: this.petId ? 'PUT' : 'POST', data: payload })
        this.toast('已保存')
        setTimeout(() => this.goBack(), 400)
      } catch (error) {
        this.toast(error.message)
      }
    },
    onTypeChange(event) { this.form.pet_type = this.typeOptions[Number(event.detail.value)].value },
    onGenderChange(event) { this.form.gender = this.genderOptions[Number(event.detail.value)].value },
    onSterilizedChange(event) { this.form.sterilized = this.sterilizedOptions[Number(event.detail.value)].value },
    onVaccineChange(event) { this.form.vaccine_status = this.statusOptions[Number(event.detail.value)].value },
    onDewormChange(event) { this.form.deworm_status = this.statusOptions[Number(event.detail.value)].value },
    labelOf(options, value) { const item = options.find(option => option.value === value); return item ? item.label : '请选择' },
    goBack() {
      const pages = getCurrentPages()
      if (pages.length > 1) return uni.navigateBack({ delta: 1 })
      uni.navigateTo({ url: '/pages/pet/index' })
    },
    toast(title) { uni.showToast({ title, icon: 'none' }) }
  }
}
</script>

<style>
page { background: #f3f5f8; }
.page { min-height: 100vh; padding: 24rpx; color: #172033; }
.panel { padding: 28rpx; border: 1rpx solid #e2e8ef; border-radius: 8rpx; background: #fff; }
.head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 22rpx; }
.title { font-size: 34rpx; font-weight: 700; }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16rpx; }
.field { min-width: 0; }
.label { display: block; margin-bottom: 8rpx; color: #536173; font-size: 22rpx; font-weight: 600; }
.input, .picker, .textarea { width: 100%; border: 1rpx solid #d9e0e8; border-radius: 8rpx; background: #fbfcfd; color: #172033; font-size: 24rpx; box-sizing: border-box; }
.input, .picker { height: 72rpx; padding: 0 18rpx; line-height: 72rpx; }
.textarea { min-height: 150rpx; padding: 18rpx; line-height: 1.5; }
.full-field { margin-top: 16rpx; }
.switch-line { display: flex; align-items: center; justify-content: space-between; height: 72rpx; padding: 0 18rpx; border: 1rpx solid #d9e0e8; border-radius: 8rpx; background: #fbfcfd; color: #526172; box-sizing: border-box; }
.primary, .ghost { display: flex; align-items: center; justify-content: center; height: 62rpx; margin: 18rpx 0 0; padding: 0 22rpx; border-radius: 8rpx; font-size: 24rpx; }
.primary { width: 220rpx; color: #fff; background: #1f6b57; }
.ghost { margin: 0; color: #1f6b57; background: #e8f3ef; }
@media screen and (max-width: 760px) {
  .form-grid { grid-template-columns: 1fr; }
}
</style>
