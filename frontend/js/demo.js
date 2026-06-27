// TerritoireSport — Démo Bayard Argentan
// Parcours utilisateur pré-rempli pour le projet "Ping pour Tous"

const DEMO_CLUB_ID = "90f8a193-a4b8-4975-b315-8e1484cdf3a3";
const DEMO_THEMES = ["cohesion", "inclusion", "sante"];

// 1. Charger la shortlist pour le club démo
async function loadDemoShortlist() {
  try {
    const res = await api(`/api/shortlist/${DEMO_CLUB_ID}?themes=${DEMO_THEMES.join(",")}&limit=10`);
    renderShortlist(res);
  } catch (err) {
    console.error("Erreur shortlist:", err);
    document.getElementById("shortlist-container").innerHTML =
      `<div class="card" style="border-left:4px solid var(--gold);">
        <strong>⚠️ Erreur de chargement</strong><br>
        ${err.message}
      </div>`;
  }
}

// 2. Afficher la shortlist
function renderShortlist(data) {
  const container = document.getElementById("shortlist-container");
  if (!container) return;

  const { club, shortlist, total_partners_in_territory, themes_requested } = data;

  let html = `
    <div class="card" style="background:var(--primary);color:white;">
      <h3 style="margin-bottom:.5rem;">🏓 ${club.name}</h3>
      <p style="opacity:.9;">${club.city} (${club.department}) — ${club.sport}</p>
      <p style="margin-top:1rem;font-size:.9rem;opacity:.8;">
        Thèmes sélectionnés : ${themes_requested.join(", ")}<br>
        ${total_partners_in_territory} partenaires identifiés sur le territoire
      </p>
    </div>
  `;

  if (shortlist.length === 0) {
    html += `<div class="card">Aucun partenaire ne matche ces critères. Essayez d'autres thèmes.</div>`;
  } else {
    shortlist.forEach((p, i) => {
      const typeLabel = { public: "Public", association: "Associatif", private: "Privé" }[p.type] || p.type;
      const themesHtml = (p.themes || []).map(t => `<span style="background:var(--accent2);color:white;padding:.2rem .6rem;border-radius:12px;font-size:.75rem;margin-right:.3rem;">${t}</span>`).join("");
      const matchingHtml = (p.matching_themes || []).map(t => `<span style="background:var(--gold);color:var(--primary);padding:.2rem .6rem;border-radius:12px;font-size:.75rem;margin-right:.3rem;font-weight:700;">✓ ${t}</span>`).join("");

      html += `
        <div class="card" style="border-left:4px solid var(--accent);">
          <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:.5rem;">
            <div>
              <h4 style="color:var(--primary);margin-bottom:.3rem;">${i + 1}. ${p.name}</h4>
              <p style="color:var(--muted);font-size:.85rem;">${typeLabel} — ${p.city || ""}</p>
            </div>
            <div style="background:var(--primary);color:white;padding:.4rem .8rem;border-radius:20px;font-weight:700;font-size:.9rem;">
              Score: ${p.score}
            </div>
          </div>
          <p style="margin:.8rem 0;font-size:.9rem;">${p.description || ""}</p>
          <div style="margin-top:.8rem;">
            ${matchingHtml}
            ${themesHtml}
          </div>
          ${p.contact_email ? `<p style="margin-top:.8rem;font-size:.85rem;">📧 <a href="mailto:${p.contact_email}">${p.contact_email}</a></p>` : ""}
          ${p.contact_url ? `<p style="font-size:.85rem;">🔗 <a href="${p.contact_url}" target="_blank">${p.contact_url}</a></p>` : ""}
        </div>
      `;
    });
  }

  container.innerHTML = html;
}

// 3. Lancer au chargement
document.addEventListener("DOMContentLoaded", () => {
  loadDemoShortlist();
});