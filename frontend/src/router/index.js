import { createRouter, createWebHistory } from "vue-router";
import Login from "../components/auth/Login.vue";
import Register from "../components/auth/Register.vue";
import Quiz from "@/components/user/Quiz.vue";

const routes = [
	{
		path: "/",
		redirect: "/login",
	},
	{
		path: "/login",
		name: "Login",
		component: Login,
		meta: { requiresAuth: false },
	},
	{
		path: "/register",
		name: "Register",
		component: Register,
		meta: { requiresAuth: false },
	},
	{
		path: "/admin",
		component: () => import("../components/admin/Dashboard.vue"),
		meta: { requiresAuth: true, requiresAdmin: true },
		children: [
			{
				path: "dashboard",
				redirect: "/admin/subjects",
			},
			{
				path: "",
				redirect: "/admin/subjects",
			},
			{
				path: "subjects",
				name: "AdminSubjects",
				component: () => import("../components/admin/Subjects.vue"),
			},
			{
				path: "chapters",
				name: "AdminChapters",
				component: () => import("../components/admin/Chapters.vue"),
			},
			{
				path: "quizzes",
				name: "AdminQuizzes",
				component: () => import("../components/admin/Quizzes.vue"),
			},
			{
				path: "quizzes/:quizId/questions",
				name: "AdminQuestions",
				component: () => import("../components/admin/Questions.vue"),
			},
			{
				path: "users",
				name: "AdminUsers",
				component: () => import("../components/admin/Users.vue"),
			},
		],
	},
	{
		path: "/user",
		component: () => import("../components/user/Dashboard.vue"),
		meta: { requiresAuth: true },
		children: [
			{
				path: "",
				redirect: "/user/dashboard",
			},
			{
				path: "dashboard",
				name: "UserDashboard",
				component: () => import("../components/user/Dashboard.vue"),
			},
			{
				path: "subjects", // This route might not be strictly necessary if SubjectList is always shown in Dashboard
				name: "UserSubjects",
				component: () => import("../components/user/SubjectList.vue"), // Or keep it nested in Dashboard
			},
			{
				path: "quiz/:id",
				name: "UserQuiz",
				component: Quiz,
				props: true, // Pass route params as props
			},
			{
				path: "scores",
				name: "UserScores",
				component: () => import("../components/user/Scores.vue"),
			},
		],
	},
];

const router = createRouter({
	history: createWebHistory(),
	routes,
});

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
	const token = localStorage.getItem("token");
	let user = null;

	try {
		const userStr = localStorage.getItem("user");
		user = userStr ? JSON.parse(userStr) : null;
	} catch (e) {
		// If there's an error parsing user data, clear it
		localStorage.removeItem("user");
		localStorage.removeItem("token");
		user = null;
	}

	// Allow access to login and register pages even when logged in
	if ((to.path === "/login" || to.path === "/register") && token) {
		// If user is already logged in, redirect to appropriate dashboard
		if (user?.roles?.includes("admin")) {
			return next("/admin");
		}
		return next("/user/dashboard");
	}

	// Check if route requires authentication
	if (to.meta.requiresAuth && !token) {
		return next("/login");
	}

	// Check if route requires admin role
	if (to.meta.requiresAdmin && (!user || !user.roles?.includes("admin"))) {
		return next("/user/dashboard");
	}

	next();
});

export default router;
