// Тут буде ваш JavaScript код
document.addEventListener('DOMContentLoaded', function() {
    console.log('Game Library ready!');
    
    // Приклад: Плавна прокрутка для якорних посилань
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                window.scrollTo({
                    top: target.offsetTop - 70,
                    behavior: 'smooth'
                });
            }
        });
    });
});