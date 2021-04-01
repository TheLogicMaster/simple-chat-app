import Vue from 'vue'
import Vuex from 'vuex'
import { Auth } from '@aws-amplify/auth'
import { API } from '@aws-amplify/api'

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
      user: null,
      conversations: [],
      friends: []
    },
    getters: {
      getConversation: state => id => {
        return state.conversations.find(conversation => conversation.id === id)
      }
    },
    actions: {
      async login ({ commit, dispatch }) {
        const info = await Auth.currentUserInfo()
        commit('set', ['user', {
          username: info.username
        }])
        await dispatch('updateFriendsList')
      },
      async updateConversationList ({ commit, getters }) {
        try {
          const response = await API
            .post('api', 'conversation-list', {
              /*headers: {},
              body: {
                conversation: '1234'
              },
              response: true, // (return the entire Axios response object instead of only response.data)
              queryStringParameters: {
                name: 'param',
              }*/
            })
          let conversations = []
          for (let conversation of response) {
            const existing = getters.getConversation(conversation.id) || {}
            conversations.push({ ...existing, ...conversation })
          }
          commit('set', ['conversations', conversations])
          return true
        } catch (e) {
          console.error(e)
        }
      },
      async updateConversations({ state, dispatch, commit }) {
        try {
          await dispatch('updateConversationList')
          const conversations = []
          for (let conversation of state.conversations)
            conversations.push(await API
              .post('api', 'conversation-get', {
                body: {
                  conversation: conversation.id
                }
              }))
          commit('set', ['conversations', conversations])
          return true
        } catch (e) {
          console.error(e)
        }
      },
      async updateConversation ({ commit, state }, id) {
        try {
          const response = await API
            .post('api', 'conversation-get', {
              body: {
                conversation: id
              }
            })
          let conversations = state.conversations.filter(conversation => conversation.id !== response.id)
          conversations.push(response)
          commit('set', ['conversations', conversations])
          return true
        } catch (e) {
          console.error(e)
        }
      },
      async updateFriendsList ({ commit }) {
        if (!await Auth.currentUserInfo())
          return
        try {
          const response = await API
            .post('api', 'friend-list', {})
          commit('set', ['friends', response])
          return true
        } catch (e) {
          console.error(e)
        }
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
