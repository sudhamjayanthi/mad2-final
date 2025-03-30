<template>
	<div class="toast-container position-fixed bottom-0 end-0 p-3">
		<div class="toast" :class="toastClass" role="alert" ref="toast">
			<div class="toast-body d-flex align-items-center">
				<i :class="iconClass" class="me-2"></i>
				{{ message }}
			</div>
		</div>
	</div>
</template>

<script>
import { Toast } from "bootstrap";

export default {
	name: "Toast",
	props: {
		message: {
			type: String,
			required: true,
		},
		type: {
			type: String,
			default: "error",
			validator: (value) => ["error", "success", "warning", "info"].includes(value),
		},
		duration: {
			type: Number,
			default: 3000,
		},
	},
	computed: {
		toastClass() {
			const classes = {
				error: "bg-danger",
				success: "bg-success",
				warning: "bg-warning",
				info: "bg-info",
			};
			return `${classes[this.type]} text-white`;
		},
		iconClass() {
			const icons = {
				error: "bi bi-exclamation-circle",
				success: "bi bi-check-circle",
				warning: "bi bi-exclamation-triangle",
				info: "bi bi-info-circle",
			};
			return icons[this.type];
		},
	},
	mounted() {
		const toast = new Toast(this.$refs.toast, {
			delay: this.duration,
			autohide: true,
		});
		toast.show();

		this.$refs.toast.addEventListener("hidden.bs.toast", () => {
			this.$emit("hidden");
		});
	},
};
</script>
