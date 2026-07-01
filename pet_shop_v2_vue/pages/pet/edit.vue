<template>
  <view class="page">
    <view class="panel">
      <text class="title">{{ petId ? '编辑宠物' : '新增宠物' }}</text>
      <input class="input" v-model="form.name" placeholder="宠物名" />
      <picker :range="typeOptions" range-key="label" @change="onTypeChange">
        <view class="picker">{{ typeLabel }}</view>
      </picker>
      <input class="input" v-model="form.breed" placeholder="品种，例如 英短 / 柯基" />
      <picker :range="genderOptions" range-key="label" @change="onGenderChange">
        <view class="picker">{{ genderLabel }}</view>
      </picker>
      <input class="input" v-model="form.weight" type="digit" placeholder="体重 kg" />
      <input class="input" v-model="form.avatar_url" placeholder="头像 URL，例如 /static/logo.png" />
      <input class="input" v-model="form.birthday" placeholder="生日 YYYY-MM-DD" />
      <input class="input" v-model="form.arrival_date" placeholder="到家日期 YYYY-MM-DD" />
      <picker :range="sterilizedOptions" range-key="label" @change="onSterilizedChange">
        <view class="picker">{{ sterilizedLabel }}</view>
      </picker>
      <picker :range="statusOptions" range-key="label" @change="onVaccineChange">
        <view class="picker">疫苗：{{ vaccineLabel }}</view>
      </picker>
      <picker :range="statusOptions" range-key="label" @change="onDewormChange">
        <view class="picker">驱虫：{{ dewormLabel }}</view>
      </picker>
      <textarea class="textarea" v-model="form.health_notes" placeholder="健康备注"></textarea>
      <view class="switch-row">
        <text>设为当前宠物</text>
        <switch :checked="form.is_current" color="#1c6b56" @change="form.is_current = Boolean($event.detail.value)" />
      </view>
      <button class="primary-button" @click="savePet">保存</button>
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
      typeOptions: [
        { label: '猫咪', value: 'cat' },
        { label: '狗狗', value: 'dog' }
      ],
      genderOptions: [
        { label: '未知', value: 'unknown' },
        { label: '男孩', value: 'male' },
        { label: '女孩', value: 'female' }
      ],
      sterilizedOptions: [
        { label: '绝育未知', value: 'unknown' },
        { label: '已绝育', value: 'yes' },
        { label: '未绝育', value: 'no' }
      ],
      statusOptions: [
        { label: '未知', value: 'unknown' },
        { label: '待完成', value: 'pending' },
        { label: '已完成', value: 'completed' },
        { label: '规律进行', value: 'regular' }
      ],
      form: {
        name: '',
        pet_type: 'cat',
        breed: '',
        gender: 'unknown',
        birthday: '',
        arrival_date: '',
        weight: '',
        avatar_url: '/static/logo.png',
        sterilized: 'unknown',
        vaccine_status: 'unknown',
        deworm_status: 'unknown',
        health_notes: '',
        visibility: 'private',
        is_current: false
      }
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
    if (savedBase) {
      this.apiBase = savedBase
    }
    this.token = uni.getStorageSync('petShopToken')
    this.petId = options.id || ''
    if (!this.token) {
      uni.switchTab({ url: '/pages/account/account' })
      return
    }
    if (this.petId) {
      this.loadPet()
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
    async loadPet() {
      try {
        const data = await this.request({ url: `/pets/${this.petId}` })
        this.form = Object.assign({}, this.form, data, {
          weight: data.weight || '',
          birthday: data.birthday || '',
          arrival_date: data.arrival_date || ''
        })
      } catch (error) {
        this.toast(error.message)
      }
    },
    async savePet() {
      if (!this.form.name) {
        this.toast('请输入宠物名')
        return
      }
      const payload = Object.assign({}, this.form, {
        weight: this.form.weight === '' ? null : Number(this.form.weight),
        birthday: this.form.birthday || null,
        arrival_date: this.form.arrival_date || null
      })
      try {
        await this.request({
          url: this.petId ? `/pets/${this.petId}` : '/pets',
          method: this.petId ? 'PUT' : 'POST',
          data: payload
        })
        this.toast('已保存')
        uni.navigateBack()
      } catch (error) {
        this.toast(error.message)
      }
    },
    onTypeChange(event) { this.form.pet_type = this.typeOptions[Number(event.detail.value)].value },
    onGenderChange(event) { this.form.gender = this.genderOptions[Number(event.detail.value)].value },
    onSterilizedChange(event) { this.form.sterilized = this.sterilizedOptions[Number(event.detail.value)].value },
    onVaccineChange(event) { this.form.vaccine_status = this.statusOptions[Number(event.detail.value)].value },
    onDewormChange(event) { this.form.deworm_status = this.statusOptions[Number(event.detail.value)].value },
    labelOf(options, value) {
      const item = options.find(option => option.value === value)
      return item ? item.label : '请选择'
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
.panel { padding: 28rpx; border-radius: 8rpx; background: #fff; }
.title { display: block; margin-bottom: 22rpx; font-size: 34rpx; font-weight: 700; }
.input, .picker, .textarea { box-sizing: border-box; width: 100%; margin-bottom: 16rpx; border: 1rpx solid #d9e0e8; border-radius: 8rpx; background: #fbfcfd; font-size: 25rpx; }
.input, .picker { height: 76rpx; padding: 0 20rpx; line-height: 76rpx; }
.textarea { min-height: 150rpx; padding: 18rpx 20rpx; line-height: 1.5; }
.switch-row { display: flex; align-items: center; justify-content: space-between; margin: 10rpx 0 22rpx; color: #526172; font-size: 25rpx; }
.primary-button { display: flex; align-items: center; justify-content: center; height: 78rpx; margin: 0; border-radius: 8rpx; color: #fff; background: #1c6b56; font-size: 26rpx; }
</style>
