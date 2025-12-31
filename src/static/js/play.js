// Function to hide and show things after the user's response
function show_answer(btn_answer) {
  const answer = document.querySelector(".flashcard-answer");
  const btnsGradeDiv = document.querySelector(".btns_grade_div");

  // Shows answer
  answer.classList.remove("d-none");

  // Hides the btn_answer
  btn_answer.classList.add("d-none");

  // Shows buttons of grade
  btnsGradeDiv.classList.remove("d-none");
}

// Function to reset the card after the show_answer() function changes some things
function reset_card() {
  const answer = document.querySelector(".flashcard-answer");
  const btnAnswer = document.getElementById("btn_answer");
  const btnsGradeDiv = document.querySelector(".btns_grade_div");

  // Hides answer
  answer.classList.add("d-none");

  // Hides buttons of grade
  btnsGradeDiv.classList.add("d-none");

  // Shows the btn_answer
  btnAnswer.classList.remove("d-none");
}

// Function to send user's grade and obtain the next playable card
document.addEventListener("DOMContentLoaded", function () {
  document
    .getElementsByClassName("btns_grade_div")[0]
    .addEventListener("click", async (event) => {
      const gradeBtn = event.target.closest(".btns_grade");
      if (!gradeBtn) return;

      // Get the data to be send
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

        // Gets the response from the server
        const result = await response.json();

        // If there are no more playable cards, go to the decks page
        if (result.done) {
          alert("No more cards to review!");
          window.location.href = "/decks";
          return;
        }

        // Create the next playable card

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

        // Redefine everything that the show_answer() function did
        reset_card();
      } catch (error) {
        alert("Connection error");
        console.error(error);
      }
    });
});
