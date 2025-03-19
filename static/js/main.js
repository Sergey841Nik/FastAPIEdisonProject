// Получение элементов DOM
const loginBtn = document.getElementById('loginBtn');
const registerBtn = document.getElementById('registerBtn');
const predictBtn = document.getElementById('predictBtn');
const profileBtn = document.getElementById('profileBtn');
const adminBtn = document.getElementById('adminBtn');
const logoutBtn = document.getElementById('logoutBtn');
const authSection = document.getElementById('auth-section');
const registerSection = document.getElementById('register-section');
const profileSection = document.getElementById('profile-section');
const predictSection = document.getElementById('predict-section');
const adminSection = document.getElementById('admin-section');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const updateProfileForm = document.getElementById('updateProfileForm');
const imageInput = document.getElementById('imageInput');
const uploadBtn = document.getElementById('uploadBtn');
const resultDiv = document.getElementById('result');
const predictionResult = document.getElementById('predictionResult');
const processedImage = document.getElementById('processedImage');
const profileEmail = document.getElementById('profileEmail');
const profileName = document.getElementById('profileName');

// Отладочный код
console.log('Elements initialized:', {
    loginBtn,
    registerBtn,
    predictBtn,
    profileBtn,
    logoutBtn,
    authSection,
    registerSection,
    profileSection,
    predictSection,
    loginForm,
    registerForm,
    updateProfileForm,
    imageInput,
    uploadBtn,
    resultDiv,
    predictionResult,
    processedImage,
    profileEmail,
    profileName
});

// Токен авторизации
let authToken = localStorage.getItem('authToken');

// Функции для управления видимостью секций
const showSection = (sectionId) => {
    document.getElementById(sectionId).classList.remove('hidden');
};

const hideSection = (sectionId) => {
    document.getElementById(sectionId).classList.add('hidden');
};

// Функция для обновления состояния навигации
const updateNavigation = (isAuthenticated, isAdmin = false) => {
    loginBtn.classList.toggle('hidden', isAuthenticated);
    registerBtn.classList.toggle('hidden', isAuthenticated);
    profileBtn.classList.toggle('hidden', !isAuthenticated);
    adminBtn.classList.toggle('hidden', !isAdmin);
    logoutBtn.classList.toggle('hidden', !isAuthenticated);
};

// Обработчики событий для навигации
loginBtn.addEventListener('click', () => {
    showSection('auth-section');
    hideSection('register-section');
    hideSection('predict-section');
    hideSection('profile-section');
});

registerBtn.addEventListener('click', () => {
    console.log('Register button clicked');
    showSection('register-section');
    hideSection('auth-section');
    hideSection('predict-section');
    hideSection('profile-section');
});

profileBtn.addEventListener('click', async () => {
    if (!authToken) {
        alert('Пожалуйста, войдите в систему');
        return;
    }
    hideSection('auth-section');
    hideSection('register-section');
    hideSection('predict-section');
    showSection('profile-section');
    await loadProfile();
});

logoutBtn.addEventListener('click', () => {
    localStorage.removeItem('authToken');
    authToken = null;
    updateNavigation(false);
    hideSection('profile-section');
    hideSection('predict-section');
    showSection('auth-section');
});

predictBtn.addEventListener('click', () => {
    if (!authToken) {
        alert('Пожалуйста, войдите в систему');
        return;
    }
    hideSection('auth-section');
    hideSection('register-section');
    hideSection('profile-section');
    showSection('predict-section');
});

adminBtn.addEventListener('click', async () => {
    if (!authToken) {
        alert('Пожалуйста, войдите в систему');
        return;
    }
    hideSection('auth-section');
    hideSection('register-section');
    hideSection('predict-section');
    hideSection('profile-section');
    showSection('admin-section');
    await loadAdminData();
});

// Загрузка профиля пользователя
async function loadProfile() {
    try {
        const response = await fetch('/auth/user/me/', {
            headers: {
                'Authorization': `Bearer ${authToken}`,
            }
        });

        if (!response.ok) {
            throw new Error('Ошибка при загрузке профиля');
        }

        const userData = await response.json();
        profileEmail.textContent = userData.email;
        profileName.textContent = userData.name;
    } catch (error) {
        alert(error.message);
    }
}

// Функции для админ панели
async function loadAdminData() {
    try {
        await loadUsers();
    } catch (error) {
        alert(error.message);
    }
}

async function loadUsers() {
    try {
        const response = await fetch('/admin/users/', {
            headers: {
                'Authorization': `Bearer ${authToken}`,
            }
        });

        if (!response.ok) {
            throw new Error('Ошибка при загрузке пользователей');
        }

        const users = await response.json();
        const tbody = document.getElementById('usersTableBody');
        tbody.innerHTML = '';

        users.forEach(user => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${user.id}</td>
                <td>${user.name}</td>
                <td>${user.email}</td>
                <td><span class="user-status ${user.is_active ? 'active' : 'inactive'}">${user.is_active ? 'Активен' : 'Неактивен'}</span></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        alert(error.message);
    }
}

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
        
        // Проверяем админские права
        const userResponse = await fetch("/auth/user/me/", {
            headers: {
                'Authorization': `Bearer ${authToken}`,
            }
        });
        
        if (userResponse.ok) {
            const userData = await userResponse.json();
            updateNavigation(true, userData.is_admin);
        } else {
            updateNavigation(true, false);
        }
        
        hideSection('auth-section');
        showSection('predict-section');
    } catch (error) {
        alert(error.message);
    }
});

// Обработка формы регистрации
registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(registerForm);
    
    try {
        const response = await fetch("/auth/register/", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: formData.get('name'),
                email: formData.get('email'),
                password: formData.get('password'),
                confirm_password: formData.get('confirm_password')
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Ошибка регистрации");
        }
        
        alert('Регистрация успешна! Теперь вы можете войти.');
        showSection('auth-section');
        hideSection('register-section');
    } catch (error) {
        alert(error.message);
    }
});

// Обработка формы обновления профиля
updateProfileForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(updateProfileForm);
    
    try {
        const response = await fetch("/auth/user/me/update_user/", {
            method: "PUT",
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                new_email: formData.get('new_email') || null,
                new_name: formData.get('new_name') || null
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Ошибка обновления профиля");
        }
        
        alert('Профиль успешно обновлен!');
        await loadProfile();
        updateProfileForm.reset();
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
    updateNavigation(true);
    predictBtn.click();
} else {
    updateNavigation(false);
    showSection('auth-section');
} 