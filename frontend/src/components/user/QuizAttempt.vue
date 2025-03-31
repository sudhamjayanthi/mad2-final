<template>
	<div class="container py-4">
		<!-- Quiz Header (always visible) -->
		<div class="d-flex justify-content-between align-items-center mb-4">
			<h3>{{ quiz?.quiz_id ? `Quiz QDS2025${quiz.quiz_id}` : "Loading..." }}</h3>
			<div class="d-flex gap-3 align-items-center" v-if="!quizResult">
				<!-- Show Timer when quiz is active -->
				<span v-if="timeRemaining !== null" class="badge bg-warning text-dark fs-6">
					<i class="bi bi-stopwatch me-1"></i>
					Time Left: {{ formattedTime }}
				</span>
				<span v-else class="text-muted">
					<i class="bi bi-clock me-1"></i>
					Duration: {{ quiz?.time_duration }}
				</span>
			</div>
			<div v-else>
				<span class="badge bg-success fs-6">Completed</span>
			</div>
		</div>

		<!-- Display Quiz or Results -->
		<div v-if="!quizResult">
			<!-- Question Navigation -->
			<div class="mb-4">
				<div class="d-flex flex-wrap gap-2">
					<button
						v-for="(_, index) in quiz?.questions || []"
						:key="index"
						class="btn"
						:class="[
							currentQuestion === index ? 'btn-primary' : 'btn-outline-secondary',
							answers[quiz.questions[index].id] ? 'border-success' : '',
						]"
						@click="currentQuestion = index"
					>
						{{ index + 1 }}
					</button>
				</div>
			</div>

			<!-- Question Display -->
			<div class="card" v-if="quiz?.questions?.length">
				<div class="card-body">
					<h5 class="card-title">Question {{ currentQuestion + 1 }}</h5>
					<p class="card-text">{{ currentQuestionData.question }}</p>

					<div class="list-group mt-3">
						<button
							v-for="(option, index) in currentQuestionData.options"
							:key="index"
							class="list-group-item list-group-item-action"
							:class="{ active: answers[currentQuestionData.id] === index + 1 }"
							@click="selectAnswer(currentQuestionData.id, index + 1)"
						>
							{{ option }}
						</button>
					</div>
				</div>
			</div>

			<!-- Navigation Buttons -->
			<div class="d-flex justify-content-between mt-4">
				<button
					class="btn btn-outline-primary"
					@click="previousQuestion"
					:disabled="currentQuestion === 0"
				>
					<i class="bi bi-arrow-left me-1"></i>
					Previous
				</button>

				<button
					v-if="currentQuestion < quiz?.questions?.length - 1"
					class="btn btn-outline-primary"
					@click="nextQuestion"
				>
					Next
					<i class="bi bi-arrow-right ms-1"></i>
				</button>

				<button
					v-else
					class="btn btn-success"
					@click="submitQuiz"
					:disabled="!isAllAnswered"
				>
					Submit Quiz
				</button>
			</div>
		</div>

		<!-- Quiz Results Section -->
		<div v-else class="card text-center">
			<div class="card-body">
				<h4 class="card-title">Quiz Submitted!</h4>
				<p class="card-text fs-5">
					You scored
					<strong class="text-primary">
						{{ quizResult.total_scored }} out of {{ quizResult.total_possible }}
					</strong>
					({{ quizResult.percentage.toFixed(2) }}%).
				</p>
			</div>
		</div>

		<Toast v-if="error" :message="error" type="error" @hidden="error = null" />
	</div>
</template>

<script>
import { api } from "@/utils/api";
import Toast from "@/components/common/Toast.vue";

export default {
	name: "QuizAttempt",
	components: { Toast },
	data() {
		return {
			quiz: null,
			currentQuestion: 0,
			answers: {},
			error: null,
			quizResult: null,
			timeRemaining: null, // Time remaining in seconds
			timerInterval: null, // To store setInterval ID
		};
	},
	computed: {
		currentQuestionData() {
			return this.quiz?.questions[this.currentQuestion] || {};
		},
		isAllAnswered() {
			return this.quiz?.questions?.every((q) => this.answers[q.id]) || false;
		},
		// Format remaining time as MM:SS
		formattedTime() {
			if (this.timeRemaining === null || this.timeRemaining < 0) return "00:00";
			const minutes = Math.floor(this.timeRemaining / 60);
			const seconds = this.timeRemaining % 60;
			return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
		},
	},
	async created() {
		const quizId = this.$route.params.id;
		try {
			const response = await api.post(`/user/quizzes/${quizId}/start`);
			this.quiz = response;
			// Start timer only if quiz is loaded and has duration
			if (this.quiz && this.quiz.time_duration) {
				this.timeRemaining = this.parseDuration(this.quiz.time_duration);
				this.startTimer();
			}
		} catch (error) {
			this.error = error.response?.data?.error || "Failed to load quiz";
			setTimeout(() => {
				this.$router.push("/user/quizzes");
			}, 3000);
		}
	},
	// Clear timer when component is destroyed
	beforeDestroy() {
		clearInterval(this.timerInterval);
	},
	methods: {
		// Parse "HH:MM" duration string into seconds
		parseDuration(durationString) {
			const parts = durationString.split(":");
			if (parts.length !== 2) return 0;
			const hours = parseInt(parts[0], 10);
			const minutes = parseInt(parts[1], 10);
			if (isNaN(hours) || isNaN(minutes)) return 0;
			return hours * 3600 + minutes * 60;
		},
		// Start the countdown timer
		startTimer() {
			clearInterval(this.timerInterval); // Clear any existing timer
			this.timerInterval = setInterval(() => {
				if (this.timeRemaining > 0) {
					this.timeRemaining--;
				} else {
					clearInterval(this.timerInterval);
					this.timeRemaining = 0; // Ensure it shows 00:00
					// Only auto-submit if results are not already showing
					if (!this.quizResult) {
						console.log("Time is up! Submitting quiz...");
						this.submitQuiz();
					}
				}
			}, 1000); // Update every second
		},
		selectAnswer(questionId, optionNumber) {
			// Only allow answers if the quiz is active (not submitted/timed out)
			if (!this.quizResult && this.timeRemaining > 0) {
				this.answers[questionId] = optionNumber;
			}
		},
		nextQuestion() {
			if (this.currentQuestion < this.quiz.questions.length - 1) {
				this.currentQuestion++;
			}
		},
		previousQuestion() {
			if (this.currentQuestion > 0) {
				this.currentQuestion--;
			}
		},
		async submitQuiz() {
			// Stop the timer when submitting
			clearInterval(this.timerInterval);
			// Prevent multiple submissions
			if (this.quizResult) return;

			try {
				// Send timestamp in standard ISO format (UTC)
				const response = await api.post(`/user/quizzes/${this.quiz.quiz_id}/submit`, {
					answers: this.answers,
					time_stamp_of_attempt: new Date().toISOString(), // Use standard ISO string (UTC)
				});
				this.quizResult = response;
				this.error = null;
			} catch (error) {
				this.error = error.response?.data?.error || "Failed to submit quiz";
				// Optionally restart timer if submission fails? Or leave it stopped?
				// For now, leave it stopped. User can retry submission manually.
			}
		},
		goToSummary() {
			this.$router.push(`/user/quiz/${this.quiz.quiz_id}/summary`);
		},
	},
};
</script>

<style scoped>
.list-group-item {
	cursor: pointer;
}
.list-group-item:hover:not(.active) {
	background-color: #f8f9fa;
}
</style>
