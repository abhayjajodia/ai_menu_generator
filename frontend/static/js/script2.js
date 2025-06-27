// Form steps
const formSteps = [
    {
        question: "What type of event is this?",
        field: "event_type",
        type: "select",
        options: ["birthday", "wedding", "corporate", "family", "other"]
    },
    {
        question: "What cuisine would you like?",
        field: "cuisine",
        type: "select",
        options: ["italian", "indian", "mexican", "american", "japanese", "other"]
    },
    {
        question: "How formal is the event?",
        field: "formality",
        type: "select",
        options: ["casual", "semi-formal", "formal"]
    },
    {
        question: "How many guests will attend?",
        field: "guest_count",
        type: "number",
        min: 1
    },
    {
        question: "Any dietary restrictions?",
        field: "dietary_restrictions",
        type: "text",
        placeholder: "e.g., vegetarian, gluten-free, none"
    },
    {
        question: "Will you prepare food yourself?",
        field: "service_type",
        type: "select",
        options: ["self", "catering"]
    }
];

let currentStep = 0;
let formData = {};

// Initialize the form
function renderFormStep() {
    const formContainer = document.getElementById('form-container');
    const step = formSteps[currentStep];
    
    let html = `
        <div class="form-step active">
            <p style="margin-right: 10px; font-weight: 500;">${step.question}</p>
    `;
    
    if (step.type === 'select') {
        html += `<select id="form-input">`;
        step.options.forEach(option => {
            html += `<option value="${option}">${option.charAt(0).toUpperCase() + option.slice(1)}</option>`;
        });
        html += `</select>`;
    } else if (step.type === 'number') {
        html += `<input type="number" id="form-input" min="${step.min || 1}" value="10">`;
    } else {
        html += `<input type="text" id="form-input" placeholder="${step.placeholder || ''}">`;
    }
    
    html += `
        <button onclick="nextStep()">${currentStep === formSteps.length - 1 ? 'Finish' : 'Next'}</button>
        </div>
    `;
    
    formContainer.innerHTML = html;
    
    // Add user message to chat
    addMessage(step.question, 'bot');
    
    // Auto-focus the input
    document.getElementById('form-input').focus();
}

function nextStep() {
    const input = document.getElementById('form-input');
    const step = formSteps[currentStep];
    
    // Save response
    formData[step.field] = input.value;
    
    // Add user response to chat
    addMessage(input.value, 'user');
    
    // Move to next step or submit
    if (currentStep < formSteps.length - 1) {
        currentStep++;
        renderFormStep();
    } else {
        submitForm();
    }
}

function addMessage(text, sender) {
    const chat = document.getElementById('chat-messages');
    const message = document.createElement('div');
    message.className = `message ${sender}-message`;
    message.textContent = text;
    chat.appendChild(message);
    chat.scrollTop = chat.scrollHeight;
}

function submitForm() {
    const formContainer = document.getElementById('form-container');
    formContainer.innerHTML = `
        <div class="loading">Generating your perfect menu with DeepSeek AI...</div>
    `;
    
    // Add thinking message to chat
    addMessage("Generating your personalized menu...", 'bot');
    
    // Send data to backend
    fetch('/api/plan', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        displayResults(data);
    })
    .catch(error => {
        addMessage("Sorry, something went wrong. Please try again later.", 'bot');
        console.error('Error:', error);
        formContainer.innerHTML = `<button onclick="window.location.reload()">Try Again</button>`;
    });
}

function displayResults(data) {
    const results = document.getElementById('results');
    results.style.display = 'block';
    
    let html = '';
    
    // Check if menu data exists
    if (data.menu && data.menu.menu_description && data.menu.courses) {
        html += `
            <h2>Your Custom Menu</h2>
            <p class="menu-description">${data.menu.menu_description}</p>
        `;
        
        // Display menu courses
        data.menu.courses.forEach(course => {
            html += `
                <h3>${course.name}</h3>
            `;
            
            course.dishes.forEach(dish => {
                html += `
                    <div class="dish-card">
                        <h4>${dish.name}</h4>
                        <p>${dish.description || "A delicious dish prepared to perfection"}</p>
                    </div>
                `;
            });
        });
    } else {
        html += `
            <div class="error">
                <h2>⚠️ Menu Generation Failed</h2>
                <p>We couldn't generate a menu. Please try again with different parameters.</p>
                <p>Error details: ${JSON.stringify(data)}</p>
            </div>
        `;
    }
    
    // Display grocery list if available
    if (data.grocery_list && data.grocery_list.ingredients) {
        html += `
            <div class="grocery-section">
                <h2>Grocery List</h2>
                <div class="ingredient-list">
                    <ul>
        `;
        
        data.grocery_list.ingredients.forEach(ingredient => {
            html += `
                <li><strong>${ingredient.name}</strong>: ${ingredient.quantity} (${ingredient.category || "uncategorized"})</li>
            `;
        });
        
        html += `
                    </ul>
                </div>
        `;
        
        if (data.grocery_list.prep_tips) {
            html += `
                <h3>Preparation Tips</h3>
                <ul class="tips-list">
            `;
            
            data.grocery_list.prep_tips.forEach(tip => {
                html += `<li>${tip}</li>`;
            });
            
            html += `</ul>`;
        }
        
        html += `</div>`;
    }
    
    results.innerHTML = html;
    
    // Add final message to chat
    addMessage("Here's your personalized menu and planning details! 🎉", 'bot');
    
    // Reset form container
    document.getElementById('form-container').innerHTML = `
        <button onclick="window.location.reload()">Plan Another Event</button>
    `;
}

// Start the form when page loads
document.addEventListener('DOMContentLoaded', renderFormStep);