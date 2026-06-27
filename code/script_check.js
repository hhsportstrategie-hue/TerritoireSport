
// ========== STATE ==========
const API = '';
const state = {
    club_id: null,
    answers: {},
    score: 0,
    profile: null,
    selected_project: null,
    selected_partners: [],
    selected_aaps: [],
    dossier_id: null
};

// ========== INIT ==========
document.addEventListener('DOMContentLoaded', () => {
    loadStep1();
    const form = document.getElementById('club-form');
    if (form) form.addEventListener('submit', submitStep1);
});

// ========== STEP 1: Création club ==========
async function loadStep1() {}

async function submitStep1(e) {
    if (e) e.preventDefault();
    const data = {
        name: document.getElementById('club-name').value,
        sport: document.getElementById('club-sport').value,
        commune: document.getElementById('club-commune').value,
        email: document.getElementById('club-email').value
    };
    let r, j;
    try {
        r = await fetch(API + '/api/clubs/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        j = await r.json();
    } catch (err) {
        // Mode dégradé : générer un ID local pour permettre de continuer
        state.club_id = 'local-' + Date.now();
        document.getElementById('result-1').innerHTML = `
            <div class="result-box">
                <h3>✅ Club créé (mode local)</h3>
                <p><strong>Nom:</strong> ${data.name}</p>
                <p><strong>Sport:</strong> ${data.sport}</p>
                <p><strong>Commune:</strong> ${data.commune}</p>
                <p style="font-size:0.85em;color:#6b7280;margin-top:8px;">⚠️ Sauvegarde serveur indisponible, votre parcours reste en local.</p>
            </div>`;
        markDone(1);
        renderQuestions();
        goToStep(2);
        return;
    }
    if (r.ok) {
        state.club_id = j.club_id || j.id;
        document.getElementById('result-1').innerHTML = `
            <div class="result-box">
                <h3>✅ Club créé avec succès</h3>
                <p><strong>Nom:</strong> ${j.name || data.name}</p>
                <p><strong>Sport:</strong> ${j.sport || data.sport}</p>
                <p><strong>Commune:</strong> ${j.commune || data.commune}</p>
            </div>`;
        markDone(1);
        renderQuestions();
        goToStep(2);
    } else {
        document.getElementById('result-1').innerHTML = `
            <div class="result-box error">
                <h3>❌ Erreur</h3>
                <p>${j.detail || 'Erreur inconnue'}</p>
            </div>`;
    }
}

// ========== STEP 2: Questions ==========
function renderQuestions() {
    const questions = [
        { id: 'q1', text: 'Avez-vous déjà réalisé un projet à impact social/environnemental ?', options: ['Oui, plusieurs', 'Oui, un', 'Non, jamais'] },
        { id: 'q2', text: 'Avez-vous des partenariats actifs avec des associations locales ?', options: ['Oui, régulièrement', 'Ponctuellement', 'Non'] },
        { id: 'q3', text: 'Mesurez-vous l\'impact de vos actions ?', options: ['Oui, avec des indicateurs', 'Informellement', 'Non'] },
        { id: 'q4', text: 'Avez-vous une stratégie RSE ou de développement durable ?', options: ['Oui, formalisée', 'En réflexion', 'Non'] },
        { id: 'q5', text: 'Avez-vous déjà candidaté à un appel à projets ?', options: ['Oui, et obtenu', 'Oui, sans succès', 'Non'] }
    ];
    const html = questions.map(q => `
        <div class="question-card" style="margin-bottom: 16px; padding: 16px; background: #f9fafb; border-radius: 8px;">
            <label style="font-weight: 500; display: block; margin-bottom: 8px;">${q.text}</label>
            <select id="${q.id}" class="form-select" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px;">
                <option value="">-- Choisir --</option>
                ${q.options.map(o => `<option value="${o}">${o}</option>`).join('')}
            </select>
        </div>
    `).join('');
    document.getElementById('questions-container').innerHTML = html;
}

async function submitStep2() {
    const answers = {};
    document.querySelectorAll('.question-card select').forEach(sel => {
        answers[sel.id] = sel.value;
    });
    const r = await fetch(API + '/api/diagnostics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ club_id: state.club_id, answers })
    });
    const j = await r.json();
    if (r.ok) {
        state.score = j.score;
        state.profile = j.profile;
        document.getElementById('result-2').innerHTML = `
            <div class="result-box">
                <h3>📊 Profil évalué</h3>
                <p><strong>Score:</strong> ${j.score}/20</p>
                <p><strong>Profil:</strong> ${j.profile}</p>
                <p style="margin-top: 12px; color: #6b7280;">${j.description || ''}</p>
            </div>`;
        markDone(2);
        goToStep(3);
    } else {
        alert('Erreur: ' + (j.detail || 'inconnue'));
    }
}

// ========== STEP 3: Commune ==========
async function loadStep3() {
    const r = await fetch(API + '/api/communes/all?limit=20');
    const d = await r.json();
    const communes = d.communes || [];
    const select = document.getElementById('commune-select');
    if (select) {
        select.innerHTML = '<option value="">-- Choisir --</option>' +
            communes.map(c => `<option value="${c.code_insee}">${c.nom} (${c.code_insee})</option>`).join('');
    }
}

async function submitStep3() {
    const code = document.getElementById('commune-select').value;
    if (!code) { alert('Sélectionnez une commune'); return; }
    const r = await fetch(API + `/api/communes/${code}`);
    const j = await r.json();
    if (r.ok) {
        document.getElementById('result-3').innerHTML = `
            <div class="result-box">
                <h3>📍 ${j.nom}</h3>
                <p><strong>Population:</strong> ${j.population?.toLocaleString() || 'N/A'}</p>
                <p><strong>Département:</strong> ${j.departement || 'N/A'}</p>
            </div>`;
        markDone(3);
        loadStep4();
        goToStep(4);
    }
}

// ========== STEP 4: Diagnostic territorial ==========
async function loadStep4() {
    const code = document.getElementById('commune-select').value;
    if (!code) return;
    const r = await fetch(API + `/api/communes/${code}/diagnostic-territorial`);
    const d = await r.json();
    const thematiques = d.thematiques_prioritaires || [];
    const html = thematiques.map(t => `
        <div class="badge badge-orange" style="margin: 4px; padding: 8px 12px; display: inline-block;">${t}</div>
    `).join('');
    document.getElementById('result-4').innerHTML = `
        <div class="result-box">
            <h3>🎯 Thématiques prioritaires</h3>
            <div>${html || 'Aucune thématique identifiée'}</div>
        </div>`;
}

// ========== STEP 5: Shortlist partenaires ==========
async function loadStep5() {
    const code = document.getElementById('commune-select').value;
    if (!code) return;
    const thematiques = Array.from(document.querySelectorAll('#result-4 .badge'))
        .map(b => b.textContent.trim());
    const params = new URLSearchParams({ commune: code, limit: '10' });
    if (thematiques.length) params.append('thematiques', thematiques.join(','));
    const r = await fetch(API + '/api/shortlist?' + params);
    const d = await r.json();
    const partners = d.partners || [];
    if (!partners.length) {
        document.getElementById('result-5').innerHTML = `
            <div class="result-box"><p>Aucun partenaire identifié pour cette commune.</p></div>`;
        return;
    }
    const html = partners.map(p => `
        <div class="partner-card" data-id="${p.id}" onclick="togglePartner(this, '${p.id}')" style="cursor: pointer; padding: 12px; border: 2px solid #e5e7eb; border-radius: 8px; margin-bottom: 8px;">
            <div style="font-weight: 600;">${p.nom}</div>
            <div style="font-size: 0.9em; color: #6b7280;">${p.activite_principale || p.type || ''}</div>
            <div style="margin-top: 6px;"><span class="badge badge-blue">Score: ${p.score}</span></div>
        </div>
    `).join('');
    document.getElementById('result-5').innerHTML = `
        <div style="margin-bottom: 12px;"><strong>${partners.length} partenaires potentiels</strong> — cliquez pour sélectionner</div>
        ${html}`;
}

function togglePartner(el, id) {
    el.classList.toggle('selected');
    if (el.classList.contains('selected')) {
        el.style.borderColor = '#10b981';
        el.style.background = '#f0fdf4';
        state.selected_partners.push(id);
    } else {
        el.style.borderColor = '#e5e7eb';
        el.style.background = 'white';
        state.selected_partners = state.selected_partners.filter(p => p !== id);
    }
}

async function submitStep5() {
    if (state.selected_partners.length === 0) {
        alert('Sélectionnez au moins 1 partenaire');
        return;
    }
    markDone(5);
    goToStep(6);
    loadStep6();
}

// ========== STEP 6: Cas inspirants ==========
async function loadStep6() {
    const thematiques = Array.from(document.querySelectorAll('#result-4 .badge'))
        .map(b => b.textContent.trim());
    const params = new URLSearchParams({ limit: '5' });
    let cas = [];
    try {
        const r = await fetch(API + '/api/cas-inspirants/match?' + params);
        if (r.ok) {
            const d = await r.json();
            cas = d.cas_inspirants || [];
        }
    } catch (e) {
        console.warn('Cas inspirants match endpoint error:', e);
    }
    // Fallback : si le match n'a rien donné ou a planté, essayer le listing brut
    if (cas.length === 0) {
        try {
            const r2 = await fetch(API + '/api/cas-inspirants?limit=5');
            if (r2.ok) {
                const d2 = await r2.json();
                cas = d2.cas_inspirants || [];
            }
        } catch (e2) {
            console.warn('Cas inspirants fallback error:', e2);
        }
    }
    if (!cas.length) {
        document.getElementById('result-6').innerHTML = `
            <div class="result-box"><p>Aucun cas inspirant trouvé.</p></div>`;
        return;
    }
    const html = cas.map(c => `
        <div class="partner-card" data-id="${c.id}" onclick="selectCasInspirant(this, '${c.id}')" style="cursor: pointer; padding: 16px; border: 2px solid #e5e7eb; border-radius: 8px; margin-bottom: 12px;">
            <div style="font-weight: 600; font-size: 1.05em;">${c.titre || c.name || 'Sans titre'}</div>
            <div style="color: #6b7280; font-size: 0.9em; margin: 6px 0;">${c.description || ''}</div>
            <div style="margin-top: 8px;">
                ${(c.thematiques || []).slice(0, 3).map(t => `<span class="badge badge-green" style="margin-right: 4px; font-size: 0.8em;">${t}</span>`).join('')}
                ${c.score ? `<span class="badge badge-blue" style="margin-right: 4px; font-size: 0.8em;">Score: ${c.score}</span>` : ''}
                ${c.budget_reel ? `<span class="badge badge-orange" style="font-size: 0.8em;">Budget: ${c.budget_reel.toLocaleString()} €</span>` : ''}
            </div>
        </div>
    `).join('');
    document.getElementById('result-6').innerHTML = `
        <div style="margin-bottom: 12px;"><strong>${cas.length} cas inspirants</strong> — sélectionnez celui qui vous inspire le plus</div>
        ${html}`;
}

function selectCasInspirant(el, id) {
    document.querySelectorAll('#result-6 .partner-card').forEach(c => {
        c.style.borderColor = '#e5e7eb';
        c.style.background = 'white';
    });
    el.style.borderColor = '#10b981';
    el.style.background = '#f0fdf4';
    state.selected_project = id;
}

async function submitStep6() {
    if (!state.selected_project) {
        alert('Sélectionnez un cas inspirant');
        return;
    }
    markDone(6);
    goToStep(7);
    loadStep7();
}

// ========== STEP 7: AAP ==========
async function loadStep7() {
    const r = await fetch(API + '/api/funding-sources');
    const d = await r.json();
    const sources = d.funding_sources || [];
    if (!sources.length) {
        document.getElementById('result-7').innerHTML = `
            <div class="result-box"><p>Aucun AAP disponible actuellement.</p></div>`;
        return;
    }
    const html = sources.map(f => {
        const deadline = f.deadline || 'Non précisée';
        const isUrgent = f.deadline && new Date(f.deadline) < new Date(Date.now() + 30*24*60*60*1000);
        const montant = f.amount_max ? `Jusqu'à ${f.amount_max.toLocaleString()} €` : (f.amount_min ? `À partir de ${f.amount_min.toLocaleString()} €` : 'Montant variable');
        const eligible = (f.eligibility_criteria || []).slice(0, 3).map(e => `<span class="badge badge-green" style="margin: 2px; font-size: 0.75em;">${e}</span>`).join(' ');
        return `
        <div class="partner-card" data-id="${f.id}" onclick="toggleAAP(this, '${f.id}')" style="cursor: pointer; padding: 16px; border: 2px solid #e5e7eb; border-radius: 8px; margin-bottom: 12px;">
            <div style="font-weight: 600; font-size: 1.1em; margin-bottom: 4px;">${f.name}</div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-bottom: 8px;">
                <span class="badge badge-orange">${f.type || 'AAP'}</span>
                <span style="color: ${isUrgent ? '#dc2626' : '#6b7280'}; font-size: 0.9em; font-weight: ${isUrgent ? 'bold' : 'normal'};">📅 Deadline : ${deadline}${isUrgent ? ' ⚠️' : ''}</span>
            </div>
            <div style="color: #6b7280; font-size: 0.9em; margin-bottom: 6px;">💰 ${montant}</div>
            ${eligible ? `<div>Éligibilité : ${eligible}</div>` : ''}
            ${f.description ? `<div style="margin-top: 8px; color: #4b5563; font-size: 0.9em;">${f.description.substring(0, 200)}${f.description.length > 200 ? '...' : ''}</div>` : ''}
            ${f.url ? `<div style="margin-top: 8px;"><a href="${f.url}" target="_blank" style="color: #3b82f6; text-decoration: none; font-size: 0.85em;">🔗 En savoir plus</a></div>` : ''}
        </div>`;
    }).join('');
    document.getElementById('result-7').innerHTML = `
        <div style="margin-bottom: 16px; padding: 12px; background: #fff7ed; border-radius: 8px;">
            <strong>📢 ${sources.length} appels à projets</strong> identifiés pour votre profil.
            <br><span style="font-size: 0.9em; color: #6b7280;">Cliquez sur un AAP pour l'ajouter à votre dossier (${state.selected_aaps.length} sélectionné(s))</span>
        </div>
        ${html}`;
}

function toggleAAP(el, id) {
    el.classList.toggle('selected');
    if (el.classList.contains('selected')) {
        el.style.borderColor = '#10b981';
        el.style.background = '#f0fdf4';
        state.selected_aaps.push(id);
    } else {
        el.style.borderColor = '#e5e7eb';
        el.style.background = 'white';
        state.selected_aaps = state.selected_aaps.filter(a => a !== id);
    }
}

async function submitStep7() {
    if (state.selected_aaps.length === 0) {
        alert('Sélectionnez au moins 1 AAP');
        return;
    }
    const r = await fetch(API + '/api/dossiers/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            club_id: state.club_id,
            project_id: state.selected_project,
            funding_source_ids: state.selected_aaps
        })
    });
    const j = await r.json();
    if (r.ok) {
        state.dossier_id = j.dossier_id;
        renderStep8(j);
        markDone(7);
        goToStep(8);
    } else {
        alert('Erreur: ' + (j.detail || 'inconnue'));
    }
}

// ========== STEP 8: Dossier final ==========
function renderStep8(j) {
    const profilLabels = {
        engaged: '🌟 Engaged (Mature)',
        emerging: '🌿 Emerging (En progression)',
        aware: '🌱 Aware (Démarrage)',
        novice: '🌰 Novice (Débutant)'
    };
    const profil = profilLabels[state.profile] || 'Non défini';
    document.getElementById('result-8').innerHTML = `
        <div style="background: linear-gradient(135deg, #f0fdf4 0%, #ecfeff 100%); padding: 32px; border-radius: 16px; border: 2px solid #10b981;">
            <h2 style="color: #059669; margin-bottom: 16px;">🎉 Votre dossier est prêt !</h2>
            <p style="font-size: 1.1em; color: #374151; margin-bottom: 24px;">
                Félicitations ! Vous avez parcouru les 8 étapes du parcours TerritoireSport.
                Voici un récapitulatif de votre projet à impact.
            </p>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px;">
                <div style="background: white; padding: 16px; border-radius: 8px; border-left: 4px solid #3b82f6;">
                    <div style="font-size: 0.85em; color: #6b7280;">Votre profil</div>
                    <div style="font-size: 1.1em; font-weight: bold; color: #111827;">${profil}</div>
                    <div style="font-size: 0.9em; color: #6b7280;">Score : ${state.score}/20</div>
                </div>
                <div style="background: white; padding: 16px; border-radius: 8px; border-left: 4px solid #10b981;">
                    <div style="font-size: 0.85em; color: #6b7280;">Partenaires</div>
                    <div style="font-size: 1.1em; font-weight: bold; color: #111827;">${state.selected_partners.length} sélectionné(s)</div>
                    <div style="font-size: 0.9em; color: #6b7280;">Sur la shortlist</div>
                </div>
                <div style="background: white; padding: 16px; border-radius: 8px; border-left: 4px solid #f59e0b;">
                    <div style="font-size: 0.85em; color: #6b7280;">AAP ciblés</div>
                    <div style="font-size: 1.1em; font-weight: bold; color: #111827;">${j.funding_sources.length} financement(s)</div>
                    <div style="font-size: 0.9em; color: #6b7280;">Identifiés pour vous</div>
                </div>
            </div>
            <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 24px;">
                <h3 style="margin: 0 0 12px 0; color: #111827;">📋 Contenu de votre dossier</h3>
                <ul style="margin: 0; padding-left: 20px; color: #4b5563; line-height: 1.8;">
                    <li><strong>Fiche club</strong> : identification, sport, territoire</li>
                    <li><strong>Diagnostic territorial</strong> : enjeux et thématiques de votre commune</li>
                    <li><strong>Évaluation maturité</strong> : profil, forces, axes de progression</li>
                    <li><strong>Cas inspirant de référence</strong> : projet modèle à adapter</li>
                    <li><strong>Shortlist de partenaires</strong> : ${state.selected_partners.length} contacts qualifiés</li>
                    <li><strong>Argumentaires AAP</strong> : ${j.funding_sources.length} dossiers adaptés</li>
                </ul>
            </div>
            <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 24px;">
                <a href="${j.download_url}" style="background: #10b981; color: white; padding: 14px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; display: inline-block;">📥 Télécharger mon dossier</a>
                <a href="mailto:contact@territoiresport.fr?subject=Demande%20d'accompagnement%20-%20Dossier%20${j.dossier_id}" style="background: #3b82f6; color: white; padding: 14px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; display: inline-block;">🤝 Demander un accompagnement</a>
                <button onclick="window.print()" style="background: white; color: #374151; padding: 14px 24px; border-radius: 8px; border: 2px solid #d1d5db; font-weight: 600; cursor: pointer;">🖨️ Imprimer</button>
            </div>
            <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 8px;">
                <h4 style="margin: 0 0 8px 0; color: #92400e;">📌 Prochaines étapes recommandées</h4>
                <ol style="margin: 0; padding-left: 24px; color: #78350f; line-height: 1.8;">
                    <li><strong>Semaine 1-2</strong> : prenez contact avec les ${state.selected_partners.length} partenaires sélectionnés pour présenter votre projet</li>
                    <li><strong>Semaine 3-4</strong> : adaptez le cas inspirant à votre territoire en impliquant vos partenaires</li>
                    <li><strong>Mois 2</strong> : finalisez votre dossier de candidature AAP avec les éléments collectés</li>
                    <li><strong>Mois 3</strong> : déposez votre demande avant la deadline du premier AAP</li>
                    <li><strong>En continu</strong> : documentez votre démarche pour la mesure d'impact</li>
                </ol>
            </div>
            <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid #e5e7eb; font-size: 0.85em; color: #6b7280;">
                <strong>Référence dossier</strong> : ${j.dossier_id}<br>
                <strong>Date de génération</strong> : ${new Date().toLocaleDateString('fr-FR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
            </div>
        </div>`;
}

// ========== UTILITIES ==========
function goToStep(n) {
    document.querySelectorAll('.step-card').forEach(s => s.classList.remove('active'));
    document.getElementById('step-' + n).classList.add('active');
    document.getElementById('step-' + n).scrollIntoView({ behavior: 'smooth', block: 'start' });
    if (n === 3) loadStep3();
    if (n === 5) loadStep5();
}

function markDone(n) {
    const indicator = document.getElementById('step-' + n + '-status');
    if (indicator) {
        indicator.textContent = '✅';
        indicator.style.color = '#10b981';
    }
}
