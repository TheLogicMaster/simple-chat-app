<template>
  <q-page class="q-pa-sm">
    <q-list>
      <div class="row items-center">
        <div class="text-h4 q-mr-lg q-mb-sm inline-block">Your Conversations</div>
        <q-btn round :loading="loading" color="secondary" @click="refresh" icon="refresh"></q-btn>
      </div>

      <q-card v-ripple flat bordered class="q-pa-sm q-ma-xs q-hoverable" v-for="conversation of $store.state.conversations"
              :key="conversation.id" @click="">
        <span class="q-focus-helper"></span>
        <q-card-section>
          <div class="text-h6 inline-block">{{ conversation.name }}</div>
          <div class="text-subtitle2">{{ getLastMessage(conversation.messages) }}</div>
        </q-card-section>
      </q-card>
    </q-list>
  </q-page>
</template>

<script>

export default {
  name: 'PageIndex',
  data() {
    return {
      loading: false
    }
  },
  async mounted () {
    await this.refresh()
  },
  methods: {
    async refresh() {
      this.loading = true
      await this.$store.dispatch('updateConversationList')
      await this.$store.dispatch('updateConversations')
      this.loading = false
    },
    getLastMessage(messages) {
      if (!messages || messages.length === 0)
        return ''
      return messages[messages.length - 1]
    }
  }
}
</script>
