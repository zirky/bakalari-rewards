window.app = Vue.createApp({
  el: '#vue',
  mixins: [window.LNbits.mixins.custom],
  data: function () {
    return {
      students: [],
      bakalari_rewards: {
        bakalari_url: '',
        bakalari_username: '',
        bakalari_password: '',
        reward_grade_1: 0,
        reward_grade_2: 0,
        reward_grade_3: 0,
        reward_grade_4: 0,
        reward_grade_5: 0
      },
      formDialog: {
        show: false,
        data: {}
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
    // Získání seznamu studentů
    getStudents: function () {
      var self = this
      LNbits.api
        .request(
          'GET',
          '/bakalari_rewards/api/v1/students', // Opravená cesta
          this.g.user.wallets[0].adminkey
        )
        .then(function (response) {
          self.students = response.data
        })
        .catch(function (error) {
          LNbits.utils.confirmDialog(error.data.detail)
        })
    },
    // Smazání studenta
    deleteStudent: function (studentId) {
      var self = this
      var student = _.find(this.students, {id: studentId})

      LNbits.utils
        .confirmDialog('Opravdu chcete smazat studenta ' + student.name + '?')
        .onOk(function () {
          LNbits.api
            .request(
              'DELETE',
              '/bakalari_rewards/api/v1/students/' + studentId, // Opravená cesta
              self.g.user.wallets[0].adminkey
            )
            .then(function (response) {
              self.students = _.reject(self.students, function (obj) {
                return obj.id === studentId
              })
            })
            .catch(function (error) {
              LNbits.utils.confirmDialog(error.data.detail)
            })
        })
    },
    // Vytvoření nového studenta (odeslání formuláře)
    sendStudentData: function () {
      var self = this
      var data = this.formDialog.data

      LNbits.api
        .request(
          'POST',
          '/bakalari_rewards/api/v1/students', // Opravená cesta
          this.g.user.wallets[0].adminkey,
          data
        )
        .then(function (response) {
          self.students.push(response.data)
          self.formDialog.show = false
          self.formDialog.data = {} // Reset formuláře
        })
        .catch(function (error) {
          LNbits.utils.confirmDialog(error.data.detail)
        })
    },
    // Otevření dialogu pro přidání studenta
    openFormDialog: function () {
      this.formDialog.data = {
        reward_grade_1: 10, // Výchozí hodnoty v satoshi
        reward_grade_2: 5,
        reward_grade_3: 0,
        reward_grade_4: 0,
        reward_grade_5: 0
      }
      this.formDialog.show = true
    }
  },
  created: function () {
    if (this.g.user.wallets.length) {
      this.getStudents()
    }
  }
})
