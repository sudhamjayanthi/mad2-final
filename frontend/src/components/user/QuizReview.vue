<template>
	<div class="container py-4">
		<div class="card">
			<div class="card-header d-flex justify-content-between align-items-center">
				<h4>Quiz Review</h4>
				<div class="badge bg-primary">Score: {{ quizReview.score }}%</div>
			</div>
			<div class="card-body">
				<div
					class="mb-4"
					v-for="(question, index) in quizReview.questions"
					:key="question.id"
				>
					<div class="question-header d-flex justify-content-between align-items-center">
						<h5>Question {{ index + 1 }}</h5>
						<div
							class="badge"
							:class="question.is_correct ? 'bg-success' : 'bg-danger'"
						>
							{{ question.is_correct ? "Correct" : "Incorrect" }}
						</div>
					</div>

					<p class="question-text">{{ question.question }}</p>

					<div class="options-list">
						<div
							v-for="(option, optIndex) in question.options"
							:key="optIndex"
							class="mb-2"
						>
							<div class="p-3 rounded" :class="getOptionClass(question, optIndex)">
								{{ option }}
								<span v-if="optIndex === question.correct_answer" class="ms-2">
									<i class="bi bi-check-circle-fill text-success"></i>
								</span>
								<span
									v-if="
										optIndex === question.user_answer &&
										optIndex !== question.correct_answer
									"
									class="ms-2"
								>
									<i class="bi bi-x-circle-fill text-danger"></i>
								</span>
							</div>
						</div>
					</div>

					<div class="mt-2 explanation" v-if="question.explanation">
						<div class="p-3 bg-light rounded">
							<strong>Explanation:</strong> {{ question.explanation }}
						</div>
					</div>

					<hr class="my-4" />
				</div>

				<div class="text-center">
					<button class="btn btn-primary" @click="backToSummary">Back to Summary</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import { api } from "@/utils/api";

export default {
	name: "QuizReview",
	data() {
		return {
			quizReview: {
				id: null,
				score: 0,
				questions: [],
			},
		};
	},
	async created() {
		await this.loadQuizReview();
	},
	methods: {
		async loadQuizReview() {
			try {
				const quizId = this.$route.params.id;
				const response = await api.get(`/user/quiz/${quizId}/review`);
				this.quizReview = response;
			} catch (error) {
				console.error("Error loading quiz review:", error);
			}
		},
		getOptionClass(question, optionIndex) {
			if (optionIndex === question.correct_answer) {
				return "bg-success bg-opacity-25";
			} else if (
				optionIndex === question.user_answer &&
				optionIndex !== question.correct_answer
			) {
				return "bg-danger bg-opacity-25";
			}
			return "bg-light";
		},
		backToSummary() {
			this.$router.push(`/user/quiz/${this.$route.params.id}/summary`);
		},
	},
};
</script>

<style scoped>
.question-text {
	font-size: 1.1rem;
	margin-bottom: 1.5rem;
}
.options-list .bg-light:hover {
	background-color: #f0f0f0 !important;
}
.explanation {
	font-size: 0.95rem;
}
</style>
