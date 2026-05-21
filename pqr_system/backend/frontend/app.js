/**
 * PQR System - Frontend Application
 * Handles UI interactions, API calls, and real-time AI analysis.
 */

const API_BASE = '/api/v1';
let debounceTimer = null;

// === INITIALIZATION ===
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initRealTimeAnalysis();
});

// === TAB NAVIGATION ===
function initTabs() {
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            const tabId = `tab-${tab.dataset.tab}`;
            document.getElementById(tabId).classList.add('active');
            if (tab.dataset.tab === 'consultar') loadPQRs();
        });
    });
}

// === REAL-TIME ANALYSIS ===
function initRealTimeAnalysis() {
    const contenido = document.getElementById('contenido');
    contenido.addEventListener('input', () => {
        document.getElementById('charCount').textContent = contenido.value.length;
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            if (contenido.value.length >= 10) {
                analyzeRealTime(contenido.value);
            } else {
                document.getElementById('previewClassification').classList.add('hidden');
            }
        }, 800);
    });
}

async function analyzeRealTime(text) {
    try {
        const classResp = await fetch(`${API_BASE}/pqr/classify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ contenido: text })
        });
        if (classResp.ok) {
            const classification = await classResp.json();
            showPreviewClassification(classification);
        }
    } catch (error) {
        console.error('Real-time analysis error:', error);
    }
}

function showPreviewClassification(classification) {
    const div = document.getElementById('previewClassification');
    div.classList.remove('hidden');

    const typeColors = {
        'Petición': 'badge-info', 'Queja': 'badge-warning',
        'Reclamo': 'badge-danger', 'Sugerencia': 'badge-success'
    };

    document.getElementById('previewType').innerHTML = `
        <span class="badge ${typeColors[classification.pqr_type] || 'badge-info'}">${classification.pqr_type}</span>
        ${classification.sub_type ? `<span class="badge badge-purple" style="margin-left:0.5rem">${classification.sub_type}</span>` : ''}
        <span style="margin-left:0.5rem;font-size:0.8rem;color:#6b7280">Confianza: ${(classification.confidence * 100).toFixed(0)}%</span>
    `;

    document.getElementById('previewArea').innerHTML = `<span style="font-size:0.85rem">🏢 <strong>Área asignada:</strong> ${classification.assigned_area}</span>`;

    const priorityColors = { 'Urgente': 'badge-danger', 'Alta': 'badge-warning', 'Media': 'badge-info', 'Baja': 'badge-success' };
    document.getElementById('previewPriority').innerHTML = `
        <span style="font-size:0.85rem">⚡ <strong>Prioridad:</strong></span>
        <span class="badge ${priorityColors[classification.priority] || 'badge-info'}" style="margin-left:0.25rem">${classification.priority}</span>
    `;

    document.getElementById('previewTerm').innerHTML = `
        <span style="font-size:0.85rem">⏱️ <strong>Término:</strong> ${classification.response_term_days} días hábiles</span>
        <div style="font-size:0.75rem;color:#6b7280;margin-top:0.25rem">${classification.legal_basis}</div>
    `;
}

// === RADICAR PQR ===
async function radicarPQR() {
    const contenido = document.getElementById('contenido').value.trim();
    if (contenido.length < 10) {
        showToast('El contenido debe tener al menos 10 caracteres', 'error');
        return;
    }

    const data = {
        contenido: contenido,
        asunto: document.getElementById('asunto').value.trim() || null,
        ciudadano: getCitizenInfo(),
        archivos_adjuntos: getAttachedFiles(),
        canal_recepcion: 'Web'
    };

    showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/pqr`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error al radicar el PQR');
        }

        const result = await response.json();
        showPQRResult(result);
        showToast(`PQR radicado exitosamente: ${result.radicado}`, 'success');
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

function showPQRResult(result) {
    document.getElementById('aiPreview').classList.add('hidden');
    const resultDiv = document.getElementById('aiResult');
    resultDiv.classList.remove('hidden');

    const typeColors = { 'Petición': 'badge-info', 'Queja': 'badge-warning', 'Reclamo': 'badge-danger', 'Sugerencia': 'badge-success' };
    const priorityColors = { 'Urgente': 'badge-danger', 'Alta': 'badge-warning', 'Media': 'badge-info', 'Baja': 'badge-success' };
    const cl = result.classification;

    document.getElementById('resultDetails').innerHTML = `
        <div class="result-field"><span class="result-label">Radicado</span><span class="result-value" style="color:#1a56db;font-size:1rem">${result.radicado}</span></div>
        <div class="result-field"><span class="result-label">Fecha radicación</span><span class="result-value">${formatDate(result.fecha_radicado)}</span></div>
        <div class="result-field"><span class="result-label">Tipo</span><span class="result-value"><span class="badge ${typeColors[cl.pqr_type]}">${cl.pqr_type}</span> ${cl.sub_type ? `<span class="badge badge-purple" style="margin-left:0.25rem">${cl.sub_type}</span>` : ''}</span></div>
        <div class="result-field"><span class="result-label">Área asignada</span><span class="result-value">${cl.assigned_area}</span></div>
        <div class="result-field"><span class="result-label">Prioridad</span><span class="result-value"><span class="badge ${priorityColors[cl.priority]}">${cl.priority}</span></span></div>
        <div class="result-field"><span class="result-label">Término de respuesta</span><span class="result-value">${cl.response_term_days} días hábiles</span></div>
        <div class="result-field"><span class="result-label">Fecha límite</span><span class="result-value">${formatDate(result.fecha_limite_respuesta)}</span></div>
        <div class="result-field"><span class="result-label">Base legal</span><span class="result-value" style="font-size:0.8rem">${cl.legal_basis}</span></div>
        ${cl.summary ? `<div style="margin-top:1rem;padding:0.75rem;background:#f0f9ff;border-radius:8px;font-size:0.85rem"><strong>Resumen IA:</strong> ${cl.summary}</div>` : ''}
    `;
}

// === CONSULTAR PQRs ===
async function loadPQRs() {
    const type = document.getElementById('filterType').value;
    const status = document.getElementById('filterStatus').value;

    let url = `${API_BASE}/pqr?limit=50`;
    if (type) url += `&pqr_type=${type}`;
    if (status) url += `&status=${status}`;

    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Error al cargar PQRs');
        const pqrs = await response.json();
        renderPQRList(pqrs);
    } catch (error) {
        showToast('Error al cargar PQRs', 'error');
    }
}

function renderPQRList(pqrs) {
    const list = document.getElementById('pqrList');
    if (pqrs.length === 0) {
        list.innerHTML = '<div class="card text-center"><p class="text-muted">No hay PQRs radicados.</p></div>';
        return;
    }

    const typeColors = { 'Petición': 'badge-info', 'Queja': 'badge-warning', 'Reclamo': 'badge-danger', 'Sugerencia': 'badge-success' };
    const priorityColors = { 'Urgente': 'badge-danger', 'Alta': 'badge-warning', 'Media': 'badge-info', 'Baja': 'badge-success' };

    list.innerHTML = pqrs.map(pqr => {
        const cl = pqr.classification;
        return `
        <div class="pqr-item" onclick="showPQRDetail('${pqr.id}')">
            <div class="pqr-header">
                <span class="pqr-radicado">${pqr.radicado}</span>
                <span class="pqr-date">${formatDate(pqr.fecha_radicado)}</span>
            </div>
            <div class="pqr-body">${pqr.contenido.substring(0, 150)}${pqr.contenido.length > 150 ? '...' : ''}</div>
            <div class="pqr-meta">
                <span class="badge ${typeColors[cl.pqr_type]}">${cl.pqr_type}</span>
                <span class="badge ${priorityColors[cl.priority]}">${cl.priority}</span>
                <span class="pqr-meta-item">🏢 ${cl.assigned_area}</span>
                <span class="pqr-meta-item">⏱️ ${cl.response_term_days} días</span>
                <span class="pqr-meta-item">📊 ${(cl.confidence * 100).toFixed(0)}%</span>
            </div>
        </div>`;
    }).join('');
}

async function showPQRDetail(pqrId) {
    try {
        const response = await fetch(`${API_BASE}/pqr/${pqrId}`);
        if (!response.ok) throw new Error('PQR no encontrado');
        const pqr = await response.json();

        // Switch to copilot tab and fill data
        document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        document.querySelector('[data-tab="copiloto"]').classList.add('active');
        document.getElementById('tab-copiloto').classList.add('active');

        document.getElementById('copilotPqrId').value = pqr.id;
        document.getElementById('copilotType').value = pqr.classification.pqr_type;
        document.getElementById('copilotContenido').value = pqr.contenido;

        showToast(`PQR ${pqr.radicado} cargado en el copiloto`, 'info');
    } catch (error) {
        showToast('Error al cargar detalle del PQR', 'error');
    }
}

// === COPILOT ===
async function generateCopilotResponse() {
    const contenido = document.getElementById('copilotContenido').value.trim();
    if (!contenido) {
        showToast('Ingrese el contenido del PQR', 'error');
        return;
    }

    const request = {
        pqr_id: document.getElementById('copilotPqrId').value || 'N/A',
        pqr_contenido: contenido,
        pqr_type: document.getElementById('copilotType').value,
        funcionario_notas: document.getElementById('copilotNotas').value.trim() || null,
        tono: document.getElementById('copilotTono').value
    };

    showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/copilot/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request)
        });

        if (!response.ok) throw new Error('Error al generar respuesta');
        const result = await response.json();
        showCopilotResult(result);
        showToast('Borrador generado exitosamente', 'success');
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

function showCopilotResult(result) {
    const div = document.getElementById('copilotResult');

    let sourcesHtml = '';
    if (result.fuentes_utilizadas && result.fuentes_utilizadas.length > 0) {
        sourcesHtml = `<div class="copilot-sources"><strong>📚 Fuentes utilizadas:</strong><div style="margin-top:0.5rem">${result.fuentes_utilizadas.map(s => `<span class="copilot-source">📖 ${s}</span>`).join('')}</div></div>`;
    }

    let suggestionsHtml = '';
    if (result.sugerencias_adicionales && result.sugerencias_adicionales.length > 0) {
        suggestionsHtml = `<div class="copilot-suggestions"><strong>💡 Sugerencias:</strong>${result.sugerencias_adicionales.map(s => `<div class="copilot-suggestion">⚠️ ${s}</div>`).join('')}</div>`;
    }

    div.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem">
            <span class="badge ${result.requires_review ? 'badge-warning' : 'badge-success'}">${result.requires_review ? '⚠️ Requiere revisión' : '✅ Listo'}</span>
            <span style="font-size:0.85rem;color:#6b7280">Confianza: <strong>${(result.confidence_score * 100).toFixed(0)}%</strong></span>
        </div>
        <div class="copilot-draft">${result.borrador_respuesta}</div>
        ${sourcesHtml}
        ${suggestionsHtml}
        <button class="btn btn-secondary" style="margin-top:1rem;width:100%" onclick="copyDraft()">📋 Copiar borrador al portapapeles</button>
    `;
}

function copyDraft() {
    const draft = document.querySelector('.copilot-draft');
    if (draft) {
        navigator.clipboard.writeText(draft.textContent).then(() => {
            showToast('Borrador copiado al portapapeles', 'success');
        }).catch(() => {
            showToast('Error al copiar', 'error');
        });
    }
}

// === HELPER FUNCTIONS ===
function getCitizenInfo() {
    return {
        nombre_completo: document.getElementById('nombre').value.trim() || null,
        tipo_documento: document.getElementById('tipoDoc').value || null,
        numero_documento: document.getElementById('numDoc').value.trim() || null,
        email: document.getElementById('email').value.trim() || null,
        telefono: document.getElementById('telefono').value.trim() || null,
        direccion: document.getElementById('direccion').value.trim() || null,
        municipio: document.getElementById('municipio').value.trim() || null,
        departamento: document.getElementById('departamento').value.trim() || null
    };
}

function getAttachedFiles() {
    const input = document.getElementById('archivos');
    if (input.files) {
        return Array.from(input.files).map(f => f.name);
    }
    return [];
}

function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString('es-CO', { year: 'numeric', month: 'long', day: 'numeric' });
}

function showLoading(show) {
    const overlay = document.getElementById('loading');
    if (show) {
        overlay.classList.remove('hidden');
    } else {
        overlay.classList.add('hidden');
    }
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.remove();
    }, 4000);
}
