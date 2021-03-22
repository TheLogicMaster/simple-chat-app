<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="leftDrawerOpen = !leftDrawerOpen"
        />

        <q-toolbar-title>
          Simple Chat App
        </q-toolbar-title>

        <q-btn round color="red" class="q-mr-sm" to="/settings">
          <q-avatar color="red" text-color="white" icon="settings" />
        </q-btn>

        <div>{{ $store.state.user.username }}</div>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
      content-class="bg-grey-1"
    >
      <q-list>
        <q-item clickable v-ripple exact @click="logout">
          <q-item-section avatar>
            <q-icon name="logout" />
          </q-item-section>
          <q-item-section>Logout</q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script>

import { Auth } from '@aws-amplify/auth'

export default {
  name: 'MainLayout',
  data () {
    return {
      leftDrawerOpen: false,
      conversations: []
    }
  },
  methods: {
    async logout() {
      await Auth.signOut()
      await this.$router.push('/login')
    }
  }
}
</script>
