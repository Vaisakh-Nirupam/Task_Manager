// Fade out ALL flash messages after 3s
setTimeout(() => {
    const flashes = document.querySelectorAll(".flash");
    flashes.forEach(flash => {
        flash.style.opacity = 0;
        setTimeout(() => flash.remove(), 500);
    });
}, 3000);

// Fade Flash & Hide Button Function
function handleFlashAndButton(buttonId) {
    const flash = document.querySelector(".flash");
    const button = document.getElementById(buttonId);

    if (flash && button) {
        button.style.display = "none";
        setTimeout(() => {
            flash.style.opacity = 0;
            setTimeout(() => {
                flash.remove();
                button.style.display = "inline-block";
            }, 500);
        }, 3000);
    }
}

// Adding Buttons for Fading 
[
    "edit_profile_btn",
    "change_profile_btn",
    "add_task_btn",
    "login_btn",
    "signup_btn",
    "create_pass_btn",
    "change_pass_btn",
    "send_message_mobile"
].forEach(id => handleFlashAndButton(id));


// Back & Exit Navigation
function setStage(stage, formId) {
    document.getElementById("stage_action").value = stage;
    document.querySelector(`#${formId} form`).submit();
}