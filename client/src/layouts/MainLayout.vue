<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="leftDrawerOpen = !leftDrawerOpen">
          <q-tooltip> {{ leftDrawerOpen ? 'Hide' : 'Show' }} drawer </q-tooltip>
        </q-btn>

        <q-toolbar-title>
          Simple Chat App
        </q-toolbar-title>

        <q-btn round color="red" class="q-mr-sm" to="/settings">
          <q-avatar color="red" text-color="white" icon="settings"/>
          <q-tooltip>Settings</q-tooltip>
        </q-btn>

        <div v-if="$store.state.user">{{ $store.state.user.username }}</div>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
      content-class="bg-grey-1">
      <q-list>
        <q-item clickable v-ripple exact to="/">
          <q-item-section avatar>
            <q-icon name="home"/>
          </q-item-section>
          <q-item-section>Home</q-item-section>
        </q-item>
        <q-separator/>
        <q-item>
          <q-item-section avatar>
            <q-icon name="contacts"/>
          </q-item-section>
          <q-item-section>Friends</q-item-section>
          <q-item-section class="items-end">
            <q-btn color="accent" icon="add" style="width: 50px" @click="addFriendDialog = true">
              <q-tooltip>Add a friend</q-tooltip>
            </q-btn>
          </q-item-section>
        </q-item>
        <q-item v-for="friend in $store.state.friends" :key="friend" clickable v-ripple @click="viewDM(friend)">
          <q-item-section avatar>
            <q-icon name="account_circle"/>
          </q-item-section>
          <q-item-section> {{ friend }}</q-item-section>
        </q-item>
        <q-separator/>
        <q-item clickable v-ripple exact @click="logout">
          <q-item-section avatar>
            <q-icon name="logout"/>
          </q-item-section>
          <q-item-section>Logout</q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view/>
    </q-page-container>

    <q-dialog v-model="addFriendDialog">
      <q-card>
        <q-card-section class="row items-center">
          <q-avatar icon="contacts" color="primary" text-color="white"/>
          <h6 class="q-ml-sm q-mt-sm q-mb-xs"> Add a New Friend </h6>
        </q-card-section>
        <q-card-section>
          <q-input v-model="addFriendUsername" label="Username"/>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="primary" v-close-popup/>
          <q-btn flat label="Add Friend" color="primary" @click="addFriend"/>
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-layout>
</template>

<script>

import { Auth } from '@aws-amplify/auth'
import { API } from '@aws-amplify/api'

export default {
  name: 'MainLayout',
  data () {
    return {
      leftDrawerOpen: false,
      conversations: [],
      addFriendDialog: false,
      addFriendUsername: ''
    }
  },
  methods: {
    async logout () {
      await Auth.signOut()
      await this.$router.push('/login')
    },
    async addFriend () {
      if (this.addFriendUsername === '')
        return

      try {
        await API.post('api', 'friend-add', {
          body: {
            user: this.addFriendUsername
          }
        })
        await this.$store.dispatch('updateFriendsList')
      } catch (e) {
        console.error(e)
      }
    },
    async viewDM (friend) {
      const path = '/conversation/' + (await API.post('api', 'direct-messages-get', {
        body: {
          friend: friend
        }
      }))['id']
      if (this.$route.path !== path)
        await this.$router.push(path)
    }
  }
}
</script>
