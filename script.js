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

  // Signup Functionality
  signupBtn.addEventListener("click", () => {
    document.getElementById("signup-form").style.display = "flex";
  });

  document.getElementById("signup-submit").addEventListener("click", () => {
    const email = document.getElementById("signup-email").value;
    const password = document.getElementById("signup-password").value;
    
    auth.createUserWithEmailAndPassword(email, password)
      .then((userCredential) => {
        const user = userCredential.user;
        
        // First create the user data
        db.ref("users/" + user.uid).set({
            email: user.email,
        }).then(() => {
            // Then increment the registered users counter
            const counterRef = db.ref('metrics/registeredUsers');
            counterRef.transaction(currentValue => (currentValue || 0) + 1);
        });

        document.getElementById("signup-form").style.display = "none";
        alert("User signed up successfully!");
        signupBtn.style.display = "none";
        loginBtn.style.display = "none";
        logoutBtn.style.display = "inline-block";
        newPostSection.style.display = "block";
      })
      .catch((error) => alert(error.message));
  });

  // Login Functionality
  loginBtn.addEventListener("click", () => {
    document.getElementById("login-form").style.display = "flex";
  });

  // Add new login form submission handler
  document.getElementById("login-submit").addEventListener("click", () => {
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;
    
    auth.signInWithEmailAndPassword(email, password)
      .then(() => {
        document.getElementById("login-form").style.display = "none";
        loginBtn.style.display = "none";
        logoutBtn.style.display = "inline-block";
        newPostSection.style.display = "block";
      })
      .catch((error) => alert(error.message));
  });
  
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
    if (user) {
      logoutBtn.style.display = "inline-block";
      loginBtn.style.display = "none";
      signupBtn.style.display = "none";
      userEmailElement.style.display = "inline-block";
      userEmailElement.textContent = user.email;
      notificationBell.style.display = "flex";
      loadNotifications();
    } else {
      logoutBtn.style.display = "none";
      loginBtn.style.display = "inline-block";
      signupBtn.style.display = "inline-block";
      userEmailElement.style.display = "none";
      userEmailElement.textContent = "";
      notificationBell.style.display = "none";
    }
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
    postContentDiv.innerHTML = `
      <div class="post">
        <div class="post-content">${post.content}</div>
        <div class="post-footer">
          <span class="post-author">Posted by ${userEmail}</span>
        </div>
      </div>
    `;
    document.querySelector('.categories').style.display = 'none';
    postDetailsSection.style.display = "block";
    loadReplies(category, postId);
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
      // Check for mentions
      const mentionRegex = /@([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)/g;
      const mentions = content.match(mentionRegex);
      
      if (mentions) {
        mentions.forEach(mention => {
          const mentionedEmail = mention.substring(1);
          // Find user by email and add notification
          db.ref('users').orderByChild('email').equalTo(mentionedEmail).once('value', snapshot => {
            snapshot.forEach(userSnapshot => {
              addNotification(userSnapshot.key, `${user.email} mentioned you in a reply`);
            });
          });
        });
      }
      db.ref(`categories/${currentCategory}/threads/${currentPostId}/replies`).push({
        content: content,
        user: user.email
      });
      replyQuill.setText('');
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
        db.ref(`categories/${category}/threads`).push({
          content: content,
          userId: user.uid,
          timestamp: firebase.database.ServerValue.TIMESTAMP
        }).then(() => {
          postQuill.setText('');
          newPostModal.style.display = "none";
        }).catch((error) => {
          console.error("Error adding post:", error);
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
    
    postsRef.on("value", async (snapshot) => {
      categoryPosts.innerHTML = "";
      
      if (!snapshot.exists()) {
        return; // Remove the "no posts yet!" message
      }

      const posts = [];
      snapshot.forEach((thread) => {
        posts.unshift({ key: thread.key, ...thread.val() }); // Add newest first
      });

      const postsToShow = isPreview ? posts.slice(0, 2) : posts; // Show only 2 posts for preview
      const promises = postsToShow.map(post => 
        db.ref("users/" + post.userId).once("value")
          .then(userSnapshot => {
            const userData = userSnapshot.val();
            const userEmail = userData?.email || "deleted user";
            const postDiv = createPostElement(post, category, userEmail);
            categoryPosts.appendChild(postDiv);
          })
      );
      
      await Promise.all(promises);
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
    button.addEventListener('click', (e) => {
      e.stopPropagation(); // Prevent category click event
      const category = button.closest('.category');
      category.classList.toggle('expanded');
      if (category.classList.contains('expanded')) {
        loadCategoryPosts(category.dataset.category, false);
        button.textContent = 'Show less';
      } else {
        loadCategoryPosts(category.dataset.category, true);
        button.textContent = 'See all';
      }
    });
  });

  // Load previews when page loads
  document.addEventListener('DOMContentLoaded', () => {
    const categories = ['updates', 'issues', 'discussions', 'suggestions'];
    categories.forEach(category => loadCategoryPosts(category, true));
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
  
    upvoteBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      if (!auth.currentUser) {
        alert('Please login to upvote');
        return;
      }
  
      const upvoteRef = db.ref(`${basePath}/upvotes/${auth.currentUser.uid}`);
      const countRef = db.ref(`${basePath}/upvoteCount`);
      
      upvoteRef.once('value', (snapshot) => {
        if (snapshot.exists()) {
          // Remove upvote
          upvoteRef.remove();
          countRef.transaction(count => (count || 1) - 1);
          upvoteBtn.classList.remove('active');
        } else {
          // Add upvote
          upvoteRef.set(true);
          countRef.transaction(count => (count || 0) + 1);
          upvoteBtn.classList.add('active');
  
          // Get the content owner's info and send notification
          db.ref(basePath).once('value', (itemSnapshot) => {
            const itemData = itemSnapshot.val();
            // For replies, we need to check the user property
            const ownerId = isReply ? 
              // First try to find the userId, fallback to finding user by email
              (itemData.userId || new Promise((resolve) => {
                db.ref('users').orderByChild('email').equalTo(itemData.user).once('value', snapshot => {
                  snapshot.forEach(userSnap => resolve(userSnap.key));
                });
              })) :
              itemData.userId;
  
            // Handle both direct userId and Promise cases
            Promise.resolve(ownerId).then(finalOwnerId => {
              if (finalOwnerId && finalOwnerId !== auth.currentUser.uid) {
                const notifRef = db.ref(`users/${finalOwnerId}/notifications`).push();
                notifRef.set({
                  message: `${auth.currentUser.email} upvoted your ${itemType}`,
                  timestamp: firebase.database.ServerValue.TIMESTAMP,
                  read: false,
                  type: 'upvote',
                  itemId: itemId,
                  category: category
                });
              }
            });
          });
        }
      });
    });
  
    return upvoteBtn;
  }
  
  // Modify the post creation in loadCategoryPosts function
  function createPostElement(post, category, userEmail) {
    const postDiv = document.createElement("div");
    postDiv.classList.add("post");
    
    const deleteButton = auth.currentUser && auth.currentUser.uid === post.userId 
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
    
    postDiv.innerHTML = `
      <div class="post-content">${post.content}</div>
      <div class="post-footer">
        <div class="post-actions">
          <span class="post-author">Posted by ${userEmail}</span>
        </div>
        <div class="post-actions">
          ${deleteButton}
        </div>
      </div>
    `;
  
    const upvoteBtn = createUpvoteButton(post.key, category, 'post', post.upvoteCount || 0, null);
    postDiv.querySelector('.post-actions').prepend(upvoteBtn);
  
    // Add your existing event listeners
    if (deleteButton) {
      postDiv.querySelector(".delete-btn").addEventListener("click", (event) => {
        event.stopPropagation();
        deletePost(category, post.key);
      });
    }
    
    postDiv.addEventListener("click", () => openPost(category, post.key, post, userEmail));
    return postDiv;
  }
  
  // Modify the reply creation in loadReplies function
  function createReplyElement(reply, replyKey, category, postId) {
    const replyDiv = document.createElement("div");
    replyDiv.classList.add("reply");
    
    const deleteButton = auth.currentUser && auth.currentUser.email === reply.user 
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
          <span class="reply-author">Replied by ${reply.user}</span>
        </div>
        <div class="reply-actions">
          ${deleteButton}
        </div>
      </div>
    `;
  
    const upvoteBtn = createUpvoteButton(replyKey, category, 'reply', reply.upvoteCount || 0, postId);
    replyDiv.querySelector('.reply-actions').prepend(upvoteBtn);
  
    if (deleteButton) {
      replyDiv.querySelector(".delete-reply-btn").addEventListener("click", (e) => {
        e.stopPropagation();
        if (confirm("Are you sure you want to delete this reply?")) {
          db.ref(`categories/${category}/threads/${postId}/replies/${replyKey}`).remove()
            .then(() => console.log("Reply deleted successfully"))
            .catch((error) => console.error("Error deleting reply:", error));
        }
      });
    }
  
    return replyDiv;
  }
  
  function addNotification(userId, message) {
    db.ref(`users/${userId}/notifications`).push({
      message: message,
      timestamp: firebase.database.ServerValue.TIMESTAMP,
      read: false
    });
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
        db.ref(`users/${auth.currentUser.uid}/notifications/${notifKey}/read`).set(true);
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
  
} else {
    console.error("Firebase is not loaded");
}