<template>
  <q-page class="q-pa-sm">
    <q-list style="padding-top: 50px">
      <q-card v-ripple flat bordered class="q-pa-sm q-ma-xs q-hoverable"
              v-for="conversation of $store.state.conversations"
              :key="conversation.id" @click="$router.push('/conversation/' + conversation.id).then()">
        <span class="q-focus-helper"></span>
        <q-card-section horizontal>
          <div class="col">
            <div class="text-h6 inline-block">{{ conversation.name }}</div>
            <div class="text-subtitle2">{{ getLastMessage(conversation.messages) | truncate(100) }}</div>
          </div>

          <q-card-actions class="justify-around q-px-md">
            <q-btn flat round color="primary" icon="create" v-on:click.stop.prevent="showEditDialog(conversation.id)">
              <q-tooltip>Manage conversation</q-tooltip>
            </q-btn>
            <q-btn flat round color="accent" icon="delete"
                   v-on:click.stop.prevent="deleteConversation(conversation.id)">
              <q-tooltip>Delete conversation</q-tooltip>
            </q-btn>
            <q-btn flat round color="primary" icon="directions_walk"
                   v-on:click.stop.prevent="leaveConversation(conversation.id)">
              <q-tooltip>Leave conversation</q-tooltip>
            </q-btn>
          </q-card-actions>
        </q-card-section>
      </q-card>
    </q-list>

    <q-page-sticky position="top" expand class="bg-secondary text-white">
      <q-toolbar>
        <q-btn round :loading="loading" color="accent" @click="refresh" icon="refresh">
          <q-tooltip>Refresh conversations</q-tooltip>
        </q-btn>
        <q-toolbar-title>Your Conversations</q-toolbar-title>
      </q-toolbar>
    </q-page-sticky>

    <q-page-sticky position="top-right" :offset="[10, 10]">
      <q-btn fab icon="add" color="accent" @click="showCreateDialog">
        <q-tooltip>Create conversation</q-tooltip>
      </q-btn>
    </q-page-sticky>

    <q-dialog v-model="createGroupDialog">
      <q-card>
        <q-card-section class="row items-center">
          <q-avatar icon="question_answer" color="primary" text-color="white"/>
          <h6 class="q-ml-sm q-mt-sm q-mb-xs"> Create a Group Chat</h6>
        </q-card-section>
        <q-card-section>
          <q-input outlined v-model="groupName" label="Group Name"/>
        </q-card-section>
        <q-card-section>
          <q-select outlined clearable v-model="groupUsers" use-input use-chips multiple input-debounce="0"
                    @new-value="createFriendOption" :options="groupUserOptions" style="max-width: 400px" label="Users"/>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="primary" v-close-popup/>
          <q-btn flat label="Create Chat" color="primary" @click="createGroupChat"/>
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="editGroupDialog">
      <q-card v-if="conversation">
        <q-card-section class="row justify-between">
          <h6 class="q-ml-sm q-mt-sm q-mb-xs q-mr-md"> Manage {{ conversation.name | truncate(25) }}</h6>
          <q-btn color="primary" label="Invite" @click="showInviteDialog" :disable="conversation.dm">
            <q-tooltip>Invite a user to the conversation</q-tooltip>
          </q-btn>
        </q-card-section>
        <q-card-section>
          <q-card v-for="user in conversation.users" :key="user" class="row items-start" flat bordered>
            <q-card-section style="min-width: 150px"> {{ user }}</q-card-section>
            <q-card-section class="q-mr-sm"> {{ conversation.admins.includes(user) ? 'Admin' : 'Member' }}
            </q-card-section>
            <q-card-actions class="col" align="right">
              <q-btn :disable="!conversation.admins.includes($store.state.user.username)
              || conversation.admins.includes(user)" flat color="primary" label="Promote" @click="promoteUser(user)">
                <q-tooltip>Promote user to an admin</q-tooltip>
              </q-btn>
              <q-btn :disable="!conversation.admins.includes($store.state.user.username)
              || conversation.admins.includes(user)" flat color="red" label="Kick" @click="kickUser(user)">
                <q-tooltip>Kick user from conversation</q-tooltip>
              </q-btn>
            </q-card-actions>
          </q-card>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Close" color="primary" v-close-popup/>
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="inviteUserDialog">
      <q-card>
        <q-card-section class="row items-center">
          <q-avatar icon="question_answer" color="primary" text-color="white"/>
          <h6 class="q-ml-sm q-mt-sm q-mb-xs"> Create a Group Chat</h6>
        </q-card-section>
        <q-card-section>
          <q-select outlined clearable v-model="groupUsers" use-input use-chips input-debounce="0"
                    @new-value="createFriendOption" :options="groupUserOptions" style="max-width: 400px" label="Users"/>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="primary" v-close-popup/>
          <q-btn flat label="Invite User" color="primary" @click="inviteUser()"/>
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script>

import { API } from '@aws-amplify/api'

export default {
  name: 'PageIndex',
  data () {
    return {
      loading: false,
      fab: false,
      createGroupDialog: false,
      editGroupDialog: false,
      inviteUserDialog: false,
      groupName: '',
      groupUsers: [],
      groupUserOptions: [],
      conversation: null
    }
  },
  async mounted () {
    await this.refresh()
  },
  methods: {
    showCreateDialog () {
      this.groupUsers = []
      this.groupUserOptions = this.getOtherUsers(this.$store.state.friends)
      this.groupName = ''
      this.createGroupDialog = true
    },
    showEditDialog (id) {
      this.conversation = this.$store.getters.getConversation(id)
      const users = this.getOtherUsers(this.conversation.users)
      this.groupUsers = users
      this.groupUserOptions = users
      this.editGroupDialog = true
    },
    showInviteDialog () {
      this.groupUsers = null
      this.groupUserOptions = this.$store.state.friends.filter(v => !this.conversation.users.includes(v))
      this.inviteUserDialog = true
    },
    async deleteConversation (conversation) {
      await API.post('api', 'conversation-delete', {
        body: {
          conversation: conversation
        }
      })
      await this.$store.dispatch('updateConversations')
    },
    async createGroupChat () {
      if (this.groupName === '')
        return
      try {
        await API.post('api', 'conversation-create', {
          body: {
            name: this.groupName,
            users: this.groupUsers || []
          }
        })
        this.createGroupDialog = false
        await this.$store.dispatch('updateConversationList')
      } catch (e) {
        console.error(e)
      }
    },
    createFriendOption (val, done) {
      if (val.length === 0)
        return
      if (!this.groupUserOptions.includes(val))
        this.groupUserOptions.push(val)
      done(val, 'toggle')
    },
    getOtherUsers (users) {
      return users.filter(v => v.toLowerCase() !== this.$store.state.user.username)
    },
    async refresh () {
      this.loading = true
      await this.$store.dispatch('updateConversationList')
      await this.$store.dispatch('updateConversations')
      this.loading = false
    },
    getLastMessage (messages) {
      if (!messages || messages.length === 0)
        return ''
      const message = messages[messages.length - 1]
      return message.user + ': ' + (message.type === 'image' ? 'Sent an Image' : message.content)
    },
    async kickUser (user) {
      await API.post('api', 'conversation-kick', {
        body: {
          user: user,
          conversation: this.conversation.id
        }
      })
      await this.$store.dispatch('updateConversation', this.conversation.id)
      this.conversation = this.$store.getters.getConversation(this.conversation.id)
    },
    async promoteUser (user) {
      await API.post('api', 'conversation-promote', {
        body: {
          user: user,
          conversation: this.conversation.id
        }
      })
      await this.$store.dispatch('updateConversation', this.conversation.id)
      this.conversation = this.$store.getters.getConversation(this.conversation.id)
    },
    async inviteUser () {
      if (!this.groupUsers)
        return
      await API.post('api', 'conversation-invite', {
        body: {
          user: this.groupUsers,
          conversation: this.conversation.id
        }
      })
      this.inviteUserDialog = false
      await this.$store.dispatch('updateConversation', this.conversation.id)
      this.conversation = this.$store.getters.getConversation(this.conversation.id)
    },
    async leaveConversation (conversation) {
      await API.post('api', 'conversation-leave', {
        body: {
          conversation: conversation
        }
      })
      await this.$store.dispatch('updateConversations')
    }
  }
}
</script>
