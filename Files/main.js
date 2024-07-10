console.log("main load correctly");

// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { getAuth, 
         createUserWithEmailAndPassword, 
         signInWithEmailAndPassword, 
         GoogleAuthProvider,
         signInWithPopup,
         onAuthStateChanged,
         signOut } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";

// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDKtXsA4mSPqYSclYvbX5Yq9yGNE5tpm5c",
  authDomain: "photos-5766c.firebaseapp.com",
  projectId: "photos-5766c",
  storageBucket: "photos-5766c.appspot.com",
  messagingSenderId: "177177901562",
  appId: "1:177177901562:web:7a0187c9f9e205a6b38c43",
  measurementId: "G-J9B44TZBWV"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth();
const provider = new GoogleAuthProvider();


// logged in and logged out sections
const loggedInView = document.getElementById('logged-in-view')
const loggedOutView = document.getElementById('logged-out-view')
const userEmail = document.getElementById('user-email')

// email and password for signin
const emailSignInForm = document.getElementById('signin-email-input')
const passwordSignInForm = document.getElementById('signin-password-input')

// email and password for signup
const emailSignUpForm = document.getElementById('signup-email-input')
const passwordSignUpForm = document.getElementById('signup-password-input')

// Buttons
const signInGoogleBtn = document.getElementById('sign-in-with-google-btn')
const signUpGoogleBtn = document.getElementById('sign-up-with-google-btn')
const googleBtns = [signInGoogleBtn, signUpGoogleBtn]

const createAccountBtn = document.getElementById('sign-up-btn')
const loginBtn = document.getElementById('sign-in-btn')
const logoutBtn = document.getElementById('logout-button')

// Messages
const passwordError = document.getElementById('password-error-message');
const signUpEmailError = document.getElementById('Sign-up-email-error-message');
const signUpPasswordError = document.getElementById('Sign-up-password-error-message');


// Detects state change
onAuthStateChanged(auth, (user) => {
    if (user) {
      // User is signed in, see docs for a list of available properties
      // https://firebase.google.com/docs/reference/js/auth.user
      const uid = user.uid;
      const email = user.email
      loggedInView.style.display = 'block'
      userEmail.innerText = email
      loggedOutView.style.display = 'none'
      // ...
    } else {
      // User is signed out
      // ...
      loggedInView.style.display = 'none'
      loggedOutView.style.display = 'block'
    }
  });

  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$/;

// Event Listeners for Buttons
// Click on Create Account Button
createAccountBtn.addEventListener('click', () => {
//Case: password too short

    //Display error msg
    if(emailSignUpForm.value.includes(' ')){  //spaces in email error msg
        signUpEmailError.innerText = "Invaild Email! Spaces are not allowed";
        signUpEmailError.style.display = 'block';
    }
    else if(!passwordRegex.test(passwordSignUpForm.value)){  //Doesn't meet password requirements
        signUpPasswordError.innerText = "Password must contain at least one uppercase letter, one lowercase letter, one number, one special character, and be at least 6 characters long.";
        signUpPasswordError.style.display = 'block';
    }
    else{  //Remove error msg
        signUpEmailError.innerText = '';
        signUpPasswordError.innerText = '';
        signUpEmailError.style.display = 'none';
        signUpPasswordError.style.display = 'none';

        createUserWithEmailAndPassword(auth, emailSignUpForm.value, passwordSignUpForm.value)
            .then((userCredential) => {
                // Signed up 
                const user = userCredential.user;
                console.log(user)
                
            })
            .catch((error) => {
                const errorCode = error.code;
                const errorMessage = error.message;
                console.log(errorMessage)

            // email exists already error msg
            if (errorCode === 'auth/email-already-in-use') {
                signUpEmailError.innerText = 'Email already in use. Please use a different email.';
                signUpEmailError.style.display = 'block';
            } 
            else if(errorCode === 'auth/invalid-email'){  //Email is not vaild via firebase
                signUpEmailError.innerText = "Invaild Email! Please Try again.";
                signUpEmailError.style.display = 'block';
            }
            else if(errorcode === 'auth/missing-password'){
                signUpPasswordError.innerText = "Invaild Password! Please Try again.";
                signUpPasswordError.style.display = 'block';
            }
            else if(errorcode === 'auth/weak-password'){
                signUpPasswordError.innerText = "Weak Password! Must be at least 6 characters.";
                signUpPasswordError.style.display = 'block';
            }
                    
        });
    }

    console.log('Create Account Button Clicked')
    console.log(`Email: ${emailSignUpForm.value}`)
    console.log(`Password: ${passwordSignUpForm.value}`)
})

// Click on Login Button
loginBtn.addEventListener('click', () => {
    signInWithEmailAndPassword(auth, emailSignInForm.value, passwordSignInForm.value)
        .then((userCredential) => {
            // Signed in 
            const user = userCredential.user;
            console.log(user)


            // Clear password error msg
            passwordError.innerText = '';
            passwordError.style.display = 'none';
        })
        .catch((error) => {
            const errorCode = error.code;
            const errorMessage = error.message;
            console.log(errorMessage)

            // Display error message
            passwordError.innerText = 'Incorrect email/password! Please try again.';
            passwordError.style.display = 'block'; // Show the error message div
        });

    console.log('Login Clicked')
    console.log(`Email: ${emailSignInForm.value}`)
    console.log(`Password: ${passwordSignInForm.value}`)
})

// Click on Google Signin
googleBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        signInWithPopup(auth, provider)
            .then((result) => {
                // This gives you a Google Access Token. You can use it to access the Google API.
                const credential = GoogleAuthProvider.credentialFromResult(result);
                const token = credential.accessToken;
                // The signed-in user info.
                const user = result.user;
                console.log(user);
                // IdP data available using getAdditionalUserInfo(result)
                
                // Clear password error msg
                passwordError.innerText = '';
                passwordError.style.display = 'none';
            }).catch((error) => {
                // Handle Errors here.
                const errorCode = error.code;
                const errorMessage = error.message;
                console.log(errorMessage);
                // The email of the user's account used.
                const email = error.customData.email;
                // The AuthCredential type that was used.
                const credential = GoogleAuthProvider.credentialFromError(error);
                // ...
            });
        console.log('Google Signin Clicked');
    });
});



// logout button
logoutBtn.addEventListener('click', () => {
    signOut(auth).then(() => {
        // Sign-out successful.
      }).catch((error) => {
        // An error happened.
      });
      
    console.log('Logout Clicked')
})

document.addEventListener('DOMContentLoaded', function() {
    const userEmailElement = document.getElementById('user-email');
    const firstNameInputElement = document.getElementById('first-name-input');
    const lastNameInputElement = document.getElementById('last-name-input');
    const addNameButton = document.querySelector('.add-name-btn');
    const nameDropdown = document.getElementById('name-dropdown');
    const albumsContainer = document.getElementById('albums-container');
    const photoUploadContainer = document.querySelector('.photo-upload-container');
    const uploadFormElement = document.getElementById('photo-upload-form');
    const photoFileInputElement = document.getElementById('photo-file-input');

    // Example user email (replace with actual login implementation)
    userEmailElement.textContent = 'user@example.com';

    // Placeholder photo URL
    const placeholderPhotoUrl = 'images/PlaceholderPhoto.jpg'; // Adjust path if necessary

    // Event listener for adding a name
    addNameButton.addEventListener('click', function() {
        const firstName = firstNameInputElement.value.trim();
        const lastName = lastNameInputElement.value.trim();
        if (firstName !== '' && lastName !== '') {
            const fullName = `${firstName} ${lastName}`;
            const option = document.createElement('option');
            option.textContent = fullName;
            option.value = fullName;
            nameDropdown.appendChild(option);
            nameDropdown.disabled = false; // Enable dropdown after adding a name
            createAlbum(fullName); // Create album for the added name
            firstNameInputElement.value = '';
            lastNameInputElement.value = '';
        }
    });

    // Function to create an album for a name
    function createAlbum(name) {
        const albumDiv = document.createElement('div');
        albumDiv.classList.add('album');

        const nameElement = document.createElement('h4');
        nameElement.textContent = name;
        albumDiv.appendChild(nameElement);

        const imgElement = document.createElement('img');
        imgElement.src = placeholderPhotoUrl;
        imgElement.alt = `${name}'s Album`;
        albumDiv.appendChild(imgElement);

        albumsContainer.appendChild(albumDiv);
    }

    // Event listener for selecting a name from dropdown
    nameDropdown.addEventListener('change', function() {
        const selectedName = nameDropdown.value;
        if (selectedName !== '') {
            document.getElementById('current-album-name').textContent = `${selectedName}'s Album`;
            photoUploadContainer.style.display = 'block';
        } else {
            photoUploadContainer.style.display = 'none';
        }
    });

    // Event listener for photo upload form submission
    uploadFormElement.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission
        const selectedAlbumName = document.getElementById('current-album-name').textContent;
        const uploadedFile = photoFileInputElement.files[0];
        
        // Example: Handle file upload (replace with actual upload code)
        if (uploadedFile && selectedAlbumName !== '') {
            // Process the file upload here
            console.log(`Uploaded file '${uploadedFile.name}' to ${selectedAlbumName}`);

            // Update placeholder photo with uploaded photo (example)
            const albums = document.querySelectorAll('.album');
            albums.forEach(album => {
                const albumName = album.querySelector('h4').textContent;
                if (albumName === selectedAlbumName) {
                    const albumImg = album.querySelector('img');
                    albumImg.src = URL.createObjectURL(uploadedFile); // Assuming uploadedFile is a Blob/File
                }
            });

            // Reset form after successful upload
            uploadFormElement.reset();
        }
    });

    // Example: Logout functionality
    document.getElementById('logout-button').addEventListener('click', function() {
        // Example: Implement logout action
        console.log('Logout clicked');
    });
});

