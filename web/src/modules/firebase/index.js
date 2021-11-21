import firebase from "firebase/app"
import "firebase/auth"
import "firebase/firestore"
import store from "../store"

const firestoreEmulatorPort = process.env.VUE_APP_FIRESTORE_EMULATOR_PORT
const authEmulatorHost = process.env.VUE_APP_AUTH_EMULATOR_HOST

const firebaseApiKey = process.env.VUE_APP_FIREBASE_API_KEY
const firebaseProject = process.env.VUE_APP_FIREBASE_PROJECT

console.log(`project: ${firebaseProject}`)

const config = {
  apiKey: firebaseApiKey,
  authDomain: `${firebaseProject}.firebaseapp.com`,
  projectId: firebaseProject,
  storageBucket: "",
  messagingSenderId: "",
  appId: "",
}

export const app = firebase.initializeApp(config)
export const firestore = firebase.firestore()
export const auth = firebase.auth()

if (firestoreEmulatorPort) {
  console.warn("Firestore Emulator enabled")
  firestore.useEmulator("localhost", firestoreEmulatorPort)
}

if (authEmulatorHost) {
  auth.useEmulator(authEmulatorHost)
}

firebase.auth().onAuthStateChanged(user => {
  store.dispatch("updateUser", user)
})

export const getCurrentUser = () => {
  return new Promise((resolve, reject) => {
    const unsubscribe = firebase.auth().onAuthStateChanged(user => {
      unsubscribe()
      resolve(user)
    }, reject)
  })
}
