document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("add-card").addEventListener("click", async () => {
    const input_front = document.getElementById("front_card");
    const input_back = document.getElementById("back_card");
    const deck_id = document.getElementById("deck_id").value;

    const front = input_front.value.trim();
    const back = input_back.value.trim();

    if (!front) {
      alert("Must provide front input");
      return;
    }

    if (!back) {
      alert("Must provide back input");
      return;
    }

    const data = {
      front: front,
      back: back,
      deck_id: deck_id,
    };

    const response = await fetch("/api/create_cards", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      alert("Erro ao criar card");
      return;
    }

    const card = await response.json();
    console.log(card);

    let html = `<tr><td>${card[card.length - 1].front}</td><td>${
      card[card.length - 1].back
    }</td></tr>`;

    // INSERE ANTES do card de criação
    const table_body = document.querySelector("tbody");
    table_body.innerHTML += html;

    input_front.value = "";
    input_back.value = "";
  });
});

document.addEventListener("DOMContentLoaded", function () {
  let input = document.getElementById("search_card_input");
  input.addEventListener("input", async function () {
    // async function search_cards() {
    const input = document.getElementById("search_card_input");
    const deck_id = document.getElementById("deck_id").value;

    const table_body = document.querySelector("tbody");

    let response = await fetch(
      "/api/search?q=" + input.value + "&deck_id=" + deck_id
    );

    let cards = await response.json();

    let html = "";

    for (let i in cards) {
      html += `<tr><td>${cards[i].front}</td><td>${cards[i].back}</td><td>
        <button id=${cards[i].id} type="button" class="btn btn-sm btn-danger delete-card">
          <i class="bi bi-trash"></i>
        </button>
      </td></tr>`;
    }

    table_body.innerHTML = html;
  });
});

document.addEventListener("DOMContentLoaded", function () {
  document
    .getElementById("table_cards")
    .addEventListener("click", async (event) => {
      const deleteBtn = event.target.closest(".delete-card");
      if (!deleteBtn) return;

      const cardId = deleteBtn.id;
      const row = deleteBtn.closest("tr");

      // if (!confirm("Deseja realmente deletar este card?")) return;

      try {
        const response = await fetch(`/api/delete_card/${cardId}`, {
          method: "DELETE",
        });

        if (!response.ok) {
          alert("Erro ao deletar card");
          return;
        }

        // Remove from table (DOM)
        row.remove();
      } catch (error) {
        alert("Erro de conexão com o servidor");
      }
    });
});
