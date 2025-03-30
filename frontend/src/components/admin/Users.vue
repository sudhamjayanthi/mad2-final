<template>
	<div class="card">
		<div class="card-body">
			<div class="d-flex justify-content-between align-items-center mb-4">
				<h5 class="card-title mb-0">Users</h5>
			</div>

			<Toast v-if="error" :message="error" type="error" @hidden="error = null" />

			<!-- Users List -->
			<div class="table-responsive">
				<table class="table table-hover">
					<thead>
						<tr>
							<th>ID</th>
							<th>Name</th>
							<th>Email</th>
							<th>Qualification</th>
							<th>Role</th>
							<th>Status</th>
							<th>Created At</th>
							<th>Actions</th>
						</tr>
					</thead>
					<tbody>
						<tr v-for="user in users" :key="user.id">
							<td>{{ user.id }}</td>
							<td>{{ user.full_name }}</td>
							<td>{{ user.email }}</td>
							<td>{{ user.qualification || "-" }}</td>
							<td>
								<span class="badge" :class="getRoleBadgeClass(user.roles)">
									{{ user.roles.join(", ") }}
								</span>
							</td>
							<td>
								<span class="badge" :class="getStatusBadgeClass(user.active)">
									{{ user.active ? "Active" : "Inactive" }}
								</span>
							</td>
							<td>{{ formatDate(user.created_at) }}</td>
							<td>
								<div class="btn-group">
									<button
										class="btn btn-sm"
										:class="user.active ? 'btn-warning' : 'btn-success'"
										@click="toggleUserStatus(user)"
										:disabled="loading"
									>
										{{ user.active ? "Deactivate" : "Activate" }}
									</button>
									<button
										class="btn btn-sm btn-danger ms-2"
										@click="confirmDelete(user)"
										:disabled="loading"
									>
										Delete
									</button>
								</div>
							</td>
						</tr>
						<tr v-if="!users.length">
							<td colspan="8" class="text-center">No users found</td>
						</tr>
					</tbody>
				</table>
			</div>
		</div>

		<!-- Delete Confirmation Modal -->
		<div class="modal fade" id="deleteModal" tabindex="-1" ref="deleteModal">
			<div class="modal-dialog">
				<div class="modal-content">
					<div class="modal-header">
						<h5 class="modal-title">Confirm Delete</h5>
						<button type="button" class="btn-close" data-bs-dismiss="modal"></button>
					</div>
					<div class="modal-body">
						Are you sure you want to delete user "{{ selectedUser?.full_name }}"?
					</div>
					<div class="modal-footer">
						<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
							Cancel
						</button>
						<button
							type="button"
							class="btn btn-danger"
							@click="deleteUser"
							:disabled="loading"
						>
							Delete
						</button>
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
	name: "Users",
	components: {
		Toast,
	},
	data() {
		return {
			users: [],
			loading: false,
			selectedUser: null,
			deleteModal: null,
			error: null,
		};
	},
	mounted() {
		this.fetchUsers();
		this.deleteModal = new Modal(this.$refs.deleteModal);
	},
	methods: {
		async fetchUsers() {
			this.loading = true;
			try {
				this.users = await api.get("/admin/users");
			} catch (error) {
				console.error("Error fetching users:", error);
				this.error = error.response?.data?.error || "Failed to load users";
			} finally {
				this.loading = false;
			}
		},
		async toggleUserStatus(user) {
			this.loading = true;
			try {
				const updatedUser = await api.put(`/admin/users/${user.id}/toggle-active`);
				const index = this.users.findIndex((u) => u.id === updatedUser.id);
				if (index !== -1) {
					this.users[index].active = updatedUser.active;
				}
			} catch (error) {
				console.error("Error toggling user status:", error);
				this.error = error.response?.data?.error || "Failed to update user status";
			} finally {
				this.loading = false;
			}
		},
		confirmDelete(user) {
			this.selectedUser = user;
			this.deleteModal.show();
		},
		async deleteUser() {
			if (!this.selectedUser) return;

			this.loading = true;
			try {
				await api.delete(`/admin/users/${this.selectedUser.id}`);
				this.users = this.users.filter((u) => u.id !== this.selectedUser.id);
				this.deleteModal.hide();
			} catch (error) {
				console.error("Error deleting user:", error);
				this.error = error.response?.data?.error || "Failed to delete user";
			} finally {
				this.loading = false;
				this.selectedUser = null;
			}
		},
		getRoleBadgeClass(roles) {
			return roles.includes("admin") ? "bg-danger" : "bg-primary";
		},
		getStatusBadgeClass(active) {
			return active ? "bg-success" : "bg-secondary";
		},
		formatDate(dateString) {
			return new Date(dateString).toLocaleDateString("en-US", {
				year: "numeric",
				month: "short",
				day: "numeric",
			});
		},
	},
};
</script>

<style scoped>
.table th {
	background-color: #f8f9fa;
}

.badge {
	font-size: 0.875rem;
	font-weight: 500;
}

.btn-group .btn {
	padding: 0.25rem 0.5rem;
	font-size: 0.875rem;
}
</style>
