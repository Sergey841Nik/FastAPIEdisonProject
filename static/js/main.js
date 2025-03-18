// Получение элементов DOM
const loginBtn = document.getElementById('loginBtn');
const registerBtn = document.getElementById('registerBtn');
const predictBtn = document.getElementById('predictBtn');
const authSection = document.getElementById('auth-section');
const predictSection = document.getElementById('predict-section');
const loginForm = document.getElementById('loginForm');
const imageInput = document.getElementById('imageInput');
const uploadBtn = document.getElementById('uploadBtn');
const resultDiv = document.getElementById('result');
const predictionResult = document.getElementById('predictionResult');
const processedImage = document.getElementById('processedImage');

// Токен авторизации
let authToken = localStorage.getItem('authToken');

// Функции для управления видимостью секций
const showSection = (sectionId) => {
    document.getElementById(sectionId).classList.remove('hidden');
};

const hideSection = (sectionId) => {
    document.getElementById(sectionId).classList.add('hidden');
};

// Обработчики событий для навигации
loginBtn.addEventListener('click', () => {
    showSection('auth-section');
    hideSection('predict-section');
});

registerBtn.addEventListener('click', () => {
    // TODO: Добавить форму регистрации
    alert('Функция регистрации в разработке');
});

predictBtn.addEventListener('click', () => {
    if (!authToken) {
        alert('Пожалуйста, войдите в систему');
        return;
    }
    hideSection('auth-section');
    showSection('predict-section');
});

// Обработка формы входа
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(loginForm);
    
    try {
        const response = await fetch("/auth/login/", {
            method: "POST",
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Ошибка авторизации");
        }
        
        const data = await response.json();
        authToken = data.access_token;
        localStorage.setItem("authToken", authToken);
        hideSection('auth-section');
        showSection('predict-section');
    } catch (error) {
        alert(error.message);
    }
});

// Обработка загрузки изображения
uploadBtn.addEventListener('click', async () => {
    const file = imageInput.files[0];
    if (!file) {
        alert('Пожалуйста, выберите изображение');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/predictions/predict/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
            },
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка при получении предсказания');
        }

        const data = await response.json();
        predictionResult.textContent = JSON.stringify(data.detections, null, 2);
        processedImage.src = `data:image/jpeg;base64,${data.processed_image}`;
        resultDiv.classList.remove('hidden');
    } catch (error) {
        alert(error.message);
    }
});

// Проверка авторизации при загрузке страницы
if (authToken) {
    predictBtn.click();
} 