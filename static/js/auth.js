document.addEventListener("DOMContentLoaded",() => {
    const loginForm = document.getElementById("login-form");
    const signupForm = document.getElementById("signup-form");
    
    if (loginForm) {
        loginForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            const errorBox = document.getElementById("error-box");
            errorBox.textContent = ""; // Clear previous error messages
            if (!document.getElementById("username").value || !document.getElementById("password").value) {
                errorBox.textContent = "Username and password are required";
                return;
            }
            
            const payload = {
                username: document.getElementById("username").value,
                password: document.getElementById("password").value
            };
            
            try {
                const response = await fetch("/auth/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();
                if (!response.ok) {
                    errorBox.textContent = data.message || "Login failed";
                    return;
                } else {
                    localStorage.setItem("access_token", data.access_token);
                    window.location.href = "/dashboards-page"; // Redirect to dashboard or another page
                } 
            } catch (error) {
                errorBox.textContent = "An error occurred. Please try again.";
            }
        });
    }

    if (signupForm) {
        signupForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            const errorBox = document.getElementById("error-box");
            errorBox.textContent = ""; // Clear previous error messages
            if (!document.getElementById("username").value || !document.getElementById("password").value || !document.getElementById("email").value) {
                errorBox.textContent = "Username, email, and password are required";
                return;
            }

            const payload = {
                username: document.getElementById("username").value,
                email: document.getElementById("email").value,
                password: document.getElementById("password").value
            };

            try {
                const response = await fetch("/auth/signup", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();
                if (!response.ok) {
                    errorBox.textContent = data.message || "Signup failed";
                    return;
                } else {
                    localStorage.setItem("access_token", data.access_token);
                    window.location.href = "/dashboards-page"; // Redirect to dashboard or another page
                }
            } catch (error) {
                errorBox.textContent = "An error occurred. Please try again.";
            }
        });
    }
});