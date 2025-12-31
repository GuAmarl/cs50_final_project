function show_answer(btn_answer) {
  const answer = document.querySelector(".flashcard-answer");
  const btnsGradeDiv = document.querySelector(".btns_grade_div");

  // mostra resposta
  answer.classList.remove("d-none");

  // esconde botão Answer
  btn_answer.classList.add("d-none");

  // mostra botões de grade
  btnsGradeDiv.classList.remove("d-none");
  // const btns_grade = document.getElementsByClassName("btns_grade");

  // answer[0].style.display = "block";

  // for (let i = 0; i <= btns_grade.length - 1; i++) {
  //   btns_grade[i].style.visibility = "visible";
  // }

  // btn_answer.style.visibility = "hidden";
}

function reset_card() {
  const answer = document.querySelector(".flashcard-answer");
  const btnAnswer = document.getElementById("btn_answer");
  const btnsGradeDiv = document.querySelector(".btns_grade_div");

  answer.classList.add("d-none");
  btnsGradeDiv.classList.add("d-none");
  btnAnswer.classList.remove("d-none");
}

document.addEventListener("DOMContentLoaded", function () {
  document
    .getElementsByClassName("btns_grade_div")[0]
    .addEventListener("click", async (event) => {
      const gradeBtn = event.target.closest(".btns_grade");
      if (!gradeBtn) return;

      const grade = parseInt(gradeBtn.value, 10);
      const cardId = parseInt(
        document.getElementsByClassName("btns_grade_div")[0].id,
        10
      );
      const deckId = parseInt(
        document.getElementsByClassName("deck_id")[0].id,
        10
      );

      try {
        const response = await fetch("/api/play_cards", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            card_id: cardId,
            deck_id: deckId,
            grade: grade,
          }),
        });

        if (!response.ok) {
          alert("Server error");
          return;
        }

        const result = await response.json();

        if (result.done) {
          alert("No more cards to review!");
          window.location.href = "/decks";
          return;
        }

        // ---------- Badge ----------
        let badgeClass = "bg-primary";

        if (result.state === "learning") badgeClass = "bg-success";
        else if (result.state === "review") badgeClass = "bg-primary";
        else if (result.state === "relearning") badgeClass = "bg-warning";

        document.getElementById("state_badge").innerHTML = `
          <span class="badge ${badgeClass} ms-auto">
            ${result.state}
          </span>
        `;

        // ---------- Card content ----------
        document.querySelector(".flashcard-question").innerHTML = result.front;
        document.querySelector(".flashcard-answer").innerHTML = result.back;

        // ---------- Update card id ----------
        document.querySelector(".btns_grade_div").id = result.id;

        reset_card();
      } catch (error) {
        alert("Connection error");
        console.error(error);
      }
    });
});
