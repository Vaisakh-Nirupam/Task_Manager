// Fading the Flash Messages
setTimeout(() => {
    const flash = document.getElementById("flash-message");
    if (flash) {
        flash.style.opacity = 0;
        setTimeout(() => flash.remove(), 500);
    }
}, 3000);


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