<template>
	<div class="modal fade" :id="modalId" tabindex="-1">
		<div class="modal-dialog">
			<div class="modal-content">
				<div class="modal-header">
					<h5 class="modal-title">View Quiz</h5>
					<button type="button" class="btn-close" data-bs-dismiss="modal"></button>
				</div>
				<div class="modal-body">
					<div class="mb-3">
						<label class="fw-bold">ID:</label>
						<span class="ms-2">QDS2025{{ quiz.id }}</span>
					</div>
					<div class="mb-3">
						<label class="fw-bold">Subject:</label>
						<span class="ms-2">{{ quiz.subject_name }}</span>
					</div>
					<div class="mb-3">
						<label class="fw-bold">Chapter:</label>
						<span class="ms-2">{{ quiz.chapter_name }}</span>
					</div>
					<div class="mb-3">
						<label class="fw-bold">Number of Questions:</label>
						<span class="ms-2">{{ quiz.total_questions }}</span>
					</div>
					<div class="mb-3">
						<label class="fw-bold">Scheduled Date:</label>
						<span class="ms-2">{{ formatDate(quiz.date_of_quiz) }}</span>
					</div>
					<div class="mb-3">
						<label class="fw-bold">Duration:</label>
						<span class="ms-2">{{ quiz.time_duration }}</span>
					</div>
				</div>
				<div class="modal-footer">
					<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
						Close
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
export default {
	name: "QuizDetailsModal",
	props: {
		quiz: {
			type: Object,
			required: true,
		},
		modalId: {
			type: String,
			required: true,
		},
	},
	methods: {
		formatDate(date) {
			return new Date(date).toLocaleString();
		},
	},
};
</script>
