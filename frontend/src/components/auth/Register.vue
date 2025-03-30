<template>
	<div class="container mt-5">
		<div class="row justify-content-center">
			<div class="col-md-6">
				<div class="card">
					<div class="card-header">
						<h3 class="text-center">Register</h3>
					</div>
					<div class="card-body">
						<form @submit.prevent="handleRegister">
							<div class="mb-3">
								<label for="email" class="form-label">Email</label>
								<input
									type="email"
									class="form-control"
									id="email"
									v-model="formData.email"
									required
								/>
							</div>
							<div class="mb-3">
								<label for="password" class="form-label">Password</label>
								<input
									type="password"
									class="form-control"
									id="password"
									v-model="formData.password"
									required
								/>
							</div>
							<div class="mb-3">
								<label for="fullName" class="form-label">Full Name</label>
								<input
									type="text"
									class="form-control"
									id="fullName"
									v-model="formData.full_name"
									required
								/>
							</div>
							<div class="mb-3">
								<label for="qualification" class="form-label">Qualification</label>
								<input
									type="text"
									class="form-control"
									id="qualification"
									v-model="formData.qualification"
									required
								/>
							</div>
							<div class="mb-3">
								<label for="dob" class="form-label">Date of Birth</label>
								<input
									type="date"
									class="form-control"
									id="dob"
									v-model="formData.dob"
									required
								/>
							</div>
							<div class="alert alert-danger" v-if="error">{{ error }}</div>
							<div class="d-grid">
								<button type="submit" class="btn btn-primary" :disabled="loading">
									{{ loading ? "Loading..." : "Register" }}
								</button>
							</div>
						</form>
						<div class="text-center mt-3">
							<p>
								Already have an account?
								<router-link to="/login">Login here</router-link>
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
	name: "Register",
	components: {
		Toast,
	},
	data() {
		return {
			formData: {
				email: "",
				password: "",
				full_name: "",
				qualification: "",
				dob: "",
			},
			loading: false,
			error: null,
		};
	},
	methods: {
		async handleRegister() {
			this.loading = true;
			this.error = null;

			try {
				const response = await fetch("http://localhost:6900/api/auth/register", {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify(this.formData),
				});

				const data = await response.json();

				if (!response.ok) {
					throw new Error(data.error || data.message || "Registration failed");
				}

				// Redirect to login page after successful registration
				this.$router.push("/login");
			} catch (error) {
				console.error("Error during registration:", error);
				this.error = error.message || "Registration failed";
			} finally {
				this.loading = false;
			}
		},
	},
};
</script>
