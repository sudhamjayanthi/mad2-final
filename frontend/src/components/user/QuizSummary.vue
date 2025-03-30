<template>
	<div class="container py-4">
		<div class="card">
			<div class="card-header">
				<h4>Quiz Summary</h4>
			</div>
			<div class="card-body">
				<div class="summary-stats mb-4">
					<div class="row">
						<div class="col-md-3">
							<div class="stat-card p-3 border rounded">
								<h6>Total Score</h6>
								<h3>{{ summary.attempt_details.percentage }}%</h3>
							</div>
						</div>
						<div class="col-md-3">
							<div class="stat-card p-3 border rounded">
								<h6>Correct Answers</h6>
								<h3>
									{{ summary.attempt_details.total_scored }}/{{
										summary.attempt_details.total_possible
									}}
								</h3>
							</div>
						</div>
						<div class="col-md-3">
							<div class="stat-card p-3 border rounded">
								<h6>Attempt</h6>
								<h3>
									{{ summary.attempt_details.attempt_number }}/{{
										summary.quiz_details.max_attempts
									}}
								</h3>
							</div>
						</div>
						<div class="col-md-3">
							<div class="stat-card p-3 border rounded">
								<h6>Time Taken</h6>
								<h3>{{ formatTime(summary.time_taken) }}</h3>
							</div>
						</div>
					</div>
				</div>

				<div class="text-center mb-4">
					<button class="btn btn-primary me-2" @click="viewAnswers">
						Review Answers
					</button>
					<button
						v-if="
							summary.quiz_details.attempts_used < summary.quiz_details.max_attempts
						"
						class="btn btn-success me-2"
						@click="retakeQuiz"
					>
						Retake Quiz
					</button>
					<button class="btn btn-secondary" @click="backToQuizzes">
						Back to Quizzes
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import { api } from "@/utils/api";

export default {
	name: "QuizSummary",
	data() {
		return {
			summary: {
				score: 0,
				correct_answers: 0,
				total_questions: 0,
				time_taken: 0,
			},
		};
	},
	async created() {
		await this.loadSummary();
	},
	methods: {
		async loadSummary() {
			try {
				const quizId = this.$route.params.id;
				this.summary = await api.get(`/user/quiz/${quizId}/summary`);
			} catch (error) {
				console.error("Error loading quiz summary:", error);
			}
		},
		formatTime(seconds) {
			const minutes = Math.floor(seconds / 60);
			const remainingSeconds = seconds % 60;
			return `${minutes}m ${remainingSeconds}s`;
		},
		viewAnswers() {
			this.$router.push(`/user/quiz/${this.$route.params.id}/review`);
		},
		backToQuizzes() {
			this.$router.push("/user/quizzes");
		},
		retakeQuiz() {
			this.$router.push(`/user/quiz/${this.$route.params.id}/attempt`);
		},
	},
};
</script>

<style scoped>
.stat-card {
	background-color: #f8f9fa;
	text-align: center;
}
.stat-card h3 {
	color: #0d6efd;
	margin: 0;
}
</style>
