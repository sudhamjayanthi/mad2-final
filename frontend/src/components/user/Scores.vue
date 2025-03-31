<template>
	<div class="container mt-4">
		<div class="card">
			<div class="card-header">
				<h3 class="mb-0">Your Quiz History</h3>
			</div>
			<div class="card-body">
				<div class="table-responsive">
					<table class="table table-hover">
						<thead>
							<tr>
								<th>Quiz ID</th>
								<th>No of Questions</th>
								<th>Date</th>

								<th>Score (%)</th>
							</tr>
						</thead>
						<tbody>
							<tr v-for="score in scores" :key="score.quiz_id">
								<td>QDS2025{{ score.quiz_id }}</td>
								<td>{{ score.total_questions }}</td>
								<td>{{ formatDate(score.attempted_at) }}</td>
								<td>{{ score.percentage }}%</td>
							</tr>
						</tbody>
					</table>
				</div>

				<div v-if="scores.length === 0" class="text-center py-4">
					<p class="mb-0">You haven't attempted any quizzes yet.</p>
					<router-link to="/user/quizzes" class="btn btn-primary mt-3">
						Take a Quiz
					</router-link>
				</div>
			</div>
		</div>
		<Toast v-if="error" :message="error" type="error" @hidden="error = null" />
	</div>
</template>

<script>
import { api } from "@/utils/api";
import Toast from "@/components/common/Toast.vue";

export default {
	name: "Scores",
	components: {
		Toast,
	},
	data() {
		return {
			scores: [],
			error: null,
		};
	},
	async created() {
		await this.fetchScores();
	},
	methods: {
		async fetchScores() {
			try {
				const response = await api.get("/user/scores");
				console.log("Raw scores data received:", response); // Keep this for debugging if needed
				this.scores = response;
			} catch (error) {
				this.error = error.response?.data?.error || "Failed to load scores";
			}
		},
		formatDate(isoString) {
			if (!isoString) return "N/A";

			try {
				const date = new Date(isoString);
				if (isNaN(date.getTime())) {
					console.error("Invalid date string received:", isoString);
					return "Invalid Date";
				}

				const options = {
					year: "numeric",
					month: "short",
					day: "numeric",
					hour: "numeric",
					minute: "2-digit",
				};
				return new Intl.DateTimeFormat(undefined, options).format(date);
			} catch (e) {
				console.error("Error formatting date:", e, "Input string:", isoString);
				return "Error Formatting Date";
			}
		},
	},
};
</script>
