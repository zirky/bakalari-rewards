// static/js/index.js

window.app = Vue.createApp({
  el: '#vue',
  mixins: [window.LNbits.mixins.custom],
  data: function () {
    return {
      // Seznam studentů pro tabulku
      students: [],
      // Objekt pro dialog (TADY byla ta chyba 'undefined')
      formDialog: {
        show: false,
        data: {
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
      // Nastavení tabulky
      studentsTable: {
        columns: [
          { name: 'name', align: 'left', label: 'Student', field: 'name' },
          { name: 'bakalari_url', align: 'left', label: 'URL školy', field: 'bakalari_url' },
          { name: 'last_check', align: 'left', label: 'Poslední kontrola', field: 'last_check' }
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
          LNbits.utils.confirmDialog(error.data.detail)
        })
    },
    sendStudentData: function () {
      var self = this
      // Posíláme to, co je vnořené ve formDialog.data
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
          // Reset dat po úspěchu
          self.formDialog.data = { reward_grade_1: 10, reward_grade_2: 5 }
        })
        .catch(function (error) {
          LNbits.utils.confirmDialog(error.data.detail)
        })
    }
  },
  created: function () {
    if (this.g.user.wallets.length) {
      this.getStudents()
    }
  }
})
