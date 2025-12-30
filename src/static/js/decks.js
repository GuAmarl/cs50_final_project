document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("add-deck").addEventListener("click", async () => {
    const input = document.getElementById("deck-name");
    const name = input.value.trim();

    if (!name) {
      alert("Must provide a name to the deck");
      return;
    }

    const response = await fetch("/api/create_decks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });

    if (!response.ok) {
      alert("Erro ao criar deck");
      return;
    }

    const deck = await response.json();

    const li = document.createElement("li");
    li.dataset.id = deck[deck.length - 1].id;
    li.className = "list-group-item list-group-item-secondary me-2";

    li.innerHTML = `
    <div class="card flashcard text-dark bg-light">
      <div class="deck-container">
        <div class="deck-wrapper">
          <div class="card deck-card back-2"></div>
          <div class="card deck-card back-1"></div>
          <div class="card-header">${deck[deck.length - 1].name}</div>
          <div class="card-body">
            <p class="card-text">This is a deck</p>
            <div class="d-grid gap-2 d-md-block">
              <a
                type="button"
                class="btn btn-sm btn-success"
                href="{{url_for('play', deck_id = deck.id)}}"
              >
                Play
                <i class="bi bi-play-fill"></i>
              </a>
              <a
                type="button"
                class="btn btn-sm btn-primary d-inline-flex align-items-center"
                href="{{url_for('cards', deck_id = deck.id)}}"
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

    // INSERE ANTES do card de criação
    const list = document.getElementById("deck-list");
    list.insertBefore(li, list.lastElementChild);

    input.value = "";
  });
});

document.addEventListener("DOMContentLoaded", function () {
  document
    .getElementById("deck-list")
    .addEventListener("click", async (event) => {
      if (!event.target.classList.contains("delete-deck")) return;

      const li = event.target.closest("li");
      const deckId = li.dataset.id;

      try {
        const response = await fetch(`/api/delete_deck/${deckId}`, {
          method: "DELETE",
        });

        if (!response.ok) {
          alert("Erro ao deletar deck");
          return;
        }

        li.remove();
      } catch (error) {
        alert("Falha de conexão com o servidor");
      }
    });
});
