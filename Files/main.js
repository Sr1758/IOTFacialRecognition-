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


// Event Listeners for Buttons
// Click on Create Account Button
createAccountBtn.addEventListener('click', () => {

    //Display error msg
    if(!(emailSignUpForm.value.includes('@') && emailSignUpForm.value.includes('.'))){
        signUpEmailError.innerText = "Invaild Email! Please Try again.";
        signUpEmailError.style.display = 'block';
    }
    else{
        createUserWithEmailAndPassword(auth, emailSignUpForm.value, passwordSignUpForm.value)
            .then((userCredential) => {
                // Signed up 
                const user = userCredential.user;
                console.log(user)
                
                //Remove error msg
                signUpEmailError.innerText = '';
                signUpEmailError.style.display = 'none';
            })
            .catch((error) => {
                const errorCode = error.code;
                const errorMessage = error.message;
                console.log(errorMessage)
                
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
                // ...
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
