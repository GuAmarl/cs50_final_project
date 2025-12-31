// Function to create a new deck
document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("add-deck").addEventListener("click", async () => {
    const input = document.getElementById("deck-name");
    const name = input.value.trim();

    if (!name) {
      alert("Must provide a name to the deck");
      return;
    }

    // Sends the name of the new deck
    const response = await fetch("/api/create_decks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });

    if (!response.ok) {
      alert("Erro ao criar deck");
      return;
    }

    // Gets the response of the new deck
    const deck = await response.json();

    // Create the HTML element for the list to display this new deck on the page.
    const li = document.createElement("li");
    li.dataset.id = deck[deck.length - 1].id;
    li.className =
      "list-group-item list-group-item-secondary flex-shrink-0 me-3";

    let html = `
      <div class="deck-container">
        <div class="deck-wrapper">
          <div class="card deck-card back-2"></div>
          <div class="card deck-card back-1"></div>
          <div class="card flashcard text-dark bg-light">
            <div class="card-header">
              <div class="row align-items-center">
                <div class="col-4"></div>

                <div class="col-4 text-center fw-semibold">${
                  deck[deck.length - 1].name
                }</div>

                <div class="col-4 text-end">
                <span class="badge bg-secondary ms-auto">
                ${deck[deck.length - 1].card_count} Cards
                </span>
              </div>
            </div>
          </div>
          <div class="card-body">
            <p class="card-text">This is a deck</p>
            <div class="d-grid gap-2 d-md-block">
              <a
                type="button"
                class="btn btn-sm btn-success position-relative"
                href="{{url_for('play', deck_id = ${
                  deck[deck.length - 1].id
                })}}"
              >
                Play`;

    // Add the badge with the number of playable cards only if there is more than one.
    if (deck[deck.length - 1].num_play_cards > 0) {
      html += `<span
                  class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger"
                >
                  ${deck[deck.length - 1].num_play_cards}
                  <span class="visually-hidden">playable cards</span>
                </span>`;
    }
    html += `
                <i class="bi bi-play-fill"></i>
              </a>
              <a
                type="button"
                class="btn btn-sm btn-primary d-inline-flex align-items-center"
                href="{{url_for('cards', deck_id = ${
                  deck[deck.length - 1].id
                })}}"
              >
                Inspect
                <span class="icon-deck me-1">
                  <i class="bi bi-file-fill"></i>
                  <i class="bi bi-file-fill"></i>
                  <i class="bi bi-file-fill"></i>
                </span>
              </a>
              <button type="button" class="btn btn-sm btn-danger delete-deck">
                Del Deck
                <i class="bi bi-trash"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    `;

    li.innerHTML = html;

    // Insert before the deck creation card
    const list = document.getElementById("deck-list");
    list.insertBefore(li, list.lastElementChild);

    input.value = "";
  });
});

// Function to delete a deck
document.addEventListener("DOMContentLoaded", function () {
  document
    .getElementById("deck-list")
    .addEventListener("click", async (event) => {
      if (!event.target.classList.contains("delete-deck")) return;

      const li = event.target.closest("li");
      const deckId = li.dataset.id;

      // Send the id of the deck to be deleted
      try {
        const response = await fetch(`/api/delete_deck/${deckId}`, {
          method: "DELETE",
        });

        if (!response.ok) {
          alert("Erro ao deletar deck");
          return;
        }

        // Waits for deletion in the database and then removes the element from the list as well.
        li.remove();
      } catch (error) {
        alert("Falha de conexão com o servidor");
      }
    });
});
