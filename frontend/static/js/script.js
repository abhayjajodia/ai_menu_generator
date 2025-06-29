document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('plan-form');
    const resultsDiv = document.getElementById('results');
    const errorDiv = document.getElementById('error-message');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Show loading indicator
        resultsDiv.innerHTML = '<div class="loading">Generating your menu...</div>';
        errorDiv.style.display = 'none';
        
        // Get form data
        const formData = {
            event_type: document.getElementById('event-type').value,
            cuisine: document.getElementById('cuisine').value,
            formality: document.getElementById('formality').value,
            guest_count: parseInt(document.getElementById('guest-count').value),
            service_type: document.querySelector('input[name="service-type"]:checked').value
        };
        
        try {
            const response = await fetch('/api/plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                showError(result.message || 'Server error occurred');
                return;
            }
            
            if (result.status === 'error') {
                showError(result.message);
                return;
            }
            
            // Display results
            displayResults(result);
            
        } catch (error) {
            showError(`Network error: ${error.message}`);
        }
    });
    
    function showError(message) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        resultsDiv.innerHTML = '';
    }
    
    function displayResults(result) {
        let html = `
            <div class="success-message">
                <h2>${result.message}</h2>
            </div>
            <div class="menu-section">
                <h3>Your Menu Plan</h3>
        `;
        
        // Display menu sections
        const sections = {
            appetizers: 'Appetizers',
            main_courses: 'Main Courses',
            desserts: 'Desserts',
            beverages: 'Beverages'
        };
        
        for (const [key, title] of Object.entries(sections)) {
            if (result.menu[key] && result.menu[key].length > 0) {
                html += `<h4>${title}</h4><ul>`;
                result.menu[key].forEach(item => {
                    html += `<li>${item}</li>`;
                });
                html += '</ul>';
            }
        }
        
        // Display preparation notes
        if (result.menu.preparation_notes) {
            html += `
                <h4>Preparation Notes</h4>
                <p>${result.menu.preparation_notes}</p>
            `;
        }
        
        html += '</div>'; // Close menu-section
        
        // Display grocery list if available
        if (result.grocery_list) {
            html += `
                <div class="grocery-section">
                    <h3>Shopping List</h3>
                    <ul>`;
            
            // Split grocery list into items
            const groceryItems = result.grocery_list.split('\n')
                .filter(item => item.trim().startsWith('-'))
                .map(item => item.replace(/^-/, '').trim());
            
            groceryItems.forEach(item => {
                html += `<li>${item}</li>`;
            });
            
            html += `
                    </ul>
                </div>
            `;
        }
        
        resultsDiv.innerHTML = html;
    }
});


// Form steps
// const formSteps = [
//     {
//         question: "What type of event is this?",
//         field: "event_type",
//         type: "select",
//         options: ["birthday", "wedding", "corporate", "family", "other"]
//     },
//     {
//         question: "What cuisine would you like?",
//         field: "cuisine",
//         type: "select",
//         options: ["italian", "indian", "mexican", "american", "japanese", "mediterranean", "other"]
//     },
//     {
//         question: "How formal is the event?",
//         field: "formality",
//         type: "select",
//         options: ["casual", "semi-formal", "formal"]
//     },
//     {
//         question: "How many guests will attend?",
//         field: "guest_count",
//         type: "number",
//         min: 1
//     },
//     {
//         question: "Any dietary restrictions?",
//         field: "dietary_restrictions",
//         type: "text",
//         placeholder: "e.g., vegetarian, gluten-free, none"
//     },
//     {
//         question: "Will you prepare food yourself?",
//         field: "service_type",
//         type: "select",
//         options: ["self", "catering"]
//     }
// ];

// let currentStep = 0;
// let formData = {};

// // Initialize the form
// function renderFormStep() {
//     const formContainer = document.getElementById('form-container');
//     const step = formSteps[currentStep];
    
//     let html = `
//         <div class="form-step active">
//             <p>${step.question}</p>
//     `;
    
//     if (step.type === 'select') {
//         html += `<select id="form-input">`;
//         step.options.forEach(option => {
//             html += `<option value="${option}">${option.charAt(0).toUpperCase() + option.slice(1)}</option>`;
//         });
//         html += `</select>`;
//     } else if (step.type === 'number') {
//         html += `<input type="number" id="form-input" min="${step.min || 1}" value="10">`;
//     } else {
//         html += `<input type="text" id="form-input" placeholder="${step.placeholder || ''}" value="none">`;
//     }
    
//     html += `
//         <button onclick="nextStep()">${currentStep === formSteps.length - 1 ? 'Finish' : 'Next'}</button>
//         </div>
//     `;
    
//     formContainer.innerHTML = html;
    
//     // Add user message to chat
//     addMessage(step.question, 'bot');
    
//     // Auto-focus the input
//     document.getElementById('form-input').focus();
// }

// function nextStep() {
//     const input = document.getElementById('form-input');
//     const step = formSteps[currentStep];
    
//     // Save response
//     formData[step.field] = input.value;
    
//     // Add user response to chat
//     addMessage(input.value, 'user');
    
//     // Move to next step or submit
//     if (currentStep < formSteps.length - 1) {
//         currentStep++;
//         renderFormStep();
//     } else {
//         submitForm();
//     }
// }

// function addMessage(text, sender) {
//     const chat = document.getElementById('chat-messages');
//     const message = document.createElement('div');
//     message.className = `message ${sender}-message`;
//     message.textContent = text;
//     chat.appendChild(message);
//     chat.scrollTop = chat.scrollHeight;
// }

// function submitForm() {
//     const formContainer = document.getElementById('form-container');
//     formContainer.innerHTML = `<div class="loading">Generating your perfect menu with DeepSeek AI...</div>`;
    
//     // Add thinking message to chat
//     addMessage("Generating your personalized menu...", 'bot');
    
//     // Send data to backend
//     fetch('/api/plan', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify(formData)
//     })
//     .then(response => response.json())
//     .then(data => {
//         if (data.status === "success") {
//             displayResults(data);
//         } else {
//             showError(data.message || "Unknown error occurred");
//         }
//     })
//     .catch(error => {
//         showError("Network error: " + error.message);
//     });
// }

// function displayResults(data) {
//     const results = document.getElementById('results');
//     results.style.display = 'block';
    
//     let html = `<div class="success">Successfully generated your event plan!</div>`;
    
//     // Menu section
//     if (data.menu && data.menu.courses) {
//         html += `<h2>Your Custom Menu</h2>`;
//         if (data.menu.menu_description) {
//             html += `<p class="menu-description">${data.menu.menu_description}</p>`;
//         }
        
//         data.menu.courses.forEach(course => {
//             html += `<h3>${course.name}</h3>`;
            
//             course.dishes.forEach(dish => {
//                 html += `
//                     <div class="dish-card">
//                         <h4>${dish.name}</h4>
//                         <p>${dish.description || "Delicious dish prepared to perfection"}</p>
//                     </div>
//                 `;
//             });
//         });
//     } else {
//         html += `<div class="error">Menu generation failed. Please try again.</div>`;
//     }
    
//     // Grocery section
//     if (data.grocery_list && data.service_type === "self") {
//         html += `<h2>Grocery List</h2>`;
        
//         if (data.grocery_list.ingredients && data.grocery_list.ingredients.length > 0) {
//             html += `<div class="ingredient-list">`;
//             data.grocery_list.ingredients.forEach(ingredient => {
//                 html += `
//                     <div class="ingredient-item">
//                         <strong>${ingredient.name}</strong>
//                         <div>Quantity: ${ingredient.quantity}</div>
//                         <div>Category: ${ingredient.category || "General"}</div>
//                     </div>
//                 `;
//             });
//             html += `</div>`;
//         }
        
//         if (data.grocery_list.prep_tips && data.grocery_list.prep_tips.length > 0) {
//             html += `<h3>Preparation Tips</h3><ul>`;
//             data.grocery_list.prep_tips.forEach(tip => {
//                 html += `<li>${tip}</li>`;
//             });
//             html += `</ul>`;
//         }
//     }
    
//     results.innerHTML = html;
    
//     // Add final message to chat
//     addMessage("Here's your personalized menu and planning details! 🎉", 'bot');
    
//     // Reset form container
//     document.getElementById('form-container').innerHTML = `
//         <button onclick="window.location.reload()">Plan Another Event</button>
//     `;
// }

// function showError(message) {
//     const formContainer = document.getElementById('form-container');
//     formContainer.innerHTML = `
//         <div class="error">${message}</div>
//         <button onclick="submitForm()">Try Again</button>
//         <button onclick="window.location.reload()">Start Over</button>
//     `;
    
//     addMessage("Sorry, something went wrong. Please try again.", 'bot');
// }

// // Start the form
// document.addEventListener('DOMContentLoaded', renderFormStep);