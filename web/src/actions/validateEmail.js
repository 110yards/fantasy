export default v => {
  if (!v) return "Email is required"
  if (/.+@.+\..+/.test(v) == false) "Invalid email"
  return true
}
