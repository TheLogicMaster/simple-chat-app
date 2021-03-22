import Vue from 'vue'
import Vuex from 'vuex'
import { Auth } from '@aws-amplify/auth'

// import example from './module-example'

Vue.use(Vuex)

/*
 * If not building with SSR mode, you can
 * directly export the Store instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Store instance.
 */

export default async function (/* { ssrContext } */) {
  const Store = new Vuex.Store({
    state: {
      user: null
    },
    getters: {

    },
    actions: {
      async login({ commit }) {
        const info = await Auth.currentUserInfo()
        commit('set', ['user', {
          username: info.username
        }])
      }
    },
    mutations: {
      set (state, [variable, value]) {
        state[variable] = value
      }
    },

    // enable strict mode (adds overhead!)
    // for dev mode only
    strict: process.env.DEBUGGING
  })

  if (await Auth.currentUserInfo() !== null)
    await Store.dispatch('login')

  return Store
}
