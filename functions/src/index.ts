import * as functions from 'firebase-functions/v1';
import * as admin from 'firebase-admin';
import * as cors from 'cors';
import OpenAI from 'openai'; // Import OpenAI

// Initialize Firebase Admin SDK
admin.initializeApp();

// Configure CORS options
const corsHandler = cors({ origin: 'http://127.0.0.1:5501' }); // Remember to update for production

// Initialize OpenAI client
// Get the API key from Firebase environment configuration
const openaiApiKey = functions.config().openai?.key;
let openai: OpenAI | null = null;
if (openaiApiKey) {
    openai = new OpenAI({ apiKey: openaiApiKey });
} else {
    console.error("OpenAI API key not found in Firebase function configuration. Set it using `firebase functions:config:set openai.key=\"YOUR_API_KEY\"`");
}

// Trigger when a new user is created
export const addUserToDatabase = functions.auth.user().onCreate(async (user) => {
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
  } catch (error) {
    console.error('Error adding user to database:', error);
    return null;
  }
});

// Define the callChatAPI function as an onRequest function
export const callChatAPI = functions.https.onRequest((request, response) => {
    corsHandler(request, response, async () => {
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

        const userMessage = request.body.data?.message;

        if (!userMessage) {
            console.error('No message provided in request body.');
            response.status(400).json({ error: 'No message provided.' });
            return;
        }

        try {
            console.log("Received message:", userMessage);

            // --- Call OpenAI API --- 
            const completion = await openai.chat.completions.create({
                model: "gpt-3.5-turbo", // Or your preferred model, e.g., "gpt-4"
                messages: [
                    { role: "system", content: "You are TARS, a helpful assistant from the movie Interstellar. Respond concisely and helpfully, sometimes with a bit of dry humor like the character." },
                    { role: "user", content: userMessage }
                ],
                max_tokens: 150, // Adjust as needed
            });

            const reply = completion.choices[0]?.message?.content?.trim();

            if (!reply) {
                console.error('No reply content received from OpenAI.');
                throw new Error('Failed to get valid response from AI.');
            }
            // --- End OpenAI API Call ---

            console.log("Sending reply:", reply);
            response.status(200).json({ data: { reply: reply } });

        } catch (error: any) {
            console.error('Error calling OpenAI or processing chat request:', error);
            let errorMessage = 'Failed to get response from TARS.';
            if (error.response) {
                // Log more details if available from OpenAI error
                console.error('OpenAI API Error Status:', error.response.status);
                console.error('OpenAI API Error Data:', error.response.data);
                errorMessage = `AI service error: ${error.response.data?.error?.message || error.message}`;
            } else {
                errorMessage = `Error: ${error.message}`;
            }
            response.status(500).json({ error: errorMessage });
        }
    });
});

// New HTTPS Callable function to generate and store a TARS log
export const generateTarsLog = functions.https.onCall(async (data, context) => {
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
            model: "gpt-3.5-turbo", // Or your preferred model
            messages: [
                { role: "system", content: "You are TARS from Interstellar. Generate log entries based on the prompt." },
                { role: "user", content: logPrompt }
            ],
            max_tokens: 30, // Keep logs concise
            temperature: 0.8, // Allow for some creativity
        });

        const logMessage = completion.choices[0]?.message?.content?.trim();

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

    } catch (error: any) {
        console.error('Error generating or saving TARS log:', error);
        // Throw an HttpsError for the client
        throw new functions.https.HttpsError('internal', `Failed to generate TARS log: ${error.message}`);
    }
});
