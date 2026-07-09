<script>
export default {
  onLaunch() {
    console.log('Pet Shop App Launch')
  },
  onShow() {
    console.log('Pet Shop App Show')
  },
  onHide() {
    console.log('Pet Shop App Hide')
  }
}
</script>

<style>
page {
  box-sizing: border-box;
  background: #f3f5f8;
  color: #18202c;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

view,
text,
input,
textarea,
button {
  box-sizing: border-box;
}

button::after {
  border: none;
}

/* Browser-style sizing overrides for H5/B/S pages. */
.page {
  width: 100% !important;
  max-width: 1280px !important;
  min-height: 100vh !important;
  margin: 0 auto !important;
  padding: 20px !important;
}

.topbar,
.toolbar {
  min-height: 64px !important;
  margin-bottom: 18px !important;
}

.title,
.brand {
  font-size: 24px !important;
  line-height: 1.25 !important;
}

.subtitle,
.sub,
.muted,
.panel-note {
  font-size: 14px !important;
  line-height: 1.55 !important;
}

.layout {
  gap: 20px !important;
  padding: 0 !important;
}

.sidebar {
  width: 190px !important;
  padding: 18px !important;
}

.main {
  min-width: 0 !important;
}

.hero,
.panel,
.metric,
.card {
  border-radius: 8px !important;
}

.hero,
.panel {
  padding: 22px !important;
}

.metric-grid,
.pet-grid,
.action-grid,
.form-grid,
.grid {
  gap: 16px !important;
}

.metric-grid {
  grid-template-columns: repeat(3, minmax(220px, 1fr)) !important;
}

.pet-grid {
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)) !important;
}

.action-grid {
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)) !important;
}

.form-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)) !important;
}

.detail {
  grid-template-columns: 360px minmax(0, 1fr) !important;
  gap: 24px !important;
}

.cover {
  max-height: 360px !important;
}

.detail > .cover {
  width: 100% !important;
  height: 360px !important;
}

.avatar {
  width: 56px !important;
  height: 56px !important;
}

.input,
.picker,
.field-input,
.picker-input {
  height: 40px !important;
  padding: 0 12px !important;
  border-radius: 6px !important;
  font-size: 14px !important;
  line-height: 40px !important;
}

.textarea {
  min-height: 96px !important;
  padding: 12px !important;
  border-radius: 6px !important;
  font-size: 14px !important;
}

.primary,
.secondary,
.ghost,
.danger,
.nav,
.chip,
.role,
.step {
  min-height: 36px !important;
  height: 36px !important;
  padding: 0 14px !important;
  border-radius: 6px !important;
  font-size: 14px !important;
  line-height: 36px !important;
}

.wide {
  height: 42px !important;
}

.table {
  overflow-x: auto !important;
}

.row {
  min-height: 64px !important;
  padding: 12px 16px !important;
  gap: 12px !important;
  font-size: 14px !important;
}

.head {
  min-height: 44px !important;
}

.product-cell,
.pet-cell {
  gap: 12px !important;
}

.product-cell .cover,
.row .cover {
  width: 56px !important;
  height: 56px !important;
}

.name,
.profile-name,
.user-name,
.order-no,
.panel-title {
  font-size: 16px !important;
  line-height: 1.4 !important;
}

.price {
  font-size: 18px !important;
}

@media screen and (min-width: 1100px) {
  .page {
    padding: 20px 24px !important;
  }
}

@media screen and (max-width: 820px) {
  .page {
    padding: 16px !important;
  }

  .layout,
  .topbar,
  .toolbar,
  .detail {
    flex-direction: column !important;
    grid-template-columns: 1fr !important;
  }

  .sidebar {
    width: 100% !important;
  }

  .detail > .cover {
    height: 260px !important;
  }
}
</style>
