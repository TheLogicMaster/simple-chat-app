<template>
  <q-page>
    <q-layout container view="hHh lpR fFf" v-if="$store.getters.getConversation(this.$route.params.conversation)"
              :style="'height: ' + height + 'px'">

      <q-page-container>
        <q-page>
          <div style="padding-top: 50px" class="q-mx-md">
            <q-chat-message :name="message.user" :sent="message.user === $store.state.user.username"
                            :bg-color="message.user === $store.state.user.username ? 'secondary': ''"
                            :stamp="Number(message.timestamp) | moment('from', 'now')" :key="key"
                            v-for="(message, key) in $store.getters.getConversation(this.$route.params.conversation).messages">
              <div v-if="message.type === 'text'">{{ message.content }}</div>
              <q-img v-else-if="message.type === 'image'" :src="message.content" spinner-color="red" contain
                     style="max-width: 70vw; max-height: 70vh; min-width: 200px; min-height: 200px"
                     placeholder-src="https://http.cat/404" @click="showImageDialog(message.content)"/>
            </q-chat-message>
          </div>
          <div id="bottom"></div>
          <q-page-sticky position="top" expand class="bg-accent text-white">
            <q-toolbar>
              <q-toolbar-title>{{ $store.getters.getConversation(this.$route.params.conversation).name }}</q-toolbar-title>
            </q-toolbar>
          </q-page-sticky>
        </q-page>
      </q-page-container>

      <q-footer elevated>
        <div class="row q-pa-xs items-end">
          <div class="q-pr-xs">
            <q-btn size="23px" round dense color="accent" icon="add_a_photo" @click="$refs.image.pickFiles()"
                   :disable="sending">
              <q-tooltip>Send an image</q-tooltip>
            </q-btn>
          </div>
          <q-input class="col-grow" input-style="max-height: 6em; min-height: 30px" autogrow square outlined
                   v-model="message" label="Message"
                   :disable="sending" filled/>
          <div class="q-pl-xs">
            <q-btn color="accent" style="width: 100px; height: 56px" @click="sendMessage"
                   :disable="sending || message === ''" label="Send">
              <q-tooltip>Send Message</q-tooltip>
            </q-btn>
          </div>
        </div>
      </q-footer>
    </q-layout>

    <q-dialog v-model="imageDialog">
      <q-card>
        <q-card-section class="row items-center">
          <img :src="dialogImage" style="max-width: 90%; max-height: 80%">
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Close" color="primary" v-close-popup/>
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-file v-model="image" ref="image" class="hidden" @input="onSelectImage" accept="image/*"/>
  </q-page>
</template>

<script>
import { API } from '@aws-amplify/api'
import { scroll } from 'quasar'

const {
  getScrollTarget,
  setScrollPosition
} = scroll

export default {
  name: 'Conversation',
  data () {
    return {
      message: '',
      image: null,
      sending: false,
      timer: null,
      scrollTarget: null,
      scrollBottom: null,
      loaded: false,
      height: 0,
      imageDialog: false,
      dialogImage: '',
    }
  },
  async mounted () {
    this.height = window.innerHeight - 50
    await this.refresh()
    this.timer = setInterval(() => {
      this.refresh().then()
    }, 1000)
  },
  beforeDestroy () {
    clearInterval(this.timer)
  },
  methods: {
    showImageDialog(image) {
      this.dialogImage = image
      this.imageDialog = true
    },
    async refresh () {
      if (!this.$store.getters.getConversation(this.$route.params.conversation) &&
        (!(await this.$store.dispatch('updateConversationList')
          || !(await this.$store.getters.getConversation(this.$route.params.conversation)))))
        return
      const previous = this.$store.getters.getConversation(this.$route.params.conversation)
      if (!previous || !await this.$store.dispatch('updateConversation', this.$route.params.conversation))
        return
      if (!this.scrollBottom) {
        this.scrollBottom = document.getElementById('bottom')
        this.scrollTarget = getScrollTarget(this.scrollBottom)
      }
      if (!this.loaded || (previous.messages.length !== this.$store.getters.getConversation(this.$route.params.conversation).messages.length
        && this.scrollTarget.scrollHeight - this.scrollTarget.offsetHeight - this.scrollTarget.scrollTop < 200)) {
        setScrollPosition(this.scrollTarget, this.scrollBottom.offsetTop, 1000)
        this.loaded = true
      }
    },
    async onSelectImage () {
      if (this.image === undefined)
        return
      this.sending = true
      try {
        let response = await API.post('api', 'send-image', {
          body: {
            conversation: this.$route.params.conversation
          }
        })
        const formData = new FormData()
        for (let [field, value] of Object.entries(response.fields))
          formData.append(field, response.fields[field])
        formData.append('file', this.image)
        response = await this.$axios.post(response.url, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            //Authorization: `Bearer ${(await Auth.currentSession()).getIdToken().getJwtToken()}` // Todo: Require auth
          },
        })

        //this.$refs.image.removeFile(this.image) // Todo: Fix error
      } catch (e) {
        console.error(e)
      }
      this.sending = false
    },
    async sendMessage () {
      this.sending = true
      try {
        await API.post('api', 'send-message', {
          body: {
            conversation: this.$route.params.conversation,
            message: this.message
          }
        })
        this.message = ''
      } catch (e) {
        console.error(e)
      }
      this.sending = false
      await this.refresh()
    }
  }
}
</script>

<style scoped>

</style>
