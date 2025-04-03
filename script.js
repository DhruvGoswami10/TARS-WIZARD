// Import the functions you need from the SDKs you need
// Initialize Firebase
const firebaseConfig = {
  apiKey: "AIzaSyBOEOxU866-jIoT0KIO-hBG3GbUaTEnsQg",
  authDomain: "fir-forums-54bdb.firebaseapp.com",
  projectId: "fir-forums-54bdb",
  storageBucket: "fir-forums-54bdb.firebasestorage.app",
  messagingSenderId: "159128608485",
  appId: "1:159128608485:web:b68c2b41f4ba97c28d3e0c",
  measurementId: "G-J50YZC2H2L"
};

// Initialize Firebase
if(typeof firebase !== 'undefined') {
  const app = firebase.initializeApp(firebaseConfig);
  const auth = firebase.auth();
  const db = firebase.database();
  const analytics = firebase.analytics();

  console.log("Firebase initialized successfully");
  
  const signupBtn = document.getElementById("signup-btn");
  const loginBtn = document.getElementById("login-btn");
  const logoutBtn = document.getElementById("logout-btn");
  const postBtn = document.getElementById("post-btn");
  const postsSection = document.getElementById("posts");
  const newPostSection = document.getElementById("new-post");
  const backBtn = document.getElementById("back-btn");
  const postDetailsSection = document.getElementById("post-details");
  const postContentDiv = document.getElementById("post-content");
  const repliesDiv = document.getElementById("replies");
  const replyText = document.getElementById("reply-text");
  const replyBtn = document.getElementById("reply-btn");
  const createPostBtn = document.getElementById("create-post-btn");
  const newPostModal = document.getElementById("new-post-modal");

  let currentPostId = null;
  let currentCategory = null;
  let hasPromptedForUsername = false; // Add this at the top with other global variables

  // Initialize Quill editors
  const postQuill = new Quill('#new-post-editor', {
    theme: 'snow',
    modules: {
      toolbar: [
        ['bold', 'italic', 'underline', 'strike'],
        ['blockquote', 'code-block'],
        [{ 'header': 1 }, { 'header': 2 }],
        [{ 'list': 'ordered'}, { 'list': 'bullet' }],
        [{ 'script': 'sub'}, { 'script': 'super' }],
        [{ 'indent': '-1'}, { 'indent': '+1' }],
        [{ 'size': ['small', false, 'large', 'huge'] }],
        ['link', 'image'],
        [{ 'color': [] }, { 'background': [] }],
        [{ 'align': [] }]
      ]
    }
  });

  const replyQuill = new Quill('#reply-editor', {
    theme: 'snow',
    placeholder: 'Write your reply...',
    modules: {
      toolbar: [
        ['bold', 'italic', 'underline'],
        ['link', 'image'],
        [{ 'list': 'ordered'}, { 'list': 'bullet' }],
        [{ 'align': [] }]
      ]
    }
  });

  // Forum Guidelines Popup Handler
  document.addEventListener('DOMContentLoaded', () => {
    const guidelinesPopup = document.getElementById('guidelines-popup');
    const understandBtn = document.getElementById('understand-btn');
    
    // Check if user has already accepted guidelines
    const hasAcceptedGuidelines = localStorage.getItem('acceptedForumGuidelines');
    
    if (!hasAcceptedGuidelines && guidelinesPopup) {
        guidelinesPopup.style.display = 'flex';
        
        understandBtn.addEventListener('click', () => {
            guidelinesPopup.style.display = 'none';
            localStorage.setItem('acceptedForumGuidelines', 'true');
        });
    }
  });

  // Signup Functionality
  signupBtn.addEventListener("click", () => {
    document.getElementById("signup-form").style.display = "flex";
  });

  // Update the signup handler
  document.getElementById("signup-submit").addEventListener("click", () => {
    const email = document.getElementById("signup-email").value;
    const password = document.getElementById("signup-password").value;
    
    auth.createUserWithEmailAndPassword(email, password)
        .then((userCredential) => {
            const user = userCredential.user;
            
            // Just store email and creation time
            return db.ref(`users/${user.uid}`).set({
                email: user.email,
                createdAt: firebase.database.ServerValue.TIMESTAMP
            });
        })
        .then(() => {
            document.getElementById("signup-form").style.display = "none";
            alert("User signed up successfully!");
            signupBtn.style.display = "none";
            loginBtn.style.display = "none";
            logoutBtn.style.display = "inline-block";
            newPostSection.style.display = "block";
        })
        .catch((error) => {
            console.error("Error in signup:", error);
            alert(error.message);
        });
});

// Add this new function to sync the users count
function syncUsersCount() {
    db.ref('users').once('value')
        .then(snapshot => {
            const userCount = snapshot.numChildren();
            return db.ref('metrics/registeredUsers').update(userCount);
        })
        .catch(error => console.error("Error syncing users count:", error));
}

// Call syncUsersCount periodically (every 5 minutes) to ensure accuracy
setInterval(syncUsersCount, 5 * 60 * 1000);

// Login Functionality
  loginBtn.addEventListener("click", () => {
    document.getElementById("login-form").style.display = "flex";
  });

  // Add new login form submission handler
  document.getElementById("login-submit").addEventListener("click", () => {
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    if (!document.getElementById('terms-checkbox').checked) {
      alert('Please accept the Terms and Conditions to continue');
      return;
    }
    
    auth.signInWithEmailAndPassword(email, password)
      .then(() => {
        document.getElementById("login-form").style.display = "none";
        document.getElementById("signup-form").style.display = "none";
      })
      .catch((error) => alert(error.message));
  });

  function showUsernamePrompt(user) {
    // Don't show prompt if we've already shown it
    if (hasPromptedForUsername) {
      return;
    }
    
    hasPromptedForUsername = true;
    const usernameModal = document.getElementById('username-modal');
    usernameModal.style.display = 'block';
    
    document.getElementById('save-username-btn').onclick = () => {
      const username = document.getElementById('username-input').value.trim();
      
      if (username) {
        if (username.length < 3 || username.length > 30) {
          alert('Username must be between 3 and 30 characters');
          return;
        }
  
        // First try to reserve the username
        firebase.database().ref(`usernames/${username}`).transaction((current) => {
          if (current === null) {
            return user.uid;
          }
          return; // abort if username exists
        }).then((result) => {
          if (result.committed) {
            // Username was reserved successfully, now update user data
            return firebase.database().ref(`users/${user.uid}`).update({
              username: username,
              email: user.email,
              hasSetUsername: true // Add this flag to user data
            }).then(() => {
              usernameModal.style.display = 'none';
              document.getElementById("login-form").style.display = "none";
              document.getElementById("signup-form").style.display = "none";
              
              // Update UI to show username
              const userEmailElement = document.getElementById("user-email");
              if (userEmailElement) {
                userEmailElement.textContent = username;
              }
            });
          } else {
            throw new Error('Username already taken');
          }
        }).catch(error => {
          console.error('Error saving username:', error);
          alert(error.message || 'Error saving username. Please try another.');
          hasPromptedForUsername = false; // Reset flag on error
        });
      } else {
        alert('Please enter a valid username');
      }
    };
  }
  
  // Logout Functionality
  logoutBtn.addEventListener("click", () => {
    auth.signOut().then(() => {
      loginBtn.style.display = "inline-block";
      logoutBtn.style.display = "none";
      newPostSection.style.display = "none";
    });
  });

  auth.onAuthStateChanged((user) => {
    const userEmailElement = document.getElementById("user-email");
    const notificationBell = document.getElementById("notification-bell");
    const createPostBtn = document.getElementById("create-post-btn");
    
    if (user) {
      // Get existing user data first
      firebase.database().ref(`users/${user.uid}`).once('value')
        .then((snapshot) => {
          const existingData = snapshot.val() || {};
          
          // Only update lastLogin
          return firebase.database().ref(`users/${user.uid}`).update({
            lastLogin: firebase.database.ServerValue.TIMESTAMP,
            email: user.email || existingData.email
          });
        })
        .then(() => {
          // Update UI with email
          userEmailElement.style.display = "inline-block";
          userEmailElement.textContent = user.email;

          // Show authenticated UI elements
          logoutBtn.style.display = "inline-block";
          loginBtn.style.display = "none";
          signupBtn.style.display = "none";
          notificationBell.style.display = "flex";
          createPostBtn.style.display = "block";
          loadNotifications();
        })
        .catch((error) => {
          console.error("Error handling auth state change:", error);
          userEmailElement.style.display = "inline-block";
          userEmailElement.textContent = user.email;
        });
    } else {
      // Reset UI for logged out state
      hasPromptedForUsername = false;
      logoutBtn.style.display = "none";
      loginBtn.style.display = "inline-block";
      signupBtn.style.display = "inline-block";
      userEmailElement.style.display = "none";
      userEmailElement.textContent = "";
      notificationBell.style.display = "none";
      createPostBtn.style.display = "none";
    }
    
    loadAllCategoryPreviews();
  });

  function loadPosts(loggedInUserId) {
    const postsRef = db.ref("categories/General Discussion/threads");
    postsRef.off();
    postsSection.style.display = "block";
    
    postsRef.on("value", async (snapshot) => {
      postsSection.innerHTML = "";
      
      if (!snapshot.exists()) {
        postsSection.innerHTML = "<p>No posts yet!</p>";
        return;
      }

      const promises = [];
      snapshot.forEach((thread) => {
        const postData = thread.val();
        const userId = postData.userId;
        
        // Simplified user data fetching
        const promise = db.ref("users/" + userId).once("value")
          .then(userSnapshot => {
            const userData = userSnapshot.val();
            // Always show the email if it exists
            const userEmail = userData?.email || "deleted user";
            const postDiv = document.createElement("div");
            postDiv.classList.add("post");
            
            const deleteButton = loggedInUserId && loggedInUserId === userId 
              ? `<button class="delete-btn">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 69 14" class="svgIcon bin-top">
                    <g clip-path="url(#clip0_35_24)">
                      <path fill="black" d="M20.8232 2.62734L19.9948 4.21304C19.8224 4.54309 19.4808 4.75 19.1085 4.75H4.92857C2.20246 4.75 0 6.87266 0 9.5C0 12.1273 2.20246 14.25 4.92857 14.25H64.0714C66.7975 14.25 69 12.1273 69 9.5C69 6.87266 66.7975 4.75 64.0714 4.75H49.8915C49.5192 4.75 49.1776 4.54309 49.0052 4.21305L48.1768 2.62734C47.3451 1.00938 45.6355 0 43.7719 0H25.2281C23.3645 0 21.6549 1.00938 20.8232 2.62734ZM64.0023 20.0648C64.0397 19.4882 63.5822 19 63.0044 19H5.99556C5.4178 19 4.96025 19.4882 4.99766 20.0648L8.19375 69.3203C8.44018 73.0758 11.6746 76 15.5712 76H53.4288C57.3254 76 60.5598 73.0758 60.8062 69.3203L64.0023 20.0648Z"></path>
                    </g>
                    <defs>
                      <clipPath id="clip0_35_24">
                        <rect fill="white" height="14" width="69"></rect>
                      </clipPath>
                    </defs>
                  </svg>
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 69 57" class="svgIcon bin-bottom">
                    <g clip-path="url(#clip0_35_22)">
                      <path fill="black" d="M20.8232 -16.3727L19.9948 -14.787C19.8224 -14.4569 19.4808 -14.25 19.1085 -14.25H4.92857C2.20246 -14.25 0 -12.1273 0 -9.5C0 -6.8727 2.20246 -4.75 4.92857 -4.75H64.0714C66.7975 -4.75 69 -6.8727 69 -9.5C69 -12.1273 66.7975 -14.25 64.0714 -14.25H49.8915C49.5192 -14.25 49.1776 -14.4569 49.0052 -14.787L48.1768 -16.3727C47.3451 -17.9906 45.6355 -19 43.7719 -19H25.2281C23.3645 -19 21.6549 -17.9906 20.8232 -16.3727ZM64.0023 1.0648C64.0397 0.4882 63.5822 0 63.0044 0H5.99556C5.4178 0 4.96025 0.4882 4.99766 1.0648L8.19375 50.3203C8.44018 54.0758 11.6746 57 15.5712 57H53.4288C57.3254 57 60.5598 54.0758 60.8062 50.3203L64.0023 1.0648Z"></path>
                    </g>
                    <defs>
                      <clipPath id="clip0_35_22)">
                        <rect fill="white" height="57" width="69"></rect>
                      </clipPath>
                    </defs>
                  </svg>
                </button>` 
              : '';
            
            postDiv.innerHTML = `
              <div class="post-content">${postData.content}</div>
              <div class="post-footer">
                <span class="post-author">Posted by ${userEmail}</span>
                ${deleteButton}
              </div>
            `;
            
            if (deleteButton) {
              postDiv.querySelector(".delete-btn").addEventListener("click", (event) => {
                event.stopPropagation();
                deletePost("General Discussion", thread.key);
              });
            }
            
            postDiv.addEventListener("click", () => openPost("General Discussion", thread.key, postData, userEmail));
            postsSection.appendChild(postDiv);
          });
        
        promises.push(promise);
      });
      
      await Promise.all(promises);
    });
  }

  function deletePost(category, postId) {
    if (confirm("Are you sure you want to delete this post?")) {
      db.ref(`categories/${category}/threads/${postId}`).remove()
        .then(() => {
          console.log("Post deleted successfully");
        })
        .catch((error) => {
          console.error("Error deleting post:", error);
        });
    }
  }

  function openPost(category, postId, post, userEmail) {
    currentPostId = postId;
    currentCategory = category;
    
    firebase.database().ref(`users/${post.userId}`).once('value')
      .then(snapshot => {
        const userData = snapshot.val();
        const displayName = userData?.username || userData?.email || "deleted user";
        
        postContentDiv.innerHTML = `
          <div class="post">
            <div class="post-content">${post.content}</div>
            <div class="post-footer">
              <span class="post-author">Posted by ${displayName}</span>
            </div>
          </div>
        `;
      })
      .catch(error => {
        console.error("Error getting username:", error);
        // Fallback to email if error occurs
        postContentDiv.innerHTML = `
          <div class="post">
            <div class="post-content">${post.content}</div>
            <div class="post-footer">
              <span class="post-author">Posted by ${userEmail}</span>
            </div>
          </div>
        `;
      });

    document.querySelector('.categories').style.display = 'none';
    postDetailsSection.style.display = "block";
    loadReplies(category, postId);

    // Add authentication check for reply section
    const replyEditor = document.getElementById('reply-editor');
    const replyBtn = document.getElementById('reply-btn');
    
    if (auth.currentUser) {
        replyEditor.style.display = 'block';
        replyBtn.style.display = 'block';
    } else {
        replyEditor.style.display = 'none';
        replyBtn.style.display = 'none';
        // Updated login prompt with icon
        const loginPrompt = document.createElement('div');
        loginPrompt.className = 'login-prompt';
        loginPrompt.innerHTML = `
            <p>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M13.8 12H3"/>
                </svg>
                Please <button class="inline-login-btn">login</button> to reply to this post
            </p>
        `;
        // Add click handler for the login button
        loginPrompt.querySelector('.inline-login-btn').addEventListener('click', () => {
            document.getElementById('login-form').style.display = 'flex';
        });
        // Insert login prompt after replies section
        document.getElementById('replies').after(loginPrompt);
    }
  }

  function loadReplies(category, postId) {
    db.ref(`categories/${category}/threads/${postId}/replies`).on("value", (snapshot) => {
      repliesDiv.innerHTML = "";
      snapshot.forEach((reply) => {
        const replyElement = createReplyElement(reply.val(), reply.key, category, postId);
        repliesDiv.appendChild(replyElement);
      });
    });
  }

  replyBtn.addEventListener("click", () => {
    const content = replyQuill.root.innerHTML;
    if (content.trim() !== '<p><br></p>') {
      const user = auth.currentUser;
      
      // Store userId instead of email
      db.ref(`categories/${currentCategory}/threads/${currentPostId}/replies`).push({
        content: content,
        userId: user.uid,  // Changed from user.email to user.uid
        timestamp: firebase.database.ServerValue.TIMESTAMP,
        user: user.email // Keep this for backward compatibility
      }).then(() => {
        replyQuill.setText('');
      }).catch(error => {
        console.error("Error adding reply:", error);
        alert("Error posting reply");
      });
    } else {
      alert("Reply cannot be empty!");
    }
  });

  backBtn.addEventListener("click", () => {
    postDetailsSection.style.display = "none";
    document.querySelector('.categories').style.display = 'grid';
  });
  
  // Add a New Post
  postBtn.addEventListener("click", () => {
    const content = postQuill.root.innerHTML;
    const category = document.getElementById("category-select").value;
    
    if (content.trim() !== '<p><br></p>') {
      const user = auth.currentUser;
      if (user) {
        // Disable the button while posting
        postBtn.disabled = true;
        
        // Remove existing listener for this category before adding the post
        const postsRef = db.ref(`categories/${category}/threads`);
        postsRef.off();

        postsRef.push({
          content: content,
          userId: user.uid,
          timestamp: firebase.database.ServerValue.TIMESTAMP
        }).then(() => {
          postQuill.setText('');
          newPostModal.style.display = "none";
          // Re-enable the button after successful post
          postBtn.disabled = false;
          
          // Refresh the page after successful post
          window.location.reload();
        }).catch((error) => {
          console.error("Error adding post:", error);
          // Re-enable the button if there's an error
          postBtn.disabled = false;
        });
      }
    } else {
      alert("Post cannot be empty!");
    }
  });

  createPostBtn.addEventListener("click", () => {
    if (auth.currentUser) {
      newPostModal.style.display = "block";
    } else {
      alert("Please login to create a post");
    }
  });

  // Close modal when clicking outside
  window.onclick = (event) => {
    if (event.target === newPostModal) {
      newPostModal.style.display = "none";
    }
  };

  // Update the loadCategoryPosts function
  function loadCategoryPosts(category, isPreview = false) {
    const postsRef = db.ref(`categories/${category}/threads`).orderByChild('timestamp');
    const containerSelector = isPreview ? '.preview-posts' : '.category-posts';
    const categoryPosts = document.querySelector(`[data-category="${category}"] ${containerSelector}`);
    
    if (!categoryPosts) {
      console.error(`Container not found for category: ${category}`);
      return;
    }
  
    // Clean up existing listeners
    postsRef.off('value');
    
    // Clear existing posts
    categoryPosts.innerHTML = "";
    
    // Create a single listener
    const listener = postsRef.on("value", async (snapshot) => {
      const postCount = snapshot.numChildren();
      const seeMoreBtn = document.querySelector(`[data-category="${category}"] .see-more`);
      
      if (seeMoreBtn && !seeMoreBtn.closest('.category').classList.contains('expanded')) {
        updateCategoryCount(category, postCount);
      }
      
      categoryPosts.innerHTML = "";
      
      if (!snapshot.exists()) {
        categoryPosts.innerHTML = "<p>No posts yet in this category!</p>";
        return;
      }
  
      const posts = [];
      snapshot.forEach((thread) => {
        posts.unshift({ key: thread.key, ...thread.val() });
      });
  
      // Sort posts by timestamp in descending order (newest first)
      posts.sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));
  
      // When in preview mode, show only the 2 most recent posts
      const postsToShow = isPreview ? posts.slice(0, 2) : posts;
      const fragment = document.createDocumentFragment();
      
      await Promise.all(postsToShow.map(async post => {
        try {
          const userSnapshot = await db.ref("users/" + post.userId).once("value");
          const userData = userSnapshot.val();
          const userEmail = userData?.email || "deleted user";
          const postDiv = createPostElement(post, category, userEmail);
          fragment.appendChild(postDiv);
        } catch (error) {
          console.error("Error loading post:", error);
        }
      }));
  
      categoryPosts.appendChild(fragment);
    });
  }

  // Add function to load all category previews
  function loadAllCategoryPreviews() {
    const categories = ['updates', 'issues', 'discussions', 'suggestions'];
    categories.forEach(category => loadCategoryPosts(category, true));
  }

  // Update category click handlers to only handle preview display
  document.querySelectorAll('.category h2').forEach(header => {
    header.addEventListener('click', () => {
      const category = header.closest('.category');
      if (!category.classList.contains('expanded')) {
        loadCategoryPosts(category.dataset.category, true);
      }
    });
  });

  // Add "See all" button handlers
  document.querySelectorAll('.see-more').forEach(button => {
    button.addEventListener('click', async (e) => {
      e.stopPropagation(); // Prevent category click event
      const category = button.closest('.category');
      category.classList.toggle('expanded');
  
      if (category.classList.contains('expanded')) {
        loadCategoryPosts(category.dataset.category, false);
        button.textContent = 'Show less';
      } else {
        const postCount = await getPostCount(category.dataset.category);
        loadCategoryPosts(category.dataset.category, true);
        button.textContent = `See all (${postCount})`;
      }
    });
  });
  
  // Add these functions after Firebase initialization
  function updateNotificationCount(unreadCount) {
    const bell = document.getElementById('notification-bell');
    if (unreadCount > 0) {
      bell.setAttribute('data-count', unreadCount);
      bell.style.display = 'flex';
    } else {
      bell.removeAttribute('data-count');
    }
  }

  function loadNotifications() {
    if (!auth.currentUser) return;
    
    const notificationList = document.querySelector('.notification-list');
    db.ref(`users/${auth.currentUser.uid}/notifications`)
      .orderByChild('timestamp')
      .limitToLast(10)
      .on('value', (snapshot) => {
        notificationList.innerHTML = '';
        const notifications = [];
        
        snapshot.forEach((notif) => {
          notifications.unshift({
            key: notif.key,
            ...notif.val()
          });
        });

        notifications.forEach((notif) => {
          const div = document.createElement('div');
          div.className = 'notification-item';
          div.textContent = notif.message;
          if (!notif.read) {
            div.classList.add('unread');
          }
          notificationList.appendChild(div);
        });

        updateNotificationCount(notifications.filter(n => !n.read).length);
      });
  }

  // Add notification bell click handler
  document.getElementById('notification-bell').addEventListener('click', (e) => {
    e.stopPropagation();
    const dropdown = document.querySelector('.notifications-dropdown');
    dropdown.classList.toggle('active');
  });

  // Close dropdown when clicking outside
  document.addEventListener('click', () => {
    document.querySelector('.notifications-dropdown').classList.remove('active');
  });

  // Clear notifications handler
  document.getElementById('clear-notifications').addEventListener('click', () => {
    if (auth.currentUser) {
      db.ref(`users/${auth.currentUser.uid}/notifications`).remove()
        .then(() => {
          updateNotificationCount(0);
        });
    }
  });

  function createUpvoteButton(itemId, category, itemType, currentUpvotes = 0, postId = null) {
    const upvoteBtn = document.createElement('button');
    upvoteBtn.className = 'upvote-btn';
    upvoteBtn.innerHTML = `
      <div class="upvote-arrow"></div>
      <span class="upvote-count">${currentUpvotes || 0}</span>
    `;
  
    const isReply = itemType === 'reply';
    const basePath = isReply 
      ? `categories/${category}/threads/${postId}/replies/${itemId}`
      : `categories/${category}/threads/${itemId}`;
  
    // Check if user has already upvoted and update UI accordingly
    if (auth.currentUser) {
      db.ref(`${basePath}/upvotes/${auth.currentUser.uid}`).once('value')
        .then(snapshot => {
          if (snapshot.exists() && snapshot.val() === true) {
            upvoteBtn.classList.add('active');
          }
        })
        .catch(error => console.error("Error checking upvote status:", error));
    }
  
    upvoteBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      
      if (!auth.currentUser) {
        alert('Please login to upvote');
        return;
      }
  
      try {
        // Get current upvote status
        const userUpvoteRef = db.ref(`${basePath}/upvotes/${auth.currentUser.uid}`);
        const snapshot = await userUpvoteRef.once('value');
        const hasUpvoted = snapshot.exists() && snapshot.val() === true;
        
        // Get current upvote count
        const upvoteCountRef = db.ref(`${basePath}/upvoteCount`);
        const countSnapshot = await upvoteCountRef.once('value');
        const currentCount = countSnapshot.exists() ? countSnapshot.val() : 0;
        
        // Update upvote status (add or remove)
        if (hasUpvoted) {
          // Remove upvote
          await userUpvoteRef.remove();
          await upvoteCountRef.set(Math.max(0, currentCount - 1));
          upvoteBtn.classList.remove('active');
          upvoteBtn.querySelector('.upvote-count').textContent = Math.max(0, currentCount - 1);
        } else {
          // Add upvote
          await userUpvoteRef.set(true);
          await upvoteCountRef.set(currentCount + 1);
          upvoteBtn.classList.add('active');
          upvoteBtn.querySelector('.upvote-count').textContent = currentCount + 1;
          
          // Send notification
          const itemData = (await db.ref(basePath).once('value')).val();
          if (itemData && itemData.userId && itemData.userId !== auth.currentUser.uid) {
            const message = `${auth.currentUser.email} upvoted your ${itemType}`;
            addNotification(
              itemData.userId,
              message,
              'upvote',
              isReply ? postId : itemId
            );
          }
        }
      } catch (error) {
        console.error("Error updating upvote:", error);
        alert("Failed to update upvote. Please try again.");
      }
    });
    
    return upvoteBtn;
  }
  
  // Modify the post creation in loadCategoryPosts function
  function createPostElement(post, category, userEmail) {
    const postDiv = document.createElement("div");
    postDiv.classList.add("post");
    
    const isAuthenticated = auth.currentUser;
    const isAuthor = isAuthenticated && auth.currentUser.uid === post.userId;
    
    const deleteButton = isAuthor 
      ? `<button class="delete-btn">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 69 14" class="svgIcon bin-top">
            <g clip-path="url(#clip0_35_24)">
              <path fill="white" d="M20.8232 2.62734L19.9948 4.21304C19.8224 4.54309 19.4808 4.75 19.1085 4.75H4.92857C2.20246 4.75 0 6.87266 0 9.5C0 12.1273 2.20246 14.25 4.92857 14.25H64.0714C66.7975 14.25 69 12.1273 69 9.5C69 6.87266 66.7975 4.75 64.0714 4.75H49.8915C49.5192 4.75 49.1776 4.54309 49.0052 4.21305L48.1768 2.62734Z"></path>
            </g>
          </svg>
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 69 57" class="svgIcon bin-bottom">
            <path fill="white" d="M63.9723 3.04906C64.0092 3.62279 63.551 4.11106 62.9723 4.11106H6.02772C5.44905 4.11106 4.99084 3.62279 5.02772 3.04906L8.27772 53.8615C8.52772 57.6615 11.8277 60.6111 15.7777 60.6111H53.2223C57.1723 60.6111 60.4723 57.6615 60.7223 53.8615L63.9723 3.04906Z"></path>
          </svg>
        </button>` 
      : '';
    
    const upvoteBtn = createUpvoteButton(post.key, category, 'post', post.upvoteCount || 0, null);
    
    firebase.database().ref(`users/${post.userId}`).once('value')
      .then(snapshot => {
        const userData = snapshot.val();
        const displayName = userData?.username || userData?.email || "deleted user";
        
        postDiv.innerHTML = `
          <div class="post-content">${post.content}</div>
          <div class="post-footer">
            <div class="post-meta">
              <span class="post-author">Posted by ${displayName}</span>
              <span class="reply-count">
                <svg viewBox="0 0 24 24" width="16" height="16">
                  <path fill="currentColor" d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h14l4 4V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/>
                </svg>
                <span class="count">0</span> replies
              </span>
            </div>
            <div class="post-actions">
              ${isAuthenticated ? upvoteBtn.outerHTML : ''}
              ${isAuthor ? deleteButton : ''}
            </div>
          </div>
        `;

        // Get real-time reply count updates
        db.ref(`categories/${category}/threads/${post.key}/replies`).on('value', (snapshot) => {
          const replyCount = snapshot.numChildren() || 0;
          const countElement = postDiv.querySelector('.reply-count .count');
          if (countElement) {
            countElement.textContent = replyCount;
          }
        });

        // Handle delete button click
        if (deleteButton) {
          const deleteBtn = postDiv.querySelector(".delete-btn");
          deleteBtn.addEventListener("click", (event) => {
            event.stopPropagation();
            deletePost(category, post.key);
          });
        }
        
        // Handle upvote button click
        if (isAuthenticated) {
          const upvoteButton = postDiv.querySelector('.upvote-btn');
          if (upvoteButton) {
            upvoteButton.addEventListener('click', async (e) => {
              e.preventDefault();
              e.stopPropagation();
              
              try {
                const userUpvoteRef = db.ref(`categories/${category}/threads/${post.key}/upvotes/${auth.currentUser.uid}`);
                const upvoteCountRef = db.ref(`categories/${category}/threads/${post.key}/upvoteCount`);
                
                const snapshot = await userUpvoteRef.once('value');
                const hasUpvoted = snapshot.exists() && snapshot.val() === true;
                
                const countSnapshot = await upvoteCountRef.once('value');
                const currentCount = countSnapshot.exists() ? countSnapshot.val() : 0;
                
                if (hasUpvoted) {
                  // Remove upvote
                  await userUpvoteRef.remove();
                  await upvoteCountRef.set(Math.max(0, currentCount - 1));
                  upvoteButton.classList.remove('active');
                  const countSpan = upvoteButton.querySelector('.upvote-count');
                  countSpan.textContent = Math.max(0, currentCount - 1);
                } else {
                  // Add upvote
                  await userUpvoteRef.set(true);
                  await upvoteCountRef.set(currentCount + 1);
                  upvoteButton.classList.add('active');
                  const countSpan = upvoteButton.querySelector('.upvote-count');
                  countSpan.textContent = currentCount + 1;
                  
                  // Handle notification
                  if (post.userId !== auth.currentUser.uid) {
                    addNotification(post.userId, `${auth.currentUser.email} upvoted your post`, 'upvote', post.key);
                  }
                }
              } catch (error) {
                console.error("Error updating upvote:", error);
                alert("Failed to update upvote. Please try again.");
              }
            });
          }
        }
        
        // Add post click handler
        postDiv.addEventListener("click", () => {
          openPost(category, post.key, post, userEmail);
        });
        
        // Get reply count before creating post element
        db.ref(`categories/${category}/threads/${post.key}/replies`).once('value', (snapshot) => {
          const replyCount = snapshot.numChildren();
          const countElement = postDiv.querySelector('.reply-count .count');
          if (countElement) {
            countElement.textContent = replyCount;
          }
        });

        // Add listener for reply count updates
        db.ref(`categories/${category}/threads/${post.key}/replies`).on('value', (snapshot) => {
          const replyCount = snapshot.numChildren();
          const countElement = postDiv.querySelector('.reply-count .count');
          if (countElement) {
            countElement.textContent = replyCount;
          }
        });
      })
      .catch(error => {
        console.error("Error getting username:", error);
        // Fallback to email if error occurs
        postDiv.innerHTML = `
          <div class="post-content">${post.content}</div>
          <div class="post-footer">
            <div class="post-meta">
              <span class="post-author">Posted by ${userEmail}</span>
              <span class="reply-count">
                <svg viewBox="0 0 24 24" width="16" height="16">
                  <path fill="currentColor" d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h14l4 4V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/>
                </svg>
                <span class="count">0</span> replies
              </span>
            </div>
            <div class="post-actions">
              ${isAuthenticated ? upvoteBtn.outerHTML : ''}
              ${isAuthor ? deleteButton : ''}
            </div>
          </div>
        `;

        // Get real-time reply count updates
        db.ref(`categories/${category}/threads/${post.key}/replies`).on('value', (snapshot) => {
          const replyCount = snapshot.numChildren() || 0;
          const countElement = postDiv.querySelector('.reply-count .count');
          if (countElement) {
            countElement.textContent = replyCount;
          }
        });

        // Handle delete button click
        if (deleteButton) {
          const deleteBtn = postDiv.querySelector(".delete-btn");
          deleteBtn.addEventListener("click", (event) => {
            event.stopPropagation();
            deletePost(category, post.key);
          });
        }
        
        // Handle upvote button click
        if (isAuthenticated) {
          const upvoteButton = postDiv.querySelector('.upvote-btn');
          if (upvoteButton) {
            upvoteButton.addEventListener('click', async (e) => {
              e.preventDefault();
              e.stopPropagation();
              
              try {
                const userUpvoteRef = db.ref(`categories/${category}/threads/${post.key}/upvotes/${auth.currentUser.uid}`);
                const upvoteCountRef = db.ref(`categories/${category}/threads/${post.key}/upvoteCount`);
                
                const snapshot = await userUpvoteRef.once('value');
                const hasUpvoted = snapshot.exists() && snapshot.val() === true;
                
                const countSnapshot = await upvoteCountRef.once('value');
                const currentCount = countSnapshot.exists() ? countSnapshot.val() : 0;
                
                if (hasUpvoted) {
                  // Remove upvote
                  await userUpvoteRef.remove();
                  await upvoteCountRef.set(Math.max(0, currentCount - 1));
                  upvoteButton.classList.remove('active');
                  const countSpan = upvoteButton.querySelector('.upvote-count');
                  countSpan.textContent = Math.max(0, currentCount - 1);
                } else {
                  // Add upvote
                  await userUpvoteRef.set(true);
                  await upvoteCountRef.set(currentCount + 1);
                  upvoteButton.classList.add('active');
                  const countSpan = upvoteButton.querySelector('.upvote-count');
                  countSpan.textContent = currentCount + 1;
                  
                  // Handle notification
                  if (post.userId !== auth.currentUser.uid) {
                    addNotification(post.userId, `${auth.currentUser.email} upvoted your post`, 'upvote', post.key);
                  }
                }
              } catch (error) {
                console.error("Error updating upvote:", error);
                alert("Failed to update upvote. Please try again.");
              }
            });
          }
        }
        
        // Add post click handler
        postDiv.addEventListener("click", () => {
          openPost(category, post.key, post, userEmail);
        });
        
        // Get reply count before creating post element
        db.ref(`categories/${category}/threads/${post.key}/replies`).once('value', (snapshot) => {
          const replyCount = snapshot.numChildren();
          const countElement = postDiv.querySelector('.reply-count .count');
          if (countElement) {
            countElement.textContent = replyCount;
          }
        });

        // Add listener for reply count updates
        db.ref(`categories/${category}/threads/${post.key}/replies`).on('value', (snapshot) => {
          const replyCount = snapshot.numChildren();
          const countElement = postDiv.querySelector('.reply-count .count');
          if (countElement) {
            countElement.textContent = replyCount;
          }
        });
      });

    return postDiv;
  }
  
  // Modify the reply creation in loadReplies function
  function createReplyElement(reply, replyKey, category, postId) {
    const replyDiv = document.createElement("div");
    replyDiv.classList.add("reply");
    
    // First, check if the userId property exists in the reply
    const userId = reply.userId;
    if (!userId) {
      // For legacy replies that only have user email
      firebase.database().ref('users').orderByChild('email').equalTo(reply.user).once('value')
        .then(snapshot => {
          let foundUserId = null;
          snapshot.forEach(child => {
            foundUserId = child.key;
          });
          if (foundUserId) {
            return firebase.database().ref(`users/${foundUserId}`).once('value');
          }
          throw new Error('User not found');
        })
        .then(userSnapshot => {
          const userData = userSnapshot.val();
          displayReplyContent(userData?.username || reply.user);
        })
        .catch(error => {
          console.error("Error getting username:", error);
          displayReplyContent(reply.user || "Unknown User");
        });
    } else {
      // For new replies that have userId
      firebase.database().ref(`users/${userId}`).once('value')
        .then(snapshot => {
          const userData = snapshot.val();
          displayReplyContent(userData?.username || userData?.email || "Unknown User");
        })
        .catch(error => {
          console.error("Error getting username:", error);
          displayReplyContent("Unknown User");
        });
    }
  
    function displayReplyContent(displayName) {
      const deleteButton = auth.currentUser && 
        (auth.currentUser.uid === reply.userId || auth.currentUser.email === reply.user)
          ? `<button class="delete-reply-btn">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 69 14" class="svgIcon bin-top">
                <g clip-path="url(#clip0_35_24)">
                  <path fill="white" d="M20.8232 2.62734L19.9948 4.21304C19.8224 4.54309 19.4808 4.75 19.1085 4.75H4.92857C2.20246 4.75 0 6.87266 0 9.5C0 12.1273 2.20246 14.25 4.92857 14.25H64.0714C66.7975 14.25 69 12.1273 69 9.5C69 6.87266 66.7975 4.75 64.0714 4.75H49.8915C49.5192 4.75 49.1776 4.54309 49.0052 4.21305L48.1768 2.62734Z"></path>
                </g>
              </svg>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 69 57" class="svgIcon bin-bottom">
                <path fill="white" d="M63.9723 3.04906C64.0092 3.62279 63.551 4.11106 62.9723 4.11106H6.02772C5.44905 4.11106 4.99084 3.62279 5.02772 3.04906L8.27772 53.8615C8.52772 57.6615 11.8277 60.6111 15.7777 60.6111H53.2223C57.1723 60.6111 60.4723 57.6615 60.7223 53.8615L63.9723 3.04906Z"></path>
              </svg>
            </button>` 
          : '';
  
      replyDiv.innerHTML = `
        <div class="reply-content">${reply.content}</div>
        <div class="reply-footer">
          <div class="reply-actions">
            <span class="reply-author">Replied by ${displayName}</span>
          </div>
          <div class="reply-actions">
            ${deleteButton}
          </div>
        </div>
      `;
  
      // Add upvote button and handlers
      const upvoteBtn = createUpvoteButton(replyKey, category, 'reply', reply.upvoteCount || 0, postId);
      replyDiv.querySelector('.reply-actions').prepend(upvoteBtn);
  
      if (deleteButton) {
        replyDiv.querySelector(".delete-reply-btn").addEventListener("click", (e) => {
          e.stopPropagation();
          if (confirm("Are you sure you want to delete this reply?")) {
            firebase.database().ref(`categories/${category}/threads/${postId}/replies/${replyKey}`).remove()
              .then(() => console.log("Reply deleted successfully"))
              .catch((error) => console.error("Error deleting reply:", error));
          }
        });
      }
    }
  
    return replyDiv;
  }
  
  function addNotification(userId, message, type, sourceId) {
    if (!userId || userId === auth.currentUser?.uid) return;
  
    try {
      const notificationData = {
        message: message,
        timestamp: firebase.database.ServerValue.TIMESTAMP,
        type: type || 'general',
        sourceId: sourceId || '',
        read: false
      };
      
      db.ref(`users/${userId}/notifications`).push(notificationData)
        .catch(error => console.error("Error adding notification:", error));
    } catch (error) {
      console.error("Error in addNotification:", error);
    }
  }
  
  function loadNotifications() {
    if (!auth.currentUser) return;
    
    const notificationList = document.querySelector('.notification-list');
    db.ref(`users/${auth.currentUser.uid}/notifications`)
      .orderByChild('timestamp')
      .limitToLast(10)
      .on('value', (snapshot) => {
        notificationList.innerHTML = '';
        const notifications = [];
        
        snapshot.forEach((notif) => {
          notifications.unshift({
            key: notif.key,
            ...notif.val()
          });
        });
  
        notifications.forEach((notif) => {
          const div = document.createElement('div');
          div.className = 'notification-item';
          div.dataset.key = notif.key;  // Add this to track notification ID
          
          // Format the notification message
          let message = notif.message;
          if (notif.type === 'upvote') {
            message = `👍 ${message}`;  // Add an upvote emoji for upvote notifications
          }
          
          div.textContent = message;
          
          if (!notif.read) {
            div.classList.add('unread');
          }
          
          notificationList.appendChild(div);
        });
  
        updateNotificationCount(notifications.filter(n => !n.read).length);
      });
  }
  
  // Add click handler for notifications
  document.querySelector('.notification-list').addEventListener('click', (e) => {
    if (e.target.classList.contains('notification-item')) {
      e.target.classList.remove('unread');
      const notifKey = e.target.dataset.key;
      if (notifKey && auth.currentUser) {
        db.ref(`users/${auth.currentUser.uid}/notifications/${notifKey}/read`).update(true);
      }
    }
  });
  
  // Update clear notifications handler
  document.getElementById('clear-notifications').addEventListener('click', () => {
    if (auth.currentUser) {
      db.ref(`users/${auth.currentUser.uid}/notifications`).remove()
        .then(() => {
          updateNotificationCount(0);
        });
    }
  });
  
  // Update the metrics listener to handle permission errors
  db.ref('metrics').on('value', 
    (snapshot) => {
        const metricsData = snapshot.val() || { pageViews: 0, registeredUsers: 0 };
        updateDisplayedCounters(metricsData);
    },
    (error) => {
        console.warn("Error reading metrics:", error);
        // Set default values if read fails
        updateDisplayedCounters({ pageViews: 0, registeredUsers: 0 });
    }
);

// Initialize categories if they don't exist
function initializeCategories() {
  const categories = ['updates', 'issues', 'discussions', 'suggestions'];
  categories.forEach(category => {
    db.ref(`categories/${category}`).once('value', snapshot => {
      if (!snapshot.exists()) {
        db.ref(`categories/${category}`).update({
          threads: {}
        });
      }
    });
  });
}

// Add this to the Firebase initialization block
if(typeof firebase !== 'undefined') {
  // ...existing initialization code...

  // Initialize categories when the app starts
  initializeCategories();

  // Load all category previews when page loads
  document.addEventListener('DOMContentLoaded', () => {
    const categories = ['updates', 'issues', 'discussions', 'suggestions'];
    categories.forEach(category => loadCategoryPosts(category, true));
  });

  // ...rest of existing code...
}

// ...existing code...

// Function to update the displayed counters
function updateDisplayedCounters(metricsData) {
  if (typeof metricsData !== 'object') {
    console.warn('Invalid metrics data received:', metricsData);
    metricsData = { pageViews: 0, registeredUsers: 0 };
  }

  const userCount = document.getElementById('user-count');
  const pageViews = document.getElementById('page-views');
  
  if (userCount) {
    userCount.textContent = (metricsData.registeredUsers || 0).toLocaleString();
  }
  
  if (pageViews) {
    pageViews.textContent = (metricsData.pageViews || 0).toLocaleString();
  }
}

// Update the metrics listener to handle errors gracefully
if(typeof firebase !== 'undefined') {
  const db = firebase.database();
  db.ref('metrics').on('value', 
    (snapshot) => {
      const metricsData = snapshot.val() || { pageViews: 0, registeredUsers: 0 };
      updateDisplayedCounters(metricsData);
    },
    (error) => {
      console.warn("Error reading metrics:", error);
      updateDisplayedCounters({ pageViews: 0, registeredUsers: 0 });
    }
  );
}

// Add styles for the login prompt
document.head.insertAdjacentHTML('beforeend', `
  <style>
    .login-prompt {
      position: fixed;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(0, 0, 0, 0.8);
      color: white;
      padding: 10px 20px;
      border-radius: 5px;
      z-index: 1000;
    }
    
    .inline-login-btn {
      background: none;
      border: none;
      color: #007bff;
      text-decoration: underline;
      cursor: pointer;
      padding: 0;
      font: inherit;
    }
    
    .inline-login-btn:hover {
      color: #0056b3;
    }
  </style>
`);
}

function updateCategoryCount(category, count) {
  const seeMoreBtn = document.querySelector(`[data-category="${category}"] .see-more`);
  if (seeMoreBtn) {
    seeMoreBtn.textContent = `See all (${count})`;
  }
}

// Modify the loadCategoryPosts function to update counts
function loadCategoryPosts(category, isPreview = false) {
  const postsRef = db.ref(`categories/${category}/threads`).orderByChild('timestamp');
  const containerSelector = isPreview ? '.preview-posts' : '.category-posts';
  const categoryPosts = document.querySelector(`[data-category="${category}"] ${containerSelector}`);
  
  if (!categoryPosts) {
    console.error(`Container not found for category: ${category}`);
    return;
  }

  // Remove any existing listeners
  postsRef.off();
  
  postsRef.on("value", async (snapshot) => {
    // Update the post count first
    const postCount = snapshot.numChildren();
    const seeMoreBtn = document.querySelector(`[data-category="${category}"] .see-more`);
    
    // Only update if not expanded and if count has changed
    if (seeMoreBtn && 
        !seeMoreBtn.closest('.category').classList.contains('expanded') && 
        !seeMoreBtn.textContent.includes(`(${postCount})`)) {
      updateCategoryCount(category, postCount);
    }
    
    // ...rest of existing code...
  });
}

// ...rest of existing code...

// Modify the post button click handler
postBtn.addEventListener("click", () => {
  const content = postQuill.root.innerHTML;
  const category = document.getElementById("category-select").value;
  
  if (content.trim() !== '<p><br></p>') {
    const user = auth.currentUser;
    if (user) {
      postBtn.disabled = true;
      
      db.ref(`categories/${category}/threads`).push({
        content: content,
        userId: user.uid,
        timestamp: firebase.database.ServerValue.TIMESTAMP
      }).then(() => {
        postQuill.setText('');
        newPostModal.style.display = "none";
        postBtn.disabled = false;
        
        // Refresh the page after successful post
        window.location.reload();
      }).catch((error) => {
        console.error("Error adding post:", error);
        postBtn.disabled = false;
      });
    }
  } else {
    alert("Post cannot be empty!");
  }
});

// Modify the "See all" button handlers
document.querySelectorAll('.see-more').forEach(button => {
  button.addEventListener('click', async (e) => {
    e.stopPropagation();
    const category = button.closest('.category');
    const isExpanded = category.classList.contains('expanded');
    
    if (isExpanded) {
      // Going back to preview mode
      category.classList.remove('expanded');
      const count = await getPostCount(category.dataset.category);
      button.textContent = `See all (${count})`;
      loadCategoryPosts(category.dataset.category, true);
    } else {
      // Expanding to show all posts
      category.classList.add('expanded');
      button.textContent = 'Show less';
      loadCategoryPosts(category.dataset.category, false);
    }
  });
});

// Update loadCategoryPosts to properly handle preview mode
function loadCategoryPosts(category, isPreview = false) {
  const postsRef = db.ref(`categories/${category}/threads`).orderByChild('timestamp');
  const containerSelector = isPreview ? '.preview-posts' : '.category-posts';
  const categoryPosts = document.querySelector(`[data-category="${category}"] ${containerSelector}`);
  
  if (!categoryPosts) return;

  // Remove existing listeners
  postsRef.off('value');
  
  // Clear existing posts
  categoryPosts.innerHTML = "";
  
  postsRef.on("value", async (snapshot) => {
    const posts = [];
    snapshot.forEach((thread) => {
      posts.unshift({ key: thread.key, ...thread.val() });
    });

    // Sort posts by timestamp in descending order
    posts.sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));
    
    // Update post count if in preview mode
    if (isPreview) {
      const seeMoreBtn = document.querySelector(`[data-category="${category}"] .see-more`);
      if (seeMoreBtn && !seeMoreBtn.textContent.includes('Show less')) {
        updateCategoryCount(category, posts.length);
      }
    }

    // Show all posts or just the preview
    const postsToShow = isPreview ? posts.slice(0, 2) : posts;
    const fragment = document.createDocumentFragment();

    await Promise.all(postsToShow.map(async post => {
      try {
        const userSnapshot = await db.ref("users/" + post.userId).once("value");
        const userData = userSnapshot.val();
        const userEmail = userData?.email || "deleted user";
        const postDiv = createPostElement(post, category, userEmail);
        fragment.appendChild(postDiv);
      } catch (error) {
        console.error("Error loading post:", error);
      }
    }));

    categoryPosts.appendChild(fragment);
  });
}

// ...existing code...

// Add this function near the top with other utility functions
async function getPostCount(category) {
  try {
    const snapshot = await db.ref(`categories/${category}/threads`).once('value');
    return snapshot.numChildren();
  } catch (error) {
    console.error('Error getting post count:', error);
    return 0;
  }
}

// Update the "See all" button handlers
document.querySelectorAll('.see-more').forEach(button => {
  button.addEventListener('click', async (e) => {
    e.stopPropagation();
    const category = button.closest('.category');
    const isExpanded = category.classList.contains('expanded');
    
    if (isExpanded) {
      // Going back to preview mode
      category.classList.remove('expanded');
      try {
        const count = await getPostCount(category.dataset.category);
        button.textContent = `See all (${count})`;
        loadCategoryPosts(category.dataset.category, true);
      } catch (error) {
        console.error('Error updating post count:', error);
      }
    } else {
      // Expanding to show all posts
      category.classList.add('expanded');
      button.textContent = 'Show less';
      loadCategoryPosts(category.dataset.category, false);
    }
  });
});

// ...existing code...

function createPostElement(post, category, userEmail) {
  const postDiv = document.createElement("div");
  postDiv.classList.add("post");
  
  // Get reply count before creating post element
  db.ref(`categories/${category}/threads/${post.key}/replies`).on('value', (snapshot) => {
    const replyCount = snapshot.numChildren() || 0;
    const metaDiv = postDiv.querySelector('.post-meta');
    if (metaDiv) {
      const replyText = metaDiv.querySelector('.reply-text');
      replyText.textContent = `${replyCount} ${replyCount === 1 ? 'reply' : 'replies'}`;
    }
  });

  const isAuthenticated = auth.currentUser;
  const isAuthor = isAuthenticated && auth.currentUser.uid === post.userId;
  
  firebase.database().ref(`users/${post.userId}`).once('value')
    .then(snapshot => {
      const userData = snapshot.val();
      const displayName = userData?.username || userData?.email || "deleted user";
      
      postDiv.innerHTML = `
        <div class="post-content">${post.content}</div>
        <div class="post-footer">
          <div class="post-meta">
            <span class="post-author">Posted by ${displayName}</span>
            <span class="reply-count">
              <svg viewBox="0 0 24 24" width="16" height="16">
                <path fill="currentColor" d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h14l4 4V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/>
              </svg>
              <span class="count">0</span> replies
            </span>
          </div>
          <div class="post-actions">
            ${isAuthenticated ? createUpvoteButton(post.key, category, 'post', post.upvoteCount || 0).outerHTML : ''}
            ${isAuthor ? deleteButton : ''}
          </div>
        </div>
      `;

      // Get real-time reply count updates
      db.ref(`categories/${category}/threads/${post.key}/replies`).on('value', (snapshot) => {
        const replyCount = snapshot.numChildren() || 0;
        const countElement = postDiv.querySelector('.reply-count .count');
        if (countElement) {
          countElement.textContent = replyCount;
        }
      });

      // ...rest of the existing function code...
    })
    .catch(error => {
      console.error("Error getting username:", error);
      // Fallback to email if error occurs
      postDiv.innerHTML = `
        <div class="post-content">${post.content}</div>
        <div class="post-footer">
          <div class="post-meta">
            <span class="post-author">Posted by ${userEmail}</span>
            <!-- ...rest of existing post footer... -->
          </div>
        </div>
      `;
    });

  return postDiv;
}

// Update the addNotification function to include more metadata
function addNotification(userId, message, type, sourceId) {
  if (userId === auth.currentUser?.uid) return; // Don't notify yourself
  
  db.ref(`users/${userId}/notifications`).push({
    message,
    timestamp: firebase.database.ServerValue.TIMESTAMP,
    type, // 'upvote', 'reply', etc.
    sourceId, // postId or replyId
    read: false
  });
}

// Update the loadNotifications function
function loadNotifications() {
  if (!auth.currentUser) return;
  
  const notificationList = document.querySelector('.notification-list');
  if (!notificationList) return;
  
  db.ref(`users/${auth.currentUser.uid}/notifications`)
    .orderByChild('timestamp')
    .limitToLast(10)
    .on('value', (snapshot) => {
      notificationList.innerHTML = '';
      const notifications = [];
      let unreadCount = 0;
      
      snapshot.forEach((notif) => {
        const notification = {
          key: notif.key,
          ...notif.val()
        };
        notifications.unshift(notification);
        if (!notification.read) unreadCount++;
      });

      // Update notification bell badge
      const bell = document.getElementById('notification-bell');
      if (unreadCount > 0) {
        bell.setAttribute('data-count', unreadCount);
        bell.classList.add('has-notifications');
      } else {
        bell.removeAttribute('data-count');
        bell.classList.remove('has-notifications');
      }

      // Render notifications
      notifications.forEach((notif) => {
        const div = document.createElement('div');
        div.className = `notification-item ${notif.read ? '' : 'unread'}`;
        div.dataset.key = notif.key;
        div.dataset.type = notif.type;
        div.dataset.sourceId = notif.sourceId;
        
        // Add icon based on notification type
        const icon = notif.type === 'upvote' ? '👍' : 
                    notif.type === 'reply' ? '💬' : '📢';
        
        div.innerHTML = `
          <span class="notification-icon">${icon}</span>
          <span class="notification-message">${notif.message}</span>
          <span class="notification-time">${formatTimestamp(notif.timestamp)}</span>
        `;
        
        // Add click handler to mark as read and navigate
        div.addEventListener('click', () => handleNotificationClick(notif));
        
        notificationList.appendChild(div);
      });
    });
}

// Add this helper function
function formatTimestamp(timestamp) {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now - date;
  
  if (diff < 60000) return 'just now';
  if (diff < 3600000) return `${Math.floor(diff/60000)}m ago`;
  if (diff < 86400000) return `${Math.floor(diff/3600000)}h ago`;
  return date.toLocaleDateString();
}

// Add notification click handler
function handleNotificationClick(notification) {
  // Mark as read
  db.ref(`users/${auth.currentUser.uid}/notifications/${notification.key}/read`)
    .set(true);

  // Navigate to the relevant content based on type
  if (notification.sourceId) {
    if (notification.type === 'reply' || notification.type === 'upvote') {
      // Find the post and open it
      db.ref('categories').once('value', (snapshot) => {
        snapshot.forEach((category) => {
          const threads = category.child('threads');
          if (threads.hasChild(notification.sourceId)) {
            // Found the post, open it
            openPost(category.key, notification.sourceId);
            return true;
          }
        });
      });
    }
  }
  
  // Close the dropdown
  document.querySelector('.notifications-dropdown').classList.remove('active');
}

// Update upvote handler to include notifications
function createUpvoteButton(itemId, category, itemType, currentUpvotes = 0, postId = null) {
  const upvoteBtn = document.createElement('button');
  upvoteBtn.className = 'upvote-btn'; // Remove isActive variable reference
  upvoteBtn.innerHTML = `
    <div class="upvote-arrow"></div>
    <span class="upvote-count">${currentUpvotes}</span>
  `;

  const isReply = itemType === 'reply';
  const basePath = isReply 
    ? `categories/${category}/threads/${postId}/replies/${itemId}`
    : `categories/${category}/threads/${itemId}`;

  if (auth.currentUser) {
    // Check if user has already upvoted
    db.ref(`${basePath}/upvotes/${auth.currentUser.uid}`).once('value', (snapshot) => {
      if (snapshot.exists()) {
        upvoteBtn.classList.add('active');
        const countSpan = upvoteBtn.querySelector('.upvote-count');
        countSpan.textContent = currentUpvotes || 0;
      }
    });
  }

  upvoteBtn.addEventListener('click', async (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!auth.currentUser) {
        alert('Please login to upvote');
        return;
    }

    try {
        const upvoteRef = db.ref(`${basePath}/upvotes/${auth.currentUser.uid}`);
        const countRef = db.ref(`${basePath}/upvoteCount`);
        
        const snapshot = await upvoteRef.once('value');
        const hasUpvoted = snapshot.exists();
        
        await db.ref(basePath).transaction(current => {
            if (!current) return current;
            
            if (hasUpvoted) {
                // Remove upvote
                if (current.upvotes) {
                    delete current.upvotes[auth.currentUser.uid];
                }
                current.upvoteCount = (current.upvoteCount || 1) - 1;
            } else {
                // Add upvote
                if (!current.upvotes) current.upvotes = {};
                current.upvotes[auth.currentUser.uid] = true;
                current.upvoteCount = (current.upvoteCount || 0) + 1;
            }
            return current;
        });

        // Update button state without reloading
        upvoteBtn.classList.toggle('active');
        const countSpan = upvoteBtn.querySelector('.upvote-count');
        const currentCount = parseInt(countSpan.textContent);
        countSpan.textContent = hasUpvoted ? currentCount - 1 : currentCount + 1;

        // Handle notification if adding upvote
        if (!hasUpvoted) {
            const itemData = (await db.ref(basePath).once('value')).val();
            const ownerId = isReply ? 
                await getUserIdByEmail(itemData.user) : 
                itemData.userId;

            if (ownerId && ownerId !== auth.currentUser.uid) {
                const message = itemType === 'reply' ?
                  `${auth.currentUser.email} upvoted your reply` :
                  `${auth.currentUser.email} upvoted your post`;
                  
                addNotification(ownerId, message, 'upvote', itemId);
            }
        }
    } catch (error) {
        console.error("Error updating upvote:", error);
    }
});

return upvoteBtn;
}

// Update reply handler to include notifications
replyBtn.addEventListener("click", () => {
  const content = replyQuill.root.innerHTML;
  if (content.trim() !== '<p><br></p>') {
    const user = auth.currentUser;
    
    // Get post author ID
    db.ref(`categories/${currentCategory}/threads/${currentPostId}`)
      .once('value')
      .then((snapshot) => {
        const post = snapshot.val();
        
        db.ref(`categories/${currentCategory}/threads/${currentPostId}/replies`).push({
          content: content,
          userId: user.uid,
          timestamp: firebase.database.ServerValue.TIMESTAMP
        }).then((replyRef) => {
          // Add notification for post author
          if (post.userId !== user.uid) {
            addNotification(
              post.userId,
              `${user.email} replied to your post`,
              'reply',
              currentPostId
            );
          }
          replyQuill.setText('');
        });
      });
  } else {
    alert("Reply cannot be empty!");
  }
});

// Update the createUpvoteButton function
function createUpvoteButton(itemId, category, itemType, currentUpvotes = 0, postId = null) {
  const upvoteBtn = document.createElement('button');
  upvoteBtn.className = 'upvote-btn'; // Remove isActive variable reference
  upvoteBtn.innerHTML = `
    <div class="upvote-arrow"></div>
    <span class="upvote-count">${currentUpvotes}</span>
  `;

  const isReply = itemType === 'reply';

  upvoteBtn.addEventListener('click', async (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!auth.currentUser) {
      alert('Please login to upvote');
      return;
    }

    try {
      const basePath = isReply 
        ? `categories/${category}/threads/${postId}/replies/${itemId}`
        : `categories/${category}/threads/${itemId}`;

      // First, check if user has already upvoted
      const upvoteRef = db.ref(`${basePath}/upvotes/${auth.currentUser.uid}`);
      const snapshot = await upvoteRef.once('value');
      const hasUpvoted = snapshot.exists();

      // Update upvote count and user upvote status
      await db.ref(basePath).update({
        [`upvotes/${auth.currentUser.uid}`]: hasUpvoted ? null : true,
        upvoteCount: firebase.database.ServerValue.increment(hasUpvoted ? -1 : 1)
      });

      // Update UI
      upvoteBtn.classList.toggle('active');
      const countSpan = upvoteBtn.querySelector('.upvote-count');
      const currentCount = parseInt(countSpan.textContent || '0');
      countSpan.textContent = hasUpvoted ? currentCount - 1 : currentCount + 1;

      // Handle notification
      if (!hasUpvoted) {
        const itemSnapshot = await db.ref(basePath).once('value');
        const itemData = itemSnapshot.val();
        if (itemData.userId && itemData.userId !== auth.currentUser.uid) {
          const message = `${auth.currentUser.email} upvoted your ${itemType}`;
          addNotification(itemData.userId, message, 'upvote', itemId);
        }
      }
    } catch (error) {
      console.error("Error updating upvote:", error);
      // Revert UI changes if error occurs
      upvoteBtn.classList.remove('active');
    }
  });

  return upvoteBtn;
}

// Update the addNotification function
function addNotification(userId, message, type, sourceId) {
  if (!userId || userId === auth.currentUser?.uid) return;

  const notificationRef = db.ref(`users/${userId}/notifications`).push();
  notificationRef.set({
    message,
    type,
    sourceId,
    timestamp: firebase.database.ServerValue.TIMESTAMP,
    read: false
  }).catch(error => {
    console.error("Error adding notification:", error);
  });
}

// Add this helper function for vote count updates
function updateVoteCount(path) {
  return db.ref(path).transaction((current) => {
    if (current === null) return 0;
    return current;
  });
}

// Update the Reply button click handler to include notifications
replyBtn.addEventListener("click", () => {
  const content = replyQuill.root.innerHTML;
  if (content.trim() !== '<p><br></p>') {
    const user = auth.currentUser;
    
    // Get post author ID
    db.ref(`categories/${currentCategory}/threads/${currentPostId}`)
      .once('value')
      .then((snapshot) => {
        const post = snapshot.val();
        
        db.ref(`categories/${currentCategory}/threads/${currentPostId}/replies`).push({
          content: content,
          userId: user.uid,
          timestamp: firebase.database.ServerValue.TIMESTAMP,
          user: user.email // Keep this for backward compatibility
        }).then((replyRef) => {
          // Add notification for post author
          if (post.userId && post.userId !== user.uid) {
            addNotification(
              post.userId,
              `${user.email} replied to your post`,
              'reply',
              currentPostId
            );
          }
          replyQuill.setText('');
        }).catch(error => {
          console.error("Error adding reply:", error);
          alert("Error posting reply");
        });
      })
      .catch(error => {
        console.error("Error fetching post data:", error);
        alert("Error posting reply");
      });
  } else {
    alert("Reply cannot be empty!");
  }
});

// Update the createReplyElement function to include reply author information for notifications
function createReplyElement(reply, replyKey, category, postId) {
  const replyDiv = document.createElement("div");
  replyDiv.classList.add("reply");
  
  // First, check if the userId property exists in the reply
  const userId = reply.userId;
  if (!userId) {
    // For legacy replies that only have user email
    firebase.database().ref('users').orderByChild('email').equalTo(reply.user).once('value')
      .then(snapshot => {
        let foundUserId = null;
        snapshot.forEach(child => {
          foundUserId = child.key;
        });
        if (foundUserId) {
          return firebase.database().ref(`users/${foundUserId}`).once('value');
        }
        throw new Error('User not found');
      })
      .then(userSnapshot => {
        const userData = userSnapshot.val();
        displayReplyContent(userData?.username || reply.user, foundUserId || null);
      })
      .catch(error => {
        console.error("Error getting username:", error);
        displayReplyContent(reply.user || "Unknown User", null);
      });
  } else {
    // For new replies that have userId
    firebase.database().ref(`users/${userId}`).once('value')
      .then(snapshot => {
        const userData = snapshot.val();
        displayReplyContent(userData?.username || userData?.email || "Unknown User", userId);
      })
      .catch(error => {
        console.error("Error getting username:", error);
        displayReplyContent("Unknown User", null);
      });
  }

  function displayReplyContent(displayName, replyUserId) {
    const deleteButton = auth.currentUser && 
      (auth.currentUser.uid === reply.userId || auth.currentUser.email === reply.user)
        ? `<button class="delete-reply-btn">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 69 14" class="svgIcon bin-top">
              <g clip-path="url(#clip0_35_24)">
                <path fill="white" d="M20.8232 2.62734L19.9948 4.21304C19.8224 4.54309 19.4808 4.75 19.1085 4.75H4.92857C2.20246 4.75 0 6.87266 0 9.5C0 12.1273 2.20246 14.25 4.92857 14.25H64.0714C66.7975 14.25 69 12.1273 69 9.5C69 6.87266 66.7975 4.75 64.0714 4.75H49.8915C49.5192 4.75 49.1776 4.54309 49.0052 4.21305L48.1768 2.62734Z"></path>
              </g>
            </svg>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 69 57" class="svgIcon bin-bottom">
              <path fill="white" d="M63.9723 3.04906C64.0092 3.62279 63.551 4.11106 62.9723 4.11106H6.02772C5.44905 4.11106 4.99084 3.62279 5.02772 3.04906L8.27772 53.8615C8.52772 57.6615 11.8277 60.6111 15.7777 60.6111H53.2223C57.1723 60.6111 60.4723 57.6615 60.7223 53.8615L63.9723 3.04906Z"></path>
            </svg>
          </button>` 
        : '';

    replyDiv.innerHTML = `
      <div class="reply-content">${reply.content}</div>
      <div class="reply-footer">
        <div class="reply-actions">
          <span class="reply-author">Replied by ${displayName}</span>
        </div>
        <div class="reply-actions">
          ${deleteButton}
        </div>
      </div>
    `;

    // Add upvote button and handlers
    const upvoteBtn = createUpvoteButton(replyKey, category, 'reply', reply.upvoteCount || 0, postId);
    replyDiv.querySelector('.reply-actions').prepend(upvoteBtn);

    if (deleteButton) {
      replyDiv.querySelector(".delete-reply-btn").addEventListener("click", (e) => {
        e.stopPropagation();
        if (confirm("Are you sure you want to delete this reply?")) {
          firebase.database().ref(`categories/${category}/threads/${postId}/replies/${replyKey}`).remove()
            .then(() => console.log("Reply deleted successfully"))
            .catch((error) => console.error("Error deleting reply:", error));
        }
      });
    }
  }

  return replyDiv;
}

// Update the handleNotificationClick function to better handle both upvote and reply notifications
function handleNotificationClick(notification) {
  // Mark as read
  db.ref(`users/${auth.currentUser.uid}/notifications/${notification.key}/read`)
    .set(true);

  // Navigate to the relevant content based on type
  if (notification.sourceId) {
    if (notification.type === 'reply') {
      // For reply notifications, navigate to the post that was replied to
      db.ref('categories').once('value', (snapshot) => {
        snapshot.forEach((categorySnapshot) => {
          const categoryKey = categorySnapshot.key;
          const threadRef = db.ref(`categories/${categoryKey}/threads/${notification.sourceId}`);
          
          threadRef.once('value', (threadSnapshot) => {
            if (threadSnapshot.exists()) {
              // Found the post, open it
              openPost(categoryKey, notification.sourceId, threadSnapshot.val());
              return true;
            }
          });
        });
      });
    } else if (notification.type === 'upvote') {
      // For upvote notifications, try to find the post or reply that was upvoted
      db.ref('categories').once('value', (snapshot) => {
        let found = false;
        
        snapshot.forEach((categorySnapshot) => {
          if (found) return;
          
          const categoryKey = categorySnapshot.key;
          const threadsRef = categorySnapshot.child('threads');
          
          threadsRef.forEach((threadSnapshot) => {
            if (found) return;
            
            const threadKey = threadSnapshot.key;
            
            // Check if this is the upvoted post
            if (threadKey === notification.sourceId) {
              openPost(categoryKey, threadKey, threadSnapshot.val());
              found = true;
              return;
            }
            
            // Check if this is a reply in this thread
            const repliesRef = threadSnapshot.child('replies');
            repliesRef.forEach((replySnapshot) => {
              if (replySnapshot.key === notification.sourceId) {
                openPost(categoryKey, threadKey, threadSnapshot.val());
                found = true;
                return;
              }
            });
          });
        });
      });
    }
  }
  
  // Close the dropdown
  document.querySelector('.notifications-dropdown').classList.remove('active');
}

// Update the addNotification function for clarity
function addNotification(userId, message, type, sourceId) {
  if (!userId || userId === auth.currentUser?.uid) return;

  const notificationRef = db.ref(`users/${userId}/notifications`).push();
  notificationRef.set({
    message,
    type,  // 'upvote', 'reply', etc.
    sourceId,  // postId or replyId
    timestamp: firebase.database.ServerValue.TIMESTAMP,
    read: false
  }).catch(error => {
    console.error("Error adding notification:", error);
  });
}

// Update the loadNotifications function to include reply-specific icon
function loadNotifications() {
  if (!auth.currentUser) return;
  
  const notificationList = document.querySelector('.notification-list');
  if (!notificationList) return;
  
  db.ref(`users/${auth.currentUser.uid}/notifications`)
    .orderByChild('timestamp')
    .limitToLast(10)
    .on('value', (snapshot) => {
      notificationList.innerHTML = '';
      const notifications = [];
      let unreadCount = 0;
      
      snapshot.forEach((notif) => {
        const notification = {
          key: notif.key,
          ...notif.val()
        };
        notifications.unshift(notification);
        if (!notification.read) unreadCount++;
      });

      // Update notification bell badge
      const bell = document.getElementById('notification-bell');
      if (unreadCount > 0) {
        bell.setAttribute('data-count', unreadCount);
        bell.classList.add('has-notifications');
      } else {
        bell.removeAttribute('data-count');
        bell.classList.remove('has-notifications');
      }

      // Render notifications
      notifications.forEach((notif) => {
        const div = document.createElement('div');
        div.className = `notification-item ${notif.read ? '' : 'unread'}`;
        div.dataset.key = notif.key;
        div.dataset.type = notif.type;
        div.dataset.sourceId = notif.sourceId;
        
        // Add icon based on notification type
        const icon = notif.type === 'upvote' ? '👍' : 
                     notif.type === 'reply' ? '💬' : '📢';
        
        div.innerHTML = `
          <span class="notification-icon">${icon}</span>
          <span class="notification-message">${notif.message}</span>
          <span class="notification-time">${formatTimestamp(notif.timestamp)}</span>
        `;
        
        // Add click handler to mark as read and navigate
        div.addEventListener('click', () => handleNotificationClick(notif));
        
        notificationList.appendChild(div);
      });
    });
}

// ...existing code...

// Update the Reply button click handler to properly add notifications
replyBtn.addEventListener("click", () => {
  const content = replyQuill.root.innerHTML;
  if (content.trim() !== '<p><br></p>') {
    const user = auth.currentUser;
    
    // Get post author ID
    db.ref(`categories/${currentCategory}/threads/${currentPostId}`)
      .once('value')
      .then((snapshot) => {
        const post = snapshot.val();
        
        // Create new reply with proper data
        const newReply = {
          content: content,
          userId: user.uid,
          timestamp: firebase.database.ServerValue.TIMESTAMP,
          user: user.email // Keep for backward compatibility
        };
        
        // Push the reply to database
        db.ref(`categories/${currentCategory}/threads/${currentPostId}/replies`).push(newReply)
          .then((replyRef) => {
            // Clear the reply editor
            replyQuill.setText('');
            
            // Send notification to post author if it's not the current user
            if (post.userId && post.userId !== user.uid) {
              // Create a proper notification
              const notificationData = {
                message: `${user.email} replied to your post`,
                type: 'reply',
                sourceId: currentPostId,
                timestamp: firebase.database.ServerValue.TIMESTAMP,
                read: false
              };
              
              // Add notification directly to the user's notifications
              db.ref(`users/${post.userId}/notifications`).push(notificationData)
                .catch(error => console.error("Error sending reply notification:", error));
            }
          })
          .catch(error => {
            console.error("Error adding reply:", error);
            alert("Error posting reply");
          });
      })
      .catch(error => {
        console.error("Error fetching post data:", error);
        alert("Error posting reply");
      });
  } else {
    alert("Reply cannot be empty!");
  }
});

// ...existing code...

// Update the loadNotifications function to properly display different notification types
function loadNotifications() {
  if (!auth.currentUser) return;
  
  const notificationList = document.querySelector('.notification-list');
  if (!notificationList) return;
  
  db.ref(`users/${auth.currentUser.uid}/notifications`)
    .orderByChild('timestamp')
    .limitToLast(10)
    .on('value', (snapshot) => {
      notificationList.innerHTML = '';
      const notifications = [];
      let unreadCount = 0;
      
      snapshot.forEach((notif) => {
        const notification = {
          key: notif.key,
          ...notif.val()
        };
        notifications.unshift(notification);
        if (!notification.read) unreadCount++;
      });

      // Update notification bell badge
      const bell = document.getElementById('notification-bell');
      if (unreadCount > 0) {
        bell.setAttribute('data-count', unreadCount);
        bell.classList.add('has-notifications');
      } else {
        bell.removeAttribute('data-count');
        bell.classList.remove('has-notifications');
      }

      // Render notifications
      notifications.forEach((notif) => {
        const div = document.createElement('div');
        div.className = `notification-item ${notif.read ? '' : 'unread'}`;
        div.dataset.key = notif.key;
        div.dataset.type = notif.type || 'general';
        div.dataset.sourceId = notif.sourceId || '';
        
        // Select icon based on notification type
        let icon = '📢'; // Default icon
        if (notif.type === 'upvote') icon = '👍';
        if (notif.type === 'reply') icon = '💬';
        
        div.innerHTML = `
          <span class="notification-icon">${icon}</span>
          <span class="notification-message">${notif.message}</span>
          <span class="notification-time">${formatTimestamp(notif.timestamp)}</span>
        `;
        
        // Add click handler to mark as read and navigate
        div.addEventListener('click', () => {
          // Mark as read in database
          db.ref(`users/${auth.currentUser.uid}/notifications/${notif.key}/read`).set(true);
          
          // Remove unread styling
          div.classList.remove('unread');
          
          // Navigate based on notification type
          if (notif.sourceId) {
            navigateToSource(notif.type, notif.sourceId);
          }
          
          // Close dropdown
          document.querySelector('.notifications-dropdown').classList.remove('active');
        });
        
        notificationList.appendChild(div);
      });
    });
}

// New function to handle navigation to different source types
function navigateToSource(type, sourceId) {
  if (!sourceId) return;
  
  // For both reply and upvote notifications, we need to find the relevant thread
  db.ref('categories').once('value', (snapshot) => {
    snapshot.forEach((categorySnapshot) => {
      const categoryKey = categorySnapshot.key;
      const threadsRef = categorySnapshot.child('threads');
      
      threadsRef.forEach((threadSnapshot) => {
        const threadKey = threadSnapshot.key;
        
        // For direct thread matches (post notifications)
        if (threadKey === sourceId) {
          const threadData = threadSnapshot.val();
          openPost(categoryKey, threadKey, threadData);
          return true; // Break the loop
        }
        
        // For replies within threads
        const repliesRef = threadSnapshot.child('replies');
        let replyFound = false;
        
        repliesRef.forEach((replySnapshot) => {
          if (replySnapshot.key === sourceId) {
            const threadData = threadSnapshot.val();
            openPost(categoryKey, threadKey, threadData);
            replyFound = true;
            return true; // Break the inner loop
          }
        });
        
        if (replyFound) return true; // Break the outer loop
      });
    });
  });
}

// ...existing code...
