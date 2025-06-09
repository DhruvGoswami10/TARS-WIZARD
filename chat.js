// chat.js

document.addEventListener('DOMContentLoaded', () => {
    // Ensure Firebase is initialized before accessing its services
    if (typeof firebase === 'undefined' || !firebase.app()) {
        console.error("Firebase not initialized. Ensure script.js runs before chat.js");
        return;
    }

    const auth = firebase.auth();
    const functions = firebase.functions(); // Use compat version

    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const loadingIndicator = document.getElementById('loading-indicator');
    const errorMessage = document.getElementById('error-message');

    // Function to add a message to the chat display
    function addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender); // 'user' or 'assistant'
        messageDiv.textContent = text;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to bottom
    }

    // Function to handle sending a message
    async function sendMessage() {
        const messageText = userInput.value.trim();
        if (!messageText) return; // Don't send empty messages

        addMessage('user', messageText);
        userInput.value = ''; // Clear input
        loadingIndicator.style.display = 'block';
        errorMessage.textContent = ''; // Clear previous errors
        sendButton.disabled = true;
        userInput.disabled = true;

        try {
            // Prepare the callable function
            const callChatAPI = functions.httpsCallable('callChatAPI'); // Ensure this function exists in Firebase Functions

            // Call the function with the user's message
            const result = await callChatAPI({ message: messageText });

            // Display TARS's response
            if (result.data && result.data.reply) {
                addMessage('assistant', result.data.reply);
            } else {
                throw new Error("Invalid response from TARS.");
            }

        } catch (error) {
            console.error("Error calling chat function:", error);
            errorMessage.textContent = `Error: ${error.message || 'Could not get response from TARS.'}`;
            // Optionally add an error message to the chat
            // addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
        } finally {
            loadingIndicator.style.display = 'none';
            sendButton.disabled = false;
            userInput.disabled = false;
            userInput.focus(); // Set focus back to input
        }
    }

    // Event listeners
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }

    if (userInput) {
        userInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                sendMessage();
            }
        });
    }

    // Initial focus on input
    if (userInput) {
        userInput.focus();
    }
});
