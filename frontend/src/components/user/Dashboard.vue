<template>
	<div class="container-fluid">
		<div class="row">
			<!-- Navigation Sidebar -->
			<div class="col-md-3 col-lg-2 d-md-block bg-light sidebar">
				<div class="position-sticky pt-3">
					<h5 class="px-3 mb-3">Navigation</h5>
					<div class="nav flex-column">
						<router-link
							to="/user/dashboard"
							class="nav-link"
							:class="{ active: $route.path === '/user/dashboard' }"
						>
							<i class="bi bi-house-door me-2"></i>
							Dashboard
						</router-link>
						<router-link
							to="/user/subjects"
							class="nav-link"
							:class="{ active: $route.path === '/user/subjects' }"
						>
							<i class="bi bi-book me-2"></i>
							Subjects
						</router-link>
						<router-link
							to="/user/scores"
							class="nav-link"
							:class="{ active: $route.path === '/user/scores' }"
						>
							<i class="bi bi-trophy me-2"></i>
							My Scores
						</router-link>
					</div>
				</div>
			</div>

			<!-- Main Content -->
			<main class="col-md-9 ms-sm-auto col-lg-10 px-md-4">
				<div
					class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom"
				>
					<h2>Quiz Master</h2>
					<div class="btn-toolbar mb-2 mb-md-0">
						<div class="d-flex gap-2">
							<span class="text-muted me-2">Welcome, {{ userName }}!</span>
							<button class="btn btn-danger" @click="handleLogout">Logout</button>
						</div>
					</div>
				</div>

				<!-- Router View for nested routes -->
				<router-view v-if="$route.path !== '/user/dashboard'"></router-view>

				<!-- Dashboard Content -->
				<div v-if="$route.path === '/user/dashboard'" class="dashboard-content">
					<div class="row">
						<div class="col-md-12">
							<div class="card">
								<div class="card-body">
									<h5 class="card-title">Quick Stats</h5>
									<div class="row mt-3">
										<div class="col-md-4">
											<div class="border rounded p-3 text-center">
												<h3>{{ totalAttempts }}</h3>
												<p class="text-muted mb-0">Total Attempts</p>
											</div>
										</div>
										<div class="col-md-4">
											<div class="border rounded p-3 text-center">
												<h3>{{ averageScore }}%</h3>
												<p class="text-muted mb-0">Average Score</p>
											</div>
										</div>
										<div class="col-md-4">
											<div class="border rounded p-3 text-center">
												<h3>{{ upcomingQuizzes }}</h3>
												<p class="text-muted mb-0">Available Quizzes</p>
											</div>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>

					<!-- Recent Activity -->
					<div class="row mt-4">
						<div class="col-md-12">
							<div class="card">
								<div class="card-body">
									<h5 class="card-title">Recent Activity</h5>
									<div class="table-responsive">
										<table class="table">
											<thead>
												<tr>
													<th>Quiz</th>
													<th>Score</th>
													<th>Date</th>
												</tr>
											</thead>
											<tbody>
												<tr
													v-for="score in recentScores"
													:key="score.quiz_id"
												>
													<td>{{ score.quiz_id }}</td>
													<td>{{ score.percentage }}%</td>
													<td>{{ formatDate(score.attempted_at) }}</td>
												</tr>
											</tbody>
										</table>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</main>
		</div>
	</div>
</template>

<script>
import { api } from "@/utils/api";

export default {
	name: "UserDashboard",
	data() {
		return {
			totalAttempts: 0,
			averageScore: 0,
			upcomingQuizzes: 0,
			recentScores: [],
		};
	},
	computed: {
		userName() {
			const user = JSON.parse(localStorage.getItem("user") || "{}");
			return user.full_name || "Student";
		},
	},
	async created() {
		await this.fetchDashboardData();
	},
	methods: {
		handleLogout() {
			localStorage.removeItem("token");
			localStorage.removeItem("user");
			this.$router.push("/login");
		},
		async fetchDashboardData() {
			try {
				// Fetch dashboard statistics
				const stats = await api.get("/dashboard/");
				this.totalAttempts = stats.total_attempts;
				this.averageScore = stats.average_score;
				this.upcomingQuizzes = stats.available_quizzes;

				// Fetch recent scores
				const scores = await api.get("/user/scores");
				this.recentScores = scores.slice(0, 5); // Show only last 5 attempts
			} catch (error) {
				console.error("Error fetching dashboard data:", error);
			}
		},
		formatDate(isoString) {
			return new Date(isoString).toLocaleString();
		},
	},
};
</script>

<style scoped>
.sidebar {
	min-height: 100vh;
	box-shadow: inset -1px 0 0 rgba(0, 0, 0, 0.1);
}

.sidebar .nav-link {
	color: #333;
	padding: 0.5rem 1rem;
	margin-bottom: 0.2rem;
	border-radius: 0.25rem;
}

.sidebar .nav-link:hover {
	background-color: #e9ecef;
}

.sidebar .nav-link.active {
	color: #fff;
	background-color: #0d6efd;
}

.dashboard-content {
	margin-top: 1rem;
}

.card {
	margin-bottom: 1rem;
}
</style>
