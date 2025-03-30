<template>
	<div class="card">
		<div class="card-body">
			<div class="d-flex justify-content-between align-items-center mb-4">
				<div>
					<h5 class="card-title mb-0">Quiz Questions</h5>
					<small class="text-muted">Quiz ID: {{ $route.params.quizId }}</small>
				</div>
				<div>
					<button class="btn btn-secondary me-2" @click="$router.back()">
						<i class="bi bi-arrow-left"></i> Back to Quizzes
					</button>
					<button class="btn btn-primary" @click="showAddModal">
						<i class="bi bi-plus"></i> Add Question
					</button>
				</div>
			</div>

			<!-- Questions List -->
			<div class="table-responsive">
				<table class="table table-hover">
					<thead>
						<tr>
							<th>ID</th>
							<th>Question</th>
							<th>Options</th>
							<th>Correct</th>
							<th>Actions</th>
						</tr>
					</thead>
					<tbody>
						<tr v-for="question in questions" :key="question.id">
							<td>{{ question.id }}</td>
							<td>{{ question.question_statement }}</td>
							<td>
								<ol type="1">
									<li>{{ question.option1 }}</li>
									<li>{{ question.option2 }}</li>
									<li>{{ question.option3 }}</li>
									<li>{{ question.option4 }}</li>
								</ol>
							</td>
							<td>Option {{ question.correct_option }}</td>
							<td>
								<button
									class="btn btn-sm btn-outline-primary me-2"
									@click="editQuestion(question)"
								>
									<i class="bi bi-pencil"></i>
								</button>
								<button
									class="btn btn-sm btn-outline-danger"
									@click="confirmDelete(question)"
								>
									<i class="bi bi-trash"></i>
								</button>
							</td>
						</tr>
						<tr v-if="!questions.length">
							<td colspan="5" class="text-center">No questions found</td>
						</tr>
					</tbody>
				</table>
			</div>

			<!-- Add/Edit Modal -->
			<div
				class="modal fade"
				id="questionModal"
				tabindex="-1"
				ref="modal"
				data-bs-backdrop="static"
			>
				<div class="modal-dialog modal-lg">
					<div class="modal-content">
						<div class="modal-header">
							<h5 class="modal-title">
								{{ isEditing ? "Edit Question" : "Add Question" }}
							</h5>
							<button
								type="button"
								class="btn-close"
								data-bs-dismiss="modal"
							></button>
						</div>
						<div class="modal-body">
							<form @submit.prevent="handleSubmit">
								<div class="mb-3">
									<label for="statement" class="form-label">Question</label>
									<textarea
										class="form-control"
										id="statement"
										v-model="formData.question_statement"
										rows="3"
										required
									></textarea>
								</div>
								<div class="row">
									<div class="col-md-6 mb-3">
										<label for="option1" class="form-label">Option 1</label>
										<input
											type="text"
											class="form-control"
											id="option1"
											v-model="formData.option1"
											required
										/>
									</div>
									<div class="col-md-6 mb-3">
										<label for="option2" class="form-label">Option 2</label>
										<input
											type="text"
											class="form-control"
											id="option2"
											v-model="formData.option2"
											required
										/>
									</div>
									<div class="col-md-6 mb-3">
										<label for="option3" class="form-label">Option 3</label>
										<input
											type="text"
											class="form-control"
											id="option3"
											v-model="formData.option3"
											required
										/>
									</div>
									<div class="col-md-6 mb-3">
										<label for="option4" class="form-label">Option 4</label>
										<input
											type="text"
											class="form-control"
											id="option4"
											v-model="formData.option4"
											required
										/>
									</div>
								</div>
								<div class="mb-3">
									<label for="correct" class="form-label">Correct Option</label>
									<select
										class="form-select"
										id="correct"
										v-model="formData.correct_option"
										required
									>
										<option value="">Select correct option...</option>
										<option value="1">Option 1</option>
										<option value="2">Option 2</option>
										<option value="3">Option 3</option>
										<option value="4">Option 4</option>
									</select>
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
								:disabled="loading"
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
						<div class="modal-body">Are you sure you want to delete this question?</div>
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
	name: "Questions",
	components: {
		Toast,
	},
	data() {
		return {
			questions: [],
			formData: {
				question_statement: "",
				option1: "",
				option2: "",
				option3: "",
				option4: "",
				correct_option: "",
			},
			selectedQuestion: null,
			isEditing: false,
			loading: false,
			modal: null,
			deleteModal: null,
			error: null,
		};
	},
	mounted() {
		this.modal = new Modal(this.$refs.modal);
		this.deleteModal = new Modal(this.$refs.deleteModal);
		this.fetchQuestions();
	},
	methods: {
		async fetchQuestions() {
			this.loading = true;
			try {
				this.questions = await api.get(
					`/admin/quizzes/${this.$route.params.quizId}/questions`
				);
			} catch (error) {
				console.error("Error fetching questions:", error);
				this.error = error.response?.data?.error || "Failed to load questions";
			} finally {
				this.loading = false;
			}
		},
		showAddModal() {
			this.isEditing = false;
			this.formData = {
				question_statement: "",
				option1: "",
				option2: "",
				option3: "",
				option4: "",
				correct_option: "",
			};
			this.modal.show();
		},
		editQuestion(question) {
			this.isEditing = true;
			this.selectedQuestion = question;
			this.formData = { ...question };
			this.modal.show();
		},
		confirmDelete(question) {
			this.selectedQuestion = question;
			this.deleteModal.show();
		},
		async handleSubmit() {
			this.loading = true;
			try {
				if (this.isEditing) {
					await api.put(`/admin/questions/${this.selectedQuestion.id}`, this.formData);
				} else {
					await api.post(
						`/admin/quizzes/${this.$route.params.quizId}/questions`,
						this.formData
					);
				}
				await this.fetchQuestions();
				this.modal.hide();
			} catch (error) {
				console.error("Error saving question:", error);
				this.error = error.response?.data?.error || "Failed to save question";
			} finally {
				this.loading = false;
			}
		},
		async handleDelete() {
			this.loading = true;
			try {
				await api.delete(`/admin/questions/${this.selectedQuestion.id}`);
				await this.fetchQuestions();
				this.deleteModal.hide();
			} catch (error) {
				console.error("Error deleting question:", error);
				this.error = error.response?.data?.error || "Failed to delete question";
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

ol {
	margin-bottom: 0;
	padding-left: 1.5rem;
}
</style>
