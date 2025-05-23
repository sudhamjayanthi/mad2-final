<template>
	<div>
		<div class="row mb-4">
			<div class="col-lg-12 mb-4">
				<div class="card h-100 shadow-sm">
					<div class="card-header">
						<i class="bi bi-bar-chart-line-fill me-2"></i>Subject Wise Top Scores
					</div>
					<div class="card-body d-flex justify-content-center align-items-center">
						<div v-if="chartLoading" class="spinner-border text-primary" role="status">
							<span class="visually-hidden">Loading...</span>
						</div>
						<div v-else-if="chartError" class="alert alert-danger w-100">
							{{ chartError }}
						</div>
						<div
							v-else-if="topScoresSeries[0]?.data.length"
							class="chart-container w-100"
						>
							<apexchart
								type="bar"
								height="300"
								:options="topScoresOptions"
								:series="topScoresSeries"
							></apexchart>
						</div>
						<p v-else class="text-muted">No score data available.</p>
					</div>
				</div>
			</div>
			
		</div>

		<div class="card">
			<div class="card-body">
				<div class="d-flex justify-content-between align-items-center mb-4">
					<h5 class="card-title mb-0">Quizzes</h5>
					<button class="btn btn-primary" @click="showAddModal">
						<i class="bi bi-plus"></i> Add Quiz
					</button>
				</div>

				<div class="mb-4">
					<div class="input-group">
						<input
							type="text"
							class="form-control"
							placeholder="Search by subject or chapter..."
							v-model="searchQuery"
						/>
						<span class="input-group-text">
							<i class="bi bi-search"></i>
						</span>
					</div>
				</div>

				<div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
					<div v-for="quiz in filteredQuizzes" :key="quiz.id" class="col">
						<div class="card h-100 shadow-sm">
							<div class="card-body">
								<div class="d-flex justify-content-between align-items-start mb-2">
									<h5 class="card-title mb-0">{{ quiz.subject_name }}</h5>
									<span class="badge bg-primary">ID: {{ quiz.id }}</span>
								</div>
								<h6 class="card-subtitle mb-3 text-muted">
									{{ quiz.chapter_name }}
								</h6>

								<div class="mb-3">
									<div class="d-flex align-items-center mb-2">
										<i class="bi bi-calendar-event me-2"></i>
										<span>{{ formatDate(quiz.date_of_quiz) }}</span>
									</div>
									<div class="d-flex align-items-center">
										<i class="bi bi-clock me-2"></i>
										<span>Duration: {{ quiz.time_duration }}</span>
									</div>
								</div>

								<div class="d-flex gap-2 mt-auto">
									<button
										class="btn btn-sm btn-outline-secondary flex-grow-1"
										@click="manageQuestions(quiz)"
									>
										<i class="bi bi-list-check me-1"></i> Questions
									</button>
									<button
										class="btn btn-sm btn-outline-primary"
										@click="editQuiz(quiz)"
									>
										<i class="bi bi-pencil"></i>
									</button>
									<button
										class="btn btn-sm btn-outline-danger"
										@click="confirmDelete(quiz)"
									>
										<i class="bi bi-trash"></i>
									</button>
								</div>
							</div>
						</div>
					</div>
					<div v-if="!filteredQuizzes.length" class="col-12 text-center py-5">
						<p class="text-muted">No quizzes found</p>
					</div>
				</div>

				<div
					class="modal fade"
					id="quizModal"
					tabindex="-1"
					ref="modal"
					data-bs-backdrop="static"
				>
					<div class="modal-dialog">
						<div class="modal-content">
							<div class="modal-header">
								<h5 class="modal-title">
									{{ isEditing ? "Edit Quiz" : "Add Quiz" }}
								</h5>
								<button
									type="button"
									class="btn-close"
									data-bs-dismiss="modal"
								></button>
							</div>
							<div class="modal-body">
								<form @submit.prevent="handleSubmit">
									<template v-if="!isEditing">
										<div class="mb-3">
											<label for="subject" class="form-label"
												>Select Subject</label
											>
											<select
												class="form-select"
												id="subject"
												v-model="selectedSubject"
											>
												<option value="">Choose a subject...</option>
												<option
													v-for="subject in subjects"
													:key="subject.id"
													:value="subject.id"
												>
													{{ subject.name }}
												</option>
											</select>
										</div>
										<div class="mb-3">
											<label for="chapter" class="form-label"
												>Select Chapter</label
											>
											<select
												class="form-select"
												id="chapter"
												v-model="formData.chapter_id"
												:disabled="!selectedSubject"
											>
												<option value="">Choose a chapter...</option>
												<option
													v-for="chapter in chapters.filter(
														(c) => c.subject_id === selectedSubject
													)"
													:key="chapter.id"
													:value="chapter.id"
												>
													{{ chapter.name }}
												</option>
											</select>
										</div>
									</template>
									<div class="mb-3">
										<label for="date" class="form-label">Date and Time</label>
										<input
											type="datetime-local"
											class="form-control"
											id="date"
											v-model="formData.date_of_quiz"
											required
										/>
									</div>
									<div class="mb-3">
										<label for="duration" class="form-label"
											>Duration (HH:MM)</label
										>
										<input
											type="text"
											class="form-control"
											id="duration"
											v-model="formData.time_duration"
											pattern="[0-9]{2}:[0-9]{2}"
											placeholder="01:30"
											required
										/>
									</div>
								</form>
							</div>
							<div class="modal-footer">
								<button
									type="button"
									class="btn btn-secondary"
									data-bs-dismiss="modal"
								>
									Cancel
								</button>
								<button
									type="button"
									class="btn btn-primary"
									@click="handleSubmit"
									:disabled="loading || (!isEditing && !formData.chapter_id)"
								>
									{{ loading ? "Saving..." : "Save" }}
								</button>
							</div>
						</div>
					</div>
				</div>

				<div
					class="modal fade"
					id="deleteModal"
					tabindex="-1"
					ref="deleteModal"
					data-bs-backdrop="static"
				>
					<div class="modal-dialog">
						<div class="modal-content">
							<div class="modal-header">
								<h5 class="modal-title">Confirm Delete</h5>
								<button
									type="button"
									class="btn-close"
									data-bs-dismiss="modal"
								></button>
							</div>
							<div class="modal-body">Are you sure you want to delete this quiz?</div>
							<div class="modal-footer">
								<button
									type="button"
									class="btn btn-secondary"
									data-bs-dismiss="modal"
								>
									Cancel
								</button>
								<button
									type="button"
									class="btn btn-danger"
									@click="handleDelete"
									:disabled="loading"
								>
									{{ loading ? "Deleting..." : "Delete" }}
								</button>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import { Modal } from "bootstrap";
import { api } from "@/utils/api";
import Toast from "@/components/common/Toast.vue";
import VueApexCharts from "vue3-apexcharts";

export default {
	name: "Quizzes",
	components: {
		Toast,
		apexchart: VueApexCharts,
	},
	data() {
		return {
			quizzes: [],
			searchQuery: "",
			formData: {
				date_of_quiz: "",
				time_duration: "",
				chapter_id: "",
			},
			subjects: [],
			chapters: [],
			selectedSubject: "",
			selectedQuiz: null,
			isEditing: false,
			loading: false,
			modal: null,
			deleteModal: null,
			error: null,
			chartLoading: true,
			chartError: null,
			topScoresOptions: {
				chart: { id: "top-scores-bar", toolbar: { show: false } },
				xaxis: { categories: [] },
				yaxis: {
					max: 100,
					title: { text: "Highest Score (%)" },
					labels: {
						formatter: (val) => {
							return val + "%";
						},
					},
				},
				plotOptions: { bar: { horizontal: false, columnWidth: "55%" } },
				dataLabels: { enabled: false },
				tooltip: {
					y: {
						formatter: function (val) {
							return val + "%";
						},
					},
				},
				noData: { text: "Loading..." },
			},
			topScoresSeries: [{ name: "Highest Score (%)", data: [] }],
			attemptsOptions: {
				chart: { id: "attempts-doughnut", toolbar: { show: false } },
				labels: [],
				legend: { position: "bottom" },
				tooltip: {
					y: {
						formatter: function (val) {
							return String(val);
						},
					},
				},
				noData: { text: "Loading..." },
				responsive: [
					{
						breakpoint: 480,
						options: {
							chart: { width: 200 },
							legend: { position: "bottom" },
						},
					},
				],
			},
			attemptsSeries: [],
		};
	},
	computed: {
		filteredQuizzes() {
			if (!this.searchQuery) return this.quizzes;

			const query = this.searchQuery.toLowerCase();
			return this.quizzes.filter(
				(quiz) =>
					quiz.subject_name.toLowerCase().includes(query) ||
					quiz.chapter_name.toLowerCase().includes(query)
			);
		},
	},
	mounted() {
		this.modal = new Modal(this.$refs.modal);
		this.deleteModal = new Modal(this.$refs.deleteModal);
		this.fetchAllData();
		this.fetchChartData();
	},
	methods: {
		formatDate(dateString) {
			const date = new Date(dateString);
			return date.toLocaleString("en-GB", {
				day: "2-digit",
				month: "2-digit",
				year: "numeric",
				hour: "2-digit",
				minute: "2-digit",
			});
		},
		async fetchAllData() {
			this.loading = true;
			try {
				this.subjects = await api.get("/admin/subjects");

				const chaptersPromises = this.subjects.map((subject) =>
					api.get(`/admin/subjects/${subject.id}/chapters`)
				);
				const chaptersResults = await Promise.all(chaptersPromises);

				this.chapters = chaptersResults.flat().map((chapter) => ({
					...chapter,
					subject_name: this.subjects.find((s) => s.id === chapter.subject_id)?.name,
				}));

				const quizzesPromises = this.chapters.map((chapter) =>
					api.get(`/admin/chapters/${chapter.id}/quizzes`)
				);
				const quizzesResults = await Promise.all(quizzesPromises);

				this.quizzes = quizzesResults.flat().map((quiz) => {
					const chapter = this.chapters.find((c) => c.id === quiz.chapter_id);
					return {
						...quiz,
						chapter_name: chapter?.name,
						subject_name: chapter?.subject_name,
					};
				});
			} catch (error) {
				console.error("Error fetching data:", error);
				this.error = error.response?.data?.error || "Failed to load data";
			} finally {
				this.loading = false;
			}
		},
		showAddModal() {
			this.isEditing = false;
			this.formData = {
				date_of_quiz: "",
				time_duration: "",
				chapter_id: "",
			};
			this.selectedSubject = "";
			this.modal.show();
		},
		editQuiz(quiz) {
			this.isEditing = true;
			this.selectedQuiz = quiz;
			const date = new Date(quiz.date_of_quiz);
			this.formData = {
				date_of_quiz: new Date(date.getTime() - date.getTimezoneOffset() * 60000)
					.toISOString()
					.slice(0, 16),
				time_duration: quiz.time_duration,
				chapter_id: quiz.chapter_id,
			};
			this.selectedSubject = this.subjects.find((s) => s.id === quiz.subject_id)?.name;
			this.modal.show();
		},
		confirmDelete(quiz) {
			this.selectedQuiz = quiz;
			this.deleteModal.show();
		},
		manageQuestions(quiz) {
			this.$router.push(`/admin/quizzes/${quiz.id}/questions`);
		},
		async handleSubmit() {
			this.loading = true;
			try {
				const formattedData = {
					...this.formData,
					date_of_quiz: this.formData.date_of_quiz,
				};

				if (this.isEditing) {
					await api.put(`/admin/quizzes/${this.selectedQuiz.id}`, formattedData);
				} else {
					await api.post(
						`/admin/chapters/${this.formData.chapter_id}/quizzes`,
						formattedData
					);
				}
				await this.fetchAllData();
				this.modal.hide();
			} catch (error) {
				console.error("Error saving quiz:", error);
				this.error = error.response?.data?.error || "Failed to save quiz";
			} finally {
				this.loading = false;
			}
		},
		async handleDelete() {
			this.loading = true;
			try {
				await api.delete(`/admin/quizzes/${this.selectedQuiz.id}`);
				await this.fetchAllData();
				this.deleteModal.hide();
			} catch (error) {
				console.error("Error deleting quiz:", error);
				this.error = error.response?.data?.error || "Failed to delete quiz";
			} finally {
				this.loading = false;
			}
		},
		async fetchChartData() {
			this.chartLoading = true;
			this.chartError = null;
			this.topScoresOptions = { ...this.topScoresOptions, xaxis: { categories: [] } };
			this.topScoresSeries = [{ name: "Highest Score (%)", data: [] }];
			this.attemptsOptions = { ...this.attemptsOptions, labels: [] };
			this.attemptsSeries = [];

			try {
				const stats = await api.get("/admin/stats/subject-summary");

				if (stats.topScores && stats.topScores.length > 0) {
					this.topScoresOptions = {
						...this.topScoresOptions,
						xaxis: {
							categories: stats.topScores.map((item) => item.subject),
						},
					};
					this.topScoresSeries = [
						{
							name: "Highest Score (%)",
							data: stats.topScores.map((item) => item.topScore),
						},
					];
				} else {
					this.topScoresSeries = [{ name: "Highest Score (%)", data: [] }];
				}

				if (stats.attempts && stats.attempts.length > 0) {
					this.attemptsOptions = {
						...this.attemptsOptions,
						labels: stats.attempts.map((item) => item.subject),
					};
					this.attemptsSeries = stats.attempts.map((item) => item.attempts);
				} else {
					this.attemptsSeries = [];
				}
			} catch (error) {
				console.error("Error fetching chart data:", error);
				this.chartError = error.response?.data?.error || "Failed to load chart data";
				this.topScoresOptions = {
					...this.topScoresOptions,
					noData: { text: "Failed to load data" },
				};
				this.attemptsOptions = {
					...this.attemptsOptions,
					noData: { text: "Failed to load data" },
				};
			} finally {
				this.chartLoading = false;
			}
		},
	},
};
</script>

<style scoped>
.badge {
	font-size: 0.8rem;
}

.chart-container {
	position: relative;
	min-height: 300px;
	width: 100%;
}

.card-body {
	min-height: 350px;
}

.card-body > .spinner-border,
.card-body > .alert,
.card-body > p.text-muted {
	margin: auto;
}
</style>
