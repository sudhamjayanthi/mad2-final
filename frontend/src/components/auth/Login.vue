<template>
	<div class="container mt-5">
		<div class="row justify-content-center">
			<div class="col-md-6">
				<div class="card">
					<div class="card-header">
						<h3 class="text-center">Login</h3>
					</div>
					<div class="card-body">
						<form @submit.prevent="handleLogin">
							<div class="mb-3">
								<label for="email" class="form-label">Email</label>
								<input
									type="email"
									class="form-control"
									id="email"
									v-model="email"
									required
								/>
							</div>
							<div class="mb-3">
								<label for="password" class="form-label">Password</label>
								<input
									type="password"
									class="form-control"
									id="password"
									v-model="password"
									required
								/>
							</div>
							<div class="alert alert-danger" v-if="error">{{ error }}</div>
							<div class="d-grid">
								<button type="submit" class="btn btn-primary" :disabled="loading">
									{{ loading ? "Loading..." : "Login" }}
								</button>
							</div>
						</form>
						<div class="text-center mt-3">
							<p>
								Don't have an account?
								<router-link to="/register">Register here</router-link>
							</p>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import Toast from "@/components/common/Toast.vue";

export default {
	name: "Login",
	components: {
		Toast,
	},
	data() {
		return {
			email: "",
			password: "",
			loading: false,
			error: null,
		};
	},
	methods: {
		async handleLogin() {
			this.loading = true;
			this.error = null;

			try {
				const response = await fetch("http://localhost:6900/api/auth/login", {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({
						email: this.email,
						password: this.password,
					}),
				});

				const data = await response.json();

				if (!response.ok) {
					throw new Error(data.error || data.message || "Login failed");
				}

				localStorage.setItem("token", `${data.token}`);
				localStorage.setItem("user", JSON.stringify(data.user));

				// Redirect based on role
				if (data.user.roles.includes("admin")) {
					this.$router.push("/admin/");
				} else {
					this.$router.push("/user/");
				}
			} catch (error) {
				console.error("Error during login:", error);
				this.error = error.message || "An error occurred during login";
			} finally {
				this.loading = false;
			}
		},
	},
};
</script>
