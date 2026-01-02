// Workout Detail - Swipe to Reveal Actions

document.addEventListener('DOMContentLoaded', function() {
    const cardWrappers = document.querySelectorAll('.exercise-card-wrapper');

    cardWrappers.forEach(wrapper => {
        const content = wrapper.querySelector('.exercise-card-content');
        let startX = 0;
        let currentX = 0;
        let isDragging = false;

        // Touch events
        content.addEventListener('touchstart', handleTouchStart, { passive: true });
        content.addEventListener('touchmove', handleTouchMove, { passive: false });
        content.addEventListener('touchend', handleTouchEnd);

        // Mouse events (for desktop testing)
        content.addEventListener('mousedown', handleMouseDown);
        content.addEventListener('mousemove', handleMouseMove);
        content.addEventListener('mouseup', handleMouseEnd);
        content.addEventListener('mouseleave', handleMouseEnd);

        function handleTouchStart(e) {
            startX = e.touches[0].clientX;
            currentX = e.touches[0].clientX; // Initialize currentX
            isDragging = true;
        }

        function handleTouchMove(e) {
            if (!isDragging) return;

            currentX = e.touches[0].clientX;
            const diff = currentX - startX;

            // Only allow swiping left and only if moved more than 5px
            if (diff < -5 && diff > -160) {
                e.preventDefault();
                content.style.transition = 'none';
                content.style.transform = `translateX(${diff}px)`;
            }
        }

        function handleTouchEnd() {
            if (!isDragging) return;
            isDragging = false;

            const diff = currentX - startX;
            content.style.transition = 'transform 0.3s ease';

            // Only reveal actions if it was actually a swipe (moved more than 10px) and swiped more than 80px
            if (Math.abs(diff) > 10 && diff < -80) {
                wrapper.classList.add('swiped');
                content.style.transform = '';
            } else {
                wrapper.classList.remove('swiped');
                content.style.transform = '';
            }

            startX = 0;
            currentX = 0;
        }

        function handleMouseDown(e) {
            startX = e.clientX;
            currentX = e.clientX; // Initialize currentX
            isDragging = true;
            e.preventDefault();
        }

        function handleMouseMove(e) {
            if (!isDragging) return;

            currentX = e.clientX;
            const diff = currentX - startX;

            // Only allow swiping left and only if moved more than 5px
            if (diff < -5 && diff > -160) {
                content.style.transition = 'none';
                content.style.transform = `translateX(${diff}px)`;
            }
        }

        function handleMouseEnd() {
            if (!isDragging) return;
            isDragging = false;

            const diff = currentX - startX;
            content.style.transition = 'transform 0.3s ease';

            // Only reveal actions if it was actually a swipe (moved more than 10px) and swiped more than 80px
            if (Math.abs(diff) > 10 && diff < -80) {
                wrapper.classList.add('swiped');
                content.style.transform = '';
            } else {
                wrapper.classList.remove('swiped');
                content.style.transform = '';
            }

            startX = 0;
            currentX = 0;
        }
    });

    // Close swipe when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.exercise-card-wrapper')) {
            cardWrappers.forEach(wrapper => {
                wrapper.classList.remove('swiped');
            });
        }
    });
});

// Delete exercise with confirmation
function deleteExercise(exerciseId, exerciseName) {
    if (confirm(`Удалить упражнение "${exerciseName}"?`)) {
        // Send DELETE request
        fetch(`/workouts/exercise/${exerciseId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        })
        .then(response => {
            if (response.ok) {
                window.location.reload();
            } else {
                alert('Ошибка при удалении упражнения');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Ошибка при удалении упражнения');
        });
    }
}

// Get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}