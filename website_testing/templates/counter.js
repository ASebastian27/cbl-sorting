let updateBtn = document.querySelectorAll(".updateBtn button");
let updateNumber = document.getElementById("updateNumber");
let score = 0;

const updateScore = () => {
    updateNumber.textContent = score;
    if (score > 0) {
        updateNumber.style.color = "green";
    } if (score < 0) {
        updateNumber.style.color = "red";
    } else if (score === 0) {
        updateNumber.style.color = "#FFFFFF";
    }
}

updateBtn.forEach((button) => {
    button.addEventListener("click", (e) => {
        let btnId = e.target.id;
        if (btnId === "increment") {
            score++;
            updateScore();
            return;
        } else if (btnId === "decrement") {
            score--;
            updateScore();
            return;
        } else if (btnId === "reset") {
          score = 0;
          updateScore();
          return;
        }
    })
})

updateScore();
