<template>
	<div class="container py-4">
		<div class="d-flex justify-content-between align-items-center mb-4">
			<h3>{{ quiz?.quiz_id ? `Quiz QDS2025${quiz.quiz_id}` : "Loading..." }}</h3>
			<div class="d-flex gap-3 align-items-center" v-if="!quizResult">
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

		<div v-if="!quizResult">
			<div class="mb-4">
				<div class="progress" style="height: 10px">
					<div
						class="progress-bar bg-info"
						role="progressbar"
						:style="{ width: progressPercentage + '%' }"
						:aria-valuenow="progressPercentage"
						aria-valuemin="0"
						aria-valuemax="100"
					></div>
				</div>
				<small class="text-muted d-block text-end mt-1"
					>{{ viewedQuestions.size }} of {{ quiz?.questions?.length || 0 }} viewed</small
				>
			</div>

			<div
				class="d-flex flex-wrap gap-3 justify-content-center mb-3 small text-muted align-items-center"
			>
				<span
					><span class="legend-box bg-white border border-secondary me-1"></span>Not
					Viewed</span
				>
				<span><span class="legend-box btn-danger-fill me-1"></span>Viewed</span>
				<span><span class="legend-box btn-success-fill me-1"></span>Answered</span>
				<span><span class="legend-box border border-info me-1"></span>Marked</span>
				<span><span class="legend-box bg-info me-1"></span>Answered & Marked</span>
			</div>

			<div class="mb-4">
				<div class="d-flex flex-wrap gap-2">
					<button
						v-for="(_, index) in quiz?.questions || []"
						:key="index"
						class="btn btn-sm"
						:class="getButtonClass(index)"
						@click="goToQuestion(index)"
					>
						{{ index + 1 }}
					</button>
				</div>
			</div>

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

					<div class="d-flex justify-content-start gap-2 mt-3">
						<button
							class="btn btn-outline-secondary btn-sm"
							@click="clearAnswer"
							:disabled="!answers[currentQuestionData.id]"
						>
							<i class="bi bi-x-lg me-1"></i> Clear Response
						</button>
						<button
							class="btn btn-sm"
							:class="
								isCurrentMarkedForReview
									? 'btn-info text-white'
									: 'btn-outline-info'
							"
							@click="toggleMarkForReview"
						>
							<i
								class="bi bi-bookmark-star-fill me-1"
								v-if="isCurrentMarkedForReview"
							></i>
							<i class="bi bi-bookmark-star me-1" v-else></i>
							{{ isCurrentMarkedForReview ? "Unmark" : "Mark" }} for Review
						</button>
					</div>
				</div>
			</div>

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
					class="btn"
					:class="isAllAnswered ? 'btn-success' : 'btn-secondary'"
					@click="submitQuiz(false)"
					:disabled="!isAllAnswered || timeRemaining <= 0"
					title="Submit the quiz"
				>
					<i class="bi bi-check-circle-fill me-1"></i>
					Submit Quiz
				</button>

				<button
					v-if="currentQuestion < quiz?.questions?.length - 1"
					class="btn btn-outline-primary"
					@click="nextQuestion"
				>
					Next
					<i class="bi bi-arrow-right ms-1"></i>
				</button>
				<div v-else style="width: 80px"></div>
			</div>
		</div>

		<div v-else class="card text-center">
			<div class="card-body">
				<h4 class="card-title">Quiz Submitted!</h4>
				<div class="d-flex justify-content-center my-4">
					<apexchart
						width="250"
						:options="resultChartOptions"
						:series="resultChartSeries"
					></apexchart>
				</div>
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
import VueApexCharts from "vue3-apexcharts";
import { api } from "@/utils/api";
import Toast from "@/components/common/Toast.vue";

export default {
	name: "QuizAttempt",
	components: { Toast, apexchart: VueApexCharts },
	data() {
		return {
			quiz: null,
			currentQuestion: 0,
			answers: {},
			markedForReview: {},
			viewedQuestions: new Set(),
			error: null,
			quizResult: null,
			timeRemaining: null,
			timerInterval: null,
			resultChartOptions: {
				chart: { type: "donut" },
				plotOptions: { pie: { donut: { size: "65%" } } },
				labels: ["Correct", "Incorrect"],
				colors: ["#198754", "#dc3545"],
				stroke: { width: 0 },
				legend: { position: "bottom" },
			},
			resultChartSeries: [],
		};
	},
	computed: {
		currentQuestionData() {
			return this.quiz?.questions[this.currentQuestion] || {};
		},
		isAllAnswered() {
			return this.quiz?.questions?.every((q) => this.answers[q.id]) || false;
		},
		progressPercentage() {
			if (!this.quiz?.questions?.length) return 0;
			return Math.round((this.viewedQuestions.size / this.quiz.questions.length) * 100);
		},
		formattedTime() {
			if (this.timeRemaining === null || this.timeRemaining < 0) return "00:00";
			const minutes = Math.floor(this.timeRemaining / 60);
			const seconds = this.timeRemaining % 60;
			return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
		},
		isCurrentMarkedForReview() {
			const qId = this.currentQuestionData.id;
			return !!this.markedForReview[qId];
		},
	},
	async created() {
		const quizId = this.$route.params.id;
		try {
			const response = await api.post(`/user/quizzes/${quizId}/start`);
			this.quiz = response;
			if (this.quiz?.questions?.length > 0) {
				this.updateViewedStatus(0);
			}
			if (this.quiz && this.quiz.time_duration) {
				this.timeRemaining = this.parseDuration(this.quiz.time_duration);
				if (this.timeRemaining > 0) {
					this.startTimer();
				} else {
					this.timeRemaining = 0;
				}
			}
		} catch (error) {
			this.error = error.response?.data?.error || "Failed to load quiz";
			setTimeout(() => {
				this.$router.push("/user/quizzes");
			}, 3000);
		}
	},
	beforeDestroy() {
		clearInterval(this.timerInterval);
	},
	methods: {
		updateViewedStatus(index) {
			if (!this.viewedQuestions.has(index)) {
				this.viewedQuestions.add(index);
			}
		},
		parseDuration(durationString) {
			const parts = durationString.split(":");
			if (parts.length !== 2) return 0;
			const hours = parseInt(parts[0], 10);
			const minutes = parseInt(parts[1], 10);
			if (isNaN(hours) || isNaN(minutes)) return 0;
			return hours * 3600 + minutes * 60;
		},
		startTimer() {
			clearInterval(this.timerInterval);
			this.timerInterval = setInterval(() => {
				if (this.timeRemaining > 0) {
					this.timeRemaining--;
				} else {
					clearInterval(this.timerInterval);
					this.timeRemaining = 0;
					if (!this.quizResult) {
						console.log("Time is up! Submitting quiz...");
						this.submitQuiz(true);
					}
				}
			}, 1000);
		},
		selectAnswer(questionId, optionNumber) {
			if (!this.quizResult && this.timeRemaining > 0) {
				this.answers[questionId] = optionNumber;
			}
		},
		toggleMarkForReview() {
			const qId = this.currentQuestionData.id;
			if (!this.quizResult && this.timeRemaining > 0 && qId) {
				this.markedForReview[qId] = !this.markedForReview[qId];
			}
		},
		clearAnswer() {
			const qId = this.currentQuestionData.id;
			if (!this.quizResult && this.timeRemaining > 0 && qId) {
				delete this.answers[qId];
			}
		},
		nextQuestion() {
			if (this.currentQuestion < this.quiz.questions.length - 1) {
				this.currentQuestion++;
				this.updateViewedStatus(this.currentQuestion);
			}
		},
		previousQuestion() {
			if (this.currentQuestion > 0) {
				this.currentQuestion--;
				this.updateViewedStatus(this.currentQuestion);
			}
		},
		goToQuestion(index) {
			if (index >= 0 && index < this.quiz.questions.length) {
				this.currentQuestion = index;
				this.updateViewedStatus(index);
			}
		},
		getButtonClass(index) {
			const question = this.quiz.questions[index];
			if (!question) return "btn-outline-secondary";

			const questionId = question.id;
			const isCurrent = this.currentQuestion === index;
			const isAnswered = this.answers.hasOwnProperty(questionId);
			const isMarked =
				this.markedForReview.hasOwnProperty(questionId) && this.markedForReview[questionId];
			const isViewed = this.viewedQuestions.has(index);

			if (isCurrent) return "btn-primary";

			if (isAnswered && isMarked) return "btn-info";
			if (isAnswered) return "btn-success-fill";
			if (isMarked) return "btn-outline-info";
			if (isViewed) return "btn-danger-fill";

			return "btn-outline-secondary";
		},
		async submitQuiz(isTimeUp = false) {
			clearInterval(this.timerInterval);
			if (this.quizResult) return;

			const questionsMarkedForReview = Object.values(this.markedForReview).some(
				(v) => v === true
			);
			if (!isTimeUp && questionsMarkedForReview) {
				if (
					!confirm(
						"You have questions marked for review. Are you sure you want to submit?"
					)
				) {
					if (this.timeRemaining > 0) this.startTimer();
					return;
				}
			}

			try {
				const response = await api.post(`/user/quizzes/${this.quiz.quiz_id}/submit`, {
					answers: this.answers,
					time_stamp_of_attempt: new Date().toISOString(),
				});
				this.quizResult = response;
				const correct = this.quizResult.total_scored;
				const total = this.quizResult.total_possible;
				const incorrect = total - correct;
				this.resultChartSeries = [correct, incorrect];
				this.error = null;
				this.timeRemaining = 0;
			} catch (error) {
				this.error = error.response?.data?.error || "Failed to submit quiz";
				if (this.timeRemaining > 0) {
					this.startTimer();
				}
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

.btn-success-fill {
	background-color: var(--bs-success);
	color: white;
}
.btn-danger-fill {
	background-color: var(--bs-danger);
	color: white;
}

.legend-box {
	display: inline-block;
	width: 12px;
	height: 12px;
	vertical-align: middle; 
}
</style>
