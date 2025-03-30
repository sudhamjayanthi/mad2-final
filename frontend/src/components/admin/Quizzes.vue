<template>
	<div class="card">
		<div class="card-body">
			<div class="d-flex justify-content-between align-items-center mb-4">
				<h5 class="card-title mb-0">Quizzes</h5>
				<button class="btn btn-primary" @click="showAddModal">
					<i class="bi bi-plus"></i> Add Quiz
				</button>
			</div>

			<!-- Replace subject/chapter selection with search -->
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

			<!-- Update Quizzes List section -->
			<div class="table-responsive">
				<table class="table table-hover">
					<thead>
						<tr>
							<th>ID</th>
							<th>Subject</th>
							<th>Chapter</th>
							<th>Date</th>
							<th>Duration</th>
							<th>Actions</th>
						</tr>
					</thead>
					<tbody>
						<tr v-for="quiz in filteredQuizzes" :key="quiz.id">
							<td>{{ quiz.id }}</td>
							<td>{{ quiz.subject_name }}</td>
							<td>{{ quiz.chapter_name }}</td>
							<td>{{ formatDate(quiz.date_of_quiz) }}</td>
							<td>{{ quiz.time_duration }}</td>
							<td>
								<button
									class="btn btn-sm btn-outline-secondary me-2"
									@click="manageQuestions(quiz)"
								>
									Manage Questions
								</button>
								<button
									class="btn btn-sm btn-outline-primary me-2"
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
							</td>
						</tr>
						<tr v-if="!filteredQuizzes.length">
							<td colspan="6" class="text-center">No quizzes found</td>
						</tr>
					</tbody>
				</table>
			</div>

			<!-- Add/Edit Modal -->
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
								<!-- Only show subject/chapter selection when adding new quiz -->
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
								<!-- Existing date and duration fields -->
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
							<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
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

			<!-- Delete Confirmation Modal -->
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
							<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
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
</template>

<script>
import { Modal } from "bootstrap";
import { api } from "@/utils/api";
import Toast from "@/components/common/Toast.vue";

export default {
	name: "Quizzes",
	components: {
		Toast,
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
				// Fetch subjects first
				this.subjects = await api.get("/admin/subjects");

				// Fetch chapters for each subject
				const chaptersPromises = this.subjects.map((subject) =>
					api.get(`/admin/subjects/${subject.id}/chapters`)
				);
				const chaptersResults = await Promise.all(chaptersPromises);

				// Flatten chapters array and add subject info
				this.chapters = chaptersResults.flat().map((chapter) => ({
					...chapter,
					subject_name: this.subjects.find((s) => s.id === chapter.subject_id)?.name,
				}));

				// Fetch quizzes for each chapter
				const quizzesPromises = this.chapters.map((chapter) =>
					api.get(`/admin/chapters/${chapter.id}/quizzes`)
				);
				const quizzesResults = await Promise.all(quizzesPromises);

				// Flatten quizzes array and add chapter/subject info
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
				const localDate = new Date(this.formData.date_of_quiz);
				const utcDate = new Date(
					localDate.getTime() + localDate.getTimezoneOffset() * 60000
				);

				const formattedData = {
					...this.formData,
					date_of_quiz: utcDate.toISOString(),
				};

				if (this.isEditing) {
					await api.put(`/admin/quizzes/${this.selectedQuiz.id}`, formattedData);
				} else {
					await api.post(
						`/admin/chapters/${this.selectedQuiz.chapter_id}/quizzes`,
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
	},
};
</script>

<style scoped>
.table th {
	background-color: #f8f9fa;
}
</style>
