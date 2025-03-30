<template>
	<div class="card">
		<div class="card-body">
			<div class="d-flex justify-content-between align-items-center mb-4">
				<h5 class="card-title mb-0">Subjects</h5>
				<button class="btn btn-primary" @click="showAddModal">
					<i class="bi bi-plus"></i> Add Subject
				</button>
			</div>

			<!-- Subjects List -->
			<div class="table-responsive">
				<table class="table table-hover">
					<thead>
						<tr>
							<th>ID</th>
							<th>Name</th>
							<th>Actions</th>
						</tr>
					</thead>
					<tbody>
						<tr v-for="subject in subjects" :key="subject.id">
							<td>{{ subject.id }}</td>
							<td>{{ subject.name }}</td>
							<td>
								<button
									class="btn btn-sm btn-outline-primary me-2"
									@click="editSubject(subject)"
								>
									<i class="bi bi-pencil"></i>
								</button>
								<button
									class="btn btn-sm btn-outline-danger"
									@click="confirmDelete(subject)"
								>
									<i class="bi bi-trash"></i>
								</button>
							</td>
						</tr>
						<tr v-if="!subjects.length">
							<td colspan="3" class="text-center">No subjects found</td>
						</tr>
					</tbody>
				</table>
			</div>

			<!-- Add/Edit Modal -->
			<div
				class="modal fade"
				id="subjectModal"
				tabindex="-1"
				ref="modal"
				data-bs-backdrop="static"
			>
				<div class="modal-dialog">
					<div class="modal-content">
						<div class="modal-header">
							<h5 class="modal-title">
								{{ isEditing ? "Edit Subject" : "Add Subject" }}
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
									<label for="name" class="form-label">Subject Name</label>
									<input
										type="text"
										class="form-control"
										id="name"
										v-model="formData.name"
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
						<div class="modal-body">Are you sure you want to delete this subject?</div>
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

			<Toast v-if="error" :message="error" type="error" @hidden="error = null" />
		</div>
	</div>
</template>

<script>
import { Modal } from "bootstrap";
import { api } from "@/utils/api";
import Toast from "@/components/common/Toast.vue";

export default {
	name: "Subjects",
	components: {
		Toast,
	},
	data() {
		return {
			subjects: [],
			formData: {
				name: "",
			},
			selectedSubject: null,
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
		this.fetchSubjects();
	},
	methods: {
		async fetchSubjects() {
			this.loading = true;
			try {
				this.subjects = await api.get("/admin/subjects");
			} catch (error) {
				console.error("Error fetching subjects:", error);
				this.error = error.response?.data?.error || "Failed to load subjects";
			} finally {
				this.loading = false;
			}
		},
		showAddModal() {
			this.isEditing = false;
			this.formData = { name: "" };
			this.modal.show();
		},
		editSubject(subject) {
			this.isEditing = true;
			this.selectedSubject = subject;
			this.formData = { name: subject.name };
			this.modal.show();
		},
		confirmDelete(subject) {
			this.selectedSubject = subject;
			this.deleteModal.show();
		},
		async handleSubmit() {
			this.loading = true;
			try {
				const data = { name: this.formData.name };
				if (this.selectedSubject) {
					await api.put(`/admin/subjects/${this.selectedSubject.id}`, data);
				} else {
					await api.post("/admin/subjects", data);
				}
				await this.fetchSubjects();
				this.modal.hide();
			} catch (error) {
				console.error("Error saving subject:", error);
				this.error = error.response?.data?.error || "Failed to save subject";
			} finally {
				this.loading = false;
			}
		},
		async handleDelete() {
			this.loading = true;
			try {
				await api.delete(`/admin/subjects/${this.selectedSubject.id}`);
				await this.fetchSubjects();
				this.deleteModal.hide();
			} catch (error) {
				console.error("Error deleting subject:", error);
				this.error = error.response?.data?.error || "Failed to delete subject";
			} finally {
				this.loading = false;
				this.selectedSubject = null;
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
