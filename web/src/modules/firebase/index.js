import firebase from "firebase/app"
import "firebase/auth"
import "firebase/firestore"
import "firebase/database"
import store from "../store"

const firestoreEmulatorPort = process.env.VUE_APP_FIRESTORE_EMULATOR_PORT
const rtdbEmulatorPort = process.env.VUE_APP_RTDB_EMULATOR_PORT
const authEmulatorHost = process.env.VUE_APP_AUTH_EMULATOR_HOST

const firebaseApiKey = process.env.VUE_APP_FIREBASE_API_KEY
const firebaseProject = process.env.VUE_APP_FIREBASE_PROJECT
const webUrl = process.env.VUE_APP_WEB_URL.replace(/^https?:\/\//, "")

console.log(`project: ${firebaseProject}`)

const databaseUrl = () => {
  if (rtdbEmulatorPort) {
    return `http://127.0.0.1:${rtdbEmulatorPort}/?ns=${firebaseProject}`
  } else {
    return `https://${firebaseProject}.firebaseio.com`
  }
}

const config = {
  apiKey: firebaseApiKey,
  authDomain: webUrl,
  projectId: firebaseProject,
  storageBucket: "",
  messagingSenderId: "",
  appId: "",
  databaseURL: databaseUrl(),
}

export const app = firebase.initializeApp(config)
export const firestore = firebase.firestore()
export const auth = firebase.auth()
export const rtdb = firebase.database()

if (firestoreEmulatorPort) {
  console.warn("Firestore Emulator enabled")
  firestore.useEmulator("localhost", firestoreEmulatorPort)
}

if (authEmulatorHost) {
  auth.useEmulator(authEmulatorHost)
}

if (rtdbEmulatorPort) {
  rtdb.useEmulator("localhost", rtdbEmulatorPort)
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
