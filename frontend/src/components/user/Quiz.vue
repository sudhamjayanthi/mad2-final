<template>
	<div class="card">
		<div class="card-body">
			<h5 class="card-title mb-4">{{ quizData.chapter_name }} Quiz</h5>

			<div v-if="!isStarted" class="text-center">
				<button @click="startQuiz" class="btn btn-primary">Start Quiz</button>
			</div>

			<div v-else>
				<div class="mb-4"><strong>Time Duration:</strong> {{ quizData.time_duration }}</div>

				<form @submit.prevent="submitQuiz">
					<div v-for="(question, index) in questions" :key="question.id" class="mb-4">
						<div class="card">
							<div class="card-body">
								<h6 class="card-subtitle mb-3">Question {{ index + 1 }}</h6>
								<p>{{ question.question }}</p>

								<div class="list-group">
									<label
										v-for="(option, idx) in question.options"
										:key="idx"
										class="list-group-item"
									>
										<input
											type="radio"
											:name="'question_' + question.id"
											:value="idx + 1"
											v-model="answers[question.id]"
											class="me-2"
										/>
										{{ option }}
									</label>
								</div>
							</div>
						</div>
					</div>

					<div class="d-grid">
						<button type="submit" class="btn btn-primary" :disabled="!isAllAnswered">
							Submit Quiz
						</button>
					</div>
				</form>
			</div>

			<!-- Results Modal -->
			<div v-if="showResults" class="modal fade show" style="display: block">
				<div class="modal-dialog">
					<div class="modal-content">
						<div class="modal-header">
							<h5 class="modal-title">Quiz Results</h5>
						</div>
						<div class="modal-body">
							<p>Score: {{ results.total_scored }} / {{ results.total_possible }}</p>
							<p>Percentage: {{ results.percentage }}%</p>
						</div>
						<div class="modal-footer">
							<button @click="goBack" class="btn btn-primary">
								Back to Subjects
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import { api } from "@/utils/api";

export default {
	name: "Quiz",
	data() {
		return {
			quizId: null,
			quizData: {},
			questions: [],
			answers: {},
			isStarted: false,
			showResults: false,
			results: null,
		};
	},
	computed: {
		isAllAnswered() {
			return this.questions.every((q) => this.answers[q.id] !== undefined);
		},
	},
	created() {
		this.quizId = this.$route.params.id;
	},
	methods: {
		async startQuiz() {
			try {
				const response = await api.post(`/user/quizzes/${this.quizId}/start`);
				this.quizData = response;
				this.questions = response.questions;
				this.isStarted = true;
			} catch (error) {
				console.error("Error starting quiz:", error);
			}
		},
		async submitQuiz() {
			try {
				const response = await api.post(`/user/quizzes/${this.quizId}/submit`, {
					answers: this.answers,
				});
				this.results = response;
				this.showResults = true;
			} catch (error) {
				console.error("Error submitting quiz:", error);
			}
		},
		goBack() {
			this.$router.push("/user/subjects");
		},
	},
};
</script>

<style scoped>
.modal {
	background-color: rgba(0, 0, 0, 0.5);
}
</style>
