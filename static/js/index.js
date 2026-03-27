window.app = Vue.createApp({
  mixins: [windowMixin],
  delimiters: ['${', '}'],
  data: function () {
    return {
      students: [],
      formDialog: {
        show: false,
        data: {
          name: '',
          wallet: '',
          bakalari_url: '',
          bakalari_username: '',
          bakalari_password: '',
          reward_grade_1: 100,
          reward_grade_2: 75,
          reward_grade_3: 50,
          reward_grade_4: 25,
          reward_grade_5: 0
        }
      },
      studentsTable: {
        columns: [
          {name: 'name', align: 'left', label: 'Jmeno', field: 'name'},
          {name: 'bakalari_url', align: 'left', label: 'URL skoly', field: 'bakalari_url'},
          {name: 'reward_sats', align: 'left', label: 'Odmena za znamky'},
          {name: 'last_check', align: 'left', label: 'Posledni kontrola', field: 'last_check'},
          {name: 'actions', align: 'center', label: 'Akce'}
        ]
      }
    }
  },
  created: function () {
    this.getStudents()
  },
  methods: {
    getStudents: function () {
      var self = this
      LNbits.api
        .request(
          'GET',
          '/bakalari_rewards/api/v1/students',
          this.g.user.wallets[0].inkey
        )
        .then(function (response) {
          self.students = response.data
        })
        .catch(function (err) {
          LNbits.utils.notifyApiError(err)
        })
    },
    createStudent: function () {
      var self = this
      var wallet = this.g.user.wallets.find(function (w) {
        return w.id === self.formDialog.data.wallet
      })
      if (!wallet) {
        wallet = this.g.user.wallets[0]
        self.formDialog.data.wallet = wallet.id
      }
      LNbits.api
        .request(
          'POST',
          '/bakalari_rewards/api/v1/students',
          wallet.adminkey,
          self.formDialog.data
        )
        .then(function (response) {
          self.students.push(response.data)
          self.formDialog.show = false
          self.formDialog.data = {
            name: '',
            wallet: '',
            bakalari_url: '',
            bakalari_username: '',
            bakalari_password: '',
            reward_grade_1: 100,
            reward_grade_2: 75,
            reward_grade_3: 50,
            reward_grade_4: 25,
            reward_grade_5: 0
          }
        })
        .catch(function (err) {
          LNbits.utils.notifyApiError(err)
        })
    },
    deleteStudent: function (id) {
      var self = this
      LNbits.api
        .request(
          'DELETE',
          '/bakalari_rewards/api/v1/students/' + id,
          this.g.user.wallets[0].adminkey
        )
        .then(function () {
          self.students = self.students.filter(function (s) {
            return s.id !== id
          })
        })
        .catch(function (err) {
          LNbits.utils.notifyApiError(err)
        })
    }
  }
}).mount('#vue')
