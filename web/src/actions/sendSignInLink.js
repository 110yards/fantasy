import { userExists } from "../api/110yards/user"
import eventBus from "../modules/eventBus"
import { auth } from "../modules/firebase"

export default async (email, checkForAccount) => {
  try {
    eventBus.$emit("loading-start")

    if (checkForAccount) {
      let exists = await userExists(email)
      if (!exists) {
        eventBus.$emit("show-error", "No account exists with that email")
        return
      }
    }

    await auth.sendSignInLinkToEmail(email, {
      url: `${process.env.VUE_APP_WEB_URL}/passwordless`,
      handleCodeInApp: true,
    })
    localStorage.setItem("emailForSignIn", email)
    return true
  } catch (error) {
    eventBus.$emit("show-error", error)
    return false
  } finally {
    eventBus.$emit("loading-stop")
  }
}
