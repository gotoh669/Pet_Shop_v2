<script>
	export default {
		onLaunch: function() {
			console.log('App Launch')
		},
		onShow: function() {
			console.log('App Show')
		},
		onHide: function() {
			console.log('App Hide')
		}
	}
</script>

<style>
	/*每个页面公共css */
	page {
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
	}

	button::after {
		border: none;
	}
</style>
