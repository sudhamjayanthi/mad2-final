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
								<th>Score</th>
								<th>Percentage</th>
								<th>Date</th>
							</tr>
						</thead>
						<tbody>
							<tr v-for="score in scores" :key="score.quiz_id">
								<td>{{ score.quiz_id }}</td>
								<td>{{ score.total_scored }} / {{ score.total_possible }}</td>
								<td>{{ score.percentage }}%</td>
								<td>{{ formatDate(score.attempted_at) }}</td>
							</tr>
						</tbody>
					</table>
				</div>

				<div v-if="scores.length === 0" class="text-center py-4">
					<p class="mb-0">You haven't attempted any quizzes yet.</p>
					<router-link to="/user/subjects" class="btn btn-primary mt-3">
						Take a Quiz
					</router-link>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import { api } from "@/utils/api";

export default {
	name: "Scores",
	data() {
		return {
			scores: [],
		};
	},
	async created() {
		await this.fetchScores();
	},
	methods: {
		async fetchScores() {
			try {
				const response = await api.get("/user/scores");
				this.scores = response;
			} catch (error) {
				console.error("Error fetching scores:", error);
			}
		},
		formatDate(isoString) {
			return new Date(isoString).toLocaleString();
		},
	},
};
</script>
