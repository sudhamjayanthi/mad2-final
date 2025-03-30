<template>
	<div class="container py-4">
		<div class="card">
			<div class="card-header d-flex justify-content-between align-items-center">
				<h4>Quiz #{{ quiz.id }}</h4>
				<div class="timer" :class="{ 'text-danger': timeRemaining < 300 }">
					Time Remaining: {{ formatTime(timeRemaining) }}
				</div>
			</div>
			<div class="card-body">
				<div v-if="currentQuestion" class="mb-4">
					<h5>Question {{ currentQuestionIndex + 1 }} of {{ quiz.questions.length }}</h5>
					<p class="question-text">{{ currentQuestion.question }}</p>

					<div class="options-list">
						<div
							v-for="(option, index) in currentQuestion.options"
							:key="index"
							class="mb-2"
						>
							<button
								class="btn w-100 text-start p-3"
								:class="getOptionClass(index)"
								@click="selectOption(index)"
								:disabled="submitted"
							>
								{{ option }}
							</button>
						</div>
					</div>

					<div v-if="feedbackVisible" class="mt-3 p-3 rounded" :class="feedbackClass">
						<i :class="feedbackIcon" class="me-2"></i>
						{{ feedbackMessage }}
					</div>
				</div>

				<div class="d-flex justify-content-between mt-4">
					<button
						class="btn btn-secondary"
						@click="previousQuestion"
						:disabled="currentQuestionIndex === 0"
					>
						Previous
					</button>
					<button
						class="btn btn-primary"
						@click="nextQuestion"
						:disabled="
							!hasAnsweredCurrent && currentQuestionIndex < quiz.questions.length - 1
						"
					>
						{{ isLastQuestion ? "Submit Quiz" : "Next Question" }}
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import { api } from "@/utils/api";

export default {
	name: "QuizAttempt",
	data() {
		return {
			quiz: {
				id: null,
				time_duration: 0,
				questions: [],
			},
			currentQuestionIndex: 0,
			timeRemaining: 0,
			timer: null,
			answers: {},
			submitted: false,
			feedbackVisible: false,
			feedbackMessage: "",
			feedbackClass: "",
			feedbackIcon: "",
			loading: true,
			error: "",
		};
	},
	computed: {
		currentQuestion() {
			return this.quiz.questions[this.currentQuestionIndex];
		},
		isLastQuestion() {
			return this.currentQuestionIndex === this.quiz.questions.length - 1;
		},
		hasAnsweredCurrent() {
			return this.currentQuestion && this.answers[this.currentQuestion.id] !== undefined;
		},
		hasQuestions() {
			return this.quiz.questions.length > 0;
		},
	},
	async created() {
		try {
			const quizId = this.$route.params.id;

			// Get quiz details including status
			const quizDetails = await api.get(`/user/quizzes/${quizId}`);

			// Handle quiz based on status
			if (quizDetails.status === "expired") {
				// If quiz is expired, show summary if available or redirect to quizzes
				if (quizDetails.has_attempt) {
					this.$router.push(`/user/quiz/${quizId}/summary`);
				} else {
					this.$router.push("/user/quizzes");
					// Optionally show a message that quiz is expired
				}
				return;
			}

			if (quizDetails.status === "completed") {
				// If already completed and user wants to see results
				this.$router.push(`/user/quiz/${quizId}/summary`);
				return;
			}

			// For 'open' or 'in_progress', start/continue the quiz
			await this.startQuiz(quizId);
		} catch (error) {
			console.error("Error starting quiz:", error);
			this.$router.push("/user/quizzes");
		} finally {
			this.loading = false;
		}
	},
	beforeUnmount() {
		this.clearTimer();
	},
	methods: {
		async startQuiz(quizId) {
			try {
				// Start the quiz and get questions
				const response = await api.post(`/user/quizzes/${quizId}/start`);

				this.quiz = {
					id: quizId,
					time_duration: response.time_duration || 30, // Default to 30 min if not provided
					questions: response.questions || [],
				};

				// If this is a continued attempt, load existing answers
				if (response.answers) {
					this.answers = response.answers;
				}

				// Only start timer if there are questions
				if (this.hasQuestions) {
					// Set time - either remaining time for in-progress or full duration for new attempts
					this.timeRemaining = response.remaining_time || this.quiz.time_duration * 60;
					this.startTimer();
				}
			} catch (error) {
				console.error("Error starting quiz:", error);
				this.error = "Failed to start quiz";
				throw error;
			}
		},
		startTimer() {
			this.timer = setInterval(() => {
				if (this.timeRemaining > 0) {
					this.timeRemaining--;
				} else {
					this.submitQuiz();
				}
			}, 1000);
		},
		clearTimer() {
			if (this.timer) {
				clearInterval(this.timer);
			}
		},
		formatTime(seconds) {
			const minutes = Math.floor(seconds / 60);
			const remainingSeconds = seconds % 60;
			return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
		},
		selectOption(optionIndex) {
			if (this.submitted) return;

			// Store the answer
			this.answers[this.currentQuestion.id] = optionIndex;

			// Show feedback
			this.showFeedback(optionIndex);
		},
		showFeedback(selectedIndex) {
			// Simple feedback based on UI only since we don't have API for correctness
			this.feedbackVisible = true;
			this.feedbackMessage = "Answer selected";
			this.feedbackClass = "bg-primary text-white";
			this.feedbackIcon = "bi bi-check-circle";

			// Hide feedback after 1 second
			setTimeout(() => {
				this.feedbackVisible = false;
			}, 1000);
		},
		getOptionClass(optionIndex) {
			if (!this.hasAnsweredCurrent) return "btn-outline-primary";
			return this.answers[this.currentQuestion.id] === optionIndex
				? "btn-primary"
				: "btn-outline-primary";
		},
		nextQuestion() {
			if (this.isLastQuestion && this.hasAnsweredCurrent) {
				this.submitQuiz();
			} else if (this.currentQuestionIndex < this.quiz.questions.length - 1) {
				this.feedbackVisible = false;
				this.currentQuestionIndex++;
			}
		},
		previousQuestion() {
			if (this.currentQuestionIndex > 0) {
				this.feedbackVisible = false;
				this.currentQuestionIndex--;
			}
		},
		async submitQuiz() {
			if (this.submitted) return;

			this.submitted = true;
			this.clearTimer();

			try {
				const result = await api.post(`/user/quizzes/${this.quiz.id}/submit`, {
					answers: this.answers,
				});

				// Redirect to summary page after successful submission
				this.$router.push(`/user/quiz/${this.quiz.id}/summary`);
			} catch (error) {
				console.error("Error submitting quiz:", error);
				// Revert submitted state if submission fails
				this.submitted = false;
				this.startTimer();
			}
		},
	},
};
</script>

<style scoped>
.timer {
	font-size: 1.2rem;
	font-weight: bold;
}
.question-text {
	font-size: 1.1rem;
	margin-bottom: 1.5rem;
}
.options-list .btn {
	border: 1px solid #dee2e6;
}
</style>
