import Vue from 'vue'

let utils = {
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
  },
  cloneObject(obj) {
    return JSON.parse(JSON.stringify(obj))
  },
  isObjectEmpty(obj) {
    return Object.keys(obj).length === 0
  }
}
Vue.prototype.$utils = utils

export {
  utils
}
