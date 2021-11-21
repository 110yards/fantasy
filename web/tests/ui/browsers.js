const { Builder, By, until } = require("selenium-webdriver")
const chrome = require("selenium-webdriver/chrome")
const firefox = require("selenium-webdriver/firefox")
const fs = require("fs")

module.exports.takeScreenshot = async (browserName, browser, imageName) => {
  let data = await browser.takeScreenshot()
  data = data.replace(/^data:image\/png;base64,/, "")

  await fs.writeFile(
    `${__dirname}/.reports/screenshots/${imageName}.${browserName}.png`,
    data,
    "base64",
  )
}

module.exports.getElementById = async (browser, id, timeout = 5000) => {
  const el = await browser.wait(until.elementLocated(By.id(id)), timeout)
  return await browser.wait(until.elementIsVisible(el), timeout)
}

function getChrome() {
  const options = new chrome.Options()
  options.headless()
  options.addArguments("--no-sandbox")
  options.addArguments("--disable-dev-shm-usage")

  let browser = new Builder()
    .forBrowser("chrome")
    .setChromeOptions(options)
    .build()

  return browser
}

function getFirefox() {
  const options = new firefox.Options()
  options.headless()

  let browser = new Builder()
    .forBrowser("firefox")
    .setFirefoxOptions(options)
    .build()

  return browser
}

const browsers = [
  ["chrome", getChrome()],
  ["firefox", getFirefox()],
]

module.exports.Browsers = browsers
