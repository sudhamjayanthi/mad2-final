<template>
	<div class="card">
		<div class="card-body">
			<div class="d-flex justify-content-between align-items-center mb-4">
				<h5 class="card-title mb-0">Chapters</h5>
				<button class="btn btn-primary" @click="showAddModal" :disabled="!selectedSubject">
					<i class="bi bi-plus"></i> Add Chapter
				</button>
			</div>

			<!-- Subject Selection -->
			<div class="mb-4">
				<label for="subject" class="form-label">Select Subject</label>
				<select
					class="form-select"
					id="subject"
					v-model="selectedSubject"
					@change="fetchChapters"
				>
					<option value="">Choose a subject...</option>
					<option v-for="subject in subjects" :key="subject.id" :value="subject.id">
						{{ subject.name }}
					</option>
				</select>
			</div>

			<!-- Chapters List -->
			<div class="table-responsive" v-if="selectedSubject">
				<table class="table table-hover">
					<thead>
						<tr>
							<th>ID</th>
							<th>Name</th>
							<th>Actions</th>
						</tr>
					</thead>
					<tbody>
						<tr v-for="chapter in chapters" :key="chapter.id">
							<td>{{ chapter.id }}</td>
							<td>{{ chapter.name }}</td>
							<td>
								<button
									class="btn btn-sm btn-outline-primary me-2"
									@click="editChapter(chapter)"
								>
									<i class="bi bi-pencil"></i>
								</button>
								<button
									class="btn btn-sm btn-outline-danger"
									@click="confirmDelete(chapter)"
								>
									<i class="bi bi-trash"></i>
								</button>
							</td>
						</tr>
						<tr v-if="!chapters.length">
							<td colspan="3" class="text-center">No chapters found</td>
						</tr>
					</tbody>
				</table>
			</div>

			<div v-else class="text-center text-muted">
				Please select a subject to view its chapters
			</div>

			<!-- Add/Edit Modal -->
			<div
				class="modal fade"
				id="chapterModal"
				tabindex="-1"
				ref="modal"
				data-bs-backdrop="static"
			>
				<div class="modal-dialog">
					<div class="modal-content">
						<div class="modal-header">
							<h5 class="modal-title">
								{{ isEditing ? "Edit Chapter" : "Add Chapter" }}
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
									<label for="name" class="form-label">Chapter Name</label>
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
						<div class="modal-body">Are you sure you want to delete this chapter?</div>
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
	name: "Chapters",
	components: {
		Toast,
	},
	data() {
		return {
			subjects: [],
			chapters: [],
			selectedSubject: "",
			formData: {
				name: "",
			},
			selectedChapter: null,
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
		async fetchChapters() {
			if (!this.selectedSubject) return;

			this.loading = true;
			try {
				this.chapters = await api.get(`/admin/subjects/${this.selectedSubject}/chapters`);
			} catch (error) {
				console.error("Error fetching chapters:", error);
				this.error = error.response?.data?.error || "Failed to load chapters";
			} finally {
				this.loading = false;
			}
		},
		showAddModal() {
			this.isEditing = false;
			this.formData = { name: "" };
			this.modal.show();
		},
		editChapter(chapter) {
			this.isEditing = true;
			this.selectedChapter = chapter;
			this.formData = { name: chapter.name };
			this.modal.show();
		},
		confirmDelete(chapter) {
			this.selectedChapter = chapter;
			this.deleteModal.show();
		},
		async handleSubmit() {
			this.loading = true;
			try {
				const data = { name: this.formData.name };
				if (this.selectedChapter) {
					await api.put(`/admin/chapters/${this.selectedChapter.id}`, data);
				} else {
					await api.post(`/admin/subjects/${this.selectedSubject}/chapters`, data);
				}
				await this.fetchChapters();
				this.modal.hide();
			} catch (error) {
				console.error("Error saving chapter:", error);
				this.error = error.response?.data?.error || "Failed to save chapter";
			} finally {
				this.loading = false;
			}
		},
		async handleDelete() {
			this.loading = true;
			try {
				await api.delete(`/admin/chapters/${this.selectedChapter.id}`);
				await this.fetchChapters();
				this.deleteModal.hide();
			} catch (error) {
				console.error("Error deleting chapter:", error);
				this.error = error.response?.data?.error || "Failed to delete chapter";
			} finally {
				this.loading = false;
				this.selectedChapter = null;
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
