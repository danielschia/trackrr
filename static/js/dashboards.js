document.addEventListener("DOMContentLoaded", () => {
	const listForm = document.getElementById("list-form");
	const listsContainer = document.getElementById("lists-container");

	if (!listForm || !listsContainer) {
		return;
	}

	const errorBox = document.getElementById("list-form-error");
	const apiUrl = listForm.dataset.apiUrl;

	const buildListCard = (list) => {
		const card = document.createElement("article");
		card.className = "list-column";
		card.dataset.listId = list.id;

		const title = document.createElement("h2");
		title.textContent = list.name;
		card.appendChild(title);

		if (list.description) {
			const description = document.createElement("p");
			description.textContent = list.description;
			card.appendChild(description);
		}

		const taskArea = document.createElement("div");
		taskArea.className = "list-column__tasks";
		card.appendChild(taskArea);

		return card;
	};

	listForm.addEventListener("submit", async (event) => {
		event.preventDefault();
		errorBox.textContent = "";

		const formData = new FormData(listForm);
		const payload = {
			dashboard_id: Number(formData.get("dashboard_id")),
			name: (formData.get("name") || "").toString().trim(),
			description: (formData.get("description") || "").toString().trim(),
		};

		try {
			const response = await fetch(apiUrl, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(payload),
			});

			const data = await response.json();

			if (!response.ok) {
				errorBox.textContent = data.error || "Unable to create list";
				return;
			}

			listsContainer.appendChild(buildListCard(data));
			listForm.reset();
		} catch (error) {
			errorBox.textContent = "An error occurred while creating the list.";
		}
	});
});
