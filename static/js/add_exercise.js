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

function generateWeightsTable() {
    const numSets = parseInt(setsInput.value) || 0;

    if (numSets === 0) {
        weightsTable.innerHTML = '<p style="color: var(--gray); text-align: center;">Укажите количество подходов</p>';
        return;
    }

    let html = '';
    for (let i = 1; i <= numSets; i++) {
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
                    value="0"
                    required
                    placeholder="0"
                >
                <span class="weight-row-unit">кг</span>
            </div>
        `;
    }

    weightsTable.innerHTML = html;

    // Фокус на первом поле
    if (numSets > 0) {
        setTimeout(() => {
            const firstInput = document.getElementById('weight_1');
            if (firstInput) firstInput.focus();
        }, 100);
    }
}

if (setsInput) {
    generateWeightsTable();
    setsInput.addEventListener('input', generateWeightsTable);
    setsInput.addEventListener('change', generateWeightsTable);
}