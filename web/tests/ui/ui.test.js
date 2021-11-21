const { Builder, By, Key, logging } = require("selenium-webdriver")
const fs = require("fs")
const { Browsers, getElementById, takeScreenshot } = require("./browsers")

const getBaseUrl = () => {
  return process.env.BASE_URL || "http://localhost:8080"
}

const logIn = async browser => {
  await browser.get(getBaseUrl() + "/login")

  let email = await getElementById(browser, "email")
  email.clear()
  email.sendKeys("test@test.com")

  let password = await getElementById(browser, "password")
  password.clear()
  password.sendKeys("test123")

  let submit = await getElementById(browser, "submit")
  submit.click()
}

describe("UI Tests", () => {
  afterAll(async () => {
    Browsers.forEach(async item => {
      await item[1].quit()
    })
  })

  test.each(Browsers)("index renders on %s", async (browserName, browser) => {
    await browser.get(getBaseUrl())
    const value = (await browser.findElement(By.id("slogan")).getText()) != null
    expect(value).toBe(true)
    await takeScreenshot(browserName, browser, "index")
  })

  test.each(Browsers)(
    "can log in with email on %s",
    async (browserName, browser) => {
      await logIn(browser)

      let result = (await getElementById(browser, "logout")) != null
      expect(result).toBe(true)

      await takeScreenshot(browserName, browser, "logged-in")
    },
  )

  test.each(Browsers)("can log out", async (browserName, browser) => {
    await logIn(browser)

    let logOut = await getElementById(browser, "logout")

    await logOut.click()

    let result = (await getElementById(browser, "login")) != null

    expect(result).toBe(true)

    await takeScreenshot(browserName, browser, "logged-out")
  })
})
