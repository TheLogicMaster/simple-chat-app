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

export default ({ Vue }) => {
  Vue.filter('truncate', function (value, size) {
    if (!value)
      return ''
    value = value.toString()
    if (value.length <= size)
      return value
    return value.substr(0, size) + '...'
  })
}

export {
  utils
}
