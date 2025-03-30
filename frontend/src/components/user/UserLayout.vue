<template>
	<div class="container-fluid">
		<div class="row">
			<!-- Navigation Sidebar -->
			<nav class="col-md-3 col-lg-2 d-md-block bg-light sidebar">
				<div class="position-sticky pt-3">
					<h5 class="px-3 mb-3">Navigation</h5>
					<div class="nav flex-column">
						<router-link
							v-for="route in navRoutes"
							:key="route.path"
							:to="route.path"
							class="nav-link"
							:class="{ active: $route.path === route.path }"
						>
							<i :class="route.icon + ' me-2'"></i>
							{{ route.name }}
						</router-link>
					</div>
				</div>
			</nav>

			<!-- Main Content -->
			<main class="col-md-9 ms-sm-auto col-lg-10 px-md-4">
				<header
					class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom"
				>
					<h2>Student Dashboard</h2>
					<div class="d-flex align-items-center gap-2">
						<span class="text-muted">Welcome, {{ userName }}!</span>
						<button class="btn btn-danger btn-sm" @click="handleLogout">
							<i class="bi bi-box-arrow-right me-1"></i>
							Logout
						</button>
					</div>
				</header>

				<router-view></router-view>
			</main>
		</div>
	</div>
</template>

<script>
export default {
	name: "UserLayout",
	data() {
		return {
			navRoutes: [
				{
					path: "/user/subjects",
					name: "Subjects",
					icon: "bi bi-book",
				},
				{
					path: "/user/scores",
					name: "My Scores",
					icon: "bi bi-trophy",
				},
			],
		};
	},
	computed: {
		userName() {
			const user = JSON.parse(localStorage.getItem("user") || "{}");
			return user.full_name || "Student";
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
.sidebar {
	min-height: 100vh;
	box-shadow: inset -1px 0 0 rgba(0, 0, 0, 0.1);
}

.nav-link {
	color: #333;
	padding: 0.5rem 1rem;
	margin-bottom: 0.2rem;
	border-radius: 0.25rem;
	transition: background-color 0.2s ease;
}

.nav-link:hover {
	background-color: #e9ecef;
}

.nav-link.active {
	background-color: var(--bs-primary);
	color: white;
}

.nav-link.active i {
	color: white;
}
</style>
