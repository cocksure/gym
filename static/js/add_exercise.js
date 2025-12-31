// Add Exercise Page JavaScript

function selectExercise(id, name, gifUrl) {
    // Убираем предыдущий выбор
    document.querySelectorAll('.exercise-selectable').forEach(el => {
        el.classList.remove('selected');
    });

    // Помечаем текущий выбор
    event.currentTarget.classList.add('selected');

    // Показываем форму
    const formCard = document.getElementById('exercise-form-card');
    if (formCard) {
        formCard.classList.remove('hidden');
    }

    // Заполняем форму
    document.getElementById('exercise-id').value = id;

    const selectedName = document.getElementById('selected-name');
    selectedName.textContent = name;
    selectedName.classList.remove('hidden');

    // Скрываем подсказку
    const preview = document.getElementById('selected-exercise');
    const hint = preview.querySelector('p');
    if (hint) hint.style.display = 'none';

    const mediaContainer = document.getElementById('selected-media');
    if (gifUrl) {
        // Проверяем это видео или изображение
        if (gifUrl.includes('.mp4') || gifUrl.includes('video')) {
            mediaContainer.innerHTML = `<video autoplay loop muted playsinline style="width: 100%; border-radius: 8px; margin-top: 0.5rem;">
                <source src="${gifUrl}" type="video/mp4">
            </video>`;
        } else {
            mediaContainer.innerHTML = `<img src="${gifUrl}" alt="${name}" style="width: 100%; border-radius: 8px; margin-top: 0.5rem;">`;
        }
    } else {
        mediaContainer.innerHTML = '';
    }

    // Прокрутка к форме на мобильных
    if (window.innerWidth <= 1024) {
        document.getElementById('exercise-form').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Генерация таблицы весов
const setsInput = document.getElementById('id_sets');
const weightsTable = document.getElementById('weights-table');
const exerciseTypeSelect = document.getElementById('exercise_type');

// Проверяем режим редактирования
const isEditing = window.editingExerciseData !== undefined;
const editData = isEditing ? window.editingExerciseData : null;

function generateWeightsTable() {
    const numSets = parseInt(setsInput.value) || 0;
    const exerciseType = isEditing ? editData.type : (exerciseTypeSelect ? exerciseTypeSelect.value : 'NORMAL');

    if (numSets === 0) {
        weightsTable.innerHTML = '<p style="color: var(--gray); text-align: center;">Укажите количество подходов</p>';
        return;
    }

    let html = '';

    if (exerciseType === 'DROPSET') {
        // Для дроп-сета: несколько весов на подход
        html += '<div class="dropset-info" style="margin-bottom: 1rem; padding: 0.75rem; background: rgba(239, 68, 68, 0.1); border-radius: 8px; border-left: 4px solid #ef4444;">';
        html += '<small style="color: #dc2626;"><i class="fas fa-fire"></i> <strong>Дроп-сет:</strong> Укажите веса через запятую (например: 10, 5, 2.5)</small>';
        html += '</div>';

        for (let i = 1; i <= numSets; i++) {
            // Получаем текущие веса для этого подхода при редактировании
            const currentSetWeights = (isEditing && editData.weights[i - 1]) ? editData.weights[i - 1] : [];
            const weightsValue = currentSetWeights.length > 0 ? currentSetWeights.join(', ') : '';

            html += `
                <div class="weight-row dropset-row">
                    <span class="weight-row-label">Подход ${i}:</span>
                    <input
                        type="text"
                        name="dropset_${i}"
                        id="dropset_${i}"
                        class="form-control dropset-input"
                        placeholder="10, 5, 2.5"
                        value="${weightsValue}"
                        required
                    >
                    <span class="weight-row-unit">кг</span>
                </div>
            `;
        }
    } else {
        // Обычное упражнение или суперсет
        if (exerciseType === 'SUPERSET') {
            html += '<div class="superset-info" style="margin-bottom: 1rem; padding: 0.75rem; background: rgba(16, 185, 129, 0.1); border-radius: 8px; border-left: 4px solid #10b981;">';
            html += '<small style="color: #059669;"><i class="fas fa-bolt"></i> <strong>Суперсет:</strong> После добавления можете сразу добавить следующее упражнение</small>';
            html += '</div>';
        }

        for (let i = 1; i <= numSets; i++) {
            // Получаем текущий вес для этого подхода при редактировании
            const currentWeight = (isEditing && editData.weights[i - 1] !== undefined) ? editData.weights[i - 1] : 0;

            html += `
                <div class="weight-row">
                    <span class="weight-row-label">Подход ${i}:</span>
                    <input
                        type="number"
                        step="0.5"
                        name="weight_${i}"
                        id="weight_${i}"
                        class="form-control"
                        min="0"
                        value="${currentWeight}"
                        required
                        placeholder="0"
                    >
                    <span class="weight-row-unit">кг</span>
                </div>
            `;
        }
    }

    weightsTable.innerHTML = html;

    // Фокус на первом поле
    if (numSets > 0) {
        setTimeout(() => {
            const firstInput = exerciseType === 'DROPSET' ?
                document.getElementById('dropset_1') :
                document.getElementById('weight_1');
            if (firstInput) firstInput.focus();
        }, 100);
    }
}

if (setsInput) {
    generateWeightsTable();
    setsInput.addEventListener('input', generateWeightsTable);
    setsInput.addEventListener('change', generateWeightsTable);
}

if (exerciseTypeSelect) {
    exerciseTypeSelect.addEventListener('change', generateWeightsTable);
}