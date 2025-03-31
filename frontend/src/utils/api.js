const BASE_URL = "http://localhost:6900/api";

const getAuthHeader = () => ({
	"Authentication-Token": localStorage.getItem("token"),
	"Content-Type": "application/json",
});

const handleResponse = async (response) => {
	if (!response.ok) {
		const error = await response.json().catch(() => ({}));
		throw new Error(error.message || `API Error: ${response.statusText}`);
	}
	return response.status === 204 ? null : response.json();
};

const request = async (endpoint, options = {}) => {
	try {
		const response = await fetch(`${BASE_URL}${endpoint}`, {
			...options,
			headers: getAuthHeader(),
		});
		return handleResponse(response);
	} catch (error) {
		if (error instanceof TypeError && error.message === "Failed to fetch") {
			throw new Error(
				"Unable to connect to the server. Please check your internet connection or try again later."
			);
		}
		throw error;
	}
};

export const api = {
	get: (endpoint) => request(endpoint),

	post: (endpoint, data) =>
		request(endpoint, {
			method: "POST",
			body: JSON.stringify(data),
		}),

	put: (endpoint, data) =>
		request(endpoint, {
			method: "PUT",
			body: data ? JSON.stringify(data) : null,
		}),

	delete: (endpoint) => request(endpoint, { method: "DELETE" }),
};
