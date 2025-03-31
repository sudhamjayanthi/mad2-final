<template>
	<div class="container mt-4">
		<div class="card">
			<div class="card-header d-flex justify-content-between align-items-center">
				<h3 class="mb-0">Your Quiz History</h3>
				<button
					class="btn btn-sm btn-outline-primary"
					@click="exportScores"
					:disabled="isExporting"
				>
					<span
						v-if="isExporting"
						class="spinner-border spinner-border-sm"
						role="status"
						aria-hidden="true"
					></span>
					{{ isExporting ? "Exporting..." : "Export Scores" }}
				</button>
			</div>
			<div class="card-body">
				<div class="mb-3 row align-items-center">
					<label for="quizFilter" class="col-sm-auto col-form-label"
						>Filter by Quiz:</label
					>
					<div class="col-sm-4">
						<select class="form-select" id="quizFilter" v-model="selectedQuizId">
							<option :value="null">All Quizzes</option>
							<option v-for="quizId in uniqueQuizIds" :key="quizId" :value="quizId">
								QDS2025{{ quizId }}
							</option>
						</select>
					</div>
				</div>

				<div v-if="scores.length > 0" class="mb-4 row">
					<div class="col-md-6 mb-3 mb-md-0">
						<apexchart
							type="line"
							height="350"
							:options="chartOptions"
							:series="chartSeries"
						></apexchart>
					</div>
					<div class="col-md-6">
						<apexchart
							type="bar"
							height="350"
							:options="highestScoreChartOptions"
							:series="highestScoreChartSeries"
						></apexchart>
					</div>
				</div>

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
							<tr v-for="score in filteredScoresByDropdown" :key="score.id">
								<td>QDS2025{{ score.quiz_id }}</td>
								<td>{{ score.total_questions }}</td>
								<td>{{ formatDate(score.attempted_at) }}</td>
								<td>{{ score.percentage }}%</td>
							</tr>
							<tr v-if="filteredScoresByDropdown.length === 0 && scores.length > 0">
								<td colspan="4" class="text-center">
									No scores found matching your filter.
								</td>
							</tr>
							<tr v-if="scores.length === 0">
								<td colspan="4" class="text-center py-4">
									You haven't attempted any quizzes yet.
									<div class="mt-3">
										<router-link
											to="/user/quizzes"
											class="btn btn-primary btn-sm"
										>
											Take a Quiz
										</router-link>
									</div>
								</td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>
		</div>
		<Toast v-if="error" :message="error" type="error" @hidden="error = null" />
		<Toast
			v-if="successMessage"
			:message="successMessage"
			type="success"
			@hidden="successMessage = null"
		/>
	</div>
</template>

<script>
import { api } from "@/utils/api";
import Toast from "@/components/common/Toast.vue";
import VueApexCharts from "vue3-apexcharts";

export default {
	name: "Scores",
	components: {
		Toast,
		apexchart: VueApexCharts,
	},
	data() {
		return {
			scores: [],
			error: null,
			successMessage: null,
			isExporting: false,
			selectedQuizId: null,
			chartOptions: {
				chart: {
					id: "quiz-scores-chart",
					type: "line",
					height: 350,
					zoom: {
						enabled: false,
					},
				},
				xaxis: {
					type: "datetime",
					title: {
						text: "Attempt Date",
					},
				},
				yaxis: {
					title: {
						text: "Score (%)",
					},
					min: 0,
					max: 100,
				},
				stroke: {
					curve: "smooth",
				},
				tooltip: {
					x: {
						format: "dd MMM yyyy HH:mm",
					},
				},
				title: {
					text: "Score Trend Over Time (All Quizzes)",
					align: "left",
				},
				noData: {
					text: "No score data available for trend chart...",
				},
			},
			chartSeries: [
				{
					name: "Score",
					data: [],
				},
			],
			highestScoreChartOptions: {
				chart: {
					id: "highest-scores-chart",
					type: "bar",
					height: 350,
				},
				xaxis: {
					categories: [],
					title: {
						text: "Quiz ID",
					},
				},
				yaxis: {
					title: {
						text: "Highest Score (%)",
					},
					min: 0,
					max: 100,
				},
				title: {
					text: "Highest Score per Quiz",
					align: "left",
				},
				plotOptions: {
					bar: {
						horizontal: false,
						columnWidth: "55%",
						endingShape: "rounded",
					},
				},
				dataLabels: {
					enabled: false,
				},
				noData: {
					text: "No score data available for highest score chart...",
				},
			},
			highestScoreChartSeries: [
				{
					name: "Highest Score",
					data: [],
				},
			],
		};
	},
	async created() {
		await this.fetchScores();
	},
	computed: {
		uniqueQuizIds() {
			const ids = new Set(this.scores.map((score) => score.quiz_id));
			return Array.from(ids).sort((a, b) => a - b);
		},
		filteredScoresByDropdown() {
			if (this.selectedQuizId === null || this.selectedQuizId === "") {
				return this.scores;
			}
			return this.scores.filter((score) => score.quiz_id === this.selectedQuizId);
		},
	},
	methods: {
		async fetchScores() {
			try {
				const response = await api.get("/user/scores");
				console.log("Raw scores data received:", response);
				this.scores = response.sort(
					(a, b) => new Date(a.attempted_at) - new Date(b.attempted_at)
				);
				this.updateTrendChartData();
				this.updateHighestScoreChartData();
			} catch (error) {
				this.error = error.response?.data?.error || "Failed to load scores";
				this.chartSeries = [{ name: "Score", data: [] }];
				this.highestScoreChartSeries = [{ name: "Highest Score", data: [] }];
				this.highestScoreChartOptions.xaxis.categories = [];
			}
		},
		updateTrendChartData() {
			const seriesData = this.scores.map((score) => {
				return {
					x: new Date(score.attempted_at).getTime(),
					y: score.percentage,
				};
			});
			this.chartSeries = [{ name: "Score", data: seriesData }];
		},
		updateHighestScoreChartData() {
			const highestScores = {};
			this.scores.forEach((score) => {
				if (
					!highestScores[score.quiz_id] ||
					score.percentage > highestScores[score.quiz_id]
				) {
					highestScores[score.quiz_id] = score.percentage;
				}
			});

			const sortedQuizIds = Object.keys(highestScores)
				.map(Number)
				.sort((a, b) => a - b);

			const categories = sortedQuizIds.map((id) => `QDS2025${id}`);
			const seriesData = sortedQuizIds.map((id) => highestScores[id]);

			this.highestScoreChartOptions = {
				...this.highestScoreChartOptions,
				xaxis: {
					...this.highestScoreChartOptions.xaxis,
					categories: categories,
				},
			};
			this.highestScoreChartSeries = [{ name: "Highest Score", data: seriesData }];
		},
		async exportScores() {
			this.isExporting = true;
			this.error = null;
			this.successMessage = null;
			try {
				const response = await api.post("/user/export/scores");
				if (response && response.message) {
					this.successMessage = response.message;
				} else {
					this.successMessage = "Score export started successfully.";
				}
			} catch (error) {
				this.error = error.response?.data?.error || "Failed to start score export";
			} finally {
				this.isExporting = false;
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
