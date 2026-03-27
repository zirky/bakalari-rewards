window.app = Vue.createApp({
  el: '#vue',
  mixins: [window.LNbits.mixins.custom],
  data: function () {
    return {
      students: [],
      // Toto jsme přidali, aby to neházelo chybu 'show'
      formDialog: {
        show: false,
        data: {
          name: '',
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
          {name: 'name', align: 'left', label: 'Student', field: 'name'},
          {name: 'bakalari_url', align: 'left', label: 'URL školy', field: 'bakalari_url'},
          {name: 'last_check', align: 'left', label: 'Poslední kontrola', field: 'last_check'}
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
        .request('GET', '/bakalari_rewards/api/v1/students', this.g.user.wallets[0].adminkey)
        .then(function (response) {
          self.students = response.data
        })
    },
    // Zjednodušená funkce pro otevření dialogu
    openFormDialog: function () {
      this.formDialog.show = true
    },
    sendStudentData: function () {
      var self = this
      LNbits.api
        .request('POST', '/bakalari_rewards/api/v1/students', this.g.user.wallets[0].adminkey, this.formDialog.data)
        .then(function (response) {
          self.students.push(response.data)
          self.formDialog.show = false
        })
    }
  },
  created: function () {
    if (this.g.user.wallets.length) {
      this.getStudents()
    }
  }
})
