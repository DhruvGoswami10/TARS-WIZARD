"use strict";
var _a;
Object.defineProperty(exports, "__esModule", { value: true });
exports.generateTarsLog = exports.callChatAPI = exports.addUserToDatabase = void 0;
const functions = require("firebase-functions/v1");
const admin = require("firebase-admin");
const cors = require("cors");
const openai_1 = require("openai"); // Import OpenAI
// Initialize Firebase Admin SDK
admin.initializeApp();
// Configure CORS options
const corsHandler = cors({ origin: 'http://127.0.0.1:5501' }); // Remember to update for production
// Initialize OpenAI client
// Get the API key from Firebase environment configuration
const openaiApiKey = (_a = functions.config().openai) === null || _a === void 0 ? void 0 : _a.key;
let openai = null;
if (openaiApiKey) {
    openai = new openai_1.default({ apiKey: openaiApiKey });
}
else {
    console.error("OpenAI API key not found in Firebase function configuration. Set it using `firebase functions:config:set openai.key=\"YOUR_API_KEY\"`");
}
// Trigger when a new user is created
exports.addUserToDatabase = functions.auth.user().onCreate(async (user) => {
    if (!user) {
        console.error('No user object found!');
        return null;
    }
    // Log user data for debugging purposes
    console.log('User created:', user);
    try {
        // Add the user to the Firebase Realtime Database
        await admin.database().ref(`/users/${user.uid}`).set({
            email: user.email || null,
            createdAt: new Date().toISOString(),
        });
        console.log(`User ${user.uid} added to database successfully.`);
        return null;
    }
    catch (error) {
        console.error('Error adding user to database:', error);
        return null;
    }
});
// Define the callChatAPI function as an onRequest function
exports.callChatAPI = functions.https.onRequest((request, response) => {
    corsHandler(request, response, async () => {
        var _a, _b, _c, _d, _e, _f;
        if (request.method !== 'POST') {
            response.status(405).send('Method Not Allowed');
            return;
        }
        // Check if OpenAI client is initialized
        if (!openai) {
            console.error('OpenAI client not initialized due to missing API key.');
            response.status(500).json({ error: 'Chat service configuration error.' });
            return;
        }
        const userMessage = (_a = request.body.data) === null || _a === void 0 ? void 0 : _a.message;
        if (!userMessage) {
            console.error('No message provided in request body.');
            response.status(400).json({ error: 'No message provided.' });
            return;
        }
        try {
            console.log("Received message:", userMessage);
            // --- Call OpenAI API --- 
            const completion = await openai.chat.completions.create({
                model: "gpt-3.5-turbo",
                messages: [
                    { role: "system", content: "You are TARS, a helpful assistant from the movie Interstellar. Respond concisely and helpfully, sometimes with a bit of dry humor like the character." },
                    { role: "user", content: userMessage }
                ],
                max_tokens: 150, // Adjust as needed
            });
            const reply = (_d = (_c = (_b = completion.choices[0]) === null || _b === void 0 ? void 0 : _b.message) === null || _c === void 0 ? void 0 : _c.content) === null || _d === void 0 ? void 0 : _d.trim();
            if (!reply) {
                console.error('No reply content received from OpenAI.');
                throw new Error('Failed to get valid response from AI.');
            }
            // --- End OpenAI API Call ---
            console.log("Sending reply:", reply);
            response.status(200).json({ data: { reply: reply } });
        }
        catch (error) {
            console.error('Error calling OpenAI or processing chat request:', error);
            let errorMessage = 'Failed to get response from TARS.';
            if (error.response) {
                // Log more details if available from OpenAI error
                console.error('OpenAI API Error Status:', error.response.status);
                console.error('OpenAI API Error Data:', error.response.data);
                errorMessage = `AI service error: ${((_f = (_e = error.response.data) === null || _e === void 0 ? void 0 : _e.error) === null || _f === void 0 ? void 0 : _f.message) || error.message}`;
            }
            else {
                errorMessage = `Error: ${error.message}`;
            }
            response.status(500).json({ error: errorMessage });
        }
    });
});
// New HTTPS Callable function to generate and store a TARS log
exports.generateTarsLog = functions.https.onCall(async (data, context) => {
    var _a, _b, _c;
    // Check if OpenAI client is initialized
    if (!openai) {
        console.error('OpenAI client not initialized.');
        throw new functions.https.HttpsError('internal', 'AI service configuration error.');
    }
    // Optional: Check if the user is authenticated (though the function itself adds the log)
    // if (!context.auth) {
    //     throw new functions.https.HttpsError('unauthenticated', 'The function must be called while authenticated.');
    // }
    // Prompt for OpenAI
    const logPrompt = "Generate a short, TARS-like log entry (max 20 words). It could be about system status, observations, user interactions (anonymized), or a dry humorous thought. Examples: 'Analyzing meme quality... Approved.', 'No solar flares today. Boring.', 'User @explorer123 accessed downloads.', 'Recalibrating humor circuits.'";
    try {
        console.log("Generating TARS log entry...");
        // Call OpenAI API
        const completion = await openai.chat.completions.create({
            model: "gpt-3.5-turbo",
            messages: [
                { role: "system", content: "You are TARS from Interstellar. Generate log entries based on the prompt." },
                { role: "user", content: logPrompt }
            ],
            max_tokens: 30,
            temperature: 0.8, // Allow for some creativity
        });
        const logMessage = (_c = (_b = (_a = completion.choices[0]) === null || _a === void 0 ? void 0 : _a.message) === null || _b === void 0 ? void 0 : _b.content) === null || _c === void 0 ? void 0 : _c.trim();
        if (!logMessage) {
            console.error('No log message content received from OpenAI.');
            throw new Error('Failed to get valid log message from AI.');
        }
        // Clean up potential quotes or extra formatting from the AI response
        const cleanedLogMessage = logMessage.replace(/^"|"$/g, ''); // Remove surrounding quotes
        console.log("Generated log:", cleanedLogMessage);
        // Write the log to Firebase Realtime Database
        const logData = {
            message: cleanedLogMessage,
            timestamp: admin.database.ServerValue.TIMESTAMP
        };
        await admin.database().ref('/tarsLogs').push(logData);
        console.log("Log entry saved to database.");
        return { success: true, message: cleanedLogMessage };
    }
    catch (error) {
        console.error('Error generating or saving TARS log:', error);
        // Throw an HttpsError for the client
        throw new functions.https.HttpsError('internal', `Failed to generate TARS log: ${error.message}`);
    }
});
//# sourceMappingURL=index.js.map