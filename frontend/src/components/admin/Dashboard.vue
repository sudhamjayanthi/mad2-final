<template>
	<div class="container-fluid">
		<nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
			<div class="container">
				<span class="navbar-brand">
					<i class="bi bi-shield-lock me-2"></i>
					Quiz Master Admin
				</span>
				<button class="btn btn-danger btn-sm" @click="handleLogout">
					<i class="bi bi-box-arrow-right me-1"></i>
					Logout
				</button>
			</div>
		</nav>

		<div class="container">
			<div class="row">
				<aside class="col-md-3">
					<div class="card">
						<div class="card-body">
							<h5 class="card-title mb-3">
								<i class="bi bi-list me-2"></i>
								Navigation
							</h5>
							<div class="list-group">
								<router-link
									v-for="route in routes"
									:key="route.path"
									:to="route.path"
									class="list-group-item list-group-item-action d-flex align-items-center"
									:class="{ active: currentRoute === route.path }"
								>
									<i :class="route.icon + ' me-2'"></i>
									{{ route.name }}
								</router-link>
							</div>
						</div>
					</div>
				</aside>

				<main class="col-md-9">
					<router-view></router-view>
				</main>
			</div>
		</div>
	</div>
</template>

<script>
export default {
	name: "AdminDashboard",
	data() {
		return {
			routes: [
				{
					path: "/admin/quizzes",
					name: "Quizzes",
					icon: "bi bi-question-circle",
				},
				{
					path: "/admin/subjects",
					name: "Subjects",
					icon: "bi bi-book",
				},
				{
					path: "/admin/chapters",
					name: "Chapters",
					icon: "bi bi-list-check",
				},
				{
					path: "/admin/users",
					name: "Users",
					icon: "bi bi-people",
				},
			],
		};
	},
	computed: {
		currentRoute() {
			return this.$route.path;
		},
	},
	methods: {
		handleLogout() {
			localStorage.removeItem("token");
			localStorage.removeItem("user");
			this.$router.push("/login");
		},
	},
};
</script>

<style scoped>
.navbar {
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.list-group-item {
	border-radius: 0.25rem !important;
	margin-bottom: 0.25rem;
	border: none;
	transition: all 0.2s ease;
}

.list-group-item.active {
	background-color: var(--bs-primary);
	border-color: var(--bs-primary);
}

.list-group-item:hover:not(.active) {
	background-color: #f8f9fa;
	transform: translateX(4px);
}
</style>
