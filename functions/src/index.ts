import * as functions from 'firebase-functions/v1';
import * as admin from 'firebase-admin';

// Initialize Firebase Admin SDK
admin.initializeApp();

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
