<template>
	<div class="dashboard-layout">
		<aside class="sidebar">
			<div class="sidebar-header">
				<i class="bi bi-shield-lock me-2"></i>
				Quiz Master 
			</div>
			<div class="navigation">
				<h5 class="navigation-title">
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
		</aside>

		<div class="main-content">
			<nav class="navbar navbar-expand-lg navbar-light bg-white header">
				<div class="container-fluid justify-content-end">
					<!-- You can add user info here if needed -->
						<span class="navbar-text me-3">Welcome, Admin!</span>
					<button class="btn btn-danger btn-sm" @click="handleLogout">
						<i class="bi bi-box-arrow-right me-1"></i>
						Logout
					</button>
				</div>
			</nav>

			<main class="content-area">
				<router-view></router-view>
			</main>
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
.dashboard-layout {
	display: flex;
	min-height: 100vh;
}

.sidebar {
	width: 250px; /* Adjust width as needed */
	flex-shrink: 0;
	background-color: #f8f9fa; /* Light background for sidebar */
	padding: 1.5rem 1rem;
	display: flex;
	flex-direction: column;
	border-right: 1px solid #dee2e6;
}

.sidebar-header {
	font-size: 1.2rem;
	font-weight: 600;
	margin-bottom: 2rem;
	color: #343a40;
}

.navigation-title {
	font-size: 0.9rem;
	color: #6c757d;
	text-transform: uppercase;
	margin-bottom: 0.75rem;
	padding-left: 0.5rem; /* Align with list items */
}

.list-group-item {
	border-radius: 0.375rem !important; /* Slightly rounded corners */
	margin-bottom: 0.25rem;
	border: none;
	transition: all 0.2s ease;
	padding: 0.75rem 1rem;
	font-size: 0.95rem;
}

.list-group-item.active {
	background-color: var(--bs-primary); /* Blue active background */
	border-color: var(--bs-primary);
	color: white;
}

.list-group-item:hover:not(.active) {
	background-color: #e9ecef; /* Lighter hover background */
}

.main-content {
	flex-grow: 1;
	display: flex;
	flex-direction: column;
	background-color: #ffffff; /* White background for content */
}

.header {
	border-bottom: 1px solid #dee2e6; /* Separator line */
	box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
	padding-top: 0.75rem;
	padding-bottom: 0.75rem;
}

.content-area {
	flex-grow: 1;
	padding: 1.5rem; /* Padding around the router-view content */
	overflow-y: auto; /* Allow scrolling if content exceeds height */
}
</style>
