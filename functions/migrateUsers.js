const admin = require('firebase-admin');
require('dotenv').config();


// Initialize Firebase Admin SDK
admin.initializeApp({
  credential: admin.credential.applicationDefault(),
  databaseURL: 'https://fir-forums-54bdb-default-rtdb.firebaseio.com/',
});

// Function to list all users and add them to Realtime Database
async function migrateUsers() {
  try {
    const listAllUsers = async (nextPageToken) => {
      const result = await admin.auth().listUsers(1000, nextPageToken);
      
      result.users.forEach((userRecord) => {
        const userData = {
          email: userRecord.email || null,
          createdAt: userRecord.metadata.creationTime,
        };

        admin.database().ref(`/users/${userRecord.uid}`).set(userData)
          .then(() => console.log(`Migrated user: ${userRecord.uid}`))
          .catch((err) => console.error(`Error migrating user ${userRecord.uid}:`, err));
      });

      if (result.pageToken) {
        await listAllUsers(result.pageToken);
      }
    };

    await listAllUsers();
    console.log('Migration completed.');
  } catch (error) {
    console.error('Migration failed:', error);
  }
}

migrateUsers();
