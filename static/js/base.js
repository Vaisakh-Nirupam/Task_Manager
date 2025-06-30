// Fading the Flash Messages
setTimeout(() => {
    const flash = document.getElementById("flash-message");
    if (flash) {
        flash.style.opacity = 0;
        setTimeout(() => flash.remove(), 500);
    }
}, 3000);


// Fading the Flash Messages (& Hiding the button) 
const flash_profile = document.getElementById("flash-message-disappear");

// Edit button on profile page
const editButton = document.getElementById("edit_profile_btn"); 
if (flash_profile && editButton) {
    editButton.style.display = "none";
    setTimeout(() => {
        flash_profile.style.opacity = 0;
        setTimeout(() => {
            flash_profile.remove();
            editButton.style.display = "inline-block";
        }, 500);
    }, 3000);
}

// Submit button on Add Task page
const addButton = document.getElementById("add_task_btn");
if (flash_profile && addButton) {
    addButton.style.display = "none";
    setTimeout(() => {
        flash_profile.style.opacity = 0;
        setTimeout(() => {
            flash_profile.remove();
            addButton.style.display = "inline-block";
        }, 500);
    }, 3000);
}

// Submit button on Login page
const loginButton = document.getElementById("login_btn");
if (flash_profile && loginButton) {
    loginButton.style.display = "none";
    setTimeout(() => {
        flash_profile.style.opacity = 0;
        setTimeout(() => {
            flash_profile.remove();
            loginButton.style.display = "inline-block";
        }, 500);
    }, 3000);
}

// Back and Exit Functionality on Signup Page
document.querySelectorAll(".return_button").forEach(button => {
    button.addEventListener("click", function() {
        const action = this.textContent.trim().toLowerCase();
        if(action === "back") {
            document.getElementById("stage_action").value = "back";
        } else if(action === "exit") {
            document.getElementById("stage_action").value = "exit";
        }
        this.form.submit();
    });
});