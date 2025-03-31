<template>
	<div>
		<div class="d-flex justify-content-between align-items-center mb-4">
			<h3>Quizzes</h3>
			<div class="d-flex gap-2">
				<div class="input-group">
					<input
						type="text"
						class="form-control"
						placeholder="Search subjects..."
						v-model="searchQuery"
					/>
					<span class="input-group-text">
						<i class="bi bi-search"></i>
					</span>
				</div>
			</div>
		</div>

		<div class="row">
			<div v-for="subject in filteredSubjects" :key="subject.id" class="col-md-6 mb-4">
				<div class="card h-100">
					<div class="card-header d-flex justify-content-between align-items-center">
						<h5 class="mb-0">{{ subject.name }}</h5>
					</div>
					<div class="card-body">
						<div v-for="chapter in subject.chapters" :key="chapter.id" class="mb-4">
							<div class="d-flex justify-content-between align-items-center mb-2">
								<h6 class="card-subtitle">{{ chapter.name }}</h6>
							</div>
							<div class="list-group">
								<div
									v-if="availableQuizzes.length"
									v-for="quiz in filterQuizzesByChapter(chapter.id)"
									:key="quiz.id"
									class="list-group-item"
								>
									<div class="d-flex justify-content-between align-items-center">
										<div>
											<span class="fw-bold">QDS2025{{ quiz.id }}</span>
											<small class="text-muted ms-2">
												<i class="bi bi-clock me-1"></i>
												Duration: {{ quiz.time_duration }}
											</small>
										</div>
										<div class="d-flex gap-2">
											<button
												class="btn btn-outline-primary btn-sm"
												@click="viewQuiz(quiz)"
												data-bs-toggle="modal"
												:data-bs-target="'#quizModal' + quiz.id"
											>
												<i class="bi bi-eye me-1"></i>
												View
											</button>
											<button
												class="btn btn-primary btn-sm"
												@click="startQuiz(quiz.id)"
											>
												<i class="bi bi-play-fill me-1"></i>
												Take Quiz
											</button>
										</div>
									</div>
								</div>
								<div v-else class="list-group-item text-muted">
									<i class="bi bi-info-circle me-2"></i>
									No quizzes available for this chapter
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<quiz-details-modal
			v-for="quiz in availableQuizzes"
			:key="'modal' + quiz.id"
			:quiz="quiz"
			:modalId="'quizModal' + quiz.id"
		/>
		<Toast v-if="error" :message="error" type="error" @hidden="error = null" />
	</div>
</template>

<script>
import { api } from "@/utils/api";
import QuizDetailsModal from "./QuizDetailsModal.vue";
import Toast from "@/components/common/Toast.vue";

export default {
	name: "SubjectList",
	components: {
		QuizDetailsModal,
		Toast,
	},
	data() {
		return {
			subjects: [],
			availableQuizzes: [],
			searchQuery: "",
			error: null,
		};
	},
	computed: {
		filteredSubjects() {
			if (!this.searchQuery) return this.subjects;
			const query = this.searchQuery.toLowerCase();
			return this.subjects.filter(
				(subject) =>
					subject.name.toLowerCase().includes(query) ||
					subject.chapters.some((chapter) => chapter.name.toLowerCase().includes(query))
			);
		},
	},
	async created() {
		try {
			// Fetch subjects
			const subjects = await api.get("/user/subjects");
			this.subjects = subjects;

			// Fetch available quizzes
			const quizzes = await api.get("/user/quizzes/upcoming");
			this.availableQuizzes = quizzes;
		} catch (error) {
			this.error = error.response?.data?.error || "Failed to load quizzes";
		}
	},
	methods: {
		filterQuizzesByChapter(chapterId) {
			return this.availableQuizzes.filter((quiz) => quiz.chapter_id === chapterId);
		},
		startQuiz(quizId) {
			this.$router.push(`/user/quiz/${quizId}`);
		},
		viewQuiz(quiz) {
			console.log("Viewing quiz:", quiz);
		},
	},
};
</script>

<style scoped>
.card {
	transition: transform 0.2s;
}
.card:hover {
	transform: translateY(-2px);
}
.list-group-item {
	transition: background-color 0.2s;
}
.list-group-item:hover {
	background-color: #f8f9fa;
}
</style>
