// static/js/index.js - OPRAVENO

window.app = Vue.createApp({
  // Smazáno: el: '#vue' - patří do .mount()
  mixins: [window.LNbits.mixins.globalMixin],  // ← OPRAVENO: globalMixin místo custom
  data: function () {
    return {
      students: [],
      formDialog: {
        show: false,
        data: {
          name: '',  // ← Přidáno: name pro formulář
          wallet: null,
          bakalari_url: '',
          bakalari_username: '',
          bakalari_password: '',
          reward_grade_1: 10,
          reward_grade_2: 5,
          reward_grade_3: 0,
          reward_grade_4: 0,
          reward_grade_5: 0
        }
      },
      studentsTable: {
        columns: [
          { name: 'name', align: 'left', label: 'Student', field: 'name' },
          { name: 'bakalari_url', align: 'left', label: 'URL školy', field: 'bakalari_url' },
          { name: 'last_check', align: 'left', label: 'Poslední kontrola', field: 'last_check' },
          { name: 'reward_sats', align: 'left', label: 'Odměny (sats)', field: 'reward_sats' },
          { name: 'actions', align: 'right', label: '', field: 'actions' }
        ],
        pagination: {
          rowsPerPage: 10
        }
      }
    }
  },
  methods: {
    getStudents: function () {
      var self = this
      LNbits.api
        .request(
          'GET',
          '/bakalari_rewards/api/v1/students',
          this.g.user.wallets[0].adminkey
        )
        .then(function (response) {
          self.students = response.data
        })
        .catch(function (error) {
          LNbits.utils.notifyApiError(error)
        })
    },
    createStudent: function () {
      var self = this
      var data = this.formDialog.data
      LNbits.api
        .request(
          'POST',
          '/bakalari_rewards/api/v1/students',
          this.g.user.wallets[0].adminkey,
          data
        )
        .then(function (response) {
          self.students.push(response.data)
          self.formDialog.show = false
          self.resetForm()
        })
        .catch(function (error) {
          LNbits.utils.notifyApiError(error)
        })
    },
    deleteStudent: function (id) {
      var self = this
      LNbits.utils.confirmDialog('Opravdu smazat?', function () {
        LNbits.api
          .request(
            'DELETE',
            `/bakalari_rewards/api/v1/students/${id}`,
            self.g.user.wallets[0].adminkey
          )
          .then(function () {
            self.students = self.students.filter(s => s.id !== id)
          })
      })
    },
    resetForm: function () {
      this.formDialog.data = {
        name: '',
        wallet: null,
        bakalari_url: '',
        bakalari_username: '',
        bakalari_password: '',
        reward_grade_1: 10,
        reward_grade_2: 5,
        reward_grade_3: 0,
        reward_grade_4: 0,
        reward_grade_5: 0
      }
    }
  },
  created: function () {
    if (this.g.user.wallets.length) {
      this.getStudents()
    }
  }
})
window.app.mount('#vue')  // ← KLÍČOVÉ: Mount aplikace!
