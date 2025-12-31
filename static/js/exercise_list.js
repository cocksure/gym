// Exercise List Page JavaScript

// Функция для добавления упражнения в тренировку
function addToWorkout(exerciseId) {
    // Можно добавить функционал выбора тренировки
    const workoutId = getCurrentWorkoutId(); // Нужно будет реализовать
    if (workoutId) {
        window.location.href = `/workout/${workoutId}/add-exercise/${exerciseId}/`;
    } else {
        // Если нет активной тренировки, предложить создать новую
        if (confirm('Сначала создайте тренировку. Перейти к созданию тренировки?')) {
            window.location.href = "/workout/create/";
        }
    }
}

// Функция для показа деталей упражнения
function showExerciseDetails(exerciseId) {
    // Здесь можно добавить AJAX запрос для получения детальной информации
    fetch(`/api/exercises/${exerciseId}/`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('modalTitle').textContent = data.name;
            document.getElementById('modalBody').innerHTML = `
                <div class="mb-3">
                    ${data.gif ? `
                        <div class="media-container mb-2">
                            ${data.gif.includes('.mp4') || data.gif.includes('video') ?
                                `<video class="exercise-media" controls>
                                    <source src="${data.gif}" type="video/mp4">
                                </video>` :
                                `<img class="exercise-media" src="${data.gif}" alt="${data.name}">`
                            }
                        </div>
                    ` : ''}
                </div>
                <div class="mb-3">
                    <h4>Детали:</h4>
                    <p><strong>Категория:</strong> ${data.category_name || 'Не указана'}</p>
                    <p><strong>Группа мышц:</strong> ${data.muscle_group || 'Не указана'}</p>
                    <p><strong>Сложность:</strong> ${data.difficulty_display || 'Не указана'}</p>
                    <p><strong>Оборудование:</strong> ${data.equipment || 'Не требуется'}</p>
                </div>
                ${data.description ? `
                    <div class="mb-3">
                        <h4>Описание:</h4>
                        <p>${data.description}</p>
                    </div>
                ` : ''}
                <div class="d-flex gap-2">
                    <button onclick="addToWorkout(${exerciseId})" class="btn btn-success">
                        <i class="fas fa-plus"></i> Добавить в тренировку
                    </button>
                    <button onclick="closeModal()" class="btn btn-outline">
                        Закрыть
                    </button>
                </div>
            `;
            document.getElementById('exerciseModal').style.display = 'flex';
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Не удалось загрузить информацию об упражнении');
        });
}

// Функция для закрытия модального окна
function closeModal() {
    document.getElementById('exerciseModal').style.display = 'none';
}

// Получение ID текущей тренировки (заглушка)
function getCurrentWorkoutId() {
    // Реализуйте логику получения текущей активной тренировки
    return null;
}

// Закрытие модального окна при клике вне его
document.addEventListener('click', function(event) {
    const modal = document.getElementById('exerciseModal');
    if (modal && event.target === modal) {
        closeModal();
    }
});